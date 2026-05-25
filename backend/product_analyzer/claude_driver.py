"""Claude Code 子进程编排:启动、流式渲染、ESC 暂停 + --resume 续跑、
session_id 即时落盘。是 ``cli.cmd_new`` / ``cli.cmd_resume`` 的唯一执行入口。
"""

from __future__ import annotations

import os
import subprocess
import sys
import threading
import time
from collections.abc import Callable
from pathlib import Path

from .config import DIM, RESET, YELLOW
from .renderer import format_event
from .tasks import update_metadata
from .ui import Spinner, err, log


_PRINT_LOCK = threading.Lock()


def _esc_watcher_unix(flag: dict, stop: dict, proc: subprocess.Popen) -> None:
    """Background thread: set ``flag['esc']=True`` if user presses ESC on
    stdin tty, AND terminate ``proc`` so the main loop's stdout iterator
    unblocks on EOF immediately instead of waiting for claude to emit the
    next event. POSIX-only (termios cbreak). Stops when ``stop['done']``."""
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
            r, _, _ = select.select([fd], [], [], 0.05)
            if not r:
                continue
            ch = os.read(fd, 1)
            if ch == b"\x1b":  # ESC
                flag["esc"] = True
                try:
                    proc.terminate()
                except (ProcessLookupError, OSError):
                    pass
                return
    finally:
        try:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)
        except (termios.error, OSError):
            pass


def _external_esc_poller(
    flag: dict, stop: dict, proc: subprocess.Popen
) -> None:
    """Dashboard sets ``flag['esc']=True``; terminate *proc* promptly so the
    stdout loop unblocks even when claude is idle (no stream-json lines)."""
    while not stop.get("done"):
        if flag.get("esc"):
            try:
                proc.terminate()
            except (ProcessLookupError, OSError):
                pass
            return
        time.sleep(0.05)


def _spawn_claude(
    prompt: str,
    resume_id: str | None,
    *,
    env: dict[str, str] | None = None,
    mcp_config: Path | None = None,
    quiet: bool = False,
) -> subprocess.Popen:
    cmd = [
        "claude", "--print",
        "--output-format", "stream-json",
        "--verbose",
        "--input-format", "text",
        "--permission-mode", "bypassPermissions",
    ]
    if resume_id:
        cmd += ["--resume", resume_id]
    if mcp_config is not None:
        cmd += ["--mcp-config", str(mcp_config)]
    if not quiet:
        log(f"启动 claude 子进程: {' '.join(cmd)}")
    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        env=env,
    )
    assert proc.stdin is not None
    proc.stdin.write(prompt)
    proc.stdin.close()
    return proc


def _read_supplement() -> str | None:
    """After ESC, ask for a supplemental message. Returns the message
    (non-empty) or None to abort entirely."""
    print(f"\n{YELLOW}── 已暂停。{RESET}")
    print(f"{DIM}    输入补充指令后回车继续(空行则放弃,直接退出)。多行用反斜杠续行。{RESET}")
    try:
        lines: list[str] = []
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


def run_claude(
    prompt: str,
    *,
    resume_id: str | None = None,
    out_dir: Path | None = None,
    non_interactive: bool = False,
    log_file: Path | None = None,
    env: dict[str, str] | None = None,
    terminal_prefix: str | None = None,
    mcp_config: Path | None = None,
    esc_flag: dict | None = None,
    event_sink: Callable[[list[str], dict], None] | None = None,
    mirror_stdout: bool = True,
    supplement_provider: Callable[[], str | None] | None = None,
) -> int:
    """Run claude in stream-json mode with ESC-pause + resume support.

    Outer loop:
      1. spawn claude (fresh OR with --resume <id>)
      2. background thread watches stdin tty for ESC
      3. main loop reads stream-json, pretty-prints, captures ``session_id``
         and persists it to ``<out_dir>/metadata.json`` so a later run can resume
      4. if ESC pressed: terminate, ask user for supplemental input, then
         re-spawn with --resume <session_id> and the new prompt
      5. exit when claude exits without a pending resume request

    Args:
        prompt: initial user message
        resume_id: existing claude session id to resume (used by cmd_resume)
        out_dir: where to persist ``last_session_id``; None = no persistence
        non_interactive: disable ESC/spinner UI; intended for batch workers
        log_file: optional file that receives raw stream-json/stdout
        env: optional environment for the Claude subprocess
        terminal_prefix: prefix for mirrored non-interactive terminal output
        mcp_config: optional JSON file for ``claude --mcp-config`` (cloud batch Cua MCP)
        esc_flag: external pause flag (dashboard); skips internal ESC watcher
        event_sink: receive formatted lines + state (batch dashboard)
        mirror_stdout: when False, do not print to terminal (events still go to sink)
        supplement_provider: after ESC, obtain resume text (batch dashboard)
    """
    raw_dump_path = os.environ.get("ANALYZE_RAW_LOG")
    raw_fh = open(raw_dump_path, "a", encoding="utf-8") if raw_dump_path else None
    log_fh = open(log_file, "a", encoding="utf-8") if log_file else None
    state: dict = {"session_id": None, "last_action": "starting"}

    current_prompt = prompt
    final_rc = 0

    try:
        while True:
            use_external_esc = esc_flag is not None
            local_esc = esc_flag if use_external_esc else {"esc": False}
            proc = _spawn_claude(
                current_prompt,
                resume_id,
                env=env,
                mcp_config=mcp_config,
                quiet=bool(event_sink and not mirror_stdout),
            )
            assert proc.stdout is not None
            stop_flag = {"done": False}
            watcher: threading.Thread | None = None
            esc_poller: threading.Thread | None = None
            if use_external_esc:
                esc_poller = threading.Thread(
                    target=_external_esc_poller,
                    args=(local_esc, stop_flag, proc),
                    daemon=True,
                )
                esc_poller.start()
            elif (
                not non_interactive
                and sys.stdin.isatty()
            ):
                watcher = threading.Thread(
                    target=_esc_watcher_unix,
                    args=(local_esc, stop_flag, proc),
                    daemon=True,
                )
                watcher.start()
                print(f"{DIM}    (按 ESC 暂停并补充指令){RESET}")
            spinner: Spinner | None = None
            if not non_interactive:
                spinner = Spinner()
                spinner.set_label(state.get("last_action") or "starting")
                spinner.start()
            persisted_sid = state.get("session_id") if out_dir else None
            try:
                for line in proc.stdout:
                    if raw_fh:
                        raw_fh.write(line)
                        raw_fh.flush()
                    if log_fh:
                        log_fh.write(line)
                        log_fh.flush()
                    line = line.rstrip("\n")
                    if not line:
                        continue
                    pretty = format_event(line, state)
                    out_lines: list[str]
                    if pretty is None:
                        out_lines = [line]
                    else:
                        out_lines = pretty
                    if event_sink is not None:
                        event_sink(out_lines, dict(state))
                    if spinner is not None:
                        for p in out_lines:
                            spinner.write_above(p)
                        spinner.set_label(state.get("last_action") or "thinking")
                    elif mirror_stdout and non_interactive and terminal_prefix:
                        _write_prefixed(terminal_prefix, out_lines)
                    elif mirror_stdout and not non_interactive and event_sink is None:
                        for p in out_lines:
                            print(p, flush=True)
                    # Persist session_id the first time it changes — gives a
                    # resume target even if claude is killed mid-stream.
                    sid_now = state.get("session_id")
                    if out_dir and sid_now and sid_now != persisted_sid:
                        update_metadata(out_dir, last_session_id=sid_now)
                        persisted_sid = sid_now
                    if local_esc.get("esc"):
                        if spinner is not None:
                            spinner.stop()
                        if mirror_stdout:
                            print(
                                f"\n{YELLOW}ESC 收到,已停掉当前 claude 子进程…{RESET}",
                                flush=True,
                            )
                        try:
                            proc.terminate()
                            proc.wait(timeout=5)
                        except subprocess.TimeoutExpired:
                            proc.kill()
                        break
            except KeyboardInterrupt:
                if spinner is not None:
                    spinner.stop()
                proc.terminate()
                err("用户 Ctrl+C,中止")
                final_rc = 130
                stop_flag["done"] = True
                if watcher and watcher.is_alive():
                    watcher.join(timeout=1)
                break
            if spinner is not None:
                spinner.stop()
            stop_flag["done"] = True
            if watcher and watcher.is_alive():
                watcher.join(timeout=1)
            if esc_poller and esc_poller.is_alive():
                esc_poller.join(timeout=1)

            if not local_esc.get("esc"):
                final_rc = proc.wait()
                break

            if non_interactive and supplement_provider is None:
                final_rc = proc.wait()
                break

            # ESC path: collect supplemental prompt, prepare to resume.
            # watcher already terminated proc; reap it so we don't leak a zombie
            # while _read_supplement blocks on input().
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
            if supplement_provider is not None:
                sup = supplement_provider()
            else:
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
            local_esc["esc"] = False
            if mirror_stdout:
                log(f"续跑(session={sid or 'n/a'})…")
    finally:
        if raw_fh:
            raw_fh.close()
        if log_fh:
            log_fh.close()
    return final_rc


def _write_prefixed(prefix: str, lines: list[str]) -> None:
    """Mirror batch worker progress without interleaving partial lines."""
    with _PRINT_LOCK:
        for item in lines:
            for physical_line in item.splitlines() or [""]:
                print(f"{prefix}{physical_line}", flush=True)
