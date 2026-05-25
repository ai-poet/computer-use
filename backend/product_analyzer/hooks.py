"""Claude Code hook entrypoints for product-analyzer.

Hooks are guardrails, not the business workflow. They block a few dangerous
commands, record sanitized events, and prevent a run from claiming completion
when required workflow artifacts are absent.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import Any

try:
    from .workflow import append_event, discover_out_dir_from_env_or_payload, validate_run
except ImportError:  # pragma: no cover - direct script execution by hooks
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from product_analyzer.workflow import (  # type: ignore
        append_event,
        discover_out_dir_from_env_or_payload,
        validate_run,
    )


HOST_GUI_PATTERNS = [
    r"(^|\s)open(\s|$)",
    r"osascript\s+.*\b(activate|launch|open)\b",
    r"cliclick\b",
    r"CGEventPost",
]

SHELL_SITE_SCRAPE_PATTERNS = [
    r"\b(curl|wget)\b.+https?://",
    r"\bpython3?\b.+requests\.",
]

ALLOWED_SHELL_HINTS = [
    "backend/sandbox_ctl.py",
    "backend/android_ctl.py",
    "sandbox_ctl.py",
    "android_ctl.py",
    "wget -O",
    "dpkg -i",
    "chmod +x",
    "uname",
    "/proc",
]


def main(argv: list[str] | None = None) -> int:
    argv = argv or sys.argv[1:]
    if not argv:
        print("usage: hooks.py pre-tool|post-tool|stop", file=sys.stderr)
        return 2
    payload = _read_payload()
    action = argv[0]
    if action == "pre-tool":
        return pre_tool(payload)
    if action == "post-tool":
        return post_tool(payload)
    if action == "stop":
        return stop(payload)
    print(f"unknown hook action: {action}", file=sys.stderr)
    return 2


def _read_payload() -> dict[str, Any]:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    try:
        data = json.loads(raw)
        return data if isinstance(data, dict) else {"payload": data}
    except json.JSONDecodeError:
        return {"raw": raw}


def _tool_name(payload: dict[str, Any]) -> str:
    for key in ("tool_name", "name"):
        value = payload.get(key)
        if isinstance(value, str):
            return value
    return ""


def _tool_input(payload: dict[str, Any]) -> dict[str, Any]:
    value = payload.get("tool_input") or payload.get("input") or {}
    return value if isinstance(value, dict) else {}


def _command(payload: dict[str, Any]) -> str:
    inp = _tool_input(payload)
    value = inp.get("command") or inp.get("cmd") or ""
    return value if isinstance(value, str) else ""


def pre_tool(payload: dict[str, Any]) -> int:
    out_dir = discover_out_dir_from_env_or_payload(payload)
    tool = _tool_name(payload)
    command = _command(payload)
    if out_dir:
        append_event(
            out_dir,
            {
                "event": "pre_tool",
                "tool": tool,
                "command": command,
            },
        )

    if tool != "Bash" or not command:
        return 0

    if _matches_any(command, HOST_GUI_PATTERNS):
        return _block(
            "product-analyzer hook blocked host GUI activation. Use sandbox_ctl/Cua MCP inside the sandbox."
        )

    runtime = os.environ.get("ANALYZER_RUNTIME", "")
    if runtime.startswith("sandbox") and _looks_like_site_scrape(command):
        return _block(
            "product-analyzer hook blocked shell-based website scraping in sandbox workflow. Use Firefox via sandbox_ctl step screenshot/click/scroll/type, except for existing direct installer URLs."
        )

    return 0


def post_tool(payload: dict[str, Any]) -> int:
    out_dir = discover_out_dir_from_env_or_payload(payload)
    if out_dir:
        append_event(
            out_dir,
            {
                "event": "post_tool",
                "tool": _tool_name(payload),
                "command": _command(payload),
                "ok": not bool(payload.get("is_error")),
            },
        )
    return 0


def stop(payload: dict[str, Any]) -> int:
    out_dir = discover_out_dir_from_env_or_payload(payload)
    if not out_dir:
        return 0
    append_event(out_dir, {"event": "stop_check"})
    issues = validate_run(out_dir, final=True)
    if not issues:
        return 0
    print(
        "product-analyzer workflow incomplete:\n"
        + "\n".join(f"- {item}" for item in issues),
        file=sys.stderr,
    )
    # Claude hooks use non-zero exit to block/flag the event. Exit 2 is the
    # conventional "blocking error" code in Claude Code hook examples.
    return 2


def _looks_like_site_scrape(command: str) -> bool:
    if not _matches_any(command, SHELL_SITE_SCRAPE_PATTERNS):
        return False
    lowered = command.lower()
    if any(hint.lower() in lowered for hint in ALLOWED_SHELL_HINTS):
        return False
    if re.search(r"\b(wget|curl)\b.+\b-o\b.+downloads/", lowered):
        return False
    return True


def _matches_any(text: str, patterns: list[str]) -> bool:
    return any(re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL) for pattern in patterns)


def _block(message: str) -> int:
    print(message, file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
