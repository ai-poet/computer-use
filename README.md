# computer-use

`computer-use` 是一条“分析一款新产品”的可重复流水线:输入产品名和官网 URL,系统启动 Claude Code agent,在 Linux 本地 Docker 沙盒里访问官网、判断客户端形态、尝试运行可用客户端,逐步截图和写阶段报告,最后汇总成一份中文产品分析报告。

默认路径已经是 **Linux-first sandbox workflow**:

1. 进入 Linux 本地 Docker 沙盒。
2. 在沙盒 Firefox 访问产品官网。
3. 判断是否有 Linux / Windows / Android / macOS / iOS 客户端。
4. 优先跑 Linux 客户端;没有 Linux 时尝试 Windows 客户端 + Wine。
5. 只有拿到官方 APK 时才启动 Android 沙盒。
6. 只有 iOS/macOS、安装失败、拿不到 APK 或无 credential 时,降级 web-only。
7. 每一步写 `steps/*.md`,最后写 `report.md` 汇总。

---

## 分层架构

系统刻意分成四层,避免把所有提示词、控制逻辑和展示逻辑揉在一起。

| 层 | 目录/文件 | 职责 |
|---|---|---|
| CLI 编排层 | `backend/analyze_product.py`, `backend/product_analyzer/cli.py` | 参数解析、预检、建输出目录、启动 Claude 子进程。 |
| 执行控制层 | `claude_driver.py`, `batch.py`, `sandbox_ctl.py` | 流式运行 Claude、批量并发、控制 Cua sandbox 的 bootstrap/step/teardown。 |
| Workflow 规则层 | `.claude/skills/product-analyzer/` | 决定分析什么、怎么降级、每步产出什么。规则改这里,不改 Python 主流程。 |
| 可视化层 | `backend/product_analyzer/server.py`, `web/` | 本地 FastAPI + React/Vite 控制台,展示任务、日志、步骤、credential 请求。 |

模块依赖方向仍保持单向:

```text
config → ui → batch_store → batch_dashboard → renderer → preflight → tasks
       → workflow → sandbox_runtime → sandbox_ctl → prompts → claude_driver
       → batch → cli
```

`sandbox_ctl` 是本地 sandbox 的唯一薄控制桥,不 import `claude_driver` 或 `batch`。

---

## 核心目录

```text
computer-use/
├── backend/
│   ├── analyze_product.py                 # CLI shim
│   ├── analyzer_server.py                 # Web 控制台后端入口
│   ├── sandbox_ctl.py                     # sandbox_ctl shim
│   └── product_analyzer/
│       ├── cli.py                         # 命令入口
│       ├── batch.py                       # 单任务/批量 worker
│       ├── claude_driver.py               # claude --print stream-json 编排
│       ├── sandbox_ctl.py                 # Cua sandbox 单步控制
│       ├── workflow.py                    # workflow.json / steps 校验
│       ├── hooks.py                       # Claude hooks 护栏
│       ├── server.py                      # FastAPI 本地控制台
│       └── credentials.py                 # 本地 keyring credential 存储
├── .claude/
│   ├── settings.json                      # 项目级 hooks 注册
│   └── skills/product-analyzer/
│       ├── SKILL.md                       # 轻量入口
│       ├── REPORT_TEMPLATE.md             # 最终报告模板
│       └── workflows/                     # 分步骤 workflow 文档
├── .agents/skills/product-analyzer/       # Codex 侧同步副本
├── web/
│   ├── src/pages/                         # 页面组装
│   ├── src/components/                    # UI 组件
│   ├── src/hooks/                         # React 数据流 hooks
│   ├── src/api.ts                         # API 调用
│   └── src/types.ts                       # 前端类型
├── reports/                               # 每次分析的产物
└── queue*.json                            # 批量队列
```

---

## Workflow 文档拆分

`product-analyzer` skill 不再承载一整坨长提示词。入口只说明“读哪些 workflow 文档”,详细规则拆到:

| 文件 | 作用 |
|---|---|
| `00-contract.md` | 输入输出、状态文件、禁止事项、credential 契约。 |
| `01-linux-sandbox.md` | 创建 Linux Docker 沙盒并打开官网。 |
| `02-website-discovery.md` | 官网真实浏览、截图、下载入口发现。 |
| `03-client-routing.md` | Linux / Windows / Android / macOS / iOS 决策树。 |
| `04-desktop-client.md` | Linux 客户端与 Windows + Wine 路径。 |
| `05-android-client.md` | 官方 APK 与 Android 沙盒路径。 |
| `06-web-only.md` | 降级后的网页体验力度。 |
| `07-reporting.md` | 阶段报告与最终报告规则。 |

改报告章节、截图规则、降级条件、客户端优先级,优先改这些 `.md`,不要把业务判断塞回 Python。

---

## 输出产物

每个任务独立写入 `reports/<slug>-YYYY-MM-DD[-N]/`:

```text
reports/<slug>-YYYY-MM-DD[-N]/
├── workflow.json              # workflow 状态、客户端路由、credential 请求
├── events.jsonl               # hooks/agent 事件,已脱敏
├── steps/
│   ├── 01_linux_sandbox.md
│   ├── 02_website.md
│   ├── 03_client_discovery.md
│   ├── 04_desktop_client.md
│   ├── 05_android_client.md
│   ├── 06_web_experience.md
│   └── 07_final_report.md
├── report.md                  # 最终中文汇总报告
├── metadata.json              # 机器可读元数据
├── sandbox.json               # sandbox 连接信息
├── run.log                    # Claude stream-json 日志
├── downloads/                 # 安装包/APK 缓存,不提交
└── screenshots/
    ├── 01_web_homepage.png
    ├── 05_app_main.png
    └── 09_android_main.png
```

截图命名: `NN_<source>_<view>.png`,`source ∈ {web, app, android}`。所有保留截图必须在阶段报告或最终报告中引用。

---

## 环境准备

### Claude Code

安装并登录 `claude` CLI:

```bash
claude --version
```

### Python

Cua Sandbox SDK 要求 Python 3.12 或 3.13:

```bash
conda create -y -n computer-use-py312 python=3.12
conda activate computer-use-py312
python -m pip install -r requirements.txt
```

关键依赖:

- `cua`: Cua Sandbox SDK/CLI
- `fastapi` / `uvicorn`: 本地控制台后端
- `keyring`: credential 加密保存

### Docker 与镜像

默认 Linux 沙盒使用 `trycua/cua-xfce:latest`:

```bash
docker info
docker pull --platform=linux/amd64 trycua/cua-xfce:latest
```

Apple Silicon 也建议带 `--platform=linux/amd64`。

### Android 可选镜像

只有找到官方 APK 时才会尝试 Android:

```bash
docker pull --platform=linux/amd64 trycua/cua-qemu-android:latest
```

---

## CLI 用法

### 单任务,默认 Linux sandbox

```bash
python3 backend/analyze_product.py "ProductiveKitty" "https://productivekitty.masterwordai.com"
```

给定下载链接:

```bash
python3 backend/analyze_product.py NAME URL DOWNLOAD_URL
```

### 旧 host/cua-driver 路径

只在需要兼容旧流程时使用:

```bash
python3 backend/analyze_product.py --host "ProductiveKitty" "https://productivekitty.masterwordai.com"
```

`--host` 会使用本机 cua-driver,不走 Linux-first workflow。

### 交互式菜单

```bash
python3 backend/analyze_product.py
```

菜单:

| 选项 | 说明 |
|---|---|
| `1` | 新任务,默认 Linux sandbox workflow。 |
| `2` | 从 `reports/` 恢复历史任务。 |
| `3` | 批量分析。 |
| `q` | 退出。 |

### 批量

```bash
python3 backend/analyze_product.py --batch queue.language-learning.json --max-workers 2 --sandbox-image linux
python3 backend/analyze_product.py --batch-all --max-workers 5 --sandbox-image linux
```

云端 sandbox 需要显式指定:

```bash
python3 backend/analyze_product.py --batch queue.json --sandbox cloud --cua-api-key sk-...
```

纯文本模式:

```bash
python3 backend/analyze_product.py --batch-all --max-workers 5 --batch-plain
```

---

## 本地 Web 控制台

后端:

```bash
python3 backend/analyzer_server.py
```

前端:

```bash
cd web
npm install
npm run dev
```

默认前端代理到 `http://127.0.0.1:8765`。

第一版控制台能力:

- 新建分析任务。
- 查看任务列表和当前 workflow 步骤。
- 通过 WebSocket 看 `run.log` / `events.jsonl` 实时输出。
- 查看最终 `report.md`。
- 处理 credential 请求,通过本地 keyring 加密保存。

前端分层:

| 目录 | 作用 |
|---|---|
| `web/src/pages/` | 页面级组合。 |
| `web/src/components/` | 可复用面板和控件。 |
| `web/src/hooks/` | 数据加载、轮询、WebSocket hooks。 |
| `web/src/api.ts` | 后端 API 封装。 |
| `web/src/types.ts` | 共享类型。 |

---

## Hooks 护栏

项目级 hooks 在 `.claude/settings.json` 注册,脚本在 `backend/product_analyzer/hooks.py`。

当前做三类事:

- `PreToolUse`:拦截 host GUI 激活命令,如 `open`、`osascript activate/open/launch`、`cliclick`;在 sandbox workflow 中拦截用 `curl/wget` 抓官网替代真实浏览。
- `PostToolUse`:记录脱敏事件到 `events.jsonl`。
- `Stop`:检查 `workflow.json`、`steps/*.md`、`metadata.json`、`report.md` 是否完整,不完整就阻止结束。

hooks 是“硬护栏”,workflow `.md` 是“业务规则”。不要把产品分析决策写进 hooks。

---

## Credential 处理

遇到客户端登录墙时,agent 应写入 `workflow.json.credential_requests[]`。Web 控制台显示请求,用户提交后:

1. 后端用 `keyring` 存到本机安全凭据系统。
2. `workflow.json` 只保存 opaque `credential_id`。
3. `events.jsonl`、`metadata.json`、`steps/*.md`、`report.md` 不写明文 secret。

如果 keyring 不可用,应拒绝保存并记录 warning,不要降级到明文落盘。

---

## 沙盒操作原则

沙盒内 GUI 操作遵守 observe → act → observe:

```bash
python backend/sandbox_ctl.py bootstrap "$OUTPUT_DIR" --open-browser --url "$URL"
python backend/sandbox_ctl.py step screenshot "$OUTPUT_DIR" --out screenshots/01_web_homepage.png
python backend/sandbox_ctl.py step click "$OUTPUT_DIR" 640 120
python backend/sandbox_ctl.py step scroll "$OUTPUT_DIR" 512 400 --scroll-y -6
python backend/sandbox_ctl.py step screenshot "$OUTPUT_DIR" --out screenshots/02_web_pricing.png
```

规则:

- 官网必须在 Firefox 里真实浏览,不能 shell 抓站代替。
- `step shell` 只用于已有直链下载安装包/APK、安装命令、系统探测或排障。
- Linux 客户端优先;没有 Linux 才尝试 Windows + Wine。
- Google Play 只记录证据,不从第三方镜像下载 APK。
- macOS/iOS-only 直接 web-only。

---

## 验证

基础检查:

```bash
python3 backend/analyze_product.py --help
python3 -m py_compile backend/product_analyzer/*.py
```

hook 快速检查:

```bash
printf '{"tool_name":"Bash","tool_input":{"command":"open https://example.com"}}' \
  | ANALYZER_RUNTIME=sandbox-local python3 backend/product_analyzer/hooks.py pre-tool
```

前端构建:

```bash
cd web
npm install
npm run build
```

sandbox smoke:

```bash
python -m unittest tests.sandbox.test_sandbox_ctl_normalize_keys -v
python -m tests.sandbox.sandbox_ctl_smoke
```

---

## Git 与生成物

会提交:

- `report.md`
- `metadata.json`
- `workflow.json`
- `events.jsonl`
- `steps/*.md`
- `screenshots/`
- `run.log`

不会提交:

- `reports/**/downloads/`
- `reports/**/.sandbox_ctl_last_shell.json`
- `web/node_modules/`
- `web/dist/`
- `web/*.tsbuildinfo`

---

## 退出码

| 码 | 含义 |
|---|---|
| `0` | 成功。 |
| `1` | 预检失败、用户中断、恢复任务缺 session。 |
| `2` | Claude 子进程非零退出。 |
| `130` | Ctrl+C 或 ESC 后放弃续跑。 |
