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
    *,
    runtime: str = "host",
    sandbox_image: str | None = None,
    sandbox_local: bool = True,
    android_enabled: bool = False,
    sandbox_warnings: list[str] | None = None,
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
    )
    sandbox_rule = (
        "4. sandbox-local / sandbox-cloud runtime 下所有 shell/screenshot/click/type "
        "操作都必须在 Cua sandbox 内完成,禁止触碰 host GUI"
    )
    return f"""请使用 product-analyzer skill 完成产品分析。

**输入参数**(请把这些直接写进 metadata.json,不要修改值):
- 产品名:{product_name}
- 官网 URL:{url}
{dl_line}
- 输出目录(已建好,所有产物写到这里):{out_dir}
- 主机:{host_os}/{host_arch}
- runtime:{runtime}
{runtime_block}

**要求**:
1. 严格遵循 .claude/skills/product-analyzer/SKILL.md 中的 canonical loop(7 步固定顺序)
2. 全程用 TodoWrite 维护进度,7 个 todos,每步开始前 in_progress、完成后 completed
3. host runtime 下桌面端驱动一律走 cua-driver,严守 cua-driver SKILL 的 no-foreground 契约
{sandbox_rule}
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


def _sandbox_sdk_example(*, local: bool) -> str:
    local_flag = "True" if local else "False"
    android_local = "True" if local else "False"
    return f"""```python
import asyncio
import os
from cua import Sandbox, Image

async def main():
    # Linux 桌面优先用 Docker/XFCE 容器镜像,不要用默认 kind=vm 的 QEMU 路径
    async with Sandbox.ephemeral(Image.linux(kind="container"), local={local_flag}) as sb:
        result = await sb.shell.run("uname -s")
        png = await sb.screenshot()

    async with Sandbox.ephemeral(Image.android(), local={android_local}) as android:
        result = await android.shell.run("getprop ro.build.version.release")
        png = await android.screenshot()

asyncio.run(main())
```
云端模式:环境变量 `CUA_API_KEY` 已由 orchestrator 注入;也可 `import cua; cua.configure(api_key=os.environ["CUA_API_KEY"])`。"""


def _runtime_block(
    runtime: str,
    *,
    sandbox_image: str | None,
    sandbox_local: bool,
    android_enabled: bool,
    sandbox_warnings: list[str],
) -> str:
    if runtime not in ("sandbox-local", "sandbox-cloud"):
        return "- runtime 说明:host 模式,使用当前主机和 cua-driver。"

    label = "本地" if sandbox_local else "云端"
    warning_lines = "\n".join(f"  - {item}" for item in sandbox_warnings) or "  - 无"
    example = _sandbox_sdk_example(local=sandbox_local)
    return f"""- sandbox.image:{sandbox_image or "auto"}
- sandbox.local:{str(sandbox_local).lower()}
- android.enabled:{str(android_enabled).lower()}
- {label} sandbox 预检 warnings:
{warning_lines}

**{runtime} 运行约束**:
- 你必须在本任务内用 Cua Sandbox SDK 创建并管理独立{label}沙箱,不要操作 host GUI。
- 默认使用 ephemeral sandbox;任务结束前让 context manager 自动清理。
- `sandbox.image=auto` 时,优先按找到的桌面安装包选择 `Image.macos()` / `Image.windows()` / `Image.linux(kind="container")`,找不到桌面包则用 `Image.linux(kind="container")` 做网页分析。
- 若检测到官方 APK 且 `android.enabled=true`,额外创建 `Sandbox.ephemeral(Image.android(), local={str(sandbox_local).lower()})` 做 Android 体验。
- 参考代码:
{example}
"""
