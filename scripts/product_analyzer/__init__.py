"""产品分析自动化工具包。

模块依赖方向(自下而上,无环):

    config       路径常量 + ANSI 配色 + USE_COLOR 开关
    ui           log/err/prompt_str/Spinner — 终端 I/O
    renderer     format_event 全家 — stream-json → 美化输出
    preflight    detect_host/ensure_claude_cli/ensure_cua_driver
    tasks        slugify / metadata I/O / list_tasks / pick_resume_target
    sandbox_runtime  batch 本地 Cua sandbox 运行上下文
    sandbox_ctl  bootstrap/step/teardown 逐步控制桥
    prompts      build_prompt / build_resume_prompt
    claude_driver  ESC watcher + spawn + run_claude(对外唯一编排接口)
    batch        CSV/JSON 队列 + 并发 worker 调度
    cli          collect_inputs / cmd_new / cmd_resume / cmd_batch / pick_action / main

外部入口只有 ``cli.main``,由 ``scripts/analyze_product.py`` 这层 shim 调用。
"""

from .cli import main  # noqa: F401

__all__ = ["main"]
