#!/usr/bin/env python3
"""Entry shim for android_ctl (see product_analyzer.android_ctl)."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from product_analyzer.android_ctl import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
