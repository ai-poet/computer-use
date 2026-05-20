# Shimeji-ee 产品分析报告

| 项目 | 值 |
|---|---|
| 官网 | https://kilkakon.com/shimeji/ |
| 下载链接 | https://kilkakon.com/shimeji/shimejiee.zip |
| 报告日期 | 2026-05-20 |
| 主机 | darwin / arm64 |
| Runtime | sandbox-local |
| 模式 | web-only |
| 用时 | ~20 分钟 |

> 本次为网页版分析，未驱动桌面端 — 产品官网明确声明 "runs only on Windows"，当前沙盒为 Linux 环境，无法运行 Windows 应用；且官网嵌入了 Google AdSense 广告脚本，导致 Firefox 在沙盒中反复崩溃，无法通过浏览器继续深入体验。

---

## 1. 详细的产品逻辑介绍

### 1.1 总定位

Shimeji-ee 是一款开源的 Windows 桌面宠物软件，基于 Java 运行。用户在桌面上放置一个或多个卡通角色（称为 "shimeji"），这些角色会在屏幕边缘爬行、跳跃、与窗口互动，为桌面增添趣味性。产品面向喜欢桌面装饰和二次元文化的 Windows 用户，核心卖点是"可高度自定义的角色系统"和"角色之间的互动机制"。

### 1.2 界面清单

按出现顺序列出实际看到的所有主要界面，每个一行，挂截图编号：

| # | 界面 | 入口 | 主要功能 | 截图 |
|---|---|---|---|---|
| 1 | 首页(网页) | https://kilkakon.com/shimeji/ | 产品介绍、下载入口、角色资源链接 | [01_web_homepage.png](screenshots/01_web_homepage.png) |

### 1.3 各界面功能与评价

#### 1.3.1 官网首页

- **功能**：首页以大标题 "Shimeji-ee Desktop Pet" 开场，配以角色动态演示图（多个 shimeji 围绕 Notepad 窗口活动）。正文介绍产品核心概念："Shimeji are little desktop companions that run around your computer screen, be it mischief or cuteness depending on the shimeji you use!" 提供四个主要行动按钮："Download Now"（下载 shimejiee.zip）、"New Characters"（跳转到角色资源页）、"Video"（YouTube 介绍视频）、"FAQ Video"（YouTube 常见问题视频）、"Affordances Tutorial"（交互配置教程）、"Source Code"（下载源码 shimejieesrc.zip）。底部导航包含 Games、Software、Downloads、YouTube、Patreon、Email、Discord 等站点链接。
- **交互**：用户通过点击按钮完成下载或跳转到相关页面。首页无登录墙，所有资源直接可访问。
- **评价**：信息传达直接明了，首页首屏即给出产品定义、下载入口和角色资源链接，没有多余内容。但设计较为朴素，属于个人开发者网站的典型风格。Google AdSense 广告嵌入在页面底部，实际体验中该广告脚本在沙盒 Firefox 中导致浏览器反复崩溃，对用户体验有明显负面影响。
- **截图**:[01_web_homepage.png](screenshots/01_web_homepage.png)

---

## 2. UI/UX 风格和质量描述

### 2.1 视觉风格

官网采用极简的个人网站风格：白底、红色标题字、蓝色按钮，无复杂配色系统。角色插画为简单的黑白线条风格（截图中可见多个圆润的小人形象），与功能演示图（Notepad 窗口截图）结合，直观传达了"桌面宠物在窗口上活动"的产品概念。整体调性偏向独立开发者的实用主义，而非商业化产品的精致感。

### 2.2 信息密度与层级

首页信息密度适中：首屏包含产品标题、一句话描述、动态演示图、行动按钮组。主要 CTA（Download Now）使用蓝色填充按钮，在白色背景上对比度足够，位于首屏正中偏下位置，易于发现。次要功能（Video、FAQ、Tutorial、Source Code）以同等大小的按钮横向排列，没有明显的视觉层级区分，可能导致用户注意力分散。

### 2.3 交互流畅度

- 页面加载：从 curl 获取的 HTML 看，页面结构简单，无复杂前端框架，理论加载速度应较快。
- 浏览器兼容性：Google AdSense 脚本（pagead2.googlesyndication.com）在沙盒 Firefox 中导致 tab 反复崩溃，说明页面存在兼容性风险。这与 SKILL.md 中提到的"失败处理"场景一致。
- 无动态交互元素（如轮播图、弹窗），页面为静态 HTML。

### 2.4 文案质量

官网文案简洁直接，无营销腔调。核心描述 "Shimeji are little desktop companions that run around your computer screen" 一句话说清了产品是什么。技术要求 "Shimeji requires Java and runs only on Windows" 明确标注了系统依赖和平台限制，避免了用户下载后的期望落差。整体文案由开发者个人撰写，语气友好但专业度一般。

### 2.5 可访问性观察

- 对比度：红色标题在白色背景上对比度足够；蓝色按钮文字可读。
- 页面包含 viewport meta 标签（width=device-width, initial-scale=1.0），声称支持移动端，但从内容布局看未针对小屏优化。
- 无明显的 ARIA 标签或语义化 HTML5 结构（使用 div 为主）。

---

## 3. 官网描述

### 3.1 关键文案摘录

> "Shimeji are little desktop companions that run around your computer screen, be it mischief or cuteness depending on the shimeji you use! Pick from the best characters drawn by artists all over the world. Shimeji requires Java and runs only on Windows."
> — 来源：首页正文

> "Shimeji-ee is an open source project. This website hosts my personal improvements to the software."
> — 来源：首页正文

### 3.2 核心卖点（官网视角）

1. **桌面宠物体验**：在屏幕上放置可爱/调皮的角色，与窗口互动（原文锚：首页描述）。
2. **丰富的角色生态**：可从 Cachomon.com、deviantArt、pixiv 等社区获取成百上千个角色（原文锚：characters.php 页面）。
3. **开源可定制**：提供源码下载，支持通过 XML 配置自定义角色行为和交互（原文锚：affordances.php 教程）。

### 3.3 与实际体验的差距

| 卖点 | 官网原文 | 实际体验 | 差距 |
|---|---|---|---|
| 平台支持 | "runs only on Windows" | 沙盒为 Linux，无法运行 | 无差距，官网已诚实声明限制 |
| 广告体验 | 无声明 | Google AdSense 导致浏览器崩溃 | 未声明广告对兼容性的影响 |

---

## 4. 定价

产品完全免费（开源，BSD License）。开发者通过 Patreon（https://www.patreon.com/Kilkakon）接受捐赠，Patreon 上提供示例角色下载等额外内容。

---

## 5. 目标用户

基于官网信息推断：
- **Windows 桌面美化爱好者**：产品核心是桌面装饰，面向喜欢在桌面上添加趣味元素的用户。
- **二次元/动漫文化受众**：角色风格偏向日式卡通，且官网推荐在 deviantArt、pixiv 等平台搜索角色资源。
- **Java 技术用户**：产品需要 Java 环境运行，对非技术用户有一定门槛。

---

## 6. 与同类产品对比

| 对比维度 | Shimeji-ee | 同类产品（如 Desktop Goose） |
|---|---|---|
| 平台 | Windows only | 通常跨平台（如 Desktop Goose 有 Windows/Mac） |
| 角色系统 | 丰富的社区角色生态（第三方支持） | 预设角色为主 |
| 自定义能力 | 可通过 XML 深度定制行为和交互 | 通常有限 |
| 开源 | 是（BSD License） | 通常闭源 |
| 技术栈 | Java | 各异（Desktop Goose 为 C#） |

---

## 7. 优劣势小结

| 维度 | 优势 | 劣势 |
|---|---|---|
| 产品逻辑 | 开源免费；丰富的角色生态；支持角色间交互 | 仅支持 Windows；依赖 Java 运行时 |
| UI/UX | 角色设计可爱；交互机制有趣（Affordances） | 官网设计朴素；广告脚本导致浏览器崩溃 |
| 工程质量 | 有详细文档教程；源码可下载 | 基于废弃项目二次开发；无现代安装包（仅 zip） |

---

## 附录 A 截图索引

| # | 文件 | 说明 |
|---|---|---|
| 01 | screenshots/01_web_homepage.png | 官网首页，含产品标题、角色演示图、下载按钮和导航 |

> 编号规则：`NN_<source>_<view>.png`，`source ∈ {web, app, android}`，`view` 短 kebab-case；`NN` 单调递增，允许跳号。本次分析为 web-only 模式，仅采集网页截图。