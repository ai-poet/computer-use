"""Local encrypted credential storage.

The web console stores credentials in the OS keychain via ``keyring``. Secrets
are never mirrored into workflow artifacts; callers receive only opaque ids.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from typing import Any

SERVICE_NAME = "computer-use-product-analyzer"


@dataclass(frozen=True)
class CredentialRef:
    credential_id: str
    label: str


def store_credential(label: str, fields: dict[str, str]) -> CredentialRef:
    try:
        import keyring
    except ImportError as exc:  # pragma: no cover - dependency/runtime guard
        raise RuntimeError("keyring is not installed") from exc
    cred_id = str(uuid.uuid4())
    payload = json.dumps({"label": label, "fields": fields}, ensure_ascii=False)
    keyring.set_password(SERVICE_NAME, cred_id, payload)
    return CredentialRef(credential_id=cred_id, label=label)


def load_credential(credential_id: str) -> dict[str, Any] | None:
    try:
        import keyring
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("keyring is not installed") from exc
    raw = keyring.get_password(SERVICE_NAME, credential_id)
    if not raw:
        return None
    return json.loads(raw)


def delete_credential(credential_id: str) -> None:
    try:
        import keyring
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("keyring is not installed") from exc
    try:
        keyring.delete_password(SERVICE_NAME, credential_id)
    except keyring.errors.PasswordDeleteError:
        return
