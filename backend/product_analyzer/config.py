"""路径常量 + ANSI 配色。无内部依赖,所有其它模块都可以导入它。"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# ---------- paths ----------

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
BACKEND_DIR = REPO_ROOT / "backend"
REPORTS_DIR = REPO_ROOT / "reports"
INSTALL_SCRIPT = BACKEND_DIR / "install_cua_driver.py"

SWIFT_APP_BUNDLE = Path("/Applications/CuaDriver.app")
RS_APP_BUNDLE = Path("/Applications/CuaDriverRs.app")
RS_HOME_DIR = Path.home() / ".cua-driver-rs"

# ---------- color ----------

_ANSI_CODES: dict[str, str] = {
    "RESET": "\x1b[0m",
    "DIM": "\x1b[2m",
    "BOLD": "\x1b[1m",
    "ITAL": "\x1b[3m",
    "GRAY": "\x1b[90m",
    "CYAN": "\x1b[36m",
    "GREEN": "\x1b[32m",
    "YELLOW": "\x1b[33m",
    "RED": "\x1b[31m",
    "MAGENTA": "\x1b[35m",
    "BLUE": "\x1b[34m",
}


def use_terminal_color() -> bool:
    force = os.environ.get("ANALYZER_FORCE_COLOR", "").strip().lower()
    if force in ("1", "true", "yes", "on"):
        return True
    if os.environ.get("NO_COLOR", ""):
        return False
    return sys.stdout.isatty()


def _c(code: str) -> str:
    return code if use_terminal_color() else ""


def __getattr__(name: str) -> str:
    if name == "USE_COLOR":
        return use_terminal_color()  # type: ignore[return-value]
    if name in _ANSI_CODES:
        return _c(_ANSI_CODES[name])
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
