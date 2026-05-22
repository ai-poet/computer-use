# Focus Bear 产品分析报告

| 项目 | 值 |
|---|---|
| 官网 | https://www.focusbear.io/ |
| 下载链接 | Mac: https://downloads.focusbear.io/FocusBearSetupMac.dmg; Windows: https://downloads.focusbear.io/FocusBearSetupWindows.exe |
| 报告日期 | 2026-05-22 |
| 主机 | linux / x86_64 |
| Runtime | sandbox-local |
| 模式 | web-only |
| 用时 | ~20 分钟 |

> 本次为网页版分析，未驱动桌面端 — 产品官网未提供 Linux 桌面版安装包（仅 Mac/Windows），当前沙盒为 Linux XFCE 环境，无可用桌面端安装包。

---

## 1. 详细的产品逻辑介绍

### 1.1 总定位

Focus Bear 是一款面向 ADHD 与 ASD 人群（即 "AuDHDers"）的跨平台生产力与习惯养成应用，核心解决思路是"让健康习惯成为阻力最小的路径"。它通过设备级分心阻断、引导式早晚例程、定时休息提醒三大支柱，帮助用户在早晨建立专注状态、白天保持深度工作、晚间顺利切换至休息模式。产品由神经多样性（neurodivergent）团队自建自用，强调"基于 lived experience"而非泛泛的效率提升。

### 1.2 界面清单

按出现顺序列出实际浏览到的所有主要网页界面：

| # | 界面 | 入口 | 主要功能 | 截图 |
|---|---|---|---|---|
| 1 | 首页 | https://www.focusbear.io/ | 产品定位、核心价值主张、CTA | [01_web_homepage.png](screenshots/01_web_homepage.png) |
| 2 | 定价页 | /pricing | 免费/Pro 两档定价、学生折扣 | [02_web_pricing.png](screenshots/02_web_pricing.png) |
| 3 | 功能页 | /features | 分心阻断、例程、休息、手机 Zen 模式 | [03_web_features.png](screenshots/03_web_features.png) |
| 4 | FAQ 页 | /faqs | 平台支持、隐私、定价、ADHD 相关问答 | [04_web_faqs.png](screenshots/04_web_faqs.png) |
| 5 | 科学页 | /en/science-behind-focus-bear | 5 个科学支撑点、研究引用 | [05_web_science.png](screenshots/05_web_science.png) |
| 6 | 关于页 | /about | 团队背景、创始人故事、使命 | [06_web_about.png](screenshots/06_web_about.png) |

### 1.3 各界面功能与评价

#### 1.3.1 首页

- **功能**：首屏以 H1 "Your personal focus coach for work and life" 直接点明定位；副标题 "Block distractions, stick to routines, and train your brain to focus better automatically" 三句话覆盖三大核心功能。首屏底部有一个橙色的 "Get the App" CTA 按钮。往下滚动依次呈现：ADHD 聚焦主题（"Focusing when you have ADHD is hard but not impossible"）、差异化卖点（"What makes Focus Bear Different"）、博客精选、创始人手记、科学背书、FAQ 入口。
- **交互**：顶部固定导航栏包含 Features / Pricing / FAQ / Science / Blog / Contact / Search / Get the App。移动端有汉堡菜单。"Get the App" 展开下载浮层，列出 Mac/Windows/Android/iOS 四个平台。
- **评价**：首屏信息层级清晰，主 CTA 颜色（橙色 `#F5A623` 系）在浅色背景上对比度足够。但首屏下方各 section 之间的视觉节奏偏快，从 "Different" 到博客到创始人到科学，section 间距较小，滚动时容易有"还没读完就进入下一段"的仓促感。另外 "Get the App" 浮层中 Android 状态标注为 "We're working on the Android App"并附 waitlist 表单，对期待移动端体验的用户可能产生落差。
- **截图**：[01_web_homepage.png](screenshots/01_web_homepage.png)

#### 1.3.2 功能页 (/features)

- **功能**：详细展开四大功能模块：(1) 跨设备分心阻断 — 支持 block list/allow list，分 "Cuddly Bear"（温和提醒）和 "Grizzly Bear"（立即阻断）两档严格度；(2) 早晚例程 — 支持 habit stacking，早晨引导完成冥想/运动等，晚间 wind down routine；(3) 生产力休息 — 默认每 20 分钟提醒，支持会议检测避免中断视频通话；(4) 手机 Zen 模式 — 电脑端启动深度工作后手机同步进入免打扰。每个模块配图文说明和 "Get the App" CTA。
- **交互**：单页长滚动，无子页面跳转。各功能模块以左右交替图文排版呈现。
- **评价**：功能描述具体且可验证（如 "每 20 分钟"、"检测会议"），避免了空泛的宣传。图文交替排版在桌面端阅读体验良好，但图片与文字的对齐在部分 viewport 下可能出现留白不均。休息模块中的 "quantified self" 子功能（追踪喝水杯数等）埋得较深，仅在展开文本中提到，未在视觉层级上突出。
- **截图**：[03_web_features.png](screenshots/03_web_features.png)

#### 1.3.3 定价页 (/pricing)

- **功能**：两栏定价对比 — 左侧 "Essentials" 免费（Pomodoro 最多 25 分钟/次、最多阻断 5 个网站/应用、早晚例程各最多 3 个习惯、休息最多 3 个活动、浏览器标签限制器、待办列表）；右侧 "Pro" $9.99/月（连续 Pomodoro、无限阻断、AI 阻断、专注模式、专注音乐、会议检测、问责伙伴功能、自定义严格度）。顶部有 "3 ways Focus Bear can help you get stuff done" 的价值说明，底部有学生 50% 折扣入口和 7 天免费试用说明。
- **交互**：无切换/折叠，直接呈现。学生折扣需要输入学校邮箱提交申请。
- **评价**：免费版的功能限制较为严格（仅 5 个阻断目标、25 分钟单次专注），对重度用户而言免费版体验可能很快触顶。定价页将 "Eliminate Distractions / Build Healthy Habits / Prevent Burnout" 三个价值维度放在价格上方，有助于用户在看到数字前先建立价值锚点。但 "Pro" 栏中 "Other Add-Ons $9.99/month" 的文案容易让人误解为额外加价，实际上是 Pro 档位的总价。
- **截图**：[02_web_pricing.png](screenshots/02_web_pricing.png)

#### 1.3.4 FAQ 页 (/faqs)

- **功能**：分 "About the App / Pricing / About ADHD" 三个分类，共约 15 个问答。覆盖平台支持、多设备同步、隐私（明确声明不记录键盘和截图）、会议干扰、Do Not Disturb 兼容、休息频率、ADHD 适用性等。
- **交互**：问答以折叠卡片形式呈现，点击展开/收起。
- **评价**：隐私问题的回答直接且具体（"No. The only thing we log is..."），对注重数据安全的用户是加分项。关于 ADHD 的问答提供了研究引用链接（"Click here to read more"），体现了科学严谨性。但部分回答较长（如 "Why is it good for people with ADHD?"），在手机端阅读可能负担较重。
- **截图**：[04_web_faqs.png](screenshots/04_web_faqs.png)

#### 1.3.5 科学页 (/en/science-behind-focus-bear)

- **功能**：系统阐述 5 个科学支撑点 — (1) 移除分心（引用互联网/手机对生产力的负面影响研究）；(2) 开启正确的一天（运动/冥想改善 ADHD 成人注意力）；(3) 消除决策疲劳（自动呈现预设例程）；(4) 视觉提示增强专注（引用 Balcetis 等人研究）；(5) 提升动机（每周自动追踪并图表化呈现）。底部附有 ADHD 社会经济影响的数据（美国每年 870-1380 亿美元损失）及多篇研究引用。
- **交互**：单页长滚动，引用以脚注/链接形式嵌入正文。
- **评价**：这是同类产品官网中少见的"硬科学"页面，引用具体到了作者和年份（Doshi et al., 2012; Caci et al., 2014 等），增强了可信度。但页面排版偏文字密集，缺乏数据可视化（如把 "870-1380 亿美元"做成信息图会更有冲击力）。
- **截图**：[05_web_science.png](screenshots/05_web_science.png)

#### 1.3.6 关于页 (/about)

- **功能**：团队自述神经多样性背景（"Half of our team is ND"），创始人以第一人称讲述 late-diagnosed AuDHDer 的个人经历，包括尝试 parental control apps、把电脑锁在柜子里、让妻子监督等失败经历，最终引出开发 Focus Bear 的动机。附有 "Learn more about the science" 和 "Founder's Note" 两个 CTA。
- **交互**：单页长滚动，创始人笔记以引用块/书信体呈现。
- **评价**：创始人故事极具感染力（"my cheeks were getting sore" 的幽默自嘲降低了技术产品的冰冷感），且明确标注了目标用户年龄（15 岁以上）。但页面缺少团队照片或具体成员介绍，对"团队有一半是 ND"这一关键信任点缺乏具象化支撑。
- **截图**：[06_web_about.png](screenshots/06_web_about.png)

---

## 2. UI/UX 风格和质量描述

### 2.1 视觉风格

整体采用暖色调（米白/浅橙背景 + 橙色 `#F5A623` 系强调色），搭配圆润的插画风格（熊的形象简洁友好）。字体使用 Inter + Montserrat，标题字重较高（bold/semibold），正文行高适中。视觉上介于"健康类 App"和"生产力工具"之间，没有传统企业软件的冰冷感，也不至于像儿童 App 般过于幼稚。

### 2.2 信息密度与层级

首屏信息量适中 — H1 + 副标题 + CTA 按钮，没有过多干扰。但往下滚动后，各 section 间距紧凑，"What makes Different" 三栏卡片在 1280px 宽度下文字较多，每栏约 80-100 字，需要一定阅读投入。定价页的两栏对比清晰，免费/Pro 的功能差异用对勾/横线标注，一眼可辨。

### 2.3 交互流畅度

官网为 Webflow 构建的静态站点，页面加载较快（首屏约 1-2s）。导航栏固定在顶部，滚动时无卡顿。FAQ 折叠卡片的展开/收起有平滑动画。下载浮层从顶部滑入，关闭按钮明显。

### 2.4 文案质量

官网文案统一使用英文，无多语言切换。用词精准且具亲和力 — 如 "AuDHDers" "lived experience" "Super Saiyan status as a Yogi" 等表达既有社群归属感又不失幽默。技术术语（如 "habit stacking" "quantified self" "nudge theory"）均有上下文解释，对非专业用户友好。

### 2.5 可访问性观察

橙色 CTA 按钮在浅色背景上对比度满足 WCAG AA。文字字号最小约 14px，未观察到明显的键盘可达性问题。但未找到深色模式切换入口，也未看到字体大小调整控件。

---

## 3. 官网描述

### 3.1 关键文案摘录

> "Your personal focus coach for work and life. Block distractions, stick to routines, and train your brain to focus better automatically."
> — 首页 H1 + 副标题

> "Built by a team with ADHD + ASD for AuDHDers who need to be productive, punctual, and peaceful."
> — 首页 meta description

> "Standard productivity apps work well for neurotypical people but don’t take our real-time habit guide into account."
> — 首页 "What makes Different" section

> "Focus Bear is smart enough to not pop up during video calls. We have two modes: 'cuddly bear' mode and 'grizzly bear' mode."
> — FAQ 页

### 3.2 核心卖点（官网视角）

1. **神经多样性团队自建自用**（"Built by a team with ADHD + ASD" — 首页 meta）
2. **跨设备分心阻断**（电脑 + 手机同步阻断 — 功能页）
3. **引导式习惯养成而非单纯追踪**（"guides you through your habits in real-time" — 功能页）
4. **会议感知智能休息**（"auto-detects meetings" — 功能页）
5. **科学背书**（5 个研究支撑点 + 文献引用 — 科学页）

### 3.3 与实际体验的差距

由于本次为 web-only 分析，未实际安装桌面/移动应用，以下差距仅基于官网声明与网页可验证信息的对比：

| 卖点 | 官网原文 | 网页可验证情况 | 差距 |
|---|---|---|---|
| Android 已可用 | 导航栏显示 "Download for Android" | 点击后显示 "We're working on the Android App" + waitlist 表单 | Android 实际未正式发布，官网入口存在误导 |
| 免费版可用 | "Focus Bear is free to use for Basic Features" | 免费版功能限制严格（5 个阻断目标、25 分钟单次专注、3 个习惯） | 免费版作为"试用"更合适，长期使用的核心功能均需付费 |

---

## 4. 定价

| 档位 | 价格 | 核心限制 |
|---|---|---|
| Essentials（免费） | $0 | Pomodoro 单次最多 25 分钟；阻断最多 5 个网站/应用；早晚例程各最多 3 个习惯；休息最多 3 个活动 |
| Pro | $9.99/月 | 无上述限制；增加 AI 阻断、专注模式、专注音乐、会议检测、问责伙伴、自定义严格度 |

- 学生凭学校邮箱可申请 50% 折扣
- 7 天免费试用，无需信用卡
- 财务困难用户可联系 support@focusbear.io 申请折扣

---

## 5. 目标用户

1. **核心用户**：15 岁以上的 ADHD/ASD（AuDHD）人群，需要在工作/学习中保持专注并建立健康习惯
2. **扩展用户**：任何希望减少数字分心、建立早晚例程的知识工作者
3. **排除用户**：不需要严格阻断机制或习惯引导的轻度效率工具用户（免费版限制较严，可能直接劝退）

---

## 6. 与同类产品对比

| 对比维度 | Focus Bear | Freedom | Forest |
|---|---|---|---|
| 目标人群 | ADHD/ASD 专项 | 泛生产力用户 | 泛专注力用户 |
| 阻断范围 | 跨设备（电脑+手机） | 跨设备 | 仅手机（种树游戏化） |
| 习惯养成 | 引导式早晚例程（主动引导） | 无 | 无 |
| 休息提醒 | 内置，带会议检测 | 无 | 无 |
| 定价 | $9.99/月，学生半价 | $8.99/月（年付 $3.33/月） | 免费+Pro $1.99 一次性 |
| 科学背书 | 5 个研究支撑点+文献引用 | 较少 | 较少 |

Focus Bear 与 Freedom 的核心差异在于：Freedom 是"纯阻断工具"，Focus Bear 是"阻断+习惯引导+休息"的整合方案。与 Forest 的差异更明显：Forest 靠游戏化（种树）提供正向激励，Focus Bear 靠例程引导和会议感知提供结构性支持。

---

## 7. 优劣势小结

| 维度 | 优势 | 劣势 |
|---|---|---|
| 产品逻辑 | ADHD/ASD 专项定位精准；跨设备同步；会议感知休息；"Cuddly/Grizzly" 两档严格度设计人性化 | Android 尚未正式发布；免费版功能限制过严，几乎只能作为试用；无 Linux 桌面版 |
| UI/UX | 暖色调视觉友好；文案有亲和力；科学页研究引用严谨 | 部分页面文字密度偏高；首屏下方 section 间距紧凑；无深色模式 |
| 官网描述 | 创始人故事真实可信；FAQ 隐私回答直接明确；定价页价值锚点前置 | Android 下载入口存在误导（显示下载按钮实际为 waitlist）；免费/Pro 的功能差异未在首页直接呈现 |

---

## 附录 A 截图索引

| # | 文件 | 说明 |
|---|---|---|
| 01 | screenshots/01_web_homepage.png | 官网首页首屏 |
| 02 | screenshots/02_web_pricing.png | 定价页完整视图 |
| 03 | screenshots/03_web_features.png | 功能页完整视图 |
| 04 | screenshots/04_web_faqs.png | FAQ 页完整视图 |
| 05 | screenshots/05_web_science.png | 科学背书页完整视图 |
| 06 | screenshots/06_web_about.png | 关于/创始人页完整视图 |

> 编号规则：`NN_<source>_<view>.png`，本次全为网页截图（`source=web`），因产品未提供 Linux 桌面版，无 `app` 段截图。
