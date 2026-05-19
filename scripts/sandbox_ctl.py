#!/usr/bin/env python3
"""Entry shim for sandbox_ctl (see product_analyzer.sandbox_ctl)."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from product_analyzer.sandbox_ctl import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
