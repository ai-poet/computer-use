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
        host_rule = (
            "3. 沙盒 runtime — 遵守 SKILL.md「Sandbox 运行合约」;"
            "禁止使用 cua-driver 或 host GUI"
        )
        sandbox_rule = (
            "4. 操作系统级操作(浏览/下载/安装/点击/截图)只在沙盒内;"
            "host 仅写 `<output_dir>` 产物"
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
    return f"""(从历史任务恢复)继续之前在 {out_dir} 上未完成的产品分析工作。

请检查现有产物(report.md / metadata.json / screenshots/)的进度,从断点处接着干。继续遵循 product-analyzer skill 的 canonical loop;TodoWrite 列表如果丢了就重建。若为 sandbox runtime,继续遵守 SKILL.md「Sandbox 运行合约」。

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
    return f"""- runtime:{runtime}
- sandbox.image:{sandbox_image or "auto"}
- sandbox.local:{str(sandbox_local).lower()}
- android.enabled:{str(android_enabled).lower()}
- batch.parallel:{str(batch_parallel).lower()}
- sandbox 预检 warnings(非致命):
{warning_lines}
- **沙盒操作**:必读 SKILL.md「Sandbox 运行合约」(Host Python/conda、镜像选择、SDK 示例、批量并行、禁止 host GUI);prompt 不再重复这些规则。
"""
