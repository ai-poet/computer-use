# CheapRouter 产品分析报告

| 项目 | 值 |
|---|---|
| 官网 | https://cheaprouter.org |
| 下载链接 | — |
| 报告日期 | 2026-05-22 |
| 主机 | linux / x86_64 |
| Runtime | sandbox-local |
| 模式 | web-only |
| 用时 | ~15 分钟 |

> 本次为网页版分析，未驱动桌面端 — 产品官网仅提供 Windows (x64/ARM64) 和 macOS (Apple Silicon & Intel) 安装包，无 Linux 版本，当前沙盒为 Linux 环境无法安装运行。

---

## 1. 详细的产品逻辑介绍

### 1.1 总定位

CheapRouter 是一款面向 Claude Code 和 Codex 用户的统一工作空间与 API 路由服务。它在用户本地运行一个桌面客户端，自动完成 Claude Code 和 Codex 的配置，将多个 AI 工具的 API 调用汇聚到一个入口点，提供按量计费、余额统一管理、多账户自动切换和 SLA 保障的服务。产品定位是"不是另一个 IDE，也不只是另一个中继服务"，而是把运行 Claude Code 和 Codex 的繁琐部分（配置、计费、故障切换）统一接管。

### 1.2 界面清单

按出现顺序列出实际看到的所有主要界面，每个一行，挂截图编号：

| # | 界面 | 入口 | 主要功能 | 截图 |
|---|---|---|---|---|
| 1 | 首页(网页) | cheaprouter.org/home | 产品定位、下载入口、功能概览 | [01_web_homepage.png](screenshots/01_web_homepage.png) |
| 2 | 应用预览(网页) | 首页向下滚动 | 桌面客户端界面展示 | [02_web_homepage_scroll1.png](screenshots/02_web_homepage_scroll1.png) |
| 3 | 平台能力(网页) | 首页向下滚动 | 按量付费、Token 级计费、多账户切换说明 | [03_web_homepage_scroll2.png](screenshots/03_web_homepage_scroll2.png) |
| 4 | 下载区(网页) | 首页向下滚动 | Windows/macOS 客户端下载入口 | [04_web_download_section.png](screenshots/04_web_download_section.png) |
| 5 | 核心卖点(网页) | 首页向下滚动 | 自动配置、统一余额、SLA 保障 | [05_web_why_section.png](screenshots/05_web_why_section.png) |
| 6 | 模型覆盖(网页) | 首页底部 | 支持的 Claude/GPT/第三方模型 | [06_web_footer.png](screenshots/06_web_footer.png) |
| 7 | 登录页(网页) | /pricing /models /docs /about /download | 统一登录入口（Linux.do OAuth 或邮箱） | [08_web_pricing.png](screenshots/08_web_pricing.png) |

### 1.3 各界面功能与评价

#### 1.3.1 首页

- **功能**:首屏展示产品核心定位"Claude Code and Codex, one workspace is enough"，提供三个主 CTA："Download now"（自动推荐当前平台）、"Download macOS"、"Use the API"。下方依次展示应用预览、平台能力、下载区域、核心卖点、模型覆盖范围。
- **交互**:单页长滚动设计，导航栏固定顶部，含 Models、Pricing、EN 语言切换、Sign in to dashboard 入口。
- **评价**:信息架构清晰，首屏即给出产品定位+下载入口+核心标签（Claude Code / Codex / Multi-account · Multi-model），用户无需滚动即可判断产品是否与自己相关。但所有内页（Pricing/Models/Docs/Download/About）均需要登录，未登录用户只能浏览首页内容，信息获取受限。
- **截图**:[01_web_homepage.png](screenshots/01_web_homepage.png)

#### 1.3.2 应用预览区

- **功能**:通过一张桌面应用截图展示 CheapRouter 客户端的实际界面，显示 Claude Code 和 Codex 并行工作的场景——左侧为对话/代码区，右侧为文件树和模型选择面板。
- **交互**:静态展示，不可交互。
- **评价**:截图展示了深色主题的 IDE 风格界面，与官网的浅色主题形成对比。能直观传达"一个窗口同时操作多个 AI 工具"的核心价值。但截图分辨率在网页上显示较小，部分文字难以辨认。
- **截图**:[02_web_homepage_scroll1.png](screenshots/02_web_homepage_scroll1.png)

#### 1.3.3 平台能力区

- **功能**:三个卡片分别说明产品的计费模式——Token-level metering（按运行付费）、Multi-account auto-switching（单 key 故障不中断整体路由）、5h/1d/7d usage windows visible（多时间维度用量可见）。主标题"Pay-as-you-go, balance never expires"强调余额不过期。
- **交互**:静态展示。
- **评价**:价值主张明确，直接回应了 AI 开发者最关心的痛点——计费透明度。"余额不过期"是对比官方 API 预付费模式的差异化卖点。
- **截图**:[03_web_homepage_scroll2.png](screenshots/03_web_homepage_scroll2.png)

#### 1.3.4 下载区

- **功能**:展示桌面客户端的下载选项。Windows 版本标注"x64 / ARM64"并被标记为"Recommended for this device"，macOS 版本标注"Apple Silicon & Intel"。左侧文案说明安装后会"auto-writes local config files without overwriting existing settings"。
- **交互**:提供 Download 按钮，但实际点击未触发下载（可能需登录或页面交互逻辑特殊）。
- **评价**:平台覆盖主流桌面系统，但没有 Linux 版本——对于以开发者为主要用户群的产品来说是一个明显缺口。"Recommended for this device"的自动推荐机制体验友好。
- **截图**:[04_web_download_section.png](screenshots/04_web_download_section.png)

#### 1.3.5 核心卖点区（WHY CHEAPROUTER）

- **功能**:三个并列板块：01 Fast Onboarding（自动本地配置）、02 Spend You Can See（统一余额面板）、03 All In One（SLA 保障+自动故障切换）。每个板块配图标和简短说明。
- **交互**:静态展示。
- **评价**:卖点提炼精准，分别对应配置繁琐、计费分散、服务不稳定三个开发者痛点。文案具体可感，如"no more copy-pasting JSON configs"、"traffic automatically switches to healthy routes"。
- **截图**:[05_web_why_section.png](screenshots/05_web_why_section.png)

#### 1.3.6 模型覆盖区

- **功能**:三个卡片展示支持的模型家族——Claude Family（Sonnet 4.6 / Opus 4.7 / Haiku 4.5）、Codex/GPT Family（GPT-5.5 / GPT-5.4 / GPT-5.3 Codex）、OpenAI-Compatible Others（Gemini / GLM / Qwen 等）。顶部文案强调"at much better prices than official API rates"。
- **交互**:静态展示，模型名称以标签形式呈现。
- **评价**:覆盖当前主流编程模型，标注具体版本号增加可信度。"Lower total cost"的目标设定与"比官方 API 更便宜"的定价策略直接关联。
- **截图**:[06_web_footer.png](screenshots/06_web_footer.png)

#### 1.3.7 登录页

- **功能**:所有内页（/pricing /models /docs /about /download）的统一登录入口。提供两种登录方式：Linux.do OAuth（"Continue with Linux.do"）和邮箱密码登录。页面底部有 Cloudflare 验证标记。
- **交互**:输入邮箱密码或点击 OAuth 按钮登录。未登录态无法访问任何功能页。
- **评价**:强制登录门槛较高，未注册用户甚至无法查看定价和文档。注册有邮箱后缀白名单限制（仅接受 @qq.com，从页面源码中的 `registration_email_suffix_whitelist` 可见）。Linux.do OAuth 的集成暗示目标用户可能偏向中文开发者社区。
- **截图**:[08_web_pricing.png](screenshots/08_web_pricing.png)

---

## 2. UI/UX 风格和质量描述

### 2.1 视觉风格

官网采用浅色背景+深色文字的 clean 设计，主色调为青绿色（teal）用于强调标题和 CTA 按钮（如"one workspace"、"Sign in to dashboard"）。整体风格偏向现代 SaaS 产品，简洁、专业、信息密度适中。首页使用大号无衬线字体（疑似 Inter 或类似字体）展示主标语，营造直接有力的第一印象。应用预览截图显示客户端采用深色主题，与官网浅色形成对比。

### 2.2 信息密度与层级

首屏信息层级清晰：产品名（左上角）→ 导航（中上）→ 核心标签（Claude Code / Codex）→ 主标语 → 三个 CTA 按钮 → 辅助说明。首屏在展示完整产品定位的同时没有信息过载。向下滚动后，每个 section 用图标+标题+短文案的三段式结构呈现，阅读节奏良好。主要 CTA（"Download now"黑色填充按钮）在浅色背景上对比度充足，一眼可寻。

### 2.3 交互流畅度

- 页面加载速度正常，无明显的加载延迟。
- 首页滚动流畅，各 section 过渡自然。
- 导航栏中的 Pricing、Models 等链接点击后直接跳转登录页，无中间加载状态，但这也暴露了"所有功能页都需要登录"的产品策略。
- 下载按钮点击后无明显反馈（未触发下载弹窗或页面跳转），交互反馈不够明确。

### 2.4 文案质量

官网文案整体质量较高，用词精准且具体。例如：
- "no more copy-pasting JSON configs"（具体痛点）
- "traffic automatically switches to healthy routes"（具体机制）
- "balance never expires"（具体承诺）

中英文混合使用（导航为英文，但 Firefox 标签页显示中文标题"一键接入 · 按量计费"），推测产品主要面向中文开发者群体。

### 2.5 可访问性观察

- 文字与背景对比度充足，主文本可读性良好。
- 按钮有明确的 hover/press 状态（黑色/白色/青绿色区分）。
- 未观察到深色模式切换器（除导航栏右侧有一个月亮图标，可能是夜间模式开关，但截图中未验证功能）。
- 登录表单有标准的 label 关联。

---

## 3. 官网描述

### 3.1 关键文案摘录

> "Claude Code and Codex, one workspace is enough"
> — 来源:首页 H1

> "One desktop app for Claude Code and Codex. Multiple agents working in parallel through worktrees · Claude and Codex side by side · File"
> — 来源:首页副标题

> "Pay-as-you-go, balance never expires. Run premium models at a friendlier price than the official API, with one entry point for both Claude Code and Codex. Balance never expires — pay only for what you use."
> — 来源:平台能力区

> "Local config, written for you. After signing up on the desktop app, Claude Code and Codex are configured for you automatically — no more copy-pasting JSON configs, without overwriting your existing settings."
> — 来源:WHY CHEAPROUTER 01

> "Install the desktop app to configure Claude Code and Codex automatically, reuse existing local settings safely, and keep usage status in one place."
> — 来源:下载区左侧文案

### 3.2 核心卖点(官网视角)

1. **统一工作空间**：一个桌面应用同时运行 Claude Code 和 Codex，多 agent 并行工作（原文锚:首页 H1 及副标题）
2. **自动本地配置**：注册后自动配置 Claude Code 和 Codex，不覆盖现有设置（原文锚:WHY CHEAPROUTER 01）
3. **按量计费+余额不过期**：比官方 API 更便宜，余额永不过期（原文锚:平台能力区）
4. **SLA 保障+自动故障切换**：流量自动切换到健康路由，提供清晰恢复指导（原文锚:WHY CHEAPROUTER 03）
5. **多模型覆盖**：支持 Claude、Codex/GPT、Gemini/GLM/Qwen 等 OpenAI 兼容模型（原文锚:模型覆盖区）

### 3.3 与实际体验的差距

| 卖点 | 官网原文 | 实际体验 | 差距 |
|---|---|---|---|
| 平台支持 | 官网展示 Windows 和 macOS 下载 | Linux 无安装包，当前环境无法体验桌面端 | 开发者群体中 Linux 用户占比不低，缺失 Linux 版限制用户覆盖 |
| 信息开放度 | 首页展示完整产品定位 | Pricing/Models/Docs/Download/About 均需要登录 | 未登录用户无法了解定价和详细功能，门槛较高 |
| 下载体验 | "Download now"按钮醒目 | 点击后无下载触发，可能需登录后才可下载 | 下载流程不够顺畅 |

---

## 4. 定价

官网首页提到"Pay-as-you-go, balance never expires"和"Run premium models at a friendlier price than the official API"，但具体价格因 /pricing 页面需要登录而无法获取。从页面源码中未发现公开的价格表或费率信息。

---

## 5. 目标用户

基于官网用语和实际功能推断：

1. ** Claude Code / Codex 重度用户** — 官网明确以这两个工具为核心场景，"For heavy Claude Code work"直接点名
2. **中文开发者** — 邮箱白名单限制为 @qq.com，Firefox 标签页标题为中文"一键接入 · 按量计费"
3. **需要多模型切换的开发者** — Multi-account auto-switching 和 Multi-model 标签表明用户可能同时使用多个 AI 工具
4. **对 API 成本敏感的用户** — "Lower total cost"、"friendlier price than the official API"直接瞄准价格敏感型用户

---

## 6. 与同类产品对比

| 维度 | CheapRouter | 官方 Claude API / Codex API | OpenRouter 等通用路由 |
|---|---|---|---|
| 定位 | Claude Code + Codex 专用统一工作空间 | 各自独立，需分别配置 | 通用多模型路由，不针对特定工具 |
| 配置方式 | 桌面客户端自动写入本地配置 | 需手动配置 API key 和参数 | 通常需手动替换 base URL 和 key |
| 计费 | 统一余额，按量付费，余额不过期 | 各自独立计费 | 统一计费，但模式各异 |
| 平台 | Windows, macOS（无 Linux） | 无客户端，纯 API | 通常无专用桌面客户端 |

---

## 7. 优劣势小结

| 维度 | 优势 | 劣势 |
|---|---|---|
| 产品逻辑 | 专门针对 Claude Code + Codex 场景，自动本地配置降低使用门槛 | 无 Linux 版，限制开发者用户覆盖；强制登录才能查看定价和功能详情 |
| UI/UX | 官网信息架构清晰，卖点提炼精准；客户端深色 IDE 风格符合开发者审美 | 下载按钮交互反馈不明确；所有内页需登录，信息开放度低 |
| 工程质量 | 覆盖主流桌面平台（Windows x64/ARM64, macOS Intel/Apple Silicon）；多模型支持完整 | 未验证客户端实际稳定性；注册邮箱白名单限制过窄 |

---

## 附录 A 截图索引

| # | 文件 | 说明 |
|---|---|---|
| 01 | screenshots/01_web_homepage.png | 官网首页主视觉 |
| 02 | screenshots/02_web_homepage_scroll1.png | 应用界面预览（桌面客户端截图） |
| 03 | screenshots/03_web_homepage_scroll2.png | 平台能力区（按量付费说明） |
| 04 | screenshots/04_web_download_section.png | 下载区域（Windows/macOS） |
| 05 | screenshots/05_web_why_section.png | WHY CHEAPROUTER 三个核心卖点 |
| 06 | screenshots/06_web_footer.png | 模型覆盖范围（Claude/GPT/第三方） |
| 08 | screenshots/08_web_pricing.png | Pricing/Models 等内页统一登录入口 |

> 编号规则:`NN_<source>_<view>.png`,`source ∈ {web, app, android}`,`view` 短 kebab-case;`NN` 单调递增,允许跳号。