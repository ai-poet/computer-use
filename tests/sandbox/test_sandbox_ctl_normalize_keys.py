#!/usr/bin/env python3
"""Unit tests for sandbox_ctl key normalization (no Docker)."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO_ROOT / "scripts"))

from product_analyzer.sandbox_ctl import _normalize_keys  # noqa: E402


class TestNormalizeKeys(unittest.TestCase):
    def test_enter_aliases(self) -> None:
        self.assertEqual(_normalize_keys("enter"), ["enter"])
        self.assertEqual(_normalize_keys("return"), ["enter"])
        self.assertEqual(_normalize_keys("Return"), ["enter"])

    def test_escape_aliases(self) -> None:
        self.assertEqual(_normalize_keys("Escape"), ["escape"])
        self.assertEqual(_normalize_keys("esc"), ["escape"])

    def test_hotkey_lowercase(self) -> None:
        self.assertEqual(_normalize_keys("Ctrl+L"), ["ctrl", "l"])
        self.assertEqual(_normalize_keys("ctrl+shift+t"), ["ctrl", "shift", "t"])

    def test_no_pascal_case_leak(self) -> None:
        for raw in ("enter", "return", "Escape", "ctrl+l"):
            for k in _normalize_keys(raw):
                self.assertEqual(k, k.lower(), msg=f"{raw!r} -> {k!r}")


if __name__ == "__main__":
    unittest.main()
