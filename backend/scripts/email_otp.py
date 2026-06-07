#!/usr/bin/env python3
"""Entry shim for email_otp (see backend/src/analysis/email_otp.py).

取代旧的 ``python -m product_analyzer.email_otp`` 调用方式。
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from analysis.email_otp import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
