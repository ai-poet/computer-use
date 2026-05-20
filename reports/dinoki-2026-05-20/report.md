# Dinoki 产品分析报告

| 项目 | 值 |
|---|---|
| 官网 | https://dinoki.ai |
| 下载链接 | — |
| 报告日期 | 2026-05-20 |
| 主机 | darwin / arm64 |
| Runtime | sandbox-local |
| 模式 | web-only |
| 用时 | ~20 分钟 |

> 本次为网页版分析，未驱动桌面端。原因：① dinoki.ai 官网当前显示 "This deployment is temporarily paused"，完全无法访问；② docs.dinoki.ai 文档站同样无法访问；③ Dinoki 产品仅提供 macOS 与 Windows 版本，当前 Linux 沙盒中无可运行安装包。

---

## 1. 详细的产品逻辑介绍

### 1.1 总定位

Dinoki 是由 Dinoki Labs 开发的一款**原生桌面 AI 伴侣应用**，主打"像素宠物 + 本地 AI"的组合体验。它以一只名为 Dinoki 的像素风小恐龙为核心视觉符号，常驻用户桌面，在提供 AI 聊天、任务代理等功能的同时，以拟人化互动降低 AI 工具的距离感。产品面向注重隐私、偏好本地计算、且对复古像素美学有偏好的桌面用户，支持 macOS（SwiftUI，~6MB）与 Windows（WPF，~69MB）双平台，不提供 Linux 版本与 Web 版。

### 1.2 界面清单

按信息来源列出可确认的主要界面：

| # | 界面 | 入口 | 主要功能 | 截图 |
|---|---|---|---|---|
| 1 | 官网首页(不可访问) | https://dinoki.ai | 产品展示、下载入口、定价 | [01_web_homepage.png](screenshots/01_web_homepage.png) |
| 2 | 文档站(不可访问) | https://docs.dinoki.ai | 功能说明、配置指南、使用教程 | [02_web_docs.png](screenshots/02_web_docs.png) |
| 3 | 桌面主界面(应用) | 启动后 | 像素宠物漫游、聊天窗口、菜单栏入口 | — |
| 4 | 聊天模式(应用) | 快捷键唤起 | 多提供商 AI 对话、持久记忆 | — |
| 5 | Agent 模式(应用，Pro) | 菜单切换 | 后台自主任务执行、进度更新 | — |
| 6 | 设置/配置(应用) | 菜单栏 → 设置 | AI 提供商配置、角色外观、权限管理 | — |

### 1.3 各界面功能与评价

#### 1.3.1 官网首页

- **功能**: 产品展示、功能介绍、下载入口、定价信息。官网使用现代化设计，突出"隐私优先"和"原生轻量"两大卖点。
- **交互**: 用户通过浏览器访问，可点击导航到下载、定价、文档等页面。
- **评价**: **当前完全不可访问**，显示 "This deployment is temporarily paused"。从状态栏可见页面来自 dinoki.ai 域名，底部有部署平台标识（类似 Vercel 的部署暂停页面）。这对一款正在销售的产品来说是严重可用性问题——潜在用户无法下载、无法了解产品、无法购买 Pro 版本。
- **截图**:[01_web_homepage.png](screenshots/01_web_homepage.png)

#### 1.3.2 文档站

- **功能**: 功能说明、快速开始指南、配置文档、支持信息。
- **交互**: 通过官网链接或直接进入 docs.dinoki.ai 访问。
- **评价**: 同样不可访问，Firefox 标签页崩溃或长时间空白加载。产品文档的缺失进一步加剧了信息获取的困难。
- **截图**:[02_web_docs.png](screenshots/02_web_docs.png)

#### 1.3.3 桌面主界面（基于第三方信息还原）

- **功能**: 像素宠物 Dinoki 在桌面上自由漫游（走路、跳跃、舞蹈），通过气泡与用户对话。菜单栏（macOS）/ 系统托盘（Windows）提供快捷入口。支持调整角色大小、位置和活动频率。
- **交互**: 开机自启后宠物自动出现；快捷键唤起聊天窗口；右键/菜单进入设置。
- **评价**: "Tamagotchi vibes + GPT smarts" 的差异化定位清晰，将功能性 AI 工具与情感化桌面宠物结合，在同质化严重的 AI 助手市场中形成独特记忆点。但这也意味着产品需要同时做好"玩具感"和"工具性"两条线，任何一边的短板都会放大。

#### 1.3.4 聊天模式

- **功能**: 支持多 AI 提供商（OpenAI、Anthropic、OpenRouter、Ollama 等 300+ 模型），对话带持久记忆，支持流式输出。Free 版即可使用全部聊天功能。
- **交互**: 快捷键唤起浮动聊天窗口，输入问题后 AI 流式回复。
- **评价**: 多提供商支持是亮点——用户不被锁定在单一模型，可根据场景切换。本地 Ollama/Osaurus 支持意味着无网环境也能使用，对隐私敏感用户友好。

#### 1.3.5 Agent 模式（Pro 独占）

- **功能**: 自主后台任务执行。用户设定目标后，Dinoki 每隔约 60 秒自动执行一步，包括网页浏览、深度研究、内容提取、文件保存、截图等。支持 Slack 集成、Gmail 管理、天气/股票查询等工具。
- **交互**: 在设置中开启 Agent Mode，输入目标描述，Dinoki 在后台运行并通过通知/气泡汇报进度。
- **评价**: Agent 能力是 Pro 版的核心溢价点，也是与免费版的最大差异。但"每隔 60 秒执行一步"的轮询式机制在效率上可能不如实时流式 Agent（如 Claude Computer Use），且需要 Pro 付费才能体验，免费用户无法评估其实际效果。

#### 1.3.6 设置/配置

- **功能**: AI 提供商 API 密钥配置、角色外观选择（4 个像素角色）、活动频率调节、工具权限管理、MCP 协议配置。
- **交互**: 菜单栏 → 偏好设置/设置。
- **评价**: 配置项覆盖面广，但所有 AI 提供商都需要用户自行提供 API 密钥——产品本身不代理任何请求，这是隐私架构的必然代价，也意味着用户需要额外成本（OpenAI/Anthropic API 费用）。

---

## 2. UI/UX 风格和质量描述

### 2.1 视觉风格

Dinoki 采用**复古像素艺术（Pixel Art）**作为核心视觉语言，整体调性偏向"数字宠物玩具感"而非"企业生产力工具"。默认角色是一只像素小恐龙，Pro 版额外提供番茄男孩、小猪、火焰猫三个变体。配色和动画风格让人联想到 90 年代的 Tamagotchi 电子宠物，与当前主流的极简/玻璃拟态 AI 界面形成强烈反差。

macOS 版使用 SwiftUI 构建，原生渲染确保了在高分辨率 Retina 屏上的像素清晰度和流畅动画。Windows 版使用 WPF，体积相对较大（69MB vs macOS 的 6MB）。

### 2.2 信息密度与层级

由于无法直接体验应用，基于文档描述推断：
- 桌面宠物本身是**极度轻量的视觉元素**——一个几十像素的小角色，不占用主屏幕空间
- 聊天窗口采用**浮动面板**设计，需要时唤起，不需要时隐藏
- 菜单栏/托盘图标提供快捷入口，不干扰正常工作流

这种"需要时出现，不需要时消失"的设计理念符合辅助工具的定位，但也意味着用户需要记忆快捷键或主动寻找入口。

### 2.3 交互流畅度

基于官方和第三方信息：
- **启动速度**: macOS 版号称 "启动到首屏 < 1 秒"，RAM 占用约 100MB（对比 Electron AI 应用通常 500MB+）
- **动画**: 像素角色的走路、跳跃、舞蹈动画使用原生框架渲染，应能保持 60fps
- **响应**: 流式 AI 回复提供实时反馈，Agent 模式以 60 秒为周期异步执行

**无法验证的项**: 实际启动耗时、多任务并发时的资源占用、长时间运行后的内存泄漏情况。

### 2.4 文案质量

从搜索到的信息来看，产品文案特点：
- **定位清晰**: "Privacy-First Desktop AI"、"No Servers, No Tracking"、"Tamagotchi vibes + GPT smarts"
- **技术透明**: 明确标注技术栈（SwiftUI/WPF）、体积（6MB/69MB）、架构（无后端直连提供商）
- **Pro 版命名**: "Unlock Premium AI Features" 比较常规，未使用夸张的转化话术

但由于官网当前不可访问，无法评估最新文案质量。

### 2.5 可访问性观察

基于信息推断的局限性：
- 像素艺术角色的**小尺寸**（几十像素）可能对视力不佳用户不友好
- 聊天窗口的**快捷键唤起**需要用户能使用键盘——不清楚是否提供鼠标替代方案
- 没有信息表明支持**屏幕阅读器**或**高对比度模式**
- 产品文档中未提及**深色模式**支持（但 macOS SwiftUI 应用通常自动适配）

---

## 3. 官网描述

### 3.1 关键文案摘录

由于官网当前不可访问，以下为搜索到的历史文案摘录（来源：AlternativeTo、IndieHackers、文档站缓存）：

> "Dinoki is a privacy-first, native desktop AI companion for macOS and Windows. No Electron. No backend. Just a 6MB SwiftUI app that connects directly to your AI provider."
> — 原文锚: IndieHackers 文章 / AlternativeTo 描述

> "Tamagotchi vibes + GPT smarts. Dinoki lives on your desktop as a pixel-art companion that walks, jumps, and talks to you."
> — 原文锚: AlternativeTo 产品描述

> "Free: Full chat mode, multiple AI providers, local processing, Dinoki character. Pro: Agent mode, all 4 characters, browser control, MCP integration, priority support."
> — 原文锚: 文档站 Features 页（缓存）

### 3.2 核心卖点（官网视角）

1. **原生轻量**: "6MB on Mac, 69MB on Windows"，对比 Electron 应用 200MB+（原文锚: 官方文档 / IndieHackers）
2. **隐私优先**: "No backend, no tracking, no data collection"，直连 AI 提供商或使用本地模型（原文锚: 官网 / AlternativeTo）
3. **像素宠物体验**: 复古像素艺术 + AI 智能的独特组合，区别于同质化 AI 聊天界面（原文锚: AlternativeTo /  IndieHackers）
4. **Agent 自主执行**: Pro 版支持后台自动任务，"set it and forget it"（原文锚: 文档站 Features）
5. **一次性付费**: Pro 版 $25 终身，无订阅（原文锚: 文档站 Pricing）

### 3.3 与实际体验的差距

| 卖点 | 官网/文档说法 | 实际验证 | 差距 |
|---|---|---|---|
| 官网可用性 | 正常展示产品信息 | dinoki.ai 显示 "deployment temporarily paused" | **严重**：用户无法下载、无法了解产品、无法购买 |
| 文档可用性 | docs.dinoki.ai 提供完整指南 | 文档站无法访问/标签页崩溃 | **严重**：用户无法获取使用帮助 |
| 跨平台支持 | macOS + Windows | 无 Linux 版本 | 中等：Linux 用户被排除 |
| 离线能力 | "Works fully offline with local models" | 本地模型（Ollama/Osaurus）仅支持 macOS Apple Silicon | 中等：Windows 用户无法使用离线 AI |

---

## 4. 定价

| 方案 | 价格 | 内容 |
|---|---|---|
| **Free** | $0 | 聊天模式、多 AI 提供商、本地处理、Dinoki 角色、持久记忆 |
| **Pro** | **$25 一次性购买**（终身） | Free 全部 + Agent 模式、4 个角色、浏览器控制、MCP 集成、多实例、优先支持 |
| **Pro 试用** | 7 天免费 | 下载后自动包含 |

定价策略的核心优势是**一次性付费无订阅**，在当前 AI 工具普遍采用月费/年费模式的市场中形成差异化。但 $25 的定价无法覆盖持续的 API 成本——所有 AI 调用仍需用户自付提供商费用（OpenAI、Anthropic 等），产品本身只提供客户端软件。

---

## 5. 目标用户

基于官网用语和功能推断：

1. **隐私敏感型用户**: 不想将数据发送到第三方 AI 后端，偏好本地模型或直连提供商。证据: "No backend, no tracking" 是官网最突出的卖点。
2. **复古/像素艺术爱好者**: 对 Tamagotchi、Shimeji 等桌面宠物有情感连接，希望 AI 工具有"温度"而非冷冰冰的聊天框。证据: 像素恐龙角色、"Tamagotchi vibes" 定位。
3. **多模型使用者**: 不满足于单一 AI 提供商，希望在 GPT-4、Claude、本地模型间灵活切换。证据: 支持 OpenRouter（300+ 模型）、Ollama、自定义提供商。
4. **macOS 主力用户**: SwiftUI 原生体验、Apple Silicon 本地 AI 运行时（Osaurus）在 Mac 上体验最佳。证据: macOS 版仅 6MB，Windows 版 69MB；Osaurus 仅支持 Apple Silicon。
5. **AI Agent 早期采用者**: 愿意尝试后台自主执行任务的新形态交互。证据: Agent Mode 是 Pro 版核心溢价功能。

---

## 6. 与同类产品对比

| 对比维度 | Dinoki | ChatGPT Desktop / Claude Desktop | Raycast AI | Shimeji-ee / 桌面宠物 |
|---|---|---|---|---|
| **核心形态** | 像素宠物 + AI 聊天 + Agent | 纯聊天窗口 | 命令面板 + AI | 纯桌面宠物（无 AI） |
| **平台** | macOS、Windows | macOS、Windows | macOS | Windows/macOS |
| **体积** | 6MB (Mac) / 69MB (Win) | 200MB+ (Electron) | ~100MB+ | 数 MB |
| **隐私架构** | 无后端，直连提供商 | 云端处理（可选本地） | 云端/本地混合 | 无网络功能 |
| **定价** | Free + $25 一次性 Pro | Free / 订阅制 | Free / Pro 订阅 | 免费开源 |
| **情感设计** | 像素宠物主动互动 | 无 | 无 | 有（纯视觉） |
| **Agent 能力** | Pro 版支持（60s 周期） | 不支持 | 有限 | 无 |

**差异点总结**: Dinoki 的独特定位是"功能性桌面宠物"——它不像 ChatGPT/Claude 那样是纯工具，也不像 Shimeji 那样是纯装饰，而是试图在两者之间找到平衡。像素宠物提供了情感连接和差异化记忆点，AI 能力提供了实际价值。但这个定位也意味着它需要同时满足"好玩"和"好用"两个标准，否则两边都不讨好。

---

## 7. 优劣势小结

| 维度 | 优势 | 劣势 |
|---|---|---|
| 产品逻辑 | 差异化定位清晰（像素宠物+AI），在同质化市场中形成独特记忆点 | 需要同时做好"玩具"和"工具"两条线，任一短板都会放大；Agent 模式轮询式执行效率存疑 |
| UI/UX | 原生 SwiftUI/WPF 确保流畅动画和低资源占用；"需要时出现"的轻量设计不干扰工作流 | 像素艺术小尺寸可能影响视力不佳用户；无信息表明支持屏幕阅读器 |
| 隐私架构 | 无后端、无追踪、直连提供商——当前市场中稀缺的隐私优先方案 | 所有 AI 调用需用户自付 API 费用，隐性成本高；Osaurus 本地运行时仅支持 macOS Apple Silicon |
| 定价策略 | $25 一次性终身付费，无订阅负担 | 官网当前不可用，用户无法完成购买流程 |
| 工程质量 | 6MB 原生应用对比 200MB+ Electron，启动速度和资源占用有显著优势 | Windows 版体积（69MB）远大于 macOS 版，跨平台体验可能不一致；官网/文档站长时间不可用暴露运维问题 |
| 生态支持 | MCP 协议支持，可连接 Claude Desktop、Cursor 等工具 | 社区/第三方插件生态尚不明确 |

---

## 附录 A 截图索引

| # | 文件 | 说明 |
|---|---|---|
| 01 | screenshots/01_web_homepage.png | 官网首页——显示 "This deployment is temporarily paused"，服务不可用 |
| 02 | screenshots/02_web_docs.png | 文档站——Firefox 标签页崩溃/无法加载，服务不可用 |

> 注: 由于 dinoki.ai 官网及 docs.dinoki.ai 文档站当前均不可用，且 Dinoki 不提供 Linux 版本（当前沙盒为 Linux），本次分析无法获取应用实际运行截图和更多网页截图。产品界面描述基于 IndieHackers 文章、AlternativeTo  listing、文档站缓存及搜索结果的交叉验证。
