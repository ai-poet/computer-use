# 88code 产品分析报告

| 项目 | 值 |
|---|---|
| 官网 | https://www.88code.org |
| 下载链接 | — |
| 报告日期 | 2026-05-22 |
| 主机 | linux / x86_64 |
| Runtime | sandbox-local |
| 模式 | web-only |
| 用时 | ~15 分钟 |

> 本次为网页版分析，未驱动桌面端 — 88code.org 官网返回 403 "This site is not available in your region"，所有路径均被地域限制屏蔽。通过关联平台 InsCode (快马) 及 TaoToken 获取产品信息。

---

## 1. 详细的产品逻辑介绍

### 1.1 总定位

88CODE 是集成在 InsCode (快马) 平台上的 AI 代码生成工具，面向编程初学者和需要快速原型的开发者。用户通过自然语言描述需求（如"创建一个计算器"），AI 自动生成可运行的 Python 代码，并附带逐行注释、实现原理说明和优化建议。产品核心是降低编程门槛，将"想法到可运行代码"的时间从小时级压缩到分钟级。

88code.org 作为产品官网，目前处于地域限制状态（Photon-Edge CDN 拦截），实际产品入口在 InsCode 平台（inscode.net）。TaoToken（taotoken.net）为其关联的 Token 计费平台，提供大模型 API 的折扣接入服务。

### 1.2 界面清单

按出现顺序列出实际看到的所有主要界面：

| # | 界面 | 入口 | 主要功能 | 截图 |
|---|---|---|---|---|
| 1 | 官网首页(403) | https://www.88code.org | 地域限制拦截页，显示 403 和品牌标识 | [01_web_homepage.png](screenshots/01_web_homepage.png) |
| 2 | InsCode 首页 | https://inscode.net | AI 应用生成入口，自然语言输入框，快捷模板 | [02_web_inscode_home.png](screenshots/02_web_inscode_home.png) |
| 3 | InsCode 项目模板 | 首页滚动下方 | 展示社区模板：语音故事机、发票拍立得、AI 智能三合一应用等 | [03_web_inscode_templates.png](screenshots/03_web_inscode_templates.png) |
| 4 | InsCode AI 工作区 | 点击模型/项目后进入 | 代码编辑区 + AI 聊天面板 + 预览/运行区 | [04_web_inscode_workspace.png](screenshots/04_web_inscode_workspace.png) |
| 5 | InsCode 工作区(滚动) | 工作区内滚动 | 展示代码调试建议、文件上传区、AI 交互输入框 | [05_web_inscode_workspace_scroll.png](screenshots/05_web_inscode_workspace_scroll.png) |
| 6 | TaoToken 首页 | https://taotoken.net | 大模型 API 接入平台，Token 计费入口 | [06_web_taotoken_home.png](screenshots/06_web_taotoken_home.png) |
| 7 | TaoToken 模型定价 | 模型列表页 | 各模型输入/输出价格，限时半价活动 | [07_web_taotoken_pricing.png](screenshots/07_web_taotoken_pricing.png) |
| 8 | TaoToken 定价(滚动) | 模型列表页滚动 | 更多模型价格：Claude-Sonnet、DeepSeek V4-Flash 等 | [08_web_taotoken_pricing_scroll.png](screenshots/08_web_taotoken_pricing_scroll.png) |

### 1.3 各界面功能与评价

#### 1.3.1 官网首页(403 拦截页)

- **功能**：展示 403 错误和品牌标识。页面标题为"403"，主体显示"This site is not available in your region"，右下角有"88code"品牌标识。使用 Photon-Edge CDN 服务，服务器位于日本边缘节点（jpn-pre.edge-cluster-jp-pre.com）。
- **交互**：访问 https://www.88code.org 时自动 301 重定向至 www.88code.ai，随后返回 403。/about、/pricing 等所有子路径同样返回 403。
- **评价**：网站做了严格的地域限制，从沙盒环境（Linux/Docker）完全无法访问任何内容。403 页面设计简洁，支持深色模式（通过 prefers-color-scheme 媒体查询），有基本的品牌露出。但作为一个产品官网，完全屏蔽非目标地区用户会影响产品传播和口碑。
- **截图**:[01_web_homepage.png](screenshots/01_web_homepage.png)

#### 1.3.2 InsCode 首页

- **功能**：InsCode (快马) 是 88CODE 的实际宿主平台。首页核心是一个自然语言输入框，placeholder 文案为"告诉 InsCode 你的创意，快速将你的创意变为应用"。输入框支持图片上传和语音输入。右侧有模型选择器（默认 Qwen3.5-Plus）和"生成项目"按钮。下方提供 5 个快捷入口模板：语音故事机、发票拍立得、自拍漫改、闪电简历、抽奖转盘。
- **交互**：用户输入需求描述后点击"生成项目"，AI 生成完整项目代码。也可点击快捷模板直接体验预设场景。顶部导航栏包含：首页、项目、权益、模型市场。
- **评价**：首页信息密度适中，核心输入框占据视觉中心，CTA 明确。Slogan"一句话 / 一个链接，几分钟生成可以发布的产品"清晰传达了产品价值。但"权益"页面需登录才能查看，未登录用户无法了解定价信息。导航栏"项目"按钮外链至 TaoToken，跳转逻辑不够直观。
- **截图**:[02_web_inscode_home.png](screenshots/02_web_inscode_home.png)

#### 1.3.3 InsCode 项目模板区

- **功能**：首页下方展示社区用户创建的模板项目，以卡片网格形式排列。可见模板包括：海龟粒子爱心代码网页、Scratch 改造传统坦克游戏、经典转盘抽奖前端实现、AI 智能三合一应用、多 LLM TextGen 网页工具、AI 写作提示工具等。每张卡片展示项目缩略图、标题和简要描述。
- **交互**：点击卡片可进入对应项目的预览或编辑页面。
- **评价**：模板区丰富了首页内容，给新用户提供了"不知道写什么"时的灵感来源。卡片式布局视觉统一，缩略图质量参差不齐（部分为代码截图，部分为设计图）。模板覆盖前端页面、小游戏、工具类应用等，展示了平台的能力边界。
- **截图**:[03_web_inscode_templates.png](screenshots/03_web_inscode_templates.png)

#### 1.3.4 InsCode AI 工作区

- **功能**：三栏式 IDE 界面。左栏为代码编辑区（显示项目介绍和代码文件），中栏为 AI 聊天面板（底部有输入框和发送按钮），右栏为预览/运行区（显示 InsCode 品牌标识和初始化状态）。顶部工具栏包含：预览、代码、博文解读、运行等按钮。
- **交互**：用户在左栏编辑代码，在中栏与 AI 对话获取帮助，在右栏实时预览效果。AI 支持理解自然语言指令并生成/修改代码。
- **评价**：工作区布局遵循主流在线 IDE 模式（左中右三栏），学习成本低。AI 聊天面板常驻，方便随时提问。但截图显示右栏仍处于"正在初始化环境，马上就好..."状态，加载时间偏长。整体 UI 采用浅色主题，边框和分割线 subtle，视觉干净。
- **截图**:[04_web_inscode_workspace.png](screenshots/04_web_inscode_workspace.png)

#### 1.3.5 TaoToken 首页

- **功能**：TaoToken 是 InsCode 关联的 Token 计费平台。首页 Slogan"全球大模型 · 稳定直连 · 分钟级接入 · 官方价 5 折"。提供"免费体验"和"购买 Token Plan"两个 CTA。底部展示已整合的模型品牌图标（Claude、OpenAI、Google、Kimi 等）。顶部 Banner 显示新人首充礼：注册后 48 小时内首笔满 ¥20 赠送 ¥10。
- **交互**：用户注册后可购买 Token Plan，按量使用各模型 API。标准 OpenAI 协议，可与 Claude Code 等工具对接。
- **评价**：作为底层计费平台，首页信息传达清晰。"官方价 5 折"是核心卖点，对开发者有吸引力。但 88CODE 用户可能需要额外了解 Token 消耗机制，增加了使用门槛。
- **截图**:[06_web_taotoken_home.png](screenshots/06_web_taotoken_home.png)

#### 1.3.6 TaoToken 模型定价页

- **功能**：模型列表以卡片网格展示，每张卡片显示模型名称、厂商、输入/输出价格（每百万 Token）、功能标签。左侧提供厂商筛选器：Anthropic、DeepSeek、OpenAI、Google、月之暗面、智谱、美团。
- **定价详情**（部分）：
  - DeepSeek：输入 ¥3/M tokens，输出 ¥6/M tokens（限时半价）
  - Claude（Anthropic）：输入 ¥18/M tokens，输出 ¥90/M tokens（限时半价）
  - GPT-5.5：输入 ¥17.5/M tokens，输出 ¥140/M tokens（限时半价）
  - Kimi-K2：输入 ¥3.25/M tokens，输出 ¥13.5/M tokens（限时半价）
  - DeepSeek V4-Flash：输入 ¥1/M tokens，输出 ¥2/M tokens
- **评价**：定价透明，按输入/输出分别计价符合行业惯例。"限时半价"标签营造紧迫感。DeepSeek 和 Kimi 系列性价比较高，Claude 和 GPT 系列价格偏高但能力更强。
- **截图**:[07_web_taotoken_pricing.png](screenshots/07_web_taotoken_pricing.png) [08_web_taotoken_pricing_scroll.png](screenshots/08_web_taotoken_pricing_scroll.png)

---

## 2. UI/UX 风格和质量描述

### 2.1 视觉风格

InsCode 平台采用极简现代风格：
- **配色**：以白色为底、灰色辅助、蓝色（#4A90D9 系）为主 CTA 色。整体色调清爽专业。
- **字体**：使用系统默认无衬线字体栈（-apple-system、BlinkMacSystemFont、Inter、Segoe UI 等），中文渲染清晰。
- **图标**：Logo 采用几何图形组合（快马的"马"形抽象），导航图标简洁。
- **调性**：介于"开发者工具"和"低代码平台"之间，既专业又不 intimidating。

88code.org 的 403 页面则极简到近乎空白：纯文字 + 超大号数字，仅有底部一个品牌标识。

### 2.2 信息密度与层级

- **InsCode 首页**：首屏只放一个输入框 + Slogan，信息极度精简。第二屏才展示模板卡片，避免首屏过载。主要 CTA（"生成项目"按钮）在输入框右侧，位置醒目。
- **AI 工作区**：三栏布局代码编辑区占约 40% 宽度，AI 面板约 30%，预览区约 30%。权重分配合理，编辑代码是核心操作。
- **TaoToken 首页**：Slogan + 两个大按钮，信息密度低但转化意图明确。

### 2.3 交互流畅度

- **页面加载**：InsCode 首页加载较快（约 2-3 秒），AI 工作区初始化需要等待（截图显示"正在初始化环境"）。
- **导航跳转**："项目"导航外链至 TaoToken，跳转无过渡动画，略显突兀。
- **滚动**：首页滚动平滑，模板卡片有轻微的 hover 效果。

### 2.4 文案质量

- **InsCode Slogan**："一句话 / 一个链接，几分钟生成可以发布的产品" —— 清晰、有画面感、承诺具体。
- **输入框 placeholder**：从"告诉 InsCode 一个设计稿截图，直接生成前端代码..."到"告诉 InsCode 一个博文链接，生成一个可交互的应用程序..."，不同场景下文案会动态变化，引导性强。
- **TaoToken**："标准 OpenAI 协议，与 Claude Code 等工具无感对接" —— 准确传达了技术兼容性。
- **一致性问题**：InsCode 使用"快马"品牌名，而 88code.org 使用"88code"，品牌关联性在官网上未明确传达（因官网不可访问）。

### 2.5 可访问性观察

- **对比度**：InsCode 主按钮蓝底白字，对比度足够。403 页面黑字白底，清晰可读。
- **深色模式**：403 页面支持 prefers-color-scheme 自动切换。InsCode 平台截图中未观察到深色模式开关。
- **键盘操作**：在线 IDE 场景下，Tab 键应在代码编辑区内缩进而非跳转到下一个元素，此行为需实际体验验证。

---

## 3. 官网描述

### 3.1 关键文案摘录

> 由于 88code.org 官网返回 403，无法直接摘录官网文案。以下来自关联平台 InsCode 和 TaoToken：

- "一句话 / 一个链接，几分钟生成可以发布的产品" —— InsCode 首页 H1
- "通过与 AI 聊天创建应用程序和网站" —— InsCode 首页副标题
- "全球大模型 · 稳定直连 · 分钟级接入 · 官方价 5 折" —— TaoToken 首页
- "标准 OpenAI 协议，与 Claude Code 等工具无感对接" —— TaoToken 首页副标题
- "新人首充礼 · 注册后 48 小时内，首笔满 ¥20 赠送 ¥10" —— TaoToken 顶部 Banner

### 3.2 核心卖点(官网视角)

1. **自然语言生成代码**：用中文描述需求即可生成可运行代码（InsCode 首页输入框）。
2. **一键部署**：生成项目后可直接部署为可访问的 Web 应用（CSDN 博客用户反馈）。
3. **模型丰富**：支持 Qwen、Kimi、Claude、GPT、DeepSeek 等多种大模型（InsCode 模型选择器 + TaoToken 模型列表）。
4. **Token 折扣**：通过 TaoToken 接入大模型 API，享受官方价 5 折优惠。
5. **模板生态**：社区提供丰富的预设模板，降低首次使用门槛（InsCode 模板卡片区）。

### 3.3 与实际体验的差距

| 卖点 | 官网/平台说法 | 实际体验 | 差距 |
|---|---|---|---|
| 官网可访问性 | 88code.org 应为产品官网 | 全站 403 地域限制 | 官网完全不可访问，用户无法从官网了解产品 |
| 生成速度 | "几分钟生成" | 工作区显示"正在初始化环境，马上就好"，实际等待时间偏长 | 初始化耗时可能超过用户预期 |
| 模型选择 | 首页默认展示 Qwen3.5-Plus | CSDN 博客提到使用 Kimi-K2 模型 | 博客文章可能基于历史版本，当前模型可能有更新 |

---

## 4. 定价

88CODE 的定价通过 TaoToken 平台实现，采用按 Token 消耗计费模式：

**Token 价格（部分模型，均为限时半价后价格）**：

| 模型 | 输入价格 | 输出价格 |
|---|---|---|
| DeepSeek | ¥3 / M tokens | ¥6 / M tokens |
| Kimi-K2 | ¥3.25 / M tokens | ¥13.5 / M tokens |
| Claude (Anthropic) | ¥18 / M tokens | ¥90 / M tokens |
| GPT-5.5 | ¥17.5 / M tokens | ¥140 / M tokens |
| GPT-5.3 | ¥6.125 / M tokens | ¥49 / M tokens |
| DeepSeek V4-Flash | ¥1 / M tokens | ¥2 / M tokens |
| Claude-Sonnet | ¥10.8 / M tokens | ¥54 / M tokens |

**优惠活动**：
- 新人首充礼：注册后 48 小时内，首笔满 ¥20 赠送 ¥10
- 所有模型均标注"限时半价"

---

## 5. 目标用户

基于平台功能和文案推断：

1. **编程初学者**：自然语言描述生成代码的功能，大幅降低了编程入门门槛。CSDN 博客作者提到"新手可以通过生成的代码反向学习编程思路"。
2. **快速原型开发者**：需要快速验证想法的开发者，"几分钟生成可以发布的产品"直击此群体痛点。
3. **前端/全栈开发者**：InsCode 模板以网页应用为主，目标用户需有基本的 Web 开发认知。
4. **AI 工具尝鲜者**：快捷入口中的"自拍漫改""语音故事机"等模板，吸引对 AI 应用感兴趣的非技术用户。

---

## 6. 与同类产品对比

| 维度 | 88CODE (InsCode) | GitHub Copilot | Cursor |
|---|---|---|---|
| **使用方式** | 网页端自然语言输入，生成完整项目 | IDE 插件，实时代码补全 | AI-first 代码编辑器 |
| **输出粒度** | 完整项目/应用级 | 代码片段/函数级 | 代码片段到项目级 |
| **部署能力** | 一键部署为 Web 应用 | 无内置部署 | 无内置部署 |
| **模型选择** | 多模型可选（Qwen、Kimi、Claude 等） | OpenAI GPT 系列 | 多模型可选 |
| **定价模式** | 按 Token 消耗（通过 TaoToken） | $10-19/月订阅 | $20/月订阅 |
| **学习辅助** | 生成代码附注释和原理说明 | 仅代码补全 | 有代码解释功能 |
| **代码修改** | 通过对话迭代优化 | 接受/拒绝建议 | 支持 AI 对话修改 |

**差异点**：88CODE/InsCode 的核心差异在于"项目级生成 + 一键部署"，而 Copilot 和 Cursor 聚焦在"代码编辑辅助"。88CODE 更像"AI 版的低代码平台"，后者是"AI 增强的 IDE"。

---

## 7. 优劣势小结

| 维度 | 优势 | 劣势 |
|---|---|---|
| 产品逻辑 | 自然语言到可运行代码的链路完整；支持迭代优化和一键部署 | 官网不可访问（403），品牌认知受阻；依赖 InsCode 平台，非独立产品 |
| UI/UX | 首页极简，输入框为视觉中心；工作区三栏布局符合开发者习惯 | AI 工作区初始化等待时间较长；"项目"导航外链跳转逻辑不直观 |
| 工程质量 | 代码遵循 PEP8 规范；多模型支持提供灵活性 | 官网 CDN 配置导致地域屏蔽；产品稳定性（初始化速度）有待提升 |
| 商业模式 | Token 折扣有吸引力；与 CSDN 生态联动 | 按量计费模式对重度用户成本不可控；定价信息需跳转 TaoToken 查看 |

---

## 附录 A 截图索引

| # | 文件 | 说明 |
|---|---|---|
| 01 | screenshots/01_web_homepage.png | 88code.org 官网 403 地域限制页面 |
| 02 | screenshots/02_web_inscode_home.png | InsCode (快马) 首页，AI 应用生成入口 |
| 03 | screenshots/03_web_inscode_templates.png | InsCode 项目模板卡片区 |
| 04 | screenshots/04_web_inscode_workspace.png | InsCode AI 编程工作区（三栏 IDE 布局） |
| 05 | screenshots/05_web_inscode_workspace_scroll.png | 工作区滚动后：调试建议、文件上传、AI 输入 |
| 06 | screenshots/06_web_taotoken_home.png | TaoToken 首页，Token 计费平台入口 |
| 07 | screenshots/07_web_taotoken_pricing.png | TaoToken 模型定价列表（首屏） |
| 08 | screenshots/08_web_taotoken_pricing_scroll.png | TaoToken 模型定价列表（滚动后更多模型） |
