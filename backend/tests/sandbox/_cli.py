"""Shared CLI helpers for sandbox smoke tests."""

from __future__ import annotations

import sys
import time
from typing import Any, Awaitable, TypeVar

T = TypeVar("T")


def log(message: str) -> None:
    print(f"==> {message}", flush=True)


def warn(message: str) -> None:
    print(f"warning: {message}", file=sys.stderr, flush=True)


def fail(message: str) -> None:
    print(f"error: {message}", file=sys.stderr, flush=True)


def section(title: str) -> None:
    print(f"\n## {title}", flush=True)


async def run_step(label: str, coro: Awaitable[T], timeout: float) -> T:
    import asyncio

    log(f"{label} ...")
    start = time.monotonic()
    try:
        result = await asyncio.wait_for(coro, timeout=timeout)
    except asyncio.TimeoutError as exc:
        raise asyncio.TimeoutError(f"{label} timed out after {timeout}s") from exc
    log(f"{label} ok ({time.monotonic() - start:.1f}s)")
    return result


def check_python_version() -> bool:
    import sys

    if sys.version_info < (3, 12) or sys.version_info >= (3, 14):
        fail(
            "Cua Sandbox SDK requires Python 3.12 or 3.13; "
            f"current Python is {sys.version.split()[0]}"
        )
        return False
    return True


def print_runtime_info() -> None:
    import importlib.metadata
    import sys

    try:
        cua_version = importlib.metadata.version("cua")
    except importlib.metadata.PackageNotFoundError:
        cua_version = "not installed"
    log(f"Python: {sys.version.split()[0]} ({sys.executable})")
    log(f"cua package: {cua_version}")


def import_cua() -> tuple[Any, Any] | None:
    try:
        from cua import Image, Sandbox

        return Image, Sandbox
    except ImportError as exc:
        fail(f"Could not import cua: {exc}")
        fail("Install with: python -m pip install -r requirements.txt")
        return None
