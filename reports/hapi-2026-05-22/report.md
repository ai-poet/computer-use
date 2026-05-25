# HAPI 产品分析报告

| 项目 | 值 |
|---|---|
| 官网 | https://github.com/tiann/hapi(代码仓库) / https://hapi.run(产品站) |
| 下载链接 | npm:`npm install -g @twsxtd/hapi`;Homebrew;`npx @twsxtd/hapi`(无独立桌面安装包) |
| 报告日期 | 2026-05-22 |
| 主机 | linux / x86_64 |
| Runtime | sandbox-local(`trycua/cua-xfce`) |
| 模式 | web-only |
| 用时 | 约 30 分钟 |

> 模式说明:**web-only** = 仅基于官网与浏览器截图。HAPI 没有独立桌面 GUI 安装包 —— 它是一个通过 npm/Homebrew 安装的 CLI(`@twsxtd/hapi`),客户端形态是 PWA / Web / Telegram Mini App。沙盒内分析时,启动 hub 还需要本机已装 Claude Code / Codex / Cursor Agent / Gemini / OpenCode 之一,这些 CLI 通常需要外部 API 凭据,因此本轮只在 Firefox 内观察官网 + `app.hapi.run` 未登录态行为。GitHub 直连在本沙盒环境被封,README 与代码元数据通过国内镜像 `kkgithub.com` 访问;`hapi.run` 直连正常。详见 §3.3。

---

## 1. 详细的产品逻辑介绍

### 1.1 总定位

HAPI 是一款面向 AI 编码代理(Claude Code、Codex、Cursor Agent、Gemini、OpenCode)的 **本地优先的远程控制层**:用户在自己机器上启动 HAPI Hub(`npx @twsxtd/hapi hub --relay`),Hub 拉起 AI 代理并把会话注册到一个 SQLite + REST 服务里;用户离开电脑后,通过手机/浏览器打开 `app.hapi.run`(或自托管 hub URL),用 access token 接入,继续审批权限、看终端、收发指令、用语音对话。官网 H1 "Vibe Coding Anytime, Anywhere"(中文版作 "Vibe Coding 随时随地,自由")精确刻画了产品定位:**会话留在本机,手机/浏览器是它的远程视图**,不是把代码搬到云端跑(见 [README §Why HAPI](screenshots/03_web_readme_features.png)、[hapi.run Hero](screenshots/05_web_hapirun_home.png) 与 [Why HAPI 对比页](screenshots/18_web_docs_whyhapi.png))。

它定位为开源项目 [Happy](https://github.com/slopus/happy) 的"本地优先替代品":Happy 把加密数据放云端,HAPI 让每个用户运行自己的 Hub,中继服务器只转发不存储(见 §3.2)。

### 1.2 界面清单

按出现顺序列出本轮观察到的所有主要界面:

| # | 界面 | 入口 | 主要功能 | 截图 |
|---|---|---|---|---|
| 1 | 代码仓库主页(网页) | github.com/tiann/hapi(经 kkgithub 镜像访问) | 仓库概览、About、Star/Fork 数、目录结构 | [02_web_readme_top.png](screenshots/02_web_readme_top.png) |
| 2 | README 头部 + Features | 仓库主页向下滚动 | 7 条产品特性、Demo 视频锚点 | [02_web_readme_top.png](screenshots/02_web_readme_top.png) [03_web_readme_features.png](screenshots/03_web_readme_features.png) |
| 3 | 产品站首页(英) | hapi.run | "Vibe Coding Anytime, Anywhere" 主标、版本徽章、Get Started CTA | [05_web_hapirun_home.png](screenshots/05_web_hapirun_home.png) |
| 4 | 产品站功能区段 | hapi.run 滚动 | 无缝切换、本地核心、Start Anywhere、Seamless Chat 等卡片 | [06_web_hapirun_scroll1.png](screenshots/06_web_hapirun_scroll1.png) [07_web_hapirun_features.png](screenshots/07_web_hapirun_features.png) |
| 5 | "Vibe Coding" Lifestyle 段 | hapi.run 继续滚动 | YOLO Mode / Full Terminal Access 等扩展特性 | [08_web_hapirun_vibecoding.png](screenshots/08_web_hapirun_vibecoding.png) |
| 6 | How it Works 与 Footer | hapi.run 末段 | 三步命令式上手 + 底部链接 | [09_web_hapirun_howitworks.png](screenshots/09_web_hapirun_howitworks.png) [10_web_hapirun_footer.png](screenshots/10_web_hapirun_footer.png) |
| 7 | 文档站 Quick Start | hapi.run/docs/guide/quick-start | npm/Homebrew/npx 三种安装、`hapi hub --relay` 启动 | [12_web_hapirun_docs.png](screenshots/12_web_hapirun_docs.png) [13_web_docs_quickstart2.png](screenshots/13_web_docs_quickstart2.png) |
| 8 | 文档站 Installation | /docs/guide/installation.html | 前置依赖、CLI 验证、架构图 | [14_web_docs_installation.png](screenshots/14_web_docs_installation.png) [15_web_docs_installation2.png](screenshots/15_web_docs_installation2.png) |
| 9 | 文档站 How it Works | /docs/guide/how-it-works.html | 三组件架构(CLI + Agent / Hub + SQLite / Web App)与通信协议 | [16_web_docs_howitworks.png](screenshots/16_web_docs_howitworks.png) [17_web_docs_howitworks2.png](screenshots/17_web_docs_howitworks2.png) |
| 10 | 文档站 Why HAPI | /docs/guide/why-hapi.html | 与 Happy 的对比表与架构差异图 | [18_web_docs_whyhapi.png](screenshots/18_web_docs_whyhapi.png) [19_web_docs_whyhapi2.png](screenshots/19_web_docs_whyhapi2.png) |
| 11 | 文档站 PWA / Voice / Cursor / FAQ | 左侧导航 | 各功能 / Agent 单独子页 | [20_web_docs_faq.png](screenshots/20_web_docs_faq.png) [23_web_docs_voice.png](screenshots/23_web_docs_voice.png) [24_web_docs_pwa.png](screenshots/24_web_docs_pwa.png) [30_web_docs_cursor.png](screenshots/30_web_docs_cursor.png) |
| 12 | 客户端(`app.hapi.run`)登录页 | 站点右上 App↗ 链接 | Access token 输入、Hub (Default) 切换、Needs help 链接、底部署名 | [21_web_app_page.png](screenshots/21_web_app_page.png) |
| 13 | 客户端登录错误态 | 直接点 Sign In | "Hub URL required" 错误 + 内嵌 Hub URL 配置弹层 | [31_web_app_token_filled.png](screenshots/31_web_app_token_filled.png) [32_web_app_signin_err.png](screenshots/32_web_app_signin_err.png) [33_web_app_huberror.png](screenshots/33_web_app_huberror.png) |
| 14 | 中文 + 暗色模式 | 顶部 "中" / 太阳图标切换 | 整站翻译 + 主题反色(强调色由红橙变为青绿) | [26_web_hapirun_zh_home.png](screenshots/26_web_hapirun_zh_home.png) [27_web_hapirun_zh_scroll.png](screenshots/27_web_hapirun_zh_scroll.png) [28_web_hapirun_dark.png](screenshots/28_web_hapirun_dark.png) [29_web_zh_getstarted.png](screenshots/29_web_zh_getstarted.png) |

### 1.3 各界面功能与评价

#### 1.3.1 GitHub 仓库主页 + README

- **功能**:展示 4.1k stars / 442 forks / 63 open issues / 38 PRs / AGPL-3.0 / 70 contributors;README 给出 Features、Demo 视频、Getting Started 命令、Docs 索引、Build from source、Credits;About 卡片同时给出 `hapi.run` 外链与一行简介("App for Claude Code / Codex / Gemini / OpenCode, vibe coding anytime, anywhere")。
- **交互**:READ-only,没有特别交互(GitHub 自带的 Code / Issues / PR 等标签页);通过镜像访问时图标和样式与原站一致。
- **评价**:
  - 信息密度合理 —— 7 条特性都是产品级承诺而非 buzzword(例:`Workspace Browser - Opt-in via one or more hapi runner start --workspace-root <path> flags` 给出了完整 CLI 形态,见 [02_web_readme_top.png](screenshots/02_web_readme_top.png) 与 [03_web_readme_features.png](screenshots/03_web_readme_features.png))。
  - "Credits" 段坦率注明 `HAPI means "哈皮" a Chinese transliteration of Happy. Great credit to the original project.`(README 提取的原文段,见 §3.1)—— 直接承认是 Happy 的派生,没遮掩,这种态度对"为什么不是 fork"类质疑提供了基础。
  - 仓库目录里同时存在 `cli`、`hub`、`shared`、`web`、`website`、`docs`(见 [02_web_readme_top.png](screenshots/02_web_readme_top.png) 仓库列表),与官网 §How it Works 描绘的"三组件 + 文档/落地页"完全一致 —— 没有"官网吹得很大、代码里啥都没"的违和。

#### 1.3.2 hapi.run 落地页

- **功能**:Hero 区(标题 + 版本徽章 `v0.18.3 is now available` + Get Started 按钮)、Seamless Handoff 主题段、"Local Core / Start Anywhere / Seamless Chat / Switch Freely" 四卡片、"The Vibe Coding Lifestyle" 段(含 YOLO Mode / Full Terminal Access 等)、How it Works(三步:Install on machine → Run anywhere → Open the URL)、底部 CTA "Ready to Vibe?" + Footer(Product / Community 两列)。
- **交互**:顶部导航固定;Get Started / 立即开始 CTA 点击后跳转到 `/docs/guide/quick-start`(见 [29_web_zh_getstarted.png](screenshots/29_web_zh_getstarted.png));右上有语言切换("中"/"EN")、明暗模式切换、GitHub 图标。整站为 SPA(`/assets/index-WB_F_LCQ.css` + 单一 JS bundle),路由错误返回站内 404 卡片(见 [11/25 删除前抓的 404 页参考]),不进入 Firefox 原生错误页。
- **评价**:
  - 落地页主轴极清晰:**"会话留在本机,手机只是一个窗口" → "无缝切换" → "三步起步"**(参 [05_web_hapirun_home.png](screenshots/05_web_hapirun_home.png) [06_web_hapirun_scroll1.png](screenshots/06_web_hapirun_scroll1.png) [09_web_hapirun_howitworks.png](screenshots/09_web_hapirun_howitworks.png))。文案与功能一对一,几乎没有空喊。
  - 卡片里嵌入了真实 UI 截图(手机壳里的会话创建、e2ee 路径下的工作树等),不是用素材图占位 —— 见 [07_web_hapirun_features.png](screenshots/07_web_hapirun_features.png) 的 `/data/github/happy/hapi__worktrees/e2ee · work...` 路径,这是开发者本人真实工作目录的截图(而且未脱敏,这点见 §2.4)。
  - YOLO Mode 与 Full Terminal Access 是产品角度比较"敢说"的卖点(直接给的话术是 "Trust your agents? Enable YOLO mode to bypass approvals and let them sprint while you sleep.",见 [08_web_hapirun_vibecoding.png](screenshots/08_web_hapirun_vibecoding.png))—— 把使用边界说清楚,而不是回避。
  - 唯一弱项:Hero 区下方很长一段全部是白底大留白(滚到第二屏才出现 Seamless Handoff 主题),首屏对"产品是什么"的解释只在右侧插画里间接体现 —— 对从 Google 直接打开页面的用户,需要滚一屏才知道"这是 AI 代理的手机端控制器"。

#### 1.3.3 文档站(Quick Start / Installation / How it Works / Why HAPI / FAQ / PWA / Voice Assistant / Cursor Agent)

- **功能**:左侧栏 9 项导航固定;中间是 H1 + 段落 + 代码块(npm / bash);右上还有 Quick Start / App↗ 浮动入口,有 Search(Ctrl K)。Installation 页给前置 CLI 校验命令(`claude --version`、`codex --version` 等),How it Works 页有 ASCII 架构图把"Your Machine"内部组件画出来:`HAPI CLI + AI Agent` ↔ `HAPI Hub + SQLite + REST API` ↔ `Web App (embedded)`,通过 Socket.IO / SSE / RPC 通讯;Why HAPI 给完整对比表(Aspect / Happy / HAPI),并配两张架构图(Happy 把加密 DB 放云端 vs HAPI 让 CLI 自己持有 keys)。
- **交互**:左栏点击切换页面有明显闪烁(应是 SSG → SPA 路由切换的 hydration 抖动);代码块右上有复制按钮;搜索框有 Ctrl K 快捷键标识但未实测。
- **评价**:
  - 内容颗粒度合适:Installation 直接列了"必须先装 Claude Code / Codex / Cursor Agent / Gemini / OpenCode 之一",而不是装作零依赖(见 [14_web_docs_installation.png](screenshots/14_web_docs_installation.png))。这是 HAPI 区别于"AI agent 平台"的关键 —— 它是 wrapper,不是 agent。
  - ASCII 架构图清晰且自洽:[16_web_docs_howitworks.png](screenshots/16_web_docs_howitworks.png) 的图和 README 中 "Native First - HAPI wraps your AI agent instead of replacing it" 的文案完全对应。
  - "Why HAPI" 章节没有回避竞争 —— 直接命名上游 Happy 并列对比表(Architecture/Users/Data storage/Deployment 等),这种直球做法在国内项目里少见,提升信任度。
  - 不足:`/installation`(无 `/docs/guide/` 前缀)是 404(见删除前的 `11_web_hapirun_install.png`),站点没做 alias 重定向 —— 用户从外部记忆里直接拼链接会扑空。

#### 1.3.4 `app.hapi.run` 客户端登录态

- **功能**:大字 "HAPI" + tagline "Vibe Coding Anytime, Anywhere" + 单个 Access token 输入框 + Sign In 按钮 + 左下 `Needs help?` 链接 + 右下 `Hub (Default)` 链接;输入 token 时密码字符替换为圆点;直接 Sign In 不带 hub 配置会弹出 "Hub URL required. Please set it before signing in." 红字错误,并把 Hub URL 配置面板内联展开(`Hub origin` 输入框 + 提示 `Use http(s) only. Any path is ignored.` + Save hub 按钮)。
- **交互**:整页极简,无导航;右上角小图标是浏览器翻译入口(Firefox 自带,不是页面提供);浏览器自动弹"保存密码"提示需手动 Esc 关掉(见 [32_web_app_signin_err.png](screenshots/32_web_app_signin_err.png))。
- **评价**:
  - 把"Hub 必须先配"这件事用错误态而不是引导性文案告诉用户 —— 略微反直觉。首次访问者看到的是空白 token 框,容易认为它是 SaaS 登录页;按 Sign In 之后才知道还要填自己的 hub origin,这个发现路径不太友好(对比 [21_web_app_page.png](screenshots/21_web_app_page.png) 与 [33_web_app_huberror.png](screenshots/33_web_app_huberror.png))。
  - 优点:Hub origin 输入框默认占位是 `https://hapi.example.com`(见 [33_web_app_huberror.png](screenshots/33_web_app_huberror.png)),且有一行短注释 "Use http(s) only. Any path is ignored." —— 一旦用户进入这一步,后续提示是清楚的。
  - `Hub (Default)` 文案说明默认连的就是 `https://app.hapi.run`(见 [33_web_app_huberror.png](screenshots/33_web_app_huberror.png) 中 `Current: https://app.hapi.run (Default)`),与"local-first / 自托管"的产品定位形成对比 —— 默认入口指向官方 hub,但允许覆盖。
  - 没有第三方登录、没有注册按钮 —— 一切凭 token 起手,与"自己持有 keys"的架构主张吻合。

#### 1.3.5 中文与暗色模式

- **功能**:顶部右侧 "中"/"EN" 按钮切语言,太阳/月亮按钮切主题。中文版整站文案被替换(Hero 译作 "Vibe Coding 随时随地,自由",副标译作 "始于桌面,续于任何地方,随时切回。",CTA "立即开始");暗色模式下背景反色为接近黑(`#0b0c0e`),强调色由原本的橙红(`#E55C42` 量级)切到青绿(`#3CDE9D` 量级)。
- **交互**:切换语言后 URL 仍是 `hapi.run`(没加 `/zh/` 前缀,试访问 `/zh/` 是 404 —— 见 §1.3.3 评价里指出的同类问题);切换主题瞬时生效,无过渡动画。
- **评价**:
  - 翻译质量高且有本地化润色("续于任何地方,随时切回" 比直译 "Continue anywhere, switch back anytime" 自然,见 [27_web_hapirun_zh_scroll.png](screenshots/27_web_hapirun_zh_scroll.png));Vibe Coding 这种概念词保留英文,避免硬译。
  - 暗色模式下 CTA 按钮从填充红橙变为填充青绿(见 [28_web_hapirun_dark.png](screenshots/28_web_hapirun_dark.png)),整体调性变化大,不是简单"反色" —— 设计上用了两套调色板而不是一套加滤镜。
  - 缺点:语言状态不进 URL 也不进 cookie 显式提示 —— 切到中文后刷新页面有时会回到英文(本次未深度验证)。

---

## 2. UI/UX 风格和质量描述

### 2.1 视觉风格

- 落地页用米色暖底(`#FBF5EB` 量级)+ 大字粗 Inter sans + 橙红(`#E55C42` 量级)强调色;插画风为温暖、低多边形、卡通拟人(机器人 + 设备),与"vibe / 放松"主题一致(见 [05_web_hapirun_home.png](screenshots/05_web_hapirun_home.png) Hero 区右侧、[08_web_hapirun_vibecoding.png](screenshots/08_web_hapirun_vibecoding.png) 三只熊插画)。
- 暗色模式下保持同款字体与版式,只切配色为深灰底 + 青绿点缀(见 [28_web_hapirun_dark.png](screenshots/28_web_hapirun_dark.png))。
- 文档站走 VitePress / Vocs 类风格:白底、左侧栏导航、灰色边线、代码块带语言标签 + 复制按钮(见 [12_web_hapirun_docs.png](screenshots/12_web_hapirun_docs.png))。
- 客户端 `app.hapi.run` 走更克制的纯白底极简(见 [21_web_app_page.png](screenshots/21_web_app_page.png))—— 没有插画、没有暖色,只一行 tagline 和登录组件;与官网刻意的"温度"形成反差,符合"工具该该专注、官网该煽情"的常见取舍。

### 2.2 信息密度与层级

- 落地页首屏只有标题 + 版本徽章 + 一个红色 CTA(Get Started),没有 5 个按钮抢镜头,层级清楚(见 [05_web_hapirun_home.png](screenshots/05_web_hapirun_home.png))。
- 主 CTA(Get Started / 立即开始)在所有页面都在右上角并一直跟随 —— 跨页一致,不会丢失。
- 缺点:首屏右侧插画占了视觉中心,但插画内容是装饰性的(机器人 + 笔记本 + 设备),没有把"它是手机控制 AI 代理"的核心信息直接画进去;依赖滚动到第二屏才能看到 Seamless Handoff 的真实手机壳示意。

### 2.3 交互流畅度

- 落地页与文档站之间的跳转有约 0.5–1s 的"白屏 → 渲染"过程,SPA 但 hydration 不算瞬时(肉眼可见左栏闪烁,见连续抓的 [12](screenshots/12_web_hapirun_docs.png) → [13](screenshots/13_web_docs_quickstart2.png) → [14](screenshots/14_web_docs_installation.png))。
- 主题切换无过渡动画(从 [27_web_hapirun_zh_scroll.png](screenshots/27_web_hapirun_zh_scroll.png) 一键到 [28_web_hapirun_dark.png](screenshots/28_web_hapirun_dark.png) 是瞬切),颜色直接换,无视觉缓冲。
- 错误反馈即时:Sign In 没填 hub 时,红字错误立刻出现,且 hub URL 输入框联动展开(见 [32](screenshots/32_web_app_signin_err.png) → [33](screenshots/33_web_app_huberror.png))。
- 加载 indicator:Firefox 自身的 tab spinner 是唯一 indicator —— 落地页 SPA 中点击 CTA 后页面会出现短暂 router transition,无骨架屏或进度条。

### 2.4 文案质量

- 英文文案凝练,几乎没有冗词:Hero 副标 *"Your session lives on your machine. Your phone is just a window."*(见 [06_web_hapirun_scroll1.png](screenshots/06_web_hapirun_scroll1.png))把整套架构哲学压成两句。
- "Why HAPI?" 文档里给出极坦率的对照(见 [18_web_docs_whyhapi.png](screenshots/18_web_docs_whyhapi.png)):*"Happy uses a centralized server that stores your encrypted data. HAPI is decentralized — each user runs their own hub, and the relay server only forwards encrypted traffic without storing anything."* —— 既不踩对手,也不和稀泥。
- 中文版本地化做了二次创作(见 §1.3.5 评价),无机翻味。
- **小问题**:示意截图([07_web_hapirun_features.png](screenshots/07_web_hapirun_features.png) 中部 phone mockup)直接露出开发者真实工作目录 `/data/github/happy/hapi__worktrees/e2ee · work...` —— 路径里把"happy"父目录也带出来了(暗示作者本人也用 happy 的 monorepo 结构),对脱敏不够讲究;作为产品截图无伤大雅,但对企业用户是个心理负担。

### 2.5 可访问性观察(肉眼可见的)

- 浅色模式下橙红 CTA 在米色底上对比度足够,Sign In 黑色按钮在白底上对比度极高 —— 主操作可达性好。
- 灰色 placeholder 文字在 token 输入框里对比度偏低(见 [21_web_app_page.png](screenshots/21_web_app_page.png) "Access token" 占位字几乎贴近 input 边缘色),WCAG AA 边缘命中。
- 语言切换按钮、主题切换按钮都是无文字图标按钮 + 单字"中"/"EN" —— 没有 `aria-label` 显式可见证据(未深查 DOM,仅以浏览器悬停未见 tooltip 为初步观察)。
- 暗色模式青绿强调色对深底对比度很高,可读性强(见 [28_web_hapirun_dark.png](screenshots/28_web_hapirun_dark.png))。

---

## 3. 官网描述

### 3.1 关键文案摘录

> "Run official Claude Code / Codex / Gemini / OpenCode sessions locally and control them remotely through a Web / PWA / Telegram Mini App."
> —— 来源:仓库 README H1 下首段(见 [02_web_readme_top.png](screenshots/02_web_readme_top.png))

> "Vibe Coding Anytime, Anywhere."
> —— 来源:hapi.run Hero H1(见 [05_web_hapirun_home.png](screenshots/05_web_hapirun_home.png))

> "Start on Desktop. Continue Anywhere. Switch Back Anytime. Your session lives on your machine. Your phone is just a window."
> —— 来源:hapi.run 第二屏(见 [06_web_hapirun_scroll1.png](screenshots/06_web_hapirun_scroll1.png))

> "Native First - HAPI wraps your AI agent instead of replacing it. Same terminal, same experience, same muscle memory."
> —— 来源:README Features 段第二条(见 [03_web_readme_features.png](screenshots/03_web_readme_features.png))

> "AFK Without Stopping - Step away from your desk? Approve AI requests from your phone with one tap."
> —— 来源:README Features 段第三条(同上)

> "YOLO Mode - Trust your agents? Enable YOLO mode to bypass approvals and let them sprint while you sleep."
> —— 来源:hapi.run "Vibe Coding Lifestyle" 段(见 [08_web_hapirun_vibecoding.png](screenshots/08_web_hapirun_vibecoding.png))

> "Happy uses a centralized server that stores your encrypted data. HAPI is decentralized — each user runs their own hub, and the relay server only forwards encrypted traffic without storing anything."
> —— 来源:文档 Why HAPI 短答(见 [18_web_docs_whyhapi.png](screenshots/18_web_docs_whyhapi.png))

> "HAPI means '哈皮' a Chinese transliteration of Happy. Great credit to the original project."
> —— 来源:README 末尾 Credits 段(README 提取原文,§1.3.1 评价已引用)

> "HAPI 是一款本地优先的自托管平台,用于在远程运行和控制 AI 编码代理(Claude Code、Codex、Gemini、OpenCode)。它让你在自己的电脑上开启编码会话,然后从手机上监控/控制它们。"(译自原文)
> —— 来源:文档 FAQ "What is HAPI?"(见 [20_web_docs_faq.png](screenshots/20_web_docs_faq.png))

### 3.2 核心卖点(官网视角)

1. **本地优先 / 自托管**(原文锚:Why HAPI 短答) —— Hub 跑在用户机器或自有 VPS 上,中继服务器零落地数据。
2. **包裹而非替换 AI 代理**(原文锚:README Features 第二条 "Native First") —— Same terminal, same experience。
3. **AFK 不打断**(原文锚:README Features 第三条 "AFK Without Stopping") —— 手机一键审批权限请求。
4. **跨 Agent 统一工作流**(原文锚:README Features 第四条 "Your AI, Your Choice") —— Claude Code / Codex / Cursor / Gemini / OpenCode 五选一,前端一致。
5. **WireGuard + TLS E2EE 中继**(原文锚:README Getting Started 末段 "The relay uses WireGuard + TLS for end-to-end encryption") —— 强加密叙事。
6. **PWA + Telegram Mini App 两条远程通道**(原文锚:hapi.run 落地页主标 "Web / PWA / Telegram Mini App")。

### 3.3 与实际体验的差距

| 卖点 | 官网原文 | 实际体验 | 差距 |
|---|---|---|---|
| "Install in one line" 隐含 | README `npx @twsxtd/hapi hub --relay` 一行起步(见 [03_web_readme_features.png](screenshots/03_web_readme_features.png)) | Installation 文档明确还要先装 Claude Code / Codex / Cursor / Gemini / OpenCode 之一(见 [14_web_docs_installation.png](screenshots/14_web_docs_installation.png)) | README/Hero 没把"需要先有底层 agent CLI"放在第一句;只有点进文档才看到 prerequisites。轻度过度承诺。 |
| 文档路径稳定性 | 站内提及 "see Installation"(README Getting Started 末段) | 直接拼 `hapi.run/installation` → 404;只有 `/docs/guide/installation.html` 才正确 | URL 别名缺失,文档站对外部链接的兼容性弱。 |
| 客户端启动门槛 | hapi.run 强调"Continue Anywhere" | `app.hapi.run` 默认指向官方 hub 但无后端,Sign In 报 "Hub URL required"(见 [33_web_app_huberror.png](screenshots/33_web_app_huberror.png)) | 默认 Hub 是占位而非真实可用 SaaS,未登录态体验不能让陌生访客一键试用 —— 与"Start Anywhere"的口号有距离;符合 local-first 哲学,但落地页文案没把这点交代清楚。 |
| 截图脱敏 | 官网功能卡片宣称代码会话流畅(见 [06_web_hapirun_scroll1.png](screenshots/06_web_hapirun_scroll1.png)) | 同张图右侧手机壳显示开发者真实工作树路径 `/data/github/happy/hapi__worktrees/e2ee · work...` | 演示素材未脱敏,泄露作者目录结构。无功能问题,但与"加密 / 隐私优先"叙事观感不一致。 |

---

## 4. 目标用户

依据官网与文档的语言指向(`vibe coding`、`AI agent`、`Claude Code / Codex / Cursor / Gemini / OpenCode`、`MCP`、`WireGuard + TLS`、`Tailscale / Cloudflare Tunnel 自托管选项`)与功能形态(CLI + Hub + PWA),目标用户是:

- **重度使用 AI 编码代理的开发者**:已经把 Claude Code / Codex / Cursor Agent 等装在工作机上,经常被 "approve this command?" 弹窗打断,希望在离开座位时也能让 agent 继续跑(证据:README "AFK Without Stopping" 与 hapi.run "Approve AI requests from your phone with one tap")。
- **对隐私/数据落地敏感的工程师团队**:对 Happy 把加密数据放云端有顾虑,愿意自己运维 Hub(证据:文档 Why HAPI 的对比表强调 `data storage: only on user's device` vs Happy 的 `centralized cloud database`,见 [18_web_docs_whyhapi.png](screenshots/18_web_docs_whyhapi.png))。
- **中英双语开发者**:站点优先英文,中文做了高质量本地化,中文 README 段落与 i18n CTA 都在(证据:Credits 段对中文谐音的解释 + 中文落地页 [27_web_hapirun_zh_scroll.png](screenshots/27_web_hapirun_zh_scroll.png))。

不像是面向"非工程师 / 零基础" —— 它没有 GUI 安装包,也没有任何 "no-code" 卖点。

---

## 5. 与同类产品对比

| 维度 | HAPI | Happy(上游) | 直接走 SSH/Mosh/tmux |
|---|---|---|---|
| 数据落地 | 仅用户设备(Why HAPI 表格,见 [18_web_docs_whyhapi.png](screenshots/18_web_docs_whyhapi.png)) | 加密数据存中心服务器 | 仅用户设备 |
| 部署复杂度 | 单二进制 npm/Homebrew(README Quick Start) | Docker + PostgreSQL + Redis(Why HAPI 表格列出) | 系统级 daemon |
| 端到端加密 | WireGuard + TLS(README "The relay uses WireGuard + TLS") | E2EE 但服务器持加密 DB | SSH 本身 |
| 客户端形态 | PWA / Web / Telegram Mini App | 移动 App + Web | 终端 over SSH |
| AI agent 集成 | 5 种内置(README Features) | 类似 | 无内置 |
| 权限审批前端 | 手机一键 approve(见 [06_web_hapirun_scroll1.png](screenshots/06_web_hapirun_scroll1.png) "Create Session" 弹层) | 类似 | 无 |

差异点:**HAPI 拿掉 Happy 的中心数据库**,代价是失去多用户共享一套服务的能力(Why HAPI 表格 `Users: any number (each runs own hub)` 隐含的就是"自己运营、自己升级"),收益是不需要相信中心运营方。对比 SSH/tmux,HAPI 的不可替代价值是"权限弹窗手机一键批准"这种 AI-agent 时代特有的交互。

---

## 6. 优劣势小结

| 维度 | 优势 | 劣势 |
|---|---|---|
| 产品逻辑 | 定位清晰("AI 代理的手机端控制器"),不与底层 agent 抢生态;对上游 Happy 的差异化(去中心化)直接、可证伪 | 强依赖底层 agent CLI(Claude/Codex 等)+ 用户自有 API 配额,首次启动门槛比落地页暗示的高一截 |
| UI/UX | 落地页温度感强、文档信息密度高、中英 + 明暗主题完整;CTA 一致跟手 | 落地页首屏对"是什么"的解释要滚一屏才显;`app.hapi.run` 未登录态对新人是个迷宫(需先填 hub URL 才能 Sign In);文档站直接拼短路径会 404 |
| 工程质量 | 仓库结构与官网架构图一一对应;4.1k stars、738 commits、活跃迭代(本次访问当天 5 小时前还在 push,见 [02_web_readme_top.png](screenshots/02_web_readme_top.png));AGPL-3.0 开源 | 演示素材未脱敏(开发者真实路径外泄);URL 别名缺失;Hub 默认占位让"立即开始"的口号在新人侧打了折扣 |

---

## 附录 A 截图索引

| # | 文件 | 说明 |
|---|---|---|
| 01 | screenshots/01_web_homepage.png | 初次抓 github.com/tiann/hapi(直连失败,空白白页) |
| 02 | screenshots/02_web_readme_top.png | 经 kkgithub 镜像加载后的仓库主页 + README HAPI 标题 + Features 头部 |
| 03 | screenshots/03_web_readme_features.png | README Features 七条与 hapi-demo.mp4 视频锚点 |
| 05 | screenshots/05_web_hapirun_home.png | hapi.run Hero(Vibe Coding Anytime, Anywhere)+ 版本徽章 + Get Started |
| 06 | screenshots/06_web_hapirun_scroll1.png | "Start on Desktop. Continue Anywhere." 主题段 + Create Session/e2ee 手机壳 |
| 07 | screenshots/07_web_hapirun_features.png | Switch Freely / Start Anywhere / Seamless Chat 四卡片 + Vibe Coding Lifestyle 区入口 |
| 08 | screenshots/08_web_hapirun_vibecoding.png | YOLO Mode + Full Terminal Access + "How it Works" 区入口 |
| 09 | screenshots/09_web_hapirun_howitworks.png | hapi.run How it Works 三步(npx 命令)+ End-to-end encrypted 注脚 |
| 10 | screenshots/10_web_hapirun_footer.png | Ready to Vibe CTA + Footer Product/Community 列 + AGPL License 署名 |
| 12 | screenshots/12_web_hapirun_docs.png | 文档 Quick Start(npm/Homebrew/npx 三 tab)+ Start the hub 第二步 |
| 13 | screenshots/13_web_docs_quickstart2.png | Quick Start Next steps(Seamless Handoff / Hub setup / Notifications / Install the App) |
| 14 | screenshots/14_web_docs_installation.png | Installation Prerequisites(必须先装 Claude/Codex/Cursor/Gemini/OpenCode 之一) |
| 15 | screenshots/15_web_docs_installation2.png | Installation "How they work together" ASCII 架构图(CLI+Agent / Hub+SQLite / Web App) |
| 16 | screenshots/16_web_docs_howitworks.png | How it Works 章节头 + Architecture Overview ASCII 图(本机内部组件) |
| 17 | screenshots/17_web_docs_howitworks2.png | How it Works Components 段 + HAPI CLI 描述(MCP 工具、会话注册等) |
| 18 | screenshots/18_web_docs_whyhapi.png | Why HAPI? TL;DR 对比表头(Architecture / Users / 等) |
| 19 | screenshots/19_web_docs_whyhapi2.png | Why HAPI 下半部分:Public Internet 架构对比图(Happy 中心化 vs HAPI 去中心化) |
| 20 | screenshots/20_web_docs_faq.png | FAQ General 段(What is HAPI / What does HAPI stand for) |
| 21 | screenshots/21_web_app_page.png | app.hapi.run 登录页(Access token + Sign In + Hub Default + Needs help) |
| 23 | screenshots/23_web_docs_voice.png | Voice Assistant 文档页(ElevenLabs Conversational AI 加持) |
| 24 | screenshots/24_web_docs_pwa.png | PWA 文档页(home screen icon / full screen / offline / auto-updates) |
| 26 | screenshots/26_web_hapirun_zh_home.png | 中文版 hapi.run Hero "Vibe Coding 随时随地,自由" |
| 27 | screenshots/27_web_hapirun_zh_scroll.png | 中文版第二屏 "始于桌面,续于任何地方,随时切回" |
| 28 | screenshots/28_web_hapirun_dark.png | 暗色模式中文 Hero(强调色切青绿,留 Get Started 绿色填充) |
| 29 | screenshots/29_web_zh_getstarted.png | "立即开始" CTA 跳转 Quick Start docs 验证 |
| 30 | screenshots/30_web_docs_cursor.png | Cursor Agent 文档页(macOS/Linux/Windows 安装命令) |
| 31 | screenshots/31_web_app_token_filled.png | app.hapi.run token 填入(密码字符替换为圆点,Sign In 按钮高亮) |
| 32 | screenshots/32_web_app_signin_err.png | Sign In 后 Firefox 弹保存密码 + 页面显示 Hub URL 必填错误 |
| 33 | screenshots/33_web_app_huberror.png | 关 Firefox 弹窗后纯净的 "Hub URL required" 错误态 + Hub origin 输入框 + Save hub 按钮 |
