"""Batch mode: run multiple product analyses in Cua sandboxes (local or cloud)."""

from __future__ import annotations

import asyncio
import csv
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .claude_driver import run_claude
from .prompts import build_prompt
from .sandbox_runtime import SandboxContext
from .tasks import post_check, prepare_output_dir, write_metadata_seed
from .ui import err, log


@dataclass
class BatchResult:
    total: int
    results: list[dict[str, Any]]

    @property
    def failed(self) -> list[dict[str, Any]]:
        return [row for row in self.results if row["rc"] != 0]


def load_queue(path: Path) -> list[dict[str, str | None]]:
    """Load CSV or JSON queue rows with product_name/url/download_url fields."""
    if not path.exists():
        resolved = path.expanduser().resolve()
        hint = (
            f"queue file not found: {resolved}\n"
            f"  cwd: {Path.cwd()}\n"
            "  example: python scripts/analyze_product.py "
            "--batch queue.language-learning.json --sandbox-image linux"
        )
        raise FileNotFoundError(hint)
    if path.suffix.lower() == ".csv":
        with path.open(newline="", encoding="utf-8") as fh:
            rows: Any = list(csv.DictReader(fh))
    elif path.suffix.lower() == ".json":
        rows = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(rows, list):
            raise ValueError("JSON queue must be a list of objects")
    else:
        raise ValueError(f"unsupported queue format: {path.suffix}; use .csv or .json")

    normalized: list[dict[str, str | None]] = []
    for i, row in enumerate(rows, start=1):
        if not isinstance(row, dict):
            raise ValueError(f"queue row {i} must be an object")
        product_name = (row.get("product_name") or row.get("name") or "").strip()
        url = (row.get("url") or "").strip()
        download_url = (row.get("download_url") or "").strip() or None
        if not product_name or not url:
            raise ValueError(f"queue row {i} must include product_name and url")
        normalized.append(
            {"product_name": product_name, "url": url, "download_url": download_url}
        )
    return normalized


def run_batch(
    queue_path: Path,
    max_workers: int,
    *,
    sandbox_ctx: SandboxContext,
    sandbox_warnings: list[str] | None = None,
) -> BatchResult:
    """Synchronous wrapper used by CLI."""
    return asyncio.run(
        _run_batch(
            queue_path,
            max_workers,
            sandbox_ctx=sandbox_ctx,
            sandbox_warnings=sandbox_warnings or [],
        )
    )


async def _run_batch(
    queue_path: Path,
    max_workers: int,
    *,
    sandbox_ctx: SandboxContext,
    sandbox_warnings: list[str],
) -> BatchResult:
    if max_workers < 1:
        raise ValueError("max_workers must be >= 1")
    rows = load_queue(queue_path)
    sem = asyncio.Semaphore(max_workers)
    tasks = [
        _run_one_with_semaphore(sem, row, index, sandbox_ctx, sandbox_warnings)
        for index, row in enumerate(rows, start=1)
    ]
    gathered = await asyncio.gather(*tasks, return_exceptions=True)

    results: list[dict[str, Any]] = []
    for row, result in zip(rows, gathered):
        if isinstance(result, Exception):
            result_row = _exception_result(row, result, sandbox_ctx)
        else:
            result_row = result
        results.append(result_row)
        status = "OK" if result_row["rc"] == 0 else f"FAIL rc={result_row['rc']}"
        log(
            f"[batch] {status}: {result_row['product']} -> "
            f"{result_row.get('out_dir') or '?'}"
        )
    return BatchResult(total=len(rows), results=results)


async def _run_one_with_semaphore(
    sem: asyncio.Semaphore,
    row: dict[str, str | None],
    index: int,
    sandbox_ctx: SandboxContext,
    sandbox_warnings: list[str],
) -> dict[str, Any]:
    async with sem:
        return await asyncio.to_thread(_run_one, row, index, sandbox_ctx, sandbox_warnings)


def _run_one(
    row: dict[str, str | None],
    index: int,
    sandbox_ctx: SandboxContext,
    sandbox_warnings: list[str],
) -> dict[str, Any]:
    product_name = row["product_name"] or ""
    url = row["url"] or ""
    download_url = row.get("download_url")

    out_dir = prepare_output_dir(product_name)
    meta = write_metadata_seed(
        out_dir,
        product_name,
        url,
        download_url,
        runtime=sandbox_ctx.runtime,
        sandbox_image=sandbox_ctx.image,
        sandbox_local=sandbox_ctx.local,
        sandbox_mode=sandbox_ctx.mode,
        android_enabled=sandbox_ctx.android_enabled,
    )
    log_file = out_dir / "run.log"
    log(f"[batch:{index}] 输出目录: {out_dir} ({sandbox_ctx.mode} sandbox)")

    env = os.environ.copy()
    env.update(sandbox_ctx.env())
    env.update(
        {
            "ANALYZER_OUTPUT_DIR": str(out_dir),
            "ANALYZER_BATCH_PARALLEL": "1",
            "ANALYZER_SANDBOX_WARNINGS": json.dumps(
                sandbox_warnings, ensure_ascii=False
            ),
        }
    )

    prompt = build_prompt(
        product_name,
        url,
        download_url,
        out_dir,
        meta["host_os"],
        meta["host_arch"],
        runtime=sandbox_ctx.runtime,
        sandbox_image=sandbox_ctx.image,
        sandbox_local=sandbox_ctx.local,
        android_enabled=sandbox_ctx.android_enabled,
        sandbox_warnings=sandbox_warnings,
        batch_parallel=True,
    )
    rc = run_claude(
        prompt,
        out_dir=out_dir,
        non_interactive=True,
        log_file=log_file,
        env=env,
        terminal_prefix=f"[batch:{index} {product_name}] ",
    )
    post_check(out_dir)
    if rc != 0:
        err(f"[batch:{index}] {product_name} 失败,详见 {log_file}")
    return {
        "product": product_name,
        "url": url,
        "out_dir": str(out_dir),
        "log_file": str(log_file),
        "sandbox_image": sandbox_ctx.image,
        "sandbox_mode": sandbox_ctx.mode,
        "rc": rc,
        "error": None,
    }


def _exception_result(
    row: dict[str, str | None],
    exc: Exception,
    sandbox_ctx: SandboxContext,
) -> dict[str, Any]:
    return {
        "product": row.get("product_name") or "",
        "url": row.get("url") or "",
        "out_dir": None,
        "log_file": None,
        "sandbox_image": sandbox_ctx.image,
        "sandbox_mode": sandbox_ctx.mode,
        "rc": 1,
        "error": f"{type(exc).__name__}: {exc}",
    }
