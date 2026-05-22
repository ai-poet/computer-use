# Paseo 产品分析报告

| 项目 | 值 |
|---|---|
| 官网 | https://github.com/getpaseo/paseo |
| 下载链接 | https://github.com/getpaseo/paseo/releases |
| 报告日期 | 2026-05-22 |
| 主机 | linux / x86_64 |
| Runtime | sandbox-local |
| 模式 | sandbox-full |
| 用时 | ~25 分钟 |

---

## 1. 详细的产品逻辑介绍

### 1.1 总定位

Paseo 是一款自托管的 coding agent 编排平台，通过统一的界面将 Claude Code、Codex、Copilot、OpenCode、Pi 等多种 AI 编程助手整合到同一工作流中。用户在本地运行 daemon 服务，agents 直接操作用户的实际开发环境（文件系统、工具链、配置），而非隔离沙盒。产品支持桌面端（Electron）、移动端（iOS/Android via Expo）、Web 端和 CLI 四种客户端形态，强调跨设备无缝衔接与隐私优先（无遥测、无追踪、无强制登录）。

### 1.2 界面清单

按出现顺序列出实际看到的所有主要界面：

| # | 界面 | 入口 | 主要功能 | 截图 |
|---|---|---|---|---|
| 1 | GitHub 仓库首页 | https://github.com/getpaseo/paseo | 产品信息、README、releases | [01_web_homepage.png](screenshots/01_web_homepage.png) |
| 2 | README 产品描述 | 首页向下滚动 | 核心定位与产品截图 | [03_web_readme_content.png](screenshots/03_web_readme_content.png) |
| 3 | README 功能列表 | 继续滚动 | 五大卖点详细介绍 | [04_web_readme_features.png](screenshots/04_web_readme_features.png) |
| 4 | README 快速开始 | 继续滚动 | CLI 安装与使用方式 | [05_web_readme_getting_started.png](screenshots/05_web_readme_getting_started.png) |
| 5 | README 架构与 Skills | 继续滚动 | monorepo 结构、skills 命令 | [06_web_readme_cli.png](screenshots/06_web_readme_cli.png) |
| 6 | Releases 页面 | 右侧栏 Releases 链接 | 全平台安装包下载 | [13_web_releases_assets_all.png](screenshots/13_web_releases_assets_all.png) |
| 7 | 桌面应用主界面 | 启动后默认窗口 | Sessions 管理、项目入口 | [14_app_main.png](screenshots/14_app_main.png) |
| 8 | Settings General | 点击设置齿轮 | Daemon 状态、连接、工具开关 | [18_app_setup_providers.png](screenshots/18_app_setup_providers.png) |
| 9 | Settings Integrations | 左侧菜单 | CLI 与 orchestration skills | [20_app_integrations.png](screenshots/20_app_integrations.png) |
| 10 | Settings Projects | 左侧菜单 | 项目列表管理 | [24_app_projects.png](screenshots/24_app_projects.png) |
| 11 | Settings About | 左侧菜单 | 版本、更新通道、检查更新 | [25_app_about.png](screenshots/25_app_about.png) |
| 12 | Web 应用 | https://app.paseo.sh | 与桌面端相同的 web 版本 | [29_web_app_paseo.png](screenshots/29_web_app_paseo.png) |

### 1.3 各界面功能与评价

#### 1.3.1 GitHub 仓库首页

- **功能**: 产品官网（以 GitHub 仓库为载体），展示 Stars(6.5k)、Forks(611)、最近提交活跃度（数小时前仍有提交）。右侧 About 栏概括产品定位。
- **交互**: 通过 Code/Issues/Pull requests 等 tab 切换，右侧 Releases 入口直达安装包。
- **评价**: 以 GitHub 作为官网减少了维护成本，但对非技术用户不够友好。Issues 348 条、PR 89 条显示社区活跃度较高。
- **截图**:[01_web_homepage.png](screenshots/01_web_homepage.png)

#### 1.3.2 README 功能列表

- **功能**: 列出五大核心卖点 — Self-hosted、Multi-provider、Voice control、Cross-device、Privacy-first。附一张桌面端+手机端的组合截图。
- **交互**: 纯文本阅读，无交互。
- **评价**: 卖点表述具体可验证（如"Privacy-first: Paseo doesn't have any telemetry, tracking, or forced log-ins"）。Cross-device 明确列出 iOS/Android/desktop/web/CLI 五种形态。
- **截图**:[04_web_readme_features.png](screenshots/04_web_readme_features.png)

#### 1.3.3 README 架构说明

- **功能**: 揭示 monorepo 结构 — packages/server（daemon）、packages/app（Expo 移动/Web 客户端）、packages/cli（命令行）、packages/desktop（Electron 桌面端）、packages/relay（远程连接）。同时介绍 skills 系统：/paseo-handoff、/paseo-loop、/paseo-advisor、/paseo-committee。
- **评价**: 架构清晰，server-client 分离设计使得"自托管"成为可能 — daemon 运行在用户机器上，各客户端通过网络连接。
- **截图**:[06_web_readme_cli.png](screenshots/06_web_readme_cli.png)

#### 1.3.4 Releases 页面

- **功能**: 提供 v0.1.80（2026-05-21）及历史版本的全平台安装包。Assets 共 26 个，覆盖 Linux(.deb/.AppImage/.rpm)、macOS(.dmg/.zip)、Windows(.zip) 三大平台双架构(x64/arm64)。
- **评价**: 发布节奏快（6 小时前刚发版），平台覆盖全面。Linux 同时提供 .deb、.AppImage、.rpm 三种格式，对不同发行版用户友好。
- **截图**:[13_web_releases_assets_all.png](screenshots/13_web_releases_assets_all.png)

#### 1.3.5 桌面应用主界面

- **功能**: 左侧 Sessions 栏显示项目列表（初始为空，提示"No projects yet"）。右侧四个入口卡片：Add a project（打开本地文件夹）、Import session（导入 CLI 会话）、Setup providers（配置 Claude Code/Codex 等）、Pair device（手机扫码连接 daemon）。
- **交互**: 点击卡片进入对应功能；左侧 + Add project 可新建项目。
- **评价**: 首屏信息架构简洁，四个入口覆盖了产品核心使用路径。但"Setup providers"文案不够直观 — 首次用户可能不理解这是配置 AI 提供商的意思。
- **截图**:[14_app_main.png](screenshots/14_app_main.png)

#### 1.3.6 Settings General

- **功能**: 展示当前 daemon 状态（Online、localhost:6767、v0.1.80）、TCP 连接延迟。提供 Enable Paseo tools（agents 管理 worktree/schedule）、System prompt（全局系统提示词）、Pair a device（QR 码配对）、Manage built-in daemon 开关。
- **交互**: 左侧设置菜单切换子页面，右侧开关/按钮操作。
- **评价**: 将 daemon 状态放在 General 页首屏是合理的设计决策 — 用户首先需要确认后端服务是否正常运行。Pair device 的 QR 码简化了手机连接流程。
- **截图**:[18_app_setup_providers.png](screenshots/18_app_setup_providers.png)

#### 1.3.7 Settings Integrations

- **功能**: 两个入口 — Command line（从终端控制和脚本化 agents）、Orchestration skills（通过 CLI 教 agents 编排）。
- **评价**: 入口较少，主要是 CLI 能力的引导。与 GitHub README 中详细的 skills 文档形成互补。
- **截图**:[20_app_integrations.png](screenshots/20_app_integrations.png)

#### 1.3.8 Settings Projects

- **功能**: 项目列表页，当前为空状态"No projects yet"。
- **评价**: 空状态页面过于简单，缺少引导用户创建第一个项目的 CTA 按钮。
- **截图**:[24_app_projects.png](screenshots/24_app_projects.png)

#### 1.3.9 Settings About

- **功能**: 显示版本信息、Release channel（Stable/Beta 切换）、App updates（检查更新按钮）。
- **评价**: 标准的关于页面。Release channel 允许用户提前体验 Beta 功能，对早期采纳者友好。
- **截图**:[25_app_about.png](screenshots/25_app_about.png)

---

## 2. UI/UX 风格和质量描述

### 2.1 视觉风格

整体采用极简的灰白配色方案，以浅灰背景(#f5f5f5)和纯白内容区为主，辅以深灰文字和少量品牌色点缀。图标风格为线性图标（outline style），线条纤细。品牌 logo 是一个抽象的蝴蝶/翅膀图形，线条流畅。整体调性偏向开发者工具风格 — 克制、功能导向，没有过多装饰元素。

### 2.2 信息密度与层级

首屏（桌面应用主界面）信息量控制得当：左侧 1/4 为 Sessions 导航栏，右侧 3/4 为四个等大的入口卡片，居中排列。主要 CTA（Add a project）位于左上卡片，视觉权重与其他卡片相同，没有特别突出 — 这可能是因为四个入口代表了不同的使用路径，产品希望用户根据需求自选而非强制引导某一路径。

Settings 页面采用经典的左侧导航+右侧内容布局，菜单项文字简洁（General/Projects/Shortcuts/Integrations/Permissions/Diagnostics/About），信息层级清晰。

### 2.3 交互流畅度

- **启动速度**: Electron 应用在沙盒内启动约 4-5 秒出现首屏，有加载动画（品牌 logo 转圈）。
- **页面切换**: Settings 内各子页面切换无明显延迟，约 200-300ms。
- **反馈**: 按钮 hover 有轻微的背景色变化（灰→更浅的灰），但没有明确的 press 态或加载指示器（如开关 toggle 无动画）。

### 2.4 文案质量

官网（GitHub README）与应用内文案保持一致，均使用英文。README 文案精炼，专业术语与口语化表达平衡得当（如"Ship from your phone or your desk"）。应用内文案偏功能性，如"Configure Claude Code, Codex, and more"直接说明了 Setup providers 的用途。无明显机翻痕迹。

### 2.5 可访问性观察

- **对比度**: 主要文字（深灰 #333 类）在白色背景上对比度足够，满足 WCAG AA。
- **键盘可达性**: 未专门测试键盘导航路径，但 Electron 应用通常支持标准 Tab 焦点切换。
- **深色模式**: 未在截图中观察到深色模式开关或自动跟随系统的证据。
- **字号**: 应用内字号偏小（约 13-14px），对视力不佳的用户可能不够友好。

---

## 3. 官网描述

### 3.1 关键文案摘录

> "Orchestrate coding agents remotely from your phone, desktop and CLI" — GitHub 仓库 About 栏

> "One interface for Claude Code, Codex, Copilot, OpenCode, and Pi agents." — README H1 下方

> "Self-hosted: Agents run on your machine with your full dev environment. Use your tools, your configs, and your skills." — README 功能列表

> "Privacy-first: Paseo doesn't have any telemetry, tracking, or forced log-ins." — README 功能列表

> "Paseo runs a local server called the daemon that manages your coding agents. Clients like the desktop app, mobile app, web app, and CLI connect to it." — README Getting Started

### 3.2 核心卖点（官网视角）

1. **多提供商统一界面** — 一个入口管理 Claude Code、Codex、Copilot、OpenCode、Pi（原文锚：README H1 下方）
2. **自托管隐私优先** — agents 在用户本地运行，无遥测无追踪（原文锚：README 功能列表）
3. **跨设备无缝衔接** — 手机、桌面、Web、CLI 四种客户端连接同一 daemon（原文锚：README Getting Started）
4. **语音控制** — 支持语音模式 dictation（原文锚：README 功能列表）
5. **Agent 编排 skills** — handoff、loop、advisor、committee 四种协作模式（原文锚：README Development 节）

### 3.3 与实际体验的差距

| 卖点 | 官网原文 | 实际体验 | 差距 |
|---|---|---|---|
| 多提供商支持 | "Claude Code, Codex, Copilot, OpenCode, and Pi" | Settings Integrations 页仅见 Command line 和 Orchestration skills 两个入口，未直接展示 providers 配置界面 | 实际 providers 配置可能隐藏在更深层菜单或首次使用向导中，当前空状态未暴露 |
| Voice control | "Dictate tasks or talk through problems in voice mode" | 桌面应用界面未找到语音输入按钮或语音模式切换入口 | 可能是移动端专属功能，或需要项目创建后才显示 |

---

## 4. 定价

未在官网、README 或应用内发现任何定价信息。GitHub 仓库为 Public 开源项目，Releases 页面提供免费的安装包下载。推测当前为完全免费的开源产品，暂无商业化定价策略。

---

## 5. 目标用户

基于官网用语与实际功能推断：

- **核心用户**: 专业软件开发者，尤其是同时使用多种 AI coding 工具（Claude Code + Codex + Copilot 等）的高级用户
- **次要用户**: 需要在移动端（手机）远程监控/干预 coding agent 执行的技术人员
- **排除用户**: 非技术背景用户 — GitHub 作为官网、CLI 安装方式、"daemon""worktree"等术语都设置了较高的使用门槛

---

## 6. 与同类产品对比

| 维度 | Paseo | Claude Code (官方) | GitHub Copilot |
|---|---|---|---|
| **多 agent 编排** | 核心能力，支持 5+ 提供商 | 单 agent，无编排 | 单 agent，IDE 插件形式 |
| **自托管** | 是，daemon 运行在用户机器 | 是，CLI 工具 | 否，云端服务 |
| **跨设备** | 桌面+移动+Web+CLI | CLI + IDE 集成 | IDE + Web |
| **移动端** | 原生 iOS/Android 应用 | 无 | 无 |
| **语音控制** | 支持 | 不支持 | 不支持 |

Paseo 的差异化在于"编排" — 不是替代某个单一 agent，而是让用户在不同任务阶段切换最优 agent（如规划用 Claude、实现用 Codex），并通过 skills 实现 agent 间协作。

---

## 7. 优劣势小结

| 维度 | 优势 | 劣势 |
|---|---|---|
| 产品逻辑 | 多 agent 编排是独特定位；自托管确保隐私和数据主权 | 空状态引导不足；providers 配置入口不够直观 |
| UI/UX | 界面简洁克制；跨客户端体验一致（Web/桌面几乎相同） | 无深色模式；字号偏小；开关 toggle 无动画反馈 |
| 工程质量 | 开源、社区活跃（6.5k stars）、发布节奏快（6 小时前刚更新） | 以 GitHub 为官网对非技术用户不友好；Electron 桌面端在沙盒内启动需 --no-sandbox 参数 |

---

## 附录 A 截图索引

| # | 文件 | 说明 |
|---|---|---|
| 01 | screenshots/01_web_homepage.png | GitHub 仓库首页 |
| 03 | screenshots/03_web_readme_content.png | README 产品核心描述与截图 |
| 04 | screenshots/04_web_readme_features.png | README 五大功能卖点 |
| 05 | screenshots/05_web_readme_getting_started.png | README CLI 安装说明 |
| 06 | screenshots/06_web_readme_cli.png | README monorepo 结构与 skills |
| 13 | screenshots/13_web_releases_assets_all.png | Releases 全平台安装包列表 |
| 14 | screenshots/14_app_main.png | 桌面应用主界面（初始状态）|
| 18 | screenshots/18_app_setup_providers.png | Settings General 页（daemon 状态）|
| 20 | screenshots/20_app_integrations.png | Settings Integrations 页 |
| 24 | screenshots/24_app_projects.png | Settings Projects 页 |
| 25 | screenshots/25_app_about.png | Settings About 页 |
| 29 | screenshots/29_web_app_paseo.png | Web 版应用界面 |

> 编号规则: `NN_<source>_<view>.png`，web=浏览器截图，app=桌面应用截图；NN 单调递增，允许跳号。