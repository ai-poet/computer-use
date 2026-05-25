"""Batch mode: run multiple product analyses in Cua sandboxes (local or cloud)."""

from __future__ import annotations

import asyncio
import csv
import json
import os
import sys
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .batch_store import BatchRunStore, JobState
from .claude_driver import run_claude
from .config import REPO_ROOT
from .prompts import build_prompt
from .sandbox_ctl import (
    cleanup_all_local_sandboxes,
    docker_cleanup_sync_quick,
    install_batch_exit_hooks,
    reset_batch_cleanup_gate,
    teardown_out_dir,
    uninstall_batch_exit_hooks,
)
from .sandbox_runtime import SandboxContext, write_cloud_mcp_config
from .tasks import post_check, prepare_output_dir, write_metadata_seed
from .ui import err, log
from .workflow import seed_workflow


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
            "  example: python backend/analyze_product.py "
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


QUEUE_GLOB = "queue*.json"


def discover_queues(root: Path | None = None) -> list[Path]:
    """Return ``queue*.json`` files under *root*, sorted by filename."""
    base = (root or REPO_ROOT).expanduser().resolve()
    if not base.is_dir():
        raise FileNotFoundError(f"queue directory not found: {base}")
    paths = sorted(base.glob(QUEUE_GLOB))
    if not paths:
        raise FileNotFoundError(
            f"no queue files matching {QUEUE_GLOB!r} under {base}\n"
            "  example: queue.language-learning.json"
        )
    return paths


def load_merged_queues(
    paths: list[Path],
) -> tuple[list[dict[str, str | None]], str]:
    """Load and merge multiple queue files; skip duplicate product+url pairs."""
    merged: list[dict[str, str | None]] = []
    seen: set[tuple[str, str]] = set()
    labels: list[str] = []
    for path in paths:
        labels.append(path.name)
        for row in load_queue(path):
            key = (row["product_name"] or "", row["url"] or "")
            if key in seen:
                continue
            seen.add(key)
            merged.append(row)
    if not merged:
        raise ValueError("merged queue is empty")
    if len(paths) == 1:
        name = paths[0].name
    else:
        name = f"all ({len(paths)} files)"
    return merged, name


def resolve_batch_rows(
    *,
    queue_path: Path | None = None,
    queue_paths: list[Path] | None = None,
    batch_all: bool = False,
    queue_root: Path | None = None,
) -> tuple[list[dict[str, str | None]], str, list[Path]]:
    """Resolve queue rows from a single file, explicit path list, or all ``queue*.json``."""
    if batch_all:
        paths = discover_queues(queue_root)
        rows, name = load_merged_queues(paths)
        return rows, name, paths
    if queue_paths is not None:
        paths = [p.expanduser() for p in queue_paths]
        if len(paths) == 1:
            rows = load_queue(paths[0])
            return rows, paths[0].name, paths
        rows, _name = load_merged_queues(paths)
        label = " → ".join(p.name for p in paths)
        return rows, label, paths
    if queue_path is None:
        raise ValueError("queue_path is required when batch_all is False")
    path = queue_path.expanduser()
    rows = load_queue(path)
    return rows, path.name, [path]


def _plain_batch_enabled() -> bool:
    if os.environ.get("ANALYZE_BATCH_PLAIN", "").strip() in ("1", "true", "yes"):
        return True
    return not sys.stdout.isatty()


def run_batch(
    max_workers: int,
    *,
    sandbox_ctx: SandboxContext,
    queue_path: Path | None = None,
    queue_paths: list[Path] | None = None,
    batch_all: bool = False,
    queue_root: Path | None = None,
    sandbox_warnings: list[str] | None = None,
    plain: bool | None = None,
) -> BatchResult:
    """Synchronous wrapper used by CLI."""
    rows, queue_name, _paths = resolve_batch_rows(
        queue_path=queue_path,
        queue_paths=queue_paths,
        batch_all=batch_all,
        queue_root=queue_root,
    )
    use_plain = _plain_batch_enabled() if plain is None else plain
    if not use_plain:
        os.environ["ANALYZER_FORCE_COLOR"] = "1"
    store = BatchRunStore(
        rows,
        max_workers=max_workers,
        queue_name=queue_name,
        dashboard_active=not use_plain,
    )

    reset_batch_cleanup_gate()
    install_batch_exit_hooks(local=sandbox_ctx.local)

    try:
        if use_plain:
            return asyncio.run(
                _run_batch(
                    rows,
                    max_workers,
                    sandbox_ctx=sandbox_ctx,
                    sandbox_warnings=sandbox_warnings or [],
                    store=store,
                )
            )

        from .batch_dashboard import run_dashboard

        worker_error: list[BaseException] = []

        def _worker() -> None:
            try:
                result = asyncio.run(
                    _run_batch(
                        rows,
                        max_workers,
                        sandbox_ctx=sandbox_ctx,
                        sandbox_warnings=sandbox_warnings or [],
                        store=store,
                    )
                )
                store.set_batch_complete(result.results)
            except BaseException as exc:
                worker_error.append(exc)
                store.set_batch_complete([], error=exc)

        thread = threading.Thread(target=_worker, daemon=True)
        thread.start()
        run_dashboard(store, sandbox_label=f"{sandbox_ctx.mode}/{sandbox_ctx.image}")
        thread.join()
        if worker_error:
            raise worker_error[0]
        return store.to_batch_result()
    finally:
        uninstall_batch_exit_hooks()
        if sandbox_ctx.local:
            cleanup_all_local_sandboxes()


async def _run_batch(
    rows: list[dict[str, str | None]],
    max_workers: int,
    *,
    sandbox_ctx: SandboxContext,
    sandbox_warnings: list[str],
    store: BatchRunStore,
) -> BatchResult:
    if max_workers < 1:
        raise ValueError("max_workers must be >= 1")
    sem = asyncio.Semaphore(max_workers)
    tasks = [
        _run_one_with_semaphore(
            sem, row, index, sandbox_ctx, sandbox_warnings, store
        )
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
        if store.dashboard_active:
            continue
        status = "OK" if result_row["rc"] == 0 else f"FAIL rc={result_row['rc']}"
        log(
            f"[batch] {status}: {result_row['product']} -> "
            f"{result_row.get('out_dir') or '?'}"
        )

    try:
        store.write_status_json(Path.cwd() / "batch-status.json")
    except OSError:
        pass

    if not store.dashboard_active:
        store.set_batch_complete(results)
    return BatchResult(total=len(rows), results=results)


def run_single(
    row: dict[str, str | None],
    *,
    sandbox_ctx: SandboxContext,
    sandbox_warnings: list[str] | None = None,
    plain: bool = True,
) -> dict[str, Any]:
    """Run one sandbox-first analysis using the same worker path as batch."""
    store = BatchRunStore(
        [row],
        max_workers=1,
        queue_name="single",
        dashboard_active=not plain,
    )
    reset_batch_cleanup_gate()
    install_batch_exit_hooks(local=sandbox_ctx.local)
    try:
        return _run_one(row, 1, sandbox_ctx, sandbox_warnings or [], store)
    finally:
        uninstall_batch_exit_hooks()
        if sandbox_ctx.local:
            cleanup_all_local_sandboxes()


async def _run_one_with_semaphore(
    sem: asyncio.Semaphore,
    row: dict[str, str | None],
    index: int,
    sandbox_ctx: SandboxContext,
    sandbox_warnings: list[str],
    store: BatchRunStore,
) -> dict[str, Any]:
    store.mark_queued(index)
    if store.should_skip_job(index):
        return _cancelled_result(row, sandbox_ctx, index)
    try:
        async with sem:
            if store.should_skip_job(index):
                return _cancelled_result(row, sandbox_ctx, index)
            store.mark_starting(index)
            return await asyncio.to_thread(
                _run_one, row, index, sandbox_ctx, sandbox_warnings, store
            )
    except Exception as exc:
        store.mark_done(index, rc=1, error=f"{type(exc).__name__}: {exc}")
        return _exception_result(row, exc, sandbox_ctx)


def _cancelled_result(
    row: dict[str, str | None],
    sandbox_ctx: SandboxContext,
    index: int,
) -> dict[str, Any]:
    return {
        "product": row.get("product_name") or "",
        "url": row.get("url") or "",
        "out_dir": None,
        "log_file": None,
        "sandbox_image": sandbox_ctx.image,
        "sandbox_mode": sandbox_ctx.mode,
        "rc": 130,
        "error": "cancelled",
        "job_id": index,
    }


def _run_one(
    row: dict[str, str | None],
    index: int,
    sandbox_ctx: SandboxContext,
    sandbox_warnings: list[str],
    store: BatchRunStore,
) -> dict[str, Any]:
    product_name = row["product_name"] or ""
    url = row["url"] or ""
    download_url = row.get("download_url")

    if store.should_skip_job(index):
        return _cancelled_result(row, sandbox_ctx, index)

    out_dir = prepare_output_dir(product_name)
    log_file = out_dir / "run.log"
    store.mark_running(index, out_dir=str(out_dir), log_file=str(log_file))

    if not store.dashboard_active:
        log(f"[batch:{index}] 输出目录: {out_dir} ({sandbox_ctx.mode} sandbox)")

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
    seed_workflow(out_dir)

    env = os.environ.copy()
    env.update(sandbox_ctx.env())
    env.update(
        {
            "ANALYZER_OUTPUT_DIR": str(out_dir),
            "ANALYZER_PRODUCT_URL": url,
            "ANALYZER_BATCH_PARALLEL": "1",
            "ANALYZER_PYTHON": sys.executable,
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
    mcp_config = None
    if sandbox_ctx.mode == "cloud" and sandbox_ctx.api_key:
        mcp_config = write_cloud_mcp_config(out_dir, api_key=sandbox_ctx.api_key)

    mirror = not store.dashboard_active
    supplement_provider = (
        store.make_supplement_provider(index) if store.dashboard_active else None
    )

    def _event_sink(lines: list[str], state: dict) -> None:
        store.append_event(index, lines, state)

    try:
        rc = run_claude(
            prompt,
            out_dir=out_dir,
            non_interactive=True,
            log_file=log_file,
            env=env,
            terminal_prefix=f"[batch:{index} {product_name}] ",
            mcp_config=mcp_config,
            esc_flag=store.esc_flag(index),
            event_sink=_event_sink if store.dashboard_active else None,
            mirror_stdout=mirror,
            supplement_provider=supplement_provider,
        )
    finally:
        if store.dashboard_active:
            store.mark_finishing(index, msg="销毁 sandbox…")
        teardown_out_dir(out_dir)

    post_check(out_dir)
    error = None
    if rc != 0:
        error = f"exit {rc}"
        if not store.dashboard_active:
            err(f"[batch:{index}] {product_name} 失败,详见 {log_file}")

    store.mark_done(index, rc=rc, error=error)
    return {
        "product": product_name,
        "url": url,
        "out_dir": str(out_dir),
        "log_file": str(log_file),
        "sandbox_image": sandbox_ctx.image,
        "sandbox_mode": sandbox_ctx.mode,
        "rc": rc,
        "error": error,
        "job_id": index,
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
