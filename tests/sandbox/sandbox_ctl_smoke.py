#!/usr/bin/env python3
"""Smoke test for scripts/product_analyzer/sandbox_ctl.py (local Docker).

Artifacts (screenshots, sandbox.json, report) are written under --output-dir
(default: tmp/sandbox-ctl-smoke/) so you can inspect PNGs after the run.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_CTL = _REPO_ROOT / "scripts" / "sandbox_ctl.py"
_DEFAULT_OUT = _REPO_ROOT / "tmp" / "sandbox-ctl-smoke"
_MIN_SCREENSHOT_BYTES = 1000
_FALLBACK_CX, _FALLBACK_CY = 512, 384


def _run_ctl(args: list[str], *, env: dict | None = None) -> subprocess.CompletedProcess[str]:
    import os

    sys.path.insert(0, str(_REPO_ROOT / "scripts"))
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


def _must_ok(label: str, proc: subprocess.CompletedProcess[str], *, soft: bool = False) -> bool:
    if proc.returncode == 0:
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


def _screen_center(out_dir: Path) -> tuple[int, int]:
    proc = _run_ctl(["step", "screen-size", str(out_dir)])
    if not _must_ok("screen-size", proc, soft=True):
        return _FALLBACK_CX, _FALLBACK_CY
    try:
        line = proc.stdout.strip().splitlines()[-1]
        payload = json.loads(line)
        w, h = int(payload["width"]), int(payload["height"])
        print(f"screen size: {w}x{h}")
        return w // 2, h // 2
    except (json.JSONDecodeError, KeyError, ValueError):
        return _FALLBACK_CX, _FALLBACK_CY


def _shot(out_dir: Path, filename: str, saved: list[str], *, soft: bool = False) -> bool:
    rel = f"screenshots/{filename}"
    proc = _run_ctl(["step", "screenshot", str(out_dir), "--out", rel])
    path = out_dir / rel
    if proc.returncode != 0:
        return _must_ok(f"screenshot {filename}", proc, soft=soft)
    if not path.is_file() or path.stat().st_size < _MIN_SCREENSHOT_BYTES:
        msg = f"{path} too small or missing"
        if soft:
            print(f"warning: {msg}", file=sys.stderr)
            return True
        print(f"error: {msg}", file=sys.stderr)
        return False
    saved.append(rel)
    print(f"saved {path} ({path.stat().st_size} bytes)")
    return True


def _run_ui_scenario(out_dir: Path) -> tuple[bool, list[str]]:
    """Mirror linux_smoke UI steps; PNGs land in out_dir/screenshots/."""
    saved: list[str] = []
    cx, cy = _screen_center(out_dir)

    if not _shot(out_dir, "01_desktop_idle.png", saved):
        return False, saved

    for cmd in (
        ["step", "move", str(out_dir), str(cx), str(cy)],
        ["step", "move", str(out_dir), "80", "80"],
    ):
        if not _must_ok("mouse move", _run_ctl(cmd)):
            return False, saved

    if not _shot(out_dir, "02_after_mouse_move.png", saved):
        return False, saved

    if not _must_ok("click", _run_ctl(["step", "click", str(out_dir), str(cx), str(cy)])):
        return False, saved
    if not _must_ok(
        "right click",
        _run_ctl(["step", "click", str(out_dir), str(cx), str(cy), "--button", "right"]),
    ):
        return False, saved
    time.sleep(0.5)

    if not _shot(out_dir, "03_after_right_click.png", saved):
        return False, saved

    _must_ok("escape", _run_ctl(["step", "key", str(out_dir), "escape"]), soft=True)
    time.sleep(0.3)

    _must_ok(
        "scroll",
        _run_ctl(["step", "scroll", str(out_dir), str(cx), str(cy), "--scroll-y", "-5"]),
        soft=True,
    )
    time.sleep(0.3)

    if not _shot(out_dir, "04_after_scroll.png", saved):
        return False, saved

    _must_ok("hotkey", _run_ctl(["step", "key", str(out_dir), "ctrl+alt+t"]), soft=True)
    time.sleep(1.5)
    _shot(out_dir, "05_terminal_open.png", saved, soft=True)

    _must_ok("type", _run_ctl(["step", "type", str(out_dir), "echo cua-ctl-smoke-ok"]), soft=True)
    _must_ok("enter", _run_ctl(["step", "key", str(out_dir), "enter"]), soft=True)
    time.sleep(0.8)

    if not _shot(out_dir, "06_after_typing.png", saved):
        return False, saved

    _must_ok(
        "double click",
        _run_ctl(["step", "click", str(out_dir), str(cx), str(cy), "--button", "double"]),
        soft=True,
    )

    if not _shot(out_dir, "07_final.png", saved):
        return False, saved

    return True, saved


def _write_report(out_dir: Path, *, passed: bool, screenshots: list[str], error: str | None) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "passed": passed,
        "output_dir": str(out_dir),
        "screenshots_dir": str(out_dir / "screenshots"),
        "screenshots": screenshots,
        "error": error,
    }
    path = out_dir / "sandbox_ctl_smoke_report.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"report: {path}")


def main() -> int:
    parser = argparse.ArgumentParser(description="sandbox_ctl smoke test with persistent screenshots")
    parser.add_argument("--check-only", action="store_true")
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
    print(f"out_dir={out_dir}")
    print(f"screenshots_dir={shots_dir}")

    boot = _run_ctl(["bootstrap", str(out_dir)])
    if boot.returncode != 0:
        _write_report(out_dir, passed=False, screenshots=[], error="bootstrap failed")
        return 1

    print(boot.stdout.strip())

    ui_ok, screenshots = _run_ui_scenario(out_dir)
    if not ui_ok:
        _write_report(out_dir, passed=False, screenshots=screenshots, error="ui scenario failed")
        _run_ctl(["teardown", str(out_dir)])
        return 1

    shell = _run_ctl(["step", "shell", str(out_dir), "--", "uname -a"])
    if shell.returncode != 0:
        print("warning: shell uname failed (screenshots already saved)", file=sys.stderr)
        if shell.stderr:
            print(shell.stderr, file=sys.stderr)
    else:
        print(shell.stdout.strip())

    if not args.no_teardown:
        down = _run_ctl(["teardown", str(out_dir)])
        if down.returncode != 0:
            _write_report(out_dir, passed=False, screenshots=screenshots, error="teardown failed")
            return 1
    else:
        print("skipped teardown (--no-teardown)")

    _write_report(out_dir, passed=True, screenshots=screenshots, error=None)
    print(f"\nAll screenshots saved under: {shots_dir}")
    for path in sorted(shots_dir.glob("*.png")):
        print(f"  - {path}")
    print("sandbox_ctl smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
