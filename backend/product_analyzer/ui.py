"""终端 I/O 基元:log/err/prompt_str/Spinner。

只依赖 ``config``,被几乎所有上层模块使用。"""

from __future__ import annotations

import sys
import threading
import time

from .config import CYAN, DIM, RESET, USE_COLOR


def log(msg: str) -> None:
    print(f"==> {msg}", flush=True)


def err(msg: str) -> None:
    print(f"error: {msg}", file=sys.stderr, flush=True)


def prompt_str(
    prompt: str,
    validate=lambda s: bool(s.strip()),
    allow_empty: bool = False,
) -> str:
    """Loop ``input()`` until ``validate`` passes. Empty allowed when
    ``allow_empty=True`` (returns "")."""
    while True:
        try:
            value = input(prompt).strip()
        except EOFError:
            err("输入流被关闭,中止")
            sys.exit(1)
        except KeyboardInterrupt:
            err("用户中断")
            sys.exit(1)
        if allow_empty and not value:
            return ""
        if validate(value):
            return value
        print("  输入无效,请重新输入")


class Spinner:
    """A self-erasing one-line loading indicator that lives on the bottom of
    the terminal while real output streams above it.

    Usage:
        sp = Spinner()
        sp.start()
        for line in stream:
            sp.write_above(line)   # erase, print real content, re-paint
            sp.set_label(...)
        sp.stop()

    Auto-disabled when not a tty (CI / pipe / redirect)."""

    FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

    def __init__(self):
        self.enabled = sys.stdout.isatty() and USE_COLOR
        self._label = "starting"
        self._frame_idx = 0
        self._lock: threading.Lock | None = None
        self._thread: threading.Thread | None = None
        self._stop: threading.Event | None = None
        self._painted = False
        self._start_time = 0.0

    def _paint(self) -> None:
        if not self.enabled:
            return
        elapsed = time.time() - self._start_time
        glyph = self.FRAMES[self._frame_idx % len(self.FRAMES)]
        line = f"{CYAN}{glyph}{RESET} {DIM}{self._label} · {elapsed:.0f}s · ESC 暂停{RESET}"
        sys.stdout.write("\r\x1b[2K" + line)
        sys.stdout.flush()
        self._painted = True

    def _erase(self) -> None:
        if not self.enabled or not self._painted:
            return
        sys.stdout.write("\r\x1b[2K")
        sys.stdout.flush()
        self._painted = False

    def _loop(self) -> None:
        assert self._stop is not None and self._lock is not None
        while not self._stop.is_set():
            with self._lock:
                self._paint()
                self._frame_idx += 1
            self._stop.wait(0.1)
        with self._lock:
            self._erase()

    def start(self) -> None:
        if not self.enabled:
            return
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._start_time = time.time()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        if not self.enabled or self._thread is None:
            return
        assert self._stop is not None and self._lock is not None
        self._stop.set()
        self._thread.join(timeout=1)
        with self._lock:
            self._erase()
        self._thread = None

    def set_label(self, label: str | None) -> None:
        self._label = label or "thinking"

    def write_above(self, line: str) -> None:
        """Print a line above the spinner: erase, print, re-paint."""
        if not self.enabled:
            print(line, flush=True)
            return
        assert self._lock is not None
        with self._lock:
            self._erase()
            sys.stdout.write(line + "\n")
            sys.stdout.flush()
            self._paint()
