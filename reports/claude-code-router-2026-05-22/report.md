# Claude Code Router 产品分析报告

| 项目 | 值 |
|---|---|
| 官网 | https://github.com/musistudio/claude-code-router |
| 下载链接 | `npm install -g @musistudio/claude-code-router` |
| 报告日期 | 2026-05-22 |
| 主机 | linux / x86_64 |
| Runtime | sandbox-local |
| 模式 | web-only |
| 用时 | ~15 分钟 |

> 本次为网页版分析，未驱动桌面端 — 该产品为 npm CLI 工具，无传统桌面安装包；沙盒内无 Node.js/npm 环境，无法安装运行 CLI。

---

## 1. 详细的产品逻辑介绍

### 1.1 总定位

Claude Code Router（简称 CCR）是一个基于 Node.js 的 CLI 代理层工具，安装在 Claude Code 与各类大模型 API 之间，充当"智能路由器"。它将 Claude Code 原本直连 Anthropic API 的请求，按用户定义的规则分发到 OpenRouter、DeepSeek、Ollama、Gemini、Volcengine 等 10 余家第三方模型提供商，同时通过内置的 request/response transformer 抹平不同 provider API 的格式差异。面向已经使用 Claude Code 进行日常开发、但希望灵活切换后端模型以控制成本或获得特定模型能力的开发者。

### 1.2 界面清单

按出现顺序列出实际看到的所有主要界面，每个一行，挂截图编号：

| # | 界面 | 入口 | 主要功能 | 截图 |
|---|---|---|---|---|
| 1 | GitHub 仓库首页 | https://github.com/musistudio/claude-code-router | 项目概览、文件树、Stars/Forks 统计、About 描述 | [01_web_homepage.png](screenshots/01_web_homepage.png) |
| 2 | README Features 区 | 首页向下滚动 | 核心功能列表：Model Routing、Multi-Provider、Transformers 等 | [02_web_features.png](screenshots/02_web_features.png) |
| 3 | README Installation 区 | Features 区下方 | 安装命令、配置说明、config.json 结构 | [03_web_installation.png](screenshots/03_web_installation.png) |
| 4 | 文档站点错误页 | musistudio.github.io/claude-code-router | 文档站点连接失败（PR_CONNECT_RESET_ERROR） | [04_web_docs_failed.png](screenshots/04_web_docs_failed.png) |

### 1.3 各界面功能与评价

#### 1.3.1 GitHub 仓库首页

- **功能**：展示项目元信息（34.2k stars、2.8k forks、355 commits、26 contributors）、代码文件树（packages/、docs/、examples/、scripts/、blog/ 等目录）、右侧 About 面板含项目描述与外部链接。
- **交互**：用户通过 GitHub 导航栏可在 Code/Issues/Pull requests/Discussions/Actions 间切换；点击文件树可浏览源码；About 面板提供文档站点外链（失效）。
- **评价**：作为开源项目的"门面"，信息密度适中，Stars 数量（34.2k）在同类型工具中处于较高水平，说明社区认可度强。但文档站点链接失效，对新用户不够友好。
- **截图**:[01_web_homepage.png](screenshots/01_web_homepage.png)

#### 1.3.2 README Features 区

- **功能**：列出 7 大核心功能模块，每个功能配有 1-2 句话的简要说明。包括：Model Routing（按场景路由到不同模型）、Multi-Provider Support（支持 10+ 提供商）、Request/Response Transformation（通过 transformers 适配不同 API）、Dynamic Model Switching（`/model` 命令动态切换）、CLI Model Management（`ccr model` 交互式管理）、GitHub Actions Integration（CI/CD 集成）、Plugin System（自定义 transformers）。
- **交互**：纯文本展示，无交互。用户阅读后向下滚动进入 Getting Started。
- **评价**：功能列表清晰、具体，每项都能对应到实际使用场景（如 background 任务用本地小模型省钱、think 任务用推理模型）。但缺乏架构图或流程图帮助理解"Router 在 Claude Code 和 API 之间的位置"。
- **截图**:[02_web_features.png](screenshots/02_web_features.png)

#### 1.3.3 README Installation 区

- **功能**：分步骤说明安装和配置流程。Step 1 要求先装 Claude Code（`npm install -g @anthropic-ai/claude-code`），Step 2 安装 Router（`npm install -g @musistudio/claude-code-router`），Step 3 创建 `~/.claude-code-router/config.json`。配置项涵盖 PROXY_URL、LOG/LOG_LEVEL、APIKEY、HOST、NON_INTERACTIVE_MODE、Providers 数组、Router 对象、API_TIMEOUT_MS 等。附带完整的 JSON 配置示例（含 OpenRouter、DeepSeek、Ollama、Gemini、Volcengine、ModelScope、DashScope、AIHubMix 等 8 个 provider 的示例）。
- **交互**：用户需复制命令到本地终端执行，手动创建和编辑配置文件。
- **评价**：安装说明步骤明确，配置示例非常丰富（几乎覆盖了主流中文/国际模型提供商），降低了上手门槛。但配置文件的复杂度较高（Provider + Router + Transformer 三层嵌套），对于不熟悉 JSON 的用户可能有一定门槛。项目提供了 `ccr ui`（Web UI）和 `ccr model`（交互式 CLI）作为配置的替代入口，这一点在 README 中有提及。
- **截图**:[03_web_installation.png](screenshots/03_web_installation.png)

---

## 2. UI/UX 风格和质量描述

### 2.1 视觉风格

GitHub 仓库页面遵循 GitHub 默认视觉规范，无自定义 CSS 或独立品牌站点。README 中使用了 emoji（✨、🚀、🤖、📝、❤️）作为章节标记，增加了可读性。整体风格偏向典型的开源开发者工具文档：技术导向、信息密度高、装饰元素少。

### 2.2 信息密度与层级

README 的信息架构合理：Features → Getting Started（Installation → Configuration → Running → UI Mode → CLI Management → Presets → Activate）→ Transformers → Router → Custom Router → GitHub Actions → Further Reading。首屏（首屏指的是 README 的前几个章节）即给出"这是什么、能做什么、怎么装"，符合开发者快速评估的需求。配置示例的 JSON 代码块较长（约 150 行），嵌套层级较深，对于快速浏览者来说是认知负担。

### 2.3 交互流畅度

GitHub 页面加载正常，但文档站点（musistudio.github.io/claude-code-router）连接失败（PR_CONNECT_RESET_ERROR），说明文档托管存在问题或域名解析异常。GitHub 仓库内的导航（Code/Commits/Issues 切换）为 GitHub SPA 标准行为，响应正常。

### 2.4 文案质量

README 为全英文撰写，语言准确、技术术语使用规范。有对应的中文版 README_zh.md（通过顶部徽章链接）。功能描述具体（如"Route requests to different models based on your needs (e.g., background tasks, thinking, long context)"），避免了空泛表述。 sponsors 部分（Z.ai GLM CODING PLAN）以 blockquote 形式置于 README 顶部，位置醒目但不喧宾夺主。

### 2.5 可访问性观察

作为 GitHub 托管页面，可访问性由 GitHub 平台保障。代码块使用了 fenced code blocks 和语法高亮。纯文本 README 不存在色彩对比度问题。无深色模式相关内容提及（CLI 工具的深色模式取决于终端设置）。

---

## 3. 官网描述

### 3.1 关键文案摘录

> "Use Claude Code as the foundation for coding infrastructure, allowing you to decide how to interact with the model while enjoying updates from Anthropic."
> — 来源：GitHub 仓库 About 面板

> "A powerful tool to route Claude Code requests to different models and customize any request."
> — 来源：README 引言

> "A powerful tool to route Claude Code requests to different models and customize any request."
> — 来源：README 顶部 blockquote

> "Progressive Disclosure of Agent Tools from the Perspective of CLI Tool Style"
> — 来源：README 顶部链接（项目设计哲学文章）

### 3.2 核心卖点（官网视角）

1. **多提供商模型路由**：一份配置即可在 Claude Code 中使用 OpenRouter、DeepSeek、Ollama、Gemini 等 10+ 提供商的模型（原文锚：README Features 第一条）
2. **Request/Response Transformer 系统**：内置 15+ transformers 自动适配不同 provider API 格式差异（原文锚：README Transformers 章节）
3. **场景化路由**：按 default/background/think/longContext/webSearch/image 等场景自动选择最优模型（原文锚：README Router 章节）
4. **GitHub Actions 集成**：在 CI/CD 流水线中触发 Claude Code 任务，支持非交互模式（原文锚：README GitHub Actions 章节）
5. **动态模型切换**：在 Claude Code 会话中通过 `/model` 命令实时切换后端模型（原文锚：README Features 第四条）

### 3.3 与实际体验的差距

| 卖点 | 官网原文 | 实际体验 | 差距 |
|---|---|---|---|
| Web UI 配置 | "`ccr ui` will open a web-based interface" | 沙盒内无法安装 Node.js，未实际运行 | 仅基于 README 描述和截图（/blog/images/ui.png），未验证实际 UI 体验 |
| 文档站点 | About 面板链接 musistudio.github.io | 连接失败（PR_CONNECT_RESET_ERROR） | 文档站点不可用，用户只能依赖 README 获取信息 |
| CLI 交互管理 | "`ccr model` provides an interactive interface" | 沙盒内无法运行 CLI | 未验证交互式 CLI 的实际体验 |

---

## 4. 目标用户

基于 README 用语和实际功能推断：

- **主要用户**：已使用 Claude Code 进行日常开发的软件工程师（需要安装 `@anthropic-ai/claude-code` 作为前置条件）
- **次要用户**：希望在 CI/CD 中使用 Claude Code 自动化的 DevOps/平台工程师（GitHub Actions 集成场景）
- **付费意愿**：用户需自备各模型提供商的 API key，Router 本身免费开源（MIT license），但使用第三方模型可能产生费用

---

## 5. 与同类产品对比

挑 1-3 个用户能想到的同类品对比：

| 维度 | Claude Code Router | aider（多模型 CLI 编辑器） | Cline（VS Code 插件） |
|---|---|---|---|
| 产品形态 | Claude Code 的代理层/npm CLI 包 | 独立 CLI 代码编辑器 | VS Code 插件 |
| 模型支持 | 通过 Router 配置任意 OpenAI-compatible API | 内置多提供商支持 | 内置多提供商支持 |
| 与 Claude Code 关系 | **依赖并扩展** Claude Code，不替代它 | 独立产品，不依赖 Claude Code | 独立产品，不依赖 Claude Code |
| 核心差异化 | 在 Claude Code 内部通过 `/model` 动态切换；场景化路由（background/think/longContext） | 多文件编辑、git 集成、代码重构 | IDE 内嵌、UI 交互、文件操作 |
| 使用门槛 | 需先装 Claude Code + 手写/用 UI 配 JSON | 直接安装即可使用 | 安装 VS Code 插件即可 |

CCR 的独特价值在于：**不替换 Claude Code 的生态位，而是在其之上增加"模型自由选择"能力**，让用户在享受 Anthropic 官方更新（如 Claude Code 的新功能）的同时，将后端模型请求分发到更便宜或更适合特定任务的提供商。

---

## 6. 优劣势小结

| 维度 | 优势 | 劣势 |
|---|---|---|
| 产品逻辑 | 定位精准（Claude Code 用户想换模型后端）；场景化路由（background/think/longContext/webSearch）设计合理；15+ 内置 transformer 覆盖主流 provider | 配置复杂度较高（Provider + Router + Transformer 三层嵌套 JSON）；依赖 Claude Code 前置安装，无法独立使用 |
| UI/UX | 提供 `ccr ui` Web UI 和 `ccr model` 交互式 CLI 作为配置的替代入口；README 示例丰富 | 文档站点不可用；无配置向导或可视化架构图帮助理解 Router 在请求链路中的位置 |
| 工程质量 | 34.2k stars 社区活跃；MIT 开源；TypeScript 96.3% 类型安全；26 位 contributors；支持环境变量插值保护 API key 安全 | 部分 transformer 标记为 experimental（gemini-cli、qwen-cli、rovo-cli）；GitHub Actions 示例中的 bun 安装方式增加了 CI 环境复杂度 |

---

## 附录 A 截图索引

| # | 文件 | 说明 |
|---|---|---|
| 01 | screenshots/01_web_homepage.png | GitHub 仓库首页全景 |
| 02 | screenshots/02_web_features.png | README Features 功能列表 |
| 03 | screenshots/03_web_installation.png | README Installation 和 Configuration 说明 |
| 04 | screenshots/04_web_docs_failed.png | 文档站点连接失败页面 |
