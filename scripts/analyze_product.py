#!/usr/bin/env python3
"""analyze_product.py — 入口 shim。

实际实现在 ``scripts/product_analyzer/`` 包里,模块依赖图见
``product_analyzer/__init__.py`` 的 docstring。
这层只负责把 ``scripts/`` 加入 ``sys.path`` 后调 ``main``。
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from product_analyzer import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
