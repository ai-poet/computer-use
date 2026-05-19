# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 这个仓库是什么

把"分析一款新产品"做成一条可重复流水线:Python 脚本(`scripts/analyze_product.py`)把产品名 + 官网 URL 喂进 `claude --print --output-format stream-json` 子进程,让 Claude Code 走 `product-analyzer` skill 完成抓取/驱动桌面端/截图/写报告,产出 `reports/<slug>-YYYY-MM-DD[-N]/{report.md, metadata.json, screenshots/}`。

**核心设计原则:改规则不改代码。**所有"分析什么、产出什么、怎么降级"的判断都在 `.claude/skills/product-analyzer/SKILL.md`(及 `REPORT_TEMPLATE.md`)里;Python 只做预检、建目录、起子进程、流式渲染、ESC 续跑。改报告章节、截图命名、降级条件,**改 skill,不要改 Python**。

## 常用命令

```bash
# 装桌面驱动器(macOS=Swift cua-driver, Linux/Windows=cua-driver-rs;首跑会自动调起)
python3 scripts/install_cua_driver.py

# 跑一次完整分析
python3 scripts/analyze_product.py "ProductiveKitty" "https://productivekitty.masterwordai.com"

# 全参(给定 download_url 跳过"在官网找下载链接"那步)
python3 scripts/analyze_product.py NAME URL DOWNLOAD_URL

# 零参数 → 进交互菜单(新任务 / 恢复历史 / 退出)
python3 scripts/analyze_product.py

# 直接进恢复流程
python3 scripts/analyze_product.py --resume

# 批量:默认本地 sandbox;仅 --sandbox cloud 时走云端
python3 scripts/analyze_product.py --batch queue.json --max-workers 2 --sandbox-image auto
python3 scripts/analyze_product.py --batch queue.json --sandbox cloud --cua-api-key sk-...

# 调试:把 stream-json 同时落盘
ANALYZE_RAW_LOG=/tmp/raw.jsonl python3 scripts/analyze_product.py NAME URL
```

仓库里没有 lint / test / build 配置 — 这是脚本仓,Python 模块手工跑就是验证。改完代码后跑一次 `python3 scripts/analyze_product.py --help` 确保 import 链不破即可。

## 架构(big picture)

### 两层分工

```
scripts/analyze_product.py        # 5 行 shim,只调 product_analyzer.main
scripts/product_analyzer/         # Python 实现包(预检/建目录/起子进程/流式渲染)
.claude/skills/product-analyzer/  # 业务规则(SKILL.md + REPORT_TEMPLATE.md)
.claude/skills/cua-driver/        # 桌面自动化规则(snapshot→act→verify、no-foreground 契约)
```

`scripts/product_analyzer/__init__.py` 顶部的 docstring 是模块依赖图的权威来源。依赖**单向无环**,改动时务必保持:

```
    config → ui → renderer → preflight → tasks → sandbox_runtime → prompts → claude_driver → batch → cli
```

每个模块的职责一句话:

- `config.py` — 路径常量(`REPORTS_DIR`、各 cua-driver bundle path)+ ANSI 配色 + `USE_COLOR` 开关。
- `ui.py` — `log` / `err` / `prompt_str` / `Spinner`(底部自擦除式 loading,只在 tty 启用)。
- `renderer.py` — `format_event(line, state)`:把 stream-json 单行 JSON 翻译成 Claude Code 风格的彩色终端输出(thinking / tool_use / tool_result / TodoWrite 列表 / result)。**不直接 print,把行返回给上层**,让 Spinner 控制擦除/重画时机。
- `preflight.py` — `detect_host()` 归一化 OS+arch;`ensure_claude_cli` 检查 `which claude`;`ensure_cua_driver` 缺则自动调 `install_cua_driver.py`;`ensure_cua_sdk` / `check_local_sandbox_prereqs` 支撑本地 sandbox batch。
- `tasks.py` — `slugify`(ASCII-fold + kebab,纯中文走 `product-<md5前6>` 兜底)、`prepare_output_dir`(同日重跑加 `-2` 后缀,从不覆盖)、`metadata.json` 读/写/合并、`list_tasks`(扫 `reports/` 标 finished/in_progress/stale)、`pick_resume_target`、`post_check`。
- `sandbox_runtime.py` — batch 模式的 Cua sandbox 上下文(本地/云端、`sandbox.image`、`CUA_API_KEY`/`NO_PROXY` env),只生成合约和 env,不替 Claude 直接操作 sandbox。
- `prompts.py` — `build_prompt`(全新任务,7 步 canonical loop,可带 sandbox runtime 合约)和 `build_resume_prompt`(从 session 续跑)。
- `claude_driver.py` — **唯一的子进程编排入口** `run_claude(prompt, resume_id, out_dir)`:spawn → ESC 监听线程 → 主循环按行读 stdout → 调 renderer 美化 → 抓到 `session_id` 立即落盘到 metadata(用于断点恢复)→ ESC 触发则停子进程、收集补充指令、`--resume` 重启。batch 模式用 `non_interactive` + `log_file` 写每任务 `run.log`。
- `batch.py` — 读取 CSV/JSON 队列,用 `asyncio.Semaphore(max_workers)` 控制 sandbox worker 并发,每个产品独立 output_dir / metadata / Claude 子进程。
- `cli.py` — argparse、`pick_action` 菜单、`cmd_new` / `cmd_resume` / `cmd_batch`、`main`(对外唯一入口)。

### 子进程协议

`claude_driver._spawn_claude` 起的命令固定是:

```
claude --print --output-format stream-json --verbose
       --input-format text --permission-mode bypassPermissions
       [--resume <session_id>]
```

- `bypassPermissions` 让工具调用不打断流程。要交互式确认就改这一行。
- prompt 通过 stdin 一次性写入再 close。
- stdout 是逐行 stream-json,`renderer.format_event` 解析。`system.subtype=init` 事件里的 `session_id` 抓住后**立刻**通过 `update_metadata(out_dir, last_session_id=...)` 写盘,这样即使 claude 中途被 kill 也能 `--resume`。

### ESC 暂停 + 续跑

`_esc_watcher_unix` 后台线程在 cbreak 模式下 `select` stdin,读到 `\x1b` 设 `flag['esc']=True`。主循环每读完一行就检查 flag,触发就 `proc.terminate()`,然后 `_read_supplement()` 收集多行补充指令(反斜杠续行),再以 `--resume <session_id>` + 新 prompt 重起。整段只在 `sys.stdin.isatty()` 时启用,管道 / CI 自动禁用。

### 任务状态机

`reports/<slug>-YYYY-MM-DD[-N]/metadata.json` 是唯一的真相源。`list_tasks()` 读它判 status:

- `finished` — `finished_at` 已设 **且** `report.md` ≥ 200 字节
- `in_progress` — 有 `last_session_id` 但 `finished_at` 空(可 `--resume`)
- `stale` — 连 `last_session_id` 都没有(claude 没真正起跑过)— 不能恢复,提示删目录重跑

### Skill 调用链

`build_prompt` 的内容**显式**告诉 claude "请使用 product-analyzer skill 完成产品分析",并把 `output_dir`、主机信息、产品名/URL 列出来。Claude 读 `.claude/skills/product-analyzer/SKILL.md` 进入 7 步 canonical loop,在 step 3-5 通过 `cua-driver` skill 操作浏览器/桌面应用。两个 skill 的分工:**product-analyzer 决定"分析什么、产出什么";cua-driver 决定"如何不抢焦点地驱动桌面"**。

## 写代码 / 改 skill 时必须遵守的契约

### 改 Python:保依赖单向

- 改任意模块前,先看它在 `__init__.py` 依赖图的位置,**不要让下层 import 上层**(比如 `tasks.py` 不能 import `claude_driver`)。
- 新增"原子能力"先想是不是该塞进 `ui.py` 或 `tasks.py`,而不是再起一层。
- `claude_driver.run_claude` 是唯一对外的子进程编排接口,`cli` 之外不要直接 `subprocess.Popen` 起 claude。

### 改 skill:别动强制章节顺序

- `report.md` 的 6 个**必有**章节顺序固定:`总定位 → 界面清单 → 各界面功能与评价 → UI/UX → 官网描述 → 附录 A 截图索引`。可选章节(定价/目标用户/同类对比/优劣势)**只在有证据时出现**,无则整段省略,**不留"信息不足"占位**。
- 截图命名 `NN_<source>_<view>.png`,`source ∈ {web, app, android}`,`NN` 单调但允许跳号。每张图都必须在 `report.md` 里被引用过 — 没引用的删掉。
- 降级到 `mode: "web-only"` **只允许**三种触发条件(见 SKILL.md 末尾):没出当前 OS 安装包 / 当前平台没 cua-driver 预编译 / 应用启动反复失败。其它情况老老实实跑 full 模式。

### 桌面自动化:no-foreground 是死契约

任何驱动桌面端的工作都受 `.claude/skills/cua-driver/SKILL.md` 约束。最重要一条:**用户的前台应用不能变**。这意味着以下命令在本仓库里**绝对禁用**(除非用户**明确**要求"切到前台"):

- 任何形式的 `open` CLI(`open -a`、`open <bundle>`、`open <file>`、`open <url>`)— 都走 LaunchServices,都会激活。
- `osascript -e 'tell application "X" to activate / launch / open ...'`
- `cliclick` / 跨 app `CGEventPost` — 会真实挪用户的鼠标
- 浏览器的 `⌘L`(focus omnibox)、`⌘1..⌘9` / `⌘[` / `⌘]`(切 tab)— 都会被接收方解读为激活意图

正确做法:**`launch_app({bundle_id, urls:[...]})` 起进程并打开 URL**(内部有 FocusRestoreGuard),后续操作走 `get_window_state` → `element_index` 点击 → 再 `get_window_state` 校验。详尽规则在 `.claude/skills/cua-driver/SKILL.md`。

### 核心不变量(cua-driver):snapshot before AND after

每次动作都必须前后各一次 `get_window_state(pid, window_id)`。前一次解析 `element_index`(每次 snapshot 重建索引,跨调用即过期);后一次验证动作真的落地了。**跳过任意一边都会引入"看似成功的静默 no-op"**。

## 输入输出约定

### 输入

- `product_name`(必填)— 展示用原文,允许中文。> 80 字符会被拒。
- `url`(必填)— `https://...`。
- `download_url`(可选第三参)— 直接指向当前主机能用的安装包,有它就跳过"在官网找下载链接"。空字符串视为未提供。
- 缺位置参数会回退到 `input()`,**stdin 不是 tty 时直接 `cmd_new` 走兜底输入**。

### 输出

```
reports/<slug>-2026-05-18/
├── report.md            # 简体中文,6 强制章节按固定顺序
├── metadata.json        # 机器可读元数据,Python 写雏形,Claude 在结束前补齐
├── downloads/           # 安装包 / APK 下载缓存
└── screenshots/
    ├── 01_web_homepage.png
 ├── 05_app_main.png
 └── 09_android_main.png
```

`metadata.json` 关键字段:`product_name / url / download_url / host_os / host_arch / runtime ∈ {host, sandbox-local, sandbox-cloud} / sandbox / android / started_at / finished_at / mode ∈ {full, sandbox-full, web-only} / last_session_id / screenshots[] / warnings[]`。

## 退出码

| 码 | 含义 |
|---|---|
| 0 | 成功 |
| 1 | 预检失败 / 用户中断 / 续跑没 session_id |
| 2 | claude 子进程非零退出 |
| 130 | Ctrl+C 或 ESC 后放弃续跑 |
