"""Stream-JSON → 终端美化输出。

输入是 ``claude --output-format stream-json --verbose`` 的一行 JSON 文本,
输出是若干行渲染好的字符串,由调用方(``claude_driver``)写到终端。

这层不直接 print,把"什么时候打、打到哪里"留给上层 — 这样 Spinner
能控制擦除/重画的时机,renderer 不耦合输出设备。
"""

from __future__ import annotations

import json

from . import config


def _trunc(s: str, n: int = 120) -> str:
    s = (s or "").replace("\n", " ⏎ ")
    if len(s) > n:
        return s[:n] + f"{config.DIM}…{config.RESET}"
    return s


def _summarize_tool_input(tool: str, inp) -> str:
    if not isinstance(inp, dict):
        return ""
    if tool == "Bash":
        return _trunc((inp.get("command") or "").strip(), 110)
    if tool in ("Read", "Write", "Edit", "NotebookEdit"):
        return inp.get("file_path") or inp.get("notebook_path") or ""
    if tool == "Glob":
        return inp.get("pattern", "")
    if tool == "Grep":
        pat = inp.get("pattern", "")
        path = inp.get("path", "")
        return f"{pat!r}{(' in ' + path) if path else ''}"
    if tool == "WebFetch":
        return inp.get("url", "")
    if tool == "WebSearch":
        return inp.get("query", "")
    if tool == "TaskCreate":
        return _trunc(inp.get("subject", ""), 80)
    if tool == "TaskUpdate":
        return f"#{inp.get('taskId', '?')} → {inp.get('status', '?')}"
    if tool == "TaskGet":
        return f"#{inp.get('taskId', '?')}"
    if tool == "TodoWrite":
        todos = inp.get("todos") or []
        if isinstance(todos, list):
            return f"{len(todos)} item(s)"
        return ""
    if tool == "Skill":
        return inp.get("skill", "")
    if tool == "Agent":
        return _trunc(inp.get("description", "") or inp.get("subagent_type", ""), 80)
    keys = list(inp.keys())[:2]
    parts = []
    for k in keys:
        v = inp[k]
        if isinstance(v, str):
            v = _trunc(v, 60)
        elif isinstance(v, (list, dict)):
            v = f"<{type(v).__name__}>"
        parts.append(f"{k}={v}")
    return " ".join(parts)


def _render_todos(todos: list) -> list[str]:
    """Render a TodoWrite list as ☐/◐/☑ lines."""
    out = []
    glyphs = {
        "pending": ("☐", config.GRAY),
        "in_progress": ("◐", config.YELLOW),
        "completed": ("☑", config.GREEN),
    }
    for td in todos:
        if not isinstance(td, dict):
            continue
        status = td.get("status", "pending")
        glyph, color = glyphs.get(status, ("·", config.GRAY))
        text = td.get("activeForm") if status == "in_progress" else None
        text = text or td.get("content") or td.get("subject") or td.get("description") or ""
        if status == "completed":
            line = f"  {color}{glyph} {config.DIM}{_trunc(text, 90)}{config.RESET}"
        else:
            line = f"  {color}{glyph} {_trunc(text, 90)}{config.RESET}"
        out.append(line)
    return out


def _flatten_tool_result(content) -> tuple[str, bool]:
    """Return ``(text, is_error_hint)``. ``content`` is str or a list of
    ``{type:text,text:...}`` blocks."""
    if isinstance(content, str):
        return content, False
    if isinstance(content, list):
        chunks = []
        for c in content:
            if isinstance(c, dict) and c.get("type") == "text":
                chunks.append(c.get("text", ""))
        return "\n".join(chunks), False
    return str(content or ""), False


def format_event(raw: str, state: dict | None = None) -> list[str] | None:
    """Parse one stream-json line; return a list of pretty lines (or None if
    the line wasn't JSON — caller should pass it through verbatim).

    ``state``, when provided, is a mutable dict the caller passes in so we
    can surface the session id back (used by the ESC resume loop) and track
    the last meaningful action for the loading spinner.
    """
    try:
        ev = json.loads(raw)
    except json.JSONDecodeError:
        return None
    if not isinstance(ev, dict):
        return []
    t = ev.get("type")
    out: list[str] = []

    if t == "system":
        if ev.get("subtype") == "init":
            model = ev.get("model", "?")
            cwd = ev.get("cwd", "")
            sid = ev.get("session_id")
            if state is not None:
                if sid:
                    state["session_id"] = sid
                state["last_action"] = "thinking"
            out.append(
                f"{config.DIM}── claude session · model={model} · cwd={cwd}{config.RESET}"
            )
        return out

    if t == "assistant":
        msg = ev.get("message") or {}
        content = msg.get("content")
        if not isinstance(content, list):
            return out
        for block in content:
            if not isinstance(block, dict):
                continue
            btype = block.get("type")
            if btype == "thinking":
                txt = (block.get("thinking") or "").strip()
                if txt:
                    if state is not None:
                        state["last_action"] = "thinking"
                    out.append(f"{config.DIM}{config.ITAL}✻ Thinking{config.RESET}")
                    for line in txt.split("\n"):
                        out.append(f"{config.DIM}  {line}{config.RESET}")
            elif btype == "text":
                txt = (block.get("text") or "").rstrip()
                if txt:
                    if state is not None:
                        state["last_action"] = "writing"
                    out.append(txt)
            elif btype == "tool_use":
                name = block.get("name", "?")
                summary = _summarize_tool_input(name, block.get("input"))
                tail = f" {config.DIM}{summary}{config.RESET}" if summary else ""
                out.append(f"{config.CYAN}● {name}{config.RESET}{tail}")
                if state is not None:
                    state["last_action"] = f"running {name}"
                inp = block.get("input")
                if name == "TodoWrite" and isinstance(inp, dict):
                    todos = inp.get("todos") or []
                    if isinstance(todos, list) and todos:
                        out.extend(_render_todos(todos))
        return out

    if t == "user":
        msg = ev.get("message") or {}
        content = msg.get("content")
        if not isinstance(content, list):
            return out
        for block in content:
            if not isinstance(block, dict):
                continue
            if block.get("type") == "tool_result":
                txt, _ = _flatten_tool_result(block.get("content"))
                txt = (txt or "").strip()
                is_err = bool(block.get("is_error"))
                color = config.RED if is_err else config.GRAY
                first = txt.split("\n", 1)[0] if txt else "(empty)"
                tag = "↳ error" if is_err else "↳"
                out.append(f"  {color}{tag} {_trunc(first, 110)}{config.RESET}")
                if state is not None:
                    state["last_action"] = "thinking"
        return out

    if t == "result":
        sub = ev.get("subtype", "")
        cost = ev.get("total_cost_usd")
        dur = ev.get("duration_ms")
        bits = [f"── result: {sub}"]
        if cost is not None:
            bits.append(f"${cost:.4f}")
        if dur is not None:
            bits.append(f"{dur / 1000:.1f}s")
        color = config.GREEN if sub == "success" else config.YELLOW
        out.append(f"{color}{' · '.join(bits)}{config.RESET}")
        if state is not None:
            state["last_action"] = None
        return out

    return out
