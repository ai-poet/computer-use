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
    ensure_cua_driver,
    ensure_cua_sdk,
)
from .prompts import build_prompt, build_resume_prompt
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


def cmd_new(args: argparse.Namespace) -> int:
    """Start a brand-new product analysis run."""
    product_name, url, download_url = collect_inputs(args)
    log(f"输入已确认:product_name={product_name!r}  url={url!r}  download_url={download_url!r}")

    out_dir = prepare_output_dir(product_name)
    log(f"输出目录: {out_dir}")
    meta = write_metadata_seed(out_dir, product_name, url, download_url)

    prompt = build_prompt(
        product_name, url, download_url, out_dir,
        meta["host_os"], meta["host_arch"],
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
    """Run a CSV/JSON queue with one local sandbox contract per product."""
    from .batch import run_batch

    assert args.batch is not None
    warnings = check_local_sandbox_prereqs(args.sandbox_image)
    for warning in warnings:
        err(f"[sandbox preflight] {warning}")

    result = run_batch(
        args.batch,
        args.max_workers,
        sandbox_image=args.sandbox_image,
        sandbox_warnings=warnings,
    )
    ok = result.total - len(result.failed)
    log(f"批量完成: total={result.total} ok={ok} failed={len(result.failed)}")
    for row in result.results:
        status = "OK" if row["rc"] == 0 else f"FAIL rc={row['rc']}"
        log(
            f"  [{status}] {row['product']} "
            f"sandbox={row.get('sandbox_image')} out={row.get('out_dir')} "
            f"log={row.get('log_file')}"
        )
        if row.get("error"):
            err(f"    error: {row['error']}")
    return 2 if result.failed else 0


def pick_action(args: argparse.Namespace) -> str:
    """Decide which subcommand to run.

    - Any positional arg given (orchestrator path) → 'new', skip the menu
    - Otherwise show the new/resume picker
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
    print("  q. 退出")
    while True:
        try:
            choice = input("选择 [1/2/q,默认 1]: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            return "quit"
        if choice in ("", "1", "n", "new"):
            return "new"
        if choice in ("2", "r", "resume"):
            return "resume"
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
            "  批量:    python3 scripts/analyze_product.py --batch queue.json --max-workers 2\n"
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
        help="CSV/JSON 队列路径。启用后每个产品使用独立本地 Cua sandbox。",
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=2,
        help="批量模式最大并发 sandbox 数。默认 2。",
    )
    parser.add_argument(
        "--sandbox-image",
        choices=("auto", "linux", "macos", "windows"),
        default="auto",
        help="批量模式桌面 sandbox 镜像。默认 auto。",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    log("预检:claude CLI")
    ensure_claude_cli()

    if args.batch is not None:
        if args.resume:
            err("--batch 与 --resume 不能同时使用")
            return 1
        log("预检:Cua Sandbox SDK")
        ensure_cua_sdk()
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
    return cmd_new(args)
