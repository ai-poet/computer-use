# NekoCode 产品分析报告

| 项目 | 值 |
|---|---|
| 官网 | https://nekocode.ai |
| 下载链接 | — |
| 报告日期 | 2026-05-22 |
| 主机 | linux / x86_64 |
| Runtime | sandbox-local |
| 模式 | web-only |
| 用时 | ~10 分钟 |

> 本次为网页版分析，未驱动桌面端 — Neko Code 是一款纯 Web API 中继服务，本身不提供桌面应用安装包；用户需通过 npm 安装 Claude Code CLI 后配置 `ANTHROPIC_BASE_URL` 来使用该服务。

---

## 1. 详细的产品逻辑介绍

### 1.1 总定位

Neko Code 是一款面向中文用户的 AI API 中继（relay）服务，兼容 OpenAI 与 Anthropic API 格式。用户注册账号获取 API Key 后，通过在 Claude Code CLI 的配置文件中设置 `ANTHROPIC_BASE_URL: "https://nekocode.ai"`，将原本直接发往 Anthropic 官方 API 的请求转发至 Neko Code 平台，由平台统一计费并提供多模型选择（含 Claude 系列与 OpenAI 系列）。产品核心解决的是国内用户访问 Anthropic API 的便捷性与支付（人民币结算）问题。

### 1.2 界面清单

| # | 界面 | 入口 | 主要功能 | 截图 |
|---|---|---|---|---|
| 1 | 官网首页 | https://nekocode.ai | Claude Code 配置向导、平台切换（macOS/Linux/Windows） | [01_web_homepage.png](screenshots/01_web_homepage.png) |
| 2 | 配置步骤区 | 首页滚动 | API 配置指南、settings.json 示例 | [02_web_features.png](screenshots/02_web_features.png) |
| 3 | 开始使用区 | 首页底部 | 运行 `claude` 命令启动 | [03_web_start_using.png](screenshots/03_web_start_using.png) |
| 4 | 定价页 | /pricing | 订阅套餐、模型按量计费价格表 | [04_web_pricing.png](screenshots/04_web_pricing.png) |
| 5 | 套餐详情 | 定价页滚动 | Pay as You Go / Pro / Max / Ultra / Mini 五档套餐 | [05_web_pricing_plans.png](screenshots/05_web_pricing_plans.png) |
| 6 | 模型定价 | 定价页底部 | Claude 6 模型 + OpenAI 9 模型的 token 单价表 | [06_web_pricing_models.png](screenshots/06_web_pricing_models.png) |
| 7 | 关于页 | /about | 产品简介、进入控制台入口 | [07_web_about.png](screenshots/07_web_about.png) |

### 1.3 各界面功能与评价

#### 1.3.1 官网首页

- **功能**：首页以 "Claude Code Configuration Guide" 为大标题，提供三步配置向导（安装 Claude Code → 添加 API 配置 → 开始使用）。支持 macOS / Linux / Windows 三平台切换，切换后展示对应平台的安装命令（实际命令内容一致，均为 `npm install -g @anthropic-ai/claude-code`）。
- **交互**：页面为单页滚动式，无多级导航。顶部 Navbar 含 Pricing、About、通知、深色模式切换、语言切换（EN）、Login 入口。
- **评价**：首页信息密度较低，首屏仅标题 + CTA + 平台切换器，配置步骤需滚动后才可见。对于新用户而言，"Neko 是什么"这个问题在首页没有得到直接回答（需点击 About 才知其是 API relay 服务）。平台切换器样式为 pill 形分段控件，视觉反馈明确。代码块配有 "Copy" 按钮，方便一键复制命令。
- **截图**：[01_web_homepage.png](screenshots/01_web_homepage.png)

#### 1.3.2 配置步骤区（首页滚动）

- **功能**：展示 `~/.claude/settings.json` 的完整配置示例，包含 `ANTHROPIC_AUTH_TOKEN` 和 `ANTHROPIC_BASE_URL: "https://nekocode.ai"` 两个关键字段。下方提示 "Replace your-api-key with API Key from console"。
- **交互**：代码块可一键复制，console 为可点击链接。
- **评价**：配置示例清晰，但缺少对 `ANTHROPIC_BASE_URL` 作用的解释（用户可能不理解为什么要改 base URL）。代码块使用深色主题，与页面浅色背景形成对比，可读性较好。
- **截图**：[02_web_features.png](screenshots/02_web_features.png)

#### 1.3.3 定价页

- **功能**：分上下两部分。上半部分为 Subscription Plans，提供 5 个档位：Pay as You Go（按量计费，无最低消费）、Pro（$299/30 天，日配额 $20）、Max（$689/30 天，日配额 $50，Recommended）、Ultra（$1199/30 天，日配额 $100）、Mini（$14.90/3 天，日配额 $10，New User Exclusive）。下半部分为 Models 按量计费表，列出 Claude 6 个模型与 OpenAI 9 个模型的 Input/Output/Cache Read/Cache Write 单价。
- **交互**：套餐卡片直观，Pro/Max/Ultra 均标有 "Sold Out" 标签。模型表可横向滚动（在窄屏下）。
- **评价**：定价透明度较高，按 token 计费细则完整列出。但 Pro/Max/Ultra 全部 Sold Out 的状态对新用户不太友好——只剩下 Pay as You Go 和 Mini 可选。Billing Note 中注明 "Top-up settled in CNY. Current exchange rate: 1 USD = 1 CNY"，暗示平台主要面向人民币支付用户。模型名称使用了未来日期的版本号（如 `claude-opus-4-5-20251101`），与 Anthropic 官方命名不一致，可能引起混淆。
- **截图**：[04_web_pricing.png](screenshots/04_web_pricing.png)、[05_web_pricing_plans.png](screenshots/05_web_pricing_plans.png)、[06_web_pricing_models.png](screenshots/06_web_pricing_models.png)

#### 1.3.4 关于页

- **功能**：一句话定义 "Neko is an AI API relay service compatible with OpenAI and Anthropic API formats"，并提供 "Enter Console" 按钮跳转到用户控制台。
- **交互**：页面极简，无多余信息。
- **评价**：信息过少。对于一个 API 中继服务，About 页至少应该说明服务商背景、数据隐私政策、API 可用性保障等信任要素，目前这些全部缺失。
- **截图**：[07_web_about.png](screenshots/07_web_about.png)

---

## 2. UI/UX 风格和质量描述

### 2.1 视觉风格

整体采用极简主义风格，以黑白为主色调，辅以紫色（Recommended 标签）和红色（Sold Out 标签）作为点缀。字体为无衬线体，标题使用粗体大字，代码块使用等宽字体 + 深色背景。整体调性偏向开发者工具风，没有多余的装饰元素。

### 2.2 信息密度与层级

首屏信息量偏少，仅一个大标题 + 一个 CTA + 平台切换器。配置步骤（产品核心使用流程）被放在首屏下方，需要滚动才能看到。定价页的模型价格表信息密度较高，但表头固定、列对齐良好，扫描成本可控。主要 CTA（"Get Started"、"Login to Top Up"、"Enter Console"）使用深色填充按钮，在浅色背景下对比度充足，一眼可辨。

### 2.3 交互流畅度

- 页面加载速度较快，无明显白屏时间。
- SPA 路由切换（Pricing / About）通过地址栏导航实现，页面内容即时刷新。
- 每次进入新页面时会出现 "System Notice" 弹窗（展示可用分组和注意事项），需要手动关闭后才能查看页面内容。该弹窗反复出现，打断浏览流程。
- 代码块的 "Copy" 按钮有 hover 反馈（光标变化）。
- 平台切换器（macOS / Linux / Windows）选中态为深色填充，未选中态为浅色描边，状态清晰。

### 2.4 文案质量

官网文案以英文为主，少量中文（如 System Notice 中的注意事项）。首页标题 "Claude Code Configuration Guide" 准确描述了页面功能，但缺少对 "Neko" 品牌本身的介绍。定价页文案 "Pay-as-you-go with transparent pricing" 简洁明了。System Notice 中的中文文案存在重复（"禁止使用探针监控 ClaudeCode-MAX 系列分组！" 重复三次），显得粗糙。整体文案风格偏技术文档，情感表达较少。

### 2.5 可访问性观察（肉眼可见的）

- 文字与背景对比度整体充足，代码块深色背景上的浅色文字对比度良好。
- 未观察到明显的键盘导航支持（如 Skip Link、焦点轮廓等）。
- 深色模式切换按钮存在，但当前分析在浅色模式下完成。
- System Notice 弹窗的关闭按钮（X）尺寸较小，可能不利于触屏操作。

---

## 3. 官网描述

### 3.1 关键文案摘录

> "Neko is an AI API relay service compatible with OpenAI and Anthropic API formats."
> — 来源: About 页

> "Register an account to get your API Key and configure it in your application to get started."
> — 来源: About 页

> "Pay-as-you-go with transparent pricing. Or choose a subscription for daily quota."
> — 来源: Pricing 页 H1 下方

> "Prices in USD, billed by actual usage. Top-up settled in CNY. Current exchange rate: 1 USD = 1 CNY"
> — 来源: Pricing 页 Billing Note

### 3.2 核心卖点（官网视角）

1. **兼容双格式 API**：同时兼容 OpenAI 和 Anthropic API 格式（原文锚: About 页首句）。
2. **透明定价**：按 token 计费，价格公开可查（原文锚: Pricing 页副标题）。
3. **订阅套餐选择**：提供多档位日配额套餐，适合不同用量用户（原文锚: Pricing 页 Subscription Plans）。
4. ** Claude Code 配置向导**：三步完成配置，支持三大桌面平台（原文锚: 首页标题与配置步骤）。

### 3.3 与实际体验的差距

| 卖点 | 官网原文 | 实际体验 | 差距 |
|---|---|---|---|
| 多模型选择 | Pricing 页列出 Claude 6 模型 + OpenAI 9 模型 | 模型名称使用非官方命名（如 `claude-opus-4-5-20251101`） | 模型标识与官方不一致，用户难以确认对应关系 |
| 订阅套餐 | "Choose a plan that suits you" | Pro/Max/Ultra 全部 Sold Out，仅剩 Pay as You Go 和 Mini | 可选套餐极少，实际选择空间受限 |
| 平台支持 | macOS / Linux / Windows 三平台切换 | 切换后安装命令完全一致 | 平台切换器实际无差异化内容，形式大于实质 |

---

## 4. 定价

Neko Code 采用「按量计费 + 订阅套餐」双轨模式：

**按量计费（Pay as You Go）**：
- Claude 系列：haiku $1/$5 per 1M tokens（input/output），sonnet $3/$15，opus $5/$25
- OpenAI 系列：gpt-5.1 $1.25/$10 per 1M tokens，gpt-5.5 $5/$30
- Cache Read/Write 单独计价（仅 Claude 模型支持）

**订阅套餐**：

| 套餐 | 价格 | 有效期 | 日配额 | 总价值 | 状态 |
|---|---|---|---|---|---|
| Mini | $14.90 | 3 天 | $10 | $30 | 新用户专属，限 1 次 |
| Pro | $299.00 | 30 天 | $20 | $600 | Sold Out |
| Max | $689.00 | 30 天 | $50 | $1500 | Sold Out |
| Ultra | $1199.00 | 30 天 | $100 | $3000 | Sold Out |

- 结算货币：充值以人民币（CNY）结算，汇率为 1 USD = 1 CNY（固定汇率）。
- 日配额每日午夜重置。

---

## 5. 目标用户

基于官网用语与实际功能推断：

1. **国内 Claude Code 用户**：网站以中文 System Notice 为主，充值以人民币结算，明确面向中国大陆用户群体。
2. **开发者 / 技术从业者**：产品形态为 API relay，配置方式涉及 npm、settings.json、环境变量等，非技术用户难以独立完成。
3. **高频 Claude Code 使用者**：订阅套餐的日配额机制（$20–$100/天）暗示目标用户为每日大量使用 Claude Code 的重度用户，而非偶尔尝鲜的轻量用户。

---

## 6. 优劣势小结

| 维度 | 优势 | 劣势 |
|---|---|---|
| 产品逻辑 | 解决国内用户访问 Anthropic API 的支付与网络痛点；兼容 OpenAI + Anthropic 双格式 | 本质是 API 中转层，无自有模型能力；依赖上游 Anthropic/OpenAI 的稳定性 |
| UI/UX | 定价透明，按 token 计费表完整可查；配置向导三步完成，降低上手门槛 | 官网信息架构偏弱（首页不解释产品是什么）；System Notice 弹窗反复打断浏览；模型命名与官方不一致 |
| 工程质量 | 支持 Claude Code 全平台配置（macOS/Linux/Windows）；提供 Copy 按钮等细节体验 | Pro/Max/Ultra 套餐全部 Sold Out，资源紧张；About 页信息极少，缺乏隐私政策与服务保障说明 |

---

## 附录 A 截图索引

| # | 文件 | 说明 |
|---|---|---|
| 01 | screenshots/01_web_homepage.png | 官网首页全景（Claude Code Configuration Guide） |
| 02 | screenshots/02_web_features.png | 首页 API 配置步骤（settings.json 示例） |
| 03 | screenshots/03_web_start_using.png | 首页底部开始使用区（运行 claude 命令） |
| 04 | screenshots/04_web_pricing.png | 定价页顶部（套餐概览） |
| 05 | screenshots/05_web_pricing_plans.png | 定价页套餐详情（五档套餐） |
| 06 | screenshots/06_web_pricing_models.png | 定价页模型计费表 + Billing Note |
| 07 | screenshots/07_web_about.png | 关于页（产品定义与 Enter Console 入口） |
