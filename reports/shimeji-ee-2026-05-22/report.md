# Shimeji-ee 产品分析报告

| 项目 | 值 |
|---|---|
| 官网 | https://kilkakon.com/shimeji/ |
| 下载链接 | https://kilkakon.com/shimeji/shimejiee.zip |
| 报告日期 | 2026-05-22 |
| 主机 | linux / x86_64 |
| Runtime | sandbox-local |
| 模式 | web-only |
| 用时 | ~15 分钟 |

> 本次为网页版分析，未驱动桌面端 — 官网明确声明 "Shimeji requires Java and runs only on Windows"，当前沙盒为 Linux，无对应平台安装包。

---

## 1. 详细的产品逻辑介绍

### 1.1 总定位

Shimeji-ee 是一款 Windows 平台的桌面宠物软件，由 Kilkakon 基于已废弃的 Shimeji-ee group 项目二次开发（原作者为 Group Finity 的 Yuki Yamada）。产品核心是在用户电脑屏幕上放置一个或多个卡通角色（Shimeji），它们会自主在屏幕边缘爬行、攀爬窗口、做出各种动画动作，为用户提供桌面陪伴和趣味互动。角色资源来自全球艺术家的创作，用户可以从 Cachomon.com、deviantArt、pixiv 等平台下载额外角色。产品需要 Java 运行时环境，仅支持 Windows 系统。

### 1.2 界面清单

按出现顺序列出实际浏览到的所有页面：

| # | 界面 | 入口 | 主要功能 | 截图 |
|---|---|---|---|---|
| 1 | 官网首页 | https://kilkakon.com/shimeji/ | 产品介绍、下载入口、演示图 | [01_web_homepage.png](screenshots/01_web_homepage.png) |
| 2 | 首页版权区 | 首页滚动后 | BSD 风格许可证声明 | [02_web_homepage_after_close.png](screenshots/02_web_homepage_after_close.png) |
| 3 | 首页底部 | 首页继续滚动 | 免责声明、站点导航 | [03_web_homepage_footer.png](screenshots/03_web_homepage_footer.png) |
| 4 | 角色获取页 | https://kilkakon.com/shimeji/characters.php | 推荐角色来源、搜索建议 | [06_web_characters.png](screenshots/06_web_characters.png) |
| 5 | 角色搜索页 | characters.php 滚动后 | deviantArt/pixiv 搜索入口 | [07_web_characters_scroll.png](screenshots/07_web_characters_scroll.png) |
| 6 | 交互教程页 | https://kilkakon.com/shimeji/affordances.php | 高级交互动画制作指南 | [08_web_affordances.png](screenshots/08_web_affordances.png) |
| 7 | Software 分类页 | https://kilkakon.com/software.php | 产品分类展示、简介 | [10_web_software.png](screenshots/10_web_software.png) |
| 8 | 主站下载页 | https://kilkakon.com/downloads.php | 开发者全部作品下载 | [09_web_downloads_main.png](screenshots/09_web_downloads_main.png) |
| 9 | Games 分类页 | https://kilkakon.com/games.php | 开发者游戏作品展示 | [11_web_games.png](screenshots/11_web_games.png) |

### 1.3 各界面功能与评价

#### 1.3.1 官网首页

- **功能**：首页以大幅演示图展示 Shimeji 在 Notepad 窗口上爬行的效果，配合标题 "Shimeji-ee Desktop Pet" 和一句话产品介绍。页面中部提供 "Download Now" 和 "New Characters" 两个主 CTA 按钮，底部有视频、FAQ 视频、教程、源代码等次级入口。
- **交互**：用户通过滚动查看完整页面内容，点击按钮进入对应子页面。底部导航栏链接到 Kilkakon 主站的其他分类（Games、Software、Downloads）。
- **评价**：首页信息传达直接，一张演示图胜过千言万语。但 "Download Now" 按钮在沙盒 Firefox 中点击无反应（可能是纯 HTML 链接 `shimejiee.zip`，浏览器尝试直接下载但未触发下载弹窗）。页面缺少版本号、更新日期、系统要求明细等关键信息，仅在描述文字中提及 "requires Java and runs only on Windows"。
- **截图**:[01_web_homepage.png](screenshots/01_web_homepage.png)

#### 1.3.2 首页版权区

- **功能**：展示软件的版权归属和许可证条款。说明本项目基于 Shimeji-ee group 的废弃项目，原作者 Yuki Yamada 来自 Group Finity。因原项目未提供 BSD 许可证的具体条款，Kilkakon 自行拟定了一份类似 BSD 的许可证。
- **交互**：纯文本展示，无交互元素。
- **评价**：许可证声明较为冗长，占据了首页近半的纵向空间，对于只想快速下载体验的用户来说信息量过大。但开源项目明确许可证是必要之举，体现了开发者的合规意识。
- **截图**:[02_web_homepage_after_close.png](screenshots/02_web_homepage_after_close.png)

#### 1.3.3 角色获取页

- **功能**：指导用户去哪里寻找 Shimeji 角色资源。推荐了两个主要来源：Cachomon.com（官方合作站点，提供数百个流行文化角色）和 Shimeji Desktop Pets deviantArt Group。
- **交互**："Visit Site" 按钮可跳转到 Cachomon.com。
- **评价**：页面结构清晰，但内容较为单薄，仅有文字推荐而无角色预览图或热门角色排行。对于新用户来说，知道"去哪里找"但不知道"找什么"，缺少引导性内容。
- **截图**:[06_web_characters.png](screenshots/06_web_characters.png)

#### 1.3.4 角色搜索建议区

- **功能**：提示用户可以在 deviantArt 和 pixiv 上搜索 "shimeji" 标签发现新角色，并提醒 "shimeji" 是日本蘑菇的一种，搜索结果中可能出现无关的蘑菇图片。
- **交互**：提供 deviantArt 和 pixiv 两个快捷搜索按钮。
- **评价**：这个"蘑菇提示"增加了页面的趣味性，体现了开发者的人文关怀。但快捷按钮的可用性取决于外部站点的稳定性。
- **截图**:[07_web_characters_scroll.png](screenshots/07_web_characters_scroll.png)

#### 1.3.5 交互教程页

- **功能**：面向高级用户的 Affordances（交互 affordance 系统）教程，讲解如何让两个 Shimeji 角色之间产生交互动画。教程假设用户已了解 XML 文件编辑和帧动画添加的基础知识。
- **交互**：纯文本教程，包含步骤说明和概念解释（Broadcast、ScanMove、Interact）。提供 Patreon 上的工作示例下载链接。
- **评价**：教程内容专业，但门槛较高，要求用户具备 XML 编辑经验。对于普通用户来说，这部分内容几乎无法触及。将高级示例放在 Patreon 上（"a working example for free from my Patreon"）是一种社区支持模式，但"free"和"Patreon"的组合表述略显矛盾。
- **截图**:[08_web_affordances.png](screenshots/08_web_affordances.png)

#### 1.3.6 Software 分类页

- **功能**：Kilkakon 主站的 Software 分类入口页，Shimeji Desktop Pet 作为该分类下的唯一产品展示。
- **交互**："Download Now" 和 "Read More" 按钮链接到 Shimeji-ee 子站点。
- **评价**：Software 分类目前仅有一个产品，页面显得空旷。"Read More" 按钮实际链接到 Shimeji-ee 子站首页，功能与 "Download Now" 有一定重叠。
- **截图**:[10_web_software.png](screenshots/10_web_software.png)

---

## 2. UI/UX 风格和质量描述

### 2.1 视觉风格

官网采用极简的白色背景 + 红色标题 + 蓝色按钮的配色方案，整体风格偏向 2000 年代中后期的个人开发者网站。标题使用红色无衬线粗体，正文为灰色小字，按钮为蓝色矩形带白色文字。产品演示图是 Notepad 窗口上几个简笔画风格小人的截图，与网站的朴素风格一致。整体调性偏向"开源工具感"而非"商业产品感"。

### 2.2 信息密度与层级

首页信息密度适中：首屏以大幅演示图和产品描述为主，CTA 按钮位于描述下方，一眼可及。但版权和许可证声明占据了首页约 40% 的纵向空间，对首屏信息有稀释作用。次级入口（Video、FAQ、Tutorial、Source Code）以等宽的蓝色按钮横排展示，视觉权重与主 CTA 几乎相同，导致层级区分不够明显。

### 2.3 交互流畅度

- 页面加载速度较快，无明显的加载动画或骨架屏。
- 按钮无 hover/press 状态反馈（颜色不变），点击后无过渡动画。
- "Download Now" 按钮在沙盒环境中点击无反应，无法确认是环境问题还是按钮实现问题（从 HTML 源码看是普通的 `<a>` 链接指向 `shimejiee.zip`）。
- 页面无响应式设计，在 1024×768 分辨率下右侧有大量空白。

### 2.4 文案质量

官网文案风格口语化、友好。例如 "Shimeji are little desktop companions that run around your computer screen, be it mischief or cuteness depending on the shimeji you use!" 这句话既传达了产品功能又带有情感温度。但 "shimeji are a type of Japanese mushroom so you might have a few mushroomy results crop up" 这类文案虽然有趣，却对非英语母语用户可能造成理解障碍。全文无中文支持。

### 2.5 可访问性观察

- 蓝色按钮（#428bca）与白色背景的对比度约 3.5:1，低于 WCAG AA 标准（4.5:1），对视力较弱用户不够友好。
- 按钮文字较小（约 14px），无加粗处理。
- 页面无深色模式支持。
- 无明显的键盘导航焦点样式。

---

## 3. 官网描述

### 3.1 关键文案摘录

> "Shimeji are little desktop companions that run around your computer screen, be it mischief or cuteness depending on the shimeji you use! Pick from the best characters drawn by artists all over the world. Shimeji requires Java and runs only on Windows."
> — 来源：首页首屏描述

> "This version of Shimeji-ee is based off a seemingly abandoned project by the Shimeji-ee group, based off work by Yuki Yamada of Group Finity (link no longer working)."
> — 来源：首页版权区

> "Interactive actions have the following components: 1. A shimeji Broadcasts an affordance 2. Other shimeji detect this affordance and move towards it (ScanMove) 3. Once the shimeji meet, they Interact."
> — 来源：Affordances Tutorial 页

### 3.2 核心卖点（官网视角）

1. **免费桌面宠物**：开源免费，可自定义角色（原文锚：首页 "Download Now" 按钮 + 许可证声明）
2. **丰富的角色生态**：全球艺术家创作，可从 Cachomon.com、deviantArt、pixiv 获取（原文锚：characters.php）
3. **高度可定制**：支持 XML 编辑和交互动画制作（原文锚：affordances.php）

### 3.3 与实际体验的差距

由于本次为 web-only 分析，未实际运行桌面端，以下为官网声明与可验证事实的对比：

| 卖点 | 官网原文 | 可验证事实 | 差距 |
|---|---|---|---|
| 平台支持 | "runs only on Windows" | 官网仅提供 shimejiee.zip，无 Linux/macOS 安装包 | 与声明一致，Windows 独占 |
| Java 依赖 | "requires Java" | 未在沙盒内验证实际运行效果 | 无法验证 |
| 角色生态 | "hundreds of Shimeji characters" | Cachomon.com 为外部站点，未验证实际数量 | 无法验证 |

---

## 4. 目标用户

基于官网用语和实际功能推断：

1. **Windows 桌面个性化爱好者**：追求桌面趣味性和个性化的用户，愿意安装 Java 环境来运行桌面宠物。
2. **二次元/同人文化参与者**：产品角色资源主要来自同人创作社区（deviantArt、pixiv），天然吸引动漫、游戏同人圈用户。
3. **有技术能力的定制者**：affordances 教程和 XML 编辑门槛表明，产品也面向愿意深入定制角色行为的高级用户。

---

## 5. 与同类产品对比

| 维度 | Shimeji-ee | 同类产品（如 Desktop Goose） |
|---|---|---|
| 平台 | Windows only（需 Java） | 通常有 Windows/macOS 多平台支持 |
| 角色来源 | 社区创作（deviantArt/pixiv/Cachomon） | 官方提供或有限定制 |
| 交互深度 | 支持 XML 自定义交互动画 | 通常为预设行为，不可深度定制 |
| 活跃维护 | Kilkakon 持续更新（基于废弃项目二次开发） | 因产品而异 |
| 付费模式 | 完全免费（开源） | 有免费也有付费 |

---

## 6. 优劣势小结

| 维度 | 优势 | 劣势 |
|---|---|---|
| 产品逻辑 | 开源免费，角色生态丰富，支持深度定制 | Windows 独占，依赖 Java，安装门槛较高 |
| UI/UX | 演示图直观传达产品价值 | 官网设计陈旧，无响应式，按钮无交互反馈 |
| 工程质量 | 基于成熟项目二次开发，许可证清晰 | 原项目已废弃，长期维护存疑；无跨平台计划 |

---

## 附录 A 截图索引

| # | 文件 | 说明 |
|---|---|---|
| 01 | screenshots/01_web_homepage.png | 官网首页全景，展示产品主图和描述 |
| 02 | screenshots/02_web_homepage_after_close.png | 首页版权和许可证声明区 |
| 03 | screenshots/03_web_homepage_footer.png | 首页底部免责声明和站点导航 |
| 04 | screenshots/04_web_downloads.png | 404 错误页（证明 /shimeji/downloads/ 不存在） |
| 06 | screenshots/06_web_characters.png | 角色获取推荐页面 |
| 07 | screenshots/07_web_characters_scroll.png | 角色搜索建议（deviantArt/pixiv） |
| 08 | screenshots/08_web_affordances.png | 高级交互动画制作教程 |
| 09 | screenshots/09_web_downloads_main.png | Kilkakon 主站下载页 |
| 10 | screenshots/10_web_software.png | Software 分类页 |
| 11 | screenshots/11_web_games.png | Games 分类页 |

> 编号规则：`NN_<source>_<view>.png`，`source ∈ {web, app, android}`，`view` 短 kebab-case；`NN` 单调递增，允许跳号。本次为 web-only 模式，所有截图均为 `web` 来源。