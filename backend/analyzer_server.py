#!/usr/bin/env python3
"""Run the local product-analyzer web console backend."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

from product_analyzer.server import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())
