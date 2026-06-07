#!/usr/bin/env python3
"""Entry shim for workflow_cli (see backend/src/analysis/workflow_cli.py).

取代旧的 ``python -m product_analyzer.workflow_cli`` 调用方式。
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from analysis.workflow_cli import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
