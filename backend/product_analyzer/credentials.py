"""Local encrypted credential storage.

The web console stores credentials in the OS keychain via ``keyring``. Secrets
are never mirrored into workflow artifacts; callers receive only opaque ids.

A small JSON index (``index``) is kept alongside the secrets in the same
keyring service so the console and agents can enumerate saved credentials by
``label`` / ``source_run`` / ``product`` without ever exposing secret values.
"""

from __future__ import annotations

import json
import time
import uuid
from dataclasses import dataclass
from typing import Any

SERVICE_NAME = "computer-use-product-analyzer"
INDEX_KEY = "credential-index"


@dataclass(frozen=True)
class CredentialRef:
    credential_id: str
    label: str


def _keyring():
    try:
        import keyring
    except ImportError as exc:  # pragma: no cover - dependency/runtime guard
        raise RuntimeError("keyring is not installed") from exc
    return keyring


def _load_index() -> list[dict[str, Any]]:
    raw = _keyring().get_password(SERVICE_NAME, INDEX_KEY)
    if not raw:
        return []
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return []
    return data if isinstance(data, list) else []


def _save_index(entries: list[dict[str, Any]]) -> None:
    _keyring().set_password(SERVICE_NAME, INDEX_KEY, json.dumps(entries, ensure_ascii=False))


def store_credential(
    label: str,
    fields: dict[str, str],
    *,
    source_run: str | None = None,
    product: str | None = None,
) -> CredentialRef:
    keyring = _keyring()
    cred_id = str(uuid.uuid4())
    payload = json.dumps(
        {
            "label": label,
            "fields": fields,
            "source_run": source_run,
            "product": product,
            "created_at": time.time(),
        },
        ensure_ascii=False,
    )
    keyring.set_password(SERVICE_NAME, cred_id, payload)

    index = _load_index()
    index.append(
        {
            "credential_id": cred_id,
            "label": label,
            "source_run": source_run,
            "product": product,
            "field_names": sorted(fields.keys()),
            "created_at": time.time(),
        }
    )
    _save_index(index)
    return CredentialRef(credential_id=cred_id, label=label)


def load_credential(credential_id: str) -> dict[str, Any] | None:
    raw = _keyring().get_password(SERVICE_NAME, credential_id)
    if not raw:
        return None
    return json.loads(raw)


def list_credentials(*, product: str | None = None, source_run: str | None = None) -> list[dict[str, Any]]:
    """Return index metadata only (never secret field values)."""
    entries = _load_index()
    if product is not None:
        entries = [e for e in entries if e.get("product") == product]
    if source_run is not None:
        entries = [e for e in entries if e.get("source_run") == source_run]
    return sorted(entries, key=lambda e: e.get("created_at") or 0, reverse=True)


def find_credential(*, product: str | None = None, label: str | None = None) -> dict[str, Any] | None:
    """Look up the most recent matching credential and return its full payload."""
    for entry in list_credentials(product=product):
        if label is not None and entry.get("label") != label:
            continue
        payload = load_credential(entry["credential_id"])
        if payload is not None:
            payload["credential_id"] = entry["credential_id"]
            return payload
    return None


def delete_credential(credential_id: str) -> None:
    keyring = _keyring()
    try:
        keyring.delete_password(SERVICE_NAME, credential_id)
    except keyring.errors.PasswordDeleteError:
        pass
    index = [e for e in _load_index() if e.get("credential_id") != credential_id]
    _save_index(index)
