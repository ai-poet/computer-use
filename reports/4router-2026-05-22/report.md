# 4Router 产品分析报告

| 项目 | 值 |
|---|---|
| 官网 | https://4router.net |
| 下载链接 | — |
| 报告日期 | 2026-05-22 |
| 主机 | linux / x86_64 |
| Runtime | sandbox-local |
| 模式 | web-only |
| 用时 | 18分钟 |

> 本次为网页版分析 — 4Router 为纯 Web API 服务平台，官网未提供任何桌面客户端安装包（.dmg/.exe/.deb/AppImage 等），亦无 Android APK。用户通过 API 调用或 Web 控制台使用服务。

---

## 1. 详细的产品逻辑介绍

### 1.1 总定位

4Router 是一个 LLM API 路由与聚合服务平台，面向开发者提供统一接口访问多个大语言模型提供商（OpenAI、Anthropic、Google、Mistral 等）。核心解决"多模型接入碎片化"问题：开发者无需分别为每个模型提供商维护独立的 API 接入代码、认证方式和计费逻辑，通过 4Router 的单一端点即可按需调用不同模型。产品额外提供策略路由（按成本/延迟/质量自动选择）、请求可观测性和故障自动重试等工程化能力。

### 1.2 界面清单

按浏览顺序列出实际访问到的所有界面：

| # | 界面 | 入口 | 主要功能 | 截图 |
|---|---|---|---|---|
| 1 | 首页 | https://4router.net | 产品定位、支持模型展示、核心功能介绍 | [01_web_homepage.png](screenshots/01_web_homepage.png) |
| 2 | 功能介绍区 | 首页滚动 | Unified Access、Policy Routing、Observability、Reliable Delivery 四大功能 | [02_web_features.png](screenshots/02_web_features.png) |
| 3 | 模型定价 | https://4router.net/pricing | 各模型输入/输出 token 单价查询 | [03_web_pricing.png](screenshots/03_web_pricing.png) |
| 4 | 定价详情 | /pricing 滚动 | 更多模型（Claude、GPT 系列）价格 | [04_web_pricing_more.png](screenshots/04_web_pricing_more.png) |
| 5 | 关于/服务条款 | https://4router.net/about | 服务条款、隐私政策 | [05_web_about.png](screenshots/05_web_about.png) |
| 6 | 文档中心 | https://4router.net/docs | 一键配置教程、手动配置、环境变量、Claude Code 代理配置 | [06_web_docs.png](screenshots/06_web_docs.png) |
| 7 | 登录页 | https://4router.net/login | 用户名/密码登录、linuxDo 第三方登录 | [07_web_login.png](screenshots/07_web_login.png) |

### 1.3 各界面功能与评价

#### 1.3.1 首页

- **功能**：首屏展示品牌标识（橙色笑脸图标 + "4Router" 像素字体）、主标语 "Where language models cost less"、副标语 "Built for the ones who build"。下方以玻璃态卡片形式展示支持的模型提供商（OpenAI、Anthropic、Google 等）。再下方是四大核心功能卡片。
- **交互**：顶部导航栏包含 Home、Console、Model、Documentation、About、Sign In、Sign up。首次访问会弹出 System Notice 弹窗（可 ESC 关闭）。
- **评价**：首页设计简洁，信息层级清晰。但 System Notice 弹窗强制打断首屏体验，且弹窗内容偏向运营通知（加群领额度、模型升级公告），对新用户理解产品价值无直接帮助。标语中的 "cost less" 暗示了价格优势，但首页未直接展示与官方 API 的价格对比。
- **截图**：[01_web_homepage.png](screenshots/01_web_homepage.png)

#### 1.3.2 模型定价页

- **功能**：以列表形式展示所有可用模型的输入/输出 token 单价。左侧提供 Provider 筛选器（Anthropic、OpenAI、Mistral 等）和模型搜索框。支持 Table view 切换。
- **交互**：直接访问 /pricing 即可查看，无需登录。可筛选、搜索、切换视图。
- **评价**：定价信息透明，覆盖主流模型（GPT-4o、Claude 3.7 Sonnet、Claude Opus 等）。以人民币（¥）计价，面向中文用户。但页面未显示与官方 API 原价的对比，用户无法直观判断"cost less"的节省幅度。模型列表较长时无分页，全部平铺。
- **截图**：[03_web_pricing.png](screenshots/03_web_pricing.png)、[04_web_pricing_more.png](screenshots/04_web_pricing_more.png)

#### 1.3.3 文档中心

- **功能**：左侧导航包含教程、开始使用、手动配置、环境变量、模型定价、Claude Code 代理配置、Cloudflare 代理配置等章节。右侧为具体内容区。
- **交互**：点击左侧导航切换内容。文档为静态渲染，无需登录即可阅读。
- **评价**：文档结构合理，特别提供了 Claude Code 的代理配置教程，说明产品定位与 Claude Code 用户群体有重叠。但部分导航项点击后内容未刷新（可能是 SPA 路由问题），且文档页面 URL 为 /docs 而导航栏显示 Documentation（指向 /documentation，实际为 404），存在路由不一致。
- **截图**：[06_web_docs.png](screenshots/06_web_docs.png)

#### 1.3.4 登录页

- **功能**：提供用户名/邮箱 + 密码登录，支持"Forgot password"密码找回，以及 linuxDo 第三方登录。右侧为登录表单，左侧为品牌展示和 SIGN UP 注册入口。
- **交互**：Console 和 Model 导航项点击后均重定向至此登录页。注册按钮在左下角。
- **评价**：登录表单设计简洁，但无邮箱验证码登录选项（仅支持密码）。第三方登录仅提供 linuxDo（一个中文开发者社区），未提供 GitHub/Google 等国际常用 OAuth 提供商，国际化程度有限。
- **截图**：[07_web_login.png](screenshots/07_web_login.png)

---

## 2. UI/UX 风格和质量描述

### 2.1 视觉风格

整体采用深色主题（近黑色背景），搭配像素化马赛克纹理背景，营造"复古科技"氛围。品牌标识使用橙色笑脸图标和像素风格字体，与深色背景形成高对比度。内容卡片采用玻璃态（glassmorphism）设计：半透明深色背景 + 细边框 + 微弱高光，在像素背景上产生悬浮感。整体调性偏向开发者工具风格，有一定的极客/复古游戏感，不算企业级沉稳也不算消费级活泼。

### 2.2 信息密度与层级

首页首屏信息密度适中：品牌 + 标语 + 两个模型卡片占据主要视觉空间。四大功能卡片在第二屏，每个卡片标题 + 一句话描述，信息精炼。定价页信息密度较高：模型名称、版本、输入价格、输出价格、提供商标签全部平铺，无分页，长列表下略感拥挤。主要 CTA（Sign up）以橙色实心按钮置于导航栏右上角，对比度足够，一眼可辨。

### 2.3 交互流畅度

- 首页加载速度正常，从打开 URL 到首屏渲染约 2-3 秒
- 页面滚动无掉帧，玻璃态卡片渲染流畅
- 导航栏链接点击后，部分页面（/model、/documentation）返回 404，体验中断
- System Notice 弹窗首次访问必现，关闭后当日不再出现（"Close Today"）
- 无明显的加载指示器（spinner/skeleton），页面切换时为空白等待

### 2.4 文案质量

- 首页英文标语 "Where language models cost less" 与中文运营通知（"加群领取2刀额度"）混用，语言风格不统一
- 功能卡片文案为英文（Unified Access、Policy Routing 等），但文档为中文，存在中英文混杂
- "cost less" 暗示价格优势，但未在定价页提供与官方 API 的对比数据来支撑这一主张
- 服务条款页面为中文，符合国内法律合规要求

### 2.5 可访问性观察

- 深色背景 + 白色文字对比度足够，但玻璃态卡片上的浅灰色文字在复杂背景前可读性略降
- 未观察到键盘导航焦点指示器
- 未发现深色/浅色模式切换选项（仅深色主题）
- 弹窗关闭按钮（X）尺寸较小，约 16×16 像素

---

## 3. 官网描述

### 3.1 关键文案摘录

> "Where language models cost less" — 首页主标语

> "Built for the ones who build" — 首页副标语

> "4Router 提供超过 15 种模型，包括来自..." — 定价页说明

> "LLM is all your need" — 登录页品牌语

> "Unified Access: One key to unlock the world's top LLMs" — 功能卡片原文

> "Policy Routing: Smart model selection balancing quality, speed, and cost" — 功能卡片原文

> "Observability: Deep usage insights and tracking of every request" — 功能卡片原文

> "Reliable Delivery: Automatic retries and failover ensuring your requests always get through" — 功能卡片原文

### 3.2 核心卖点（官网视角）

1. **统一接入多家 LLM**：通过一个 API 密钥访问 OpenAI、Anthropic、Google 等 15+ 模型（原文锚：功能卡片 "Unified Access"）
2. **智能策略路由**：根据质量、速度、成本自动选择模型（原文锚：功能卡片 "Policy Routing"）
3. **请求可观测性**：深度使用洞察和每次请求的追踪（原文锚：功能卡片 "Observability"）
4. **可靠传输**：自动重试和故障转移确保请求始终送达（原文锚：功能卡片 "Reliable Delivery"）
5. **价格优势**：标语 "cost less" 暗示比官方 API 更便宜

### 3.3 与实际体验的差距

| 卖点 | 官网原文 | 实际体验 | 差距 |
|---|---|---|---|
| 统一接入 | "One key to unlock" | 定价页确实列出 15+ 模型 | 一致，但未验证实际 API 调用是否真正统一端点 |
| 价格优势 | "cost less" | 定价页展示价格，但无官方原价对比 | 无法验证"便宜"幅度，用户缺乏参照系 |
| 文档完整 | 导航栏有 Documentation | /documentation 返回 404，实际文档在 /docs | 路由不一致，Documentation 入口无效 |
| 模型页面 | 导航栏有 Model | /model 返回 404 | 该导航项无对应页面 |
| 控制台 | 导航栏有 Console | 重定向到登录页，未登录无法查看 | 需要登录，符合预期 |

---

## 4. 定价

4Router 采用按量计费模式，根据各模型的输入/输出 token 数量收费。定价以人民币（¥）标示，按每 1K tokens 计价。

**代表性模型定价**（来自定价页截图）：

| 模型 | 输入价格 (¥/1K tokens) | 输出价格 (¥/1K tokens) |
|---|---|---|
| gpt-4o | 0.0025 | 0.0100 |
| gpt-4o-mini | 0.00015 | 0.0006 |
| gpt-4.1 | 0.0020 | 0.0080 |
| gpt-4.1-mini | 0.0004 | 0.0016 |
| claude-3-7-sonnet | 0.0030 | 0.0150 |
| claude-sonnet-4-0 | 0.0020 | 0.0100 |
| claude-opus-4-1 | 0.0105 | 0.0525 |

**定价模式特点**：
- 无固定月费或订阅档位，纯按量计费
- 新用户可通过加群领取 2 美元额度（System Notice 弹窗信息）
- 价格以人民币标价，面向中文用户群体
- 未提供与 OpenAI/Anthropic 官方 API 的直接价格对比

---

## 5. 目标用户

基于官网用语和实际功能推断：

1. **中文开发者/技术团队**：人民币定价、中文文档、QQ 群运营、linuxDo 登录，均指向中文开发者社区
2. **Claude Code 用户**：文档中专设"Claude Code 代理配置"章节，说明该用户群体是目标用户之一
3. **多模型需求的应用开发者**：需要同时接入 GPT、Claude、Gemini 等多个模型，不愿维护多套接入代码
4. **成本敏感型用户**：标语 "cost less" 和免费额度暗示价格敏感用户

---

## 6. 与同类产品对比

| 对比维度 | 4Router | OpenRouter | One API |
|---|---|---|---|
| **定位** | LLM API 路由/聚合 | 开源 LLM 路由网关 | 开源 LLM API 聚合平台 |
| **部署方式** | SaaS（托管服务） | SaaS + 开源自托管 | 开源自托管为主 |
| **模型覆盖** | 15+（OpenAI、Anthropic、Google 等） | 200+（更广） | 取决于用户配置的渠道 |
| **定价展示** | 官网透明定价页 | 官网透明定价页 | 由部署者自行设定 |
| **中文支持** | 原生中文界面和文档 | 英文为主 | 中文原生（国内开源项目） |
| **社区运营** | QQ 群 + linuxDo | Discord + GitHub | GitHub Issues |
| **独特优势** | 开箱即用、Claude Code 集成教程 | 模型覆盖最广、社区生态成熟 | 开源免费、可私有化部署 |

---

## 7. 优劣势小结

| 维度 | 优势 | 劣势 |
|---|---|---|
| 产品逻辑 | 统一接入多模型，降低开发者接入成本；提供策略路由和可观测性工程能力 | 模型覆盖（15+）少于竞品 OpenRouter（200+）；"/model" 和 "/documentation" 页面 404 |
| UI/UX | 深色主题 + 玻璃态卡片视觉统一；定价页信息透明 | 首页弹窗强制打断体验；中英文文案混用；部分导航链接失效 |
| 工程质量 | 文档覆盖一键配置、手动配置、Claude Code 集成等场景 | 路由不一致（/docs 可用但 /documentation 404）；无加载状态指示 |
| 商业模式 | 按量计费灵活；人民币定价贴合国内用户 | 无订阅档位，高频用户成本不可控；价格对比官方 API 的节省幅度未展示 |

---

## 附录 A 截图索引

| # | 文件 | 说明 |
|---|---|---|
| 01 | screenshots/01_web_homepage.png | 官网首页，展示品牌、标语和模型卡片 |
| 02 | screenshots/02_web_features.png | 首页功能卡片区：Unified Access、Policy Routing、Observability、Reliable Delivery |
| 03 | screenshots/03_web_pricing.png | 模型定价页，展示 GPT-4o、Claude 3.7 Sonnet 等模型价格 |
| 04 | screenshots/04_web_pricing_more.png | 定价页滚动后更多模型（Claude Opus、GPT-4.1 系列） |
| 05 | screenshots/05_web_about.png | 关于页面，展示服务条款和隐私政策 |
| 06 | screenshots/06_web_docs.png | 文档中心，左侧导航含 Claude Code 代理配置等教程 |
| 07 | screenshots/07_web_login.png | 登录页，支持用户名/密码和 linuxDo 第三方登录 |
