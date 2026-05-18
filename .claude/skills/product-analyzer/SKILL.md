---
name: product-analyzer
description: 给定产品名和官网 URL,产出含三个强制章节(产品逻辑/UIUX/官网描述)的中文 Markdown 产品分析报告与配套截图文件夹。优先驱动桌面端;桌面端不可用时自动降级 web-only。触发方式:scripts/analyze_product.py 调用,或对话中"分析/拆解/评测/调研 这个产品 https://..."类请求且包含 URL。
---

# product-analyzer

把"分析一个新产品"这件事固化成一条可重复流水线。每次跑都产出一份结构稳定的报告 + 一组带命名规则的截图,方便对外提交、归档、跨产品横向比较。

## 工作模式

- **完整模式 (full)**:抓官网 → 找出当前主机能用的安装包 → 装好驱动器(`scripts/install_cua_driver.py`)→ 启动产品 → 用 cua-driver 操作主要界面 → 批量截图 → 整合写报告
- **网页模式 (web-only)**:仅基于官网信息 + 浏览器截图。仅在桌面驱动不可达时启用 — 见下文"跨平台与降级"

## 输入

由调用方(脚本或对话)提供:
- `product_name` — 必填,展示用原文(允许中文 / 大小写混排)
- `url` — 必填,产品官网 https URL
- `download_url` — 可选,直接指向当前主机能用的安装包(.dmg / .exe / .deb 等)。**优先级最高**,有它就跳过"在官网找下载链接"步骤
- `output_dir` — 调用方已经建好的绝对路径,形如 `<repo>/reports/<slug>-YYYY-MM-DD[-N]/`,本 skill 把所有产物写进去

## 输出布局

```
<output_dir>/
  report.md                     # 报告主体
  metadata.json                 # 机器可读元数据
  screenshots/
    01_web_homepage.png
    02_web_pricing.png         # 编号见下
    05_app_main.png
    ...
```

`metadata.json` 的最终形态(Python 脚本写了雏形,本 skill 在结束前补齐):
```json
{
  "product_name": "ProductiveKitty",
  "url": "https://productivekitty.masterwordai.com",
  "download_url": null,
  "host_os": "darwin",
  "host_arch": "arm64",
  "started_at": "2026-05-18T03:30:00+08:00",
  "finished_at": "2026-05-18T03:55:00+08:00",
  "mode": "full",
  "screenshots": [
    {"file": "screenshots/01_web_homepage.png", "view": "web-homepage", "caption": "官网首页"},
    ...
  ],
  "warnings": []
}
```

## 截图命名

`NN_<source>_<view>.png`:
- `NN` — 两位零填充的单调编号。**允许跳号**:web 段一般 01-04,app 段 05+ 起;若中途新增也可以拿 09、10
- `source ∈ {web, app}` — `web` 表示浏览器内截图,`app` 表示桌面应用窗口截图
- `view` — 短 kebab-case,语义化:`homepage / pricing / faq / main / settings / new-task / focus-mode / report-detail` 等

每张截图都必须在 `report.md` 里以相对路径(`screenshots/NN_*.png`)出现,且在**附录 A 截图索引**里有一行说明。没引用过的截图删掉,不要留弃图。

## Canonical loop(7 步,固定顺序)

调用方进入时,`output_dir` 已建好、`metadata.json` 雏形已写。这 skill 接管后续。

**两条铁律(优先级高于任何步骤细节)**:

1. **找下载链接 = 用 cua-driver 真实操作浏览器**,不是只跑 curl + grep。`curl + grep` 只是快速线索,**不是判定 web-only 的依据**。`grep` 没出结果时**必须**继续打开浏览器,真实点击导航到"下载"/"Download"/"产品"/"Pricing"等页面,把官网走一遍 — 很多产品的下载入口藏在二级菜单、弹窗、用户登录后的页面、或者由 JS 动态注入的 CDN URL 里,只看初始 HTML 必然漏。所有这些点击都通过 cua-driver,严守 no-foreground 契约
2. **降级 web-only 是最后手段,且改变后续行为**:确认能下载到安装包 → **跳过网页内深度交互,所有时间花在桌面端**;确认下不到 → 这时才把网页当主战场,用 cua-driver 在浏览器里完整体验各个页面(首页 / 功能页 / 定价 / 文档 / 博客 / FAQ / 注册前能看到的 demo)。**两种模式不并行体验,避免 web 段截图浪费精力**

### 7 步详细

1. **TodoWrite 建 7 个 todos**:`抓取官网` → `定位下载链接` → `安装/启动应用` → `驱动目标(应用或网页)` → `批量截图` → `整合报告` → `补齐 metadata.json`。每步开始前 `in_progress`,完成转 `completed`

2. **抓取官网原始信息(仅作为线索,不是体验)** — 用 `curl -fsSL` 拿 HTML(走父 shell 代理),用 Python 把 `<script>` / `<style>` 剥掉提取纯文本备用。**这一步不算"体验"**,纯粹搜集后续 grep / 导航的素材。可以同时通过 cua-driver 打开浏览器,做一张首页全景截图(`01_web_homepage.png`)

3. **定位下载链接(分两层:静态 grep + 真实浏览)** —
   优先用调用方传入的 `download_url`。否则:

   **3.1 静态扫描(快速、便宜,但**不**充分)**:
   - 全文 URL 正则:`grep -oE 'https?://[^"<>\s]+\.(dmg|exe|pkg|msi|deb|rpm|appimage|tar\.gz|tar\.xz|zip)([?#][^"<>\s]*)?' homepage.html | sort -u`
   - 关键字定位跳转页:grep `download` / `下载` / `releases` / `\.app[^a-z]`
   - storage bucket 列表:静态命中 URL 指向公开目录(MinIO / S3 ListBucketResult XML)就 curl 那个根目录

   **3.2 浏览器实操(必须做,不可跳过 — 除非 3.1 已经命中且按主机 OS 选定了正确架构)**:
   通过 cua-driver:
   - 打开浏览器,定位到官网,**用 cua-driver 真实点击**导航栏里所有看起来相关的入口:`Download`/`下载`/`Get the App`/`Install`/`Pricing`/`Get Started`/`Try Free`/`产品`等
   - 每个候选页都截图存档(`screenshots/02_web_<view>.png` 形式)
   - 用 cua-driver 滚到底部,看 footer 有没有 `Mac` / `Windows` / `Linux` 的小图标按钮
   - 点击平台切换器(很多站点会先显示访客 OS 推荐)、关掉登录弹窗、关掉 cookie 横幅,继续找
   - 任何 a11y 树为空 / Electron canvas 的页面按 [cua-driver SKILL](../cua-driver/SKILL.md) 的 escalation 阶梯升级到 vision

   **3.3 命中后选最匹配的安装包**:
   - `darwin/arm64` 优先 `*arm64*.dmg`、`*aarch64*.dmg`,否则 `darwin/x86_64` 用 `*x64*.dmg`、`*intel*.dmg`、不带架构标的 `.dmg`
   - `linux/x86_64` 优先 `*x86_64*.AppImage`/`.deb`/`.tar.gz`
   - `windows/x86_64` 选 `*.exe` / `*.msi` / `Setup-*.exe`

   **3.4 全部失败才标 web-only**,并在 `metadata.warnings[]` 写明:
   - 静态 grep 试过哪些
   - 浏览器实际访问/点击过哪些页面(列出页面 URL,证明做了真实 hunt)
   - 最终结论(如"产品仅有 Web 版,无桌面端安装包")

4. **安装/启动应用(仅当 step 3 命中)** — 用 `scripts/install_cua_driver.py` 确保桌面驱动器已装(预检过,但 sanity-check 一次 `which cua-driver`)。下载产品安装包到临时目录,按平台用对应方式安装(macOS:`hdiutil attach` + `cp -R` + `xattr -d com.apple.quarantine`;Linux:`dpkg -i` 或 `chmod +x` AppImage;Windows:`start /wait` MSI)。**严格遵循 [cua-driver SKILL](../cua-driver/SKILL.md) 的 no-foreground 契约**。

5. **驱动目标(应用 OR 网页,二选一,**不并行**)** —

   **5.A 完整模式(step 3 命中):驱动桌面应用** — 启动产品,**主要功能挨个走一遍**。每打开一个新界面就 snapshot + screenshot。覆盖到的典型界面:启动页 / 主功能页 / 创建/新建流 / 设置 / 偏好 / 帮助 / 关于 / 错误状态(故意触发一次)。**所有 a11y/click/type/screenshot 必须通过 cua-driver**,直接 `screencapture` / `osascript activate` 是违约。**这一阶段不再花时间深挖网页**,网页只保留 step 2 的首页快照即可。

   **5.B 网页模式(step 3 全部失败,降级 web-only):用 cua-driver 在浏览器里完整体验** — 这时网页就是产品本体,cua-driver 驱动浏览器逐页深入:
   - 首页(滚到底,各 section 各截一张)
   - 主功能页 / 演示页(能交互的部分都试一下:输入、提交、播放、切 tab)
   - 定价 / Pricing(各档位都点开)
   - 文档 / 帮助 / Changelog
   - FAQ / 博客头版 / 关于
   - 登录入口(只看不操作账号)
   - 国际化:有 `EN/中文/...` 切换器就切一遍各看一张
   - 错误态:故意输入错的、点不该点的,看交互反馈

   两种模式都要保证 §1 报告章节有足够多的"界面"可写。完整模式的 web 段不应超过 1-2 张图;web-only 模式的 web 段至少 6-10 张图。

6. **批量截图** — 整理 screenshots/,删冗余、保留代表性的、确保命名连续(允许跳号)

7. **整合报告** — 拷贝 [REPORT_TEMPLATE.md](REPORT_TEMPLATE.md) 到 `<output_dir>/report.md`,逐节填写。可选章节(定价 / 目标用户 / 同类对比 / 优劣势)**只在有证据时保留,否则整段删除**。所有"评价"型陈述必须可被截图或官网原文证实

每步结束 TodoWrite 标 `completed`,下一步标 `in_progress`,然后开始下一步。

## 报告模板要求

参见 [REPORT_TEMPLATE.md](REPORT_TEMPLATE.md)。要点:

- **必有章节(顺序不能变)**:`总定位` → `界面清单` → `各界面功能与评价` → `UI/UX` → `官网描述` → `附录 A 截图索引`
- **可选章节**(`定价 / 目标用户 / 同类对比 / 优劣势小结`):有证据才写,无则整段删,**不要留"信息不足"占位**
- **每个评价必须可证伪**:不写"流畅"、"美观",写"启动到首屏约 0.8s,无加载动画"或"主 CTA 用紫色填充按钮位于首屏右下,与背景对比度满足 WCAG AA"
- **官网原文用引号引用**(不要意译),节标题旁标"原文锚:首页 H1"之类的位置信息

## 跨平台与降级

桌面驱动后端的 OS 矩阵由 `scripts/install_cua_driver.py` 决定:
- macOS arm64 / x86_64 → Swift `cua-driver`
- Linux x86_64 → `cua-driver-rs`
- Windows x86_64 → `cua-driver-rs` (PowerShell 安装)
- Linux aarch64 → 无预编译 → 自动 web-only

降级到 `mode: "web-only"` 的触发条件,只有这三种:
1. 产品官网没出当前主机 OS 的安装包(如 ProductiveKitty 没 Linux 版,而你在 Linux 主机上)
2. 当前主机平台没有 cua-driver 预编译(Linux aarch64)
3. 应用安装/启动失败 / 反复闪退

降级时:
- `metadata.json.mode = "web-only"`
- 在 `metadata.json.warnings[]` 加一条形如 `"web-only: no macos package found at <url>"`
- 报告头的元信息表"模式"列填 `web-only`,并在表下用一句话说明降级原因
- 报告其他部分照常写,只是 §1 仅基于官网 + 浏览器截图,长度可能比 full 模式短

## 失败处理与升级

- **AX 树为空 / Electron canvas / WebView2 应用** → 按 [cua-driver SKILL](../cua-driver/SKILL.md) 的 escalation 一节处理(检测 webview、必要时 vision 兜底)。本 skill 不复述这些规则
- **应用启动闪退** → 截屏崩溃对话框,记录系统日志路径(macOS:`~/Library/Logs/DiagnosticReports/`,Linux:`journalctl --user-unit`),`§1.3` 标"该界面因崩溃未能采集",降级到尽量多的可达界面
- **登录墙** → 不绕过、不创建账号。能采集的:首页、定价、文档、博客、Changelog;`metadata.json.warnings[]` 加 `"login-required: feature pages not analyzed"`,报告头注明"未登录态分析"
- **单步 30s 超时** — 跳过该步,`metadata.json.warnings[]` 记录,继续下一步;不要无限等
- **下载/安装权限受阻**(/Applications 不可写、SIP 卡在 quarantine 等)→ 记录原因,降级 web-only

## 风格守则

- **报告全程中文**(简体)
- **不夸张**:不用"完美"、"惊艳"、"颠覆"。事实陈述 + 一两句评价就够
- **不和稀泥**:产品有问题就写,但要落到具体细节,不要泛泛批评
- **可证伪**:每个评价指向截图或官网原文。读者扫一眼能 follow back to evidence

## 与 cua-driver skill 的关系

本 skill 负责"分析什么、产出什么"。所有"如何驱动桌面端"的具体规则(snapshot 不变量、no-foreground 契约、坐标系、escalation 阶梯、平台差异)都在 [.claude/skills/cua-driver/SKILL.md](../cua-driver/SKILL.md)。**不要在这里复述,只在工作中遵守**。
