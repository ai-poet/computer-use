# Deepwrk 产品分析报告

| 项目 | 值 |
|---|---|
| 官网 | https://www.deepwrk.io/ |
| 下载链接 | — |
| 报告日期 | 2026-05-22 |
| 主机 | linux / x86_64 |
| Runtime | sandbox-local |
| 模式 | web-only |
| 用时 | ~25 分钟 |

> 本次为网页版分析 — Deepwrk 是纯 Web 应用（app.deepwrk.io），官网未提供任何桌面端安装包（.dmg/.exe/.deb/AppImage）。

---

## 1. 详细的产品逻辑介绍

### 1.1 总定位

Deepwrk 是一款面向 ADHD（注意力缺陷多动障碍）成年人的在线"body doubling"（陪伴专注）平台，通过虚拟群组视频 coworking 的形式，帮助用户减少分心、提升专注力、完成拖延的任务。产品由主持人（host）引导结构化专注会议，结合行为科学原理（社会促进、问责制、时间盒、单任务）和 gamification（游戏化奖励），将 ADHD 从"弱点"重构为可被社群力量加持的特质。

### 1.2 界面清单

| # | 界面 | 入口 | 主要功能 | 截图 |
|---|---|---|---|---|
| 1 | 官网首页 | https://www.deepwrk.io/ | 产品介绍、核心卖点、用户证言、行为科学背书 | [01_web_homepage_full.png](screenshots/01_web_homepage_full.png) |
| 2 | 功能介绍页 | /accountability-partner-app | Accountability partner 概念科普、四步流程、科学原理 | [03_web_features.png](screenshots/03_web_features.png) |
| 3 | 定价页 | /pricing | 三档订阅方案、FAQ、页脚导航 | [02_web_pricing_full.png](screenshots/02_web_pricing_full.png) |
| 4 | Web App 登录页 | app.deepwrk.io/main-login | 邮箱/Google/Facebook 登录入口 | [04_web_app_login.png](screenshots/04_web_app_login.png) |

### 1.3 各界面功能与评价

#### 1.3.1 官网首页

- **功能**：首屏即传达核心主张 — "Focus better. Get more done. Take control of ADHD"，配合视频通话界面截图（展示多人视频格子的 body doubling 场景）。首屏下方用统计数据建立信任："2x your productivity"、"3.8x the odds of finishing your tasks"。继续向下滚动，依次呈现：问题共鸣区（"Struggling to get started? stay on task? focus?"）、任务类型标签（Design、Do the laundry、Plan your week 等）、"How It Works"四步流程、"What's Included"功能清单、科学原理区、用户证言轮播、定价入口、FAQ 折叠面板。
- **交互**：顶部固定导航栏包含 Logo、"Learn More"下拉、"Login"、紫色 CTA "Try for Free"。首屏 CTA 按钮直达注册页。页面滚动时各 section 以卡片式布局依次展开，无复杂动效。
- **评价**：信息架构清晰，从"痛点共鸣 → 解决方案 → 社会证明 → 行动号召"的漏斗设计完整。统计数据（2x、3.8x）前置有利于快速建立信任。不足：首屏视频通话截图中的界面细节较小，新用户难以一眼看出具体如何使用；"How It Works"区的四步流程（Book → Join → Focus → Earn Rewards）文字说明偏简略，对 body doubling 概念陌生的用户可能需要更多解释。
- **截图**：[01_web_homepage_full.png](screenshots/01_web_homepage_full.png)

#### 1.3.2 功能介绍页（Accountability Partner App）

- **功能**：以"Accountability Partner App: Get More Done, Together"为标题，系统性地解释 accountability partner 概念、Deepwrk 的四步工作流（Book → Join → Focus → Earn Rewards → Community）、以及六项行为科学支撑（Accountability、Social Facilitation、Intentionality、Timeboxing、Monotasking、Flow State）。每项科学原理都配有简要说明和引用来源。
- **交互**：与首页共享导航和页脚，内容以长文+插图形式单页滚动呈现。无交互式 demo 或视频播放。
- **评价**：科普价值高，将"body doubling"从民间经验上升到行为科学理论，有利于消解"这是不是玄学"的疑虑。但页面纯文本+静态图，缺乏动态演示（如嵌入一段 30 秒 session 录像），对视觉型学习者的吸引力有限。
- **截图**：[03_web_features.png](screenshots/03_web_features.png)

#### 1.3.3 定价页

- **功能**：展示两档个人订阅方案（Monthly $19/mo、Annual $12/mo）和两档 Premium 方案（£150、£500）。个人方案均标"No credit card required"，暗示免费试用机制。下方列出通用功能清单（Host-led group focus sessions、Silent focus space、Access to the community、Member perks and discounts）。页面中部有用户证言轮播，底部为 12 项 FAQ 折叠面板和页脚。
- **交互**：月付/年付切换通过两个独立卡片呈现，无显式 toggle 开关。FAQ 为可点击展开的 accordion 组件。
- **评价**：定价结构简洁，但 Premium 方案（£150、£500）的功能差异未在页面上直观对比，用户需自行推断"为什么贵 3 倍多"。FAQ 覆盖了核心疑虑（"Is Deepwrk free?"、"Do I have to keep my video on?"、"Is it introvert friendly?"），降低了决策摩擦。月付和年付的 savings 未明确标出（年付相当于 37% 折扣），是个可优化的转化点。
- **截图**：[02_web_pricing_full.png](screenshots/02_web_pricing_full.png)

#### 1.3.4 Web App 登录页

- **功能**：极简登录界面，中央卡片包含 Deepwrk Logo、"Welcome back to Deepwrk!"问候、Google/Facebook 第三方登录按钮、邮箱/密码表单、"Forgot password?"链接。背景为纯紫色渐变+火箭插画。
- **交互**：第三方登录优先于邮箱登录，降低了注册门槛。无"Sign up"入口在登录页（需从官网 CTA 进入）。
- **评价**：视觉风格与官网一致（紫色主色调），但登录页信息密度过低 — 仅有登录功能，无产品价值提示（如"New here? See what Deepwrk can do for you"），对从外部链接直接到达的用户不够友好。
- **截图**：[04_web_app_login.png](screenshots/04_web_app_login.png)

---

## 2. UI/UX 风格和质量描述

### 2.1 视觉风格

整体采用**紫白配色**（主色为深紫到浅紫渐变，辅白/浅灰背景），调性偏向"温暖专业"而非"医疗/临床"。插画风格为扁平化人物插画（首页的视频通话截图展示真实用户面孔，增强亲和力）。字体无衬线，标题字号大、字重高，正文区留白充足。无深色模式切换入口。

### 2.2 信息密度与层级

首页首屏信息量适中：H1（主标题）+ 副标题 + CTA 按钮 + 产品截图 + 统计数字，视觉焦点明确。"How It Works"区采用数字编号+图标+短文案的三栏/四栏布局，信息层级清晰。但"What's Included"区的功能卡片在截图中未能完全识别（可能被截断或未在首屏完整展示），需滚动后才能看到完整内容。定价页的两栏卡片在移动端可能需要垂直堆叠，桌面端并排展示合理。

### 2.3 交互流畅度

- **加载**：官网基于 Webflow 构建，静态页面加载无明显延迟。
- **滚动**：长页面滚动流畅，无固定锚点导航（如"返回顶部"按钮）。
- **反馈**：CTA 按钮有圆角填充样式，hover 状态未在截图中验证。FAQ accordion 的展开/收起动效未经验证。
- **表单**：登录页输入框有标准边框样式，但无焦点状态（focus ring）的截图证据。

### 2.4 文案质量

官网文案整体**口语化、共情导向**，大量使用第二人称"you"和 ADHD 社群内部语言（"body doubling"、"find your flow"、"take control of ADHD"）。产品名"Deepwrk"与"deep work"谐音，易记且有语义关联。文案一致性良好：首页、功能页、定价页的核心主张（"focus better, get more done"）保持统一。无明显的机翻痕迹，专业术语（social facilitation、timeboxing）均有简要解释，降低了认知门槛。

### 2.5 可访问性观察（肉眼可见）

- **对比度**：紫色背景+白色文字的组合在截图中清晰可读，但具体是否满足 WCAG AA 需工具验证。
- **键盘可达性**：未测试 Tab 键导航顺序。
- **深色模式**：未提供切换入口。
- **字号**：正文字号适中，未提供显式字号调节功能。

---

## 3. 官网描述

### 3.1 关键文案摘录

> "Focus better. Get more done. Take control of ADHD" — 首页 H1

> "Group body doubling for adults with ADHD to escape distractions and get anything done" — 首页副标题

> "Deepwrk is a body doubling website for adults with ADHD to focus better, work smarter & get more done" — meta description

> "Regular accountability check-ins increase odds of completing a goal by 3.8x (from 25% to 95%)" — 科学背书区

> "Presence of people, even not engaged in the same task, can boost your performance by 16-32%" — 社会促进原理

> "Deep, focused work enables a flow state, which can boost productivity by 500% (McKinsey)" — 心流状态引用

### 3.2 核心卖点（官网视角）

1. **行为科学背书**：将 body doubling 与六项心理学/行为经济学原理挂钩（Accountability、Social Facilitation、Intentionality、Timeboxing、Monotasking、Flow State），并引用具体数据（3.8x、16-32%、500%）。
2. **社群归属感**：强调"ADHD Community"、"people who get it"，将产品定位从"工具"升级为"社群"。
3. **游戏化激励**：通过"Earn Rewards"、里程碑奖励、徽章系统，将枯燥的任务完成转化为正向反馈循环。
4. **结构化会议**：由 host 引导的 predefined agenda，降低用户"不知道做什么"的认知负担。
5. **免费试用门槛低**：7 天免费试用，无需信用卡即可开始。

### 3.3 与实际体验的差距

| 卖点 | 官网原文 | 实际体验 | 差距 |
|---|---|---|---|
| 产品形式 | "Body doubling website"、"Body doubling app" | 仅体验到官网静态页面和登录页，未进入实际 session | 无法验证 video call 质量、host 引导水平、社区活跃度 |
| 游戏化 | "Gamification: Experience rooted in behavioural science" | 未体验到实际的奖励/徽章系统 | 游戏化的具体机制和效果未知 |
| 定价 | "$19/month or $12/month if paid annually" |  pricing 页展示，但 £150/£500 Premium 方案的功能差异未详细说明 | 高阶方案的价值主张不够清晰 |

---

## 4. 定价

| 方案 | 价格 | 内容 |
|---|---|---|
| Free | £0 | Power Hour：每日免费 coworking session |
| Monthly | $19/月 | Unlimited access，无信用卡要求 |
| Annual | $12/月（年付）| Unlimited access for one year，相当于 37% 折扣 |
| Premium ( tiers) | £150 / £500 | 40+ facilitated live sessions/周、weekly/monthly planning sessions、host-led group focus、silent focus space、member perks |

**观察**：个人订阅采用简单的两档结构（月付/年付），降低了选择困难。Premium 方案以英镑计价（与个人方案的美元不同），可能暗示目标市场的地域差异。£500 方案的功能描述与 £150 方案有重叠，差异化不够明显。

---

## 5. 目标用户

- **核心用户**：已确诊或自我认同为 ADHD 的成年人（18-45 岁），远程工作/自由职业/学生群体，因分心、拖延、启动困难而影响工作效率。
- **扩展用户**：无 ADHD 诊断但希望提升专注力的远程工作者（官网明确欢迎："you don't need a formal ADHD diagnosis to join"）。
- **排除用户**：需要深度协作（如 pair programming、实时编辑）的团队用户 — Deepwrk 的 body double "doesn't actively help, engage or interfere with your tasks"。

---

## 6. 与同类产品对比

| 维度 | Deepwrk | Focusmate | Flow Club |
|---|---|---|---|
| **目标人群** | ADHD 成年人（核心），扩展至一般远程工作者 | 泛远程工作者、自由职业者 | 创业者、创意工作者 |
| **会议形式** | Host 引导的 group session（多人） | 1-on-1 peer matching（双人） | Host 引导的 group session（多人） |
| **科学背书** | 六项行为科学原理，引用具体数据 | 轻量提及 accountability | 提及 flow state，但无系统理论框架 |
| **社区属性** | 强 — "ADHD Community"是核心卖点 | 弱 — 工具导向，匹配陌生人 | 中 — 有社群感但无疾病标签 |
| **定价** | $12-19/月，Premium £150-500 | 免费基础版 + $9.99/月 Pro | $40-60/月（更高阶） |
| **差异化** | ADHD 专属定位 + 游戏化 + 行为科学系统 | 极简 1-on-1，低门槛 | 更高定价，更偏"精英社群" |

Deepwrk 的核心差异化在于**将 ADHD 从"需要被修正的问题"重构为"需要被社群加持的特质"**，这种身份认同层面的定位是 Focusmate 等泛工具不具备的。

---

## 7. 优劣势小结

| 维度 | 优势 | 劣势 |
|---|---|---|
| 产品逻辑 | ADHD 专属定位精准，行为科学背书系统性强，社群归属感强 | 纯 Web 应用无桌面端，离线场景不可用；未体验实际 session 质量 |
| UI/UX | 紫白配色温暖专业，信息架构漏斗完整，文案共情力强 | 首屏产品截图细节小，功能页缺动态演示，登录页缺价值提示 |
| 工程质量 | Webflow 构建，静态页面加载快；第三方登录降低注册门槛 | 无桌面客户端、无移动端 App（至少官网未宣传）；深色模式缺失 |

---

## 附录 A 截图索引

| # | 文件 | 说明 |
|---|---|---|
| 01 | screenshots/01_web_homepage_full.png | 官网首页完整长截图（含 How It Works、What's Included、科学原理、证言区） |
| 02 | screenshots/02_web_pricing_full.png | 定价页完整长截图（含 FAQ、页脚导航） |
| 03 | screenshots/03_web_features.png | 功能介绍页（Accountability Partner App） |
| 04 | screenshots/04_web_app_login.png | Web App 登录页 |
