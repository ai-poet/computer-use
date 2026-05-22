# Kilo Code (CN) 产品分析报告

| 项目 | 值 |
|---|---|
| 官网 | https://kilo.org.cn |
| 下载链接 | VS Code Marketplace: https://marketplace.visualstudio.com/items?itemName=kilocode.kilo-code |
| 报告日期 | 2026-05-22 |
| 主机 | linux / x86_64 |
| Runtime | sandbox-local |
| 模式 | sandbox-full |
| 用时 | ~25 分钟 |

---

## 1. 详细的产品逻辑介绍

### 1.1 总定位

Kilo Code 是一款开源的 AI 编码智能体(Coding Agent),以 VS Code 扩展形态为主,同时提供 JetBrains 插件和 CLI 版本。它通过自然语言指令驱动代码生成、重构、调试、文档编写和终端命令执行,支持 500 余种 AI 模型(包括 Claude、Gemini 等)。截至分析时,其在 VS Code Marketplace 已有超过 111 万次安装,官方宣称处理了 20T+ Token,在 OpenRouter 上排名第 1。产品定位为"全栈智能体工程平台",面向需要 AI 辅助编程的开发者群体。

### 1.2 界面清单

按出现顺序列出实际看到的所有主要界面:

| # | 界面 | 入口 | 主要功能 | 截图 |
|---|---|---|---|---|
| 1 | 官网首页 | https://kilo.org.cn | 产品定位、核心数据、CTA | [02_web_homepage_clean.png](screenshots/02_web_homepage_clean.png) |
| 2 | 官网功能介绍 | 首页滚动 | 全栈智能体工程平台特性 | [03_web_homepage_scroll1.png](screenshots/03_web_homepage_scroll1.png) |
| 3 | 官网 AI 投资回报 | 首页滚动 | 企业级管理功能 | [04_web_homepage_scroll2.png](screenshots/04_web_homepage_scroll2.png) |
| 4 | 官网特性模块 | 首页底部 | 六大功能模块概览 | [06_web_homepage_footer.png](screenshots/06_web_homepage_footer.png) |
| 5 | 定价总览 | https://kilo.ai/pricing | 四款产品定价对比 | [08_web_pricing.png](screenshots/08_web_pricing.png) |
| 6 | Kilo Code 定价详情 | 定价页滚动 | Free & Open Source 档位 | [10_web_pricing_kilo_code.png](screenshots/10_web_pricing_kilo_code.png) |
| 7 | 中文文档 | https://kilo.org.cn/docs | 产品介绍、快速上手 | [15_web_docs.png](screenshots/15_web_docs.png) |
| 8 | VS Code Marketplace | 文档内链接跳转 | 扩展详情、安装指引 | [16_web_install_ext.png](screenshots/16_web_install_ext.png) |
| 9 | Marketplace 功能详情 | Marketplace 滚动 | 核心功能列表 | [17_web_marketplace_scroll.png](screenshots/17_web_marketplace_scroll.png) |
| 10 | VS Code 主界面 | 沙盒内启动 VS Code | IDE 主界面、欢迎页 | [19_app_vscode_main.png](screenshots/19_app_vscode_main.png) |
| 11 | Kilo Code 侧边栏 | 点击左侧 Kilo 图标 | 扩展面板、消息输入 | [23_app_extensions.png](screenshots/23_app_extensions.png) |
| 12 | 登录弹窗 | 发送消息后触发 | GitHub/Google/Apple 登录 | [28_app_kilo_response.png](screenshots/28_app_kilo_response.png) |
| 13 | 命令面板 | Ctrl+Shift+P | Kilo Code 命令列表 | [32_app_kilo_commands.png](screenshots/32_app_kilo_commands.png) |
| 14 | VS Code + Kilo Code 完整界面 | 最终状态 | 侧边栏 + CHAT 面板 | [33_app_vscode_final.png](screenshots/33_app_vscode_final.png) |

### 1.3 各界面功能与评价

#### 1.3.1 官网首页

- **功能**:首屏展示品牌定位"以 Kilo 速度前行",副标题"使用最受欢迎的开源编码智能体,实现更快的构建、发布和迭代";核心数据展示区(#1 on OpenRouter、100万+ 开发者、20T+ Token);CTA 按钮"使用 Kilo 开始"和"咨询专家"
- **交互**:滚动逐 section 展示,导航栏固定顶部(产品、定价、支持、文档、博客、登录/注册)
- **评价**:首屏信息密度适中,核心数据用金色大字号突出,视觉层次清晰。"以 Kilo 速度前行"的标题采用黄色发光字体,在深色背景上有较高对比度。但"使用 Kilo 开始"按钮点击后未明确跳转至安装页面,交互反馈不够直接
- **截图**:[02_web_homepage_clean.png](screenshots/02_web_homepage_clean.png)

#### 1.3.2 官网功能介绍区

- **功能**:展示"全栈智能体工程平台"定位,列出四大卖点:跨界面同步(移动设备开始任务,VS Code/JetBrains/CLI 无缝完成)、持久化上下文、打开黑盒(开源可定制)、无摩擦交付
- **交互**:纯展示型 section,无交互元素
- **评价**:功能描述具体且可验证,右侧配图展示了 VS Code 中的 Kilo Code 界面,图文对应清晰。但"无摩擦交付"的描述较抽象,缺少具体操作流程的演示
- **截图**:[03_web_homepage_scroll1.png](screenshots/03_web_homepage_scroll1.png)

#### 1.3.3 官网 AI 投资回报区

- **功能**:面向企业决策者的卖点:遏制 AI 乱象(集中管理、安全风险控制)、追踪并提升速度(管理仪表板、ROI 衡量)、集中式管理(共享点数、统一账单)、缩短顶尖开发者入职培训
- **交互**:纯展示,右侧有管理仪表板截图
- **评价**:从开发者工具延伸到企业管理的视角,扩展了产品边界。仪表板截图展示了团队级别的 AI 使用追踪,但截图分辨率较低,具体指标难以辨认
- **截图**:[04_web_homepage_scroll2.png](screenshots/04_web_homepage_scroll2.png)

#### 1.3.4 定价页面

- **功能**:四档产品并列展示:KiloClaw($51/mo, Managed OpenClaw)、Kilo Code(Free & Open Source, Agentic Engineering)、Kilo Pass($19/mo, AI inference)、Teams($15/mo, Ship together)
- **交互**:点击各产品卡片可查看详情
- **评价**:定价结构清晰,Kilo Code 的"Free & Open Source"定位与竞争对手(Copilot $10/mo、Cursor $20/mo)形成差异化。但"AI usage billed separately"的提示意味着免费版仍需自付 API 费用,实际成本因使用量而异
- **截图**:[08_web_pricing.png](screenshots/08_web_pricing.png)、[10_web_pricing_kilo_code.png](screenshots/10_web_pricing_kilo_code.png)

#### 1.3.5 VS Code Marketplace 页面

- **功能**:扩展详情页,展示 1,117,854 次安装、Free 标签、185 条评分;安装命令 `ext install kilocode.Kilo-Code`;功能列表(Key Features: Code Generation、Inline Autocomplete、Task Automation、Automated Refactoring、MCP Server Marketplace、Multi Mode)
- **交互**:提供"Copy"按钮复制安装命令,链接跳转至官网
- **评价**:安装量数据(111万+)增强了产品可信度。功能列表使用图标+文字的格式,一目了然。但 185 条评分相对较低(对比 Copilot 数千条评分),说明用户反馈活跃度有提升空间
- **截图**:[16_web_install_ext.png](screenshots/16_web_install_ext.png)、[17_web_marketplace_scroll.png](screenshots/17_web_marketplace_scroll.png)

#### 1.3.6 VS Code 内 Kilo Code 扩展界面

- **功能**:
  - **左侧侧边栏**:Kilo Code 图标面板,显示产品描述("Kilo Code is an AI coding assistant..."),消息输入框,模式选择器(Code/Auto Free)
  - **右侧 CHAT 面板**:"Build with Agent"标题,输入框"Describe what to build",支持附件、模式切换
  - **命令面板**:提供 20+ 条命令,涵盖 Agent Manager(工作树管理)、Context 管理、Terminal 操作等
- **交互**:输入自然语言指令 → 发送 → AI 生成代码/执行任务。支持 Ctrl+K 快捷键(Add to Context)、Ctrl+Shift+N(Advanced New Worktree)
- **评价**:
  - 双面板设计(侧边栏 + CHAT)充分利用了 VS Code 的扩展能力,与原生 IDE 体验融合度较高
  - 命令面板集成度深,支持键盘快捷键,符合开发者工作流
  - **登录墙**:未登录时发送消息会弹出"Sign in to use AI Features"弹窗,支持 GitHub/Google/Apple/GHE.com 四种登录方式。这意味着扩展安装后仍需账号授权才能使用核心功能,增加了首次使用门槛
  - 输入框的"Auto"标签暗示支持自动模式选择,但具体逻辑未在界面中说明
- **截图**:[23_app_extensions.png](screenshots/23_app_extensions.png)、[28_app_kilo_response.png](screenshots/28_app_kilo_response.png)、[32_app_kilo_commands.png](screenshots/32_app_kilo_commands.png)、[33_app_vscode_final.png](screenshots/33_app_vscode_final.png)

#### 1.3.7 中文文档页面

- **功能**:文档站点(kilo.org.cn/docs),左侧导航树(欢迎、入门、使用 Kilo Code、核心概念、付费计划、Agent 行为、高级用法、扩展 Kilo Code 等),右侧内容区展示产品功能列表(生成代码、重构调试、编写文档、回答问题、自动化任务、创建项目、自动补全)
- **交互**:树形导航,搜索框,主题切换,语言切换(中文/英语)
- **评价**:文档结构完整,从入门到高级用法分层清晰。但"快速上手"section 在首屏未完整展示,需要进一步滚动才能看到安装步骤
- **截图**:[15_web_docs.png](screenshots/15_web_docs.png)

---

## 2. UI/UX 风格和质量描述

### 2.1 视觉风格

官网采用深色主题(接近纯黑 `#0a0a0a`)为主基调,搭配高饱和度的黄色/金色作为品牌色,形成强烈的视觉对比。标题使用大号无衬线字体(目测 48-64px),正文使用灰色系(层级分明)。整体调性偏向"开发者工具"的科技感,但通过圆润的卡片圆角和渐变光晕效果 soften 了硬核感。VS Code 扩展界面遵循 VS Code 原生主题,不突兀。

### 2.2 信息密度与层级

官网首屏信息量适中:品牌 slogan → 核心数据 → CTA 按钮,三层递进清晰。功能介绍区采用左文右图的布局,每段一个勾选图标+标题+描述,阅读节奏良好。定价页面四列卡片等高并列,便于横向对比。主要 CTA("使用 Kilo 开始")使用蓝色填充按钮,在深色背景中对比度充足,一眼可辨。

### 2.3 交互流畅度

- 官网页面滚动平滑,无明显的加载延迟或白屏
- VS Code 扩展安装通过 CLI 命令 `ext install kilocode.Kilo-Code` 一键完成,安装过程约 3-5 秒
- 扩展面板切换响应迅速,输入框焦点切换无明显延迟
- **不足**:官网"使用 Kilo 开始"按钮点击后未产生明显的页面跳转或弹窗,交互反馈不足;发送消息后的登录弹窗遮挡了主界面,且关闭后仍需登录才能继续使用

### 2.4 文案质量

官网中英文混合使用,中文翻译质量较高,无明显的机翻痕迹。例如"保持心流状态""无摩擦交付""打开黑盒"等表述既传达了技术概念,又保持了可读性。文档中的功能列表使用动词开头(生成、重构、编写、回答),符合技术文档的规范。VS Code Marketplace 页面的英文描述专业且简洁。

### 2.5 可访问性观察

- 官网文字与背景对比度在大部分区域满足 WCAG AA 标准(黄色标题在深色背景上对比度充足)
- 文档页面支持深色/浅色主题切换
- VS Code 扩展继承了 IDE 的主题设置,支持高对比度模式
- **不足**:官网部分截图(如管理仪表板)中的文字较小,在低分辨率下难以阅读;登录弹窗的关闭按钮(X)尺寸较小,对精细运动控制有要求的用户可能不易点击

---

## 3. 官网描述

### 3.1 关键文案摘录

> "以 Kilo 速度前行" — 官网首页 H1

> "使用最受欢迎的开源编码智能体,实现更快的构建、发布和迭代。" — 官网首页副标题

> "Kilo Code 加速开发,提供 AI 驱动的代码生成和任务自动化。这个开源扩展可以直接插入 VS Code。" — 中文文档首页

> "Open Source AI coding agent that generates code from natural language, automates tasks, and runs terminal commands. Features inline autocomplete, browser automation, automated refactoring, and custom modes for planning, coding, and debugging. Supports 500+ AI models including Claude (Anthropic), Gemini." — VS Code Marketplace 描述

> "Free & Open Source — For every knowledge worker building with AI" — 定价页面 Kilo Code 卡片

### 3.2 核心卖点(官网视角)

1. **开源免费**:Kilo Code 完全免费开源,源码可查可定制(官网首页、定价页、Marketplace)
2. **多模型支持**:支持 500+ AI 模型,不绑定单一供应商(Marketplace 描述)
3. **全平台覆盖**:VS Code 扩展 + JetBrains 插件 + CLI,跨 IDE 使用(文档首页、定价页)
4. **企业级管理**:提供 AI 管理仪表板、统一账单、数据隐私控制(官网 AI 投资回报区)
5. **Agent 能力**:不仅是代码补全,还能执行终端命令、自动化浏览器、重构代码(Marketplace Key Features)

### 3.3 与实际体验的差距

| 卖点 | 官网原文 | 实际体验 | 差距 |
|---|---|---|---|
| 免费使用 | "Free & Open Source" | 扩展安装免费,但使用 Chat 需登录;AI Token 费用需自付 | "Free"仅指扩展本身,AI 推理成本另计 |
| 一键开始 | "使用 Kilo 开始" | 按钮点击后无明确安装引导,需手动到 Marketplace 安装 | CTA 按钮的落地页不够直接 |
| 开源可定制 | "打开黑盒:Kilo 是开源的" | 源码可在 GitHub 获取,但文档中定制指南较深 | 定制门槛对普通用户较高 |

---

## 4. 定价

Kilo 提供四档产品:

| 产品 | 价格 | 定位 |
|---|---|---|
| **Kilo Code** | Free (AI usage billed separately) | 开源 AI 编码助手,VS Code/JetBrains/CLI 扩展 |
| KiloClaw | $51/mo (年付) / $55/mo (月付) | Managed OpenClaw,企业级代理管理 |
| Kilo Pass | $19/mo | AI 推理服务,按量计费 |
| Teams | $15/mo/人 | 团队协作功能 |

Kilo Code 本身免费,但 AI 推理费用需用户自行承担(通过各模型提供商的 API Key)。这与 GitHub Copilot($10-19/mo)和 Cursor($20/mo)的"全包"模式不同,Kilo Code 更像是一个"免费前端 + 自付后端"的架构,对高频使用者可能更划算,对低频使用者则增加了配置成本。

---

## 5. 目标用户

基于官网用语和实际功能推断:

1. **个人开发者**:"For every knowledge worker building with AI"(定价页),需要 AI 辅助编码但不愿支付订阅费
2. **企业开发团队**:官网设有"咨询专家"按钮、AI 管理仪表板、企业级数据隐私控制,说明面向 B 端市场
3. **多 IDE 用户**:跨 VS Code/JetBrains/CLI 的支持,吸引同时使用多种工具的开发者的用户

---

## 6. 与同类产品对比

| 维度 | Kilo Code | GitHub Copilot | Cursor |
|---|---|---|---|
| **价格** | 扩展免费,AI Token 自付 | $10-19/mo 全包 | $20/mo 全包 |
| **开源** | 完全开源 | 闭源 | 闭源(基于 VS Code 开源) |
| **模型选择** | 500+ 模型(Claude, Gemini, etc.) | 仅限 OpenAI/GitHub 模型 | 仅限内置模型 |
| **Agent 能力** | 强(终端命令、浏览器自动化、任务自动化) | 弱(主要为补全和聊天) | 中(Composer 模式) |
| **IDE 支持** | VS Code, JetBrains, CLI | VS Code, JetBrains, Vim, CLI | 仅 VS Code 分支 |
| **安装量** | 111万+(Marketplace) | 数千万级 | 未公开 |

Kilo Code 的核心差异化在于"开源 + 多模型 + 强 Agent 能力",但生态成熟度和品牌认知度不及 Copilot,IDE 集成深度不及 Cursor。

---

## 7. 优劣势小结

| 维度 | 优势 | 劣势 |
|---|---|---|
| 产品逻辑 | 开源免费,不绑定单一模型,Agent 能力强(终端+浏览器自动化) | 需自付 AI Token 费用,配置门槛高;核心功能需登录 |
| UI/UX | VS Code 原生扩展体验,双面板设计合理,命令集成度高 | 官网 CTA 引导不足;登录弹窗阻断首次使用流程 |
| 工程质量 | 111万+安装量验证稳定性,支持 500+ 模型,跨平台 | 评分数量较少(185条),社区活跃度待观察;中文文档相对英文版较简略 |

---

## 附录 A 截图索引

| # | 文件 | 说明 |
|---|---|---|
| 02 | screenshots/02_web_homepage_clean.png | 官网首页首屏(翻译弹窗关闭后) |
| 03 | screenshots/03_web_homepage_scroll1.png | 首页功能介绍区(全栈智能体工程平台) |
| 04 | screenshots/04_web_homepage_scroll2.png | 首页 AI 投资回报区 |
| 05 | screenshots/05_web_homepage_bottom.png | 首页提问模式区 |
| 06 | screenshots/06_web_homepage_footer.png | 首页底部六大特性模块 |
| 08 | screenshots/08_web_pricing.png | 定价总览页(四款产品) |
| 10 | screenshots/10_web_pricing_kilo_code.png | Kilo Code 定价详情(Free & Open Source) |
| 15 | screenshots/15_web_docs.png | 中文文档首页 |
| 16 | screenshots/16_web_install_ext.png | VS Code Marketplace 扩展页 |
| 17 | screenshots/17_web_marketplace_scroll.png | Marketplace 功能详情 |
| 19 | screenshots/19_app_vscode_main.png | VS Code 主界面(含 Kilo Code CHAT 面板) |
| 23 | screenshots/23_app_extensions.png | Kilo Code 侧边栏扩展面板 |
| 28 | screenshots/28_app_kilo_response.png | 发送消息后触发的登录弹窗 |
| 32 | screenshots/32_app_kilo_commands.png | 命令面板中的 Kilo Code 命令列表 |
| 33 | screenshots/33_app_vscode_final.png | VS Code + Kilo Code 完整界面 |

> 编号规则:`NN_<source>_<view>.png`,`source ∈ {web, app}`,`view` 短 kebab-case;`NN` 单调递增,允许跳号(web 段 02-17, app 段 19-33)。
