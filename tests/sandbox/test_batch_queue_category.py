#!/usr/bin/env python3
"""Unit tests for batch queue category output paths (no Docker)."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

_REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO_ROOT / "backend"))

from product_analyzer.batch import load_queue, queue_category_from_path  # noqa: E402
from product_analyzer.server import _run_id  # noqa: E402
from product_analyzer.tasks import prepare_output_dir  # noqa: E402


class TestQueueCategory(unittest.TestCase):
    def test_category_from_queue_filename(self) -> None:
        self.assertEqual(
            queue_category_from_path(Path("queue.language-learning.json")),
            "language-learning",
        )
        self.assertEqual(
            queue_category_from_path(Path("queue.desktop-pets.csv")),
            "desktop-pets",
        )
        self.assertEqual(queue_category_from_path(Path("queue.json")), "queue")

    def test_load_queue_adds_category_and_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "queue.coding-platforms.json"
            path.write_text(
                json.dumps(
                    [
                        {
                            "product_name": "Example",
                            "url": "https://example.com",
                        }
                    ]
                ),
                encoding="utf-8",
            )
            rows = load_queue(path)
        self.assertEqual(rows[0]["queue_category"], "coding-platforms")
        self.assertEqual(rows[0]["queue_file"], "queue.coding-platforms.json")

    def test_row_category_overrides_filename(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "queue.misc.json"
            path.write_text(
                json.dumps(
                    [
                        {
                            "category": "custom-category",
                            "product_name": "Example",
                            "url": "https://example.com",
                        }
                    ]
                ),
                encoding="utf-8",
            )
            rows = load_queue(path)
        self.assertEqual(rows[0]["queue_category"], "custom-category")

    def test_prepare_output_dir_uses_category_subdir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch("product_analyzer.tasks.REPORTS_DIR", Path(tmp)):
                out = prepare_output_dir("Example Product", category="Language Learning")
        self.assertEqual(out.parent.name, "language-learning")
        self.assertTrue(out.name.startswith("example-product-"))

    def test_server_run_id_encodes_category_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "language-learning" / "example-2026-05-25"
            out.mkdir(parents=True)
            with mock.patch("product_analyzer.server.REPORTS_DIR", Path(tmp)):
                self.assertEqual(_run_id(out), "language-learning~example-2026-05-25")


if __name__ == "__main__":
    unittest.main()
