# 木鱼专注 产品分析报告

| 项目 | 值 |
|---|---|
| 官网 | http://dolphinflow.cn/ |
| 下载链接 | — |
| 报告日期 | 2026-05-22 |
| 主机 | linux / x86_64 |
| Runtime | sandbox-local |
| 模式 | web-only |
| 用时 | 25 分钟 |

> 本次为网页版分析，未驱动桌面端 — 原因：① 官网 http://dolphinflow.cn/ 无法访问（连接被重置）；② 产品为纯移动端应用（Android/iOS），无 Linux 桌面端安装包；③ Android 沙盒未启用（android.enabled=false）。

---

## 1. 详细的产品逻辑介绍

### 1.1 总定位

木鱼专注（英文名 PeaceFocus / Muyu Focus）是由 DolphinFlow（成都海豚律动科技有限公司）开发的一款移动端专注效率工具，面向需要提升学习和工作专注力的用户。产品将番茄工作法、待办清单、白噪音、敲木鱼音效与"修行" gamification 机制融合，以治愈系小和尚"一休"为 IP 形象，试图用禅意交互降低用户开始专注任务的心理门槛。

### 1.2 界面清单

按信息来源列出实际采集到的所有主要界面：

| # | 界面 | 入口 | 主要功能 | 截图 |
|---|---|---|---|---|
| 1 | 官网首页（错误页） | http://dolphinflow.cn/ | 官网无法访问，显示连接重置 | [01_web_homepage.png](screenshots/01_web_homepage.png) |
| 2 | 应用宝产品页 | sj.qq.com/appdetail/... | 展示应用基本信息、下载按钮、分类标签 | [02_web_appstore.png](screenshots/02_web_appstore.png) |
| 3 | 应用宝详情页 | 滚动后 | 说明如何在电脑上下载并使用 | [03_web_appstore_detail.png](screenshots/03_web_appstore_detail.png) |
| 4 | Mergeek 产品页 | mergeek.com/... | 展示产品简介、标签、英文描述 | [04_web_mergeek.png](screenshots/04_web_mergeek.png) |
| 5 | Mergeek 详情页 | 滚动后 | 展示英文功能描述和促销信息 | [05_web_mergeek_detail.png](screenshots/05_web_mergeek_detail.png) |
| 6 | Mergeek 功能页 | 滚动后 | 展示核心功能英文介绍 | [06_web_mergeek_features.png](screenshots/06_web_mergeek_features.png) |
| 7 | Mergeek 底部分页 | 滚动到底 | 展示目标用户群体描述 | [07_web_mergeek_bottom.png](screenshots/07_web_mergeek_bottom.png) |

### 1.3 各界面功能与评价

#### 1.3.1 官网首页（错误页）

- **功能**：官网 http://dolphinflow.cn/ 本应作为产品的主要信息入口，提供产品介绍、下载链接、功能说明等。
- **实际状态**：页面无法加载，Firefox 显示 "The connection was reset" 错误。Host 侧 curl 测试同样返回空回复（curl: (52) Empty reply from server），域名解析到 198.18.0.243（测试网段地址）。
- **评价**：官网作为产品的门面和信任基础，完全不可用是严重问题。用户无法通过官网获取产品信息或验证产品真实性，只能依赖第三方应用商店（应用宝、App Store）的信息。
- **截图**：[01_web_homepage.png](screenshots/01_web_homepage.png)

#### 1.3.2 应用宝产品页

- **功能**：腾讯应用宝作为 Android 主要分发渠道，展示产品图标、名称、评分（0.0）、下载量（363 次）、分类标签（"其他"）及"电脑"下载按钮。
- **交互**：用户可点击"电脑"按钮下载应用宝电脑版，再通过模拟器运行 Android 应用。
- **评价**：
  - 下载量仅 363 次，评分 0.0，说明产品在应用宝的曝光度和用户基础较低。
  - 分类为"其他"而非"效率"或"工具"，可能影响搜索发现。
  - 页面明确提示"木鱼专注为手机应用，需先安装腾讯应用宝提供电脑端启动能力"，说明产品无原生桌面端。
- **截图**：[02_web_appstore.png](screenshots/02_web_appstore.png)

#### 1.3.3 Mergeek 产品展示页

- **功能**：Mergeek 是一个产品发现平台，展示木鱼专注的详细介绍、功能列表、定价信息和用户群体描述。
- **关键信息**：
  - 标签：Android、iOS、效率、健康健美
  - 英文描述："Muyu Focus is a timer efficiency tool that helps you enter the flow state when studying or working. It integrates multiple functions such as to-do lists, Pomodoro clocks, white noise, focus training, personalized dressing, and interactive components."
  - 促销：限时活动 5.0 折优惠，立减 29 元
- **评价**：Mergeek 页面提供了比应用宝更完整的产品信息，但英文描述为主，中文内容较少，且没有实际应用截图展示。
- **截图**：[04_web_mergeek.png](screenshots/04_web_mergeek.png)、[05_web_mergeek_detail.png](screenshots/05_web_mergeek_detail.png)

#### 1.3.4 Mergeek 功能详情页

- **功能**：展示产品的核心功能模块英文介绍。
- **关键文案**：
  - "It improves concentration and attention through immersive white noise combinations and Schulte grid training."
  - "Each time you focus, will receive merit beads as a cultivation reward to unlock more adorable focus interface combinations, making it more motivating to execute focus behaviors."
- **截图**：[06_web_mergeek_features.png](screenshots/06_web_mergeek_features.png)

#### 1.3.5 Mergeek 目标用户页

- **功能**：描述产品的目标用户群体。
- **关键文案**："People who want to improve efficiency and focus at work or study"、"People preparing for the college entrance examination, civil service examination, postgraduate entrance examination, and institution entrance examination."
- **评价**：目标用户定位清晰 — 学生、备考人群和职场效率追求者。
- **截图**：[07_web_mergeek_bottom.png](screenshots/07_web_mergeek_bottom.png)

---

## 2. UI/UX 风格和质量描述

### 2.1 视觉风格

根据应用图标和第三方平台描述，产品采用**治愈系禅意风格**：
- **IP 形象**：以小和尚"一休"为核心视觉元素，应用图标为闭眼微笑的小和尚头像，传递平静、专注的情绪。
- **配色**：以暖色调为主（木色、米白、暖黄），配合渐变紫色卡片（Mergeek 页面可见），整体调性温和不刺眼。
- **设计风格**：极简 + 拟物结合，融入"修行""功德"等东方禅意概念，区别于传统效率工具的冷峻科技感。

### 2.2 信息密度与层级

基于第三方描述推断：
- 首页以"一休"小和尚为视觉焦点，配合大号倒计时显示，信息层级清晰 — 核心功能（专注计时）一眼可及。
- 次要功能（待办清单、数据统计、白噪音、装扮）通过底部 Tab 或侧边入口收纳，不干扰主流程。
- 修行模式作为 gamification 层，通过"功德珠"积累提供正向反馈，增强用户粘性。

### 2.3 交互流畅度

由于未实际运行应用，无法评估真实交互流畅度。根据平台信息：
- 支持 iOS 17 可交互小组件（Interactive Widgets）和 StandBy 待机显示模式，说明开发团队跟进最新系统特性。
- 支持云端数据备份，防止数据丢失。

### 2.4 文案质量

- **一致性**：产品名称存在多个版本 — "木鱼专注"（中文）、"PeaceFocus"（App Store 英文名）、"Muyu Focus"（Mergeek 英文名），品牌统一性有待加强。
- **风格**：文案走治愈系路线，使用"修行""功德""心流"等词汇，与产品禅意定位一致。
- **英文描述**：Mergeek 页面的英文介绍存在语法问题（如"will receive merit beads"缺少主语），可能为非母语者撰写。

### 2.5 可访问性观察

基于第三方信息推断：
- iOS 版本支持 StandBy 显示和交互式小组件，对视力辅助有一定支持。
- 木鱼音效 + 白噪音的组合对听障用户可能不够友好，需依赖视觉反馈。
- 无深色模式支持信息。

---

## 3. 官网描述

### 3.1 关键文案摘录

> 官网 http://dolphinflow.cn/ 无法访问，无文案可摘录。

以下摘录来自第三方平台：

> "木鱼专注是一款助你学习工作时进入心流状态的计时器效率工具，集番茄钟、待办清单、白噪音、敲木鱼、数据统计、桌面小组件于一体。" — Mergeek 页面简介

> "Muyu Focus is a timer efficiency tool that helps you enter the flow state when studying or working. It integrates multiple functions such as to-do lists, Pomodoro clocks, white noise, focus training, personalized dressing, and interactive components." — Mergeek 英文描述

> "木鱼专注为手机应用，需先安装腾讯应用宝提供电脑端启动能力，安全可靠，体验超越传统模拟器。" — 应用宝页面

### 3.2 核心卖点（第三方平台视角）

1. **禅意番茄钟**：将传统番茄工作法与木鱼敲击音效结合，用声音锚点帮助用户保持专注（原文锚：Mergeek 描述）。
2. **修行 gamification**：每次专注积累"功德珠"，解锁小和尚装扮，将效率管理游戏化（原文锚：Mergeek "merit beads as a cultivation reward"）。
3. **舒尔特方格训练**：内置专注力训练工具，不只是计时器（原文锚：Mergeek "Schulte grid training"）。
4. **iOS 生态深度整合**：支持可交互小组件、StandBy 显示、云端同步（原文锚：App Store 描述）。
5. **全场景白噪音**：多种沉浸式白噪音组合，覆盖专注、睡眠等场景（原文锚：Mergeek 描述）。

### 3.3 与实际体验的差距

| 卖点 | 平台原文 | 实际可验证状态 | 差距 |
|---|---|---|---|
| 官网信息 | 应有完整产品介绍和下载入口 | 官网完全无法访问 | 官网与产品存在感严重不匹配 |
| 下载量 | 应用宝显示 363 下载 | 可验证 | 用户基数极低，与"效率工具"定位的市场预期有差距 |
| 桌面端 | 应用宝宣传"电脑版" | 实为通过应用宝模拟器运行 Android 版 | 无原生桌面端，宣传口径有误导性 |

---

## 4. 定价

根据 Mergeek 页面信息：
- **促销价**：限时 5.0 折优惠，立减 29 元
- **推断原价**：约 58 元（一次性付费或订阅制，信息不足）
- **免费版**：应用宝页面可下载，推测有免费基础功能 + 付费高级功能（装扮、数据同步等）的 freemium 模式

---

## 5. 目标用户

基于平台描述推断：
1. **学生群体**：需要备考（高考、考研、考公、考编）的年轻人，对时间管理和专注力有强需求。
2. **职场效率追求者**：希望在工作学习中减少手机干扰、提升效率的白领。
3. **禅意/治愈系爱好者**：喜欢东方禅意美学、对 gamification 有正向反馈需求的用户。

---

## 6. 与同类产品对比

| 维度 | 木鱼专注 | Forest（专注森林） | 番茄 ToDo |
|---|---|---|---|
| 核心机制 | 番茄钟 + 修行功德珠 + 木鱼音效 | 番茄钟 + 种树 gamification | 番茄钟 + 待办清单 |
| IP 风格 | 禅意小和尚"一休" | 像素森林 | 极简无 IP |
| 平台覆盖 | Android、iOS | Android、iOS、Web、桌面端 | Android、iOS、Web |
| 社交功能 | 未提及 | 好友种树、全球排名 | 自习室、统计数据分享 |
| 品牌成熟度 | 低（官网不可用、下载量低） | 高（多年运营、大量用户） | 中（成熟产品、稳定用户群） |

木鱼专注的差异化在于"禅意 + 东方美学 + 木鱼音效"，但品牌成熟度和用户基础远不及 Forest 等成熟产品。

---

## 7. 优劣势小结

| 维度 | 优势 | 劣势 |
|---|---|---|
| 产品逻辑 | 禅意 gamification 有差异化；功能覆盖全面（番茄钟 + 待办 + 白噪音 + 训练） | 官网不可用严重影响品牌信任度；无原生桌面端；下载量极低 |
| UI/UX | 治愈系视觉风格独特；iOS 生态整合好（小组件、StandBy） | 英文文案质量一般；无实际界面可验证流畅度 |
| 工程质量 | 跟进 iOS 17 新特性；支持云端备份 | 官网服务器不稳定；Android 分发量极低；品牌命名不统一 |

---

## 附录 A 截图索引

| # | 文件 | 说明 |
|---|---|---|
| 01 | screenshots/01_web_homepage.png | 官网首页（连接被重置错误页） |
| 02 | screenshots/02_web_appstore.png | 应用宝产品页（产品信息、下载按钮） |
| 03 | screenshots/03_web_appstore_detail.png | 应用宝详情页（电脑版使用说明） |
| 04 | screenshots/04_web_mergeek.png | Mergeek 产品展示页（简介、标签） |
| 05 | screenshots/05_web_mergeek_detail.png | Mergeek 详情页（英文描述、促销信息） |
| 06 | screenshots/06_web_mergeek_features.png | Mergeek 功能页（核心功能英文介绍） |
| 07 | screenshots/07_web_mergeek_bottom.png | Mergeek 底部分页（目标用户描述） |
