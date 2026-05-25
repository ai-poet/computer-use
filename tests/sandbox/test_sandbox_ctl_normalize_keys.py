#!/usr/bin/env python3
"""Unit tests for sandbox_ctl key normalization (no Docker)."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO_ROOT / "backend"))

from product_analyzer.sandbox_ctl import (  # noqa: E402
    _LINUX_FIREFOX_LAUNCH_SHELL,
    _normalize_keys,
)


class TestFirefoxLaunchShell(unittest.TestCase):
    def test_uses_firefox_not_chromium(self) -> None:
        low = _LINUX_FIREFOX_LAUNCH_SHELL.lower()
        self.assertIn("firefox", low)
        self.assertNotIn("chromium", low)
        self.assertIn("/tmp/.x11-unix", low)


class TestNormalizeKeys(unittest.TestCase):
    def test_enter_aliases(self) -> None:
        self.assertEqual(_normalize_keys("enter"), ["enter"])
        self.assertEqual(_normalize_keys("return"), ["enter"])
        self.assertEqual(_normalize_keys("Return"), ["enter"])

    def test_escape_aliases(self) -> None:
        self.assertEqual(_normalize_keys("Escape"), ["esc"])
        self.assertEqual(_normalize_keys("esc"), ["esc"])

    def test_page_and_delete_aliases(self) -> None:
        self.assertEqual(_normalize_keys("PageDown"), ["page_down"])
        self.assertEqual(_normalize_keys("pgdn"), ["page_down"])
        self.assertEqual(_normalize_keys("del"), ["delete"])

    def test_super_maps_to_cmd(self) -> None:
        self.assertEqual(_normalize_keys("meta"), ["cmd"])
        self.assertEqual(_normalize_keys("super"), ["cmd"])

    def test_hotkey_lowercase(self) -> None:
        self.assertEqual(_normalize_keys("Ctrl+L"), ["ctrl", "l"])
        self.assertEqual(_normalize_keys("ctrl+shift+t"), ["ctrl", "shift", "t"])

    def test_no_pascal_case_leak(self) -> None:
        for raw in ("enter", "return", "Escape", "ctrl+l"):
            for k in _normalize_keys(raw):
                self.assertEqual(k, k.lower(), msg=f"{raw!r} -> {k!r}")


if __name__ == "__main__":
    unittest.main()
