#!/usr/bin/env python3
"""启动 Product Analyzer 后端服务器。

从任意目录调用时自动定位到 backend/src 并启动 server。
用法:
    python3 backend/scripts/start_server.py [--host HOST] [--port PORT] [--reload]
"""
from __future__ import annotations

import os
import sys
from pathlib import Path


def _ensure_src_on_path() -> None:
    this_file = Path(__file__).resolve()
    backend_dir = this_file.parent.parent
    src_dir = backend_dir / "src"
    project_root = backend_dir.parent

    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    os.chdir(str(backend_dir))


def main() -> int:
    _ensure_src_on_path()
    from web.server import main as server_main

    return server_main()


if __name__ == "__main__":
    raise SystemExit(main())
