#!/usr/bin/env python3
"""Entry shim for android_ctl (see backend/src/sandbox/android_ctl.py)."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from sandbox.android_ctl import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
