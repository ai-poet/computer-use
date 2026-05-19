"""Thin CLI bridge: step-by-step Cua sandbox control for batch workers.

Does not import claude_driver (keeps dependency graph acyclic).
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
import sys
import urllib.request
from pathlib import Path
from typing import Any

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


async def _launch_browser_once(out_dir: Path) -> int:
    """One-time shell helper to start Chromium; navigation after this is mouse/keyboard."""
    return await cmd_step_shell(
        out_dir,
        "chromium --no-sandbox --new-window about:blank >/dev/null 2>&1 & "
        "sleep 2 || firefox about:blank >/dev/null 2>&1 & sleep 2 || true",
    )


async def cmd_step_open_url(out_dir: Path, url: str, *, launch: bool = True) -> int:
    """Open URL in sandbox browser using keyboard focus + type (mouse-first navigation)."""
    if launch:
        await _launch_browser_once(out_dir)
        await asyncio.sleep(1.0)
    # Focus omnibox then type URL (works in Chromium/Firefox on XFCE).
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


_KEY_ALIASES: dict[str, str] = {
    "escape": "Escape",
    "esc": "Escape",
    "enter": "Return",
    "return": "Return",
}


def _normalize_keys(keys: str) -> list[str]:
    parts = [k.strip() for k in keys.split("+") if k.strip()]
    if len(parts) > 1:
        return [_KEY_ALIASES.get(p.lower(), p) for p in parts]
    single = parts[0] if parts else keys
    return [_KEY_ALIASES.get(single.lower(), single)]


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
        await sb.mouse.scroll(x, y, scroll_x, scroll_y)
    _emit({"ok": True, "x": x, "y": y, "scroll_x": scroll_x, "scroll_y": scroll_y})
    return 0


async def cmd_step_screen_size(out_dir: Path) -> int:
    apply_no_proxy_env()
    info = load_sandbox_info(out_dir)
    async with _connect_from_info(info) as sb:
        width, height = await sb.screen.size()
    _emit({"ok": True, "width": width, "height": height})
    return 0


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
        help="After bootstrap, launch browser (use with --url for mouse-first navigation)",
    )
    boot.add_argument(
        "--url",
        default=None,
        help="Product homepage URL (opens via step open-url / Ctrl+L, not wget)",
    )

    sub.add_parser("teardown", help="Delete sandbox and remove sandbox.json").add_argument(
        "out_dir", type=Path
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
        help="Skip chromium launch (browser already running)",
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
