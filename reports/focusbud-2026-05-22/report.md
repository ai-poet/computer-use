# FocusBud 产品分析报告

| 项目 | 值 |
|---|---|
| 官网 | https://gabesilverstein.com/focusbud.html |
| 下载链接 | — |
| 报告日期 | 2026-05-22 |
| 主机 | linux / x86_64 |
| Runtime | sandbox-local |
| 模式 | web-only |
| 用时 | ~15 分钟 |

> 本次为网页版分析，未驱动桌面端 — FocusBud 为 2021 年春季学生概念设计项目，官网仅展示设计过程与 UI 原型，未提供任何可下载或可安装的桌面端/移动端产品。

---

## 1. 详细的产品逻辑介绍

### 1.1 总定位

FocusBud 是一款受 Tamagotchi（日本电子宠物）启发的游戏化专注工具，面向 ADHD（注意力缺陷多动障碍）用户设计。核心逻辑是：通过"养植物"的拟人化机制，将专注时长转化为植物的"成长值"，以正向激励帮助用户建立工作/学习中的专注习惯。该产品由 Gabe Silverstein 主导，联合 Cianna Robinson 与 Nikola Jovanovic 在 2021 年春季学期完成，历时 6 周，属于概念设计 + 物理硬件组件的综合项目，未实际商业化发布。

### 1.2 界面清单

按官网展示顺序列出所有主要界面：

| # | 界面 | 入口 | 主要功能 | 截图 |
|---|---|---|---|---|
| 1 | 首页（网页） | https://gabesilverstein.com/focusbud.html | 项目概述、团队信息、问题定义 | [01_web_homepage.png](screenshots/01_web_homepage.png) |
| 2 | 项目详情（网页） | 首页向下滚动 | 合作者、角色分工、时间线、问题陈述 | [02_web_homepage_scroll1.png](screenshots/02_web_homepage_scroll1.png) |
| 3 | 产品展示（网页） | 首页继续滚动 | 产品渲染图、工具使用、设计过程 | [03_web_homepage_scroll2.png](screenshots/03_web_homepage_scroll2.png) |
| 4 | 研究背景（网页） | 首页继续滚动 | 二手研究、竞品分析、用户画像、故事板 | [04_web_homepage_bottom.png](screenshots/04_web_homepage_bottom.png) |
| 5 | 设计流程（网页） | 首页继续滚动 | 五步设计过程、草图、实体模型 | [06_web_design_process.png](screenshots/06_web_design_process.png) |
| 6 | UI 流程（网页） | 首页继续滚动 | Home → Start Session → In Session → Summary | [08_web_mockups.png](screenshots/08_web_mockups.png) |
| 7 | 会话总结（网页） | 首页继续滚动 | 会话统计、反思总结 | [09_web_ui_detail.png](screenshots/09_web_ui_detail.png) |
| 8 | Figma 原型（网页） | 点击 "View Prototype" 按钮 | 交互式 UI 原型（Sessions 日历视图） | [16_web_figma_prototype.png](screenshots/16_web_figma_prototype.png) |

### 1.3 各界面功能与评价

#### 1.3.1 首页（网页）

- **功能**：展示项目名称、定位标语、导航栏（Work / Explore / Writing / About），顶部 banner 使用淡绿色渐变背景与 FocusBud 品牌 logo。
- **交互**：向下滚动进入项目详情区；点击导航栏可跳转至作者其他页面。
- **评价**：作为作品集子页面，首页信息层级清晰，标题 "FocusBud" 与副标题 "A gamified tool for those with ADHD to improve their focus" 一句话说清定位。但导航栏的 "Work" 等链接在当前页面点击后未跳转（可能是单页应用或链接指向同一页面），体验上略有困惑。
- **截图**：[01_web_homepage.png](screenshots/01_web_homepage.png)

#### 1.3.2 项目详情区（网页）

- **功能**：列出合作者（Cianna Robinson, Nikola Jovanovic, Gabe Silverstein）、角色分工（Project Manager & Scribe）、时间线（Spring 2021, 6 Weeks），以及 Problem / Insight / Solution 三段式项目陈述。
- **交互**：纯文本展示，无交互功能；"View Prototype" 按钮链接至 Figma 原型。
- **评价**：信息结构采用标准的作品集叙事格式（问题→洞察→方案），便于快速理解项目背景。Problem 部分明确提到灵感来源（Tamagotchi）和目标人群（ADHD 用户在工作环境中的专注问题），定位具体可证伪。Solution 部分简述了"责任感"和"奖励专注时长"两大机制。
- **截图**：[02_web_homepage_scroll1.png](screenshots/02_web_homepage_scroll1.png)

#### 1.3.3 产品展示与设计流程（网页）

- **功能**：展示产品设计渲染图（一个圆柱形硬件设备 + 配套 App UI）、使用的工具（Figma 等图标）、五步设计过程（Identify → Prototype → Define → 3D Model → Final Mockup），以及草图、实体模型照片。
- **交互**：纯图片展示，无点击交互。
- **评价**：硬件 + 软件的综合设计展示了较完整的工业设计能力。渲染图中硬件为一个白色圆柱形设备，顶部或侧面配有显示屏显示植物状态；App 界面围绕"植物养成"主题展开。设计流程从目标受众调研到 3D 建模再到最终原型，步骤完整。但官网未提供各步骤的详细产出物（如用户调研原始数据、可用性测试报告），无法验证设计决策的依据。
- **截图**：[03_web_homepage_scroll2.png](screenshots/03_web_homepage_scroll2.png)、[06_web_design_process.png](screenshots/06_web_design_process.png)

#### 1.3.4 研究背景区（网页）

- **功能**：展示三项二手研究（ADHD in the Classroom / Disciplining Domesticity / Effects of Adderall on the Body）、竞品分析（Forest、Habitica 等）、用户画像（Personas）和使用故事板（Storyboard）。
- **交互**：纯展示，无交互。
- **评价**：研究部分展示了项目的前期调研深度，竞品分析直接对标了 Forest（种树专注 App）和 Habitica（游戏化待办清单），定位准确。Key Takeaways 中提到了"积分系统奖励正确行为"、"游戏化创造积极影响"等结论，与后续产品机制一致。但页面上的研究文档缩略图无法点击放大阅读具体内容。
- **截图**：[04_web_homepage_bottom.png](screenshots/04_web_homepage_bottom.png)

#### 1.3.5 UI 流程展示（网页）

- **功能**：通过四张 mockup 展示 App 的核心使用流程：
  1. **Home Screen**：显示当前时间、日期、植物状态（Focusbud）、健康值、设置按钮
  2. **Start Session Screen**：选择专注时长（如 60:00），点击 "Start" 开始
  3. **In Session**：倒计时运行中，显示剩余时间，可手动标记 "Distracted" 或 "Finished"
  4. **Summary and Trends**：会话结束后的统计（专注次数、XP 点数、时间线）
- **交互**：静态展示，无实际可点击的 UI。
- **评价**：流程设计完整，覆盖了"开始→执行→结束→回顾"的专注闭环。手动标记 "Distracted" 的功能是一个设计亮点，允许用户主动记录分心事件，有助于后续自我觉察。但界面信息显示密度较高（时间、健康值、XP、设置等多元素同时呈现），对于 ADHD 用户（目标人群）是否会造成认知负担，缺乏验证证据。
- **截图**：[08_web_mockups.png](screenshots/08_web_mockups.png)

#### 1.3.6 会话总结（网页）

- **功能**：展示 Session Summary 界面的详细设计，包括：分心次数统计、XP 点数、时间线（专注/分心/休息三段），以及项目反思（What worked? / What didn't?）。
- **交互**：纯展示。
- **评价**：会话总结界面信息丰富，时间线可视化（Ring）帮助用户直观了解本次会话的专注分布。反思部分坦诚记录了设计中的取舍（如"植物本身容易混淆"、"硬件和软件需要更紧密配合"），体现了设计思考过程。但作为概念项目，这些反思未经过真实用户测试验证。
- **截图**：[09_web_ui_detail.png](screenshots/09_web_ui_detail.png)

#### 1.3.7 Figma 原型（网页）

- **功能**：通过 Figma 链接展示可交互的 UI 原型，当前可见界面为 "May's Sessions" 日历视图，显示五月份的专注会话记录（日期以圆圈标记，不同颜色可能代表不同完成状态）。
- **交互**：Figma 原型支持有限的点击交互（Back / Done 按钮、日期选择），但实测点击后界面无变化，可能需要登录 Figma 才能完整体验。左侧有 Flow 1 / Flow 2 切换。
- **评价**：原型展示了日历回顾功能，用户可以通过日历视图追踪长期的专注习惯，这是从单次专注向习惯养成延伸的重要功能。但原型交互受限，无法验证完整流程的流畅度。
- **截图**：[16_web_figma_prototype.png](screenshots/16_web_figma_prototype.png)

---

## 2. UI/UX 风格和质量描述

### 2.1 视觉风格

整体视觉以**自然/植物主题**为核心，主色调为**绿色系**（深绿 #1B5E20 搭配浅绿渐变背景），呼应"养植物"的产品概念。图标采用简洁的扁平风格，植物角色（Focusbud）为一个带有笑脸的盆栽形象，具有亲和力。硬件渲染图为白色圆柱形设备，设计语言简约现代，类似 Alexa 或 Nest Thermostat 的家电风格（官网明确将这三者列为硬件参考）。

字体使用无衬线字体，标题粗大、正文适中，整体排版偏向作品集展示风格（大图 + 短段落），而非产品落地页的信息密集型布局。

### 2.2 信息密度与层级

官网作为**作品集展示页**，信息层级符合预期：首屏品牌识别 → 项目背景 → 设计过程 → UI 展示 → 反思总结。每个区块有明确的标题分隔，阅读节奏良好。

但 App UI 本身的信息密度偏高：Home Screen 同时显示时间、日期、植物状态、健康值、设置入口等多个元素。对于 ADHD 用户（产品目标人群），过多的同时呈现信息可能增加认知负荷——这一点官网反思部分也提到了"植物本身容易混淆"的问题。

### 2.3 交互流畅度

由于该产品为概念设计项目，未提供可实际安装运行的应用，因此无法评估真实交互流畅度。Figma 原型在浏览器中加载正常，但点击交互热点无响应（可能需要登录 Figma 或原型本身只做了有限交互）。

官网页面滚动流畅，图片加载无明显延迟。"View Prototype" 按钮有明确的 hover 样式（橙色边框），视觉反馈清晰。

### 2.4 文案质量

官网文案为**英文**，语言简洁专业。关键文案摘录：

> "A gamified tool for those with ADHD to improve their focus."
> — 首页副标题

> "FocusBud is your focus companion. Inspired by the Tamagotchi, the wildly successful and popular Japanese virtual pet used to teach responsibility. FocusBud aims to help those with ADHD better focus in a work environment."
> — Problem 区

> "Just like the Tamagotchi, FocusBud empowers its users with a sense of accountability. Rewarding focus sessions and mitigating distractions."
> — Solution 区

文案中 "gamified"、"companion"、"accountability" 等词准确传达了产品定位，未出现机翻痕迹。但全站为英文，无中文或其他语言版本。

### 2.5 可访问性观察（肉眼可见的）

- **对比度**：绿色按钮（如 "Done"）上的白色文字对比度看起来足够；但部分浅绿色背景上的白色/灰色文字可能接近 WCAG AA 边界。
- **字号**：正文字号适中，但 Figma 原型中部分小标签（如日历中的日期数字）在缩小展示时可能难以辨认。
- **键盘可达性**：无法测试，因无实际可运行的应用。
- **深色模式**：官网和 UI 设计均为浅色主题，未展示深色模式支持。

---

## 3. 官网描述

### 3.1 关键文案摘录

> "FocusBud — A gamified tool for those with ADHD to improve their focus."
> — 首页 H1 区

> "FocusBud is your focus companion. Inspired by the Tamagotchi, the wildly successful and popular Japanese virtual pet used to teach responsibility."
> — Problem 区

> "Diagnoses of ADHD children and adults continues to rise each year. Simultaneously, distractions are becoming more ubiquitous."
> — Insight 区

> "Just like the Tamagotchi, FocusBud empowers its users with a sense of accountability. Rewarding focus sessions and mitigating distractions."
> — Solution 区

> "An exciting market for companion focused apps already exist, like the Amazon Echo."
> — Reflection / What worked?

### 3.2 核心卖点（官网视角）

1. **游戏化专注机制**：以 Tamagotchi 式的"养植物"为核心，将专注行为转化为游戏内正向反馈（原文锚：Solution 区）。
2. **ADHD 专项设计**：针对 ADHD 用户在工作环境中的专注问题，强调"责任感"和"分心缓解"（原文锚：Problem + Insight 区）。
3. **软硬件结合**：不仅设计 App UI，还设计了配套的物理硬件设备（原文锚：产品渲染图 + Physical Mock-ups 区）。

### 3.3 与实际体验的差距

| 卖点 | 官网原文 | 实际体验 | 差距 |
|---|---|---|---|
| 产品可用性 | 展示完整 UI 流程和 Figma 原型 | 无可安装/可下载的产品，Figma 原型交互受限 | 概念设计 ≠ 可运行产品 |
| 硬件产品 | 展示 3D 渲染图和实体模型 | 无实际硬件或量产计划 | 设计稿 ≠ 实体产品 |
| ADHD 验证 | 基于二手研究和竞品分析 | 无真实 ADHD 用户测试数据展示 | 研究结论未经用户验证 |

---

## 5. 目标用户

基于官网信息，FocusBud 的**核心目标用户**为：

1. **ADHD 患者**（儿童和成人）：官网明确将 ADHD 人群作为主要服务对象，Problem 区直接引用 ADHD 诊断率上升的数据。
2. **办公场景下的知识工作者**：Solution 区提到 "in a work environment"，暗示主要场景是工作/学习时的桌面专注。
3. **游戏化 productivity 工具爱好者**：以 Tamagotchi 为灵感，吸引喜欢养成类游戏机制的用户。

目标用户定位清晰，但缺乏用户分层（如轻度 ADHD vs 重度 ADHD、儿童 vs 成人是否需要不同界面）。

---

## 6. 与同类产品对比

官网明确列出了两个竞品：

| 维度 | FocusBud（概念） | Forest | Habitica |
|---|---|---|---|
| **核心机制** | 养植物（Tamagotchi 式） | 种树（离开 App 树会枯死） | RPG 游戏化待办清单 |
| **硬件** | 设计了配套物理设备 | 无 | 无 |
| **目标人群** | ADHD 专项 | 泛大众 | 泛大众 |
| **实际可用性** | 概念设计，不可用 | 已发布（iOS/Android/浏览器扩展） | 已发布（全平台） |
| **分心记录** | 手动标记 "Distracted" | 离开 App 即失败 | 任务未完成即惩罚 |

FocusBud 与 Forest 在设计理念上最接近（都是"培育生命体"的正向激励），但 FocusBud 多了硬件组件设计和 ADHD 专项定位。与 Habitica 相比，FocusBud 的专注闭环更单一（只聚焦"专注时长"），而 Habitica 覆盖了整个生活管理（待办、习惯、每日任务）。

---

## 7. 优劣势小结

| 维度 | 优势 | 劣势 |
|---|---|---|
| 产品逻辑 | 游戏化机制（Tamagotchi 养植物）新颖且情感化；手动标记分心功能有助于自我觉察 | 仅为概念设计，无实际产品；未经验证 ADHD 用户是否真正接受该机制 |
| UI/UX | 视觉风格统一（绿色/植物主题）；流程覆盖完整（开始→执行→总结→回顾） | App UI 信息密度偏高，可能对 ADHD 用户造成认知负担；无深色模式 |
| 官网呈现 | 作品集式展示完整（研究→设计→原型→反思）；Figma 原型可交互 | 无下载/试用入口；Figma 原型需登录才能完整体验 |
| 商业化 | — | 无商业化路径、无定价、无发布计划；为 2021 年学生项目，后续无更新 |

---

## 附录 A 截图索引

| # | 文件 | 说明 |
|---|---|---|
| 01 | screenshots/01_web_homepage.png | 官网首页顶部，FocusBud 品牌展示 |
| 02 | screenshots/02_web_homepage_scroll1.png | 项目详情：团队、角色、问题陈述 |
| 03 | screenshots/03_web_homepage_scroll2.png | 产品渲染图与工具使用 |
| 04 | screenshots/04_web_homepage_bottom.png | 二手研究、竞品分析、用户画像 |
| 06 | screenshots/06_web_design_process.png | 五步设计流程与草图 |
| 08 | screenshots/08_web_mockups.png | UI 核心流程：Home → Start → In Session → Summary |
| 09 | screenshots/09_web_ui_detail.png | 会话总结界面与项目反思 |
| 10 | screenshots/10_web_footer.png | 页脚：其他项目推荐与社交媒体 |
| 16 | screenshots/16_web_figma_prototype.png | Figma 可交互原型：Sessions 日历视图 |
