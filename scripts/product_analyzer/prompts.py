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
    batch_banner = ""
    if batch_parallel and runtime in ("sandbox-local", "sandbox-cloud"):
        batch_banner = _batch_sandbox_banner(out_dir, runtime)

    if runtime in ("sandbox-local", "sandbox-cloud"):
        host_rule = (
            "3. 本任务是沙盒 runtime — **禁止**使用 cua-driver 或任何 host GUI/浏览器;"
            "见下方沙盒约束"
        )
        sandbox_rule = (
            "4. **全部** shell / 下载 / 安装 / 浏览器 / 鼠标 / 键盘 / 截图操作"
            "只能在 Cua sandbox 操作系统内完成;host 仅用于写报告到输出目录"
        )
    else:
        host_rule = (
            "3. host runtime 下桌面端驱动一律走 cua-driver,"
            "严守 cua-driver SKILL 的 no-foreground 契约"
        )
        sandbox_rule = ""

    return f"""请使用 product-analyzer skill 完成产品分析。
{batch_banner}
**输入参数**(请把这些直接写进 metadata.json,不要修改值):
- 产品名:{product_name}
- 官网 URL:{url}
{dl_line}
- 输出目录(已建好,所有产物写到这里):{out_dir}
- 主机(编排器侧,仅作记录):{host_os}/{host_arch}
- runtime:{runtime}
{runtime_block}

**要求**:
1. 严格遵循 .claude/skills/product-analyzer/SKILL.md 中的 canonical loop(7 步固定顺序)
2. 全程用 TodoWrite 维护进度,7 个 todos,每步开始前 in_progress、完成后 completed
{host_rule}
{sandbox_rule}
5. 结束前在 metadata.json 里补齐 finished_at / mode / screenshots[] / warnings[]

现在开始执行。
"""


def _batch_sandbox_banner(out_dir: Path, runtime: str) -> str:
    env_label = "本地 Docker 沙盒" if runtime == "sandbox-local" else "Cua Cloud 沙盒"
    return f"""
**批量并行 worker — 必须在{env_label}内完成全部操作系统级工作(最高优先级)**:
- 你是批量队列中的**独立** Claude worker;与其它产品并行,互不共享 sandbox。
- 编排器已在 host 创建 `{out_dir}`,但**除读写该目录下的 report/metadata/screenshots/downloads 外,不得把 host 当作分析环境**。
- 第一步:用 Cua Sandbox SDK 创建本产品的 ephemeral sandbox;之后**所有**操作只在沙盒 OS 内执行。
- 必须在沙盒内完成的事项(不可放到 host):打开/浏览官网,curl/wget 抓 HTML,定位下载链接,下载并安装桌面包,启动应用,鼠标点击与滚动,键盘输入,`await sb.screenshot()` 截图,Android APK 路径(若启用)。
- **严禁**在 host 上:cua-driver、`open`/`osascript` 激活应用、本机浏览器、本机桌面 GUI、任何改变用户前台窗口的操作。
- 不要用「host 能跑 curl 就走父 shell」的捷径 — 批量模式下官网与 GUI 证据必须来自沙盒。

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
    from .sandbox_runtime import LINUX_CONTAINER_IMAGE, LINUX_DOCKER_PLATFORM

    local_flag = "True" if local else "False"
    android_local = "True" if local else "False"
    runtime_line = (
        f'        runtime=DockerRuntime(ephemeral=True, platform="{LINUX_DOCKER_PLATFORM}"),\n'
        if local
        else ""
    )
    return f"""```python
import asyncio
from dataclasses import replace
from cua import Image, Sandbox
from cua_sandbox.runtime.docker import DockerRuntime

LINUX_IMAGE = "{LINUX_CONTAINER_IMAGE}"

async def main():
    img = replace(Image.linux(kind="container"), _registry=LINUX_IMAGE)
    async with Sandbox.ephemeral(
        img,
        local={local_flag},
{runtime_line}    ) as sb:
        result = await sb.shell.run("uname -s")
        png = await sb.screenshot()

    async with Sandbox.ephemeral(Image.android(), local={android_local}) as android:
        result = await android.shell.run("getprop ro.build.version.release")
        png = await android.screenshot()

asyncio.run(main())
```
本地 Linux 需 `linux/amd64` 平台(Apple Silicon 上尤其重要)。云端模式:`CUA_API_KEY` 已由 orchestrator 注入。"""


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
        return "- runtime 说明:host 模式,使用当前主机和 cua-driver。"

    label = "本地" if sandbox_local else "云端"
    warning_lines = "\n".join(f"  - {item}" for item in sandbox_warnings) or "  - 无"
    example = _sandbox_sdk_example(local=sandbox_local)
    batch_note = ""
    if batch_parallel:
        batch_note = (
            "- **批量并行**:与其它产品 worker 同时运行;每个产品独占一个 sandbox 生命周期,"
            "禁止复用其它 `reports/` 任务或 host 环境。\n"
        )
    return f"""- sandbox.image:{sandbox_image or "auto"}
- sandbox.local:{str(sandbox_local).lower()}
- android.enabled:{str(android_enabled).lower()}
- batch.parallel:{str(batch_parallel).lower()}
- {label} sandbox 预检 warnings:
{warning_lines}

**{runtime} 运行约束**:
- 你必须在本任务内用 Cua Sandbox SDK 创建并管理独立{label}沙箱;**全部操作系统级操作在沙盒内完成**,不要操作 host GUI。
{batch_note}- 默认使用 ephemeral sandbox;任务结束前让 context manager 自动清理。
- `sandbox.image=auto` 时,优先按找到的桌面安装包选择 `Image.macos()` / `Image.windows()` / `Image.linux(kind="container")`,找不到桌面包则用 `Image.linux(kind="container")` 做网页分析。
- 若检测到官方 APK 且 `android.enabled=true`,额外创建 `Sandbox.ephemeral(Image.android(), local={str(sandbox_local).lower()})` 做 Android 体验。
- 参考代码:
{example}
"""
