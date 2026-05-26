#!/usr/bin/env python3
"""启动 Product Analyzer 后端服务器。

从任意目录调用时自动定位到 backend/ 并启动 server。
用法:
    python3 backend/start_server.py [--host HOST] [--port PORT] [--reload]
    python3 -m backend.start_server [--host HOST] [--port PORT] [--reload]
"""
from __future__ import annotations

import os
import sys
from pathlib import Path


def _ensure_backend_on_path() -> None:
    this_file = Path(__file__).resolve()
    backend_dir = this_file.parent
    project_root = backend_dir.parent

    if str(backend_dir) not in sys.path:
        sys.path.insert(0, str(backend_dir))
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    os.chdir(str(backend_dir))


def main() -> int:
    _ensure_backend_on_path()
    from product_analyzer.server import main as server_main

    return server_main()


if __name__ == "__main__":
    raise SystemExit(main())
