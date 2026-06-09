# 回归任务规格（详细版）

> 用途：把本批已完成的工作反推成**实现无关**但**足够详细**的任务规格，交给另一个 coding agent 独立实现，再与本仓库现有产出做盲对比。
>
> 对应 git 区间：`6b11e97`（不含）→ `f8751cd`，18 个提交。
>
> 本版在保留「不写目录名/模块名/函数名」约束的同时，补充了：架构位置、接口契约、数据流、状态机、硬约束来源、验收清单和常见陷阱。让对比 agent 既能独立设计，又不会偏离核心不变量。

---

## 产品背景（所有任务包的共同上下文）

一条产品分析流水线：输入「产品名 + 官网 URL」，驱动一个 AI coding agent 子进程，让它访问官网、发现并体验客户端（桌面/移动）、截图，最终产出一份中文分析报告（`report.md` + `metadata.json` + `screenshots/`）。已有一个 CLI 编排层和一套「业务规则文档」（skill）。本批任务在此基础上扩展。

核心设计原则：**改规则不改代码**。所有"分析什么、产出什么、怎么降级"的判断都在业务规则文档里；Python 只做预检、建目录、起子进程、流式渲染、ESC 续跑。

下面拆成 5 个可独立交付的任务包。每个都能单独丢给对比 agent。

---

## 任务包 A：网页控制台前端

### 目标

做一个本地 Web 控制台，可视化这条流水线的运行。用户可以在浏览器里：看历史任务、发起新分析、批量导入、实时看子进程日志、读最终报告、管理凭据和邮箱配置。

### 在整体架构中的位置

- 前端是独立 SPA，通过 HTTP/WS 与后端通信。
- 后端是 FastAPI 服务，复用已有 CLI 的批量 worker 逻辑，但把「curses 控制台」替换为「WebSocket 流 + 浏览器 UI」。
- 前端不直接操作文件系统，所有状态来自后端 API。

### 后端 API 契约

后端至少暴露以下 REST + WebSocket 端点：

1. **任务列表**：`GET /api/runs`
   - 返回所有历史/进行中任务，含状态、进度、产品名、分类、起止时间。
   - 状态推导逻辑：
     - `completed`：metadata 有 `finished_at` 且 `report.md` ≥ 200 字节
     - `failed`：`workflow.steps` 中有任一步骤状态为 `failed`
     - `running`：有 `last_session_id` 或任一步骤 `in_progress`
     - `pending`：其它
   - 进度从 `workflow.steps` 计算：`(completed + skipped) / total * 100`

2. **创建单任务**：`POST /api/runs`
   - Body：产品名、URL、可选下载链接、sandbox 镜像、Android 开关、邮箱注册开关、邮箱覆盖参数
   - 后端同步创建输出目录、写 `metadata.json` 种子、写 `workflow.json`
   - 返回任务 ID 和 warnings
   - 实际分析在后台线程启动，避免阻塞 HTTP 响应

3. **创建批量任务**：`POST /api/runs/batch`
   - Body：任务行数组（每行含产品名/URL/下载链接/分类）、最大并发数、队列名、sandbox 镜像等
   - 后端为每一行预创建输出目录并写种子，然后启动后台线程跑批量 worker
   - 返回 batch_id 和任务 ID 列表

4. **任务详情**：`GET /api/runs/{run_id}`
   - 返回 metadata + workflow（含步骤列表和凭据请求）

5. **报告读取**：`GET /api/runs/{run_id}/report`
   - 返回 `report.md` 纯文本，不存在时返回空字符串

6. **截图列表与读取**：
   - `GET /api/runs/{run_id}/screenshots` 返回文件名数组
   - `GET /api/runs/{run_id}/screenshots/{name}` 返回图片文件

7. **步骤报告读取**：`GET /api/runs/{run_id}/steps/{step_file}`
   - 返回 `steps/` 下某个 markdown 文件内容
   - 必须做路径安全检查，防止 `../` 越界

8. **实时日志**：`WebSocket /api/runs/{run_id}/stream`
   - 服务端每秒轮询一次 `run.log` 和 `events.jsonl`
   - `run.log` 是子进程原始 stream-json，需要经过 renderer 转成终端行后发送
   - `events.jsonl` 是 hook 写入的结构化事件，直接作为 JSON 数组发送
   - 消息格式：`{source, chunk, lines?, events?}`
   - 客户端需要做行数/字符数上限截断（例如最多保留 1200 行、8 万字符、300 个事件）

9. **凭据提交**：`POST /api/runs/{run_id}/credentials`
   - Body：request_id、label、fields（键值对）
   - 写入系统钥匙串，并在 workflow 的 `credential_requests` 中标记该请求为 `submitted`

10. **设置读写**：
    - `GET /api/settings`：返回邮箱配置（非敏感字段明文，敏感字段只返回 `configured` 布尔）
    - `PUT /api/settings`：更新非敏感字段和敏感字段；敏感字段空字符串表示清除

11. **凭据列表与删除**：
    - `GET /api/credentials?product=...`：返回凭据索引（不含 secret 值）
    - `DELETE /api/credentials/{credential_id}`

### 前端页面结构

至少包含以下区域：

1. **左侧边栏（RunSidebar）**
   - 顶部品牌区
   - 新建任务表单：产品名、URL、下载链接、邮箱 provider/地址覆盖
   - 批量导入：JSON 文本粘贴或文件上传，解析为任务数组
   - 过滤器：按状态（全部/运行中/已完成/失败）、按分类、按搜索词
   - 任务列表：展示产品名、状态徽章、进度条、时间

2. **顶部栏（TopBar）**
   - 当前选中任务概览
   - 刷新按钮
   - 主题切换（明暗色）
   - 打开全局设置弹窗

3. **工作区（三栏或四栏布局）**
   - **WorkflowPanel**：展示 workflow 步骤状态（pending/in_progress/completed/skipped/failed）
   - **CredentialPanel**：
     - 若 workflow 有 pending 的 `credential_requests`，展示表单让用户输入字段
     - 展示该产品已保存的凭据列表（label、field_names、来源任务），可删除
   - **LogPanel**：
     - 终端风格流式展示，支持按 kind 过滤（all/thinking/tool/todo/result/hook/raw）
     - 自动滚动开关、复制、下载
     - WebSocket 连接状态指示
   - **ReportPanel**：
     - Markdown 渲染（含目录导航开关）
     - 报告下载、打印
     - 截图画廊（按 source 分组：web/app/android）

### 数据模型要点

- **Run**：id、product_name、url、status、started_at、finished_at、progress、queue.category
- **RunDetail**：metadata（完整 JSON）、workflow.steps、credential_requests
- **WorkflowStep**：id、title、file、status、summary
- **CredentialRequest**：id、service、reason、status、fields
- **TerminalLine**：id、source、kind、text、tone、indent、tool、status、raw、meta
- **Settings**：provider、mailosaur_server_id、mailosaur_server_domain、mailosaur_api_key_configured、imap_host、imap_port、imap_username、imap_password_configured、imap_folder、imap_ssl、email_address、alias_mode

### 前端工程约束

- 组件按「功能域」组织，避免单文件几百行。
- 统一 API 客户端层，不在组件里散写 `fetch`。
- 样式方案组件级隔离（例如 CSS Modules + Less 或 Tailwind）。
- 使用 Vite 构建，TypeScript + React。
- 开发模式支持 `npm run dev:all` 同时启动前端和后端。

### 启动脚本契约

- 前端 `npm run dev` 起 Vite 开发服务器（默认 5173）。
- 前端 `npm run dev:all` 通过 `concurrently` 同时启动后端（Python FastAPI）和前端。
- 后端启动脚本需要：
  - 自动探测可用的 Python 解释器（优先 conda/homebrew 的 python3）
  - 检查 `fastapi` 和 `uvicorn` 是否已安装
  - 启动 FastAPI server，默认绑定 `127.0.0.1:8765`
  - 正确转发 SIGINT/SIGTERM 给子进程

### 验收标准

- `npm run dev` 起得来，能连本地后端拉到任务列表。
- 大组件（日志面板、任务侧栏、报告面板）有明确的子组件/数据模型分离。
- WebSocket 日志流能实时更新，过滤生效。
- 创建任务后左侧列表自动刷新并选中新任务。
- 报告 Markdown 渲染正常，截图画廊能点击查看。
- 设置弹窗能保存/读取邮箱配置，敏感字段不回显明文。

### 常见陷阱

- 任务 ID 是输出目录的相对路径（例如 `category~slug-2026-06-09`），URL 编码时要注意 `/` 和 `~`。
- 截图文件名可能含 `_web_`、`_app_`、`_android_`，前端据此推断 source。
- WebSocket 重连：切换任务时要先关闭旧连接再开新连接。
- 凭据面板只在 `detail.workflow.credential_requests` 有 pending 项时显示表单。

---

## 任务包 B：邮箱验证码自动注册

### 目标

当目标产品需要注册才能体验时，让 agent 能自助完成「邮箱注册 + 收验证码/验证链接」。

### 在整体架构中的位置

- 这是一个**工具层**，被 agent 通过命令行调用（不是被 Python 直接 import 进工作流）。
- 与任务包 C（配置持久化）紧密配合：读取全局邮箱配置、写入注册产生的凭据。
- 与任务包 A（前端）的关系：前端设置弹窗编辑配置；前端凭据面板可手动补录账号。

### 支持的邮箱 Provider

必须支持两类 provider：

1. **Mailosaur**（推荐，一次性邮箱）
   - 配置项：api_key、server_id、server_domain（可选，默认 `{server_id}.mailosaur.net`）
   - 生成地址格式：`{run_local_part}@{server_domain}`

2. **IMAP 固定邮箱**（用户提供的真实测试邮箱）
   - 配置项：host、port、username、password、folder（默认 INBOX）、email_address、alias_mode
   - alias_mode 支持两种：
     - `plus`：生成 `local+pa-{suffix}@domain` 的 plus alias
     - `fixed`：直接使用 `email_address`

3. **Auto**（自动选择）
   - Mailosaur 配置完整 → 用 Mailosaur
   - 否则 IMAP 配置完整 → 用 IMAP
   - 否则 disabled

### CLI 接口设计

工具以命令行形式暴露给 agent，子命令包括：

- `status`：打印 provider 配置状态（是否启用、选中 provider、原因）
- `create-address --out-dir <dir> [--force-fixed]`：创建或复用测试邮箱地址
  - 如果 workflow 里已有 email_address 且不是 force_fixed，直接复用
  - 否则按 provider 生成新地址
  - 把结果写入 workflow.json 的 `registration` 块和 metadata.json
- `wait-code --out-dir <dir> --email <address> --timeout <seconds>`：轮询收件箱等验证码
  - 返回 `{"ok": true, "provider": ..., "source": ..., "code": "123456"}`
  - 超时返回 `{"ok": false, "error": "timeout"}`
- `wait-link --out-dir <dir> --email <address> --timeout <seconds>`：轮询等验证链接
  - 返回结构类似 wait-code，但字段是 `link` 而不是 `code`
- `mark-completed --out-dir <dir> [--used-for web|desktop|android]`：标记注册已完成
- `mark-failed --out-dir <dir> --reason <reason>`：标记注册失败
- `mark-skipped --out-dir <dir> --reason <reason>`：标记注册跳过

### 验证码/链接提取逻辑（必须可单元测试）

**验证码提取**：
- 先尝试从 Mailosaur message 的 `text.codes` / `html.codes` 读取（Mailosaur 已解析好的验证码）
- 回退到正则匹配 4-8 位连续数字
- 对候选数字打分：
  - 附近 50 字符内出现 "code/otp/verification/verify/验证码/校验码/验证/确认" 等关键词 +10 分
  - 与关键词的距离越近加分越多（最多 +80）
  - 验证码长度本身也加分（最多 +8）
- 返回得分最高的候选

**链接提取**：
- Mailosaur：优先取 `html.links[].href` 中的 HTTPS 链接
- 回退到正则匹配 `https://...`
- 对链接打分：
  - HTTPS 协议 +10 分
  - URL 中含 verify/verification/confirm/activate/auth +8 分
- 返回得分最高的链接

### 安全硬约束（不可违反）

- **禁止**：手机号注册、绕过 CAPTCHA、邀请码破解、付费绑卡、营销邀请。
- **禁止**：把验证码、密码、API key 写进 `report.md`、`metadata.json`、`workflow.json`、步骤报告或日志。
- 工具返回的 secrets **只能**出现在当前 tool call 的返回值中，由调用者（agent）立即使用。
- 日志和事件流必须经过脱敏（redaction），把 `code`、`otp`、`verification_code`、`password`、`api_key`、`token`、`MAILOSAUR_API_KEY`、`ANALYZER_IMAP_PASSWORD` 等替换为 `[REDACTED]`。

### 状态写入契约

每次调用都更新两个地方：

1. **workflow.json 的 `registration` 块**（较完整，供 agent 读取）：
   - `enabled`、`provider`、`email_address`、`status`、`alias_mode`、`failure_reason`、`used_for`

2. **metadata.json 的 `registration` 块**（只写非敏感字段，供前端展示）：
   - `enabled`、`provider`、`status`、`email_domain`、`alias_mode`、`failure_reason`、`used_for`
   - **不写** `email_address`

### 与 Skill 规则的衔接

业务规则文档需要新增/更新：
- 何时允许注册（仅当邮箱配置启用且目标产品明确需要账号时）
- 注册流程：创建地址 → 在页面填写 → 触发发送 → wait-code/wait-link → 填入 → 标记完成
- 注册失败时的降级策略（继续 web-only，记录 warning）
- 注册成功后立即把账号密码写入凭据存储（见任务包 C）

### 验收标准

- 有不依赖真实网络的单元测试覆盖：
  - 配置解析（auto 优先 Mailosaur、回退 IMAP、未配置 disabled）
  - 地址生成（plus alias 格式正确、force_fixed 生效）
  - 验证码提取（英文/中文文本、关键词加权）
  - 链接提取（HTTPS 优先、验证类 URL 加权）
  - 文本脱敏（code/api_key/password 被替换）
- CLI 各子命令 `--help` 能正常显示。
- 未配置时 `create-address` 返回 `ok=false` 而不是抛异常。

### 常见陷阱

- Mailosaur 的 `received_after` 参数需要是 naive datetime（不带时区）。
- IMAP 轮询要用 `SINCE` 筛选 + 收件人匹配，避免把历史邮件当成验证码。
- 收件人匹配要考虑 plus alias：目标地址是 `a+pa-xxx@b.com` 时，邮件的 `To` 可能只显示 `a@b.com`。
- 超时上限要 clamp 到合理范围（例如 1-180 秒），防止 agent 传过大值。

---

## 任务包 C：配置持久化 + 凭据安全存储

### 目标

让邮箱服务配置可持久化，让注册产生的账号凭据被安全保存、可跨同产品任务复用。

### 在整体架构中的位置

- 属于**全局基础设施**，被任务包 B（email_otp）和任务包 A（web 前端）共同使用。
- 位于依赖图最底层（settings 子包），不依赖任何业务包。
- 存储分两处：非敏感字段写 JSON 文件，敏感字段写操作系统钥匙串（keyring）。

### 配置分层与优先级

邮箱配置需要支持三层合并，优先级自高到低：

1. **任务级 overrides**（单次任务或前端表单传入）
2. **全局设置**（JSON 文件 + keyring）
3. **os.environ**（兜底）

合并后的结果以环境变量名的形式输出，直接喂给任务包 B 的配置解析器。

### 非敏感配置存储

- 存储位置：`~/.config/<app-name>/settings.json`（或 `$ANALYZER_CONFIG_DIR`）
- 字段：provider、mailosaur_server_id、mailosaur_server_domain、imap_host、imap_port、imap_username、imap_ssl、imap_folder、email_address、alias_mode
- `save_settings` 语义：
  - 值为 `None` 或空字符串 → 删除该字段
  - 未提供的 key → 保留原值
  - 其它 → 覆盖

### 敏感配置存储

- 使用 `keyring` 库存入操作系统钥匙串。
- Service name 统一（例如 `computer-use-product-analyzer`）。
- 字段：mailosaur_api_key、imap_password
- 每个敏感字段单独存一条 keyring 记录，key 带前缀区分（例如 `setting:mailosaur_api_key`）。
- `set_secret` 语义：
  - 值为 `None` 或空字符串 → 调用 `delete_password`
  - 其它 → 调用 `set_password`

### 凭据存储（Credential Store）

凭据是「注册成功后保存的账号密码」，与「邮箱配置」是不同概念。

**数据结构**：
- 每条凭据是一个 JSON 对象：`{label, fields, source_run, product, created_at}`
- 存入 keyring，key 是一个随机 UUID（`credential_id`）
- 同时维护一个 keyring 内的索引（index key），记录所有凭据的元数据

**索引条目**：
- `credential_id`、`label`、`source_run`、`product`、`field_names`（不含值）、`created_at`

**接口**：
- `store_credential(label, fields, source_run, product)` → 返回 `CredentialRef(credential_id, label)`
- `load_credential(credential_id)` → 返回完整 payload（含 secret fields）
- `list_credentials(product=None, source_run=None)` → 只返回索引（不含 secret）
- `find_credential(product=None, label=None)` → 返回最近一条匹配的完整 payload
- `delete_credential(credential_id)` → 从 keyring 删除，并从索引移除

### 安全硬约束

- secrets **不进版本库**、**不进报告**、**不在 API 响应里明文回传**给非必要场景。
- `list_credentials` 返回的条目只能包含 `field_names`，不能包含 `fields` 的值。
- 读取已存凭据与「创建新邮箱」是两个独立开关：
  - 配置关闭时仍可读旧凭据（`cred-get` / `cred-list` 可用）
  - 但不创建新测试邮箱（`create-address` 返回 not_configured）

### Web API 设计

- `GET /api/settings`：返回非敏感字段明文 + 敏感字段 `configured` 布尔
- `PUT /api/settings`：
  - 非敏感字段直接更新 JSON
  - 敏感字段：只处理请求中出现的 key；空字符串表示清除；未出现表示保持不变
- `GET /api/credentials?product=...`：返回凭据索引
- `DELETE /api/credentials/{credential_id}`
- `POST /api/runs/{run_id}/credentials`：前端手动提交凭据（见任务包 A）

### 与任务包 B 的衔接

任务包 B 提供以下 CLI 子命令来操作凭据：
- `cred-put --out-dir <dir> --label <label> --field key=value [--field ...]`
- `cred-list [--out-dir <dir>] [--all]`
- `cred-get --out-dir <dir> [--label <label>]`

`cred-put` 自动从 `metadata.json` 读取 `product_name` 作为 `product` 标签。
`cred-list` 默认只列出同 product 的凭据；`--all` 列出全部。
`cred-get` 默认返回同 product 最近一条凭据；可传 `--label` 过滤。

### 单元测试要求

- 用 fake keyring（内存字典）mock 掉真实 keyring。
- 用临时目录 mock 掉配置目录。
- 覆盖：
  - 非敏感字段保存/加载/删除
  - 敏感字段 roundtrip，且 `settings_status` 不回显明文
  - 三层优先级（overrides > 全局 > env）
  - `email_env_delta` 只含邮箱相关键，不含 PATH 等无关键
  - overrides blob 经环境变量传递后，子进程仍能正确还原优先级
  - 凭据存取隔离（A 产品的凭据 B 产品看不到）

### 验收标准

- 有 mock 掉真实安全存储和网络的单元测试，且全部通过。
- 前端设置弹窗保存后刷新，敏感字段显示「已配置」而不是明文。
- `cred-list` 的输出中不出现任何 password/token。
- 同 product 的后续任务可以通过 `cred-get` 复用凭据。

### 常见陷阱

- keyring 在某些 CI/无头环境会报错，需要 graceful fallback 或测试时 mock。
- 索引和实际凭据可能不一致（例如手动删了 keyring 里的某条但索引没更新），`list_credentials` 应该 tolerate 这种不一致。
- `effective_email_env` 的 `base_env` 默认是 `os.environ`，测试时要隔离。

---

## 任务包 D：Android 客户端分析能力

### 目标

当产品有 Android 客户端时，能在移动沙盒里安装 APK 并体验、截图。

### 在整体架构中的位置

- 属于 sandbox 层，与 Linux 桌面 sandbox 是**完全独立的第二套控制桥**。
- 依赖 Cua Sandbox SDK 的 `sb.mobile` 触控接口和 QEMU Android 镜像。
- 被 agent 通过 CLI 调用，也被批量流程通过环境变量和 prompt 参数间接启用。

### 核心不变量

1. **独立触控语义**：移动端有独立控制桥，不得复用桌面沙盒的 `click/scroll/type/key`。
2. **snapshot before AND after**：每次 `tap/swipe/type/key/shell` 前后都要截图。
3. **官方 APK 来源**：只用官网直链或官方 release asset；Google Play 只记录证据，不从第三方镜像下载。
4. **失败隔离**：Android 沙盒失败只影响 `metadata.android.mode`，不让整单失败。

### 镜像与运行时

- Android 镜像：`trycua/cua-qemu-android:latest`
- Apple Silicon / arm64 Mac 拉取时必须带 `--platform=linux/amd64`
- 本地运行时通过 Cua SDK：`Sandbox.create(Image.from_registry(...), name=..., local=True)`
- 使用**持久 sandbox**（方便断点、截图、清理），不要用 `Sandbox.ephemeral(...)` 做主流程

### CLI 控制桥接口

工具维护一个状态文件 `<out_dir>/android_sandbox.json`，包含：name、image、local、api_url、apk_path、install_with_image。

子命令：

- `bootstrap <out_dir> [--apk <path>] [--name <name>] [--install-with-image]`
  - 创建 Android sandbox
  - 若传 `--install-with-image`，则通过 `Image.from_registry(...).apk_install(apk_path)` 在镜像构建时安装 APK
  - 写 `android_sandbox.json` 和 metadata.android 块

- `install <out_dir> <apk_path>`
  - 连接已创建的 sandbox，执行 `adb install -r <apk_path>`
  - 用于 image builder 安装失败时的降级
  - 要求 APK 路径在 sandbox 内可见

- `screenshot <out_dir> --out <path>`
  - 调用 `sb.screenshot()`，写入 PNG
  - 检查文件大小 ≥ 1000 字节，否则视为失败

- `tap <out_dir> <x> <y>`
  - 调用 `sb.mobile.tap(x, y)`

- `swipe <out_dir> <x1> <y1> <x2> <y2> [--duration-ms 400]`
  - 调用 `sb.mobile.swipe(x1, y1, x2, y2, duration_ms=...)`

- `type <out_dir> <text>`
  - 调用 `sb.mobile.type_text(text)`

- `key <out_dir> <key>`
  - 支持 `back`、`home`、`enter`、`recents`
  - 其它值视为数字 keycode，调用 `sb.mobile.key(int(key))`

- `shell <out_dir> -c <command>`
  - 调用 `sb.shell.run(command)`
  - 仅作为降级，例如 `adb shell monkey -p com.example.app 1`

- `status <out_dir>`：打印 `android_sandbox.json`
- `teardown <out_dir>`：删除 sandbox 并移除状态文件

### 输出规范

- 截图保存到 `screenshots/NN_android_<view>.png`
- 必须在 `steps/05_android_client.md` 中记录：
  - APK 来源和文件路径
  - Android 沙盒启动/安装/运行结果
  - sandbox 名称、镜像来源
  - 控制命令步骤摘要
  - 截图索引
  - 成功或失败的结论与 warning
- 更新 `metadata.json` 的 `android` 块：
  - `mode ∈ {bootstrapped, installed, failed, skipped}`
  - `apk_file`
  - `package_name`（如能获取）

### 与批量流程的集成

- CLI 通过 `--android` / `--no-android` / `--sandbox-image auto|linux` 控制是否启用 Android 路径
- `sandbox_image=auto` 默认启用 Android；`sandbox_image=linux` 默认禁用
- 启用时，批量 worker 在 prompt 中告知 agent：`android.enabled=true`
- agent 在客户端发现阶段判断是否有官方 APK，有才启动 Android sandbox
- 批量退出时，`teardown_out_dir` 会同时销毁 Linux sandbox 和 Android sandbox

### 与 Skill 规则的衔接

业务规则文档需要新增 Android 分支：
- 前置条件：`android.enabled=true` + 找到官方 APK + 镜像可启动
- 客户端优先级：Linux 客户端 → Windows + Wine → 官方 APK + Android 沙盒 → web-only
- 控制命令用法：明确 `android_ctl` 与 `sandbox_ctl` 不得混用
- snapshot 不变量：每次动作前后截图
- 安全：不授予高危权限、不创建账号、不从第三方 APK 站下载
- 失败降级：安装失败/闪退/sandbox 失败时，设 `android.mode=failed/skipped`，继续用 web-only 完成报告

### 验收标准

- 控制桥每条命令单步执行、输出结构化 JSON、可断点续跑（依赖 `android_sandbox.json`）。
- `bootstrap` 后 `status` 能正确读取状态。
- `screenshot` 输出有效 PNG（≥1000 字节）。
- `tap/swipe/type/key` 执行后输出 `{"ok": true, ...}`。
- `teardown` 后状态文件被删除。
- 与 Linux 桌面 sandbox 状态文件隔离（`android_sandbox.json` vs `sandbox.json`）。

### 常见陷阱

- `Sandbox.connect` 需要传 `http_url=api_url` 才能连到本地 Docker 暴露的 computer-server 端口。
- `sb.mobile` 接口与 `sb.mouse` / `sb.keyboard` 完全不同，不要混用。
- image builder 安装 APK 失败后，APK 路径必须在 Android container 内可见才能用 `adb install` 降级。
- QEMU Android 启动慢，bootstrap 和 install 命令的超时要给够（install 建议 180 秒）。
- 截图文件名要符合 `NN_<source>_<view>.png` 规范，且必须在 report.md 中被引用。

---

## 任务包 E：后端目录重构为分层 `src` 布局

### 目标

把扁平的实现包重组为标准的 `src` 布局 + 独立入口脚本目录，用现代 Python 包管理器管理依赖。

### 在整体架构中的位置

这是一次**纯重构**，不改 CLI 参数、子进程协议、任务状态机、文件输出格式。

### 目标目录结构

```
backend/
├── scripts/           # 薄 shim：所有外部入口
│   ├── analyze_product.py
│   ├── android_ctl.py
│   ├── email_otp.py
│   ├── sandbox_ctl.py
│   ├── start_server.py
│   └── ...
├── src/               # 实现代码，按依赖层次分 6 个子包
│   ├── core/          # 最底层：config, ui, renderer, tasks, preflight
│   ├── settings/      # 叶子：app_config, credentials（不依赖业务包）
│   ├── sandbox/       # sandbox_runtime, sandbox_ctl, android_ctl（只依赖 core）
│   ├── analysis/      # prompts, workflow, claude_driver, email_otp, hooks, cli...
│   ├── batch/         # batch_store, ansi_curses, batch_dashboard, batch
│   └── web/           # server（依赖以上全部）
├── tests/             # 与 src 同级的测试目录
├── pyproject.toml
└── uv.lock
```

### 依赖单向无环（硬约束）

```
core → settings → sandbox → analysis → batch → web
```

- `core` 出度为 0：不 import 任何业务包。
- `settings` 是叶子：不依赖任何业务包。
- `sandbox` 只依赖 `core` 和 `settings`。
- `analysis` 依赖 `core`、`settings`、`sandbox`。
- `batch` 依赖 `core`、`settings`、`sandbox`、`analysis`。
- `web` 依赖以上全部。

**特别注意**：`sandbox.sandbox_ctl` / `sandbox.android_ctl` 不得 import `analysis.claude_driver` 或 `batch.batch`。

### 导入规范

- **包内**用相对导入：`from .config import ...`
- **跨包**用绝对包名：`from core.config import ...`、`from sandbox.sandbox_runtime import ...`
- 运行时由 scripts shim 或 pytest 的 `pythonpath=["src"]` 把 `src/` 挂上，所以跨包名直接以子包开头。

### 入口脚本契约

每个 `backend/scripts/*.py` 必须是薄 shim，只做三件事：
1. 把 `backend/src` 加入 `sys.path`
2. 从对应模块 import `main`
3. 调用 `sys.exit(main())`

例如：
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from analysis.cli import main
if __name__ == "__main__":
    sys.exit(main())
```

### `pyproject.toml` 要求

- 使用 `[project]` 定义 name/version/description/requires-python/dependencies
- dependencies 至少包含：`cua`, `fastapi`, `keyring`, `mailosaur`, `uvicorn`
- `[tool.uv] package = false`（非包模式，避免构建 wheel）
- `[tool.pytest.ini_options]` 配置 `pythonpath = ["src"]` 和 `testpaths = ["tests"]`
- 需要生成 lockfile（`uv.lock`）

### 测试迁移

- 测试从仓库根目录的 `tests/` 迁入 `backend/tests/`
- 测试通过 `sys.path.insert(0, repo_root / "backend" / "src")` 引入被测代码
- 用 `unittest` 或 `pytest` 编写
- 必须有 fake keyring 实现，mock 掉真实 keyring

### 所有外部调用链同步更新（极易遗漏）

重构时必须全仓搜索并更新以下路径引用：
- CLI help 文本中的示例命令路径
- README / CLAUDE.md / AGENTS.md 中的命令示例
- Skill 文档（`.claude/skills/**/*.md`）中的脚本路径
- Hook 注册路径（如果项目用了 Claude Code hooks）
- 前端启动后端的脚本路径（`web/scripts/start-backend.mjs`）
- Prompt 中 hardcode 的工具路径（例如 `python backend/scripts/email_otp.py`）

### 验收标准

- 所有入口 `--help` 跑得通：
  - `python backend/scripts/analyze_product.py --help`
  - `python backend/scripts/android_ctl.py --help`
  - `python backend/scripts/email_otp.py --help`
  - `python backend/scripts/sandbox_ctl.py --help`
- 全模块可编译：`python -m compileall backend/src`
- 测试全过：`cd backend && uv run pytest`（或等价命令）
- 全仓搜不到旧包名的残留引用（迁移说明性文字除外）
- 依赖单向无环：可用 `grep -r "from batch\|from web\|from analysis" backend/src/core backend/src/settings backend/src/sandbox` 验证上游不 import 下游

### 常见陷阱

- 路径推导（仓库根、安装脚本位置等）必须随文件深度变化同步修正。例如 `Path(__file__).resolve().parent.parent` 在旧位置和新位置算出的根不同。
- `pyproject.toml` 设 `package = false` 后，不能用 `pip install -e .`，要用 `uv run` 或手动管理 `PYTHONPATH`。
- 测试里的 `sys.path.insert` 要从 `tests/test_xxx.py` 的新深度重新计算 `repo_root`。
- Skill 文档里的命令路径最容易遗漏，要全文搜索 `backend/` 和 `product_analyzer/`。
- 重构后如果 `hooks.py` 路径变了，`.claude/settings.json` 里的 hook 注册路径必须同步更新。

---

## 任务包之间的边界与协作

| 任务包 | 主要产出 | 依赖谁 | 被谁依赖 |
|---|---|---|---|
| A 网页控制台 | React SPA + FastAPI 后端 | B, C, D, E | 无 |
| B 邮箱注册 | email_otp 工具 CLI | C | A, D（通过 prompt/workflow） |
| C 配置持久化 | app_config + credentials 模块 | 无 | A, B |
| D Android 沙盒 | android_ctl 工具 CLI | E 的目录结构 | A, B（通过 workflow） |
| E 目录重构 | src 布局 + pyproject.toml | 无 | A, B, C, D |

### 数据流总览

1. 用户在前端（A）填写产品名/URL，或上传批量 JSON。
2. 前端调用后端 API（A），后端：
   - 读取全局邮箱配置（C）
   - 创建输出目录、写 metadata/workflow 种子
   - 启动后台线程跑批量 worker
3. Worker 启动 Claude 子进程，把 prompt（含 runtime/android/email 参数）喂给 agent。
4. Agent 按 skill 规则执行：
   - 需要注册时调用 email_otp CLI（B）
   - 需要保存账号时调用 cred-put（B + C）
   - 需要 Android 体验时调用 android_ctl CLI（D）
5. 子进程输出 stream-json，经 renderer 写入 `run.log`；hook 事件写入 `events.jsonl`。
6. 前端通过 WebSocket（A）实时读取 `run.log` 和 `events.jsonl`。
7. 任务完成后前端展示 report.md 和截图画廊（A）。

---

## 用法建议（盲对比）

- 把任意一个任务包整段（含「产品背景」）交给对比 agent，不给它看本仓库的 commit。
- 它实现完后，拿对应任务包的「验收标准」逐条核对两边。
- 差异维度重点看：
  1. 是否满足硬约束（尤其 B/C 的 secrets 不外泄、D 的 snapshot 不变量、E 的依赖无环）
  2. 拆分粒度和架构选择
  3. 是否带测试
  4. 接口契约是否一致（JSON 结构、状态机、CLI 子命令）
