"""Render ANSI-colored lines (renderer output) on a curses window."""

from __future__ import annotations

import curses
import re
from typing import Iterator

from .batch_store import _strip_ansi

_ANSI_RE = re.compile(r"\x1b\[([0-9;]*)m")


def _attr_for_codes(codes: list[str], base: int) -> int:
    attr = base
    for code in codes:
        if code in ("", "0"):
            attr = base
        elif code == "1":
            attr |= curses.A_BOLD
        elif code == "2":
            attr |= curses.A_DIM
        elif code == "3":
            attr |= curses.A_DIM
        elif code == "90":
            attr |= curses.A_DIM
        elif code == "36":
            attr = (attr & ~curses.A_COLOR) | curses.color_pair(4)
        elif code == "32":
            attr = (attr & ~curses.A_COLOR) | curses.color_pair(1)
        elif code == "33":
            attr = (attr & ~curses.A_COLOR) | curses.color_pair(2)
        elif code == "31":
            attr = (attr & ~curses.A_COLOR) | curses.color_pair(3)
    return attr


def iter_ansi_segments(text: str, *, base_attr: int = 0) -> Iterator[tuple[str, int]]:
    """Yield (visible_text, curses_attr) preserving renderer color codes."""
    pos = 0
    attr = base_attr
    for match in _ANSI_RE.finditer(text):
        if match.start() > pos:
            yield text[pos : match.start()], attr
        parts = [p for p in match.group(1).split(";") if p != ""]
        if not parts:
            attr = base_attr
        else:
            attr = _attr_for_codes(parts, base_attr)
        pos = match.end()
    if pos < len(text):
        yield text[pos:], attr


def visible_width(text: str) -> int:
    return len(_strip_ansi(text))


def trunc_visible(text: str, width: int) -> str:
    """Truncate by visible columns, keeping leading ANSI codes."""
    if width < 1:
        return ""
    plain = _strip_ansi(text)
    if len(plain) <= width:
        return text
    if width <= 1:
        return plain[:width]
    # Rebuild: walk segments until width exhausted.
    out: list[str] = []
    used = 0
    prefix = ""
    m = _ANSI_RE.match(text)
    while m and m.start() == 0:
        prefix += m.group(0)
        text = text[m.end() :]
        m = _ANSI_RE.match(text)
    out.append(prefix)
    for chunk, _attr in iter_ansi_segments(text):
        if not chunk:
            continue
        room = width - used
        if room <= 0:
            break
        if len(chunk) <= room:
            out.append(chunk)
            used += len(chunk)
        else:
            out.append(chunk[:room])
            used = width
            break
    if used >= width and width > 1:
        out.append("…")
    return "".join(out)


def addstr_ansi(
    win: curses.window,
    y: int,
    x: int,
    text: str,
    width: int,
    *,
    default_attr: int = 0,
) -> None:
    """Draw one logical line with ANSI colors (Claude Code / renderer style)."""
    if width < 1:
        return
    text = trunc_visible(text, width)
    col = x
    for chunk, attr in iter_ansi_segments(text, base_attr=default_attr):
        if not chunk or col >= x + width:
            break
        room = (x + width) - col
        piece = chunk[:room]
        try:
            win.addstr(y, col, piece, attr)
        except curses.error:
            return
        col += len(piece)
