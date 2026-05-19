#!/usr/bin/env python3
"""Smoke-test local Cua Linux sandbox: create, shell, input, screenshot."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

# Match batch local sandbox: bypass system HTTP proxy for localhost Docker ports.
_NO_PROXY = "127.0.0.1,localhost"
for _key in ("NO_PROXY", "no_proxy"):
    _existing = os.environ.get(_key, "").strip()
    os.environ[_key] = f"{_NO_PROXY},{_existing}" if _existing else _NO_PROXY

from ._cli import (
    check_python_version,
    fail,
    import_cua,
    log,
    print_runtime_info,
    run_step,
    section,
)
from .docker_diag import dump_cua_diagnostics, print_docker_summary


@dataclass
class StepResult:
    name: str
    ok: bool
    detail: str = ""
    elapsed_s: float | None = None


@dataclass
class SmokeReport:
    passed: bool = False
    python: str = ""
    cua_import_ok: bool = False
    docker_ok: bool = False
    steps: list[StepResult] = field(default_factory=list)
    screenshot: str | None = None
    error: str | None = None


def record(report: SmokeReport, name: str, ok: bool, detail: str = "") -> None:
    report.steps.append(StepResult(name=name, ok=ok, detail=detail))


async def smoke_linux(args: argparse.Namespace) -> int:
    report = SmokeReport(python=sys.version.split()[0])

    section("Runtime")
    if not check_python_version():
        report.error = "unsupported Python version"
        _write_report(args.output_dir, report)
        return 1
    print_runtime_info()

    cua = import_cua()
    if cua is None:
        report.error = "cua import failed"
        _write_report(args.output_dir, report)
        return 1
    Image, Sandbox = cua
    report.cua_import_ok = True

    section("Docker")
    report.docker_ok = print_docker_summary()
    if args.check_only:
        report.passed = report.docker_ok and report.cua_import_ok
        _write_report(args.output_dir, report)
        return 0 if report.passed else 1

    if not report.docker_ok:
        report.error = "docker unavailable"
        _write_report(args.output_dir, report)
        return 1

    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    screenshot_path = output_dir / "linux_sandbox_screenshot.png"

    section("Linux sandbox (Docker/XFCE)")
    try:
        async with Sandbox.ephemeral(Image.linux(kind="container"), local=True) as sb:
            log("sandbox ready")
            record(report, "create_sandbox", True)

            shell = await run_step(
                "shell.run(uname/pwd/whoami)",
                sb.shell.run("uname -a && pwd && whoami && python3 --version"),
                args.timeout,
            )
            print(f"shell.returncode={shell.returncode}", flush=True)
            print("shell.stdout:", flush=True)
            print(shell.stdout, flush=True)
            if shell.stderr:
                print("shell.stderr:", file=sys.stderr, flush=True)
                print(shell.stderr, file=sys.stderr, flush=True)
            shell_ok = shell.returncode == 0 and bool((shell.stdout or "").strip())
            record(report, "shell", shell_ok, f"returncode={shell.returncode}")
            if not shell_ok:
                fail("shell command failed")
                report.error = "shell failed"
                dump_cua_diagnostics(args.log_tail)
                _write_report(args.output_dir, report)
                return 1

            await run_step("mouse.move", sb.mouse.move(100, 100), args.timeout)
            record(report, "mouse_move", True)
            await run_step("mouse.click", sb.mouse.click(100, 100), args.timeout)
            record(report, "mouse_click", True)
            await run_step("keyboard.press", sb.keyboard.press("Return"), args.timeout)
            record(report, "keyboard_press", True)

            png = await run_step("screenshot", sb.screenshot(), args.timeout)
            screenshot_path.write_bytes(png)
            report.screenshot = str(screenshot_path)
            log(f"screenshot saved: {screenshot_path} ({len(png)} bytes)")
            shot_ok = len(png) >= 1000
            record(report, "screenshot", shot_ok, f"bytes={len(png)}")
            if not shot_ok:
                fail("screenshot is unexpectedly small")
                report.error = "screenshot too small"
                dump_cua_diagnostics(args.log_tail)
                _write_report(args.output_dir, report)
                return 1

        report.passed = True
        log("Linux sandbox smoke test passed")
        _write_report(args.output_dir, report)
        return 0
    except asyncio.TimeoutError as exc:
        fail(str(exc))
        report.error = str(exc)
        record(report, "timeout", False, str(exc))
        dump_cua_diagnostics(args.log_tail)
        _write_report(args.output_dir, report)
        return 124
    except Exception as exc:
        fail(f"{type(exc).__name__}: {exc}")
        report.error = f"{type(exc).__name__}: {exc}"
        record(report, "exception", False, str(exc))
        dump_cua_diagnostics(args.log_tail)
        _write_report(args.output_dir, report)
        return 1


def _write_report(output_dir: Path, report: SmokeReport) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    payload: dict[str, Any] = {
        "passed": report.passed,
        "python": report.python,
        "cua_import_ok": report.cua_import_ok,
        "docker_ok": report.docker_ok,
        "screenshot": report.screenshot,
        "error": report.error,
        "steps": [asdict(step) for step in report.steps],
    }
    path = output_dir / "linux_smoke_report.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    log(f"report saved: {path}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Smoke-test Cua local Linux sandbox (create, shell, input, screenshot).",
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Only verify Python/cua/Docker prerequisites; do not create a sandbox.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=180,
        help="Seconds to wait per SDK step. Default: 180.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("tmp/sandbox-smoke"),
        help="Artifacts directory. Default: tmp/sandbox-smoke.",
    )
    parser.add_argument(
        "--log-tail",
        type=int,
        default=120,
        help="Docker log lines to dump on failure. Default: 120.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return asyncio.run(smoke_linux(args))


if __name__ == "__main__":
    raise SystemExit(main())
