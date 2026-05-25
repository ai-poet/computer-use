#!/usr/bin/env python3
# cspell:ignore scriptblock
"""
install_cua_driver.py

Picks the right CUA driver for the host:
  - macOS  → Swift `cua-driver` (mature, official macOS build)
  - Linux  → `cua-driver-rs` (Rust port, x86_64 only)
  - Windows → `cua-driver-rs` (PowerShell installer)

If the *other* variant is already installed, it is uninstalled first so the
single `cua-driver` symlink in ~/.local/bin always points at the right backend.

Usage:
    python3 install_cua_driver.py                    # default
    python3 install_cua_driver.py --dry-run          # plan only
    python3 install_cua_driver.py --version 0.2.2    # pin a release
    python3 install_cua_driver.py --no-modify-path

Proxy: respects HTTPS_PROXY / HTTP_PROXY / ALL_PROXY in the parent shell.
"""

from __future__ import annotations

import argparse
import os
import platform
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.request import Request, urlopen


REPO_RAW = "https://raw.githubusercontent.com/trycua/cua/main"

SWIFT_INSTALL_URL = f"{REPO_RAW}/libs/cua-driver/scripts/install.sh"
SWIFT_UNINSTALL_URL = f"{REPO_RAW}/libs/cua-driver/scripts/uninstall.sh"
RS_INSTALL_SH_URL = f"{REPO_RAW}/libs/cua-driver-rs/scripts/install.sh"
RS_INSTALL_PS1_URL = f"{REPO_RAW}/libs/cua-driver-rs/scripts/install.ps1"

SWIFT_APP_BUNDLE = Path("/Applications/CuaDriver.app")
RS_APP_BUNDLE = Path("/Applications/CuaDriverRs.app")
RS_HOME_DIR = Path.home() / ".cua-driver-rs"


def log(msg: str) -> None:
    print(f"==> {msg}", flush=True)


def err(msg: str) -> None:
    print(f"error: {msg}", file=sys.stderr, flush=True)


def detect_platform() -> tuple[str, str]:
    system_name = platform.system().lower()
    if system_name == "darwin":
        os_name = "darwin"
    elif system_name == "linux":
        os_name = "linux"
    elif system_name.startswith("win") or system_name == "windows":
        os_name = "windows"
    else:
        os_name = system_name

    machine = platform.machine().lower()
    if machine in ("amd64", "x86_64"):
        arch = "x86_64"
    elif machine in ("arm64", "aarch64"):
        arch = "arm64"
    else:
        arch = machine
    return os_name, arch


def is_swift_installed() -> bool:
    if SWIFT_APP_BUNDLE.exists():
        return True
    found = shutil.which("cua-driver")
    if not found:
        return False
    real = os.path.realpath(found)
    return "CuaDriver.app" in real and "CuaDriverRs.app" not in real


def is_rust_installed() -> bool:
    if RS_APP_BUNDLE.exists() or RS_HOME_DIR.exists():
        return True
    found = shutil.which("cua-driver")
    if not found:
        return False
    real = os.path.realpath(found)
    return "CuaDriverRs.app" in real or "/.cua-driver-rs/" in real


def fetch_text(url: str) -> str:
    req = Request(url, headers={"User-Agent": "install_cua_driver.py"})
    with urlopen(req, timeout=60) as r:  # noqa: S310
        return r.read().decode("utf-8")


def run_remote_bash(url: str, forwarded_args: list[str], dry_run: bool) -> int:
    if dry_run:
        log(f"[dry-run] would download and run: {url}")
        if forwarded_args:
            log(f"[dry-run] forwarded args: {forwarded_args}")
        return 0
    script = fetch_text(url)
    with tempfile.NamedTemporaryFile("w", suffix=".sh", delete=False) as tf:
        tf.write(script)
        tmp_path = tf.name
    os.chmod(tmp_path, 0o700)
    try:
        return subprocess.call(["/bin/bash", tmp_path, *forwarded_args])
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


def run_remote_powershell(url: str, forwarded_args: list[str], dry_run: bool) -> int:
    if dry_run:
        log(f"[dry-run] would download and run via PowerShell: {url}")
        if forwarded_args:
            log(f"[dry-run] forwarded args: {forwarded_args}")
        return 0
    pwsh = shutil.which("pwsh") or shutil.which("powershell.exe") or "powershell.exe"
    quoted = " ".join(f'"{a}"' for a in forwarded_args)
    cmd = (
        f"$ProgressPreference='SilentlyContinue'; "
        f"$script = (Invoke-WebRequest -UseBasicParsing -Uri '{url}').Content; "
        f"& ([scriptblock]::Create($script)) {quoted}"
    )
    return subprocess.call(
        [pwsh, "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", cmd]
    )


def uninstall_swift(dry_run: bool) -> None:
    log("Swift cua-driver detected; running its uninstall script first...")
    rc = run_remote_bash(SWIFT_UNINSTALL_URL, [], dry_run)
    if rc != 0:
        err(f"Swift uninstall.sh exited {rc}; continuing anyway")
    if SWIFT_APP_BUNDLE.exists() and not dry_run:
        log(f"force-removing leftover {SWIFT_APP_BUNDLE}")
        try:
            shutil.rmtree(SWIFT_APP_BUNDLE)
        except PermissionError:
            err(f"could not remove {SWIFT_APP_BUNDLE} without sudo; remove manually")


def uninstall_rust(dry_run: bool) -> None:
    log("cua-driver-rs detected; removing it before Swift install...")
    if dry_run:
        log(f"[dry-run] would remove {RS_APP_BUNDLE} and {RS_HOME_DIR}")
        log("[dry-run] would remove ~/.local/bin/cua-driver if it points into cua-driver-rs")
        return
    if RS_APP_BUNDLE.exists():
        try:
            shutil.rmtree(RS_APP_BUNDLE)
            log(f"removed {RS_APP_BUNDLE}")
        except PermissionError:
            err(f"could not remove {RS_APP_BUNDLE} without sudo; remove manually")
    if RS_HOME_DIR.exists():
        shutil.rmtree(RS_HOME_DIR, ignore_errors=True)
        log(f"removed {RS_HOME_DIR}")
    bin_link = Path.home() / ".local" / "bin" / "cua-driver"
    if bin_link.is_symlink():
        target = os.readlink(bin_link)
        if "CuaDriverRs.app" in target or ".cua-driver-rs" in target:
            bin_link.unlink()
            log(f"removed stale symlink {bin_link}")


def main() -> int:
    p = argparse.ArgumentParser(
        description="Install Swift cua-driver on macOS, cua-driver-rs elsewhere."
    )
    p.add_argument("--dry-run", action="store_true", help="print actions without executing")
    p.add_argument("--version", help="pin a release tag (e.g. 0.2.2)")
    p.add_argument("--bin-dir", help="override visible install dir; forwarded as --bin-dir")
    p.add_argument("--no-modify-path", action="store_true", help="do not edit shell rc files")
    args = p.parse_args()

    os_name, arch = detect_platform()
    log(f"platform: {os_name}/{arch}")

    forwarded: list[str] = []
    if args.bin_dir:
        forwarded.extend(["--bin-dir", args.bin_dir])
    if args.no_modify_path:
        forwarded.append("--no-modify-path")

    if os_name == "darwin":
        target = "swift"
    elif os_name == "linux":
        if arch != "x86_64":
            err(f"cua-driver-rs has no prebuilt for linux/{arch} (only x86_64).")
            err("Build from source: https://github.com/trycua/cua/tree/main/libs/cua-driver-rs")
            return 2
        target = "rust"
    elif os_name == "windows":
        target = "rust"
    else:
        err(f"unsupported OS: {os_name}")
        return 2

    log(f"selected backend: {target} ({'Swift cua-driver' if target == 'swift' else 'cua-driver-rs'})")

    if args.version:
        if target == "swift":
            os.environ["CUA_DRIVER_VERSION"] = args.version
        else:
            os.environ["CUA_DRIVER_RS_VERSION"] = args.version

    if target == "swift":
        if is_rust_installed():
            uninstall_rust(args.dry_run)
        log("Installing Swift cua-driver (mature macOS build)...")
        return run_remote_bash(SWIFT_INSTALL_URL, forwarded, args.dry_run)

    if is_swift_installed():
        uninstall_swift(args.dry_run)
    if os_name == "windows":
        log("Installing cua-driver-rs (Windows PowerShell installer)...")
        return run_remote_powershell(RS_INSTALL_PS1_URL, forwarded, args.dry_run)
    log("Installing cua-driver-rs (Linux bash installer)...")
    return run_remote_bash(RS_INSTALL_SH_URL, forwarded, args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
