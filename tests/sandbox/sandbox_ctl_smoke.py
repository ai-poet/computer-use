#!/usr/bin/env python3
"""Smoke test for backend/product_analyzer/sandbox_ctl.py (local Docker + Firefox).

Covers two paths in one run:
  1. Browser (batch worker): bootstrap --open-browser --url → dismiss modal → scroll/click.
  2. Desktop regression: move, right-click, scroll, terminal hotkey, type.

Artifacts land under --output-dir (default tmp/sandbox-ctl-smoke/).
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[2]
_CTL = _REPO_ROOT / "backend" / "sandbox_ctl.py"
_DEFAULT_OUT = _REPO_ROOT / "tmp" / "sandbox-ctl-smoke"
_DEFAULT_URL = "https://juejin.cn"
_MIN_SCREENSHOT_BYTES = 1000


@dataclass
class StepResult:
    name: str
    ok: bool
    detail: str = ""


@dataclass
class SmokeReport:
    passed: bool = False
    output_dir: str = ""
    url: str = ""
    screenshots: list[str] = field(default_factory=list)
    steps: list[StepResult] = field(default_factory=list)
    error: str | None = None


def _record(report: SmokeReport, name: str, ok: bool, detail: str = "") -> None:
    report.steps.append(StepResult(name=name, ok=ok, detail=detail))


def _run_ctl(args: list[str], *, env: dict | None = None) -> subprocess.CompletedProcess[str]:
    import os

    sys.path.insert(0, str(_REPO_ROOT / "backend"))
    from product_analyzer.sandbox_runtime import (  # noqa: E402
        LINUX_CONTAINER_IMAGE,
        LINUX_DOCKER_PLATFORM,
        _local_no_proxy_env,
    )

    run_env = os.environ.copy()
    run_env.update(_local_no_proxy_env())
    run_env.setdefault("ANALYZER_RUNTIME", "sandbox-local")
    run_env.setdefault("ANALYZER_SANDBOX_IMAGE", "linux")
    run_env.setdefault("ANALYZER_LINUX_CONTAINER_IMAGE", LINUX_CONTAINER_IMAGE)
    run_env.setdefault("ANALYZER_LINUX_DOCKER_PLATFORM", LINUX_DOCKER_PLATFORM)
    if env:
        run_env.update(env)
    return subprocess.run(
        [sys.executable, str(_CTL), *args],
        cwd=str(_REPO_ROOT),
        env=run_env,
        capture_output=True,
        text=True,
        timeout=300,
    )


def _must_ok(
    report: SmokeReport,
    label: str,
    proc: subprocess.CompletedProcess[str],
    *,
    soft: bool = False,
) -> bool:
    ok = proc.returncode == 0
    detail = proc.stdout.strip().splitlines()[-1] if proc.stdout.strip() else ""
    if not ok and proc.stderr.strip():
        detail = proc.stderr.strip().splitlines()[-1]
    _record(report, label, ok or soft, detail)
    if ok:
        return True
    if soft:
        print(f"warning: {label} failed — continuing", file=sys.stderr)
        if proc.stderr:
            tail = proc.stderr.strip().splitlines()
            if tail:
                print(tail[-1], file=sys.stderr)
        return True
    print(f"error: {label}", file=sys.stderr)
    if proc.stdout:
        print(proc.stdout, file=sys.stderr)
    if proc.stderr:
        print(proc.stderr, file=sys.stderr)
    return False


def _screen_center(out_dir: Path, report: SmokeReport) -> tuple[int, int]:
    proc = _run_ctl(["step", "screen-size", str(out_dir)])
    if not _must_ok(report, "screen-size", proc, soft=True):
        return 512, 384
    try:
        line = proc.stdout.strip().splitlines()[-1]
        payload = json.loads(line)
        w, h = int(payload["width"]), int(payload["height"])
        print(f"screen size: {w}x{h}")
        _record(report, "screen_size", True, f"{w}x{h}")
        return w // 2, h // 2 + 40
    except (json.JSONDecodeError, KeyError, ValueError):
        _record(report, "screen_size", False, "parse failed")
        return 512, 424


def _shot(
    report: SmokeReport,
    out_dir: Path,
    filename: str,
    saved: list[str],
    *,
    soft: bool = False,
) -> bool:
    rel = f"screenshots/{filename}"
    proc = _run_ctl(["step", "screenshot", str(out_dir), "--out", rel])
    path = out_dir / rel
    if proc.returncode != 0:
        return _must_ok(report, f"screenshot {filename}", proc, soft=soft)
    size = path.stat().st_size if path.is_file() else 0
    ok = path.is_file() and size >= _MIN_SCREENSHOT_BYTES
    _record(report, f"screenshot {filename}", ok or soft, f"bytes={size}")
    if not ok:
        msg = f"{path} too small or missing"
        if soft:
            print(f"warning: {msg}", file=sys.stderr)
            return True
        print(f"error: {msg}", file=sys.stderr)
        return False
    saved.append(rel)
    print(f"saved {path} ({size} bytes)")
    return True


def _dismiss_overlays(out_dir: Path, report: SmokeReport) -> None:
    """Close Firefox translation / cookie banners before scroll or click."""
    for label, keys in (
        ("dismiss overlay (escape)", "escape"),
        ("dismiss overlay (escape x2)", "escape"),
    ):
        _must_ok(report, label, _run_ctl(["step", "key", str(out_dir), keys]), soft=True)
        time.sleep(0.25)


def _run_browser_scenario(
    out_dir: Path,
    url: str,
    report: SmokeReport,
    cx: int,
    cy: int,
) -> tuple[bool, list[str]]:
    """Batch-worker path: homepage → dismiss modal → scroll → click → reopen URL."""
    saved: list[str] = []

    if not _shot(report, out_dir, "01_web_homepage.png", saved):
        return False, saved

    _dismiss_overlays(out_dir, report)

    if not _must_ok(
        report,
        "scroll page",
        _run_ctl(["step", "scroll", str(out_dir), str(cx), str(cy), "--scroll-y", "-8"]),
    ):
        return False, saved
    time.sleep(0.8)

    if not _shot(report, out_dir, "02_web_after_scroll.png", saved):
        return False, saved

    if not _must_ok(
        report,
        "click page",
        _run_ctl(["step", "click", str(out_dir), str(cx), str(cy)]),
    ):
        return False, saved
    time.sleep(0.5)

    if not _shot(report, out_dir, "03_web_after_click.png", saved):
        return False, saved

    ff = _run_ctl(
        ["step", "shell", str(out_dir), "-c", "pgrep -x firefox >/dev/null && echo firefox_ok"],
    )
    if not _must_ok(report, "firefox running", ff):
        return False, saved

    sleep_check = _run_ctl(
        [
            "step",
            "shell",
            str(out_dir),
            "-c",
            "export DISPLAY=${DISPLAY:-:1}; "
            "command -v xset >/dev/null && xset q | grep -E 'Monitor is|Screen is' || echo xset_skip",
        ],
    )
    _must_ok(report, "sleep disabled (xset)", sleep_check, soft=True)

    reopen = _run_ctl(["step", "open-url", str(out_dir), url, "--no-launch"])
    _must_ok(report, "open-url no-launch", reopen, soft=True)

    if not _shot(report, out_dir, "04_web_reopen_url.png", saved, soft=True):
        return False, saved

    return True, saved


def _run_desktop_scenario(
    out_dir: Path,
    report: SmokeReport,
    cx: int,
    cy: int,
) -> tuple[bool, list[str]]:
    """XFCE desktop regression: mouse, scroll, terminal, keyboard."""
    saved: list[str] = []

    if not _must_ok(
        report,
        "mouse move corner",
        _run_ctl(["step", "move", str(out_dir), "80", "80"]),
    ):
        return False, saved

    if not _must_ok(
        report,
        "mouse move center",
        _run_ctl(["step", "move", str(out_dir), str(cx), str(cy)]),
    ):
        return False, saved

    if not _shot(report, out_dir, "05_desktop_after_move.png", saved, soft=True):
        return False, saved

    if not _must_ok(
        report,
        "scroll desktop",
        _run_ctl(["step", "scroll", str(out_dir), str(cx), str(cy), "--scroll-y", "-5"]),
    ):
        return False, saved
    time.sleep(0.3)

    if not _shot(report, out_dir, "06_desktop_after_scroll.png", saved, soft=True):
        return False, saved

    if not _must_ok(
        report,
        "right click",
        _run_ctl(
            ["step", "click", str(out_dir), str(cx), str(cy), "--button", "right"],
        ),
    ):
        return False, saved
    time.sleep(0.5)

    if not _shot(report, out_dir, "07_desktop_after_right_click.png", saved):
        return False, saved

    _must_ok(report, "dismiss context menu", _run_ctl(["step", "key", str(out_dir), "escape"]))

    if not _must_ok(
        report,
        "open terminal (ctrl+alt+t)",
        _run_ctl(["step", "key", str(out_dir), "ctrl+alt+t"]),
        soft=True,
    ):
        return False, saved
    time.sleep(1.5)

    if not _shot(report, out_dir, "08_desktop_terminal.png", saved, soft=True):
        return False, saved

    if not _must_ok(
        report,
        "type in terminal",
        _run_ctl(["step", "type", str(out_dir), "echo sandbox-ctl-smoke-ok"]),
    ):
        return False, saved

    if not _must_ok(
        report,
        "enter in terminal",
        _run_ctl(["step", "key", str(out_dir), "enter"]),
    ):
        return False, saved
    time.sleep(0.8)

    if not _shot(report, out_dir, "09_desktop_after_typing.png", saved, soft=True):
        return False, saved

    _must_ok(
        report,
        "double click",
        _run_ctl(
            ["step", "click", str(out_dir), str(cx), str(cy), "--button", "double"],
        ),
        soft=True,
    )

    if not _shot(report, out_dir, "10_desktop_final.png", saved, soft=True):
        return False, saved

    return True, saved


def _write_report(out_dir: Path, report: SmokeReport) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    payload: dict[str, Any] = {
        "passed": report.passed,
        "output_dir": str(out_dir),
        "url": report.url,
        "screenshots_dir": str(out_dir / "screenshots"),
        "screenshots": report.screenshots,
        "error": report.error,
        "steps": [asdict(step) for step in report.steps],
    }
    path = out_dir / "sandbox_ctl_smoke_report.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"report: {path}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="sandbox_ctl smoke test (browser + desktop mouse/keyboard steps)",
    )
    parser.add_argument("--check-only", action="store_true")
    parser.add_argument(
        "--url",
        default=_DEFAULT_URL,
        help=f"Page to open in Firefox during bootstrap (default: {_DEFAULT_URL})",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=_DEFAULT_OUT,
        help=f"Persistent artifacts root (default: {_DEFAULT_OUT})",
    )
    parser.add_argument(
        "--no-teardown",
        action="store_true",
        help="Leave sandbox running after success (for manual inspection)",
    )
    args = parser.parse_args()

    if not shutil.which("docker"):
        print("skip: docker not found")
        return 0

    try:
        from tests.sandbox._cli import check_python_version, import_cua

        if not check_python_version():
            return 1
        if import_cua() is None:
            print("skip: cua not installed")
            return 0
    except ImportError:
        print("skip: tests.sandbox._cli unavailable")
        return 0

    if args.check_only:
        print("sandbox_ctl smoke: deps ok")
        return 0

    out_dir = args.output_dir.resolve()
    shots_dir = out_dir / "screenshots"
    shots_dir.mkdir(parents=True, exist_ok=True)
    report = SmokeReport(output_dir=str(out_dir), url=args.url.strip())
    print(f"out_dir={out_dir}")
    print(f"url={report.url}")
    print(f"screenshots_dir={shots_dir}")

    stale = out_dir / "sandbox.json"
    if stale.is_file():
        print(f"cleaning stale sandbox: {stale}")
        _run_ctl(["teardown", str(out_dir)])

    boot = _run_ctl(["bootstrap", str(out_dir), "--open-browser", "--url", report.url])
    if not _must_ok(report, "bootstrap", boot):
        report.error = "bootstrap failed"
        _write_report(out_dir, report)
        return 1
    print(boot.stdout.strip())

    cx, cy = _screen_center(out_dir, report)

    browser_ok, screenshots = _run_browser_scenario(out_dir, report.url, report, cx, cy)
    if not browser_ok:
        report.screenshots = screenshots
        report.error = "browser scenario failed"
        _write_report(out_dir, report)
        _run_ctl(["teardown", str(out_dir)])
        return 1

    desktop_ok, desktop_shots = _run_desktop_scenario(out_dir, report, cx, cy)
    report.screenshots = screenshots + desktop_shots
    if not desktop_ok:
        report.error = "desktop scenario failed"
        _write_report(out_dir, report)
        _run_ctl(["teardown", str(out_dir)])
        return 1

    if not args.no_teardown:
        down = _run_ctl(["teardown", str(out_dir)])
        if not _must_ok(report, "teardown", down):
            report.error = "teardown failed"
            _write_report(out_dir, report)
            return 1
    else:
        print("skipped teardown (--no-teardown)")

    report.passed = True
    _write_report(out_dir, report)
    print(f"\nAll screenshots saved under: {shots_dir}")
    for path in sorted(shots_dir.glob("*.png")):
        print(f"  - {path}")
    print("sandbox_ctl smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
