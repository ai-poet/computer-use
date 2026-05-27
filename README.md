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
| 执行控制层 | `claude_driver.py`, `batch.py`, `sandbox_ctl.py`, `android_ctl.py` | 流式运行 Claude、批量并发、控制 Linux 桌面沙盒和 Android 移动端沙盒。 |
| Workflow 规则层 | `.claude/skills/product-analyzer/` | 决定分析什么、怎么降级、每步产出什么。规则改这里,不改 Python 主流程。 |
| 可视化层 | `backend/product_analyzer/server.py`, `web/` | 本地 FastAPI + React/Vite 控制台,展示任务、日志、步骤、credential 请求。 |

模块依赖方向仍保持单向:

```text
config → ui → batch_store → batch_dashboard → renderer → preflight → tasks
       → workflow → sandbox_runtime → sandbox_ctl / android_ctl → prompts → claude_driver
       → batch → cli
```

`sandbox_ctl` 是 Linux/Firefox 桌面沙盒控制桥;`android_ctl` 是 Android/QEMU 移动端控制桥。两者都不 import `claude_driver` 或 `batch`。

---

## 核心目录

```text
computer-use/
├── backend/
│   ├── analyze_product.py                 # CLI shim
│   ├── analyzer_server.py                 # Web 控制台后端入口
│   ├── sandbox_ctl.py                     # sandbox_ctl shim
│   ├── android_ctl.py                     # android_ctl shim
│   └── product_analyzer/
│       ├── cli.py                         # 命令入口
│       ├── batch.py                       # 单任务/批量 worker
│       ├── claude_driver.py               # claude --print stream-json 编排
│       ├── sandbox_ctl.py                 # Cua sandbox 单步控制
│       ├── android_ctl.py                 # Android sb.mobile 单步控制
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
│   │   ├── StatusBadge.tsx                # 状态徽章
│   │   ├── MarkdownRenderer.tsx           # Markdown 渲染（含目录导航）
│   │   ├── ScreenshotGallery.tsx          # 截图预览画廊
│   │   ├── EmptyState.tsx                 # 空状态
│   │   ├── LoadingState.tsx               # 加载骨架屏
│   │   └── ErrorState.tsx                 # 错误状态
│   ├── src/hooks/                         # React 数据流 hooks
│   ├── src/api.ts                         # API 调用
│   ├── src/types.ts                       # 前端类型
│   └── docs/ui-ux-improvements.md         # UI/UX 设计文档
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

批量任务会按队列文件分类写入子目录:

```text
reports/language-learning/duolingo-YYYY-MM-DD/
reports/desktop-pets/productivekitty-YYYY-MM-DD/
```

分类默认来自队列文件名,例如 `queue.language-learning.json` → `language-learning`;队列行里的 `category` 或 `queue_category` 字段可以覆盖默认分类。单任务仍写在 `reports/<slug>-YYYY-MM-DD[-N]/`。

Web 控制台内部会把分类 run id 显示成 `language-learning~duolingo-YYYY-MM-DD`,对应磁盘目录仍是 `reports/language-learning/duolingo-YYYY-MM-DD/`。

截图命名: `NN_<source>_<view>.png`,`source ∈ {web, app, android}`。所有保留截图必须在阶段报告或最终报告中引用。

---

## 环境准备

### Claude Code

安装并登录 `claude` CLI:

```bash
claude --version
```

### 前端

```bash
cd web
npm install
```

前端技术栈:

- **React 19** + Vite 6 + TypeScript
- **Tailwind CSS v4** (`@tailwindcss/vite`) - 原子化样式 + 暗色/亮色主题
- **react-markdown** + **remark-gfm** - Markdown 报告渲染（含目录导航、代码块复制）
- **lucide-react** - 图标库

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
docker pull --platform=linux/amd64 trycua/cua-xfce:latest   # arm64 Mac 必带 platform

# 无需 Docker 的快速检查
python -m unittest tests.sandbox.test_sandbox_ctl_normalize_keys -v

# 单沙盒逐步控制 smoke(会起停一台容器; bootstrap 打开 Firefox 并截图到 tmp/sandbox-ctl-smoke/)
python -m tests.sandbox.sandbox_ctl_smoke
python -m tests.sandbox.sandbox_ctl_smoke --url https://excalidraw.com

# 可选:SDK 级 GUI smoke
python -m tests.sandbox.linux_smoke --check-only
python -m tests.sandbox.linux_smoke --timeout 180
```

Apple Silicon 也建议带 `--platform=linux/amd64`。

### Android 可选镜像

只有找到官方 APK 时才会尝试 Android:

```bash
docker pull --platform=linux/amd64 trycua/cua-qemu-android:latest
```

Apple Silicon / arm64 Mac 必须带 `--platform=linux/amd64`。Android 虚拟机通过 Cua Sandbox SDK 启动为独立 sandbox,不复用 Linux Firefox 沙盒。规则上要求找到官网直链或官方 release asset APK 后才启动 Android。

SDK 写法参考:

```python
from cua import Image, Sandbox

image = Image.from_registry("trycua/cua-qemu-android:latest")
sb = await Sandbox.create(image, name=android_name, local=True)
```

安装 APK 优先使用 image builder:

```python
image = Image.from_registry("trycua/cua-qemu-android:latest").apk_install(str(apk_path))
sb = await Sandbox.create(image, name=android_name, local=True)
```

操作 Android UI 时优先用 `sb.mobile.tap/swipe/type_text/back/home` 和 `sb.screenshot()`。Android 启动或安装失败只记录到 `metadata.android.mode` 和 `warnings[]`,整单继续走 web-only 或已有桌面证据。

Android 路径由 workflow 通过 Cua Sandbox SDK 控制独立 Android sandbox。APK 落在各产品目录的 `downloads/` 下;如果 image builder 安装失败,才降级为连接后执行 `adb install`。

若本机配置了 HTTP 代理,批量本地 sandbox 会自动为 worker 设置 `NO_PROXY=127.0.0.1,localhost`,避免 SDK 探测 `localhost:<docker_port>` 时被代理成 502。

Linux 沙盒 smoke 测试在 `tests/sandbox/`: `sandbox_ctl_smoke` 会通过 `bootstrap --open-browser --url` 打开 Firefox 并做滚动/点击截图;`linux_smoke` 会检查 SDK、Docker、GUI 截图和基础鼠标键盘操作。

### Android 移动端控制

Android 不复用 `sandbox_ctl`。Linux `sandbox_ctl` 面向 Firefox 桌面坐标流;Android 需要独立移动端桥:

```bash
python backend/android_ctl.py bootstrap "$OUTPUT_DIR" --apk "$OUTPUT_DIR/downloads/app.apk" --install-with-image
python backend/android_ctl.py screenshot "$OUTPUT_DIR" --out screenshots/09_android_launch.png
python backend/android_ctl.py tap "$OUTPUT_DIR" 540 1600
python backend/android_ctl.py swipe "$OUTPUT_DIR" 540 1600 540 600 --duration-ms 450
python backend/android_ctl.py type "$OUTPUT_DIR" "example"
python backend/android_ctl.py key "$OUTPUT_DIR" back
python backend/android_ctl.py teardown "$OUTPUT_DIR"
```

`backend/android_ctl.py` 维护 `android_sandbox.json`,调用 Cua SDK 的 `sb.mobile` 接口。只有移动端接口不可用时,才用 `android_ctl shell -c 'adb shell input ...'` 作为降级。

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
python3 backend/analyze_product.py --batch queue.desktop-pets.json --batch queue.coding-platforms.json --max-workers 2
python3 backend/analyze_product.py --batch-all --max-workers 5 --sandbox-image linux
```

`--batch` 可重复指定,按命令行顺序合并为一条队列。输出目录按来源队列分类;`--batch-all` 会保留每个 `queue*.json` 的分类。

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

### 一键启动前后端

```bash
cd web
npm install
npm run dev:all
```

`dev:all` 通过 `concurrently` 同时启动:
- **后端** FastAPI (`backend/start_server.py`) → `http://127.0.0.1:8765`
- **前端** Vite dev server → `http://127.0.0.1:5173`

前端代理 `/api/*` 到后端,零配置即可联调。

### 分别启动

后端:

```bash
python3 backend/analyzer_server.py
# 或
python3 backend/start_server.py --port 8765 --reload
```

前端:

```bash
cd web
npm run dev
```

### 控制台能力

- **新建分析任务** - 表单验证（产品名长度、URL 格式）。
- **任务列表** - 搜索、筛选（全部/运行中/已完成/失败）、状态徽章。
- **Workflow 步骤可视化** - 进度条、步骤连接线、状态图标、可展开详情。
- **实时日志** - WebSocket 推送,日志级别筛选（All/Info/Warn/Error）、自动滚动、复制/下载。
- **截图画廊** - 网格/列表视图、Lightbox 全屏预览、键盘导航（←→Esc）。
- **最终报告渲染** - Markdown 渲染（标题、列表、代码块、表格、图片）、目录导航（TOC）、导出/打印。
- **Credential 处理** - 动态字段表单、字段验证、加密保存。
- **暗色/亮色主题** - 一键切换、`localStorage` 持久化、系统偏好自动检测。

### 前端技术栈

| 技术 | 版本 | 用途 |
|---|---|---|
| React | ^19.0.0 | UI 框架 |
| Vite | ^6.0.0 | 构建工具 |
| Tailwind CSS | ^4.3.0 | 原子化样式 + 暗色/亮色主题 |
| react-markdown | ^10.1.0 | Markdown 报告渲染 |
| remark-gfm | ^4.0.1 | GitHub Flavored Markdown 支持 |
| lucide-react | ^0.468.0 | 图标库 |

### 后端 API 端点

| 端点 | 方法 | 说明 |
|---|---|---|
| `/api/runs` | GET | 列出所有分析任务。 |
| `/api/runs` | POST | 创建新任务（后台线程启动）。 |
| `/api/runs/{run_id}` | GET | 获取任务详情（metadata + workflow）。 |
| `/api/runs/{run_id}/steps/{step_file}` | GET | 获取步骤文件内容。 |
| `/api/runs/{run_id}/report` | GET | 获取最终报告 Markdown。 |
| `/api/runs/{run_id}/screenshots` | GET | **新增**：列出截图文件列表。 |
| `/api/runs/{run_id}/screenshots/{name}` | GET | 获取单张截图图片。 |
| `/api/runs/{run_id}/credentials` | POST | 提交 credential。 |
| `/api/runs/{run_id}/stream` | WS | WebSocket 实时日志推送。 |

CORS 源可通过环境变量配置：`ANALYZER_CORS_ORIGINS=http://localhost:3000,http://localhost:5173`

### 前端分层

| 目录 | 作用 |
|---|---|
| `web/src/pages/` | 页面级组合。 |
| `web/src/components/` | 可复用面板和控件。 |
| `web/src/hooks/` | 数据加载、轮询、WebSocket hooks。 |
| `web/src/api.ts` | 后端 API 封装。 |
| `web/src/types.ts` | 共享类型。 |
| `web/docs/` | UI/UX 设计文档。 |

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

一键启动验证:

```bash
cd web
npm run dev:all
# 浏览器打开 http://127.0.0.1:5173
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
- `web/docs/`（设计文档，可选手动提交）

---

## 退出码

| 码 | 含义 |
|---|---|
| `0` | 成功。 |
| `1` | 预检失败、用户中断、恢复任务缺 session。 |
| `2` | Claude 子进程非零退出。 |
| `130` | Ctrl+C 或 ESC 后放弃续跑。 |
