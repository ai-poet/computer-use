# computer-use

一个**自动化竞品分析的 agent computer-use Python 脚本**:给它一个产品名和官网 URL,它就驱动 Claude Code 当 agent,自己打开浏览器爬官网、定位安装包、装上桌面端、用 cua-driver 操作真实 GUI 把主要界面挨个走一遍、批量截图,最后落一份结构稳定的简体中文竞品分析报告。

整条流水线是无人值守的:Python 把任务喂进 `claude --print --output-format stream-json --verbose` 子进程,Claude 通过 [`product-analyzer`](.claude/skills/product-analyzer/SKILL.md) skill 走 7 步固定 canonical loop,通过 [`cua-driver`](.claude/skills/cua-driver/SKILL.md) skill 严守 no-foreground 契约驱动桌面端 — 用户的前台应用全程不被抢走,可以一边干别的一边看 agent 在终端里把一款新产品拆开。

输入:产品名 + 官网 URL(可选第三个参数:直达安装包 URL)
输出:
- 一份结构稳定的简体中文 Markdown 竞品分析报告(6 个强制章节按固定顺序:总定位 / 界面清单 / 各界面功能与评价 / UI-UX / 官网描述 / 截图索引)
- 一个按命名规则编排的截图文件夹(`NN_<web|app>_<view>.png`)
- 一份 `metadata.json` 元数据(产物校验 + 断点续跑用)

执行过程对用户可见:stream-json 事件流被实时翻译成 Claude Code 风格的彩色终端输出 — thinking、工具调用、工具返回、TodoWrite 列表都以 ☐/◐/☑ 形式打到终端。中途发现 agent 走偏可以**按 ESC 暂停**,补一句话再 `--resume` 续跑。

---

## 仓库结构

```
computer-use/
├── README.md
├── .gitignore
├── reports/                                     # 每次跑的产出(可提交;downloads/ 与 .sandbox_ctl_last_shell.json 仍忽略)
├── scripts/
│   ├── analyze_product.py                       # 入口 shim(只调 product_analyzer.main)
│   ├── install_cua_driver.py                    # 桌面驱动器安装(macOS=Swift,Linux/Win=Rust)
│   └── product_analyzer/                        # 实现包
│       ├── __init__.py                          # 曝露 main + 模块依赖图
│       ├── config.py                            # 路径常量 + ANSI 配色
│       ├── ui.py                                # log/err/prompt_str/Spinner
│       ├── renderer.py                          # stream-json → 终端美化
│       ├── preflight.py                         # detect_host/ensure_*
│       ├── tasks.py                             # slug/metadata/list_tasks/post_check
│       ├── sandbox_runtime.py                   # 本地 Cua sandbox runtime 合约
│       ├── prompts.py                           # build_prompt + build_resume_prompt
│       ├── claude_driver.py                     # ESC + spawn + run_claude
│       ├── batch.py                             # CSV/JSON 队列 + 并发 worker
│       └── cli.py                               # argparse + cmd_new/cmd_resume/cmd_batch
└── .claude/skills/
    ├── cua-driver/                              # 桌面自动化 skill(snapshot→act→verify)
    └── product-analyzer/                        # 本项目核心 skill
        ├── SKILL.md                             # 工作流规则
        └── REPORT_TEMPLATE.md                   # 中文报告骨架
```

模块依赖单向无环:`config → ui → renderer → preflight → tasks → sandbox_runtime → prompts → claude_driver → batch → cli`。

`scripts/analyze_product.py` 不做产品分析的判断,只负责前置工作(校验输入、建目录、调 claude)。所有产品分析的判断逻辑在 `.claude/skills/product-analyzer/SKILL.md` 里 — **改规则不需要改代码**。

---

## 准备

### 1. 装 Claude Code CLI

按官方文档装好 `claude` 命令:<https://docs.claude.com/en/docs/claude-code>

### 2. 装 Python 依赖

批量本地 sandbox 模式依赖 Cua Sandbox SDK。它要求 Python 3.12 或 3.13;macOS Xcode 自带的 Python 3.9 不能安装 `cua` 包。

```bash
conda create -y -n computer-use-py312 python=3.12
conda activate computer-use-py312
python -m pip install -r requirements.txt
```

如果不用 conda,也可以用 Homebrew / pyenv / venv 创建 Python 3.12 或 3.13 环境。关键是运行 `analyze_product.py` 的 `python` 必须是 3.12/3.13。

### 3. 装桌面驱动器

```bash
python3 scripts/install_cua_driver.py
```

脚本会自动按平台选后端:

| 主机 | 后端 | 备注 |
|---|---|---|
| macOS arm64 / x86_64 | Swift `cua-driver` | 官方版,放 `/Applications/CuaDriver.app` |
| Linux x86_64 | `cua-driver-rs` | Rust 端口 |
| Windows x86_64 | `cua-driver-rs` | 走 `install.ps1`,无需管理员 |
| Linux aarch64 | 不支持(无预编译) | 需要时自行源码编译 |

如果首次运行 `analyze_product.py` 时没装,它会自动调起这个脚本。

### 4. 网络代理(可选)

`install_cua_driver.py` 会从 GitHub 下安装包,如果你需要走代理,先在父 shell 设好:

```bash
export https_proxy=http://127.0.0.1:7897
export http_proxy=http://127.0.0.1:7897
export all_proxy=socks5://127.0.0.1:7897
```

---

## 用法

### 交互式(零参数)

```bash
python3 scripts/analyze_product.py
```

菜单:

| 选项 | 说明 |
|------|------|
| `1` | 新任务 — host 模式 + cua-driver(默认) |
| `2` | 恢复历史任务 — 从 `reports/` 续跑 |
| `3` | 批量分析 — 默认**本地** Cua sandbox(Docker),可选云端 |
| `q` | 退出 |

单任务(选项 1)会依次问:

```
产品名: ProductiveKitty
官网 URL: https://productivekitty.masterwordai.com
下载链接(可选,直接回车跳过):
```

### 参数式(适合上层脚本/CI 集成)

```bash
# 两个必填位置参数
python3 scripts/analyze_product.py "ProductiveKitty" "https://productivekitty.masterwordai.com"

# 第三个位置参数(下载链接)可选,有就跳过"在官网找下载链接"那一步
python3 scripts/analyze_product.py "ProductiveKitty" \
  "https://productivekitty.masterwordai.com" \
  "https://file.masterwordai.com/zeabur/Desktop%20Cat-1.0.5-arm64.dmg"
```

任何缺失的位置参数会回退到 `input()` 询问。空字符串视为"未给"。

### 批量并发(默认本地 sandbox)

批量模式在本机用 `--max-workers` **并发**启动多个独立的 `claude --print` worker,每个 worker 分析队列里的一个产品。**并发跑时,每个产品都会先在自己的隔离环境里创建一台沙盒**(本地 Docker/Lume/QEMU,或 Cua Cloud VM),分析结束后再销毁;worker 之间不共享沙盒、也不碰你 Mac 上的前台应用。

**本机 Claude 不直接连沙盒 GUI**,而是通过 **脚本** 间接操控:

1. **Python 编排器**(`scripts/analyze_product.py` + `scripts/product_analyzer/batch.py`)只负责起子进程、注入 env、写 `reports/<slug>/`、云端时挂 `--mcp-config`;**不**替 Claude 点鼠标。
2. **每个 Claude worker** 读 product-analyzer skill,用 **Bash 反复调用** [`scripts/sandbox_ctl.py`](scripts/sandbox_ctl.py)(本地)或 **Cua MCP**(云端)完成「建沙盒 → **以鼠标为主**逐步截图/点击/滚动 → 拆沙盒」。官网用 `bootstrap --open-browser --url …` 打开,**不要**用 `wget` 抓 HTML;`step shell` 仅用于下载已有直链的安装包。若 Bash 吞 stdout,读 `reports/.../.sandbox_ctl_last_shell.json`。
3. **`sandbox_ctl`** 内部用 Cua Sandbox SDK 对 **named** 容器发单步命令(`screenshot` / `click` / `shell` …),连接信息写在 `reports/.../sandbox.json`;Claude 每步一条命令、先看 PNG 再决策,与单任务里 cua-driver 的 observe–act 节奏一致。

```
queue.json
    │
    ├─ worker 1 (claude --print) ──Bash──► sandbox_ctl bootstrap / step … / teardown
    │                                              │
    │                                              ▼
    │                                    Docker 沙盒 A (cua-xfce)
    │
    └─ worker 2 (claude --print) ──Bash──► sandbox_ctl …
                                              │
                                              ▼
                                    Docker 沙盒 B (独立)
```

worker 结束后,编排器还会在 `finally` 里 **兜底 teardown**,避免容器泄漏。

每个 worker 的 prompt **只传入参数**(runtime、sandbox 镜像、是否批量并行等)并指向 `.claude/skills/product-analyzer/SKILL.md` 的 **「Sandbox 运行合约」** 与 **「沙盒控制三阶段」**;细则在 skill 里维护(符合「改规则不改代码」)。环境变量 `ANALYZER_BATCH_PARALLEL=1`、`ANALYZER_CONDA_ENV` 等供 Claude 对照。

**Host vs 沙盒控制面对照**

| 模式 | 谁创建环境 | 本机 Claude 如何操控 |
|------|------------|----------------------|
| 单任务 `runtime=host` | 无沙盒,直接用本机桌面 | **cua-driver** MCP/CLI(`get_window_state` → `element_index`) |
| 批量 `sandbox-local` | `sandbox_ctl bootstrap` 起 Docker 等 | **鼠标优先** Bash 调 `screenshot`/`click`/`scroll`/`type`(shell 仅下载安装包) |
| 批量 `sandbox-cloud` | MCP / `sandbox_ctl` 起 Cloud VM | **Cua MCP**(`computer_screenshot` / `computer_click` / …),编排器注入 `--mcp-config` |

**不要**让 Claude 写一整段 `asyncio.run()` 把分析包进一个 Python 文件 — 应 **一条 Bash 一步**,截图落到 `reports/.../screenshots/` 后再继续。

**默认行为:本地 sandbox。** 未传 `--sandbox` 时一律走本机 Docker/Lume,即使环境里已有 `CUA_API_KEY` 也不会自动切到云端。

若要使用 **Cua Cloud 云端 sandbox**,必须显式指定:

```bash
python scripts/analyze_product.py --batch queue.json --sandbox cloud --cua-api-key sk-...
# 或
export CUA_API_KEY=sk-...
python scripts/analyze_product.py --batch queue.json --sandbox cloud
```

环境说明见 [Cua Set Up a Sandbox](https://cua.ai/docs/cua/guide/get-started/set-up-sandbox):

- **本地(默认)**:Linux 桌面用 Docker 镜像 **`trycua/cua-xfce:latest`**(轻量 XFCE + 浏览器);`--sandbox-image linux` 时由 SDK 拉取该镜像。Apple Silicon 需 `linux/amd64` 平台(见下方 `docker pull`)。macOS/Windows 桌面包仍走 Lume/QEMU。
- **云端(仅 `--sandbox cloud`)**:由 Cua Cloud 托管,需 API Key,无需本机 Docker

零参数运行后选菜单 `3` 可进入批量分析向导;向导里默认也是本地,选 `2` 才走云端。

先确认本地依赖并预拉 Linux 镜像(推荐,避免首跑超时):

```bash
conda activate computer-use-py312
python --version   # 应为 3.12.x 或 3.13.x
python -m pip install -r requirements.txt
docker info
claude --version
cua --version      # sandbox_ctl + cloud MCP

# 本地 Linux 桌面 sandbox(与 Cua 文档 "Linux on Docker" 一致)
docker pull --platform=linux/amd64 trycua/cua-xfce:latest

# 逐步控制桥 smoke(需 Docker);截图落在 tmp/sandbox-ctl-smoke/screenshots/
python -m tests.sandbox.sandbox_ctl_smoke
# 保留容器便于手查: python -m tests.sandbox.sandbox_ctl_smoke --no-teardown
```

### Android APK 沙盒(可选)

若产品官网提供 **APK**,可在 **Android 模拟器沙盒**里下载、安装、启动并截图体验(对应 skill 里的 `android` 路径、`screenshots/NN_android_*.png`)。镜像为 QEMU Android 容器,**APK 的安装与 UI 测试都在该沙盒内完成**,不占用 host 真机。

预拉镜像(Apple Silicon / arm64 Mac **必须**带 `--platform=linux/amd64`,否则会出现 `no matching manifest for linux/arm64`):

```bash
docker pull --platform=linux/amd64 trycua/cua-qemu-android:latest
```

Intel Mac / Linux x86_64 可直接:

```bash
docker pull trycua/cua-qemu-android:latest
```

批量分析时启用 Android 路径(默认 `--sandbox-image linux` **不会**走 APK;需显式打开):

```bash
python scripts/analyze_product.py \
  --batch queue.language-learning.json \
  --max-workers 2 \
  --sandbox-image auto \
  --android
```

Android 路径同样由 Claude 通过 **`sandbox_ctl`**(或云端 MCP)逐步操作独立 Android 沙盒(`adb install`、截图等),APK 落在各产品目录的 `downloads/` 下。详见 [Cua Set Up a Sandbox — Android](https://cua.ai/docs/cua/guide/get-started/set-up-sandbox) 与 skill 中的 Android 增强路径。

若本机配置了 HTTP 代理,批量本地 sandbox 会自动为 worker 设置 `NO_PROXY=127.0.0.1,localhost`,避免 SDK 探测 `localhost:<docker_port>` 时被代理成 502。

**网页点击能不能用?** 可以。`cua-xfce` 镜像是带 XFCE 桌面的 Linux 容器,内置 `computer-server`;Claude 用 `sandbox_ctl step click/type/screenshot` 在沙盒里做**坐标级**自动化(先 `step shell` 打开浏览器)。这与 host 上 cua-driver 的 `element_index` 不是同一条路,但对常规官网导航、表单、滚动足够。参考截图见 [`tmp/sandbox-ctl-smoke/screenshots/`](tmp/sandbox-ctl-smoke/screenshots/)(`python -m tests.sandbox.sandbox_ctl_smoke` 生成)。

建议先跑 Linux sandbox smoke test,确认 Cua SDK + Docker + GUI/UI 截图链路可用。测试在 `tests/sandbox/`:

```bash
# 只检查 Python / cua / Docker,不拉起 sandbox
python -m tests.sandbox.linux_smoke --check-only

# 完整 smoke(每步默认 180s 超时)
python -m tests.sandbox.linux_smoke --timeout 180
```

这个测试会覆盖:

- Python / `cua` 包版本检查
- Docker daemon 和正在运行的 Cua 容器摘要
- `Sandbox.ephemeral(trycua/cua-xfce:latest, local=True, platform=linux/amd64)` 创建
- `sb.shell.run(...)`、`sb.screen.size()`
- 常见 UI 操作:`mouse.move` / `click` / `right_click` / `double_click` / `scroll`,`keyboard.type` / `keypress`
- 多步截图(桌面、右键菜单、滚动后、尝试打开终端、输入文字等)保存到 `tmp/sandbox-smoke/screenshots/01_*.png` … `07_*.png`
- 结构化结果 `tmp/sandbox-smoke/linux_smoke_report.json`

如果卡住或失败,脚本会自动打印相关 Cua 容器的 `docker port` 和 `docker logs --tail ...`,方便定位是 Docker、容器服务还是 SDK 连接问题。

准备一个队列文件,例如 `queue.test.json`:

```json
[
  {
    "product_name": "Excalidraw",
    "url": "https://excalidraw.com"
  },
  {
    "product_name": "Tldraw",
    "url": "https://www.tldraw.com"
  }
]
```

跑两个并发 worker(默认本地 Linux sandbox,可省略 `--sandbox local`):

```bash
# 仓库里示例队列是 queue.language-learning.json,不是 queue.json
python scripts/analyze_product.py \
  --batch queue.language-learning.json \
  --max-workers 2 \
  --sandbox-image linux
```

`--sandbox-image linux` 时**不会**预检 Android,也不会走 APK 路径;需要 APK 时请预拉上方 `cua-qemu-android` 镜像并加 `--android`(或 `--sandbox-image auto`)。

云端 sandbox(必须加 `--sandbox cloud`;Key 在 [cua.ai](https://cua.ai/signin) 创建):

```bash
python scripts/analyze_product.py \
  --batch queue.test.json \
  --max-workers 2 \
  --sandbox cloud \
  --cua-api-key sk-...
```

运行后每个产品都会写入独立目录:

```text
reports/<product-slug>-YYYY-MM-DD[-N]/
├── report.md
├── metadata.json
├── run.log
├── downloads/
└── screenshots/
```

`run.log` 是该产品对应 Claude worker 的完整事件流。若本机缺少 `cua`、Docker、Lume、QEMU 或 Android SDK,CLI 会在启动前提示缺失项。第一轮批量测试建议 `--sandbox-image linux` + 已预拉 `cua-xfce` 镜像;`metadata.json` 里 `runtime` 为 `sandbox-local` 或 `sandbox-cloud`,`sandbox.mode` 为 `local` / `cloud`。

### 执行过程

启动后:

1. **预检**:`claude` CLI、cua-driver。后者没装就自动调起 `install_cua_driver.py`
2. **建目录**:`reports/<slug>-YYYY-MM-DD[-N]/screenshots/`
3. **写 metadata.json 雏形**(主机信息、起始时间)
4. **调 claude 子进程**,把任务 prompt 喂进去
5. **stream-json 事件流以 Claude Code 风格渲染** — 思考、工具调用、工具返回、文本、TodoWrite 列表都直接以彩色 + ☐/◐/☑ 的形式打到终端
6. 进程结束后做产物校验(报告和 metadata 是否就位),提示缺漏

权限模式默认 `bypassPermissions`,Claude Code 不会因每次工具调用打断流程问"允许吗?"。如果你想要交互式确认,改 `analyze_product.py` 里那行 `--permission-mode` 即可。

### ESC 中断 + 续跑

执行过程中如果发现 Claude 走偏了,**按 ESC** 暂停当前回合:

```
── 已暂停。
    输入补充指令后回车继续(空行则放弃,直接退出)。多行用反斜杠续行。
补充> 你刚才漏看了官网底部的 CDN 链接,重新扫一遍 https?://...\.dmg 再决定降级
```

回车后脚本用 `claude --resume <session_id>` 续跑,并把你的补充指令作为新一轮提示喂进去。Claude Code 会带着完整历史继续工作,不丢前面已经做的事。

空行则放弃续跑、清理退出。仅在 stdin 是真 tty(交互式终端)时启用,管道/CI 模式下自动禁用。

### 调试模式

把全量 stream-json 同时写到磁盘,用于事后排查:

```bash
ANALYZE_RAW_LOG=/tmp/raw.jsonl python3 scripts/analyze_product.py "ProductiveKitty" "https://productivekitty.masterwordai.com"
```

终端照常显示美化输出,`/tmp/raw.jsonl` 里是逐行 JSON,可以再丢给任何 stream-json 解析器复盘。

---

## 输出布局

```
reports/<slug>-2026-05-18/
├── report.md                       # 简体中文,3 强制章节按顺序
├── metadata.json                   # 机器可读元数据
├── downloads/                      # 安装包 / APK 下载缓存
└── screenshots/
    ├── 01_web_homepage.png         # NN_<source>_<view>.png
    ├── 02_web_pricing.png
    ├── 05_app_main.png
    ├── 09_android_main.png
    └── ...
```

**slug 规则**:`kebab-case(ascii-fold(产品名))`,40 字符内。中文名走 fallback `product-<md5前6位>`。

**截图编号**:`NN_<source>_<view>.png`,`source ∈ {web, app, android}`,`NN` 单调递增允许跳号。每张图都在 `report.md` 里以相对路径出现,且在附录 A 截图索引里有一行说明。

**metadata.json**(由 Python 写雏形,Claude 在结束前补齐):
```json
{
  "product_name": "ProductiveKitty",
  "url": "https://productivekitty.masterwordai.com",
  "download_url": null,
  "host_os": "darwin",
  "host_arch": "arm64",
  "runtime": "host",
  "sandbox": {"image": null, "local": true, "name": null},
  "android": {
    "enabled": false,
    "apk_url": null,
    "apk_file": null,
    "package_name": null,
    "mode": null
  },
  "started_at": "2026-05-18T03:30:00+08:00",
  "finished_at": "2026-05-18T03:55:00+08:00",
  "mode": "full",
  "screenshots": [
    {"file": "screenshots/01_web_homepage.png", "view": "web-homepage", "caption": "官网首页"}
  ],
  "warnings": []
}
```

`mode = "full"` 表示 host 上同时分析了官网与桌面端;`mode = "sandbox-full"` 表示本地 Cua sandbox 内完成官网/桌面端分析;`mode = "web-only"` 表示只看了官网(降级条件见下一节)。若额外分析了 APK,`android.mode` 会记录 Android 路径结果。

**同日重跑**不会覆盖 — 自动追加 `-2`、`-3` 后缀。

---

## 报告模板

强制章节(顺序固定):

1. **总定位** — 这是什么、解决什么、面向谁
2. **界面清单** — 实际看到的所有主要界面,挂截图
3. **各界面功能与评价** — 具体到字段/按钮,可证伪
4. **UI/UX 风格和质量描述** — 视觉风格、信息密度、交互流畅度、文案、可访问性观察
5. **官网描述** — 官网原文摘录、关键卖点、与实际体验的差距
6. **附录 A 截图索引** — 表格列每张图

可选章节(定价 / 目标用户 / 同类对比 / 优劣势)**只有有证据时出现**,无则整段省略,不留"信息不足"占位。

完整骨架见 `.claude/skills/product-analyzer/REPORT_TEMPLATE.md`。

---

## 跨平台与降级

默认 **full 模式**:用 cua-driver(macOS) / cua-driver-rs(Linux/Windows)驱动桌面端。

仅在以下三种情况降级到 **web-only**:
1. 产品官网没出当前主机 OS 的安装包
2. 当前平台没有 cua-driver 预编译(Linux aarch64)
3. 应用安装/启动反复失败

降级时:
- `metadata.json.mode = "web-only"`,`warnings[]` 记录原因
- 报告头注明"本次为网页版分析,未驱动桌面端,因为 ..."
- 报告其他部分照常写,只是 §1 仅基于官网与浏览器截图

---

## 退出码

| 退出码 | 含义 |
|---|---|
| 0 | 成功 |
| 1 | 预检失败(claude / cua-driver 缺失,且自动安装失败)、用户中断 |
| 2 | claude 子进程异常退出 |
| 130 | Ctrl+C 中断 |

---

## 改规则不改代码

要调整分析逻辑、报告章节、截图命名规则、降级条件,改 `.claude/skills/product-analyzer/SKILL.md`(和它引用的 `REPORT_TEMPLATE.md`)即可,Python 脚本不用动。

要换桌面驱动器后端逻辑,改 `scripts/install_cua_driver.py`。

要改桌面自动化的具体打法(snapshot 不变量、no-foreground 契约、坐标系),改 `.claude/skills/cua-driver/SKILL.md`。

---

## 验证

随便挑一个有官网的产品试一次:

```bash
python3 scripts/analyze_product.py "ProductiveKitty" "https://productivekitty.masterwordai.com"
```

通过条件:
1. 终端实时看见 stream-json 事件流(thinking、各类 Tool 调用、Tool 返回都可见)
2. `reports/productivekitty-YYYY-MM-DD/report.md` 存在,3 个强制章节按顺序
3. `screenshots/` 至少 1 张 `web_*` + (有桌面端时)≥3 张 `app_*`
4. 每张截图都在 `report.md` 里被引用过
5. `metadata.json` 的 `finished_at` / `mode` 字段已被补齐
6. 重跑同输入 → 产出 `...-2026-05-18-2/` 而非覆盖
