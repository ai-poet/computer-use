"""Stream-JSON → 终端美化输出。

输入是 ``claude --output-format stream-json --verbose`` 的一行 JSON 文本,
输出是若干行渲染好的字符串,由调用方(``claude_driver``)写到终端。

这层不直接 print,把"什么时候打、打到哪里"留给上层 — 这样 Spinner
能控制擦除/重画的时机,renderer 不耦合输出设备。
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import json
import re
from typing import Any

from . import config


@dataclass
class RenderedLine:
    kind: str
    text: str
    tone: str = "normal"
    indent: int = 0
    tool: str | None = None
    status: str | None = None
    raw: str | None = None
    meta: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        required = {"kind", "text", "tone", "indent"}
        return {
            key: value
            for key, value in data.items()
            if key in required or value not in (None, {})
        }


ANSI_RE = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")


def strip_ansi(text: str) -> str:
    return ANSI_RE.sub("", text)


def _trunc_plain(s: str, n: int = 120) -> str:
    s = (s or "").replace("\n", " ⏎ ")
    if len(s) > n:
        return s[:n] + "…"
    return s


def _color_text(text: str, color: str = "", *, dim: bool = False, italic: bool = False) -> str:
    prefix = ""
    if color:
        prefix += color
    if dim:
        prefix += config.DIM
    if italic:
        prefix += config.ITAL
    return f"{prefix}{text}{config.RESET}" if prefix else text


def _trunc(s: str, n: int = 120) -> str:
    plain = _trunc_plain(s, n)
    if plain.endswith("…"):
        return plain[:-1] + f"{config.DIM}…{config.RESET}"
    return plain


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
    for line in render_todo_lines(todos):
        glyph, color = glyphs.get(line.status or "pending", ("·", config.GRAY))
        text = _trunc(line.text, 90)
        if line.status == "completed":
            out.append(f"  {color}{glyph} {config.DIM}{text}{config.RESET}")
        else:
            out.append(f"  {color}{glyph} {text}{config.RESET}")
    return out


def render_todo_lines(todos: list) -> list[RenderedLine]:
    """Render TodoWrite items into Web-friendly semantic lines."""
    out: list[RenderedLine] = []
    for td in todos:
        if not isinstance(td, dict):
            continue
        status = td.get("status", "pending")
        text = td.get("activeForm") if status == "in_progress" else None
        text = text or td.get("content") or td.get("subject") or td.get("description") or ""
        tone = {
            "pending": "muted",
            "in_progress": "warning",
            "completed": "success",
        }.get(status, "muted")
        out.append(
            RenderedLine(
                kind="todo",
                text=_trunc_plain(text, 90),
                tone=tone,
                indent=1,
                status=str(status),
                meta={"priority": td.get("priority")},
            )
        )
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


def render_event(raw: str, state: dict | None = None) -> list[RenderedLine] | None:
    """Parse one stream-json line into semantic lines for Web UI consumers.

    ``None`` means the line was not JSON and should be passed through as a
    raw terminal line. ``state`` follows the same contract as ``format_event``.
    """
    try:
        ev = json.loads(raw)
    except json.JSONDecodeError:
        return None
    if not isinstance(ev, dict):
        return []

    t = ev.get("type")
    out: list[RenderedLine] = []

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
                RenderedLine(
                    kind="session",
                    text=f"── claude session · model={model} · cwd={cwd}",
                    tone="muted",
                    meta={"model": model, "cwd": cwd, "session_id": sid},
                )
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
                    out.append(RenderedLine(kind="thinking", text="✻ Thinking", tone="muted"))
                    for line in txt.split("\n"):
                        out.append(
                            RenderedLine(
                                kind="thinking",
                                text=line,
                                tone="muted",
                                indent=1,
                            )
                        )
            elif btype == "text":
                txt = (block.get("text") or "").rstrip()
                if txt:
                    if state is not None:
                        state["last_action"] = "writing"
                    for line in txt.split("\n"):
                        out.append(RenderedLine(kind="assistant_text", text=line))
            elif btype == "tool_use":
                name = block.get("name", "?")
                summary = _summarize_tool_input(name, block.get("input"))
                text = f"● {name}{(' ' + strip_ansi(summary)) if summary else ''}"
                out.append(
                    RenderedLine(
                        kind="tool_use",
                        text=text,
                        tone="accent",
                        tool=name,
                        meta={"summary": strip_ansi(summary), "id": block.get("id")},
                    )
                )
                if state is not None:
                    state["last_action"] = f"running {name}"
                inp = block.get("input")
                if name == "TodoWrite" and isinstance(inp, dict):
                    todos = inp.get("todos") or []
                    if isinstance(todos, list) and todos:
                        out.extend(render_todo_lines(todos))
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
                first = txt.split("\n", 1)[0] if txt else "(empty)"
                tag = "↳ error" if is_err else "↳"
                out.append(
                    RenderedLine(
                        kind="tool_result",
                        text=f"{tag} {_trunc_plain(first, 110)}",
                        tone="error" if is_err else "muted",
                        indent=1,
                        status="error" if is_err else "ok",
                        meta={"tool_use_id": block.get("tool_use_id")},
                    )
                )
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
        out.append(
            RenderedLine(
                kind="result",
                text=" · ".join(bits),
                tone="success" if sub == "success" else "warning",
                status=str(sub),
                meta={"cost": cost, "duration_ms": dur},
            )
        )
        if state is not None:
            state["last_action"] = None
        return out

    return out


def rendered_lines_to_text(lines: list[RenderedLine]) -> list[str]:
    out: list[str] = []
    for line in lines:
        pad = "  " * line.indent
        text = line.text
        if line.kind == "session":
            out.append(_color_text(text, dim=True))
        elif line.kind == "thinking":
            out.append(pad + _color_text(text, dim=True, italic=line.indent == 0))
        elif line.kind == "tool_use":
            if line.tool and text.startswith(f"● {line.tool}"):
                tail = text[len(f"● {line.tool}") :]
                out.append(f"{config.CYAN}● {line.tool}{config.RESET}{config.DIM}{tail}{config.RESET}")
            else:
                out.append(f"{config.CYAN}{text}{config.RESET}")
        elif line.kind == "tool_result":
            color = config.RED if line.tone == "error" else config.GRAY
            out.append(pad + _color_text(text, color))
        elif line.kind == "todo":
            glyphs = {
                "pending": ("☐", config.GRAY),
                "in_progress": ("◐", config.YELLOW),
                "completed": ("☑", config.GREEN),
            }
            glyph, color = glyphs.get(line.status or "pending", ("·", config.GRAY))
            todo_text = _trunc(line.text, 90)
            if line.status == "completed":
                out.append(f"{pad}{color}{glyph} {config.DIM}{todo_text}{config.RESET}")
            else:
                out.append(f"{pad}{color}{glyph} {todo_text}{config.RESET}")
        elif line.kind == "result":
            color = config.GREEN if line.tone == "success" else config.YELLOW
            out.append(_color_text(text, color))
        else:
            out.append(pad + text)
    return out


def format_event(raw: str, state: dict | None = None) -> list[str] | None:
    """Parse one stream-json line; return a list of pretty lines (or None if
    the line wasn't JSON — caller should pass it through verbatim).

    ``state``, when provided, is a mutable dict the caller passes in so we
    can surface the session id back (used by the ESC resume loop) and track
    the last meaningful action for the loading spinner.
    """
    lines = render_event(raw, state)
    if lines is None:
        return None
    return rendered_lines_to_text(lines)
