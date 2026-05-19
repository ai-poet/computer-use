"""预检:确保依赖工具就位再让 Claude 起跑。

- ``detect_host`` 归一化平台标记(其它模块用,比如往 metadata 写主机信息)
- ``ensure_claude_cli``:claude CLI 必须在 PATH
- ``ensure_cua_driver``:不在就调 ``install_cua_driver.py``
"""

from __future__ import annotations

import os
import platform
import shutil
import subprocess
import sys
import importlib.util

from .config import INSTALL_SCRIPT, RS_APP_BUNDLE, RS_HOME_DIR, SWIFT_APP_BUNDLE
from .ui import err, log


def detect_host() -> tuple[str, str]:
    """Return ``(os_name, arch)`` normalized to {darwin/linux/windows} ×
    {arm64/x86_64/<raw>}."""
    sys_lower = platform.system().lower()
    if sys_lower == "darwin":
        os_name = "darwin"
    elif sys_lower == "linux":
        os_name = "linux"
    elif sys_lower.startswith("win") or sys_lower == "windows":
        os_name = "windows"
    else:
        os_name = sys_lower

    machine = platform.machine().lower()
    if machine in ("amd64", "x86_64"):
        arch = "x86_64"
    elif machine in ("arm64", "aarch64"):
        arch = "arm64"
    else:
        arch = machine
    return os_name, arch


def cua_driver_installed() -> bool:
    """Detect Swift cua-driver OR cua-driver-rs."""
    if SWIFT_APP_BUNDLE.exists() or RS_APP_BUNDLE.exists() or RS_HOME_DIR.exists():
        return True
    found = shutil.which("cua-driver")
    if not found:
        return False
    real = os.path.realpath(found)
    return any(tag in real for tag in ("CuaDriver.app", "CuaDriverRs.app", "/.cua-driver-rs/"))


def ensure_claude_cli() -> None:
    if shutil.which("claude"):
        return
    err("未找到 `claude` CLI。请先安装 Claude Code:")
    err("  https://docs.claude.com/en/docs/claude-code")
    sys.exit(1)


def ensure_cua_driver() -> None:
    if cua_driver_installed():
        log("cua-driver 已安装")
        return
    log("cua-driver 未安装,自动调用 install_cua_driver.py 安装中...")
    if not INSTALL_SCRIPT.exists():
        err(f"找不到 {INSTALL_SCRIPT}")
        sys.exit(1)
    proxy_set = any(os.environ.get(k) for k in ("https_proxy", "HTTPS_PROXY", "all_proxy", "ALL_PROXY"))
    if not proxy_set:
        log("提示:install_cua_driver.py 会从 GitHub 下载安装包,如需代理请先 `export https_proxy=...`")
    rc = subprocess.call([sys.executable, str(INSTALL_SCRIPT)])
    if rc != 0:
        err(f"install_cua_driver.py 退出码 {rc};请手动跑一次后重试")
        sys.exit(1)
    if not cua_driver_installed():
        err("安装脚本退出码 0 但仍未检测到 cua-driver,请手动检查 PATH")
        sys.exit(1)
    log("cua-driver 安装完成")


def ensure_cua_sdk() -> None:
    """Ensure the Cua Sandbox SDK import is available for sandbox workers."""
    if importlib.util.find_spec("cua") is not None:
        return
    err("未找到 `cua` Python 包。批量本地沙箱模式需要先安装 Cua Sandbox SDK:")
    err("  python3 -m pip install -r requirements.txt")
    sys.exit(1)


def check_local_sandbox_prereqs(sandbox_image: str = "auto") -> list[str]:
    """Return non-fatal warnings for missing local sandbox runtimes."""
    warnings: list[str] = []
    image = sandbox_image.lower()

    if image in ("auto", "linux") and not shutil.which("docker"):
        warnings.append("local linux sandbox requires Docker, but `docker` was not found")

    if image in ("auto", "macos") and not shutil.which("lume"):
        warnings.append("local macOS sandbox requires Lume, but `lume` was not found")

    qemu_available = any(
        shutil.which(cmd)
        for cmd in ("qemu-system-x86_64", "qemu-system-aarch64", "qemu-system-arm")
    )
    if image in ("auto", "windows") and not qemu_available:
        warnings.append("local Windows sandbox requires QEMU, but no qemu-system binary was found")

    android_sdk_available = shutil.which("adb") and shutil.which("emulator")
    if not android_sdk_available and not qemu_available:
        warnings.append(
            "local Android sandbox requires Android SDK (adb + emulator) or QEMU, "
            "but neither complete runtime was found"
        )

    return warnings
