"""命令行入口:argparse、子命令调度、新任务/恢复任务两条路径。

只有 ``main`` 是公共函数;其它都是私有 helper。``main`` 由
``scripts/analyze_product.py`` 这层 5 行 shim 调用。
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .claude_driver import run_claude
from .config import BOLD, DIM, RESET
from .preflight import (
    check_local_sandbox_prereqs,
    ensure_claude_cli,
    ensure_cua_api_key,
    ensure_cua_cli,
    ensure_cua_driver,
    ensure_cua_sdk,
)
from .prompts import build_prompt, build_resume_prompt
from .sandbox_runtime import (
    build_sandbox_context,
    resolve_api_key,
    resolve_sandbox_mode,
)
from .tasks import (
    pick_resume_target,
    post_check,
    prepare_output_dir,
    write_metadata_seed,
)
from .ui import err, log, prompt_str


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


def _prompt_api_key_if_needed(mode: str, api_key: str | None) -> str | None:
    if mode != "cloud":
        return None
    if api_key:
        return api_key
    from os import environ

    env_key = environ.get("CUA_API_KEY", "").strip()
    if env_key:
        return env_key
    key = prompt_str(
        "CUA API Key(也可事先 export CUA_API_KEY): ",
        validate=lambda s: len(s.strip()) > 0,
    )
    return key.strip()


def resolve_android_enabled(args: argparse.Namespace) -> bool:
    """Android APK path is opt-in unless sandbox-image is auto."""
    if getattr(args, "android", False):
        return True
    if getattr(args, "no_android", False):
        return False
    return args.sandbox_image == "auto"


def prepare_batch_context(args: argparse.Namespace):
    """Resolve sandbox mode, preflight, and return (SandboxContext, warnings)."""
    interactive = sys.stdin.isatty() and args.sandbox is None
    api_key = resolve_api_key(args.cua_api_key)
    android_enabled = resolve_android_enabled(args)
    mode = resolve_sandbox_mode(
        cli_sandbox=args.sandbox,
        interactive=interactive,
    )
    if mode == "cloud":
        api_key = ensure_cua_api_key(api_key)
        log(f"批量模式:云端 Cua sandbox (image={args.sandbox_image})")
        warnings: list[str] = []
    else:
        api_key = None
        log(f"批量模式:本地 Cua sandbox (image={args.sandbox_image})")
        warnings = check_local_sandbox_prereqs(
            args.sandbox_image,
            android_enabled=android_enabled,
        )
        for warning in warnings:
            err(f"[sandbox preflight] {warning}")

    ctx = build_sandbox_context(
        args.sandbox_image,
        mode=mode,
        android_enabled=android_enabled,
        api_key=api_key,
    )
    return ctx, warnings


def collect_batch_args() -> argparse.Namespace:
    """Interactive prompts for menu option 3 (batch)."""
    scope_raw = prompt_str(
        "队列 [文件路径 / all=全部 queue*.json, 默认 all]: ",
        validate=lambda s: s == "" or len(s.strip()) > 0,
        allow_empty=True,
    ).strip().lower()
    batch_all = scope_raw in ("", "all", "*")
    queue_path: Path | None = None
    queue_root: Path | None = None
    if not batch_all:
        queue_path = Path(scope_raw).expanduser()
        if not queue_path.exists():
            raise FileNotFoundError(queue_path)
        if queue_path.suffix.lower() not in (".csv", ".json"):
            raise ValueError("队列文件必须是 .csv 或 .json")

    workers_raw = prompt_str(
        "最大并发数 [默认 2]: ",
        validate=lambda s: s == "" or s.isdigit(),
        allow_empty=True,
    )
    max_workers = int(workers_raw) if workers_raw.strip() else 2

    image_raw = prompt_str(
        "Sandbox 镜像 [auto/linux/macos/windows, 默认 auto]: ",
        validate=lambda s: s in ("", "auto", "linux", "macos", "windows"),
        allow_empty=True,
    )
    sandbox_image = image_raw.strip() or "auto"

    mode = resolve_sandbox_mode(cli_sandbox=None, interactive=True)
    api_key: str | None = None
    if mode == "cloud":
        api_key = _prompt_api_key_if_needed("cloud", resolve_api_key(None))
        if api_key:
            ensure_cua_api_key(api_key)

    return argparse.Namespace(
        batch=queue_path,
        batch_all=batch_all,
        batch_dir=queue_root,
        max_workers=max_workers,
        sandbox_image=sandbox_image,
        sandbox="cloud" if mode == "cloud" else "local",
        cua_api_key=api_key if mode == "cloud" else None,
        product_name=None,
        url=None,
        download_url=None,
        resume=False,
    )


def cmd_new(args: argparse.Namespace) -> int:
    """Start a brand-new product analysis run."""
    product_name, url, download_url = collect_inputs(args)
    log(f"输入已确认:product_name={product_name!r}  url={url!r}  download_url={download_url!r}")

    out_dir = prepare_output_dir(product_name)
    log(f"输出目录: {out_dir}")
    meta = write_metadata_seed(
        out_dir,
        product_name,
        url,
        download_url,
        runtime="host",
        sandbox_image=None,
        sandbox_local=True,
        sandbox_mode="local",
        android_enabled=False,
    )

    prompt = build_prompt(
        product_name, url, download_url, out_dir,
        meta["host_os"], meta["host_arch"],
        runtime="host",
        batch_parallel=False,
    )
    rc = run_claude(prompt, out_dir=out_dir)
    log(f"claude 子进程退出码: {rc}")
    post_check(out_dir)
    if rc != 0:
        err("claude 子进程非零退出,请翻阅上方事件流定位问题")
        return 2
    return 0


def cmd_resume() -> int:
    """List past runs, let the user pick one, ask for a supplemental prompt,
    and resume via ``--resume <session_id>``."""
    target = pick_resume_target()
    if target is None:
        return 0  # user backed out, not an error
    meta = target["meta"]
    out_dir = target["dir"]
    sid = meta.get("last_session_id")

    if target["status"] == "stale" or not sid:
        err(f"任务 {out_dir} 没有 last_session_id,无法 --resume(可能 claude 之前从未真正启动)。")
        err("可以删掉 reports/ 下这个目录后重新跑新任务。")
        return 1

    print(f"\n{BOLD}恢复任务:{RESET} {meta.get('product_name', '?')}")
    print(f"  {DIM}目录:{out_dir}{RESET}")
    print(f"  {DIM}session_id:{sid}{RESET}")
    print(f"  {DIM}状态:{target['status']}{RESET}\n")

    print(f"{DIM}输入要给 claude 的补充指令(回车空行 = 让它按原计划继续)。多行用反斜杠续行。{RESET}")
    sup_lines: list[str] = []
    try:
        while True:
            try:
                line = input("补充> " if not sup_lines else "      ")
            except EOFError:
                break
            if line.endswith("\\"):
                sup_lines.append(line[:-1])
                continue
            sup_lines.append(line)
            break
    except KeyboardInterrupt:
        err("用户中断")
        return 130
    supplement = "\n".join(sup_lines).strip()

    prompt = build_resume_prompt(out_dir, supplement)
    log(f"以 session_id={sid} 续跑…")
    rc = run_claude(prompt, resume_id=sid, out_dir=out_dir)
    log(f"claude 子进程退出码: {rc}")
    post_check(out_dir)
    if rc != 0:
        err("claude 子进程非零退出,请翻阅上方事件流定位问题")
        return 2
    return 0


def cmd_batch(args: argparse.Namespace) -> int:
    """Run a CSV/JSON queue with one sandbox (local or cloud) per product."""
    import os

    from .batch import resolve_batch_rows, run_batch

    batch_all = getattr(args, "batch_all", False)
    if args.batch is None and not batch_all:
        err("请指定 --batch 或 --batch-all")
        return 1
    sandbox_ctx, warnings = prepare_batch_context(args)
    plain = getattr(args, "batch_plain", False) or os.environ.get(
        "ANALYZE_BATCH_PLAIN", ""
    ).strip() in ("1", "true", "yes")

    rows, queue_name, paths = resolve_batch_rows(
        queue_path=args.batch,
        batch_all=batch_all,
        queue_root=getattr(args, "batch_dir", None),
    )
    if not plain:
        if batch_all:
            file_list = ", ".join(p.name for p in paths)
            log(
                f"批量(全量): {len(paths)} 个队列 · {file_list} · "
                f"共 {len(rows)} 条 · 并发 {args.max_workers} · "
                f"sandbox={sandbox_ctx.mode}/{sandbox_ctx.image}"
            )
        else:
            log(
                f"批量: {queue_name} · 共 {len(rows)} 条 · "
                f"并发 {args.max_workers} · sandbox={sandbox_ctx.mode}/{sandbox_ctx.image}"
            )
        log("进入批量控制台(↑/↓ 列表 · Enter 详情 · q 退出); "
            "纯文本模式请加 --batch-plain")

    try:
        result = run_batch(
            args.max_workers,
            sandbox_ctx=sandbox_ctx,
            queue_path=args.batch,
            batch_all=batch_all,
            queue_root=getattr(args, "batch_dir", None),
            sandbox_warnings=warnings,
            plain=plain,
        )
    except KeyboardInterrupt:
        err("用户中断批量任务")
        return 130
    ok = result.total - len(result.failed)
    log(f"批量完成: total={result.total} ok={ok} failed={len(result.failed)}")
    for row in result.results:
        status = "OK" if row["rc"] == 0 else f"FAIL rc={row['rc']}"
        log(
            f"  [{status}] {row['product']} "
            f"sandbox={row.get('sandbox_mode')}/{row.get('sandbox_image')} "
            f"out={row.get('out_dir')} log={row.get('log_file')}"
        )
        if row.get("error"):
            err(f"    error: {row['error']}")
    return 2 if result.failed else 0


def pick_action(args: argparse.Namespace) -> str:
    """Decide which subcommand to run.

    - Any positional arg given (orchestrator path) → 'new', skip the menu
    - Otherwise show the new/resume/batch picker
    - If stdin isn't a tty (CI / pipe) and no args → default to 'new' so
      the existing input() prompts kick in
    """
    if args.product_name or args.url or args.download_url:
        return "new"
    if not sys.stdin.isatty():
        return "new"

    print(f"\n{BOLD}产品分析自动化{RESET}")
    print("  1. 新任务(start a new run)")
    print("  2. 恢复历史任务(resume from reports/)")
    print("  3. 批量分析(batch,本地/云端 sandbox)")
    print("  q. 退出")
    while True:
        try:
            choice = input("选择 [1/2/3/q,默认 1]: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            return "quit"
        if choice in ("", "1", "n", "new"):
            return "new"
        if choice in ("2", "r", "resume"):
            return "resume"
        if choice in ("3", "b", "batch"):
            return "batch"
        if choice in ("q", "quit", "exit"):
            return "quit"
        print("  无效输入,请重试")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="analyze_product",
        description="产品分析自动化入口。零参数进入交互菜单(新任务/恢复历史);带位置参数直接走新任务路径。",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "示例:\n"
            "  交互式:  python3 scripts/analyze_product.py            # 弹菜单选 新任务/恢复\n"
            '  新任务:  python3 scripts/analyze_product.py "ProductiveKitty" '
            '"https://productivekitty.masterwordai.com"\n'
            "  全参:    python3 scripts/analyze_product.py NAME URL DOWNLOAD_URL\n"
            "  恢复:    在零参数模式选 2,或直接 --resume\n"
            "  批量(默认本地): python3 scripts/analyze_product.py --batch queue.json "
            "--max-workers 10 --sandbox-image linux\n"
            "  批量全量:    python3 scripts/analyze_product.py --batch-all "
            "--max-workers 5 --sandbox-image linux\n"
            "  批量纯文本: python3 scripts/analyze_product.py --batch queue.json "
            "--batch-plain\n"
            "  批量云端: python3 scripts/analyze_product.py --batch queue.json "
            "--sandbox cloud --cua-api-key sk-...\n"
        ),
    )
    parser.add_argument(
        "product_name", nargs="?", default=None,
        help="产品名(展示用原文)。省略则交互输入。",
    )
    parser.add_argument(
        "url", nargs="?", default=None,
        help="产品官网 URL。省略则交互输入。",
    )
    parser.add_argument(
        "download_url", nargs="?", default=None,
        help="可选:直接指向当前主机能用的安装包。给空字符串视为未提供。",
    )
    parser.add_argument(
        "--resume", action="store_true",
        help='跳过菜单,直接进入"恢复历史任务"流程。',
    )
    parser.add_argument(
        "--batch",
        type=Path,
        default=None,
        help="CSV/JSON 队列路径。与 --batch-all 二选一。",
    )
    parser.add_argument(
        "--batch-all",
        action="store_true",
        help="自动合并仓库根目录下全部 queue*.json 队列(无需手动合并 JSON)。",
    )
    parser.add_argument(
        "--batch-dir",
        type=Path,
        default=None,
        help="--batch-all 时扫描队列文件的目录。默认仓库根目录。",
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=2,
        help="批量模式最大并发 sandbox 数。默认 2。超出部分排队等待。",
    )
    parser.add_argument(
        "--batch-plain",
        action="store_true",
        help="批量模式禁用 curses 控制台,使用前缀行日志(适合 CI/管道)。",
    )
    parser.add_argument(
        "--sandbox-image",
        choices=("auto", "linux", "macos", "windows"),
        default="auto",
        help="批量模式桌面 sandbox 镜像。默认 auto。",
    )
    parser.add_argument(
        "--sandbox",
        choices=("local", "cloud"),
        default=None,
        help="批量 sandbox 运行环境。默认 local;仅 --sandbox cloud 时走 Cua Cloud。",
    )
    parser.add_argument(
        "--cua-api-key",
        default=None,
        help="Cua Cloud API Key(仅 --sandbox cloud 时需要)。也可 export CUA_API_KEY。",
    )
    parser.add_argument(
        "--android",
        action="store_true",
        help="批量时启用 Android APK 分析路径(需 adb/QEMU 或 cua-qemu-android 镜像)。",
    )
    parser.add_argument(
        "--no-android",
        action="store_true",
        help="批量时禁用 Android 路径(默认 --sandbox-image linux 时已禁用)。",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    log("预检:claude CLI")
    ensure_claude_cli()

    if args.batch is not None or args.batch_all:
        if args.resume:
            err("--batch/--batch-all 与 --resume 不能同时使用")
            return 1
        if args.batch is not None and args.batch_all:
            err("--batch 与 --batch-all 不能同时使用")
            return 1
        log("预检:Cua Sandbox SDK")
        ensure_cua_sdk()
        log("预检:cua CLI")
        ensure_cua_cli()
        return cmd_batch(args)

    log("预检:cua-driver")
    ensure_cua_driver()

    if args.resume:
        return cmd_resume()

    action = pick_action(args)
    if action == "quit":
        log("退出")
        return 0
    if action == "resume":
        return cmd_resume()
    if action == "batch":
        log("预检:Cua Sandbox SDK")
        ensure_cua_sdk()
        log("预检:cua CLI")
        ensure_cua_cli()
        try:
            batch_args = collect_batch_args()
        except (FileNotFoundError, ValueError) as exc:
            err(str(exc))
            return 1
        except KeyboardInterrupt:
            err("用户中断")
            return 130
        return cmd_batch(batch_args)
    return cmd_new(args)
