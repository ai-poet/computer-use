"""Email OTP helper for product-analyzer runs.

This module is a tool layer for agents. It can provision a test email address
and wait for verification codes or links without storing secrets in workflow
artifacts.
"""

from __future__ import annotations

import argparse
import email
import email.policy
import imaplib
import json
import re
import socket
import ssl
import sys
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from email.message import Message
from html import unescape
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from settings import app_config
from settings import credentials as cred_store
from core.tasks import read_metadata, slugify, update_metadata
from .workflow import load_workflow, write_workflow


PROVIDER_AUTO = "auto"
PROVIDER_MAILOSAUR = "mailosaur"
PROVIDER_IMAP = "imap"
PROVIDERS = {PROVIDER_AUTO, PROVIDER_MAILOSAUR, PROVIDER_IMAP}
DEFAULT_TIMEOUT_S = 90
MAX_TIMEOUT_S = 180
CODE_RE = re.compile(r"(?<!\d)(\d{4,8})(?!\d)")
HTTPS_URL_RE = re.compile(r"https://[^\s\"'<>）)]+", re.IGNORECASE)
KEYWORD_RE = re.compile(
    r"(?i)(code|otp|verification|verify|security|confirm|验证码|校验码|验证|确认)"
)


@dataclass(frozen=True)
class EmailConfig:
    provider: str
    selected_provider: str | None
    enabled: bool
    reason: str | None = None
    mailosaur_api_key: str | None = None
    mailosaur_server_id: str | None = None
    mailosaur_server_domain: str | None = None
    imap_host: str | None = None
    imap_port: int = 993
    imap_username: str | None = None
    imap_password: str | None = None
    imap_ssl: bool = True
    imap_folder: str = "INBOX"
    email_address: str | None = None
    alias_mode: str = "plus"


def resolve_config(env: dict[str, str] | None = None) -> EmailConfig:
    if env is None:
        env = app_config.effective_email_env()
    requested = (env.get("ANALYZER_EMAIL_PROVIDER") or PROVIDER_AUTO).strip().lower()
    if requested not in PROVIDERS:
        return EmailConfig(
            provider=requested,
            selected_provider=None,
            enabled=False,
            reason="invalid_provider",
        )

    mailosaur = _mailosaur_config(env, requested)
    imap = _imap_config(env, requested)

    if requested == PROVIDER_MAILOSAUR:
        return mailosaur
    if requested == PROVIDER_IMAP:
        return imap
    if mailosaur.enabled:
        return mailosaur
    if imap.enabled:
        return imap
    return EmailConfig(
        provider=PROVIDER_AUTO,
        selected_provider=None,
        enabled=False,
        reason="not_configured",
    )


def _mailosaur_config(env: dict[str, str], requested: str) -> EmailConfig:
    api_key = env.get("MAILOSAUR_API_KEY", "").strip()
    server_id = env.get("MAILOSAUR_SERVER_ID", "").strip()
    domain = env.get("MAILOSAUR_SERVER_DOMAIN", "").strip()
    if not domain and server_id:
        domain = f"{server_id}.mailosaur.net"
    ok = bool(api_key and server_id and domain)
    return EmailConfig(
        provider=requested,
        selected_provider=PROVIDER_MAILOSAUR if ok else None,
        enabled=ok,
        reason=None if ok else "mailosaur_not_configured",
        mailosaur_api_key=api_key or None,
        mailosaur_server_id=server_id or None,
        mailosaur_server_domain=domain or None,
    )


def _imap_config(env: dict[str, str], requested: str) -> EmailConfig:
    host = env.get("ANALYZER_IMAP_HOST", "").strip()
    username = env.get("ANALYZER_IMAP_USERNAME", "").strip()
    password = env.get("ANALYZER_IMAP_PASSWORD", "").strip()
    address = env.get("ANALYZER_EMAIL_ADDRESS", "").strip()
    folder = env.get("ANALYZER_IMAP_FOLDER", "INBOX").strip() or "INBOX"
    raw_port = env.get("ANALYZER_IMAP_PORT", "993").strip() or "993"
    try:
        port = int(raw_port)
    except ValueError:
        port = 993
    ssl_enabled = env.get("ANALYZER_IMAP_SSL", "true").strip().lower() not in (
        "0",
        "false",
        "no",
        "off",
    )
    alias_mode = env.get("ANALYZER_EMAIL_ALIAS_MODE", "plus").strip().lower()
    if alias_mode not in {"plus", "fixed"}:
        alias_mode = "plus"
    ok = bool(host and username and password and address and "@" in address)
    return EmailConfig(
        provider=requested,
        selected_provider=PROVIDER_IMAP if ok else None,
        enabled=ok,
        reason=None if ok else "imap_not_configured",
        imap_host=host or None,
        imap_port=port,
        imap_username=username or None,
        imap_password=password or None,
        imap_ssl=ssl_enabled,
        imap_folder=folder,
        email_address=address or None,
        alias_mode=alias_mode,
    )


def registration_enabled_from_env(env: dict[str, str] | None = None) -> bool:
    return resolve_config(env).enabled


def status_payload(env: dict[str, str] | None = None) -> dict[str, Any]:
    cfg = resolve_config(env)
    return {
        "ok": cfg.enabled,
        "provider": cfg.provider,
        "selected_provider": cfg.selected_provider,
        "reason": cfg.reason,
        "mailosaur": {
            "configured": bool(
                cfg.mailosaur_api_key
                and cfg.mailosaur_server_id
                and cfg.mailosaur_server_domain
            ),
            "server_domain": cfg.mailosaur_server_domain,
        },
        "imap": {
            "configured": bool(
                cfg.imap_host
                and cfg.imap_username
                and cfg.imap_password
                and cfg.email_address
            ),
            "host": cfg.imap_host,
            "port": cfg.imap_port,
            "ssl": cfg.imap_ssl,
            "folder": cfg.imap_folder,
            "email_domain": _domain_of(cfg.email_address),
            "alias_mode": cfg.alias_mode,
        },
    }


def create_address(out_dir: Path, *, force_fixed: bool = False) -> dict[str, Any]:
    cfg = resolve_config()
    if not cfg.enabled or not cfg.selected_provider:
        payload = _result(False, error=cfg.reason or "not_configured")
        _merge_registration(out_dir, enabled=False, status="not_configured", failure_reason=payload["error"])
        return payload

    workflow = load_workflow(out_dir)
    existing = (workflow.get("registration") or {}).get("email_address")
    if isinstance(existing, str) and existing and not force_fixed:
        return _result(
            True,
            provider=(workflow.get("registration") or {}).get("provider") or cfg.selected_provider,
            email=existing,
            email_domain=_domain_of(existing),
            reused=True,
        )

    if cfg.selected_provider == PROVIDER_MAILOSAUR:
        assert cfg.mailosaur_server_domain is not None
        address = f"{_run_local_part(out_dir)}@{cfg.mailosaur_server_domain}"
    else:
        assert cfg.email_address is not None
        address = _imap_address(cfg.email_address, out_dir, cfg.alias_mode, force_fixed=force_fixed)

    provider = cfg.selected_provider
    _merge_registration(
        out_dir,
        enabled=True,
        provider=provider,
        status="available",
        email_address=address,
        email_domain=_domain_of(address),
        alias_mode=cfg.alias_mode if provider == PROVIDER_IMAP else None,
        failure_reason=None,
    )
    return _result(
        True,
        provider=provider,
        email=address,
        email_domain=_domain_of(address),
        alias_mode=cfg.alias_mode if provider == PROVIDER_IMAP else None,
        reused=False,
    )


def wait_code(out_dir: Path, email_address: str, timeout_s: int) -> dict[str, Any]:
    timeout_s = _bounded_timeout(timeout_s)
    cfg = resolve_config()
    if not cfg.enabled or not cfg.selected_provider:
        _merge_registration(out_dir, status="failed", failure_reason=cfg.reason or "not_configured")
        return _result(False, error=cfg.reason or "not_configured")

    started = _registration_started_at(out_dir)
    try:
        if cfg.selected_provider == PROVIDER_MAILOSAUR:
            message = _mailosaur_get_message(cfg, email_address, timeout_s, started)
            code = extract_code_from_mailosaur(message)
            source = "mailosaur"
        else:
            message = _imap_wait_message(cfg, email_address, timeout_s, started)
            code = extract_code_from_text(_message_text(message))
            source = "imap"
    except TimeoutError:
        _merge_registration(out_dir, status="failed", failure_reason="timeout")
        return _result(False, error="timeout")
    except Exception as exc:
        _merge_registration(out_dir, status="failed", failure_reason=type(exc).__name__)
        return _result(False, error=f"{type(exc).__name__}: {exc}")

    if not code:
        _merge_registration(out_dir, status="failed", failure_reason="code_not_found")
        return _result(False, error="code_not_found")
    _merge_registration(out_dir, status="attempted", provider=cfg.selected_provider)
    return _result(True, provider=cfg.selected_provider, source=source, code=code)


def wait_link(out_dir: Path, email_address: str, timeout_s: int) -> dict[str, Any]:
    timeout_s = _bounded_timeout(timeout_s)
    cfg = resolve_config()
    if not cfg.enabled or not cfg.selected_provider:
        _merge_registration(out_dir, status="failed", failure_reason=cfg.reason or "not_configured")
        return _result(False, error=cfg.reason or "not_configured")

    started = _registration_started_at(out_dir)
    try:
        if cfg.selected_provider == PROVIDER_MAILOSAUR:
            message = _mailosaur_get_message(cfg, email_address, timeout_s, started)
            link = extract_link_from_mailosaur(message)
            source = "mailosaur"
        else:
            message = _imap_wait_message(cfg, email_address, timeout_s, started)
            link = extract_link_from_text(_message_text(message))
            source = "imap"
    except TimeoutError:
        _merge_registration(out_dir, status="failed", failure_reason="timeout")
        return _result(False, error="timeout")
    except Exception as exc:
        _merge_registration(out_dir, status="failed", failure_reason=type(exc).__name__)
        return _result(False, error=f"{type(exc).__name__}: {exc}")

    if not link:
        _merge_registration(out_dir, status="failed", failure_reason="link_not_found")
        return _result(False, error="link_not_found")
    _merge_registration(out_dir, status="attempted", provider=cfg.selected_provider)
    return _result(True, provider=cfg.selected_provider, source=source, link=link)


def mark_completed(out_dir: Path, *, used_for: str | None = None) -> dict[str, Any]:
    fields: dict[str, Any] = {"status": "completed", "failure_reason": None}
    if used_for:
        fields["used_for"] = used_for
    _merge_registration(out_dir, **fields)
    return _result(True, status="completed")


def mark_failed(out_dir: Path, reason: str) -> dict[str, Any]:
    _merge_registration(out_dir, status="failed", failure_reason=reason)
    return _result(True, status="failed", failure_reason=reason)


def mark_skipped(out_dir: Path, reason: str) -> dict[str, Any]:
    _merge_registration(out_dir, status="skipped", failure_reason=reason)
    return _result(True, status="skipped", failure_reason=reason)


def _run_id_for(out_dir: Path) -> str:
    return out_dir.resolve().name


def cred_put(
    out_dir: Path,
    label: str,
    fields: dict[str, str],
) -> dict[str, Any]:
    """Agent-facing: persist a credential to the global store, tagged with the
    source run + product so later runs of the same product can reuse it."""
    meta = read_metadata(out_dir) or {}
    product = meta.get("product_name") or out_dir.name
    ref = cred_store.store_credential(
        label,
        fields,
        source_run=_run_id_for(out_dir),
        product=str(product),
    )
    return _result(
        True,
        credential_id=ref.credential_id,
        label=ref.label,
        product=str(product),
        field_names=sorted(fields.keys()),
    )


def cred_list(out_dir: Path | None = None, *, all_products: bool = False) -> dict[str, Any]:
    product = None
    if out_dir is not None and not all_products:
        meta = read_metadata(out_dir) or {}
        product = str(meta.get("product_name") or out_dir.name)
    entries = cred_store.list_credentials(product=product)
    return _result(True, product=product, credentials=entries)


def cred_get(out_dir: Path, *, label: str | None = None) -> dict[str, Any]:
    """Agent-facing: fetch a previously saved credential's secret fields by
    product (optionally filtered by label). Returns secrets to THIS tool call
    only — callers must not echo them into reports/artifacts."""
    meta = read_metadata(out_dir) or {}
    product = str(meta.get("product_name") or out_dir.name)
    payload = cred_store.find_credential(product=product, label=label)
    if payload is None:
        return _result(False, error="not_found", product=product)
    return _result(
        True,
        credential_id=payload.get("credential_id"),
        label=payload.get("label"),
        product=product,
        fields=payload.get("fields") or {},
    )


def extract_code_from_mailosaur(message: Any) -> str | None:
    for part_name in ("text", "html"):
        part = getattr(message, part_name, None)
        for code_obj in getattr(part, "codes", None) or []:
            value = getattr(code_obj, "value", None)
            if isinstance(value, str) and re.fullmatch(r"\d{4,8}", value.strip()):
                return value.strip()
    return extract_code_from_text(_mailosaur_message_text(message))


def extract_link_from_mailosaur(message: Any) -> str | None:
    html = getattr(message, "html", None)
    for link_obj in getattr(html, "links", None) or []:
        href = getattr(link_obj, "href", None)
        if _is_https_url(href):
            return str(href)
    return extract_link_from_text(_mailosaur_message_text(message))


def extract_code_from_text(text: str) -> str | None:
    clean = _normalize_text(text)
    candidates = [(m.group(1), m.start(1), m.end(1)) for m in CODE_RE.finditer(clean)]
    if not candidates:
        return None
    keyword_spans = [match.span() for match in KEYWORD_RE.finditer(clean)]
    best: tuple[int, int, str] | None = None
    for value, start, end in candidates:
        window = clean[max(0, start - 50) : min(len(clean), end + 50)]
        score = 0
        if KEYWORD_RE.search(window):
            score += 10
        if keyword_spans:
            distance = min(
                min(abs(start - k_end), abs(end - k_start))
                for k_start, k_end in keyword_spans
            )
            score += max(0, 80 - distance)
        score += min(len(value), 8)
        current = (score, -start, value)
        if best is None or current > best:
            best = current
    return best[2] if best else candidates[0][0]


def extract_link_from_text(text: str) -> str | None:
    clean = unescape(text)
    links = [match.group(0).rstrip(".,;:!?]") for match in HTTPS_URL_RE.finditer(clean)]
    if not links:
        return None
    scored: list[tuple[int, str]] = []
    for link in links:
        score = 0
        parsed = urlparse(link)
        lowered = link.lower()
        if parsed.scheme == "https":
            score += 10
        if any(word in lowered for word in ("verify", "verification", "confirm", "activate", "auth")):
            score += 8
        scored.append((score, link))
    scored.sort(reverse=True)
    return scored[0][1]


def _mailosaur_get_message(
    cfg: EmailConfig,
    email_address: str,
    timeout_s: int,
    received_after: datetime,
) -> Any:
    try:
        from mailosaur import MailosaurClient
        from mailosaur.models import SearchCriteria
    except ImportError as exc:
        raise RuntimeError("mailosaur package is not installed") from exc

    criteria = SearchCriteria()
    criteria.sent_to = email_address
    client = MailosaurClient(cfg.mailosaur_api_key)
    assert cfg.mailosaur_server_id is not None
    return client.messages.get(
        cfg.mailosaur_server_id,
        criteria,
        timeout=timeout_s * 1000,
        received_after=received_after.replace(tzinfo=None),
    )


def _imap_wait_message(
    cfg: EmailConfig,
    email_address: str,
    timeout_s: int,
    received_after: datetime,
) -> Message:
    deadline = time.monotonic() + timeout_s
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        try:
            message = _imap_find_latest(cfg, email_address, received_after)
            if message is not None:
                return message
        except Exception as exc:  # transient IMAP/network errors should retry
            last_error = exc
        time.sleep(5)
    if last_error is not None:
        raise TimeoutError(str(last_error)) from last_error
    raise TimeoutError("no matching email")


def _imap_find_latest(
    cfg: EmailConfig,
    email_address: str,
    received_after: datetime,
) -> Message | None:
    assert cfg.imap_host is not None
    assert cfg.imap_username is not None
    assert cfg.imap_password is not None
    mailbox: imaplib.IMAP4
    if cfg.imap_ssl:
        mailbox = imaplib.IMAP4_SSL(cfg.imap_host, cfg.imap_port, timeout=30)
    else:
        mailbox = imaplib.IMAP4(cfg.imap_host, cfg.imap_port, timeout=30)
    try:
        mailbox.login(cfg.imap_username, cfg.imap_password)
        mailbox.select(cfg.imap_folder, readonly=True)
        since = received_after.strftime("%d-%b-%Y")
        typ, data = mailbox.search(None, "SINCE", since)
        if typ != "OK" or not data:
            return None
        ids = data[0].split()
        for msg_id in reversed(ids[-50:]):
            typ, raw_data = mailbox.fetch(msg_id, "(BODY.PEEK[])")
            if typ != "OK" or not raw_data:
                continue
            raw = next((part[1] for part in raw_data if isinstance(part, tuple)), None)
            if not raw:
                continue
            msg = email.message_from_bytes(raw, policy=email.policy.default)
            if not _message_matches(msg, email_address, received_after):
                continue
            return msg
        return None
    finally:
        try:
            mailbox.logout()
        except (imaplib.IMAP4.error, OSError, socket.error, ssl.SSLError):
            pass


def _message_matches(msg: Message, email_address: str, received_after: datetime) -> bool:
    try:
        msg_date = email.utils.parsedate_to_datetime(msg.get("Date", ""))
    except (TypeError, ValueError):
        msg_date = None
    if msg_date is not None:
        if msg_date.tzinfo is None:
            msg_date = msg_date.replace(tzinfo=timezone.utc)
        if msg_date < received_after:
            return False
    target = email_address.lower()
    recipients = " ".join(
        str(msg.get(name, ""))
        for name in ("To", "Delivered-To", "X-Original-To", "Envelope-To")
    ).lower()
    if target in recipients:
        return True
    local, _, domain = target.partition("@")
    if "+" in local:
        fixed = f"{local.split('+', 1)[0]}@{domain}"
        return fixed in recipients
    return False


def _message_text(msg: Message) -> str:
    chunks: list[str] = [str(msg.get("Subject", ""))]
    if msg.is_multipart():
        for part in msg.walk():
            ctype = part.get_content_type()
            if ctype not in ("text/plain", "text/html"):
                continue
            try:
                chunks.append(str(part.get_content()))
            except (LookupError, UnicodeDecodeError):
                payload = part.get_payload(decode=True)
                if payload:
                    chunks.append(payload.decode("utf-8", errors="replace"))
    else:
        try:
            chunks.append(str(msg.get_content()))
        except (LookupError, UnicodeDecodeError):
            payload = msg.get_payload(decode=True)
            if payload:
                chunks.append(payload.decode("utf-8", errors="replace"))
    return "\n".join(chunks)


def _mailosaur_message_text(message: Any) -> str:
    chunks = [str(getattr(message, "subject", "") or "")]
    for part_name in ("text", "html"):
        part = getattr(message, part_name, None)
        body = getattr(part, "body", None)
        if isinstance(body, str):
            chunks.append(body)
    return "\n".join(chunks)


def _merge_registration(out_dir: Path, **fields: Any) -> None:
    workflow = load_workflow(out_dir)
    registration = dict(workflow.get("registration") or {})
    for key, value in fields.items():
        if value is not None:
            registration[key] = value
        elif key in registration:
            registration.pop(key, None)
    registration.setdefault("enabled", False)
    registration.setdefault("provider", None)
    registration.setdefault("email_address", None)
    registration.setdefault("status", "not_configured")
    workflow["registration"] = registration
    write_workflow(out_dir, workflow)

    meta = read_metadata(out_dir) or {}
    meta_reg = dict(meta.get("registration") or {})
    for key in (
        "enabled",
        "provider",
        "status",
        "email_domain",
        "alias_mode",
        "failure_reason",
        "used_for",
    ):
        if key in fields:
            value = fields[key]
            if value is None:
                meta_reg.pop(key, None)
            else:
                meta_reg[key] = value
    update_metadata(out_dir, registration=meta_reg)


def _registration_started_at(out_dir: Path) -> datetime:
    workflow = load_workflow(out_dir)
    registration = workflow.get("registration") or {}
    raw = registration.get("started_at") or workflow.get("started_at")
    if isinstance(raw, str):
        try:
            parsed = datetime.fromisoformat(raw)
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            return parsed - timedelta(minutes=1)
        except ValueError:
            pass
    return datetime.now(timezone.utc) - timedelta(minutes=10)


def _run_local_part(out_dir: Path) -> str:
    meta = read_metadata(out_dir) or {}
    base = slugify(str(meta.get("product_name") or out_dir.name))[:28] or "product"
    suffix = uuid.uuid5(uuid.NAMESPACE_URL, str(out_dir.resolve())).hex[:8]
    return f"pa-{base}-{suffix}"


def _imap_address(base_address: str, out_dir: Path, alias_mode: str, *, force_fixed: bool) -> str:
    if force_fixed or alias_mode == "fixed":
        return base_address
    local, at, domain = base_address.partition("@")
    if not at:
        return base_address
    suffix = uuid.uuid5(uuid.NAMESPACE_URL, str(out_dir.resolve())).hex[:8]
    return f"{local}+pa-{suffix}@{domain}"


def _domain_of(address: str | None) -> str | None:
    if not address or "@" not in address:
        return None
    return address.rsplit("@", 1)[1].lower()


def _bounded_timeout(timeout_s: int) -> int:
    return max(1, min(int(timeout_s), MAX_TIMEOUT_S))


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", unescape(text))


def _is_https_url(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    parsed = urlparse(value)
    return parsed.scheme == "https" and bool(parsed.netloc)


def _result(ok: bool, **fields: Any) -> dict[str, Any]:
    payload = {"ok": ok}
    payload.update(fields)
    return payload


def _emit(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False))


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Email OTP helper for product-analyzer")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("status", help="Print provider configuration status")

    create = sub.add_parser("create-address", help="Create or reuse a test email address")
    create.add_argument("--out-dir", type=Path, required=True)
    create.add_argument(
        "--force-fixed",
        action="store_true",
        help="For IMAP, ignore plus alias and use ANALYZER_EMAIL_ADDRESS directly",
    )

    for name in ("wait-code", "wait-link"):
        wait = sub.add_parser(name, help=f"Wait for an email {name.split('-')[1]}")
        wait.add_argument("--out-dir", type=Path, required=True)
        wait.add_argument("--email", required=True)
        wait.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT_S)

    complete = sub.add_parser("mark-completed", help="Mark registration completed")
    complete.add_argument("--out-dir", type=Path, required=True)
    complete.add_argument("--used-for", choices=("web", "desktop", "android"), default=None)

    for name in ("mark-failed", "mark-skipped"):
        mark = sub.add_parser(name, help=f"Mark registration {name.split('-')[1]}")
        mark.add_argument("--out-dir", type=Path, required=True)
        mark.add_argument("--reason", required=True)

    put = sub.add_parser("cred-put", help="Persist a credential to the global store")
    put.add_argument("--out-dir", type=Path, required=True)
    put.add_argument("--label", required=True, help="Human label, e.g. 'login account'")
    put.add_argument(
        "--field",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="Credential field (repeatable), e.g. --field username=foo --field password=bar",
    )

    listing = sub.add_parser("cred-list", help="List saved credentials (metadata only)")
    listing.add_argument("--out-dir", type=Path, default=None)
    listing.add_argument("--all", action="store_true", help="List across all products")

    getter = sub.add_parser("cred-get", help="Fetch saved credential fields for this product")
    getter.add_argument("--out-dir", type=Path, required=True)
    getter.add_argument("--label", default=None, help="Optional label filter")

    return parser


def _parse_fields(pairs: list[str]) -> dict[str, str]:
    fields: dict[str, str] = {}
    for pair in pairs:
        key, sep, value = pair.partition("=")
        if not sep or not key.strip():
            raise ValueError(f"invalid --field (expected KEY=VALUE): {pair!r}")
        fields[key.strip()] = value
    return fields


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        if args.command == "status":
            _emit(status_payload())
            return 0
        if args.command == "create-address":
            _emit(create_address(args.out_dir, force_fixed=args.force_fixed))
            return 0
        if args.command == "wait-code":
            payload = wait_code(args.out_dir, args.email, args.timeout)
            _emit(payload)
            return 0 if payload.get("ok") else 1
        if args.command == "wait-link":
            payload = wait_link(args.out_dir, args.email, args.timeout)
            _emit(payload)
            return 0 if payload.get("ok") else 1
        if args.command == "mark-completed":
            _emit(mark_completed(args.out_dir, used_for=args.used_for))
            return 0
        if args.command == "mark-failed":
            _emit(mark_failed(args.out_dir, args.reason))
            return 0
        if args.command == "mark-skipped":
            _emit(mark_skipped(args.out_dir, args.reason))
            return 0
        if args.command == "cred-put":
            payload = cred_put(args.out_dir, args.label, _parse_fields(args.field))
            _emit(payload)
            return 0 if payload.get("ok") else 1
        if args.command == "cred-list":
            _emit(cred_list(args.out_dir, all_products=args.all))
            return 0
        if args.command == "cred-get":
            payload = cred_get(args.out_dir, label=args.label)
            _emit(payload)
            return 0 if payload.get("ok") else 1
    except Exception as exc:
        _emit(_result(False, error=f"{type(exc).__name__}: {exc}"))
        return 1
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
