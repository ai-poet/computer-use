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

调用方进入时,`output_dir` 已建好、`metadata.json` 雏形已写。这 skill 接管后续:

1. **TodoWrite 建 7 个 todos**:`抓取官网` → `定位下载链接` → `安装/启动应用` → `驱动应用界面` → `批量截图` → `整合报告` → `补齐 metadata.json`。每步开始前更新对应 item 为 `in_progress`,完成转 `completed`。这是用户看进度的主要凭据
2. **抓取官网** — 用 `curl -fsSL` 拿 HTML(走父 shell 代理),用 Python 把 `<script>` / `<style>` 剥掉提取纯文本。同时打开浏览器(macOS `open -a "Google Chrome" <url>`,Linux `xdg-open`,Windows `start`)做现场截图;web 段截图至少包含首页全景
3. **定位下载链接** — 优先用调用方传入的 `download_url`。否则按以下顺序穷举,**任一命中都视为已找到**,不要在第一种没结果就早退判 web-only:
   - **a. 全文 URL 扫描**:`grep -oE 'https?://[^"<>\s]+\.(dmg|exe|pkg|msi|deb|rpm|appimage|tar\.gz|tar\.xz|zip)([?#][^"<>\s]*)?' homepage.html | sort -u` — 这条会同时抓到 `<a href="...dmg">`、`<source src=...>` 以及 JS 里硬编码的 CDN URL(很多产品把安装包放在 `file.<vendor>.com` / `dl.<vendor>.com` / 各家 OSS / S3 / R2 上,而不是同站点资源,只看 a 标签会漏)
   - **b. 关键字定位跳转页**:还没结果就 grep `download` / `下载` / `releases` / `\.app[^a-z]` 之类的锚文本,跟过去再扫一次
   - **c. 站点目录列表**:如果 step a 抓到的 URL 指向某个 storage bucket 根路径或公开目录(典型如 MinIO / S3 ListBucketResult XML),`curl` 那个根目录,再列一次资源
   - **d. 同源资源探测**:取 step a 的所有 host,试 `https://<host>/latest`、`/download`、`/releases/latest` 等约定俗成路径
   - 命中后,**按当前主机 OS + arch 选最匹配的**:`darwin/arm64` 优先 `*arm64*.dmg`、`*aarch64*.dmg`,否则 `darwin/x86_64` 用 `*x64*.dmg`、`*intel*.dmg`、不带架构标的 `.dmg`;`linux/x86_64` 优先 `*x86_64*.AppImage`/`.deb`/`.tar.gz`;`windows/x86_64` 选 `*.exe` / `*.msi` / Setup-*.exe
   - 全部 fallback 都空才标记 web-only,**并在 metadata.warnings[] 里写明已尝试的查找方式**(避免事后被怀疑没认真找)
4. **安装/启动应用** — 用 `scripts/install_cua_driver.py` 确保桌面驱动器已装(Python 脚本已经预检过,但这里再 sanity-check 一次 `which cua-driver`)。下载产品安装包到临时目录,按平台用对应方式安装(macOS 走 `hdiutil attach` + `cp -R` + `xattr -d com.apple.quarantine`;Linux 走 `dpkg -i` 或 `chmod +x` AppImage;Windows 走 `start /wait` MSI)。**严格遵循 [cua-driver SKILL](../cua-driver/SKILL.md) 里的 no-foreground 契约**:能用 `open -j` / `open -g` / `cua-driver launch` 不抢前台就这么做
5. **驱动应用界面** — 启动应用,主要功能挨个走一遍。**所有 a11y/click/type/screenshot 操作必须通过 cua-driver**,直接用 `screencapture` 或 `osascript activate` 是违约。每打开一个新界面就 snapshot + screenshot
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
