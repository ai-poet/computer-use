# computer-use

把"分析一款新产品"这件事做成一条 Python 脚本能调起来的可重复流水线。

输入:产品名 + 官网 URL  
输出:
- 一份结构稳定的简体中文 Markdown 分析报告(含三个强制章节:产品逻辑 / UI-UX / 官网描述)
- 一个按命名规则编排的截图文件夹
- 一份 `metadata.json` 元数据

执行过程对用户可见:Python 子进程调 `claude --output-format stream-json --verbose`,把 Claude Code 的全量事件流(thinking / 工具调用 / 工具返回 / 文本)实时透传到终端。

---

## 仓库结构

```
computer-use/
├── README.md
├── .gitignore
├── reports/                                     # 每次跑的产出在这里(已 .gitignore)
├── scripts/
│   ├── analyze_product.py                       # 入口 shim(只调 product_analyzer.main)
│   ├── install_cua_driver.py                    # 桌面驱动器安装(macOS=Swift,Linux/Win=Rust)
│   └── product_analyzer/                        # 实现包
│       ├── __init__.py                          # 曝露 main + 模块依赖图
│       ├── config.py                            # 路径常量 + ANSI 配色
│       ├── ui.py                                # log/err/prompt_str/Spinner
│       ├── renderer.py                          # stream-json → 终端美化
│       ├── preflight.py                         # detect_host/ensure_*
│       ├── tasks.py                             # slug/metadata/list_tasks/post_check
│       ├── prompts.py                           # build_prompt + build_resume_prompt
│       ├── claude_driver.py                     # ESC + spawn + run_claude
│       └── cli.py                               # argparse + cmd_new/cmd_resume
└── .claude/skills/
    ├── cua-driver/                              # 桌面自动化 skill(snapshot→act→verify)
    └── product-analyzer/                        # 本项目核心 skill
        ├── SKILL.md                             # 工作流规则
        └── REPORT_TEMPLATE.md                   # 中文报告骨架
```

模块依赖单向无环:`config → ui → renderer → preflight → tasks → prompts → claude_driver → cli`。

`scripts/analyze_product.py` 不做产品分析的判断,只负责前置工作(校验输入、建目录、调 claude)。所有产品分析的判断逻辑在 `.claude/skills/product-analyzer/SKILL.md` 里 — **改规则不需要改代码**。

---

## 准备

### 1. 装 Claude Code CLI

按官方文档装好 `claude` 命令:<https://docs.claude.com/en/docs/claude-code>

### 2. 装桌面驱动器

```bash
python3 scripts/install_cua_driver.py
```

脚本会自动按平台选后端:

| 主机 | 后端 | 备注 |
|---|---|---|
| macOS arm64 / x86_64 | Swift `cua-driver` | 官方版,放 `/Applications/CuaDriver.app` |
| Linux x86_64 | `cua-driver-rs` | Rust 端口 |
| Windows x86_64 | `cua-driver-rs` | 走 `install.ps1`,无需管理员 |
| Linux aarch64 | 不支持(无预编译) | 需要时自行源码编译 |

如果首次运行 `analyze_product.py` 时没装,它会自动调起这个脚本。

### 3. 网络代理(可选)

`install_cua_driver.py` 会从 GitHub 下安装包,如果你需要走代理,先在父 shell 设好:

```bash
export https_proxy=http://127.0.0.1:7897
export http_proxy=http://127.0.0.1:7897
export all_proxy=socks5://127.0.0.1:7897
```

---

## 用法

### 交互式(零参数)

```bash
python3 scripts/analyze_product.py
```

脚本依次问:
```
产品名: ProductiveKitty
官网 URL: https://productivekitty.masterwordai.com
下载链接(可选,直接回车跳过):
```

### 参数式(适合上层脚本/CI 集成)

```bash
# 两个必填位置参数
python3 scripts/analyze_product.py "ProductiveKitty" "https://productivekitty.masterwordai.com"

# 第三个位置参数(下载链接)可选,有就跳过"在官网找下载链接"那一步
python3 scripts/analyze_product.py "ProductiveKitty" \
  "https://productivekitty.masterwordai.com" \
  "https://file.masterwordai.com/zeabur/Desktop%20Cat-1.0.5-arm64.dmg"
```

任何缺失的位置参数会回退到 `input()` 询问。空字符串视为"未给"。

### 执行过程

启动后:

1. **预检**:`claude` CLI、cua-driver。后者没装就自动调起 `install_cua_driver.py`
2. **建目录**:`reports/<slug>-YYYY-MM-DD[-N]/screenshots/`
3. **写 metadata.json 雏形**(主机信息、起始时间)
4. **调 claude 子进程**,把任务 prompt 喂进去
5. **stream-json 事件流以 Claude Code 风格渲染** — 思考、工具调用、工具返回、文本、TodoWrite 列表都直接以彩色 + ☐/◐/☑ 的形式打到终端
6. 进程结束后做产物校验(报告和 metadata 是否就位),提示缺漏

权限模式默认 `bypassPermissions`,Claude Code 不会因每次工具调用打断流程问"允许吗?"。如果你想要交互式确认,改 `analyze_product.py` 里那行 `--permission-mode` 即可。

### ESC 中断 + 续跑

执行过程中如果发现 Claude 走偏了,**按 ESC** 暂停当前回合:

```
── 已暂停。
    输入补充指令后回车继续(空行则放弃,直接退出)。多行用反斜杠续行。
补充> 你刚才漏看了官网底部的 CDN 链接,重新扫一遍 https?://...\.dmg 再决定降级
```

回车后脚本用 `claude --resume <session_id>` 续跑,并把你的补充指令作为新一轮提示喂进去。Claude Code 会带着完整历史继续工作,不丢前面已经做的事。

空行则放弃续跑、清理退出。仅在 stdin 是真 tty(交互式终端)时启用,管道/CI 模式下自动禁用。

### 调试模式

把全量 stream-json 同时写到磁盘,用于事后排查:

```bash
ANALYZE_RAW_LOG=/tmp/raw.jsonl python3 scripts/analyze_product.py "ProductiveKitty" "https://productivekitty.masterwordai.com"
```

终端照常显示美化输出,`/tmp/raw.jsonl` 里是逐行 JSON,可以再丢给任何 stream-json 解析器复盘。

---

## 输出布局

```
reports/<slug>-2026-05-18/
├── report.md                       # 简体中文,3 强制章节按顺序
├── metadata.json                   # 机器可读元数据
└── screenshots/
    ├── 01_web_homepage.png         # NN_<source>_<view>.png
    ├── 02_web_pricing.png
    ├── 05_app_main.png
    └── ...
```

**slug 规则**:`kebab-case(ascii-fold(产品名))`,40 字符内。中文名走 fallback `product-<md5前6位>`。

**截图编号**:`NN_<source>_<view>.png`,`source ∈ {web, app}`,`NN` 单调递增允许跳号。每张图都在 `report.md` 里以相对路径出现,且在附录 A 截图索引里有一行说明。

**metadata.json**(由 Python 写雏形,Claude 在结束前补齐):
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
    {"file": "screenshots/01_web_homepage.png", "view": "web-homepage", "caption": "官网首页"}
  ],
  "warnings": []
}
```

`mode = "full"` 表示同时分析了官网与桌面端;`mode = "web-only"` 表示只看了官网(降级条件见下一节)。

**同日重跑**不会覆盖 — 自动追加 `-2`、`-3` 后缀。

---

## 报告模板

强制章节(顺序固定):

1. **总定位** — 这是什么、解决什么、面向谁
2. **界面清单** — 实际看到的所有主要界面,挂截图
3. **各界面功能与评价** — 具体到字段/按钮,可证伪
4. **UI/UX 风格和质量描述** — 视觉风格、信息密度、交互流畅度、文案、可访问性观察
5. **官网描述** — 官网原文摘录、关键卖点、与实际体验的差距
6. **附录 A 截图索引** — 表格列每张图

可选章节(定价 / 目标用户 / 同类对比 / 优劣势)**只有有证据时出现**,无则整段省略,不留"信息不足"占位。

完整骨架见 `.claude/skills/product-analyzer/REPORT_TEMPLATE.md`。

---

## 跨平台与降级

默认 **full 模式**:用 cua-driver(macOS) / cua-driver-rs(Linux/Windows)驱动桌面端。

仅在以下三种情况降级到 **web-only**:
1. 产品官网没出当前主机 OS 的安装包
2. 当前平台没有 cua-driver 预编译(Linux aarch64)
3. 应用安装/启动反复失败

降级时:
- `metadata.json.mode = "web-only"`,`warnings[]` 记录原因
- 报告头注明"本次为网页版分析,未驱动桌面端,因为 ..."
- 报告其他部分照常写,只是 §1 仅基于官网与浏览器截图

---

## 退出码

| 退出码 | 含义 |
|---|---|
| 0 | 成功 |
| 1 | 预检失败(claude / cua-driver 缺失,且自动安装失败)、用户中断 |
| 2 | claude 子进程异常退出 |
| 130 | Ctrl+C 中断 |

---

## 改规则不改代码

要调整分析逻辑、报告章节、截图命名规则、降级条件,改 `.claude/skills/product-analyzer/SKILL.md`(和它引用的 `REPORT_TEMPLATE.md`)即可,Python 脚本不用动。

要换桌面驱动器后端逻辑,改 `scripts/install_cua_driver.py`。

要改桌面自动化的具体打法(snapshot 不变量、no-foreground 契约、坐标系),改 `.claude/skills/cua-driver/SKILL.md`。

---

## 验证

随便挑一个有官网的产品试一次:

```bash
python3 scripts/analyze_product.py "ProductiveKitty" "https://productivekitty.masterwordai.com"
```

通过条件:
1. 终端实时看见 stream-json 事件流(thinking、各类 Tool 调用、Tool 返回都可见)
2. `reports/productivekitty-YYYY-MM-DD/report.md` 存在,3 个强制章节按顺序
3. `screenshots/` 至少 1 张 `web_*` + (有桌面端时)≥3 张 `app_*`
4. 每张截图都在 `report.md` 里被引用过
5. `metadata.json` 的 `finished_at` / `mode` 字段已被补齐
6. 重跑同输入 → 产出 `...-2026-05-18-2/` 而非覆盖
