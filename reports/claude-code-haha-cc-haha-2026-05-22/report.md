# Claude Code Haha (cc-haha) 产品分析报告

| 项目 | 值 |
|---|---|
| 官网 | https://github.com/NanmiCoder/cc-haha |
| 下载链接 | https://github.com/NanmiCoder/cc-haha/releases |
| 报告日期 | 2026-05-22 |
| 主机 | linux / x86_64 |
| Runtime | sandbox-local |
| 模式 | sandbox-full |
| 用时 | 30 分钟 |

---

## 1. 详细的产品逻辑介绍

### 1.1 总定位

Claude Code Haha 是一款基于 2026-03-31 从 Anthropic npm registry 泄露的 Claude Code 源码修复而来的桌面端 AI 编程助手工作台。它将多会话管理、Git 分支/Worktree 操作、代码 Diff 查看、权限审批、多模型提供商配置、Computer Use 桌面控制、IM 远程接入和定时任务等功能，集中到一个基于 Tauri 2 + React 构建的跨平台图形化客户端中（支持 macOS、Windows、Linux）。目标用户是不想长期停留在终端里、偏好图形界面进行 AI 辅助开发的工程师。

### 1.2 界面清单

按出现顺序列出实际看到的所有主要界面：

| # | 界面 | 入口 | 主要功能 | 截图 |
|---|---|---|---|---|
| 1 | GitHub 仓库首页 | https://github.com/NanmiCoder/cc-haha | 项目介绍、README、功能预览、下载入口 | [01_web_homepage.png](screenshots/01_web_homepage.png) |
| 2 | README 页面 | 仓库首页下滚动 | 桌面端预览、功能亮点、文档索引 | [22_web_readme_full.png](screenshots/22_web_readme_full.png) |
| 3 | 桌面端亮点 | README 内锚点 | 8 大功能模块截图与文字说明 | [23_web_readme_features.png](screenshots/23_web_readme_features.png) |
| 4 | 功能列表 | README 底部 | 多 Agent、Skills、IM、Computer Use 等文档链接 | [25_web_readme_highlights.png](screenshots/25_web_readme_highlights.png) |
| 5 | Releases 页面 | GitHub 右侧栏 Releases | 版本发布记录、Assets 下载 | [08_web_releases_page.png](screenshots/08_web_releases_page.png) |
| 6 | Release Assets | Releases 页底部 | 各平台安装包（.deb/.dmg/.app） | [12_web_release_bottom.png](screenshots/12_web_release_bottom.png) |
| 7 | 应用主界面（新建会话） | 启动后默认窗口 | 新建编码会话、模型选择、权限设置 | [05_app_main.png](screenshots/05_app_main.png) |

### 1.3 各界面功能与评价

#### 1.3.1 GitHub 仓库首页

- **功能**: 展示项目基本信息（11.5k stars、8k forks、212 issues、29 PRs）、About 描述、文件目录结构、README 内容、右侧栏（Releases、Packages、Contributors、Languages）
- **交互**: 通过 GitHub 标准导航进入 Code/Issues/Pull requests/Actions 等标签页；右侧 Releases 可进入下载页
- **评价**: 项目活跃度较高（v0.2.9 在 10 小时内发布），有 14 位贡献者。README 结构清晰，用中文撰写，包含桌面端预览截图网格。但项目基于泄露源码，License 为自定义教育研究用途，存在法律合规风险。
- **截图**: [01_web_homepage.png](screenshots/01_web_homepage.png)

#### 1.3.2 README — 桌面端预览

- **功能**: 展示 8 张桌面端功能截图（桌面端工作台、右侧代码改动 & Worktree、代码编辑 & Diff 视图、权限控制 & AI 提问、HS 远程访问、Token 用量统计、Computer Use、定时任务），每张图配简短说明
- **交互**: 截图不可点击放大，纯静态展示。上方有"下载桌面版 | MACOS | WINDOWS | 实验功能 | GUIDE"按钮组
- **评价**: 预览图采用 4×2 网格布局，直观展示了产品核心能力。但截图分辨率较小，无法看清具体 UI 细节。"桌面端亮点"部分以 bullet list 补充了文字说明，弥补了截图信息量的不足。
- **截图**: [23_web_readme_features.png](screenshots/23_web_readme_features.png)

#### 1.3.3 README — 功能亮点列表

- **功能**: 详细列出 7 大桌面端亮点：多会话工作台、分支/Worktree 启动、右侧代码改动面板、代码修改可视化、权限与确认流、多模型提供商、Computer Use、HS 远程访问、IM 接入、定时任务与用量统计
- **交互**: 纯文本阅读，下方"更多文档"表格提供各子系统的文档链接（环境变量、非官方模型、贡献与质量门禁、记忆系统、多 Agent 系统、Skills 系统、IM 接入、Computer Use、桌面端、全局使用、常见问题、源码修复记录、项目结构）
- **评价**: 功能覆盖全面，从核心编码辅助到周边生态（IM 集成、远程访问、定时任务）均有涉及。文档链接丰富，对开发者友好。但部分功能（如 IM 接入、多 Agent 系统）缺少截图或演示，只能依赖文字描述理解。
- **截图**: [25_web_readme_highlights.png](screenshots/25_web_readme_highlights.png)

#### 1.3.4 Releases 页面与 Assets

- **功能**: 展示版本发布历史（共 20 个 releases），最新 v0.2.9 包含 15 个 assets：linux_arm64_deb、linux_x64_deb、macos_arm64_app/dmg、macos_x64_app/dmg 及对应 .sig 签名文件，外加 Source code (zip/tar.gz)
- **交互**: 点击 asset 链接直接下载；macOS 用户需执行 `xattr -cr` 处理 Gatekeeper
- **评价**: 发布节奏频繁（v0.2.9 距上一版本时间很短），提供多架构支持（arm64/x64）和多格式（.deb/.app/.dmg）。每个 asset 附 sha256 校验和与 .sig 签名文件，安全性考虑到位。但缺少 Windows 安装包（只有 macOS 和 Linux）。
- **截图**: [08_web_releases_page.png](screenshots/08_web_release_page.png)、[12_web_release_bottom.png](screenshots/12_web_release_bottom.png)

#### 1.3.5 桌面应用 — 新建会话界面

- **功能**: 应用启动后的默认界面。左侧边栏包含：Claude Code Haha Logo、GitHub 链接、"+ 新建会话"、"定时任务"、搜索框、设置入口。主区域显示"新建会话"标题、说明文字（"开始一个新的编码会话。Claude 已准备好帮你构建、调试和架构你的项目。"）、输入框（"随便问点什么..."）、底部工具栏（"+"附件按钮、"询问权限"下拉、模型选择器"Opus 4.7 Claude 官方"、"运行"按钮、"选择项目..."按钮）
- **交互**: 通过左侧边栏切换功能模块；输入框可输入自然语言指令；模型选择器可切换提供商和模型；权限下拉可配置工具调用审批策略
- **评价**: 界面布局简洁，左侧导航 + 右侧主内容区的经典 IDE 式布局。中文 UI 完整，术语统一（"会话"、"权限"、"运行"）。但 sandbox 内鼠标点击未能在应用内触发交互（Electron 自定义渲染层与 sandbox 鼠标坐标存在兼容性问题），无法验证下拉菜单、按钮点击的实际响应。应用启动速度正常（约 3-5 秒出现窗口）。
- **截图**: [05_app_main.png](screenshots/05_app_main.png)

---

## 2. UI/UX 风格和质量描述

### 2.1 视觉风格

整体采用现代 IDE 风格的浅灰色主题，左侧边栏为浅灰底色，主内容区为白色。Logo 为蓝紫渐变的"CC"字母组合带 sparkle 装饰，辨识度高。字体使用系统默认无衬线字体，中文显示清晰。图标风格为扁平化线条图标（设置齿轮、搜索放大镜、时钟等）。整体调性偏向开发者工具，简洁专业，无多余装饰。

### 2.2 信息密度与层级

首屏（新建会话界面）信息密度适中：大标题"新建会话"占据视觉中心，下方说明文字和输入框层次分明。底部工具栏将模型选择、权限配置、运行按钮集中在一行，主次分明。左侧边栏功能入口精简（仅 4-5 个主要项），不干扰主内容区。但"选择项目..."按钮位于输入框下方偏右，首次使用时可能被忽略。

### 2.3 交互流畅度

- **启动到首屏**: 在 sandbox Linux 环境下，从命令行启动到窗口完全渲染约 3-5 秒，符合 Electron/Tauri 应用的常规水平
- **关键操作**: 由于 sandbox 鼠标坐标与 Electron 应用存在兼容性问题，无法验证点击、下拉等交互的响应速度。键盘输入（type）也未能在输入框中生效
- **反馈**: 静态截图显示按钮有 hover 态（如"运行"按钮为浅粉色填充），但无法验证动态反馈

### 2.4 文案质量

官网（GitHub README）与应用内文案均为简体中文，术语统一：
- "会话"对应 conversation/session
- "权限"对应 permission/approval
- "提供商"对应 provider
- "定时任务"对应 scheduled tasks

无明显的机翻痕迹，技术术语使用准确。README 中部分英文（如"Computer Use"、"Worktree"、"Context Compact"）保持原词不翻译，符合开发者习惯。

### 2.5 可访问性观察（肉眼可见的）

- **对比度**: 主文字（深灰/黑色）与白色背景的对比度足够；次要文字（浅灰"暂无会话"）对比度偏低
- **键盘可达性**: 无法验证（sandbox 内 Tab 导航未测试）
- **深色模式**: 截图中未观察到深色模式切换入口
- **字号**: 默认字号适中，未观察到字号调节入口

---

## 3. 官网描述

### 3.1 关键文案摘录

> "Claude Code Haha 基于 2026-03-31 从 Anthropic npm registry 泄露的 Claude Code 源码修复而来，现在主要是一个桌面端 Claude Code 工作台：把会话、多项目、分支 / Worktree、右侧代码改动、代码 Diff、权限审批、模型提供商、Computer Use、HS 远程访问、IM 接入和定时任务集中到一个 macOS / Windows APP 里。"
> —— README 首段，原文锚：首页 H1 下方第一段

> "Claude Code Haha 的桌面端把会话、多项目、分支 / Worktree、右侧代码改动、代码 Diff、权限确认、提供商配置和远程入口集中到一个图形化工作台里，适合不想长期停留在终端里的日常开发工作流。"
> —— "桌面端预览"章节

> "本项目由个人利用业余时间维护，欢迎企业或个人赞助支持持续开发，也可洽谈定制、集成或商务合作。"
> —— "赞助与合作"章节

### 3.2 核心卖点（官网视角）

1. **基于泄露源码修复的本地化 Claude Code** —— 在本地运行，无需依赖 Anthropic 官方服务（原文锚：README 首段）
2. **图形化桌面工作台** —— 替代终端操作，适合偏好 GUI 的开发者（原文锚：桌面端预览）
3. **多模型提供商支持** —— 不仅限于 Claude，支持 OpenAI、DeepSeek、Ollama 等（原文锚：桌面端亮点 / 非官方模型文档）
4. **Computer Use 桌面控制** —— Agent 可截图、点击、输入控制桌面应用（原文锚：桌面端亮点）
5. **IM 远程接入** —— 通过 Telegram/飞书/微信/钉钉远程对话和审批（原文锚：桌面端亮点）
6. **多会话 + Worktree 管理** —— 标签页、分支切换、终端入口集中管理（原文锚：桌面端亮点）

### 3.3 与实际体验的差距

| 卖点 | 官网原文 | 实际体验 | 差距 |
|---|---|---|---|
| 跨平台支持 | "macOS / Windows APP" | 实际 Releases 提供 linux_arm64_deb、linux_x64_deb、macos_arm64_app/dmg、macos_x64_app/dmg | 官网未明确提及 Linux 支持，但 Releases 中实际提供了 Linux .deb 包 |
| Windows 支持 | 桌面端标签显示 "MACOS \| WINDOWS" | Releases 中未找到 Windows .exe/.msi 安装包 | 存在差距：官网暗示支持 Windows，但当前 release 未提供 Windows 安装包 |
| 交互流畅度 | 截图展示丰富的功能界面 | Sandbox 内鼠标/键盘无法与应用交互（Electron 渲染层兼容性问题） | 无法验证实际交互体验 |

---

## 4. 定价

本项目为开源免费软件，无定价页面。README 中设有"赞助与合作"章节，接受个人或企业赞助以支持持续开发，同时提供定制、集成和商务合作服务。无订阅制、无功能分级。

---

## 5. 目标用户

基于官网用语和实际功能推断：

1. **终端厌倦型开发者** —— "适合不想长期停留在终端里的日常开发工作流"（原文锚：桌面端预览）
2. **多模型需求用户** —— 需要同时使用 Claude、OpenAI、DeepSeek、Ollama 等不同模型提供商的开发者
3. **远程协作需求团队** —— 需要通过 IM（Telegram/飞书/微信/钉钉）远程接入 AI 会话并进行审批的团队
4. **AI Agent 研究者** —— 项目基于 Claude Code 泄露源码，对 Agent 架构、工具调用、MCP 集成有研究兴趣的开发者（README 明确说明"用于教育和研究目的"）

---

## 6. 与同类产品对比

| 维度 | Claude Code Haha | 官方 Claude Code (Anthropic) | Cursor |
|---|---|---|---|
| **运行方式** | 本地桌面应用（Tauri），可自建后端 | 终端 CLI 工具，依赖 Anthropic 云服务 | VS Code 插件/独立 IDE |
| **源码性质** | 基于泄露源码，自定义 License（教育研究-only） | 官方闭源产品 | 商业闭源产品 |
| **模型支持** | 多提供商（Claude、OpenAI、DeepSeek、Ollama 等） | 仅 Anthropic 模型 | 多提供商 + 自有模型 |
| **UI 形式** | 独立桌面 GUI（Tauri + React） | 纯终端 TUI | 基于 VS Code 的编辑器 |
| **IM 集成** | 支持 Telegram/飞书/微信/钉钉远程接入 | 不支持 | 不支持 |
| **Computer Use** | 支持桌面控制（截图、鼠标、键盘） | 支持（官方实现） | 不支持 |
| **合法性/风险** | 高法律风险（基于泄露源码，限制商业使用） | 完全合法 | 完全合法 |

---

## 7. 优劣势小结

| 维度 | 优势 | 劣势 |
|---|---|---|
| 产品逻辑 | 功能全面（多会话、Worktree、Diff、权限、Computer Use、IM、定时任务）；多模型提供商支持 | 基于泄露源码，法律风险高；License 限制商业使用；Windows 安装包缺失 |
| UI/UX | 中文 UI 完整；IDE 式布局直观；截图展示的功能界面丰富 | Sandbox 内无法验证实际交互；部分功能无截图/演示（IM 配置、多 Agent 编排） |
| 工程质量 | 发布节奏快（v0.2.9 距上一版很短）；多架构/多格式构建完整；附签名和校验和 | 依赖 leaked source 的伦理和法律问题；个人业余维护，长期可持续性存疑 |

---

## 附录 A 截图索引

| # | 文件 | 说明 |
|---|---|---|
| 01 | screenshots/01_web_homepage.png | GitHub 仓库首页，展示项目基本信息和文件目录 |
| 05 | screenshots/05_app_main.png | 桌面应用主界面（新建会话），左侧边栏 + 输入区 + 工具栏 |
| 08 | screenshots/08_web_releases_page.png | GitHub Releases 页面，展示 v0.2.9 发布信息 |
| 12 | screenshots/12_web_release_bottom.png | Release Assets 列表，展示各平台安装包下载链接 |
| 22 | screenshots/22_web_readme_full.png | README 顶部，展示项目标题、描述和徽章 |
| 23 | screenshots/23_web_readme_features.png | 桌面端预览区，8 张功能截图网格 |
| 25 | screenshots/25_web_readme_highlights.png | 桌面端亮点列表和更多文档索引 |
