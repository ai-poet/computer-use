"""组装喂给 ``claude --print`` 的初始 prompt。

两个变体:
- ``build_prompt``:全新任务,把所有输入参数明列、要求 7 步 canonical loop
- ``build_resume_prompt``:从历史 session 续跑,只交代输出目录和补充指令

沙盒操作细则在 ``.claude/skills/product-analyzer/SKILL.md`` 的「Sandbox 运行合约」;
prompt 只传参数并指向该节,避免与 skill 重复维护两份规则。
"""

from __future__ import annotations

from pathlib import Path


def build_prompt(
    product_name: str,
    url: str,
    download_url: str | None,
    out_dir: Path,
    host_os: str,
    host_arch: str,
    *,
    runtime: str = "host",
    sandbox_image: str | None = None,
    sandbox_local: bool = True,
    android_enabled: bool = False,
    sandbox_warnings: list[str] | None = None,
    batch_parallel: bool = False,
) -> str:
    dl_line = (
        f"- 下载链接(预先给定):{download_url}"
        if download_url
        else "- 下载链接:未提供,需要从官网自行定位"
    )
    runtime_block = _runtime_block(
        runtime,
        sandbox_image=sandbox_image,
        sandbox_local=sandbox_local,
        android_enabled=android_enabled,
        sandbox_warnings=sandbox_warnings or [],
        batch_parallel=batch_parallel,
    )

    if runtime in ("sandbox-local", "sandbox-cloud"):
        ctl_hint = (
            "scripts/sandbox_ctl.py bootstrap/step/teardown"
            if runtime == "sandbox-local"
            else "Cua MCP(computer_*) 或 sandbox_ctl"
        )
        host_rule = (
            "3. 沙盒 runtime — 遵守 SKILL「沙盒控制三阶段」(bootstrap → step loop → teardown);"
            f"控制面:{ctl_hint};Linux cua-xfce 仅 Firefox(bootstrap 会起,勿 chromium);"
            "**禁止 monolithic analysis script**"
        )
        sandbox_rule = (
            "4. 操作系统级操作只在沙盒内;host 仅写 `<output_dir>`;"
            "每步 GUI 后截图到 screenshots/ 并读图再决策"
        )
    else:
        host_rule = (
            "3. **host 单任务 — 禁止沙盒**:不得 import cua / Sandbox.ephemeral / Docker;"
            "只读 SKILL「Host 单任务」;桌面与浏览器走 cua-driver(no-foreground)"
        )
        sandbox_rule = (
            "4. 勿读「Sandbox 运行合约」;该节仅用于批量"
        )

    return f"""请使用 product-analyzer skill 完成产品分析。

**输入参数**(请把这些直接写进 metadata.json,不要修改值):
- 产品名:{product_name}
- 官网 URL:{url}
{dl_line}
- 输出目录(已建好,所有产物写到这里):{out_dir}
- 主机(编排器侧,仅作记录):{host_os}/{host_arch}
{runtime_block}

**要求**:
1. 严格遵循 SKILL.md 的 canonical loop(7 步固定顺序)
2. 全程用 TodoWrite 维护进度,7 个 todos,每步开始前 in_progress、完成后 completed
{host_rule}
{sandbox_rule}
5. 结束前在 metadata.json 里补齐 finished_at / mode / screenshots[] / warnings[]

现在开始执行。
"""


def build_resume_prompt(out_dir: Path, supplement: str) -> str:
    """Prompt for the cmd_resume path: claude already has session history,
    just remind it of the output_dir + skill, then forward the user's
    supplemental instruction (or a generic 'continue' if blank)."""
    sandbox_json = out_dir / "sandbox.json"
    sandbox_hint = ""
    if sandbox_json.is_file():
        sandbox_hint = (
            f"\n- 已存在 {sandbox_json}:先 `python scripts/sandbox_ctl.py status {out_dir}`,"
            "勿重复 bootstrap;从 step loop 断点续跑;结束后 teardown。\n"
        )
    return f"""(从历史任务恢复)继续之前在 {out_dir} 上未完成的产品分析工作。

请检查现有产物(report.md / metadata.json / screenshots/)的进度,从断点处接着干。继续遵循 product-analyzer skill 的 canonical loop;TodoWrite 列表如果丢了就重建。若为 sandbox runtime,继续遵守 SKILL「沙盒控制三阶段」。
{sandbox_hint}
用户补充指令:
{supplement or '(无,请按原计划继续)'}
"""


def _runtime_block(
    runtime: str,
    *,
    sandbox_image: str | None,
    sandbox_local: bool,
    android_enabled: bool,
    sandbox_warnings: list[str],
    batch_parallel: bool = False,
) -> str:
    if runtime not in ("sandbox-local", "sandbox-cloud"):
        return (
            f"- runtime:{runtime}\n"
            "- 路径:host 单任务(非批量、非沙盒)\n"
            "- 驱动:cua-driver + 父 shell curl;**禁止** Cua Sandbox / Docker\n"
            "- 细则:SKILL.md「Host 单任务」"
        )

    warning_lines = "\n".join(f"  - {item}" for item in sandbox_warnings) or "  - 无"
    if android_enabled:
        android_rule = (
            "- **Android**:enabled — 仅在 Android 沙盒成功启动且找到 APK 时走 APK 路径;"
            "若沙盒起不来或安装失败,设 android.mode=skipped/failed,**改只操作 Firefox 网页**"
            "从官网获取产品信息(勿强行 adb/QEMU)"
        )
    else:
        android_rule = (
            "- **Android**:disabled — **禁止**创建 Android 沙盒、adb、QEMU APK 安装。"
            "**只**在 Linux 沙盒 Firefox 内浏览官网,从网页获取产品信息与截图;"
            "可记录 Play 链接到 warnings,设 metadata.android.mode=skipped"
        )
    local_ctl = (
        "- **本地控制(鼠标优先)**:"
        "`bootstrap <out_dir> --open-browser --url <官网>` → "
        "循环 `step screenshot` / `click` / `scroll` / `type` / `key`;"
        "`step shell` 仅用于 wget 安装包或 dpkg,禁止 curl 抓官网;"
        "结束 `teardown`"
        if runtime == "sandbox-local"
        else (
            "- **云端控制(鼠标优先)**:MCP `computer_screenshot`/`computer_click`/`computer_scroll`/…;"
            "少用 `computer_shell`;禁止 host GUI"
        )
    )
    return f"""- runtime:{runtime}
- sandbox.image:{sandbox_image or "auto"}
- sandbox.local:{str(sandbox_local).lower()}
- android.enabled:{str(android_enabled).lower()}
- batch.parallel:{str(batch_parallel).lower()}
{android_rule}
- sandbox 预检 warnings(非致命):
{warning_lines}
{local_ctl}
- **沙盒操作**:必读 SKILL「Sandbox 运行合约」与「沙盒控制三阶段」;禁止整段 asyncio 分析脚本。
"""
