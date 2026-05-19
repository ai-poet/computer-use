---
name: product-analyzer
description: 给定产品名和官网 URL,产出含三个强制章节(产品逻辑/UIUX/官网描述)的中文 Markdown 产品分析报告与配套截图文件夹。优先驱动桌面端;桌面端不可用时自动降级 web-only。触发方式:scripts/analyze_product.py 调用,或对话中"分析/拆解/评测/调研 这个产品 https://..."类请求且包含 URL。
---

# product-analyzer

把"分析一个新产品"这件事固化成一条可重复流水线。每次跑都产出一份结构稳定的报告 + 一组带命名规则的截图,方便对外提交、归档、跨产品横向比较。

## 工作模式

- **完整模式 (full)**:抓官网 → 找出当前主机能用的安装包 → 装好驱动器(`scripts/install_cua_driver.py`)→ 启动产品 → 用 **cua-driver** 操作主要界面 → 批量截图 → 整合写报告。**仅 `runtime=host` 单任务**走此路径。
- **沙箱完整模式 (sandbox-full)**:**仅批量** (`runtime=sandbox-local` / `sandbox-cloud`)。用 Cua Sandbox SDK 在沙盒内完成分析;`metadata.mode` 为 `sandbox-full`。单任务**不得**使用。
- **Android 模式 (android)**:**仅沙盒批量**且 `android.enabled=true` 时的增强项;host 单任务不跑 Android 沙盒。
- **网页模式 (web-only)**:仅基于官网信息 + 浏览器截图。仅在桌面驱动不可达时启用 — 见下文"跨平台与降级"

## 运行时分流(编排器契约,必读)

Python 编排器通过 prompt 里的 `runtime` 与 `metadata.json` 区分路径。**不要自行改用沙盒或改用 cua-driver。**

| 入口 | `runtime` | 驱动方式 | 禁止 |
|------|-----------|----------|------|
| **单任务**:菜单 1、位置参数、`python scripts/analyze_product.py "名" "URL"` | **`host`** | 本机 **cua-driver** + 父 shell `curl`(可走代理) | `import cua`、`Sandbox.ephemeral`、Docker/Lume/QEMU 沙盒、读「Sandbox 运行合约」当操作手册 |
| **批量**: `--batch queue.json` | **`sandbox-local`** 或 **`sandbox-cloud`** | **逐步**控制沙盒(见「沙盒控制三阶段」);本地用 `sandbox_ctl`,云端用 Cua MCP | cua-driver、host 浏览器/GUI、整段 `asyncio` 分析脚本 |

**判定**:prompt 里 `runtime:host` → 只走 [Host 单任务](#host-单任务-runtimehost)。`runtime:sandbox-local` / `sandbox-cloud` → 只走 [Sandbox 运行合约](#sandbox-运行合约)。`batch.parallel:true` 仅批量出现。

## 输入

由调用方(脚本或对话)提供:
- `product_name` — 必填,展示用原文(允许中文 / 大小写混排)
- `url` — 必填,产品官网 https URL
- `download_url` — 可选,直接指向当前主机能用的安装包(.dmg / .exe / .deb 等)。**优先级最高**,有它就跳过"在官网找下载链接"步骤
- `output_dir` — 调用方已经建好的绝对路径,形如 `<repo>/reports/<slug>-YYYY-MM-DD[-N]/`,本 skill 把所有产物写进去
- `runtime` — `host`、`sandbox-local` 或 `sandbox-cloud`。`host` 使用当前主机 + cua-driver;`sandbox-local` / `sandbox-cloud` 必须使用 Cua Sandbox SDK,且不得操作 host GUI
- `sandbox.image` — `auto` / `linux` / `macos` / `windows`,仅 sandbox runtime 有效
- `sandbox.local` — `true` 为本地 Docker/Lume/QEMU(批量默认);`false` 为 Cua Cloud(仅当调用方显式 `--sandbox cloud` 时,需 `CUA_API_KEY` 注入 env,**不要**写入 metadata.json)
- `android.enabled` — 是否检测并尝试 Android APK 路径
- `batch.parallel` — 是否为批量队列中的并行 worker(`true` 时必读下文「批量并行」)

编排器还可能通过**环境变量**注入(供你读 skill 时对照,勿写入 metadata):`ANALYZER_LINUX_CONTAINER_IMAGE`、`ANALYZER_LINUX_DOCKER_PLATFORM`、`ANALYZER_PYTHON_VERSION_MIN`、`ANALYZER_CONDA_ENV`、`ANALYZER_BATCH_PARALLEL`、`CUA_API_KEY`(仅云端)。

## 输出布局

```
<output_dir>/
  report.md                     # 报告主体
  metadata.json                 # 机器可读元数据
  downloads/                    # 下载的安装包 / APK
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
  "runtime": "host",
  "sandbox": {"image": null, "local": true, "mode": "local", "name": null, "api_url": null},
  "android": {
    "enabled": false,
    "apk_url": null,
    "apk_file": null,
    "package_name": null,
    "mode": null
  },
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
- `source ∈ {web, app, android}` — `web` 表示浏览器内截图,`app` 表示桌面应用窗口截图,`android` 表示 Android 沙箱内截图
- `view` — 短 kebab-case,语义化:`homepage / pricing / faq / main / settings / new-task / focus-mode / report-detail` 等

每张截图都必须在 `report.md` 里以相对路径(`screenshots/NN_*.png`)出现,且在**附录 A 截图索引**里有一行说明。没引用过的截图删掉,不要留弃图。

## Canonical loop(7 步,固定顺序)

调用方进入时,`output_dir` 已建好、`metadata.json` 雏形已写。这 skill 接管后续。

**两条铁律(优先级高于任何步骤细节)**:

1. **找下载链接 = 真实操作浏览器**,不是只跑 curl + grep。`curl + grep` 只是快速线索,**不是判定 web-only 的依据**。`grep` 没出结果时**必须**继续打开浏览器,真实点击导航到"下载"/"Download"/"产品"/"Pricing"等页面,把官网走一遍 — 很多产品的下载入口藏在二级菜单、弹窗、用户登录后的页面、或者由 JS 动态注入的 CDN URL 里,只看初始 HTML 必然漏。host runtime 下所有这些点击都通过 cua-driver,严守 no-foreground 契约;sandbox-local runtime 下通过 sandbox 的 browser / mouse / keyboard / screenshot 能力完成

2. **完整模式下,桌面应用是必做项,不能因为网页好玩就省略**:有安装包就**必须**装、启动、用 cua-driver 把客户端主要功能走一遍。网页可以同时深入探索(多挖一些定价、文档、博客都没问题),但 web 段做得多≠ app 段可以做得少。app 段是 §1 报告的主要素材来源,**任何"应用我看了官网就大概知道了"或"应用启动太麻烦先跳过"的偷懒都不行**。只有 step 3 全部失败、确实下不到安装包,才进入 web-only 模式,把网页当主战场

- `runtime=host` 时:只读 [Host 单任务](#host-单任务-runtimehost),**不要**读「Sandbox 运行合约」。
- `runtime` 为 `sandbox-local` 或 `sandbox-cloud` 时:必须先读 [Sandbox 运行合约](#sandbox-运行合约),再执行 canonical loop。

### 7 步详细

1. **TodoWrite 建 7 个 todos**:`抓取官网` → `定位下载链接` → `安装/启动应用` → `驱动目标(应用 + 可选网页)` → `批量截图` → `整合报告` → `补齐 metadata.json`。每步开始前 `in_progress`,完成转 `completed`

2. **抓取官网原始信息(线索 + 入门体验)** —
   - **host**:父 shell `curl -fsSL`(可走代理)+ Python 剥 HTML;用 **cua-driver** 打开浏览器截首页 `01_web_homepage.png`。
   - **sandbox**:用 `sandbox_ctl step shell` 在沙盒内 `curl`;浏览器与截图用 `sandbox_ctl step screenshot` / `click` / `type`。禁止 host 父 shell 捷径。
   - 可顺带浏览定价/文档页 — 不能替代桌面端体验。

3. **定位下载链接(分两层:静态 grep + 真实浏览)** —
   优先用调用方传入的 `download_url`。否则:

   **3.1 静态扫描(快速、便宜,但**不**充分)**:
   - 全文 URL 正则:`grep -oE 'https?://[^"<>\s]+\.(dmg|exe|pkg|msi|deb|rpm|appimage|tar\.gz|tar\.xz|zip|apk)([?#][^"<>\s]*)?' homepage.html | sort -u`
   - 关键字定位跳转页:grep `download` / `下载` / `releases` / `\.app[^a-z]` / `apk` / `android` / `google play`
   - storage bucket 列表:静态命中 URL 指向公开目录(MinIO / S3 ListBucketResult XML)就 curl 那个根目录

   **3.2 浏览器实操(必须做,不可跳过 — 除非 3.1 已经命中且按主机 OS 选定了正确架构)**:
   通过当前 runtime 的真实浏览器操作能力(host 用 cua-driver,sandbox-local 用 sandbox SDK):
   - 打开浏览器,定位到官网,**真实点击**导航栏里所有看起来相关的入口:`Download`/`下载`/`Get the App`/`Install`/`Pricing`/`Get Started`/`Try Free`/`产品`等
   - 若 `android.enabled=true`,额外点击/检查 `Android` / `APK` / `Mobile` / `Get it on Android` / `Google Play` 入口
   - 每个候选页都截图存档(`screenshots/02_web_<view>.png` 形式)
   - 滚到底部,看 footer 有没有 `Mac` / `Windows` / `Linux` / `Android` 的小图标按钮
   - 点击平台切换器(很多站点会先显示访客 OS 推荐)、关掉登录弹窗、关掉 cookie 横幅,继续找
   - 任何 a11y 树为空 / Electron canvas 的页面按 [cua-driver SKILL](../cua-driver/SKILL.md) 的 escalation 阶梯升级到 vision

   **3.3 命中后选最匹配的安装包**:
   - `darwin/arm64` 优先 `*arm64*.dmg`、`*aarch64*.dmg`,否则 `darwin/x86_64` 用 `*x64*.dmg`、`*intel*.dmg`、不带架构标的 `.dmg`
   - `linux/x86_64` 优先 `*x86_64*.AppImage`/`.deb`/`.tar.gz`
   - `windows/x86_64` 选 `*.exe` / `*.msi` / `Setup-*.exe`
   - Android APK 只接受官网直链或官方 release asset。Google Play 只记录证据,不绕登录、不抓第三方镜像、不从非官方 APK 镜像站下载
   - 找到 APK 时写入 `metadata.android.apk_url`;下载到 `<output_dir>/downloads/`,写入 `metadata.android.apk_file`

   **3.4 全部失败才标 web-only**,并在 `metadata.warnings[]` 写明:
   - 静态 grep 试过哪些
   - 浏览器实际访问/点击过哪些页面(列出页面 URL,证明做了真实 hunt)
   - 最终结论(如"产品仅有 Web 版,无桌面端安装包")

4. **安装/启动应用(仅当 step 3 命中)** —
   - host runtime:用 `scripts/install_cua_driver.py` 确保桌面驱动器已装(预检过,但 sanity-check 一次 `which cua-driver`)。下载产品安装包到 `<output_dir>/downloads/`,按平台用对应方式安装(macOS:`hdiutil attach` + `cp -R` + `xattr -d com.apple.quarantine`;Linux:`dpkg -i` 或 `chmod +x` AppImage;Windows:`start /wait` MSI)。**严格遵循 [cua-driver SKILL](../cua-driver/SKILL.md) 的 no-foreground 契约**
   - sandbox-local / sandbox-cloud runtime:沙盒已在 **bootstrap** 阶段创建;在沙盒内用 `sandbox_ctl step shell` 下载/安装/启动,GUI 用 `sandbox_ctl step` 单步操作;截图写入 `<output_dir>/screenshots/`
   - Android APK:若 `metadata.android.apk_url` 已填,额外创建 `Sandbox.ephemeral(Image.android(), local=<metadata.sandbox.local>)`,在 Android sandbox 内下载或传入 APK,用 `adb install` / sandbox shell 安装,通过 `cmd package resolve-activity` / `monkey` / 启动 intent 获取并启动包名,写入 `metadata.android.package_name` 与 `metadata.android.mode`

5. **驱动目标** —

   **5.A 完整模式(step 3 命中):桌面应用必做,官网可选深挖** —
   - **桌面端必做**:启动产品,**主要功能挨个走一遍**。每打开一个新界面就 snapshot + screenshot。覆盖到的典型界面:启动页 / 主功能页 / 创建/新建流 / 设置 / 偏好 / 帮助 / 关于 / 错误状态(故意触发一次)。host runtime 的 a11y/click/type/screenshot 必须通过 cua-driver;sandbox-local runtime 必须通过 sandbox SDK。app 段截图至少 4-8 张,**这是 §1 报告的主要素材来源**
   - **官网可选深挖**:在保证桌面端体验完整的前提下,可以继续看定价 / 文档 / 博客 / FAQ 等,补充 §3 官网描述的素材。web 段截图数量没有上限 — 但**绝对不能用网页截图替代应用截图**,也不能因为网页内容多就缩水应用体验

   **5.B 网页模式(step 3 全部失败,降级 web-only):在浏览器里完整体验** — 这时网页就是产品本体,用当前 runtime 的浏览器操作能力逐页深入:
   - 首页(滚到底,各 section 各截一张)
   - 主功能页 / 演示页(能交互的部分都试一下:输入、提交、播放、切 tab)
   - 定价 / Pricing(各档位都点开)
   - 文档 / 帮助 / Changelog
   - FAQ / 博客头版 / 关于
   - 登录入口(只看不操作账号)
   - 国际化:有 `EN/中文/...` 切换器就切一遍各看一张
   - 错误态:故意输入错的、点不该点的,看交互反馈
   - web 段至少 6-10 张图

   两种模式都要保证 §1 报告章节有足够多的"界面"可写。

   **5.C Android 增强路径(找到 APK 时追加执行)** —
   - 在 Android sandbox 中启动应用,截图保存为 `screenshots/NN_android_<view>.png`
   - 至少覆盖启动页、主界面、权限弹窗、登录墙、设置/关于、错误态中可达的部分
   - 不创建账号、不绕过登录、不授予高危权限;权限弹窗只记录默认文案和可见选项
   - 如果 APK 安装失败、启动闪退或 Android runtime 缺失,写入 `metadata.android.mode = "failed"` 和 `metadata.warnings[]`,报告里只引用已获得的证据

6. **批量截图** — 整理 screenshots/,删冗余、保留代表性的、确保命名连续(允许跳号)

7. **整合报告** — 拷贝 [REPORT_TEMPLATE.md](REPORT_TEMPLATE.md) 到 `<output_dir>/report.md`,逐节填写。可选章节(定价 / 目标用户 / 同类对比 / 优劣势)**只在有证据时保留,否则整段删除**。所有"评价"型陈述必须可被截图或官网原文证实

每步结束 TodoWrite 标 `completed`,下一步标 `in_progress`,然后开始下一步。

## Host 单任务 (`runtime=host`)

当 prompt / `metadata.json` 里 **`runtime` 为 `host`** 时(默认单任务路径):

1. **禁止沙盒**:不得 `from cua import Sandbox`、不得 `Sandbox.ephemeral`、不得拉 Docker/Lume 沙盒。即使本机已装 Docker/conda,也**不要**改用沙盒完成分析。
2. **桌面与浏览器**:一律 [cua-driver SKILL](../cua-driver/SKILL.md)(`launch_app`、`get_window_state`、`element_index` 点击、截图),严守 **no-foreground**。
3. **官网 curl**:可在 **host 父 shell** 执行(可走用户代理),用于 HTML 线索;真实点击导航仍走 cua-driver 浏览器。
4. **安装包**:下载到 `<output_dir>/downloads/`,在 **host** 安装(macOS/Linux/Windows 常规方式),用 cua-driver 驱动已安装应用。
5. **`metadata.mode`**:成功时写 `full`,降级写 `web-only` — **不要**写 `sandbox-full`。

## Sandbox 运行合约

**仅当** `runtime ∈ {sandbox-local, sandbox-cloud}`(批量 `--batch`)时,本节才是权威沙盒说明。`runtime=host` 时**跳过本节**。

### 沙盒控制三阶段(与 host cua-driver 逐步对齐)

| 阶段 | 做什么 | 禁止 |
|------|--------|------|
| **1. bootstrap(一次)** | 创建沙盒、写 `<output_dir>/sandbox.json`、可选启动浏览器 | 在 bootstrap 里 curl 全站、装包、写 `report.md` |
| **2. step loop(每步)** | 截图 → 看图 → 单步 click/type/shell → 再截图 | 单个 `asyncio.run()` 跑完 canonical loop step 2–6 |
| **3. teardown(一次)** | 销毁沙盒;编排器也可能自动 teardown | 泄漏 Docker 容器 / Cloud VM |

**observe–act 铁律**:每次 GUI 操作前后各一张截图进 `screenshots/`;路径写进当轮推理,再决定下一步坐标。

#### 反模式(明确禁止)

- 写一个 `analyze_*.py` / `run_analysis.py`,在里边 `async with Sandbox.ephemeral` 跑完全部分析。
- bootstrap 脚本里包含 step 3–7 的业务逻辑。
- 用 host 父 shell `curl` 代替沙盒内证据(`ANALYZER_BATCH_PARALLEL=1` 时)。

#### 本地 (`sandbox-local`) — 优先 `sandbox_ctl`

编排器提供薄 CLI(conda 环境 `python`,勿用系统 3.9):

```bash
conda activate computer-use-py312   # 或 $ANALYZER_CONDA_ENV
REPO=...                            # 仓库根目录

# 1) bootstrap — 创建 named sandbox,写 sandbox.json
python "$REPO/scripts/sandbox_ctl.py" bootstrap "$OUTPUT_DIR" [--open-browser]

# 2) step loop — 每步一条命令(示例)
python "$REPO/scripts/sandbox_ctl.py" step screenshot "$OUTPUT_DIR" \
  --out screenshots/01_web_homepage.png
python "$REPO/scripts/sandbox_ctl.py" step shell "$OUTPUT_DIR" -- \
  curl -fsSL -o /tmp/home.html 'https://example.com'
python "$REPO/scripts/sandbox_ctl.py" step click "$OUTPUT_DIR" 640 400
python "$REPO/scripts/sandbox_ctl.py" step type "$OUTPUT_DIR" 'hello'
python "$REPO/scripts/sandbox_ctl.py" step key "$OUTPUT_DIR" enter

# 3) teardown
python "$REPO/scripts/sandbox_ctl.py" teardown "$OUTPUT_DIR"
```

`<output_dir>/sandbox.json` 契约( bootstrap 写入,勿手改):

```json
{
  "name": "analyzer-babbel-2026-05-19",
  "provider": "docker",
  "api_url": "http://127.0.0.1:PORT",
  "image": "trycua/cua-xfce:latest",
  "platform": "linux/amd64",
  "local": true
}
```

- 使用 **`Sandbox.create(..., ephemeral=False, name=...)`**,以便 `~/.cua/sandboxes/` 有状态;**不要**用 `Sandbox.ephemeral` 做 batch 主沙盒。
- **备选**:`cua do switch docker <sandbox.json.name>` 后 `cua do screenshot` / `click`(与 `sandbox_ctl` 二选一;**优先 `sandbox_ctl`**,不依赖 Claude 记 port)。
- `sandbox_ctl status "$OUTPUT_DIR"` 排障。

#### 云端 (`sandbox-cloud`) — 优先 Cua MCP

编排器会为 worker 注入 `claude --mcp-config`( `cua serve-mcp` )。逐步使用:

- `computer_screenshot` / `computer_click` / `computer_type` / `computer_shell` 等
- **禁止**用 host Bash 操作沙盒 GUI
- MCP 返回的截图若未自动落盘,**必须** `Write` 到 `<output_dir>/screenshots/NN_*.png` 再读图分析
- 仍可用 `sandbox_ctl bootstrap` + `step`(cloud) 作 MCP 不可用时的降级

**不要**使用 `ComputerAgent(tools=[sb])` 嵌套 agent — 与当前 `claude --print` 流水线重复。

### 总原则

1. **操作系统级工作只在沙盒内**。**禁止** cua-driver、host `open`/`osascript`、本机浏览器/桌面 GUI。
2. **host 仅**:调用 `sandbox_ctl` / MCP / 读写 `<output_dir>` 产物。
3. **每个产品独立 sandbox**;禁止复用其它 `reports/` 任务的连接。

### Host 侧 Python / CLI

- Cua Sandbox SDK **仅支持 Python 3.12 或 3.13**;`sandbox_ctl` 与 `import cua` 必须用 conda 环境(读 `ANALYZER_CONDA_ENV`,默认 `computer-use-py312`)。
- 批量预检要求 `cua` CLI 在 PATH(`cua --version`)。
- 沙盒**内** shell 用容器内 `python3`(剥 HTML 等);与 host SDK 版本无关。

### 批量并行(`batch.parallel=true` 或 `ANALYZER_BATCH_PARALLEL=1`)

- 独立 worker;官网与 GUI 证据必须来自沙盒。
- 除读写当前 `<output_dir>` 外,不得把 host 当分析环境。

### 镜像

| `sandbox.image` | 本地 | 说明 |
|-----------------|------|------|
| `linux` | `trycua/cua-xfce:latest` + `linux/amd64` | `sandbox_ctl bootstrap` 默认 |
| `macos` | Lume | bootstrap 按 image 选运行时(若未实现则 warnings) |
| `windows` | QEMU Docker | 同上 |
| `auto` | 优先 linux 容器做网页 | |

- 读 `ANALYZER_LINUX_CONTAINER_IMAGE` / `ANALYZER_LINUX_DOCKER_PLATFORM`。
- 云端:由 `CUA_API_KEY` 注入;**勿写入 metadata**。

### SDK 整脚本示例(smoke/CI 专用,非 batch agent 默认)

[`tests/sandbox/linux_smoke.py`](../../tests/sandbox/linux_smoke.py) 用 `Sandbox.ephemeral` 验证链路 — **不要**照抄到产品分析 Bash 里。

### Android APK(可选)

- 仅 `android.enabled=true` 或找到 APK 时;**独立** Android sandbox(`sandbox_ctl` 或 SDK),截图 `NN_android_*.png`。
- 镜像 **`trycua/cua-qemu-android:latest`**。

### 沙盒内 GUI / 网页

- bootstrap 后 `--open-browser` 或 `step shell` 启动 Chromium/Firefox。
- **坐标级**自动化;每步 `step screenshot` 落盘。
- 复杂 SPA / 登录墙:记入 `warnings[]`,勿绕过登录。

## 报告模板要求

参见 [REPORT_TEMPLATE.md](REPORT_TEMPLATE.md)。要点:

- **必有章节(顺序不能变)**:`总定位` → `界面清单` → `各界面功能与评价` → `UI/UX` → `官网描述` → `附录 A 截图索引`
- **可选章节**(`定价 / 目标用户 / 同类对比 / 优劣势小结`):有证据才写,无则整段删,**不要留"信息不足"占位**
- **每个评价必须可证伪**:不写"流畅"、"美观",写"启动到首屏约 0.8s,无加载动画"或"主 CTA 用紫色填充按钮位于首屏右下,与背景对比度满足 WCAG AA"
- **官网原文用引号引用**(不要意译),节标题旁标"原文锚:首页 H1"之类的位置信息

## 跨平台与降级

host runtime 的桌面驱动后端 OS 矩阵由 `scripts/install_cua_driver.py` 决定:
- macOS arm64 / x86_64 → Swift `cua-driver`
- Linux x86_64 → `cua-driver-rs`
- Windows x86_64 → `cua-driver-rs` (PowerShell 安装)
- Linux aarch64 → 无预编译 → 自动 web-only

sandbox-local runtime 的桌面/Android 矩阵由 Cua Sandbox SDK 和本地运行时决定:
- Linux sandbox → Docker
- macOS sandbox → Lume
- Windows sandbox → QEMU
- Android sandbox → Android SDK(emulator + platform-tools)或 QEMU

sandbox-cloud runtime 由 Cua Cloud 托管 VM/容器;`sandbox.image` 选择 linux / macos / windows。不需要本机 Docker/Lume 预检,但需要有效的 `CUA_API_KEY`(已由 orchestrator 注入,勿写入 metadata)。

降级到 `mode: "web-only"` 的触发条件,只有这三种:
1. 产品官网没出当前主机 OS 的安装包(如 ProductiveKitty 没 Linux 版,而你在 Linux 主机上)
2. 当前主机平台没有 cua-driver 预编译(Linux aarch64)
3. 应用安装/启动失败 / 反复闪退

降级时:
- `metadata.json.mode = "web-only"`
- batch sandbox 成功驱动桌面端时 `metadata.json.mode = "sandbox-full"`;找到并成功体验 APK 时 `metadata.android.mode = "android"`
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

## 与 cua-driver / Cua Sandbox SDK 的关系

本 skill 负责"分析什么、产出什么"。host runtime 下,所有"如何驱动桌面端"的具体规则(snapshot 不变量、no-foreground 契约、坐标系、escalation 阶梯、平台差异)都在 [.claude/skills/cua-driver/SKILL.md](../cua-driver/SKILL.md)。**不要在这里复述,只在工作中遵守**。

sandbox-local / sandbox-cloud runtime 下,沙盒操作规则以**本 skill「Sandbox 运行合约」**为准(不在 prompt 里重复)。host runtime 下桌面驱动仍以 [cua-driver SKILL](../cua-driver/SKILL.md) 为准。
