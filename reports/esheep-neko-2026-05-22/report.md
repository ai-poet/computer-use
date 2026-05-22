# eSheep / Neko 产品分析报告

| 项目 | 值 |
|---|---|
| 官网 | https://esheep.petrucci.ch/ |
| 下载链接 | — |
| 报告日期 | 2026-05-22 |
| 主机 | linux / x86_64 |
| Runtime | sandbox-local |
| 模式 | web-only |
| 用时 | ~15 分钟 |

> 本次为网页版分析，未驱动桌面端 — 产品仅有 Windows 版安装包（.exe 与 UWP），当前 Linux 沙盒无法安装运行。

---

## 1. 详细的产品逻辑介绍

### 1.1 总定位

eSheep 64-bit 是一款复刻 1995 年经典 Windows 桌面宠物「Stray Sheep」的开源桌面应用。由 Adriano Petrucci 开发，用 C# 重写为 64 位版本，让经典绵羊宠物重新出现在现代 Windows 桌面上。产品核心是一个在屏幕边缘行走、攀爬、掉落、互动的动画绵羊（以及扩展的 NEKO 等宠物），以像素风格动画为桌面增添趣味。

原始作品源自日本动画师 Tatsuhiko Numura 1994 年的「Stray Sheep」系列动画（富士电视台午夜档播出），后衍生出图书、PlayStation 游戏等周边。

### 1.2 界面清单

按出现顺序列出实际看到的所有主要界面，每个一行，挂截图编号：

| # | 界面 | 入口 | 主要功能 | 截图 |
|---|---|---|---|---|
| 1 | 官网首页 | https://esheep.petrucci.ch/ | 展示产品信息、Blog、下载入口、在线编辑器入口 | [01_web_homepage.png](screenshots/01_web_homepage.png) |
| 2 | 下载页面 | 首页 → Download | Windows 安装包下载、Microsoft Store 链接 | [02_web_download.png](screenshots/02_web_download.png) |
| 3 | 帮助页面 | 底部 Help 图标 | 使用帮助文档 | [03_web_help.png](screenshots/03_web_help.png) |
| 4 | 信息页面 | 底部 Info 图标 | 产品背景、版权信息、原作介绍 | [04_web_info.png](screenshots/04_web_info.png) |
| 5 | 致谢页面 | 底部 Credits 图标 | 感谢原作团队 | [05_web_credits.png](screenshots/05_web_credits.png) |
| 6 | 在线编辑器 | 首页 → Editor | 创建自定义宠物动画 | [06_web_editor.png](screenshots/06_web_editor.png) |
| 7 | 视频页面 | 首页 → Video | 演示视频 | [07_web_video.png](screenshots/07_web_video.png) |
| 8 | 更新日志 | 底部 Changelog 图标 | 版本历史记录 | [11_web_changelog.png](screenshots/11_web_changelog.png) |

### 1.3 各界面功能与评价

#### 1.3.1 官网首页

- **功能**:首页采用复古 Windows 3.1 风格设计，中央 Blog 窗口展示项目更新动态，左侧 Editor 面板提供在线编辑器入口，右侧 Download 面板提供下载链接，底部有桌面图标式导航栏（Help、Info、Changelog、Credits、Feeds）
- **交互**:窗口可拖拽（draggable 属性），有关闭/最小化按钮，底部图标点击跳转对应页面
- **评价**:网页本身在右下角区域运行了一个 JavaScript 版 eSheep 宠物（页面底部 `esheep.Start()` 调用），让用户无需下载即可体验核心功能。但所有页面中央均覆盖「Go to GitHub」提示框，明确告知「This page is outdated」，体验上略显干扰
- **截图**:[01_web_homepage.png](screenshots/01_web_homepage.png)

#### 1.3.2 下载页面

- **功能**:提供两个下载选项 — DesktopPet.exe（可执行文件，下载量 52,101）和 DesktopPet.gz（zip 压缩包，下载量 13,296）。另有 Microsoft Store UWP 应用入口（Windows 10）
- **交互**:点击图标下载对应文件，Microsoft Store 按钮跳转商店页面
- **评价**:当前版本 1.2.3（2019年10月4日发布），使用 Visual Studio 2019 编译。页面提示「This page is outdated」，最新版本建议去 GitHub 获取。仅支持 Windows 7/8/10，无 Linux/macOS 版本
- **截图**:[02_web_download.png](screenshots/02_web_download.png)

#### 1.3.3 帮助 / 信息 / 更新日志页面

- **功能**:Help 页面提供使用索引和安装指南；Info 页面介绍产品起源（日本动画原作、富士电视台、PlayStation 游戏）；Changelog 记录版本迭代（最新 1.2.3）
- **交互**:通过底部图标导航进入
- **评价**:信息页面详细说明了原作的动画背景（Tatsuhiko Nomura 1994 年作品）和游戏衍生历史，对了解产品文化背景有帮助。Changelog 显示 2019 年后更新频率明显降低
- **截图**:[03_web_help.png](screenshots/03_web_help.png)、[04_web_info.png](screenshots/04_web_info.png)、[11_web_changelog.png](screenshots/11_web_changelog.png)

#### 1.3.4 在线编辑器

- **功能**:网页版宠物动画编辑器，可创建自定义宠物并发布
- **交互**:通过左侧 Editor 面板进入，提供「Open Editor」和「Open Converters」工具入口
- **评价**:编辑器入口存在但页面提示已迁移至 GitHub。离线编辑器需在 GitHub 项目下载
- **截图**:[06_web_editor.png](screenshots/06_web_editor.png)

---

## 2. UI/UX 风格和质量描述

### 2.1 视觉风格

官网采用**复古 Windows 3.1 风格** — 经典灰色标题栏、3D 凸起边框、系统字体、16x16 图标。桌面背景为绿色草地壁纸，与绵羊主题呼应。整个网站是一个「模拟桌面」：可拖拽的窗口、底部任务栏式导航、桌面图标式入口。这种设计既是对原始产品（1995 年 Windows 宠物）的致敬，也形成了独特的视觉识别度。

### 2.2 信息密度与层级

首页信息密度适中：中央 Blog 窗口展示最新动态，两侧边栏提供核心功能入口（下载/编辑器），底部导航栏提供辅助页面。但「Go to GitHub」弹窗遮挡了主内容区，且每个页面都有此提示，对首次访问者造成一定干扰。

### 2.3 交互流畅度

- 窗口拖拽功能正常（HTML5 draggable 实现）
- 网页内嵌的 JavaScript 版绵羊动画可正常运行
- 页面跳转无明显延迟
- 但 GitHub/GitHub Pages 链接在测试环境中无法访问（PR_CONNECT_RESET_ERROR）

### 2.4 文案质量

官网文案为英文，存在少量语法问题（如「This page gives only a COPY」）。文案风格轻松幽默，符合桌面宠物的娱乐定位。项目说明中「Can you remember this application from the '95? This nice sheep covered our desktops for years :D」带有明显的怀旧情感。

### 2.5 可访问性观察

- 对比度：复古风格的灰色标题栏文字对比度偏低
- 无明显的深色模式支持
- 页面未提供语言切换，仅英文
- 弹窗关闭按钮较小，点击区域有限

---

## 3. 官网描述

### 3.1 关键文案摘录

> "Can you remember this application from the '95? This nice sheep covered our desktops for years :D" — 首页 H1 区域

> "Since, this application was a 16-bit version and it doesn't work anymore on Windows7/8/10, I wrote a little application in c# to see this sheep again on the desktop!" — 首页介绍

> "This page is outdated. The entire project and a new editor are now hosted on GitHub." — 各页面弹窗

> "The Sheep program is based on the work of Japanese animator Tatsutoshi Nomura's 1994 'Stray Sheep' series of five-minute animation shorts that were shown at midnight on the Fuji Television network in Japan." — Info 页面

### 3.2 核心卖点（官网视角）

1. **经典复刻**：让 1995 年的桌面绵羊在现代 64 位 Windows 上复活（首页文案锚）
2. **免费开源**：完整代码在 GitHub 上开源，可自由查看和贡献（Open Source 面板）
3. **扩展生态**：支持 NEKO 等其他宠物，可从 GitHub 下载新宠物动画，有在线/离线编辑器创建自定义宠物（Editor 面板、Changelog）
4. **多显示器支持**：宠物可在多屏幕间移动（Changelog v1.2.0）

### 3.3 与实际体验的差距

| 卖点 | 官网原文 | 实际体验 | 差距 |
|---|---|---|---|
| 项目活跃度 | 「Moving to GitHub」(2019) | 官网显示所有页面已过时，最新版本 1.2.3 发布于 2019 年 10 月 | 项目维护似乎已停滞，GitHub 迁移后官网未同步更新 |
| 在线编辑器 | 「Create your own pet!」 | 编辑器页面提示去 GitHub 下载离线编辑器 | 在线编辑器功能已弃用或迁移 |
| 跨平台 | 未明确声明仅限 Windows | 仅提供 .exe 和 UWP，无 Linux/macOS 版本 | 仅限 Windows 平台，限制用户群体 |

---

## 4. 定价

产品完全免费，包括：
- DesktopPet.exe / .zip 免费下载
- Microsoft Store UWP 应用免费
- 开源代码（GitHub）
- 无付费功能或订阅

---

## 5. 目标用户

基于官网用语和实际功能推断：
- **怀旧用户**：1990 年代使用过原版 Stray Sheep 的用户（首页文案直接唤起怀旧情感）
- **Windows 桌面美化爱好者**：希望在桌面上添加趣味动画元素的用户
- **开源贡献者/开发者**：对桌面宠物动画系统感兴趣的开发者（开源项目、编辑器工具链）

---

## 6. 与同类产品对比

| 产品 | 差异点 |
|---|---|
| **Neko** (1990s 原版) | eSheep 是 Neko/Stray Sheep 的现代化复刻。Neko 原版是更简单的猫形宠物，eSheep 扩展了更多动画状态和宠物种类 |
| **BonziBuddy** (1990s-2000s) | BonziBuddy 是紫色猩猩助手，功能更复杂（语音、弹窗、搜索），但因流氓软件行为臭名昭著。eSheep 保持简单纯粹，无侵入性行为 |
| **现代桌面宠物（如 Bongo Cat）** | Bongo Cat 等现代桌面宠物基于更现代的框架（如 Electron），支持更多自定义。eSheep 保持复古像素风格和轻量级 |

---

## 7. 优劣势小结

| 维度 | 优势 | 劣势 |
|---|---|---|
| 产品逻辑 | 经典 IP 复刻，唤起怀旧情感；开源免费；支持自定义宠物扩展 | 仅限 Windows 平台；项目维护停滞（2019 年后无明显更新） |
| UI/UX | 复古 Win3.1 风格设计独特且统一；网页版可即时体验绵羊动画 | 官网提示「已过时」影响体验；GitHub 迁移后官网信息未同步 |
| 工程质量 | 开源可审计；使用现代工具链（VS2019）；支持多显示器 | 无跨平台支持；无自动更新机制（早期版本从网页更新，后改为 GitHub） |

---

## 附录 A 截图索引

| # | 文件 | 说明 |
|---|---|---|
| 01 | screenshots/01_web_homepage.png | 官网首页，展示 Blog、Editor、Download 面板及底部导航 |
| 02 | screenshots/02_web_download.png | 下载页面，Windows .exe/.zip 下载及 Microsoft Store 入口 |
| 03 | screenshots/03_web_help.png | 帮助页面，使用指南和安装说明 |
| 04 | screenshots/04_web_info.png | 信息页面，产品背景和原作介绍 |
| 05 | screenshots/05_web_credits.png | 致谢页面，感谢原作团队 |
| 06 | screenshots/06_web_editor.png | 在线编辑器入口页面 |
| 07 | screenshots/07_web_video.png | 视频演示页面 |
| 11 | screenshots/11_web_changelog.png | 更新日志，版本历史记录 |

> 编号规则：`NN_<source>_<view>.png`，`source ∈ {web, app, android}`，`view` 短 kebab-case；`NN` 单调递增，允许跳号（web 段 01-07，跳 08-10 为已删除的失败截图）。
