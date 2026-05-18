"""组装喂给 ``claude --print`` 的初始 prompt。

两个变体:
- ``build_prompt``:全新任务,把所有输入参数明列、要求 7 步 canonical loop
- ``build_resume_prompt``:从历史 session 续跑,只交代输出目录和补充指令
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
) -> str:
    dl_line = (
        f"- 下载链接(预先给定):{download_url}"
        if download_url
        else "- 下载链接:未提供,需要从官网自行定位"
    )
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


def build_resume_prompt(out_dir: Path, supplement: str) -> str:
    """Prompt for the cmd_resume path: claude already has session history,
    just remind it of the output_dir + skill, then forward the user's
    supplemental instruction (or a generic 'continue' if blank)."""
    return f"""(从历史任务恢复)继续之前在 {out_dir} 上未完成的产品分析工作。

请检查现有产物(report.md / metadata.json / screenshots/)的进度,从断点处接着干。继续遵循 product-analyzer skill 的 canonical loop;TodoWrite 列表如果丢了就重建。

用户补充指令:
{supplement or '(无,请按原计划继续)'}
"""
