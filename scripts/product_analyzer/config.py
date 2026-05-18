"""路径常量 + ANSI 配色。无内部依赖,所有其它模块都可以导入它。"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# ---------- paths ----------

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
REPORTS_DIR = REPO_ROOT / "reports"
INSTALL_SCRIPT = SCRIPTS_DIR / "install_cua_driver.py"

SWIFT_APP_BUNDLE = Path("/Applications/CuaDriver.app")
RS_APP_BUNDLE = Path("/Applications/CuaDriverRs.app")
RS_HOME_DIR = Path.home() / ".cua-driver-rs"

# ---------- color ----------

USE_COLOR = sys.stdout.isatty() and os.environ.get("NO_COLOR", "") == ""


def _c(code: str) -> str:
    return code if USE_COLOR else ""


RESET = _c("\x1b[0m")
DIM = _c("\x1b[2m")
BOLD = _c("\x1b[1m")
ITAL = _c("\x1b[3m")
GRAY = _c("\x1b[90m")
CYAN = _c("\x1b[36m")
GREEN = _c("\x1b[32m")
YELLOW = _c("\x1b[33m")
RED = _c("\x1b[31m")
MAGENTA = _c("\x1b[35m")
BLUE = _c("\x1b[34m")
