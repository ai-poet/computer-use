"""Mobile-focused Cua sandbox control for Android APK runs.

This is intentionally separate from ``sandbox_ctl``. The Linux bridge drives a
desktop Firefox sandbox with mouse/keyboard coordinates; Android needs a
persistent QEMU sandbox plus ``sb.mobile`` touch APIs.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
import shlex
import sys
from pathlib import Path
from typing import Any

from .tasks import read_metadata, update_metadata

ANDROID_JSON = "android_sandbox.json"
ANDROID_IMAGE = "trycua/cua-qemu-android:latest"
_MIN_SCREENSHOT_BYTES = 1000


def _emit(payload: dict[str, Any], *, file: Path | None = None) -> None:
    line = json.dumps(payload, ensure_ascii=False) + "\n"
    sys.stdout.write(line)
    sys.stdout.flush()
    if file is not None:
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(line, encoding="utf-8")


def android_json_path(out_dir: Path) -> Path:
    return out_dir.resolve() / ANDROID_JSON


def load_android_info(out_dir: Path) -> dict[str, Any]:
    path = android_json_path(out_dir)
    if not path.is_file():
        raise FileNotFoundError(f"{ANDROID_JSON} not found under {out_dir}; run bootstrap first")
    return json.loads(path.read_text(encoding="utf-8"))


def write_android_info(out_dir: Path, info: dict[str, Any]) -> Path:
    path = android_json_path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(info, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def _derive_android_name(out_dir: Path) -> str:
    base = out_dir.resolve().name
    safe = re.sub(r"[^a-zA-Z0-9._-]+", "-", base).strip("-").lower()
    safe = safe[:44] or "task"
    return f"analyzer-android-{safe}"


def _api_url_from_sb(sb: Any) -> str | None:
    rt = getattr(sb, "_runtime_info", None)
    if rt and getattr(rt, "api_port", None):
        host = getattr(rt, "host", None) or "127.0.0.1"
        return f"http://{host}:{rt.api_port}"
    return None


def _connect_from_info(info: dict[str, Any]) -> Any:
    from cua import Sandbox

    kwargs: dict[str, Any] = {
        "name": info["name"],
        "local": bool(info.get("local", True)),
        "api_key": os.environ.get("CUA_API_KEY") if not info.get("local", True) else None,
    }
    api_url = (info.get("api_url") or "").strip()
    if api_url:
        kwargs["http_url"] = api_url
    return Sandbox.connect(**kwargs)


def _merge_metadata_android(out_dir: Path, **fields: Any) -> None:
    meta = read_metadata(out_dir) or {}
    android = dict(meta.get("android") or {})
    android.update(fields)
    update_metadata(out_dir, android=android)


async def cmd_bootstrap(
    out_dir: Path,
    *,
    apk_path: Path | None,
    name: str | None,
    install_with_image: bool,
) -> int:
    out_dir = out_dir.resolve()
    if android_json_path(out_dir).is_file():
        print(f"error: {ANDROID_JSON} already exists; run teardown first", file=sys.stderr)
        return 1

    from cua import Image, Sandbox

    sandbox_name = name or _derive_android_name(out_dir)
    image = Image.from_registry(ANDROID_IMAGE)
    if apk_path is not None and install_with_image:
        image = image.apk_install(str(apk_path))

    sb = await Sandbox.create(image, name=sandbox_name, local=True)
    api_url = _api_url_from_sb(sb)
    info = {
        "name": sb.name or sandbox_name,
        "image": ANDROID_IMAGE,
        "local": True,
        "api_url": api_url,
        "apk_path": str(apk_path) if apk_path else None,
        "install_with_image": bool(apk_path and install_with_image),
    }
    write_android_info(out_dir, info)
    _merge_metadata_android(
        out_dir,
        mode="bootstrapped",
        sandbox=info["name"],
        image=ANDROID_IMAGE,
        apk_file=str(apk_path) if apk_path else None,
    )
    await sb.disconnect()
    _emit({"ok": True, "android": info})
    return 0


async def cmd_install(out_dir: Path, apk_path: Path) -> int:
    info = load_android_info(out_dir)
    quoted_apk = shlex.quote(str(apk_path))
    async with _connect_from_info(info) as sb:
        result = await sb.shell.run(f"adb install -r {quoted_apk}", timeout=180)
    ok = bool(getattr(result, "success", False))
    _merge_metadata_android(
        out_dir,
        apk_file=str(apk_path),
        mode="installed" if ok else "failed",
    )
    _emit(
        {
            "ok": ok,
            "returncode": getattr(result, "returncode", 1),
            "stdout": getattr(result, "stdout", ""),
            "stderr": getattr(result, "stderr", ""),
        }
    )
    return 0 if ok else 1


async def cmd_screenshot(out_dir: Path, out_path: Path) -> int:
    info = load_android_info(out_dir)
    out_path = out_path if out_path.is_absolute() else out_dir.resolve() / out_path
    out_path.parent.mkdir(parents=True, exist_ok=True)
    async with _connect_from_info(info) as sb:
        png = await sb.screenshot()
    out_path.write_bytes(png)
    ok = len(png) >= _MIN_SCREENSHOT_BYTES
    _emit({"ok": ok, "path": str(out_path), "bytes": len(png)})
    return 0 if ok else 1


async def cmd_tap(out_dir: Path, x: int, y: int) -> int:
    info = load_android_info(out_dir)
    async with _connect_from_info(info) as sb:
        await sb.mobile.tap(x, y)
    _emit({"ok": True, "action": "tap", "x": x, "y": y})
    return 0


async def cmd_swipe(out_dir: Path, x1: int, y1: int, x2: int, y2: int, duration_ms: int) -> int:
    info = load_android_info(out_dir)
    async with _connect_from_info(info) as sb:
        await sb.mobile.swipe(x1, y1, x2, y2, duration_ms=duration_ms)
    _emit({"ok": True, "action": "swipe", "from": [x1, y1], "to": [x2, y2]})
    return 0


async def cmd_type(out_dir: Path, text: str) -> int:
    info = load_android_info(out_dir)
    async with _connect_from_info(info) as sb:
        await sb.mobile.type_text(text)
    _emit({"ok": True, "chars": len(text)})
    return 0


async def cmd_key(out_dir: Path, key: str) -> int:
    info = load_android_info(out_dir)
    async with _connect_from_info(info) as sb:
        mobile = sb.mobile
        key_lower = key.lower()
        if key_lower == "back":
            await mobile.back()
        elif key_lower == "home":
            await mobile.home()
        elif key_lower == "enter":
            await mobile.enter()
        elif key_lower == "recents":
            await mobile.recents()
        else:
            await mobile.key(int(key))
    _emit({"ok": True, "key": key})
    return 0


async def cmd_shell(out_dir: Path, command: str) -> int:
    info = load_android_info(out_dir)
    async with _connect_from_info(info) as sb:
        result = await sb.shell.run(command)
    ok = bool(getattr(result, "success", False))
    _emit(
        {
            "ok": ok,
            "returncode": getattr(result, "returncode", 1),
            "stdout": getattr(result, "stdout", ""),
            "stderr": getattr(result, "stderr", ""),
            "command": command,
        }
    )
    return 0 if ok else 1


async def cmd_teardown(out_dir: Path) -> int:
    path = android_json_path(out_dir)
    if not path.is_file():
        _emit({"ok": True, "skipped": "no android_sandbox.json"})
        return 0
    info = load_android_info(out_dir)
    from cua import Sandbox

    try:
        await Sandbox.delete(info["name"], local=bool(info.get("local", True)))
    except Exception as exc:
        print(f"warning: Android Sandbox.delete: {exc}", file=sys.stderr)
    path.unlink(missing_ok=True)
    _emit({"ok": True, "deleted": info["name"]})
    return 0


def cmd_status(out_dir: Path) -> int:
    info = load_android_info(out_dir)
    _emit({"ok": True, "android": info})
    print(json.dumps(info, indent=2, ensure_ascii=False))
    return 0


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Mobile Cua sandbox control for Android APK runs")
    sub = p.add_subparsers(dest="command", required=True)

    boot = sub.add_parser("bootstrap", help="Create Android sandbox and write android_sandbox.json")
    boot.add_argument("out_dir", type=Path)
    boot.add_argument("--apk", type=Path, default=None)
    boot.add_argument("--name", default=None)
    boot.add_argument(
        "--install-with-image",
        action="store_true",
        help="Install APK through Image.from_registry(...).apk_install(apk_path) during create",
    )

    install = sub.add_parser(
        "install",
        help="Install APK with adb install fallback; APK path must be visible inside the sandbox",
    )
    install.add_argument("out_dir", type=Path)
    install.add_argument("apk", type=Path)

    shot = sub.add_parser("screenshot", help="Save Android screenshot")
    shot.add_argument("out_dir", type=Path)
    shot.add_argument("--out", type=Path, required=True)

    tap = sub.add_parser("tap", help="Tap x y")
    tap.add_argument("out_dir", type=Path)
    tap.add_argument("x", type=int)
    tap.add_argument("y", type=int)

    swipe = sub.add_parser("swipe", help="Swipe from x1 y1 to x2 y2")
    swipe.add_argument("out_dir", type=Path)
    swipe.add_argument("x1", type=int)
    swipe.add_argument("y1", type=int)
    swipe.add_argument("x2", type=int)
    swipe.add_argument("y2", type=int)
    swipe.add_argument("--duration-ms", type=int, default=400)

    type_p = sub.add_parser("type", help="Type text via sb.mobile.type_text")
    type_p.add_argument("out_dir", type=Path)
    type_p.add_argument("text")

    key = sub.add_parser("key", help="Android key: back/home/enter/recents or numeric keycode")
    key.add_argument("out_dir", type=Path)
    key.add_argument("key")

    shell = sub.add_parser("shell", help="Fallback shell command, e.g. adb shell input ...")
    shell.add_argument("out_dir", type=Path)
    shell.add_argument("-c", "--cmd", required=True)

    sub.add_parser("status", help="Print android_sandbox.json").add_argument("out_dir", type=Path)
    sub.add_parser("teardown", help="Delete Android sandbox").add_argument("out_dir", type=Path)
    return p


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if args.command == "bootstrap":
        return asyncio.run(
            cmd_bootstrap(
                args.out_dir,
                apk_path=args.apk,
                name=args.name,
                install_with_image=args.install_with_image,
            )
        )
    if args.command == "install":
        return asyncio.run(cmd_install(args.out_dir, args.apk))
    if args.command == "screenshot":
        return asyncio.run(cmd_screenshot(args.out_dir, args.out))
    if args.command == "tap":
        return asyncio.run(cmd_tap(args.out_dir, args.x, args.y))
    if args.command == "swipe":
        return asyncio.run(
            cmd_swipe(args.out_dir, args.x1, args.y1, args.x2, args.y2, args.duration_ms)
        )
    if args.command == "type":
        return asyncio.run(cmd_type(args.out_dir, args.text))
    if args.command == "key":
        return asyncio.run(cmd_key(args.out_dir, args.key))
    if args.command == "shell":
        return asyncio.run(cmd_shell(args.out_dir, args.cmd))
    if args.command == "status":
        return cmd_status(args.out_dir)
    if args.command == "teardown":
        return asyncio.run(cmd_teardown(args.out_dir))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
