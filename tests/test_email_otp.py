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
from product_analyzer import credentials as cred_store  # noqa: E402
from product_analyzer.tasks import write_metadata_seed  # noqa: E402
from product_analyzer.workflow import load_workflow, redact_text, seed_workflow  # noqa: E402


class _FakeKeyring:
    class errors:  # noqa: N801
        class PasswordDeleteError(Exception):
            pass

    def __init__(self) -> None:
        self.store: dict[tuple[str, str], str] = {}

    def get_password(self, service, key):
        return self.store.get((service, key))

    def set_password(self, service, key, value):
        self.store[(service, key)] = value

    def delete_password(self, service, key):
        if (service, key) not in self.store:
            raise self.errors.PasswordDeleteError()
        del self.store[(service, key)]


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
                    "ANALYZER_CONFIG_DIR": tmp,
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
                    "ANALYZER_CONFIG_DIR": tmp,
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


class TestCredentialStore(unittest.TestCase):
    def setUp(self) -> None:
        self._fake_kr = _FakeKeyring()
        patcher = mock.patch.object(cred_store, "_keyring", return_value=self._fake_kr)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_cred_put_get_list_roundtrip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp)
            write_metadata_seed(out_dir, "Example Product", "https://example.com", None)
            seed_workflow(out_dir)

            put = email_otp.cred_put(out_dir, "login account", {"username": "u@x.com", "password": "pw"})
            self.assertTrue(put["ok"])
            self.assertEqual(put["product"], "Example Product")
            self.assertEqual(put["field_names"], ["password", "username"])

            listing = email_otp.cred_list(out_dir)
            self.assertEqual(len(listing["credentials"]), 1)
            entry = listing["credentials"][0]
            self.assertEqual(entry["label"], "login account")
            # 列表只含元数据,不含 secret 值
            self.assertNotIn("fields", entry)
            self.assertNotIn("pw", json.dumps(listing, ensure_ascii=False))

            got = email_otp.cred_get(out_dir)
            self.assertTrue(got["ok"])
            self.assertEqual(got["fields"], {"username": "u@x.com", "password": "pw"})

    def test_cred_get_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp)
            write_metadata_seed(out_dir, "No Creds", "https://example.com", None)
            seed_workflow(out_dir)
            got = email_otp.cred_get(out_dir)
            self.assertFalse(got["ok"])
            self.assertEqual(got["error"], "not_found")

    def test_cred_isolated_per_product(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            a = Path(tmp) / "a"
            b = Path(tmp) / "b"
            a.mkdir()
            b.mkdir()
            write_metadata_seed(a, "Product A", "https://a.com", None)
            write_metadata_seed(b, "Product B", "https://b.com", None)
            seed_workflow(a)
            seed_workflow(b)
            email_otp.cred_put(a, "acct", {"username": "a@x.com"})
            # B 看不到 A 的凭据
            self.assertFalse(email_otp.cred_get(b)["ok"])
            self.assertEqual(len(email_otp.cred_list(b)["credentials"]), 0)
            self.assertEqual(len(email_otp.cred_list(b, all_products=True)["credentials"]), 1)


if __name__ == "__main__":
    unittest.main()
