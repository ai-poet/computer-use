"""全局应用配置:邮箱 provider 等设置的持久化读写 + env 合并。

存储分两处:
- 非敏感字段(provider / host / port / username / folder / alias_mode / …)
  写 ``~/.config/computer-use-analyzer/settings.json``。
- 敏感字段(Mailosaur API key、IMAP 密码)进系统钥匙串(keyring),
  绝不落盘明文。

``effective_email_env`` 把三层合并成一份 env dict,优先级自高到低:

    任务级 overrides  >  全局设置(JSON + keyring)  >  os.environ 兜底

合并结果直接喂给 ``email_otp.resolve_config(env)``,所以这里的 key 一律
用 ``resolve_config`` 认识的环境变量名,避免再维护一层映射。
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

SERVICE_NAME = "computer-use-product-analyzer"
_SECRET_PREFIX = "setting:"
OVERRIDES_ENV = "ANALYZER_EMAIL_OVERRIDES"

# friendly field name -> 环境变量名(resolve_config 读取的名字)
FIELD_TO_ENV: dict[str, str] = {
    "provider": "ANALYZER_EMAIL_PROVIDER",
    "mailosaur_server_id": "MAILOSAUR_SERVER_ID",
    "mailosaur_server_domain": "MAILOSAUR_SERVER_DOMAIN",
    "imap_host": "ANALYZER_IMAP_HOST",
    "imap_port": "ANALYZER_IMAP_PORT",
    "imap_username": "ANALYZER_IMAP_USERNAME",
    "imap_ssl": "ANALYZER_IMAP_SSL",
    "imap_folder": "ANALYZER_IMAP_FOLDER",
    "email_address": "ANALYZER_EMAIL_ADDRESS",
    "alias_mode": "ANALYZER_EMAIL_ALIAS_MODE",
}

# 敏感字段单独走 keyring
SECRET_FIELD_TO_ENV: dict[str, str] = {
    "mailosaur_api_key": "MAILOSAUR_API_KEY",
    "imap_password": "ANALYZER_IMAP_PASSWORD",
}

ALL_FIELDS = tuple(FIELD_TO_ENV) + tuple(SECRET_FIELD_TO_ENV)


def config_dir() -> Path:
    base = os.environ.get("ANALYZER_CONFIG_DIR")
    if base:
        return Path(base)
    xdg = os.environ.get("XDG_CONFIG_HOME")
    root = Path(xdg) if xdg else Path.home() / ".config"
    return root / "computer-use-analyzer"


def settings_path() -> Path:
    return config_dir() / "settings.json"


# ---------- non-sensitive settings (JSON) ----------


def load_settings() -> dict[str, str]:
    path = settings_path()
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    if not isinstance(data, dict):
        return {}
    return {str(k): str(v) for k, v in data.items() if k in FIELD_TO_ENV and v not in (None, "")}


def save_settings(values: dict[str, Any]) -> dict[str, str]:
    """合并写入非敏感字段。值为 None/"" 表示删除该字段;未提供的 key 保留。"""
    current = load_settings()
    for key, raw in values.items():
        if key not in FIELD_TO_ENV:
            continue
        if raw is None or str(raw).strip() == "":
            current.pop(key, None)
        else:
            current[key] = str(raw).strip()
    path = settings_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(current, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return current


# ---------- sensitive settings (keyring) ----------


def _keyring():
    try:
        import keyring
    except ImportError as exc:  # pragma: no cover - dependency guard
        raise RuntimeError("keyring is not installed") from exc
    return keyring


def get_secret(field: str) -> str | None:
    if field not in SECRET_FIELD_TO_ENV:
        return None
    try:
        value = _keyring().get_password(SERVICE_NAME, _SECRET_PREFIX + field)
    except RuntimeError:
        return None
    return value or None


def set_secret(field: str, value: str | None) -> None:
    if field not in SECRET_FIELD_TO_ENV:
        raise KeyError(f"unknown secret field: {field}")
    keyring = _keyring()
    if value is None or value.strip() == "":
        try:
            keyring.delete_password(SERVICE_NAME, _SECRET_PREFIX + field)
        except keyring.errors.PasswordDeleteError:
            return
        return
    keyring.set_password(SERVICE_NAME, _SECRET_PREFIX + field, value.strip())


def secret_configured(field: str) -> bool:
    return bool(get_secret(field))


# ---------- merge ----------


def settings_status() -> dict[str, Any]:
    """供前端展示:非敏感字段回明文,敏感字段只回 configured 布尔。"""
    settings = load_settings()
    payload: dict[str, Any] = {key: settings.get(key, "") for key in FIELD_TO_ENV}
    payload["provider"] = settings.get("provider", "auto") or "auto"
    for field in SECRET_FIELD_TO_ENV:
        payload[f"{field}_configured"] = secret_configured(field)
    return payload


def normalize_overrides(overrides: dict[str, Any] | None) -> dict[str, str]:
    """把前端/任务级 friendly key 的 overrides 翻成 env-name keyed dict。"""
    result: dict[str, str] = {}
    if not overrides:
        return result
    mapping = {**FIELD_TO_ENV, **SECRET_FIELD_TO_ENV}
    for key, raw in overrides.items():
        env_name = mapping.get(key)
        if not env_name:
            continue
        if raw is None or str(raw).strip() == "":
            continue
        result[env_name] = str(raw).strip()
    return result


def effective_email_env(
    overrides: dict[str, Any] | None = None,
    *,
    base_env: dict[str, str] | None = None,
) -> dict[str, str]:
    """合并三层 env,优先级:overrides > 全局设置 > base_env(默认 os.environ)。

    overrides 为 None 时,回退到从 base_env 的 ``ANALYZER_EMAIL_OVERRIDES``
    (JSON, friendly-key)读取 —— 这样父进程把任务级覆盖塞进该 env 变量后,
    子进程能在不破坏优先级的前提下还原出正确的合并结果。
    """
    env: dict[str, str] = dict(base_env if base_env is not None else os.environ)

    if overrides is None:
        raw = env.get(OVERRIDES_ENV)
        if raw:
            try:
                parsed = json.loads(raw)
                if isinstance(parsed, dict):
                    overrides = parsed
            except json.JSONDecodeError:
                overrides = None

    settings = load_settings()
    for field, value in settings.items():
        env[FIELD_TO_ENV[field]] = value
    for field in SECRET_FIELD_TO_ENV:
        secret = get_secret(field)
        if secret:
            env[SECRET_FIELD_TO_ENV[field]] = secret

    for env_name, value in normalize_overrides(overrides).items():
        env[env_name] = value
    return env


def overrides_env_blob(overrides: dict[str, Any] | None) -> str | None:
    """把任务级 overrides(friendly key)序列化成 JSON,供父进程注入子进程 env。"""
    clean = {k: v for k, v in (overrides or {}).items() if k in ALL_FIELDS and str(v).strip()}
    return json.dumps(clean, ensure_ascii=False) if clean else None


def email_env_delta(overrides: dict[str, Any] | None = None) -> dict[str, str]:
    """只返回与邮箱配置相关的 env 键(全局设置 + keyring + overrides 合并后),
    供父进程 ``env.update(...)`` 注入子进程,而不必整份复制 os.environ。"""
    delta: dict[str, str] = {}
    settings = load_settings()
    for field, value in settings.items():
        delta[FIELD_TO_ENV[field]] = value
    for field in SECRET_FIELD_TO_ENV:
        secret = get_secret(field)
        if secret:
            delta[SECRET_FIELD_TO_ENV[field]] = secret
    for env_name, value in normalize_overrides(overrides).items():
        delta[env_name] = value
    blob = overrides_env_blob(overrides)
    if blob:
        delta[OVERRIDES_ENV] = blob
    return delta
