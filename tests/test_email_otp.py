#!/usr/bin/env python3
"""Unit tests for product_analyzer.email_otp (no network)."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

_REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO_ROOT / "backend"))

from product_analyzer import email_otp  # noqa: E402
from product_analyzer.tasks import write_metadata_seed  # noqa: E402
from product_analyzer.workflow import load_workflow, redact_text, seed_workflow  # noqa: E402


class TestEmailOtpConfig(unittest.TestCase):
    def test_auto_prefers_mailosaur(self) -> None:
        cfg = email_otp.resolve_config(
            {
                "ANALYZER_EMAIL_PROVIDER": "auto",
                "MAILOSAUR_API_KEY": "sk-test",
                "MAILOSAUR_SERVER_ID": "srv",
                "MAILOSAUR_SERVER_DOMAIN": "srv.mailosaur.net",
                "ANALYZER_IMAP_HOST": "imap.example.com",
                "ANALYZER_IMAP_USERNAME": "user",
                "ANALYZER_IMAP_PASSWORD": "secret",
                "ANALYZER_EMAIL_ADDRESS": "test@example.com",
            }
        )
        self.assertTrue(cfg.enabled)
        self.assertEqual(cfg.selected_provider, "mailosaur")

    def test_mailosaur_domain_defaults_from_server_id(self) -> None:
        cfg = email_otp.resolve_config(
            {
                "ANALYZER_EMAIL_PROVIDER": "mailosaur",
                "MAILOSAUR_API_KEY": "sk-test",
                "MAILOSAUR_SERVER_ID": "srv123",
            }
        )
        self.assertTrue(cfg.enabled)
        self.assertEqual(cfg.mailosaur_server_domain, "srv123.mailosaur.net")

    def test_auto_falls_back_to_imap(self) -> None:
        cfg = email_otp.resolve_config(
            {
                "ANALYZER_IMAP_HOST": "imap.example.com",
                "ANALYZER_IMAP_USERNAME": "user",
                "ANALYZER_IMAP_PASSWORD": "secret",
                "ANALYZER_EMAIL_ADDRESS": "test@example.com",
            }
        )
        self.assertTrue(cfg.enabled)
        self.assertEqual(cfg.selected_provider, "imap")

    def test_auto_not_configured(self) -> None:
        cfg = email_otp.resolve_config({})
        self.assertFalse(cfg.enabled)
        self.assertEqual(cfg.reason, "not_configured")


class TestEmailOtpAddress(unittest.TestCase):
    def test_create_plus_alias_and_metadata_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp)
            write_metadata_seed(out_dir, "Example Product", "https://example.com", None)
            seed_workflow(out_dir)
            with mock.patch.dict(
                "os.environ",
                {
                    "ANALYZER_EMAIL_PROVIDER": "imap",
                    "ANALYZER_IMAP_HOST": "imap.example.com",
                    "ANALYZER_IMAP_USERNAME": "user",
                    "ANALYZER_IMAP_PASSWORD": "secret",
                    "ANALYZER_EMAIL_ADDRESS": "qa@example.com",
                    "ANALYZER_EMAIL_ALIAS_MODE": "plus",
                },
                clear=True,
            ):
                payload = email_otp.create_address(out_dir)
            self.assertTrue(payload["ok"])
            self.assertRegex(payload["email"], r"^qa\+pa-[0-9a-f]{8}@example\.com$")
            workflow = load_workflow(out_dir)
            self.assertEqual(workflow["registration"]["provider"], "imap")
            self.assertEqual(workflow["registration"]["email_address"], payload["email"])
            meta = json.loads((out_dir / "metadata.json").read_text(encoding="utf-8"))
            self.assertEqual(meta["registration"]["email_domain"], "example.com")
            self.assertNotIn("email_address", meta["registration"])

    def test_force_fixed_address(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp)
            write_metadata_seed(out_dir, "Example", "https://example.com", None)
            seed_workflow(out_dir)
            with mock.patch.dict(
                "os.environ",
                {
                    "ANALYZER_EMAIL_PROVIDER": "imap",
                    "ANALYZER_IMAP_HOST": "imap.example.com",
                    "ANALYZER_IMAP_USERNAME": "user",
                    "ANALYZER_IMAP_PASSWORD": "secret",
                    "ANALYZER_EMAIL_ADDRESS": "qa@example.com",
                },
                clear=True,
            ):
                payload = email_otp.create_address(out_dir, force_fixed=True)
            self.assertEqual(payload["email"], "qa@example.com")


class TestEmailOtpExtraction(unittest.TestCase):
    def test_extract_code_near_keyword(self) -> None:
        text = "Order 123456 was created. Your verification code is 834291."
        self.assertEqual(email_otp.extract_code_from_text(text), "834291")

    def test_extract_chinese_code(self) -> None:
        text = "欢迎注册。您的验证码为 6729，10 分钟内有效。"
        self.assertEqual(email_otp.extract_code_from_text(text), "6729")

    def test_extract_https_verification_link(self) -> None:
        text = "Click https://example.com/verify?token=abc to confirm."
        self.assertEqual(
            email_otp.extract_link_from_text(text),
            "https://example.com/verify?token=abc",
        )

    def test_redact_tool_result_code_and_env_secret(self) -> None:
        raw = '{"ok": true, "code": "123456", "MAILOSAUR_API_KEY": "sk-test"}'
        redacted = redact_text(raw)
        self.assertNotIn("123456", redacted)
        self.assertNotIn("sk-test", redacted)
        self.assertIn("[REDACTED]", redacted)


if __name__ == "__main__":
    unittest.main()
