#!/usr/bin/env python3
"""Unit tests for product_analyzer.app_config (no network, no real keyring)."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

_REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO_ROOT / "backend"))

from product_analyzer import app_config  # noqa: E402


class _FakeKeyring:
    """Minimal in-memory keyring stand-in."""

    class errors:  # noqa: N801 - mimic keyring.errors namespace
        class PasswordDeleteError(Exception):
            pass

    def __init__(self) -> None:
        self.store: dict[tuple[str, str], str] = {}

    def get_password(self, service: str, key: str):
        return self.store.get((service, key))

    def set_password(self, service: str, key: str, value: str) -> None:
        self.store[(service, key)] = value

    def delete_password(self, service: str, key: str) -> None:
        if (service, key) not in self.store:
            raise self.errors.PasswordDeleteError()
        del self.store[(service, key)]


class AppConfigTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self._fake_kr = _FakeKeyring()
        # 隔离配置目录 + 假 keyring
        patcher_env = mock.patch.dict(
            "os.environ", {"ANALYZER_CONFIG_DIR": self._tmp.name}, clear=False
        )
        patcher_env.start()
        self.addCleanup(patcher_env.stop)
        patcher_kr = mock.patch.object(app_config, "_keyring", return_value=self._fake_kr)
        patcher_kr.start()
        self.addCleanup(patcher_kr.stop)

    def test_save_and_load_non_sensitive(self) -> None:
        app_config.save_settings({"provider": "imap", "imap_host": "imap.x.com", "imap_port": ""})
        loaded = app_config.load_settings()
        self.assertEqual(loaded["provider"], "imap")
        self.assertEqual(loaded["imap_host"], "imap.x.com")
        self.assertNotIn("imap_port", loaded)  # 空值不落盘

    def test_secret_roundtrip_and_status_masks(self) -> None:
        app_config.set_secret("mailosaur_api_key", "sk-secret")
        self.assertTrue(app_config.secret_configured("mailosaur_api_key"))
        status = app_config.settings_status()
        self.assertTrue(status["mailosaur_api_key_configured"])
        self.assertNotIn("sk-secret", str(status))  # 不回明文

    def test_set_secret_empty_clears(self) -> None:
        app_config.set_secret("imap_password", "pw")
        app_config.set_secret("imap_password", "")
        self.assertFalse(app_config.secret_configured("imap_password"))

    def test_effective_env_priority(self) -> None:
        # 全局设置 provider=auto;overrides 应覆盖为 imap
        app_config.save_settings({"provider": "auto", "imap_host": "global-host"})
        app_config.set_secret("imap_password", "global-pw")
        env = app_config.effective_email_env(
            {"provider": "imap", "imap_host": "override-host"},
            base_env={"ANALYZER_EMAIL_PROVIDER": "mailosaur"},  # 应被全局/override 盖掉
        )
        self.assertEqual(env["ANALYZER_EMAIL_PROVIDER"], "imap")  # override 最高
        self.assertEqual(env["ANALYZER_IMAP_HOST"], "override-host")  # override > 全局
        self.assertEqual(env["ANALYZER_IMAP_PASSWORD"], "global-pw")  # 全局 secret 注入

    def test_env_delta_only_email_keys(self) -> None:
        app_config.save_settings({"provider": "imap", "imap_host": "h"})
        delta = app_config.email_env_delta({"email_address": "a@b.com"})
        self.assertEqual(delta["ANALYZER_EMAIL_PROVIDER"], "imap")
        self.assertEqual(delta["ANALYZER_IMAP_HOST"], "h")
        self.assertEqual(delta["ANALYZER_EMAIL_ADDRESS"], "a@b.com")
        self.assertIn(app_config.OVERRIDES_ENV, delta)
        # 不含无关的 os.environ 键
        self.assertNotIn("PATH", delta)

    def test_overrides_blob_roundtrip_in_child(self) -> None:
        # 模拟子进程:overrides 经 ANALYZER_EMAIL_OVERRIDES 还原,仍高于全局
        app_config.save_settings({"provider": "auto"})
        blob = app_config.overrides_env_blob({"provider": "mailosaur"})
        env = app_config.effective_email_env(
            None, base_env={app_config.OVERRIDES_ENV: blob}
        )
        self.assertEqual(env["ANALYZER_EMAIL_PROVIDER"], "mailosaur")


if __name__ == "__main__":
    unittest.main()
