#!/usr/bin/env python3
"""Smoke-test local Cua Linux sandbox: shell, UI input, multi-step screenshots."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Awaitable, Callable

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
    warn,
)
from .docker_diag import dump_cua_diagnostics, print_docker_summary

# Reuse batch defaults (XFCE image + amd64 platform).
from product_analyzer.sandbox_runtime import (
    LINUX_CONTAINER_IMAGE,
    linux_container_image,
    linux_docker_runtime,
)

_MIN_SCREENSHOT_BYTES = 1000


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
    screenshots: list[str] = field(default_factory=list)
    screenshot: str | None = None  # last screenshot path (backward compat)
    screen_size: str | None = None
    error: str | None = None


def record(report: SmokeReport, name: str, ok: bool, detail: str = "") -> None:
    report.steps.append(StepResult(name=name, ok=ok, detail=detail))


async def _capture(
    report: SmokeReport,
    shots_dir: Path,
    step_name: str,
    filename: str,
    capture: Callable[[], Awaitable[bytes]],
    timeout: float,
) -> Path | None:
    """Save a PNG from ``capture()`` (sb.screenshot or sb.screen.screenshot)."""
    png = await run_step(step_name, capture(), timeout)
    path = shots_dir / filename
    path.write_bytes(png)
    report.screenshots.append(str(path))
    report.screenshot = str(path)
    ok = len(png) >= _MIN_SCREENSHOT_BYTES
    record(report, step_name.replace(" ", "_"), ok, f"bytes={len(png)} path={path.name}")
    log(f"  saved {path} ({len(png)} bytes)")
    if not ok:
        fail(f"{step_name}: image too small ({len(png)} bytes)")
    return path if ok else None


async def _run_ui_scenario(sb: Any, shots_dir: Path, timeout: float, report: SmokeReport) -> bool:
    """Exercise common product-analyzer UI paths: mouse, keyboard, scroll, screenshots."""
    section("UI operations")
    shots_dir.mkdir(parents=True, exist_ok=True)
    all_ok = True

    width, height = await run_step("screen.size", sb.screen.size(), timeout)
    report.screen_size = f"{width}x{height}"
    log(f"screen size: {width}x{height}")
    record(report, "screen_size", width > 0 and height > 0, report.screen_size)

    cx, cy = width // 2, height // 2

    if not await _capture(
        report,
        shots_dir,
        "screenshot desktop idle",
        "01_desktop_idle.png",
        sb.screenshot,
        timeout,
    ):
        all_ok = False

    await run_step("mouse.move center", sb.mouse.move(cx, cy), timeout)
    record(report, "mouse_move", True)
    await run_step("mouse.move corner", sb.mouse.move(80, 80), timeout)
    record(report, "mouse_move_corner", True)

    if not await _capture(
        report,
        shots_dir,
        "screenshot after mouse move",
        "02_after_mouse_move.png",
        sb.screenshot,
        timeout,
    ):
        all_ok = False

    await run_step("mouse.click center", sb.mouse.click(cx, cy), timeout)
    record(report, "mouse_click", True)

    await run_step("mouse.right_click", sb.mouse.right_click(cx, cy), timeout)
    record(report, "mouse_right_click", True)
    await asyncio.sleep(0.5)

    if not await _capture(
        report,
        shots_dir,
        "screenshot after right click",
        "03_after_right_click.png",
        sb.screenshot,
        timeout,
    ):
        all_ok = False

    # Dismiss context menu if open
    await run_step("keyboard keypress Escape", sb.keyboard.keypress("escape"), timeout)
    record(report, "keyboard_escape", True)

    await run_step("mouse.scroll down", sb.mouse.scroll(cx, cy, scroll_y=-5), timeout)
    record(report, "mouse_scroll", True)
    await asyncio.sleep(0.3)

    if not await _capture(
        report,
        shots_dir,
        "screenshot after scroll",
        "04_after_scroll.png",
        sb.screenshot,
        timeout,
    ):
        all_ok = False

    # XFCE: Ctrl+Alt+T usually opens a terminal
    await run_step(
        "keyboard hotkey Ctrl+Alt+T",
        sb.keyboard.keypress(["ctrl", "alt", "t"]),
        timeout,
    )
    record(report, "keyboard_hotkey_terminal", True)
    await asyncio.sleep(1.5)

    if not await _capture(
        report,
        shots_dir,
        "screenshot terminal",
        "05_terminal_open.png",
        sb.screenshot,
        timeout,
    ):
        warn("terminal screenshot weak — hotkey may differ on this image; continuing")
        record(report, "keyboard_hotkey_terminal", False, "no visible terminal")

    await run_step("keyboard type", sb.keyboard.type("echo cua-smoke-ui-ok"), timeout)
    record(report, "keyboard_type", True)
    await run_step("keyboard keypress Enter", sb.keyboard.keypress("enter"), timeout)
    record(report, "keyboard_enter", True)
    await asyncio.sleep(0.8)

    if not await _capture(
        report,
        shots_dir,
        "screenshot after typing",
        "06_after_typing.png",
        sb.screenshot,
        timeout,
    ):
        all_ok = False

    await run_step("mouse.double_click", sb.mouse.double_click(cx, cy), timeout)
    record(report, "mouse_double_click", True)

    if not await _capture(
        report,
        shots_dir,
        "screenshot final",
        "07_final.png",
        lambda: sb.screen.screenshot(format="png"),
        timeout,
    ):
        all_ok = False

    return all_ok


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
    _, Sandbox = cua
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
    shots_dir = output_dir / "screenshots"

    section(f"Linux sandbox ({LINUX_CONTAINER_IMAGE})")
    try:
        async with Sandbox.ephemeral(
            linux_container_image(),
            local=True,
            runtime=linux_docker_runtime(),
        ) as sb:
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

            ui_ok = await _run_ui_scenario(sb, shots_dir, args.timeout, report)
            if not ui_ok:
                report.error = "one or more UI/screenshot steps failed"
                dump_cua_diagnostics(args.log_tail)
                _write_report(args.output_dir, report)
                return 1

        report.passed = True
        log("Linux sandbox smoke test passed")
        log(f"screenshots: {output_dir / 'screenshots'}")
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
        "screen_size": report.screen_size,
        "screenshots": report.screenshots,
        "screenshot": report.screenshot,
        "error": report.error,
        "steps": [asdict(step) for step in report.steps],
    }
    path = output_dir / "linux_smoke_report.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    log(f"report saved: {path}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Smoke-test Cua local Linux sandbox: shell, mouse/keyboard UI, "
            "multi-step screenshots."
        ),
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
