"""Thin CLI bridge: step-by-step Cua sandbox control for batch workers.

Does not import claude_driver (keeps dependency graph acyclic).
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
import atexit
import shutil
import signal
import subprocess
import sys
import threading
import urllib.request
from pathlib import Path
from typing import Any

from .config import REPORTS_DIR
from .sandbox_runtime import (
    LINUX_CONTAINER_IMAGE,
    LINUX_DOCKER_PLATFORM,
    apply_no_proxy_env,
    linux_container_image,
    linux_docker_runtime,
)
from .tasks import read_metadata, update_metadata

SANDBOX_JSON = "sandbox.json"
LAST_SHELL_JSON = ".sandbox_ctl_last_shell.json"
_MIN_SCREENSHOT_BYTES = 1000
ANALYZER_SANDBOX_PREFIX = "analyzer-"

_cleanup_lock = threading.Lock()
_cleanup_done = False
_batch_exit_hooks_installed = False
_prev_sigint_handler: Any = None
_prev_sigterm_handler: Any = None


def _emit(payload: dict, *, file: Path | None = None) -> None:
    """Print one JSON line to stdout (always flushed) and optionally persist."""
    line = json.dumps(payload, ensure_ascii=False) + "\n"
    sys.stdout.write(line)
    sys.stdout.flush()
    if file is not None:
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(line, encoding="utf-8")


def sandbox_json_path(out_dir: Path) -> Path:
    return out_dir.resolve() / SANDBOX_JSON


def load_sandbox_info(out_dir: Path) -> dict[str, Any]:
    path = sandbox_json_path(out_dir)
    if not path.is_file():
        raise FileNotFoundError(f"{SANDBOX_JSON} not found under {out_dir}; run bootstrap first")
    return json.loads(path.read_text(encoding="utf-8"))


def write_sandbox_info(out_dir: Path, info: dict[str, Any]) -> Path:
    path = sandbox_json_path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(info, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def _derive_sandbox_name(out_dir: Path) -> str:
    base = out_dir.resolve().name
    safe = re.sub(r"[^a-zA-Z0-9._-]+", "-", base).strip("-").lower()
    safe = safe[:48] or "task"
    return f"analyzer-{safe}"


def _api_url_from_sb(sb: Any) -> str:
    rt = getattr(sb, "_runtime_info", None)
    if rt and getattr(rt, "api_port", None):
        host = getattr(rt, "host", None) or "127.0.0.1"
        return f"http://{host}:{rt.api_port}"
    raise RuntimeError("sandbox has no api_port in runtime_info")


def _merge_metadata_sandbox(out_dir: Path, name: str, api_url: str, local: bool) -> None:
    meta = read_metadata(out_dir)
    if not meta:
        return
    sandbox = dict(meta.get("sandbox") or {})
    sandbox["name"] = name
    sandbox["api_url"] = api_url
    sandbox["local"] = local
    update_metadata(out_dir, sandbox=sandbox)


def _connect_from_info(info: dict[str, Any]) -> Any:
    from cua import Sandbox

    name = info["name"]
    local = bool(info.get("local", True))
    api_key = os.environ.get("CUA_API_KEY") if not local else None
    if info.get("api_url") and not local:
        return Sandbox.connect(
            name,
            local=False,
            api_key=api_key,
            http_url=info["api_url"],
        )
    return Sandbox.connect(name, local=local, api_key=api_key)


# cua-xfce Linux image ships Firefox only (no Chromium). Probe DISPLAY from /tmp/.X11-unix
# (often :1, not :0) before launching.
_LINUX_DISPLAY_PROBE = (
    'D="${DISPLAY:-}"; '
    'if [ -z "$D" ] || [ ! -S "/tmp/.X11-unix/X${D#:}" ] 2>/dev/null; then '
    "for x in /tmp/.X11-unix/X*; do "
    '[ -S "$x" ] || continue; '
    'D=":${x##*/X}"; break; '
    "done; "
    "fi; "
    'export DISPLAY="${D:-:1}"; '
)

_LINUX_FIREFOX_LAUNCH_SHELL = (
    _LINUX_DISPLAY_PROBE
    + "if pgrep -x firefox >/dev/null 2>&1; then exit 0; fi; "
    + "firefox --new-window about:blank >/dev/null 2>&1 & "
    + "sleep 3; "
    + "pgrep -x firefox >/dev/null"
)

# Best-effort: keep XFCE desktop awake during long batch runs (xset + xfconf + systemd).
_LINUX_XFCE_DISABLE_SLEEP_SHELL = (
    _LINUX_DISPLAY_PROBE
    + "if command -v xset >/dev/null 2>&1; then "
    + "xset s off -dpms s noblank 2>/dev/null || true; "
    + "fi; "
    + "if command -v xfconf-query >/dev/null 2>&1; then "
    + "xfconf-query -c xfce4-power-manager -p /xfce4-power-manager/inactivity-sleep-mode-on-ac -s 0 "
    + "2>/dev/null || true; "
    + "xfconf-query -c xfce4-power-manager -p /xfce4-power-manager/inactivity-sleep-mode-on-battery -s 0 "
    + "2>/dev/null || true; "
    + "xfconf-query -c xfce4-power-manager -p /xfce4-power-manager/blank-on-ac -s 0 "
    + "2>/dev/null || true; "
    + "xfconf-query -c xfce4-power-manager -p /xfce4-power-manager/blank-on-battery -s 0 "
    + "2>/dev/null || true; "
    + "xfconf-query -c xfce4-power-manager -p /xfce4-power-manager/dpms-on-ac-sleep -s 0 "
    + "2>/dev/null || true; "
    + "xfconf-query -c xfce4-power-manager -p /xfce4-power-manager/dpms-on-ac-off -s 0 "
    + "2>/dev/null || true; "
    + "xfconf-query -c screensaver -p /saver/enabled -s false 2>/dev/null || true; "
    + "xfconf-query -c screensaver -p /saver/idle-activation/enabled -s false 2>/dev/null || true; "
    + "fi; "
    + "if command -v systemctl >/dev/null 2>&1; then "
    + "systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target "
    + "2>/dev/null || true; "
    + "fi; "
    + "exit 0"
)


async def _launch_browser_once(out_dir: Path) -> int:
    """One-time shell helper to start Firefox; navigation after this is mouse/keyboard."""
    return await cmd_step_shell(out_dir, _LINUX_FIREFOX_LAUNCH_SHELL)


async def _disable_linux_xfce_sleep(out_dir: Path) -> None:
    """Best-effort disable screen blank/suspend on cua-xfce; never fails bootstrap."""
    rc = await cmd_step_shell(out_dir, _LINUX_XFCE_DISABLE_SLEEP_SHELL)
    if rc != 0:
        print(
            "warning: sandbox_ctl could not fully disable XFCE sleep (non-fatal)",
            file=sys.stderr,
        )


async def cmd_step_open_url(out_dir: Path, url: str, *, launch: bool = True) -> int:
    """Open URL in sandbox browser using keyboard focus + type (mouse-first navigation)."""
    if launch:
        await _launch_browser_once(out_dir)
        await asyncio.sleep(1.0)
    # Focus omnibox then type URL (Firefox on cua-xfce XFCE).
    await cmd_step_key(out_dir, "ctrl+l")
    await asyncio.sleep(0.4)
    await cmd_step_key(out_dir, "ctrl+a")
    await asyncio.sleep(0.1)
    await cmd_step_type(out_dir, url)
    await asyncio.sleep(0.2)
    await cmd_step_key(out_dir, "enter")
    await asyncio.sleep(2.0)
    _emit({"ok": True, "action": "open-url", "url": url})
    return 0


async def cmd_bootstrap(
    out_dir: Path,
    *,
    open_browser: bool,
    url: str | None = None,
) -> int:
    apply_no_proxy_env()
    out_dir = out_dir.resolve()
    if sandbox_json_path(out_dir).is_file():
        print(f"error: {SANDBOX_JSON} already exists; run teardown first", file=sys.stderr)
        return 1

    runtime = os.environ.get("ANALYZER_RUNTIME", "sandbox-local")
    image_key = os.environ.get("ANALYZER_SANDBOX_IMAGE", "linux").lower()
    local = runtime != "sandbox-cloud"
    name = _derive_sandbox_name(out_dir)

    from cua import Sandbox

    if local:
        if image_key not in ("auto", "linux"):
            print(
                f"warning: sandbox_ctl bootstrap only implements linux container; "
                f"got image={image_key!r}",
                file=sys.stderr,
            )
        sb = await Sandbox.create(
            linux_container_image(),
            name=name,
            local=True,
            runtime=linux_docker_runtime(ephemeral=False),
        )
        provider = "docker"
        image = os.environ.get("ANALYZER_LINUX_CONTAINER_IMAGE", LINUX_CONTAINER_IMAGE)
        platform = os.environ.get("ANALYZER_LINUX_DOCKER_PLATFORM", LINUX_DOCKER_PLATFORM)
    else:
        api_key = os.environ.get("CUA_API_KEY", "").strip()
        if not api_key:
            print("error: CUA_API_KEY required for cloud bootstrap", file=sys.stderr)
            return 1
        from cua import Image

        sb = await Sandbox.create(Image.linux(), name=name, local=False, api_key=api_key)
        provider = "cloud"
        image = "linux"
        platform = None

    api_url = _api_url_from_sb(sb)
    info = {
        "name": sb.name or name,
        "provider": provider,
        "api_url": api_url,
        "image": image,
        "platform": platform,
        "local": local,
    }
    write_sandbox_info(out_dir, info)
    _merge_metadata_sandbox(out_dir, info["name"], api_url, local)
    await sb.disconnect()

    _emit({"ok": True, "sandbox": info})

    if local and image_key in ("auto", "linux"):
        await _disable_linux_xfce_sleep(out_dir)

    if open_browser:
        target = (url or os.environ.get("ANALYZER_PRODUCT_URL") or "").strip()
        if target:
            return await cmd_step_open_url(out_dir, target, launch=True)
        return await _launch_browser_once(out_dir)
    return 0


async def cmd_teardown(out_dir: Path) -> int:
    apply_no_proxy_env()
    out_dir = out_dir.resolve()
    path = sandbox_json_path(out_dir)
    if not path.is_file():
        _emit({"ok": True, "skipped": "no sandbox.json"})
        return 0
    info = load_sandbox_info(out_dir)
    from cua import Sandbox

    try:
        await Sandbox.delete(
            info["name"],
            local=bool(info.get("local", True)),
            api_key=os.environ.get("CUA_API_KEY") if not info.get("local", True) else None,
        )
    except Exception as exc:
        print(f"warning: Sandbox.delete: {exc}", file=sys.stderr)
    path.unlink(missing_ok=True)
    _emit({"ok": True, "deleted": info["name"]})
    return 0


def cmd_status(out_dir: Path) -> int:
    out_dir = out_dir.resolve()
    path = sandbox_json_path(out_dir)
    if not path.is_file():
        _emit({"ok": False, "error": f"no {SANDBOX_JSON} in {out_dir}"})
        return 1
    info = load_sandbox_info(out_dir)
    _emit({"ok": True, "sandbox": info})
    print(json.dumps(info, indent=2, ensure_ascii=False))
    api_url = info.get("api_url", "")
    if api_url:
        try:
            req = urllib.request.Request(f"{api_url.rstrip('/')}/status", method="GET")
            with urllib.request.urlopen(req, timeout=5) as resp:
                body = resp.read().decode("utf-8", errors="replace")[:500]
            print(f"GET {api_url}/status -> {resp.status} {body[:200]}")
        except Exception as exc:
            print(f"GET {api_url}/status failed: {exc}", file=sys.stderr)
            return 1
    return 0


async def cmd_step_screenshot(out_dir: Path, out_path: Path) -> int:
    apply_no_proxy_env()
    info = load_sandbox_info(out_dir)
    out_path = out_path if out_path.is_absolute() else (out_dir.resolve() / out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    async with _connect_from_info(info) as sb:
        png = await sb.screenshot()

    out_path.write_bytes(png)
    ok = len(png) >= _MIN_SCREENSHOT_BYTES
    _emit({"ok": ok, "path": str(out_path), "bytes": len(png)})
    return 0 if ok else 1


def _resolve_shell_command(shell_cmd: str | None, shell_argv: list[str]) -> str | None:
    if shell_cmd and shell_cmd.strip():
        return shell_cmd.strip()
    parts = list(shell_argv)
    if parts and parts[0] == "--":
        parts = parts[1:]
    # REMAINDER may capture ``-c cmd ...`` when -c follows positional out_dir.
    if parts and parts[0] in ("-c", "--cmd"):
        parts = parts[1:]
    if not parts:
        return None
    return " ".join(parts)


async def cmd_step_shell(out_dir: Path, command: str) -> int:
    apply_no_proxy_env()
    out_dir = out_dir.resolve()
    artifact = out_dir / LAST_SHELL_JSON
    try:
        info = load_sandbox_info(out_dir)
        async with _connect_from_info(info) as sb:
            result = await sb.shell.run(command)
    except Exception as exc:
        payload = {
            "ok": False,
            "returncode": 1,
            "stdout": "",
            "stderr": str(exc),
            "command": command,
            "artifact": str(artifact),
            "error": f"{type(exc).__name__}: {exc}",
        }
        _emit(payload, file=artifact)
        print(f"sandbox_ctl shell: {payload['error']}", file=sys.stderr, flush=True)
        return 1
    stdout = result.stdout or ""
    stderr = result.stderr or ""
    payload = {
        "ok": result.success,
        "returncode": result.returncode,
        "stdout": stdout,
        "stderr": stderr,
        "command": command,
        "artifact": str(artifact),
    }
    _emit(payload, file=artifact)
    # Human-readable tail on stderr so Bash-tool users still see something if stdout is sparse.
    print(
        f"sandbox_ctl shell: ok={result.success} rc={result.returncode} "
        f"stdout_bytes={len(stdout)} stderr_bytes={len(stderr)}",
        file=sys.stderr,
        flush=True,
    )
    if stdout:
        sys.stderr.write(stdout if stdout.endswith("\n") else stdout + "\n")
        sys.stderr.flush()
    if stderr:
        sys.stderr.write(stderr if stderr.endswith("\n") else stderr + "\n")
        sys.stderr.flush()
    return 0 if result.success else 1


async def cmd_step_click(out_dir: Path, x: int, y: int, *, button: str) -> int:
    apply_no_proxy_env()
    info = load_sandbox_info(out_dir)
    async with _connect_from_info(info) as sb:
        if button == "right":
            await sb.mouse.right_click(x, y)
        elif button == "double":
            await sb.mouse.double_click(x, y)
        else:
            await sb.mouse.click(x, y)
    _emit({"ok": True, "action": button, "x": x, "y": y})
    return 0


async def cmd_step_move(out_dir: Path, x: int, y: int) -> int:
    apply_no_proxy_env()
    info = load_sandbox_info(out_dir)
    async with _connect_from_info(info) as sb:
        await sb.mouse.move(x, y)
    _emit({"ok": True, "x": x, "y": y})
    return 0


async def cmd_step_type(out_dir: Path, text: str) -> int:
    apply_no_proxy_env()
    info = load_sandbox_info(out_dir)
    async with _connect_from_info(info) as sb:
        await sb.keyboard.type(text)
    _emit({"ok": True, "chars": len(text)})
    return 0


# computer-server / cua_auto hotkey() only accepts lowercase names (see cua_auto.keyboard._SPECIAL).
# Do not emit pynput-style PascalCase (Return, Escape) — HTTP transport rejects them.
_KEY_ALIASES: dict[str, str] = {
    "escape": "escape",
    "esc": "escape",
    "enter": "enter",
    "return": "enter",
    "control": "ctrl",
    "command": "meta",
    "cmd": "meta",
    "win": "meta",
    "super": "meta",
    "option": "alt",
}


def _normalize_keys(keys: str) -> list[str]:
    parts = [k.strip() for k in keys.split("+") if k.strip()]
    if not parts:
        return []
    out: list[str] = []
    for p in parts:
        lk = p.lower()
        out.append(_KEY_ALIASES.get(lk, lk))
    return out


async def cmd_step_key(out_dir: Path, keys: str) -> int:
    apply_no_proxy_env()
    info = load_sandbox_info(out_dir)
    key_list = _normalize_keys(keys)
    async with _connect_from_info(info) as sb:
        await sb.keyboard.keypress(key_list)
    _emit({"ok": True, "keys": keys})
    return 0


async def cmd_step_scroll(
    out_dir: Path, x: int, y: int, *, scroll_x: int = 0, scroll_y: int = 3
) -> int:
    apply_no_proxy_env()
    info = load_sandbox_info(out_dir)
    async with _connect_from_info(info) as sb:
        # cua_sandbox Mouse.scroll sends {x,y,scroll_x,scroll_y}, but computer-server
        # LinuxAutomationHandler.scroll(x,y) treats x/y as wheel deltas and drops
        # scroll_x/scroll_y (see trycua/cua computer_server/handlers/linux.py). LocalTransport
        # does move+scroll correctly; HTTP transport to Docker does not. Work around by
        # moving first, then scroll_down/up (vertical) or raw scroll deltas (horizontal).
        await sb.mouse.move(x, y)
        transport = sb._transport
        if scroll_y < 0:
            await transport.send("scroll_down", clicks=abs(scroll_y))
        elif scroll_y > 0:
            await transport.send("scroll_up", clicks=scroll_y)
        if scroll_x < 0:
            await transport.send("scroll", x=-abs(scroll_x), y=0)
        elif scroll_x > 0:
            await transport.send("scroll", x=abs(scroll_x), y=0)
    _emit({"ok": True, "x": x, "y": y, "scroll_x": scroll_x, "scroll_y": scroll_y})
    return 0


async def cmd_step_screen_size(out_dir: Path) -> int:
    apply_no_proxy_env()
    info = load_sandbox_info(out_dir)
    async with _connect_from_info(info) as sb:
        width, height = await sb.screen.size()
    _emit({"ok": True, "width": width, "height": height})
    return 0


def _batch_cleanup_disabled() -> bool:
    return os.environ.get("ANALYZER_BATCH_NO_CLEANUP", "").strip().lower() in (
        "1",
        "true",
        "yes",
        "on",
    )


def _collect_sandbox_names_from_reports() -> set[str]:
    names: set[str] = set()
    if not REPORTS_DIR.is_dir():
        return names
    for path in REPORTS_DIR.glob("*/sandbox.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        name = (data.get("name") or "").strip()
        if name:
            names.add(name)
    return names


def _docker_cua_sandbox_container_names() -> set[str]:
    """Container names with Cua sandbox label (running or stopped)."""
    if not shutil.which("docker"):
        return set()
    proc = subprocess.run(
        [
            "docker",
            "ps",
            "-aq",
            "--filter",
            "label=cua.sandbox=true",
            "--format",
            "{{.Names}}",
        ],
        capture_output=True,
        text=True,
        timeout=60,
    )
    if proc.returncode != 0:
        return set()
    return {line.strip() for line in proc.stdout.splitlines() if line.strip()}


def _docker_force_rm(names: set[str]) -> list[str]:
    removed: list[str] = []
    if not names or not shutil.which("docker"):
        return removed
    for name in sorted(names):
        proc = subprocess.run(
            ["docker", "rm", "-f", name],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if proc.returncode == 0:
            removed.append(name)
    return removed


def _unlink_sandbox_json_for_name(name: str) -> None:
    if not REPORTS_DIR.is_dir():
        return
    for path in REPORTS_DIR.glob("*/sandbox.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        if data.get("name") == name:
            path.unlink(missing_ok=True)


async def cmd_cleanup_all(*, prefix: str = ANALYZER_SANDBOX_PREFIX) -> int:
    """Stop/remove local Cua Docker sandboxes (batch exit / manual cleanup)."""
    apply_no_proxy_env()
    from cua import Sandbox

    docker_names = _docker_cua_sandbox_container_names()
    targets: set[str] = set(docker_names)
    targets |= _collect_sandbox_names_from_reports()

    try:
        listed = await Sandbox.list(local=True)
        for info in listed:
            if info.name:
                targets.add(info.name)
    except Exception as exc:
        print(f"warning: Sandbox.list: {exc}", file=sys.stderr)

    to_delete = set(docker_names)
    to_delete |= {n for n in targets if n.startswith(prefix)}

    deleted: list[str] = []
    errors: list[str] = []
    for name in sorted(to_delete):
        try:
            await Sandbox.delete(name, local=True)
            deleted.append(name)
            _unlink_sandbox_json_for_name(name)
        except Exception as exc:
            errors.append(f"{name}: {exc}")

    docker_removed = _docker_force_rm(to_delete - set(deleted))
    deleted.extend(n for n in docker_removed if n not in deleted)

    leftover = _docker_cua_sandbox_container_names() - set(deleted)
    if leftover:
        docker_removed2 = _docker_force_rm(leftover)
        deleted.extend(n for n in docker_removed2 if n not in deleted)

    payload = {
        "ok": not errors,
        "deleted": deleted,
        "errors": errors,
        "count": len(deleted),
    }
    _emit(payload)
    if deleted:
        print(
            f"sandbox_ctl cleanup: removed {len(deleted)} container(s)",
            file=sys.stderr,
            flush=True,
        )
    for err in errors:
        print(f"sandbox_ctl cleanup: {err}", file=sys.stderr)
    return 0 if not errors else 1


def reset_batch_cleanup_gate() -> None:
    """Allow a new batch run to run exit cleanup again."""
    global _cleanup_done
    with _cleanup_lock:
        _cleanup_done = False


def docker_cleanup_sync_quick() -> int:
    """SIGINT-safe: ``docker rm -f`` Cua containers without asyncio (for signal handler)."""
    if _batch_cleanup_disabled():
        return 0
    names = _docker_cua_sandbox_container_names()
    names |= {
        n
        for n in _collect_sandbox_names_from_reports()
        if n.startswith(ANALYZER_SANDBOX_PREFIX)
    }
    removed = _docker_force_rm(names)
    if removed:
        print(
            f"sandbox_ctl: 已停止 {len(removed)} 个 Docker 沙盒容器",
            file=sys.stderr,
            flush=True,
        )
    return len(removed)


def _batch_signal_handler(signum: int, frame: Any) -> None:
    """First Ctrl+C: quick docker stop; then raise KeyboardInterrupt for ``finally``."""
    try:
        docker_cleanup_sync_quick()
    except Exception:
        pass
    raise KeyboardInterrupt


def install_batch_exit_hooks(*, local: bool) -> None:
    """Register SIGINT/SIGTERM + atexit so forced exit still cleans Docker sandboxes."""
    global _batch_exit_hooks_installed, _prev_sigint_handler, _prev_sigterm_handler
    if not local or _batch_cleanup_disabled() or _batch_exit_hooks_installed:
        return
    _prev_sigint_handler = signal.getsignal(signal.SIGINT)
    _prev_sigterm_handler = signal.getsignal(signal.SIGTERM)
    signal.signal(signal.SIGINT, _batch_signal_handler)
    signal.signal(signal.SIGTERM, _batch_signal_handler)
    atexit.register(cleanup_all_local_sandboxes)
    _batch_exit_hooks_installed = True


def uninstall_batch_exit_hooks() -> None:
    global _batch_exit_hooks_installed, _prev_sigint_handler, _prev_sigterm_handler
    if not _batch_exit_hooks_installed:
        return
    if _prev_sigint_handler is not None:
        signal.signal(signal.SIGINT, _prev_sigint_handler)
    if _prev_sigterm_handler is not None:
        signal.signal(signal.SIGTERM, _prev_sigterm_handler)
    _prev_sigint_handler = None
    _prev_sigterm_handler = None
    _batch_exit_hooks_installed = False


def cleanup_all_local_sandboxes(*, force: bool = False) -> None:
    """Idempotent batch-exit hook: tear down Cua Docker sandboxes. Never raises."""
    global _cleanup_done
    if _batch_cleanup_disabled():
        return
    with _cleanup_lock:
        if _cleanup_done and not force:
            return
        _cleanup_done = True
    try:
        asyncio.run(cmd_cleanup_all())
    except Exception as exc:
        print(f"sandbox_ctl cleanup: {exc}", file=sys.stderr, flush=True)
        try:
            docker_cleanup_sync_quick()
        except Exception:
            pass


def teardown_out_dir(out_dir: Path) -> None:
    """Best-effort teardown for batch finally hook; never raises."""
    try:
        asyncio.run(cmd_teardown(out_dir))
    except Exception as exc:
        print(f"sandbox_ctl teardown: {exc}", file=sys.stderr)


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Step-by-step Cua sandbox control for product-analyzer batch")
    sub = p.add_subparsers(dest="command", required=True)

    boot = sub.add_parser("bootstrap", help="Create named sandbox and write sandbox.json")
    boot.add_argument("out_dir", type=Path)
    boot.add_argument(
        "--open-browser",
        action="store_true",
        help="After bootstrap, launch Firefox (cua-xfce; use with --url for Ctrl+L navigation)",
    )
    boot.add_argument(
        "--url",
        default=None,
        help="Product homepage URL (opens via step open-url / Ctrl+L, not wget)",
    )

    sub.add_parser("teardown", help="Delete sandbox and remove sandbox.json").add_argument(
        "out_dir", type=Path
    )
    sub.add_parser(
        "cleanup-all",
        help="Remove all local Cua Docker sandboxes (analyzer-* + label cua.sandbox=true)",
    )
    sub.add_parser("status", help="Print sandbox.json and probe /status").add_argument(
        "out_dir", type=Path
    )

    step = sub.add_parser("step", help="Single sandbox action")
    step_sub = step.add_subparsers(dest="step_cmd", required=True)

    shot = step_sub.add_parser("screenshot", help="Save PNG to --out path")
    shot.add_argument("out_dir", type=Path)
    shot.add_argument("--out", type=Path, required=True)

    shell = step_sub.add_parser(
        "shell",
        help="Run one shell command in sandbox (prefer -c)",
    )
    shell.add_argument("out_dir", type=Path)
    shell.add_argument(
        "-c",
        "--cmd",
        dest="shell_cmd",
        metavar="CMD",
        help="Shell command string (required unless legacy args after --)",
    )
    shell.add_argument(
        "shell_argv",
        nargs=argparse.REMAINDER,
        metavar="[-- CMD ...]",
        help="Legacy: command tokens after --",
    )

    click_p = step_sub.add_parser("click", help="Click at x y")
    click_p.add_argument("out_dir", type=Path)
    click_p.add_argument("x", type=int)
    click_p.add_argument("y", type=int)
    click_p.add_argument("--button", choices=("left", "right", "double"), default="left")

    move_p = step_sub.add_parser("move", help="Move cursor to x y")
    move_p.add_argument("out_dir", type=Path)
    move_p.add_argument("x", type=int)
    move_p.add_argument("y", type=int)

    type_p = step_sub.add_parser("type", help="Type text")
    type_p.add_argument("out_dir", type=Path)
    type_p.add_argument("text")

    key_p = step_sub.add_parser("key", help="Keypress (enter or ctrl+c)")
    key_p.add_argument("out_dir", type=Path)
    key_p.add_argument("keys")

    scroll_p = step_sub.add_parser("scroll", help="Scroll at x y")
    scroll_p.add_argument("out_dir", type=Path)
    scroll_p.add_argument("x", type=int)
    scroll_p.add_argument("y", type=int)
    scroll_p.add_argument("--scroll-x", type=int, default=0)
    scroll_p.add_argument("--scroll-y", type=int, default=3)

    step_sub.add_parser("screen-size", help="Print sandbox display width x height").add_argument(
        "out_dir", type=Path
    )

    open_url = step_sub.add_parser(
        "open-url",
        help="Launch browser (once) and open URL via keyboard (mouse-first)",
    )
    open_url.add_argument("out_dir", type=Path)
    open_url.add_argument("url")
    open_url.add_argument(
        "--no-launch",
        action="store_true",
        help="Skip Firefox launch (browser already running)",
    )

    return p


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if args.command == "bootstrap":
        return asyncio.run(
            cmd_bootstrap(
                args.out_dir,
                open_browser=args.open_browser,
                url=getattr(args, "url", None),
            )
        )
    if args.command == "teardown":
        return asyncio.run(cmd_teardown(args.out_dir))
    if args.command == "cleanup-all":
        return asyncio.run(cmd_cleanup_all())
    if args.command == "status":
        return cmd_status(args.out_dir)
    if args.command == "step":
        if args.step_cmd == "screenshot":
            return asyncio.run(cmd_step_screenshot(args.out_dir, args.out))
        if args.step_cmd == "shell":
            command = _resolve_shell_command(
                getattr(args, "shell_cmd", None),
                getattr(args, "shell_argv", None) or [],
            )
            if not command:
                print(
                    "error: shell requires -c '...' or arguments after --",
                    file=sys.stderr,
                )
                return 1
            return asyncio.run(cmd_step_shell(args.out_dir, command))
        if args.step_cmd == "click":
            return asyncio.run(
                cmd_step_click(args.out_dir, args.x, args.y, button=args.button)
            )
        if args.step_cmd == "move":
            return asyncio.run(cmd_step_move(args.out_dir, args.x, args.y))
        if args.step_cmd == "type":
            return asyncio.run(cmd_step_type(args.out_dir, args.text))
        if args.step_cmd == "key":
            return asyncio.run(cmd_step_key(args.out_dir, args.keys))
        if args.step_cmd == "scroll":
            return asyncio.run(
                cmd_step_scroll(
                    args.out_dir,
                    args.x,
                    args.y,
                    scroll_x=args.scroll_x,
                    scroll_y=args.scroll_y,
                )
            )
        if args.step_cmd == "screen-size":
            return asyncio.run(cmd_step_screen_size(args.out_dir))
        if args.step_cmd == "open-url":
            return asyncio.run(
                cmd_step_open_url(
                    args.out_dir,
                    args.url,
                    launch=not args.no_launch,
                )
            )
    return 1


if __name__ == "__main__":
    sys.exit(main())
