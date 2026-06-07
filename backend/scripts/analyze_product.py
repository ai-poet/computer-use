#!/usr/bin/env python3
"""analyze_product.py — CLI 入口 shim。

实际实现在 ``backend/src/`` 下的分包里(依赖图见 CLAUDE.md / AGENTS.md)。
这层只负责把 ``backend/src`` 加入 ``sys.path`` 后调 ``analysis.cli.main``。
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from analysis.cli import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
