#!/usr/bin/env python3
# cspell:ignore productivekitty kebab Popen rstrip ascii
"""
analyze_product.py — 产品分析自动化入口

输入:产品名 + 官网 URL [+ 可选下载链接]
输出:reports/<slug>-YYYY-MM-DD[-N]/{report.md, metadata.json, screenshots/}

双模式:
  交互式  →  python3 scripts/analyze_product.py
  参数式  →  python3 scripts/analyze_product.py "<产品名>" "<URL>" ["<下载链接>"]
            (任何缺失字段会回退到 input() 询问)

预检:
  1. claude CLI 在 PATH
  2. cua-driver 已安装(否则自动调 install_cua_driver.py)

执行:
  组装 prompt → claude --print --output-format stream-json --verbose →
  stream-json 全量事件流原样透传到终端,Claude 端使用 product-analyzer skill 完成分析。

退出码:
  0 成功
  1 预检失败 / 用户中断
  2 claude 子进程异常退出
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import time
import unicodedata
from pathlib import Path
from urllib.parse import urlparse


REPO_ROOT = Path(__file__).resolve().parent.parent
REPORTS_DIR = REPO_ROOT / "reports"
INSTALL_SCRIPT = REPO_ROOT / "scripts" / "install_cua_driver.py"

SWIFT_APP_BUNDLE = Path("/Applications/CuaDriver.app")
RS_APP_BUNDLE = Path("/Applications/CuaDriverRs.app")
RS_HOME_DIR = Path.home() / ".cua-driver-rs"


# ---------- helpers ----------

def log(msg: str) -> None:
    print(f"==> {msg}", flush=True)


def err(msg: str) -> None:
    print(f"error: {msg}", file=sys.stderr, flush=True)


# ---------- stream-json pretty printer (Claude-Code-style) ----------

_USE_COLOR = sys.stdout.isatty() and os.environ.get("NO_COLOR", "") == ""
RESET = "\x1b[0m" if _USE_COLOR else ""
DIM = "\x1b[2m" if _USE_COLOR else ""
BOLD = "\x1b[1m" if _USE_COLOR else ""
ITAL = "\x1b[3m" if _USE_COLOR else ""
GRAY = "\x1b[90m" if _USE_COLOR else ""
CYAN = "\x1b[36m" if _USE_COLOR else ""
GREEN = "\x1b[32m" if _USE_COLOR else ""
YELLOW = "\x1b[33m" if _USE_COLOR else ""
RED = "\x1b[31m" if _USE_COLOR else ""
MAGENTA = "\x1b[35m" if _USE_COLOR else ""
BLUE = "\x1b[34m" if _USE_COLOR else ""


def _trunc(s: str, n: int = 120) -> str:
    s = (s or "").replace("\n", " ⏎ ")
    if len(s) > n:
        return s[:n] + f"{DIM}…{RESET}"
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
    """Render a TodoWrite todo list as ☐/◐/☑ lines."""
    out = []
    glyphs = {"pending": ("☐", GRAY), "in_progress": ("◐", YELLOW), "completed": ("☑", GREEN)}
    for td in todos:
        if not isinstance(td, dict):
            continue
        status = td.get("status", "pending")
        glyph, color = glyphs.get(status, ("·", GRAY))
        # Different harnesses use different field names; try a few
        text = td.get("activeForm") if status == "in_progress" else None
        text = text or td.get("content") or td.get("subject") or td.get("description") or ""
        line = f"  {color}{glyph} {_trunc(text, 90)}{RESET}"
        if status == "completed":
            # strikethrough completed items
            line = f"  {color}{glyph} {DIM}{_trunc(text, 90)}{RESET}"
        out.append(line)
    return out


def _flatten_tool_result(content) -> tuple[str, bool]:
    """Return (text, is_error_hint). content can be str or list of {type:text,text:...}."""
    if isinstance(content, str):
        return content, False
    if isinstance(content, list):
        chunks = []
        for c in content:
            if isinstance(c, dict):
                if c.get("type") == "text":
                    chunks.append(c.get("text", ""))
        return "\n".join(chunks), False
    return str(content or ""), False


def format_event(raw: str, state: dict | None = None) -> list[str] | None:
    """Parse one stream-json line; return list of pretty lines (or None if not JSON).

    `state`, when provided, is a mutable dict the caller passes in so we can
    surface the session id back (used by the ESC resume loop) and track the
    last meaningful action for the loading spinner."""
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
            out.append(f"{DIM}── claude session · model={model} · cwd={cwd}{RESET}")
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
                    out.append(f"{DIM}{ITAL}✻ Thinking{RESET}")
                    for line in txt.split("\n"):
                        out.append(f"{DIM}  {line}{RESET}")
            elif btype == "text":
                txt = (block.get("text") or "").rstrip()
                if txt:
                    if state is not None:
                        state["last_action"] = "writing"
                    out.append(txt)
            elif btype == "tool_use":
                name = block.get("name", "?")
                summary = _summarize_tool_input(name, block.get("input"))
                tail = f" {DIM}{summary}{RESET}" if summary else ""
                out.append(f"{CYAN}● {name}{RESET}{tail}")
                if state is not None:
                    state["last_action"] = f"running {name}"
                # Expand todo lists inline so the user sees full plan + progress
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
                color = RED if is_err else GRAY
                first = txt.split("\n", 1)[0] if txt else "(empty)"
                tag = "↳ error" if is_err else "↳"
                out.append(f"  {color}{tag} {_trunc(first, 110)}{RESET}")
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
        color = GREEN if sub == "success" else YELLOW
        out.append(f"{color}{' · '.join(bits)}{RESET}")
        if state is not None:
            state["last_action"] = None
        return out

    return out


# ---------- /pretty printer ----------


def slugify(name: str) -> str:
    """ASCII-fold + kebab-case + 40-char cap. Falls back to product-<md5> for non-ASCII."""
    folded = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("ascii")
    folded = re.sub(r'[\\/:*?"<>|]', "", folded)
    folded = re.sub(r"\s+", "-", folded.strip())
    folded = re.sub(r"[^a-zA-Z0-9._-]", "", folded).strip("-_.").lower()
    if not folded:
        digest = hashlib.md5(name.encode("utf-8")).hexdigest()[:6]
        return f"product-{digest}"
    if len(folded) > 40:
        cut = folded[:40]
        last_dash = cut.rfind("-")
        folded = cut[:last_dash] if last_dash > 20 else cut
    return folded


def is_valid_url(s: str) -> bool:
    if not s:
        return False
    try:
        parsed = urlparse(s)
    except (ValueError, TypeError):
        return False
    return parsed.scheme in ("http", "https") and bool(parsed.netloc)


def prompt_str(prompt: str, validate=lambda s: bool(s.strip()), allow_empty: bool = False) -> str:
    """Loop input() until validate() passes. Empty allowed when allow_empty=True (returns '')."""
    while True:
        try:
            value = input(prompt).strip()
        except EOFError:
            err("输入流被关闭,中止")
            sys.exit(1)
        except KeyboardInterrupt:
            err("用户中断")
            sys.exit(1)
        if allow_empty and not value:
            return ""
        if validate(value):
            return value
        print("  输入无效,请重新输入")


# ---------- preflight ----------

def detect_host() -> tuple[str, str]:
    sys_lower = platform.system().lower()
    if sys_lower == "darwin":
        os_name = "darwin"
    elif sys_lower == "linux":
        os_name = "linux"
    elif sys_lower.startswith("win") or sys_lower == "windows":
        os_name = "windows"
    else:
        os_name = sys_lower
    machine = platform.machine().lower()
    if machine in ("amd64", "x86_64"):
        arch = "x86_64"
    elif machine in ("arm64", "aarch64"):
        arch = "arm64"
    else:
        arch = machine
    return os_name, arch


def cua_driver_installed() -> bool:
    """Detect Swift cua-driver OR cua-driver-rs."""
    if SWIFT_APP_BUNDLE.exists() or RS_APP_BUNDLE.exists() or RS_HOME_DIR.exists():
        return True
    found = shutil.which("cua-driver")
    if not found:
        return False
    real = os.path.realpath(found)
    return any(tag in real for tag in ("CuaDriver.app", "CuaDriverRs.app", "/.cua-driver-rs/"))


def ensure_claude_cli() -> None:
    if shutil.which("claude"):
        return
    err("未找到 `claude` CLI。请先安装 Claude Code:")
    err("  https://docs.claude.com/en/docs/claude-code")
    sys.exit(1)


def ensure_cua_driver() -> None:
    if cua_driver_installed():
        log("cua-driver 已安装")
        return
    log("cua-driver 未安装,自动调用 install_cua_driver.py 安装中...")
    if not INSTALL_SCRIPT.exists():
        err(f"找不到 {INSTALL_SCRIPT}")
        sys.exit(1)
    proxy_hint = any(os.environ.get(k) for k in ("https_proxy", "HTTPS_PROXY", "all_proxy", "ALL_PROXY"))
    if not proxy_hint:
        log("提示:install_cua_driver.py 会从 GitHub 下载安装包,如需代理请先 `export https_proxy=...`")
    rc = subprocess.call([sys.executable, str(INSTALL_SCRIPT)])
    if rc != 0:
        err(f"install_cua_driver.py 退出码 {rc};请手动跑一次后重试")
        sys.exit(1)
    if not cua_driver_installed():
        err("安装脚本退出码 0 但仍未检测到 cua-driver,请手动检查 PATH")
        sys.exit(1)
    log("cua-driver 安装完成")


# ---------- main flow ----------

def collect_inputs(args: argparse.Namespace) -> tuple[str, str, str | None]:
    if args.product_name and args.product_name.strip():
        product_name = args.product_name.strip()
    else:
        product_name = prompt_str("产品名: ")
    if len(product_name) > 80:
        err("产品名过长(>80 字符),请重新输入")
        product_name = prompt_str("产品名: ", validate=lambda s: 0 < len(s) <= 80)

    if args.url and args.url.strip():
        url = args.url.strip()
    else:
        url = prompt_str("官网 URL: ")

    if args.download_url is None:
        dl = prompt_str(
            "下载链接(可选,直接回车跳过): ",
            validate=lambda s: True,
            allow_empty=True,
        ) or None
    else:
        dl = args.download_url.strip() or None

    return product_name, url, dl


def prepare_output_dir(product_name: str) -> Path:
    today = dt.date.today().isoformat()
    base = REPORTS_DIR / f"{slugify(product_name)}-{today}"
    out = base
    n = 2
    while out.exists():
        out = base.with_name(f"{base.name}-{n}")
        n += 1
    (out / "screenshots").mkdir(parents=True)
    return out


def write_metadata_seed(out_dir: Path, product_name: str, url: str,
                        download_url: str | None) -> dict:
    host_os, host_arch = detect_host()
    meta = {
        "product_name": product_name,
        "url": url,
        "download_url": download_url,
        "host_os": host_os,
        "host_arch": host_arch,
        "started_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "finished_at": None,
        "mode": None,
        "screenshots": [],
        "warnings": [],
    }
    (out_dir / "metadata.json").write_text(
        json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return meta


def build_prompt(product_name: str, url: str, download_url: str | None,
                 out_dir: Path, host_os: str, host_arch: str) -> str:
    dl_line = f"- 下载链接(预先给定):{download_url}" if download_url else "- 下载链接:未提供,需要从官网自行定位"
    return f"""请使用 product-analyzer skill 完成产品分析。

**输入参数**(请把这些直接写进 metadata.json,不要修改值):
- 产品名:{product_name}
- 官网 URL:{url}
{dl_line}
- 输出目录(已建好,所有产物写到这里):{out_dir}
- 主机:{host_os}/{host_arch}

**要求**:
1. 严格遵循 .claude/skills/product-analyzer/SKILL.md 中的 canonical loop(7 步固定顺序)
2. 全程用 TodoWrite 维护进度,7 个 todos,每步开始前 in_progress、完成后 completed
3. 桌面端驱动一律走 cua-driver,严守 cua-driver SKILL 的 no-foreground 契约
4. 报告全程简体中文,3 个强制章节按顺序出现
5. 结束前在 metadata.json 里补齐 finished_at / mode / screenshots[] / warnings[]

现在开始执行。
"""


def _esc_watcher_unix(flag: dict, stop: dict) -> None:
    """Background thread: set flag['esc']=True if user presses ESC on stdin tty.

    POSIX-only (termios cbreak). Stop loop when stop['done']=True."""
    import select
    import termios
    import tty
    fd = sys.stdin.fileno()
    try:
        old = termios.tcgetattr(fd)
    except (termios.error, OSError):
        return  # not a tty
    try:
        tty.setcbreak(fd)
        while not stop.get("done"):
            r, _, _ = select.select([fd], [], [], 0.2)
            if not r:
                continue
            ch = os.read(fd, 1)
            if ch == b"\x1b":  # ESC
                flag["esc"] = True
                return
    finally:
        try:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)
        except (termios.error, OSError):
            pass


class Spinner:
    """A self-erasing one-line loading indicator that lives on the bottom of
    the terminal while real output streams above it.

    Usage:
        sp = Spinner()
        sp.start()
        for line in stream:
            sp.write_above(line)   # erase, print real content, re-paint
            sp.set_label(...)
        sp.stop()

    Auto-disabled when not a tty (CI / pipe / redirect)."""

    FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

    def __init__(self):
        self.enabled = sys.stdout.isatty() and _USE_COLOR
        self._label = "starting"
        self._frame_idx = 0
        self._lock = None
        self._thread = None
        self._stop = None
        self._painted = False
        self._start_time = 0.0

    def _paint(self) -> None:
        if not self.enabled:
            return
        elapsed = time.time() - self._start_time
        glyph = self.FRAMES[self._frame_idx % len(self.FRAMES)]
        line = f"{CYAN}{glyph}{RESET} {DIM}{self._label} · {elapsed:.0f}s · ESC 暂停{RESET}"
        sys.stdout.write("\r\x1b[2K" + line)
        sys.stdout.flush()
        self._painted = True

    def _erase(self) -> None:
        if not self.enabled or not self._painted:
            return
        sys.stdout.write("\r\x1b[2K")
        sys.stdout.flush()
        self._painted = False

    def _loop(self) -> None:
        while not self._stop.is_set():
            with self._lock:
                self._paint()
                self._frame_idx += 1
            self._stop.wait(0.1)
        with self._lock:
            self._erase()

    def start(self) -> None:
        if not self.enabled:
            return
        import threading
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._start_time = time.time()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        if not self.enabled or self._thread is None:
            return
        self._stop.set()
        self._thread.join(timeout=1)
        with self._lock:
            self._erase()
        self._thread = None

    def set_label(self, label: str | None) -> None:
        self._label = label or "thinking"

    def write_above(self, line: str) -> None:
        """Print a line above the spinner: erase, print, re-paint."""
        if not self.enabled:
            print(line, flush=True)
            return
        with self._lock:
            self._erase()
            sys.stdout.write(line + "\n")
            sys.stdout.flush()
            self._paint()


def _spawn_claude(prompt: str, resume_id: str | None) -> subprocess.Popen:
    cmd = [
        "claude", "--print",
        "--output-format", "stream-json",
        "--verbose",
        "--input-format", "text",
        "--permission-mode", "bypassPermissions",
    ]
    if resume_id:
        cmd += ["--resume", resume_id]
    log(f"启动 claude 子进程: {' '.join(cmd)}")
    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    assert proc.stdin is not None
    proc.stdin.write(prompt)
    proc.stdin.close()
    return proc


def _read_supplement() -> str | None:
    """After ESC, ask the user for a supplemental message.

    Returns the message (non-empty) or None to abort entirely."""
    print(f"\n{YELLOW}── 已暂停。{RESET}")
    print(f"{DIM}    输入补充指令后回车继续(空行则放弃,直接退出)。多行用反斜杠续行。{RESET}")
    try:
        lines = []
        while True:
            try:
                line = input("补充> " if not lines else "      ")
            except EOFError:
                break
            if line.endswith("\\"):
                lines.append(line[:-1])
                continue
            lines.append(line)
            break
        text = "\n".join(lines).strip()
        return text or None
    except KeyboardInterrupt:
        return None


def run_claude(prompt: str) -> int:
    """Run claude in stream-json mode with ESC-pause + resume support.

    Outer loop:
      1. spawn claude (fresh or with --resume <id>)
      2. background thread watches stdin tty for ESC
      3. main loop reads stream-json, pretty-prints, captures session_id
      4. if ESC pressed: terminate, ask user for supplemental input,
         then re-spawn with --resume <session_id> and the new prompt
      5. exit when claude exits without a pending resume request"""
    import threading
    raw_dump_path = os.environ.get("ANALYZE_RAW_LOG")
    raw_fh = open(raw_dump_path, "a", encoding="utf-8") if raw_dump_path else None
    state = {"session_id": None}

    current_prompt = prompt
    resume_id: str | None = None
    final_rc = 0

    try:
        while True:
            proc = _spawn_claude(current_prompt, resume_id)
            assert proc.stdout is not None
            esc_flag = {"esc": False}
            stop_flag = {"done": False}
            watcher = None
            if sys.stdin.isatty():
                watcher = threading.Thread(
                    target=_esc_watcher_unix, args=(esc_flag, stop_flag), daemon=True
                )
                watcher.start()
                print(f"{DIM}    (按 ESC 暂停并补充指令){RESET}")
            spinner = Spinner()
            spinner.set_label(state.get("last_action") or "starting")
            spinner.start()
            try:
                for line in proc.stdout:
                    if raw_fh:
                        raw_fh.write(line)
                        raw_fh.flush()
                    line = line.rstrip("\n")
                    if not line:
                        continue
                    pretty = format_event(line, state)
                    if pretty is None:
                        spinner.write_above(line)
                    else:
                        for p in pretty:
                            spinner.write_above(p)
                    spinner.set_label(state.get("last_action") or "thinking")
                    if esc_flag.get("esc"):
                        spinner.stop()
                        print(f"\n{YELLOW}ESC 收到,正在停掉当前 claude 子进程…{RESET}", flush=True)
                        proc.terminate()
                        try:
                            proc.wait(timeout=5)
                        except subprocess.TimeoutExpired:
                            proc.kill()
                        break
            except KeyboardInterrupt:
                spinner.stop()
                proc.terminate()
                err("用户 Ctrl+C,中止")
                final_rc = 130
                stop_flag["done"] = True
                if watcher and watcher.is_alive():
                    watcher.join(timeout=1)
                break
            spinner.stop()
            stop_flag["done"] = True
            if watcher and watcher.is_alive():
                watcher.join(timeout=1)

            if not esc_flag.get("esc"):
                final_rc = proc.wait()
                break

            # ESC path: collect supplemental prompt, prepare to resume
            sup = _read_supplement()
            if not sup:
                err("放弃续跑")
                final_rc = 130
                break
            sid = state.get("session_id")
            if not sid:
                err("没有捕获到 session_id,无法 --resume,直接重新发起新会话")
                resume_id = None
                current_prompt = sup
            else:
                resume_id = sid
                current_prompt = sup
            log(f"续跑(session={sid or 'n/a'})…")
    finally:
        if raw_fh:
            raw_fh.close()
    return final_rc


def post_check(out_dir: Path) -> None:
    report = out_dir / "report.md"
    meta = out_dir / "metadata.json"
    issues = []
    if not report.exists() or report.stat().st_size < 200:
        issues.append(f"{report} 缺失或过短")
    if not meta.exists():
        issues.append(f"{meta} 缺失")
    else:
        try:
            data = json.loads(meta.read_text(encoding="utf-8"))
            if not data.get("finished_at"):
                issues.append("metadata.json 中 finished_at 未补齐")
            if not data.get("mode"):
                issues.append("metadata.json 中 mode 未补齐")
        except json.JSONDecodeError as e:
            issues.append(f"metadata.json 解析失败: {e}")
    if issues:
        err("产物校验发现问题:")
        for x in issues:
            err(f"  - {x}")
    else:
        log(f"产物校验通过: {out_dir}")


# ---------- entry ----------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="产品分析自动化入口。零参数进入交互模式;给参数则跳过对应交互。",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "示例:\n"
            "  交互式:  python3 scripts/analyze_product.py\n"
            "  参数式:  python3 scripts/analyze_product.py \"ProductiveKitty\" "
            "\"https://productivekitty.masterwordai.com\"\n"
            "  全参:    python3 scripts/analyze_product.py NAME URL DOWNLOAD_URL\n"
        ),
    )
    parser.add_argument("product_name", nargs="?", default=None,
                        help="产品名(展示用原文)。省略则交互输入。")
    parser.add_argument("url", nargs="?", default=None,
                        help="产品官网 URL。省略则交互输入。")
    parser.add_argument("download_url", nargs="?", default=None,
                        help="可选:直接指向当前主机能用的安装包。给空字符串视为未提供。")
    args = parser.parse_args()

    log("预检:claude CLI")
    ensure_claude_cli()
    log("预检:cua-driver")
    ensure_cua_driver()

    product_name, url, download_url = collect_inputs(args)
    log(f"输入已确认:product_name={product_name!r}  url={url!r}  download_url={download_url!r}")

    out_dir = prepare_output_dir(product_name)
    log(f"输出目录: {out_dir}")
    meta = write_metadata_seed(out_dir, product_name, url, download_url)

    prompt = build_prompt(product_name, url, download_url, out_dir,
                          meta["host_os"], meta["host_arch"])
    rc = run_claude(prompt)
    log(f"claude 子进程退出码: {rc}")

    post_check(out_dir)

    if rc != 0:
        err("claude 子进程非零退出,请翻阅上方事件流定位问题")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
