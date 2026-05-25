# 9Router 产品分析报告

| 项目 | 值 |
|---|---|
| 官网 | https://ai-bot.cn/9router |
| 下载链接 | npm install -g 9router |
| 报告日期 | 2026-05-22 |
| 主机 | linux / x86_64 |
| Runtime | sandbox-local |
| 模式 | web-only |
| 用时 | 约 25 分钟 |

> 本次为网页版分析 — 9Router 为 npm CLI 工具（`npm install -g 9router`），运行后提供本地 Web Dashboard；Linux 沙盒中无 Node.js 环境且无法安装，故仅基于官网、GitHub 仓库及 npm 页面完成分析。

---

## 1. 详细的产品逻辑介绍

### 1.1 总定位

9Router 是一款开源的 AI 编程路由代理工具，以本地运行的方式将 Claude Code、Cursor、Copilot 等主流 AI 编程工具的 API 请求智能调度到 40+ 提供商的 100+ 模型，通过三层路由策略（订阅额度 → 低成本模型 → 免费模型）实现零停机自动降级，并内置 RTK Token Saver 技术压缩 tool_result 以节省 20–40% 的 token 消耗。目标用户为重度使用 AI 编程工具的开发者，尤其是那些同时使用多个 AI 服务、希望优化成本并避免速率限制干扰工作流的用户。

### 1.2 界面清单

按信息采集顺序列出：

| # | 界面 | 入口 | 主要功能 | 截图 |
|---|---|---|---|---|
| 1 | ai-bot.cn 产品页 | https://ai-bot.cn/9router | 第三方聚合站的中文产品介绍、功能概述、定价对比 | [01_web_aibot_homepage.png](screenshots/01_web_aibot_homepage.png) |
| 2 | GitHub 仓库首页 | https://github.com/tulip-ai2/9router-local | README、代码文件、项目元信息 | [06_web_github_repo.png](screenshots/06_web_github_repo.png) |
| 3 | GitHub README | 仓库首页向下滚动 | 产品定位、How It Works 架构图、Quick Start | [07_web_github_readme.png](screenshots/07_web_github_readme.png) |
| 4 | GitHub 功能详述 | README 继续滚动 | 问题痛点、解决方案、支持的 CLI 工具与提供商 | [08_web_github_solutions.png](screenshots/08_web_github_solutions.png) |
| 5 | GitHub 架构图 | README 技术原理区 | 三层路由策略图示：CLI → localhost:20128 → 三层模型 | [10_web_github_architecture.png](screenshots/10_web_github_architecture.png) |
| 6 | npm 包页面 | https://www.npmjs.com/package/9router | 安装命令、下载统计、版本信息、功能亮点 | [14_web_npm_package.png](screenshots/14_web_npm_package.png) |

### 1.3 各界面功能与评价

#### 1.3.1 ai-bot.cn 产品聚合页

- **功能**: 作为第三方中文 AI 工具导航站的产品详情页，提供 9Router 的中文概述、核心功能、技术原理、使用方法、定价对比等信息。
- **交互**: 页面采用左侧分类导航 + 中间内容区 + 右侧推荐栏的三栏布局。用户通过滚动阅读完整内容，无复杂交互。
- **评价**: 信息组织较为清晰，"9Router 的主要功能""技术原理""如何使用""同类产品对比"等章节分层明确。但页面夹杂较多右侧广告/推荐内容，信息密度被稀释；且作为第三方聚合站，内容更新可能滞后于官方仓库。截图 [02_web_aibot_overview.png](screenshots/02_web_aibot_overview.png) 可见页面主体内容区宽度较窄，约占总宽度的 50%。

#### 1.3.2 GitHub 仓库首页

- **功能**: 展示项目代码结构、README 文档、License（MIT）、最近提交记录。README 包含产品定位、How It Works 架构图、Quick Start 安装指南、Features 详细说明。
- **交互**: 通过 Tab 切换 Code / Issues / Pull requests / Actions 等视图；README 内点击锚点跳转各章节；点击文件进入代码浏览。
- **评价**: README 结构清晰，从问题痛点 → 解决方案 → 安装步骤 → 功能详述层层递进。How It Works 的 ASCII 架构图直观展示了三层路由策略（[10_web_github_architecture.png](screenshots/10_web_github_architecture.png)）。但项目目前 0 stars、0 forks、0 contributors（截图 [06_web_github_repo.png](screenshots/06_web_github_repo.png)），社区活跃度极低，可能为新近迁移或更名的仓库。提交记录显示仅 2 commits，last month 更新。

#### 1.3.3 npm 包页面

- **功能**: 展示包元信息（版本 0.4.59、MIT License、194 versions）、周下载量（54,305）、安装命令、功能亮点。
- **交互**: Readme / Code / Dependencies 等 Tab 切换；可查看版本历史。
- **评价**: 页面信息密度高，核心数据（下载量、版本、License）一目了然。截图 [14_web_npm_package.png](screenshots/14_web_npm_package.png) 显示周下载量 54,305 且呈上升趋势，说明有一定的用户采用度。页面同时展示了 Docker pulls（9.3k）和 GHCR 链接，说明项目支持容器化部署。发布时间显示为 "12 hours ago"，版本迭代非常活跃。

---

## 2. UI/UX 风格和质量描述

### 2.1 视觉风格

9Router 本身为 CLI 工具 + 本地 Web Dashboard，未采集到 Dashboard 的实际界面。从产品外围材料观察：

- **GitHub README**: 采用标准的 GitHub Markdown 文档风格，以文字 + ASCII 架构图 + badge 为主，无自定义视觉设计。badge 包含 npm 版本、月下载量、Docker pulls、License 等信息，配色为标准的 shields.io 风格（截图 [07_web_github_readme.png](screenshots/07_web_github_readme.png)）。
- **ai-bot.cn 页面**: 采用中文工具聚合站的通用模板，左侧深色分类导航栏，中间白色内容区，右侧广告/推荐栏。内容区使用标准的标题-段落-表格排版，无特殊视觉设计（截图 [02_web_aibot_overview.png](screenshots/02_web_aibot_overview.png)）。

### 2.2 信息密度与层级

- **GitHub README**: 信息密度高，从问题定义 → 解决方案 → 安装 → 功能详述层层递进，层级清晰。但支持的 CLI Tools 和 Providers 使用表格展示（截图 [11_web_github_clitools.png](screenshots/11_web_github_clitools.png)、[12_web_github_providers.png](screenshots/12_web_github_providers.png)），在 GitHub 默认样式下阅读体验尚可。
- **ai-bot.cn**: 信息层级通过 H2/H3 标题划分，"主要功能""技术原理""使用方法""核心优势"等章节明确。但右侧推荐栏占据了约 30% 的宽度，导致正文区域偏窄。

### 2.3 交互流畅度

- 产品本身为 CLI 工具，启动后应提供本地 Web Dashboard（http://localhost:20128/dashboard），但未能在沙盒中实际体验。从 README 描述判断，Dashboard 应提供 Providers 配置、OAuth 登录、配额监控等功能。
- npm 安装命令为 `npm install -g 9router`，启动命令为 `9router`，操作门槛对熟悉 Node.js 的开发者较低。

### 2.4 文案质量

- **GitHub README 英文文案**: 简洁直接，善用短句和列表。标语 "Never stop coding. Auto-route to FREE & cheap AI models with smart fallback." 一句话说清价值主张。"Stop wasting money and hitting limits" 痛点描述准确（截图 [08_web_github_solutions.png](screenshots/08_web_github_solutions.png)）。
- **ai-bot.cn 中文文案**: 翻译质量尚可，但部分术语存在不一致，如 "RTK Token Saver" 未给出中文解释，"智能降级" 与 "自动降级" 混用。"开源 AI 编程路由代理工具" 的定位描述较为准确。

### 2.5 可访问性观察

- GitHub 和 npm 页面均依赖平台自身的可访问性支持，无特殊 a11y 问题。
- ai-bot.cn 页面文字对比度正常，但右侧广告区可能存在动态内容干扰阅读。

---

## 3. 官网描述

### 3.1 关键文案摘录

> "Never stop coding. Auto-route to FREE & cheap AI models with smart fallback." — GitHub README H1 下方标语（截图 [07_web_github_readme.png](screenshots/07_web_github_readme.png)）

> "Connect All AI Code Tools (Claude Code, Cursor, Antigravity, Copilot, Codex, Gemini, OpenCode, Cline, OpenClaw...) to 40+ AI Providers & 100+ Models." — GitHub README（截图 [07_web_github_readme.png](screenshots/07_web_github_readme.png)）

> "Save 20-40% tokens with RTK + auto-fallback to FREE & cheap AI models." — npm 页面副标题（截图 [14_web_npm_package.png](screenshots/14_web_npm_package.png)）

> "9Router 是开源的 AI 编程路由代理工具，接入 40+ 模型提供商，支持 100+ 模型，三大特性：智能调度、自动降级、多账户管理。" — ai-bot.cn 首页（截图 [02_web_aibot_overview.png](screenshots/02_web_aibot_overview.png)）

### 3.2 核心卖点（官网视角）

1. **智能路由与自动降级**: 三层路由策略（订阅 → 低成本 → 免费）确保零停机（GitHub README "How It Works" 节）。
2. **RTK Token Saver**: 自动压缩 tool_result，节省 20-40% token（npm 页面副标题）。
3. **广泛兼容**: 支持 Claude Code、Cursor 等 12+ 主流 AI 编程工具，40+ 提供商，100+ 模型（GitHub README Supported CLI Tools / Providers 节）。
4. **多账户轮询**: 同一提供商支持多账户，避免速率限制（GitHub README "Multi-account" 节）。
5. **灵活部署**: 支持 localhost、VPS、Docker、Cloudflare Workers（GitHub README Key Features 表格）。

### 3.3 与实际体验的差距

| 卖点 | 官网原文 | 实际体验 | 差距 |
|---|---|---|---|
| 社区活跃度 | GitHub 公开仓库 | 0 stars, 0 forks, 0 contributors, 仅 2 commits | 项目极新或刚迁移，社区尚未建立 |
| 版本迭代 | npm v0.4.59 | 194 versions，12 小时前发布 | 版本号高但提交记录少，版本历史可能来自更名前的包 |
| Dashboard 体验 | "Dashboard opens at http://localhost:20128" | 沙盒中无法安装 Node.js，未实际体验 Dashboard | 无法验证 Dashboard 的 UI/UX 质量 |

---

## 4. 定价

9Router 本身为开源免费软件（MIT License），采用 npm 包形式分发。实际使用成本取决于用户配置的 AI 提供商：

- **免费层**: iFlow AI（8+ models, Unlimited）、Qwen Code（3+ models, Unlimited）、Gemini CLI（180K/month FREE）、Kiro AI（Claude, Unlimited）
- **低成本层**: GLM（$0.6/1M tokens）、MiniMax（$0.2/1M tokens）
- **订阅层**: Claude Code、Codex、Gemini CLI 等（用户自行订阅）

产品核心价值在于帮助用户"最大化订阅价值"——在订阅额度用尽前充分使用，然后自动降级到低成本/免费选项，避免"每月配额未用完就过期"的浪费。

---

## 5. 目标用户

基于官网用语与实际功能推断：

1. **重度 AI 编程工具用户**: 同时使用 Claude Code、Cursor、Copilot 等多个工具，每月在各平台间手动切换以应对配额限制（证据：README 列出的 12+ 支持工具）。
2. **成本敏感型开发者/团队**: 希望优化 AI API 支出，避免为多个提供商支付重复订阅费（证据："Save 20-40% tokens"、"Stop wasting money" 文案）。
3. **自托管偏好者**: 希望数据不经过第三方 SaaS，在本地或自有 VPS 上运行路由服务（证据：支持 localhost、Docker、Cloudflare Workers 部署）。

---

## 6. 与同类产品对比

| 维度 | 9Router | OpenRouter | LiteLLM |
|---|---|---|---|
| **定位** | 开源 AI 编程路由代理工具，面向开发者个人/小团队 | 统一 API 路由服务，SaaS 为主 | 企业级 AI 网关，面向团队/企业 |
| **开源程度** | 完全开源（MIT），GitHub 仓库 | 部分开源 | 完全开源（GitHub） |
| **部署方式** | 本地、VPS、Docker、Cloudflare Workers | 云端 SaaS（API 调用） | 本地、Docker、Kubernetes |
| **核心差异化** | RTK Token Saver、三层智能降级、多账户轮询 | 统一 API 格式、部分模型免费 | 企业级监控、RBAC、预算控制 |
| **支持模型数** | 100+ | 200+ | 200+ |
| **免费额度** | 依赖各提供商免费层（iFlow、Qwen、Gemini CLI 等） | 部分模型免费 | 无 |
| **Token 优化** | RTK 自动压缩 tool_result，省 20-40% | 无明确优化 | 缓存、批处理等企业级优化 |

**关键差异**: 9Router 的 RTK Token Saver 和"订阅 → 便宜 → 免费"三层降级策略是其区别于 OpenRouter 和 LiteLLM 的核心卖点；而 OpenRouter 的 SaaS 模式更方便即用，LiteLLM 的企业级功能（RBAC、预算管理）更适合大型团队。

---

## 7. 优劣势小结

| 维度 | 优势 | 劣势 |
|---|---|---|
| 产品逻辑 | 三层智能降级策略设计精巧，RTK Token Saver 有实际成本节省价值；支持 12+ 主流 AI 编程工具，兼容性好 | 项目极新（GitHub 0 stars/0 forks），长期维护存疑；依赖各提供商 API 稳定性 |
| UI/UX | CLI 安装简单（npm install -g），Web Dashboard 应提供可视化配置 | 未实际体验 Dashboard；CLI 工具对非技术用户门槛高；无传统 GUI 应用 |
| 工程质量 | 194 个 npm 版本说明迭代活跃；支持 Docker/Cloudflare Workers 多种部署；MIT License 友好 | GitHub 仅 2 commits，代码历史与版本号不匹配，可能为更名/迁移项目；无测试覆盖率等工程指标公开 |

---

## 附录 A 截图索引

| # | 文件 | 说明 |
|---|---|---|
| 01 | screenshots/01_web_aibot_homepage.png | ai-bot.cn 9Router 页面首页 |
| 02 | screenshots/02_web_aibot_overview.png | ai-bot.cn 清理弹窗后的产品概览 |
| 03 | screenshots/03_web_aibot_features.png | ai-bot.cn 主要功能介绍 |
| 04 | screenshots/04_web_aibot_tech.png | ai-bot.cn 技术原理与使用方法 |
| 05 | screenshots/05_web_aibot_comparison.png | ai-bot.cn 同类产品对比入口 |
| 06 | screenshots/06_web_github_repo.png | GitHub 仓库首页与文件结构 |
| 07 | screenshots/07_web_github_readme.png | GitHub README 标题与核心描述 |
| 08 | screenshots/08_web_github_solutions.png | GitHub README 问题痛点与解决方案 |
| 09 | screenshots/09_web_github_quickstart.png | GitHub README Quick Start 安装指南 |
| 10 | screenshots/10_web_github_architecture.png | GitHub README How It Works 架构图 |
| 11 | screenshots/11_web_github_clitools.png | GitHub README 支持的 CLI 工具列表 |
| 12 | screenshots/12_web_github_providers.png | GitHub README 支持的提供商列表 |
| 13 | screenshots/13_web_github_keyfeatures.png | GitHub README Key Features 功能表格 |
| 14 | screenshots/14_web_npm_package.png | npm 包页面元信息与下载统计 |
| 15 | screenshots/15_web_npm_features.png | npm 页面 Why 9Router 功能亮点 |
| 16 | screenshots/16_web_aibot_detail.png | ai-bot.cn 主要功能详细说明 |
| 17 | screenshots/17_web_aibot_techdetail.png | ai-bot.cn 技术原理详细说明 |
| 18 | screenshots/18_web_aibot_advantages.png | ai-bot.cn 核心优势 |
| 19 | screenshots/19_web_aibot_table.png | ai-bot.cn 同类产品对比表格 |
