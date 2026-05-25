# AionUi 产品分析报告

| 项目 | 值 |
|---|---|
| 官网 | https://aionui.com |
| 下载链接 | https://aionui.com/download/ |
| 报告日期 | 2026-05-22 |
| 主机 | linux / x86_64 |
| Runtime | sandbox-local |
| 模式 | sandbox-full |
| 用时 | ~25 分钟 |

---

## 1. 详细的产品逻辑介绍

### 1.1 总定位

AionUi 是一款开源（Apache-2.0 License）的桌面级 AI 多代理协作平台。它将 Claude Code、Codex、Gemini CLI、Goose 等 20 余种 AI 开发工具整合到统一的本地桌面工作区中，让用户可以在一个界面内并行调度多个 AI 代理、分配任务、设置定时自动化，并通过 Telegram/WeChat/Lark/DingTalk 等渠道远程控制。产品 slogan 为 "One desktop. Your AI agents, actually writing code..."，核心解决的是"多 AI 工具碎片化"问题 —— 开发者不再需要切换多个终端或 IDE 插件来调用不同的 AI 能力。

### 1.2 界面清单

按出现顺序列出实际看到的所有主要界面：

| # | 界面 | 入口 | 主要功能 | 截图 |
|---|---|---|---|---|
| 1 | 官网首页 | https://aionui.com | 产品定位、功能预览、下载入口 | [01_web_homepage.png](screenshots/01_web_homepage.png) |
| 2 | 首页-Stella 演示 | 首页滚动 | AI 助手图像处理演示 | [02_web_homepage_scroll1.png](screenshots/02_web_homepage_scroll1.png) |
| 3 | 首页-Multi-Agent Cowork | 首页滚动 | 多代理协作任务板展示 | [03_web_homepage_scroll2.png](screenshots/03_web_homepage_scroll2.png) |
| 4 | Cowork 页面 | 导航栏 Cowork | 多代理并行工作说明 | [06_web_cowork.png](screenshots/06_web_cowork.png) |
| 5 | Assistants 页面 | 导航栏 Assistants | 20+ 内置 AI 助手展示 | [07_web_assistants.png](screenshots/07_web_assistants.png) |
| 6 | Remote 页面 | 导航栏 Remote | 远程控制渠道说明 | [08_web_remote.png](screenshots/08_web_remote.png) |
| 7 | Automation 页面 | 导航栏 Automation | 定时任务/cron 自动化说明 | [09_web_automation.png](screenshots/09_web_automation.png) |
| 8 | Download 页面 | 导航栏 Download | 全平台安装包下载 | [12_web_download.png](screenshots/12_web_download.png) |
| 9 | Linux 下载区 | Download 页面滚动 | Linux .deb 安装包选项 | [14_web_download_linux.png](screenshots/14_web_download_linux.png) |
| 10 | 安装方法页 | Download 页面滚动 | Homebrew/Winget/curl 安装 | [30_web_install_methods.png](screenshots/30_web_install_methods.png) |
| 11 | 系统要求页 | Download 页面滚动 | 各平台最低配置 | [31_web_sysreq.png](screenshots/31_web_sysreq.png) |
| 12 | Footer | 首页底部 | 版权、社区链接 | [32_web_footer.png](screenshots/32_web_footer.png) |
| 13 | 应用主界面 | 启动 AionUi 后 | 聊天、助手选择、快捷功能 | [17_app_main.png](screenshots/17_app_main.png) |

### 1.3 各界面功能与评价

#### 1.3.1 官网首页

- **功能**:首屏展示产品核心定位（"One desktop. Your AI agents, actually writing code..."），配有 GitHub Trending "#1 Repository Of The Day" 徽章（26.1k stars）。首屏 CTA 为 "Download for Linux" 黑色圆角按钮。下方依次展示：AI 助手实时协作演示（Stella 处理图片）、Multi-Agent Cowork 任务板、Assistants 网格、Remote 控制、Automation 定时任务等功能区块。
- **交互**:单页滚动式布局，导航栏固定顶部，点击锚点平滑滚动到对应区块。Cowork/Assistants/Remote/Automation/Skills 五个主导航入口。
- **评价**:信息层级清晰，首屏在 1024×768 分辨率下能完整展示 slogan + CTA + 产品截图，没有信息过载。但 Skills 导航点击后未跳转独立页面（与 Automation 同页），存在导航一致性瑕疵。
- **截图**:[01_web_homepage.png](screenshots/01_web_homepage.png)

#### 1.3.2 Stella 助手演示区

- **功能**:展示 AionUi 中名为 "Stella · UI/UX Designer" 的助手处理产品图片的完整流程：检测主体（headphones, confidence 98.2%）→ 去除背景（edge refinement applied）→ 应用渐变（#e8eeff → #f0e8ff → #ffe8f0）→ 添加投影（12px blur, 15% opacity）→ 输出 1920×1440 PNG。底部有 "Send message to Stella" 输入框。
- **交互**:纯展示性动画/截图，不可交互。输入框为视觉占位。
- **评价**:用具体的技术参数（confidence 98.2%、颜色值、blur 参数）替代了空洞的"AI 智能处理"描述，可信度较高。但整个区块是静态展示，没有可操作的 live demo。
- **截图**:[02_web_homepage_scroll1.png](screenshots/02_web_homepage_scroll1.png)

#### 1.3.3 Multi-Agent Cowork 任务板

- **功能**:展示 "Q3 Launch" 项目中 5 个 AI 代理（Claude Code、Codex、Gemini、Aion CLI、Goose）并行处理 5 项任务（Market research report、Competitor analysis、Write launch blog post、Build investor pitch deck、Social media campaign plan）的协作场景。右侧任务清单显示完成状态，底部 Activity 流实时更新各代理进展。
- **交互**:展示性截图，不可交互。
- **评价**:直观地传达了"多代理并行"的核心卖点。但所有代理状态均为 "done"/"running"，没有展示冲突解决、任务分配策略等更深层的协作机制。
- **截图**:[03_web_homepage_scroll2.png](screenshots/03_web_homepage_scroll2.png)、[06_web_cowork.png](screenshots/06_web_cowork.png)

#### 1.3.4 Assistants 页面

- **功能**:展示 20+ 内置 AI 助手角色网格，每个助手有专属头像、名称和职能标签。可见角色包括：UI/UX Designer、Python Pro、Math Wizard、3D Artist、Swift Pro、Data Sci 等。底部文案 "You can also create your own — tailored to your workflow."。
- **交互**:网格展示，不可点击深入。
- **评价**:角色覆盖编程、设计、数据分析、写作等主流领域，头像风格统一（扁平插画），但页面未展示自定义助手的方法或技能配置界面。
- **截图**:[07_web_assistants.png](screenshots/07_web_assistants.png)

#### 1.3.5 Remote 页面

- **功能**:展示远程控制架构 —— 从 Telegram、WeChat、Lark、DingTalk 或内置 WebUI 发送命令 → 任何渠道（ANY CHANNEL）→ 你的电脑（Your computer）上运行的代理。底部强调 "Easy to use, Free, Your 24/7 Remote AI Assistant"。
- **交互**:流程图展示。
- **评价**:覆盖了中国用户常用的 Lark/DingTalk 和海外用户常用的 Telegram/Discord，渠道选择有地域考量。但页面未说明远程连接的安全性机制（端到端加密、认证方式等）。
- **截图**:[08_web_remote.png](screenshots/08_web_remote.png)

#### 1.3.6 Automation 页面

- **功能**:展示 Scheduled Tasks 界面，支持 cron 式定时调度。示例任务：Weekly sales report（每周一 8:00 AM，Gemini CLI）、Daily code review（每天 9:00 AM，Claude Code，状态 Running）、Backup project files（每天 11:00 PM，Aion CLI，状态 Paused）、Generate standup notes（每周一 9:00 AM，Codex，状态 Active）。每个任务有独立开关。
- **交互**:界面截图展示。
- **评价**:任务卡片设计直观（开关 + 时间 + 代理标识），但页面未展示 cron 表达式编辑界面或错误重试机制。
- **截图**:[09_web_automation.png](screenshots/09_web_automation.png)

#### 1.3.7 Download 页面

- **功能**:提供全平台安装包下载。版本 v1.9.25（Released May 5, 2026）。macOS 支持 Apple Silicon/Intel (.dmg) + Homebrew；Windows 支持 x64/arm64 (.exe) + Winget；Linux 支持 x64/arm64 (.deb) + Headless curl 脚本。另有 SYSTEM REQUIREMENTS 区块列明各平台最低配置（4 GB RAM）。
- **交互**:平台切换式下载，自动检测访客 OS（Linux 访客显示 "Download for Linux (x64)" 为主 CTA）。
- **评价**:覆盖全面（3 大桌面平台 × 2 架构），且提供包管理器安装（brew/winget）降低安装门槛。Linux 单独提供 Headless 脚本（curl -fsSL https://get.aionui.com | bash）考虑到了服务器/远程场景。
- **截图**:[12_web_download.png](screenshots/12_web_download.png)、[14_web_download_linux.png](screenshots/14_web_download_linux.png)、[30_web_install_methods.png](screenshots/30_web_install_methods.png)、[31_web_sysreq.png](screenshots/31_web_sysreq.png)

#### 1.3.8 应用主界面

- **功能**:桌面端主窗口分为左侧导航栏和右侧主内容区。左侧：AionUi 品牌、New Chat、Search、Scheduled Tasks、Teams（当前无聊天历史显示 "No chat history"）、Settings。右侧：问候语 "Hi, what's your plan for today?"、代理选择器（当前为 Aion CLI）、多行输入框（提示文字 "Send a message, upload files, open a folder, or create a scheduled task..."）、底部快捷操作（Chat in Folder、Default Model、Permissions）和助手快捷标签（Story Roleplay、Beautiful Mermaid、moltbook、Cowork、OpenClaw Setup Expert、Star Office Helper、Academic Paper、Morph PPT、Excel Creator、PPT Creator、Word Creator）。右上角有 "AionUi Skills Market" 开关。
- **交互**:输入框可输入文字，助手标签可点击切换上下文，左侧导航可切换功能模块。Scheduled Tasks/Teams 等模块在未登录态下显示空状态。
- **评价**:界面布局遵循现代聊天应用范式（侧边栏 + 主内容区），信息密度适中。但应用启动后未提供引导流程（onboarding），空状态的 Teams 区域没有引导用户创建或加入团队的提示。Skills Market 开关位于右上角但无说明文案，新用户难以理解其用途。
- **截图**:[17_app_main.png](screenshots/17_app_main.png)

---

## 2. UI/UX 风格和质量描述

### 2.1 视觉风格

官网采用浅色主背景（#f5f5f7 类灰白）+ 深色文字（#1a1a1a）的高对比度方案，点缀色为紫色/靛蓝（用于强调文字如 "writing code"、"AI agents"）。整体风格偏向"企业级工具"——干净、规整、无多余装饰。应用内沿用相同配色体系，左侧导航栏为浅灰，主内容区为纯白，卡片和按钮使用大圆角（12-16px）。

插画风格：官网中的 AI 助手头像采用统一的扁平化人物插画，配色柔和，有辨识度。

### 2.2 信息密度与层级

官网首屏在 1024×768 分辨率下完整呈现 slogan（两行大字）+ 副标题（一行小字）+ CTA 按钮 + 产品截图，无滚动即可理解产品定位。Multi-Agent Cowork 区块采用左右分栏（文字说明左 + 界面截图右），信息分布均衡。Download 页面按平台分卡片，每个卡片内仅保留架构 + 格式 + 下载按钮，无干扰信息。

应用主界面输入区上方堆叠了代理选择器 + 输入框 + 快捷操作栏 + 助手标签云，纵向占比较高，在较小窗口中可能挤压历史消息区域。

### 2.3 交互流畅度

- 官网为静态页面（或轻度 SPA），导航点击后滚动/切换无明显延迟。
- 应用启动：在沙盒环境中从点击到主界面呈现约 5-8 秒（Electron 应用，含 Chromium 渲染进程启动）。
- 应用内标签点击无明显延迟，但部分功能（如 Scheduled Tasks）在未登录态下无反馈，用户难以区分是"加载中"还是"空状态"。

### 2.4 文案质量

官网文案风格统一、简洁，使用第二人称 "your" 增强代入感（"Your AI agents"、"Your computer"、"Your 24/7 Remote AI Assistant"）。技术术语和日常用语平衡得当（"auto-detects"、"cron"、"team them up"）。

应用内输入框提示文案覆盖多种操作意图（"Send a message, upload files, open a folder, or create a scheduled task..."），降低用户首次使用的认知门槛。

### 2.5 可访问性观察

- 对比度：官网深色文字在浅色背景上对比度充足，CTA 按钮（黑底白字）对比度明显。
- 未发现明显的键盘导航支持标识（如 focus ring 样式）。
- 官网和应用均未在采集到的截图中展示深色模式切换入口。
- 截图中未观察到字体大小调节控件。

---

## 3. 官网描述

### 3.1 关键文案摘录

> "One desktop. Your AI agents, actually writing code..." — 首页 H1
>
> "They live on your computer. Work with one, team them up, or control them remotely — getting things done, 24/7." — 首页副标题
>
> "AionUi auto-detects Claude Code, Codex, Gemini CLI and 20+ more on your machine. Run them in parallel, assign tasks to the right agent, or team them up — all in one unified workspace." — Cowork 区块
>
> "Send commands from Telegram, WeChat, Lark, DingTalk, or the built-in WebUI. Your agents keep running on your computer while you're on the go." — Remote 区块
>
> "Schedule agents to run tasks on a cron. Code review every morning, backup every night, report every Monday. They work while you sleep." — Automation 区块

### 3.2 核心卖点（官网视角）

1. **多代理统一调度**（"20+ agents"、"all in one unified workspace"）— 解决多 AI 工具碎片化
2. **本地优先**（"live on your computer"、"no cloud upload"）— 强调数据隐私
3. **远程控制**（Telegram/WeChat/Lark/DingTalk/WebUI）— 支持移动端管理
4. **定时自动化**（"24/7 Automation"、"cron"）— 支持无人值守任务
5. **开源免费**（Apache-2.0 License）— 无使用成本

### 3.3 与实际体验的差距

| 卖点 | 官网原文 | 实际体验 | 差距 |
|---|---|---|---|
| 多代理协作 | "Run them in parallel, assign tasks to the right agent" | 应用启动后仅展示单代理（Aion CLI）聊天界面，多代理协作界面未在登录前展示 | 核心卖点需登录后才能体验 |
| 20+ 助手 | "20+ assistants on your computer" | 官网展示头像网格，应用内展示助手标签云，但助手能力差异未说明 | 助手间差异和选择策略不明确 |
| 定时自动化 | "Scheduled Tasks" 展示 5 个示例任务 | 应用左侧有 Scheduled Tasks 入口，但未登录时无法查看或创建 | 功能入口可见但不可用 |

---

## 5. 目标用户

基于官网用语和实际功能推断：

1. **开发者/程序员** — 核心受众。产品围绕 Claude Code、Codex、Gemini CLI 等开发工具构建，"writing code" 是首屏核心信息。
2. **技术团队负责人** — "Q3 Launch" 任务板、standup notes、code review 等示例任务暗示团队管理场景。
3. **需要数据隐私的用户** — "live on your computer"、"no cloud upload, no third-party service" 强调本地运行，吸引对云端 AI 有顾虑的用户。

---

## 6. 与同类产品对比

| 维度 | AionUi | Claude Desktop | Continue.dev |
|---|---|---|---|
| 多代理支持 | 核心卖点，20+ 代理统一调度 | 仅 Claude 单一代理 | 支持多模型但需手动切换配置 |
| 本地运行 | 是，代理在本地机器运行 | 是，但仅 Claude | 是，IDE 插件形式 |
| 远程控制 | 支持 Telegram/WeChat/Lark/DingTalk | 不支持 | 不支持 |
| 定时自动化 | 内置 cron 式任务调度 | 不支持 | 不支持 |
| 开源 | Apache-2.0 | 否（Anthropic 商业产品） | 开源 |
| 界面形态 | 独立桌面应用 | 独立桌面应用 | IDE 插件 |

---

## 7. 优劣势小结

| 维度 | 优势 | 劣势 |
|---|---|---|
| 产品逻辑 | 多代理统一调度 + 定时自动化 + 远程控制，覆盖面广；本地优先策略契合隐私敏感用户 | 核心功能（多代理协作、定时任务）需登录后才能使用，首屏体验与卖点有落差 |
| UI/UX | 官网信息层级清晰，应用布局遵循聊天应用惯例；安装方式多样（brew/winget/.deb） | 应用内缺乏 onboarding 引导；空状态无提示；Skills Market 功能无说明 |
| 工程质量 | 全平台支持（macOS/Windows/Linux × x64/arm64）；开源社区活跃（26.1k stars, GitHub Trending #1） | Electron 应用在容器内启动需 --no-sandbox 参数，存在兼容性风险 |

---

## 附录 A 截图索引

| # | 文件 | 说明 |
|---|---|---|
| 01 | screenshots/01_web_homepage.png | 官网首页全景 |
| 02 | screenshots/02_web_homepage_scroll1.png | 首页 Stella 助手演示区 |
| 03 | screenshots/03_web_homepage_scroll2.png | 首页 Multi-Agent Cowork 任务板 |
| 06 | screenshots/06_web_cowork.png | Cowork 功能页面 |
| 07 | screenshots/07_web_assistants.png | Assistants 助手网格页面 |
| 08 | screenshots/08_web_remote.png | Remote 远程控制页面 |
| 09 | screenshots/09_web_automation.png | Automation 定时任务页面 |
| 12 | screenshots/12_web_download.png | Download 页面版本信息 |
| 14 | screenshots/14_web_download_linux.png | Linux 下载选项区 |
| 17 | screenshots/17_app_main.png | AionUi 桌面应用主界面 |
| 30 | screenshots/30_web_install_methods.png | 安装方法（brew/winget/curl） |
| 31 | screenshots/31_web_sysreq.png | 系统要求页面 |
| 32 | screenshots/32_web_footer.png | 官网 Footer（版权/社区链接） |

> 编号规则:`NN_<source>_<view>.png`,`source ∈ {web, app, android}`,`view` 短 kebab-case;`NN` 单调递增，允许跳号。
