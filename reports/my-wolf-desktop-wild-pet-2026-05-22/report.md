# My Wolf — Desktop Wild Pet（我的小狼）产品分析报告

| 项目 | 值 |
|---|---|
| 官网 | https://store.steampowered.com/app/1110890/MY_WOLF__Desktop_Wild_Pet/ |
| 下载链接 | — |
| 报告日期 | 2026-05-22 |
| 主机 | linux / x86_64 |
| Runtime | sandbox-local |
| 模式 | web-only |
| 用时 | 约 15 分钟 |

> 本次为网页版分析，未驱动桌面端 — 产品仅支持 Windows 10/11，官网（Steam 商店）未提供 Linux 安装包。

---

## 1. 详细的产品逻辑介绍

### 1.1 总定位

My Wolf 是一款将桌面宠物养成与动态壁纸结合的 Windows 桌面端应用，通过 Steam 平台发行。用户在桌面上养育一只小狼，通过喂食、饮水、睡眠等日常照料使其成长，同时狼的行为会以 3D 动态壁纸的形式实时呈现在桌面图标与窗口下方。产品由 3dm live wallpapers 开发，2022 年 6 月 11 日发布，目前处于 Early Access 阶段。

### 1.2 界面清单

按 Steam 商店页面呈现顺序列出所有可见界面：

| # | 界面 | 入口 | 主要功能 | 截图 |
|---|---|---|---|---|
| 1 | Steam 商店首页 | https://store.steampowered.com/app/1110890/ | 产品展示、购买、评价、系统需求 | [01_web_homepage.png](screenshots/01_web_homepage.png) |
| 2 | 产品头图区 | 商店页顶部 | 品牌标识、主视觉展示 | [02_web_header.jpg](screenshots/02_web_header.jpg) |
| 3 | 产品封面 | 商店页侧栏 | 产品主封面图 | [03_web_capsule.jpg](screenshots/03_web_capsule.jpg) |
| 4 | 游戏艺术场景 | 商店页滚动区 | 展示游戏美术风格 | [04_web_artwork.png](screenshots/04_web_artwork.png) |
| 5 | 商店核心信息 | 商店页中部 | 标题、评价、开发商、发布日期 | [05_web_overview.png](screenshots/05_web_overview.png) |
| 6 | About This Game | 商店页描述区 | 产品介绍、价格、购买按钮 | [06_web_about.png](screenshots/06_web_about.png) |
| 7 | 功能特性 | 商店页特性区 | 详细功能列表 | [07_web_features.png](screenshots/07_web_features.png) |
| 8 | 支持信息 | 商店页底部 | 多屏支持、自动暂停、Early Access 说明 | [08_web_support.png](screenshots/08_web_support.png) |

### 1.3 各界面功能与评价

#### 1.3.1 Steam 商店首页

- **功能**：作为产品的唯一官方展示入口，承载产品信息展示、用户购买、评价浏览、系统需求查询等功能
- **交互**：用户通过 Steam 客户端或浏览器访问，可点击"Add to Cart"购买，可浏览用户评价，可查看系统需求
- **评价**：Steam 商店页面采用标准的 Steam 游戏页面模板，信息结构清晰，但页面加载时存在年龄验证机制（部分区域需要交互后才能显示完整内容）。页面响应式适配在 Firefox 中表现正常
- **截图**：[01_web_homepage.png](screenshots/01_web_homepage.png)

#### 1.3.2 产品头图与封面区

- **功能**：展示产品品牌标识和主视觉。头图包含 "MY WOLF DESKTOP WILD PET" 标题文字，封面图为标准的 Steam 胶囊图格式
- **交互**：静态展示，无交互功能
- **评价**：视觉风格采用低多边形（low-poly）3D 渲染风格，色彩以暖色调为主（橙黄、粉紫），营造出童话般的自然场景氛围。标题字体醒目，品牌识别度较高
- **截图**：[02_web_header.jpg](screenshots/02_web_header.jpg)、[03_web_capsule.jpg](screenshots/03_web_capsule.jpg)

#### 1.3.3 商店核心信息区

- **功能**：集中展示产品关键元数据：标题图、评价摘要、发布日期、开发商/发行商信息、用户标签、特性标签
- **交互**：可点击评价查看详细评价内容，可点击标签查看同类游戏，可点击"Sign in"登录 Steam 账号
- **评价**：信息层级清晰，评价 "Mostly Positive (174) - 77%" 以绿色高亮显示，传达出产品的用户口碑。开发商和发行商均为 "3dm live wallpapers"，表明这是团队自营产品。标签区显示为 Adventure、Casual、Indie、Simulation、Utilities，准确反映了产品的跨界定位
- **截图**：[05_web_overview.png](screenshots/05_web_overview.png)

#### 1.3.4 About This Game / 产品介绍区

- **功能**：详细描述产品功能、展示宣传图片、列出主要特性
- **交互**：静态展示，图片可点击放大（推测）
- **评价**：产品介绍采用图文混排形式，每个特性配有一张宣传图，信息传达较为直观。但部分宣传图的字体（如 "SAVE THE WOLVES"）与整体风格略有差异。产品描述开篇即点明核心定位："interactive project"、"take care of a tiny wolf"、"interactive 3D live wallpaper"
- **截图**：[06_web_about.png](screenshots/06_web_about.png)

#### 1.3.5 功能特性详情区

- **功能**：列出产品的八大核心功能特性
- **交互**：静态展示
- **评价**：功能列表采用 h2 标题 + 描述的格式，结构清晰。每个功能点都有明确的用户价值：AI 驱动的自主性、成长系统、壁纸形态、资源优化、季节变化、多屏支持、智能暂停、开机自启。这些功能点覆盖了从核心体验到系统集成的完整用户旅程
- **截图**：[07_web_features.png](screenshots/07_web_features.png)

---

## 2. UI/UX 风格和质量描述

### 2.1 视觉风格

产品采用低多边形（low-poly）3D 美术风格，色彩以暖色调为主——橙黄色的草原、粉紫色的树木、蓝绿色的湖水，营造出一种童话绘本般的自然世界氛围。从截图 [04_web_artwork.png](screenshots/04_web_artwork.png) 可以看出，场景设计具有明显的风格化特征，几何感强但细节丰富，光影柔和。这种美术风格在桌面壁纸类产品中具有辨识度，同时低多边形的特性也有助于降低 GPU 负载（与产品强调的 "Optimization" 卖点一致）。

Steam 商店页面的视觉呈现延续了这一风格，头图和封面图与产品内美术风格保持一致，形成统一的品牌认知。

### 2.2 信息密度与层级

Steam 商店页面的信息架构遵循标准的 Steam 游戏页面模板，层级清晰：
- 首屏：头图 + 核心元数据（评价、日期、开发商）
- 第二屏：价格 + 购买按钮 + About This Game
- 第三屏：功能特性列表
- 第四屏：系统需求
- 第五屏：用户支持信息

信息密度适中，没有出现信息过载的情况。主要 CTA（"Add to Cart"）在滚动到价格区域后清晰可见。

### 2.3 交互流畅度

基于网页端的观察：
- 页面加载速度一般，Steam 商店页面依赖较多 JavaScript 和外部资源
- 页面滚动流畅，无明显的卡顿现象
- 由于 Steam 的年龄验证机制，首次访问时部分区域需要额外交互才能显示完整内容

### 2.4 文案质量

产品文案采用英文撰写，语言风格偏向轻松、亲切。描述中使用了拟人化表达（"our little wolf"、"your pet"），与桌面宠物的温情定位相符。功能描述简洁明了，每个功能点都能在 1-2 句话内传达核心价值。

但存在一处明显的 Early Access 提示："Please keep in mind that is Early Access stage and not everything is ready"，其中 "that is" 存在语法错误（应为 "this is"），对专业形象略有影响。

### 2.5 可访问性观察

- Steam 商店页面本身支持响应式布局，在桌面浏览器中显示正常
- 文字与背景对比度充足，阅读无障碍
- 产品仅支持 Windows 10/11，平台限制较大

---

## 3. 官网描述

### 3.1 关键文案摘录

> "MY WOLF" is an interactive project in which you'll take care of a tiny wolf who will need some of your help to deal with the big world. Teach him to hunt, show him what is good and what is bad and thanks to this our little wolf will grow every day.
> —— About This Game, Steam 商店页

> My Wolf is displayed as an interactive wallpaper under icons and windows.
> —— Desktop wallpaper project, 功能特性

> We have probably used all the available ways to limit the use of resources (CPU/GPU) as the game is displayed as wallpaper.
> —— Optimization, 功能特性

> When you want to play a normal game, the My Wolf will automatically (will recognize another game) will pause to give you 100% power of your PC.
> —— Automatic pause, 功能特性

### 3.2 核心卖点（官网视角）

1. **交互式桌面宠物**：在桌面上养育一只会成长的狼，核心玩法是照料与培养（About This Game）
2. **3D 动态壁纸形态**：宠物行为实时呈现在桌面图标与窗口下方，不打断正常工作流（Desktop wallpaper project）
3. **AI 驱动的自主性**：狼由高级 AI 控制，可自主学习狩猎和生存技能（Advanced Wolf AI）
4. **资源优化**：采用多种技术手段（如视锥剔除）限制 CPU/GPU 占用，保证不影响正常使用（Optimization）
5. **智能系统集成**：自动检测全屏游戏并暂停、支持多显示器、支持开机自启动（Automatic pause / Multi-screen support / Automatic start）

### 3.3 与实际体验的差距

由于本次分析为 web-only 模式，未实际运行桌面端应用，以下差距基于已有信息推断：

| 卖点 | 官网原文 | 实际观察 | 差距 |
|---|---|---|---|
| 资源占用 | "use very little resources" | 最低配置要求 GTX 1050 Ti | 最低配置对一款壁纸应用而言偏高 |
| 完成度 | "Early Access stage and not everything is ready" | — | 产品仍处于早期阶段，功能可能不完整 |
| 平台支持 | "Windows 10 / 11 Only!" | 无 macOS/Linux 版 | 平台覆盖有限 |

---

## 4. 定价

产品通过 Steam 平台销售，定价为 **¥30.60**（人民币），约合 $4-5 美元（截图 [06_web_about.png](screenshots/06_web_about.png)）。这一价位在 Steam 独立游戏中属于低价档位，与产品的轻量定位相符。Steam 平台支持退款政策（游玩时间少于 2 小时且购买后 14 天内），降低了用户的尝试门槛。

---

## 5. 目标用户

基于官网用语和功能设计推断：

1. **桌面美化爱好者**：产品核心形态是动态壁纸，面向希望个性化桌面的用户
2. **虚拟宠物/养成类游戏玩家**："take care of a tiny wolf"、"teach him to hunt" 等描述表明产品包含养成要素
3. **Windows 重度用户**：多屏支持、开机自启、游戏自动暂停等功能面向长时间使用电脑的用户
4. **轻度休闲玩家**：评价标签中的 Casual、Simulation 表明这不是一款重度游戏

---

## 6. 与同类产品对比

| 对比维度 | My Wolf | Desktop Goose（桌面大鹅） | Wallpaper Engine |
|---|---|---|---|
| 核心形态 | 3D 动态壁纸 + 宠物养成 | 桌面宠物（捣蛋型） | 动态壁纸引擎 |
| 交互深度 | 中等（需要照料宠物） | 低（被动接受捣蛋） | 低（纯观赏） |
| 平台 | Windows 10/11 only | Windows | Windows（Steam） |
| 价格 | ¥30.60 | 免费 | ¥18 |
| 美术风格 | 低多边形 3D | 2D 像素/手绘 | 多样（用户创作） |

**差异点**：My Wolf 的独特之处在于将"宠物养成"与"动态壁纸"两个品类融合，既有 Wallpaper Engine 的桌面美化属性，又有虚拟宠物的情感陪伴属性，且通过 AI 系统赋予宠物一定自主性，这在同类产品中较为少见。

---

## 7. 优劣势小结

| 维度 | 优势 | 劣势 |
|---|---|---|
| 产品逻辑 | 壁纸+养成的融合定位有差异化；AI 自主性减少用户操作负担；系统集成度高（开机自启、游戏暂停） | Early Access 阶段，功能完整度待验证；平台仅限 Windows 10/11 |
| UI/UX | 低多边形美术风格辨识度高；Steam 页面信息层级清晰 | 文案存在语法错误；最低显卡要求（GTX 1050 Ti）对壁纸类应用偏高 |
| 工程质量 | 明确强调资源优化；多屏支持覆盖专业用户需求 | 用户量较小（174 条评价）；开发商为小型独立团队，长期维护能力待观察 |

---

## 附录 A 截图索引

| # | 文件 | 说明 |
|---|---|---|
| 01 | screenshots/01_web_homepage.png | Steam 商店首页底部区域 |
| 02 | screenshots/02_web_header.jpg | 产品头图（MY WOLF DESKTOP WILD PET） |
| 03 | screenshots/03_web_capsule.jpg | 产品胶囊封面图 |
| 04 | screenshots/04_web_artwork.png | 游戏艺术场景（低多边形自然风景） |
| 05 | screenshots/05_web_overview.png | 商店核心信息区（标题、评价、开发商） |
| 06 | screenshots/06_web_about.png | About This Game 与价格区 |
| 07 | screenshots/07_web_features.png | 功能特性与系统需求 |
| 08 | screenshots/08_web_support.png | 多屏支持、自动暂停、Early Access 说明 |
