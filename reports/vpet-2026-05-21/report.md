# VPet (虚拟桌宠模拟器) 产品分析报告

| 项目 | 值 |
|---|---|
| 官网 | https://store.steampowered.com/app/1920960/VPet/ |
| 下载链接 | — |
| 报告日期 | 2026-05-22 |
| 主机 | linux / x86_64 |
| Runtime | sandbox-local |
| 模式 | web-only |
| 用时 | 20 分钟 |

> 本次为网页版分析,未驱动桌面端 — VPet 原版为 Windows WPF 应用,Steam 商店在 Linux 沙盒内因 TLS 握手失败无法访问;社区 Linux 移植版仓库(shishuiqiaotou/VPet_For_Linux)返回 404,无可用 Linux 安装包。

---

## 1. 详细的产品逻辑介绍

### 1.1 总定位

VPet 是一款开源免费的 Windows 桌面宠物软件,基于 WPF (Windows Presentation Foundation) 开发。用户桌面会出现一个可互动的二次元角色(默认"萝莉丝"),支持摸头、拖拽、投喂、对话等交互,同时具备完整的数值养成系统(饱食度、心情、健康、等级)。产品通过 Steam 免费分发,支持创意工坊扩展,允许玩家自定义桌宠动画、物品、对话甚至代码插件。目标用户为二次元文化爱好者、桌面个性化追求者以及需要轻度陪伴感的电脑用户。

### 1.2 界面清单

按出现顺序列出从网页端采集到的所有主要界面/功能区域:

| # | 界面 | 入口 | 主要功能 | 截图 |
|---|---|---|---|---|
| 1 | Steam 商店页(网页) | https://store.steampowered.com/app/1920960/VPet/ | 产品介绍、下载、用户评价 | [01_web_homepage.png](screenshots/01_web_homepage.png) |
| 2 | GitHub 仓库首页(网页) | https://github.com/LorisYounger/VPet | 项目源码、README、文档 | [02_web_github.png](screenshots/02_web_github.png) |
| 3 | GitHub README 介绍区(网页) | GitHub 仓库首页 | 产品介绍、获取方式 | [03_web_github_readme.png](screenshots/03_web_github_readme.png) |
| 4 | GitHub README 动画展示(网页) | GitHub 仓库首页 | 动画系统说明(32×4×3) | [04_web_github_readme2.png](screenshots/04_web_github_readme2.png) |
| 5 | GitHub README 功能说明(网页) | GitHub 仓库首页 | 免费/开源/创意工坊说明 | [05_web_github_features.png](screenshots/05_web_github_features.png) |
| 6 | indienova 游戏页(网页) | https://indienova.com/g/VPet-Simulator | 产品展示、分类、简介 | [06_web_indienova.png](screenshots/06_web_indienova.png) |
| 7 | indienova 详细介绍(网页) | indienova 游戏页 | 详细介绍、功能列表 | [07_web_indienova_detail.png](screenshots/07_web_indienova_detail.png) |
| 8 | indienova 功能说明(网页) | indienova 游戏页 | 免费/开源/创意工坊详情 | [08_web_indienova_more.png](screenshots/08_web_indienova_more.png) |
| 9 | indienova 动画展示(网页) | indienova 游戏页 | 摸头/提起动画 GIF | [09_web_indienova_screenshots.png](screenshots/09_web_indienova_screenshots.png) |
| 10 | indienova 爬墙展示(网页) | indienova 游戏页 | 屏幕边缘爬行动画 | [10_web_indienova_features.png](screenshots/10_web_indienova_features.png) |
| 11 | 萌娘百科条目(网页) | https://zh.moegirl.org.cn/虚拟桌宠模拟器 | 百科介绍、评价、截图 | [11_web_moegirl.png](screenshots/11_web_moegirl.png) |
| 12 | Linux 移植版 404(网页) | https://github.com/shishuiqiaotou/VPet_For_Linux | 社区移植版不存在 | [12_web_linux_port.png](screenshots/12_web_linux_port.png) |

### 1.3 各界面功能与评价

#### 1.3.1 宠物主窗体

- **功能**:无边框悬浮窗,宠物角色始终显示在桌面顶层。核心显示逻辑包含动画状态机、眼动追踪(EyeTracking)、场景切换。支持 PNG 动态动画和静态图片两种显示模式,食物动画支持前中后 3 层夹心效果。
- **交互**:启动后自动出现在桌面右下角或边缘;长按头部可拖拽到屏幕任意位置;单击头部/身体触发摸头/触摸反应。
- **评价**:无边框设计让桌宠融入桌面环境而不突兀;悬浮置顶保证宠物始终在视野内;拖拽手感通过"提起→移动→松手下落"的动画链条提供了物理感,截图 [09_web_indienova_screenshots.png](screenshots/09_web_indienova_screenshots.png) 展示了被提起时角色的倒置姿态和落地动画。不足:始终置顶可能在全屏应用时造成干扰(虽然应有相应的隐藏机制)。
- **截图**:[09_web_indienova_screenshots.png](screenshots/09_web_indienova_screenshots.png)

#### 1.3.2 交互工具栏(ToolBar)

- **功能**:左键点击宠物本体后弹出的快捷菜单,包含喂食、睡觉、学习、玩耍、工作、设置等功能入口,同时显示饱食度、心情、健康、等级等关键数值状态条。
- **交互**:点击宠物 → 弹出工具栏 → 选择具体活动;工具栏通常在鼠标移开后自动消失。
- **评价**:将高频操作集中在宠物本体附近,符合"就近操作"的交互原则;状态条实时显示让养成进度一目了然。但工具栏在密集操作时可能遮挡桌面内容。
- **截图**:[03_web_github_readme.png](screenshots/03_web_github_readme.png) 顶部横幅隐约可见工具栏图标

#### 1.3.3 商店界面(winBetterBuy / "更好买")

- **功能**:游戏内货币商店,商品分为正餐、零食、饮料、药品、礼品、收藏品、功能性商品七大类。点击商品右上角星标可收藏,点击右侧详情按钮可查看商品属性(价格、效果)。
- **交互**:通过工具栏进入商店 → 浏览/搜索商品 → 购买 → 自动扣除货币并生效。
- **评价**:分类清晰,收藏功能便于复购常用商品。但"更好买"这个窗口名称偏向口语化,与整体产品调性一致但不够直观。

#### 1.3.4 对话气泡(MessageBar)

- **功能**:宠物说话或反馈时弹出的文本气泡框,支持简体中文、繁体中文、英文、日文多语言显示。玩家可选择随机刷新的对话发送,宠物会回应并随机增减数值。
- **交互**:宠物主动触发或玩家通过工具栏发起对话 → 气泡弹出 → 玩家选择回复选项。
- **评价**:对话系统增加了宠物的"生命感",随机数值变化让每次对话都有轻微的不确定性。但随机刷新的对话选项可能不够贴合当前情境。

#### 1.3.5 设置面板

- **功能**:多个设置窗口分管不同维度 — winSetting(软件设置与 Mod 管理)、winGameSetting(游戏数值设置)、winCGPTSetting(ChatGPT API 配置)、winConsole(开发者控制台/ActivityLog 行为日志)。
- **交互**:右键宠物 → System → Settings 进入;或各子面板独立入口。
- **评价**:设置分散在多个窗口中,功能划分虽然清晰但增加了用户的认知负担。ChatGPT 配置面板的存在说明产品紧跟 AI 趋势,但这也意味着需要额外的 API 密钥配置门槛。

#### 1.3.6 创意工坊

- **功能**:Steam 创意工坊支持,可下载/分享玩家自制内容:桌宠动画、物品/食物/饮料、桌宠工作类型、对话文本、主题、代码插件(如接入 L2D/Spine 动画、闹钟、记事板等)。
- **交互**:Steam 客户端内订阅创意工坊内容 → 自动下载到游戏目录。
- **评价**:创意工坊是 VPet 生态的核心,将产品的可扩展性从"官方更新"扩展到"社区共创"。代码插件的支持(几乎无所不能)让高级用户可以深度定制,但这也意味着需要一定的编程能力。
- **截图**:[05_web_github_features.png](screenshots/05_web_github_features.png)

---

## 2. UI/UX 风格和质量描述

### 2.1 视觉风格

VPet 采用**二次元萌系插画风格**,默认角色"萝莉丝"为银发金瞳的 Q 版少女形象。配色以柔和的浅色系为主(白色、淡粉、浅灰),与 Windows 桌面环境形成对比但不刺眼。宠物本身使用 PNG 序列帧动画,边缘透明,可无缝叠加在任何桌面壁纸上。整体调性偏向**休闲玩具感**而非生产力工具,与"桌面宠物"的定位高度一致。

截图 [09_web_indienova_screenshots.png](screenshots/09_web_indienova_screenshots.png) 和 [10_web_indienova_features.png](screenshots/10_web_indienova_features.png) 展示了角色在代码编辑器背景上的叠加效果,证明透明通道处理良好。

### 2.2 信息密度与层级

**主界面(宠物本体)**信息密度极低 — 只有角色本身,没有任何按钮或文字覆盖,符合"宠物不应打扰用户"的设计哲学。信息在需要时才显现:点击后出现工具栏、对话时弹出气泡。

**工具栏**信息密度适中,状态条 + 功能图标排列紧凑但可读。商店界面采用网格卡片布局,每个商品有图片、名称、价格、星标收藏,信息层级清晰。

### 2.3 交互流畅度

从网页端采集的信息无法直接评估运行时性能,但根据 GitHub 仓库的架构文档:
- 动画系统使用 GraphCore 作为动画显示核心,PNGAnimation 组件处理动态序列帧
- 存在"节能/流畅"两种模式切换,说明开发者考虑过性能问题
- 音频可视化功能(宠物随音乐律动)需要实时音频处理,对性能有一定要求

潜在的性能风险:32(种)×4(状态)×3(类型)的大量动画资源可能占用较多内存;始终置顶的悬浮窗在老旧机器上可能造成渲染开销。

### 2.4 文案质量

官网/文档文案以中文为主,风格轻松活泼:
- "反正免费为啥不试试呢" — 带有网络流行语色彩,拉近与年轻用户的距离
- "更好买" — 商店窗口名称,口语化但不够正式
- 英文 README 存在但主要由社区维护,部分文档仅有中文版

整体文案风格统一,没有明显的机翻味,但专业术语(如 WPF、NuGet)与萌系文案("萝莉丝"、"摸头")混搭,形成了独特的"技术宅+二次元"调性。

### 2.5 可访问性观察

- **对比度**:宠物角色使用浅色系,在深色壁纸上对比度充足,但在浅色壁纸上可能不够明显
- **键盘可达性**:作为鼠标驱动的桌面宠物,键盘操作支持有限
- **字号可调**:设置面板中应有相关选项(文档提及"调整宠物大小、透明度")
- **深色模式**:无明确证据支持系统级深色模式适配

---

## 3. 官网描述

### 3.1 关键文案摘录

> "虚拟桌宠模拟器 一个开源的桌宠软件,可以内置到任何WPF应用程序" — GitHub 仓库 About 栏,来源:[02_web_github.png](screenshots/02_web_github.png)

> "虚拟桌宠模拟器是一款桌宠软件,支持各种互动投喂等,开源免费并且支持创意工坊" — indienova 简介,来源:[07_web_indienova_detail.png](screenshots/07_web_indienova_detail.png)

> "多达 32(种) * 4(状态) * 3(类型) 种动画,注:部分种类没有生病状态或循环等内容,实际动画数量会偏少" — GitHub README,来源:[04_web_github_readme2.png](screenshots/04_web_github_readme2.png)

> "该游戏完全免费!反正不要钱,试试不要紧" — GitHub README,来源:[05_web_github_features.png](screenshots/05_web_github_features.png)

> "该游戏支持创意工坊,您可以制作别的人物桌宠动画或者互动,并上传至创意工坊分享给更多人使用" — GitHub README,来源:[05_web_github_features.png](screenshots/05_web_github_features.png)

### 3.2 核心卖点(官网视角)

1. **开源免费**(Apache 2.0 协议) — 允许修改代码制作专属桌宠,同时 Steam 免费分发
2. **海量动画系统** — 32×4×3 维度的动画资源,覆盖多种互动场景
3. **Steam 创意工坊支持** — 社区共创生态,支持动画、物品、对话、主题、代码插件
4. **可嵌入任何 WPF 应用** — 作为库组件(NuGet 包)使用,不仅限于独立运行
5. **多种互动方式** — 摸头、提起、爬墙、投喂、对话、音频可视化等

### 3.3 与实际体验的差距

| 卖点 | 官网原文 | 实际体验(基于网页信息) | 差距 |
|---|---|---|---|
| 平台支持 | Steam 商店展示 | 仅 Windows 原生支持;Linux 移植版 404 | 官网未明确说明仅限 Windows,Linux 用户会失望 |
| 动画数量 | "32×4×3 种动画" | README 注明"部分种类没有生病状态或循环等内容,实际动画数量会偏少" | 宣传数字与实际有差距,但开发者主动做了免责声明 |
| 完全免费 | "完全免费" | Steam 免费 + 开源 | 一致,无内购/付费 DLC |

---

## 4. 定价

VPet 采用**完全免费**策略:
- Steam 商店免费下载
- GitHub 源码开源(Apache 2.0)
- NuGet 包免费使用
- 无内购、无订阅、无广告

商业模式:作为"虚拟主播模拟器"的宣传项目,主产品免费以扩大用户基数和社区生态,间接带动关联产品的关注度。

---

## 5. 目标用户

基于官网用语和实际功能推断:

1. **二次元文化爱好者** — 萌系角色、日语配音支持、创意工坊的二次元内容生态
2. **桌面个性化追求者** — 想要在单调的桌面环境中增加趣味元素
3. **开发者/技术爱好者** — 开源代码、WPF 组件化设计、可编写代码插件
4. **轻度陪伴需求用户** — 需要"有人在旁边"的感觉,但不希望强干扰
5. **虚拟主播/直播主** — 产品源自"虚拟主播模拟器",对直播场景有原生支持

---

## 6. 与同类产品对比

| 产品 | 差异点 |
|---|---|
| **Bongo Cat** (桌面宠物) | Bongo Cat 功能单一(仅键盘映射动画),无养成系统;VPet 有完整的数值养成、商店、对话系统 |
| **Desktop Goose** (桌面大鹅) | Goose 主打"捣乱"体验(拖走鼠标、留下脚印),属于干扰型;VPet 偏向"陪伴"体验,可通过专注模式减少干扰 |
| **Live2DViewerEX** | Live2DViewerEX 是通用 Live2D 展示工具,VPet 是专用桌宠框架,自带养成玩法;VPet 支持通过插件接入 L2D/Spine |

---

## 7. 优劣势小结

| 维度 | 优势 | 劣势 |
|---|---|---|
| 产品逻辑 | 开源免费降低使用门槛;创意工坊形成内容生态;可嵌入 WPF 应用扩展使用场景 | 仅限 Windows 平台;作为宣传项目,核心功能更新可能受主产品节奏影响 |
| UI/UX | 无边框悬浮设计融入桌面;物理互动(提起/下落)有真实感;信息按需显现不打扰 | 设置分散在多窗口;始终置顶可能干扰全屏应用;浅色角色在浅色壁纸上可见性差 |
| 工程质量 | Apache 2.0 开源,6.2k+ stars,600+ forks,社区活跃;模块化架构(Core/Windows/Interface 分层清晰) | WPF 技术栈限制 Windows 独占;大量 PNG 动画序列帧可能占用较多内存和磁盘 |

---

## 附录 A 截图索引

| # | 文件 | 说明 |
|---|---|---|
| 01 | screenshots/01_web_homepage.png | Steam 商店访问失败(TLS 错误),降级原因证据 |
| 02 | screenshots/02_web_github.png | GitHub 仓库首页(6.2k stars, Apache 2.0) |
| 03 | screenshots/03_web_github_readme.png | GitHub README 产品介绍与获取方式 |
| 04 | screenshots/04_web_github_readme2.png | GitHub README 动画系统(32×4×3)说明 |
| 05 | screenshots/05_web_github_features.png | GitHub README 免费/开源/创意工坊功能 |
| 06 | screenshots/06_web_indienova.png | indienova 游戏页首页(分类:放置挂机,平台:Windows) |
| 07 | screenshots/07_web_indienova_detail.png | indienova 详细介绍与功能列表 |
| 08 | screenshots/08_web_indienova_more.png | indienova 免费/开源/创意工坊详情 |
| 09 | screenshots/09_web_indienova_screenshots.png | indienova 动画展示(摸头/提起 GIF) |
| 10 | screenshots/10_web_indienova_features.png | indienova 爬墙动画展示 |
| 11 | screenshots/11_web_moegirl.png | 萌娘百科条目(Steam 5.2万评论,褒贬不一) |
| 12 | screenshots/12_web_linux_port.png | Linux 移植版 GitHub 仓库 404,不可用证据 |
