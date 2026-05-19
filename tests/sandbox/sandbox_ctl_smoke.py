#!/usr/bin/env python3
"""Smoke test for scripts/product_analyzer/sandbox_ctl.py (local Docker)."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_CTL = _REPO_ROOT / "scripts" / "sandbox_ctl.py"


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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-only", action="store_true")
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

    out_dir = Path(tempfile.mkdtemp(prefix="sandbox-ctl-smoke-"))
    print(f"out_dir={out_dir}")

    boot = _run_ctl(["bootstrap", str(out_dir)])
    if boot.returncode != 0:
        print(boot.stdout, boot.stderr)
        return 1
    print(boot.stdout)

    shot = _run_ctl(
        ["step", "screenshot", str(out_dir), "--out", "screenshots/01_smoke.png"]
    )
    if shot.returncode != 0:
        print(shot.stdout, shot.stderr)
        _run_ctl(["teardown", str(out_dir)])
        return 1
    png = out_dir / "screenshots" / "01_smoke.png"
    if not png.is_file() or png.stat().st_size < 1000:
        print(f"screenshot too small: {png}")
        _run_ctl(["teardown", str(out_dir)])
        return 1
    print(f"screenshot ok: {png.stat().st_size} bytes")

    shell = _run_ctl(["step", "shell", str(out_dir), "--", "uname -a"])
    if shell.returncode != 0:
        print(shell.stdout, shell.stderr)
        _run_ctl(["teardown", str(out_dir)])
        return 1
    print(shell.stdout)

    down = _run_ctl(["teardown", str(out_dir)])
    if down.returncode != 0:
        print(down.stdout, down.stderr)
        return 1
    print("sandbox_ctl smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
