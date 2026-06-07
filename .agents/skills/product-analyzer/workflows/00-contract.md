# 00 Contract

## 输入

调用方会在 prompt 和 `metadata.json` 中提供:
- `product_name`
- `url`
- `download_url` 可为空
- `output_dir`
- `runtime`
- `sandbox.image`
- `android.enabled`
- 批量任务还会在 `metadata.queue.category` / `metadata.queue.file` 记录来源队列

不要改写这些原始输入值。所有产物写入 `output_dir`。

## 必写产物

```
output_dir/
  workflow.json
  events.jsonl
  steps/
    01_linux_sandbox.md
    02_website.md
    03_client_discovery.md
    04_desktop_client.md
    05_android_client.md
    06_web_experience.md
    07_final_report.md
  report.md
  metadata.json
  screenshots/
  downloads/
```

每个步骤结束后立刻写对应 `steps/*.md`;最终再汇总成 `report.md`。

批量任务的 `output_dir` 会按队列文件分类,形如:

```text
reports/<queue-category>/<slug>-YYYY-MM-DD[-N]/
```

例如 `queue.language-learning.json` 默认写入 `reports/language-learning/...`。单任务继续写在 `reports/<slug>-YYYY-MM-DD[-N]/`。

## 状态更新

优先用 Python helper 更新 workflow:

```bash
python backend/scripts/workflow_cli.py ...
```

如果 helper 不可用,可以直接编辑 `workflow.json`,但必须保持 JSON 合法。每个 step 至少记录:
- `status`: `pending` / `in_progress` / `completed` / `skipped` / `failed`
- `summary`
- `started_at`
- `completed_at`

## 禁止事项

- sandbox runtime 中禁止操作 host GUI。
- 禁止用 host `open`、`osascript activate/open/launch`、`cliclick`。
- 禁止用 shell 抓官网作为主路径。官网必须在沙盒 Firefox 中通过截图、点击、滚动、输入来真实浏览。
- `step shell` 只允许下载安装包直链、安装命令、读系统信息、排障。
- 不从第三方 APK 镜像站下载 APK。
- 不绕过登录。只有 prompt 明确 `registration.email.enabled:true` 时,才允许使用系统提供的测试邮箱创建一次低风险测试账号。
- 不保存明文 credential、验证码、邮箱 API key、邮箱密码、session token。
- 禁止手机号注册、绕过 CAPTCHA、邀请码破解、付费绑卡、营销邀请、批量滥用注册。
- Android sandbox 必须是独立于 Linux Firefox sandbox 的第二个 sandbox;只有找到官方 APK 后才启动。
- `sandbox_ctl` 只用于 Linux/Firefox 桌面沙盒;Android 移动端必须用 `backend/scripts/android_ctl.py` 或同等 Cua SDK `sb.mobile` 脚本。

## 模式

- 成功体验 Linux / Windows(Wine) / Android 任一客户端: `metadata.mode = "sandbox-full"`。
- 没有可运行客户端或客户端失败后只完成网页体验: `metadata.mode = "web-only"`。
- Android 结果写在 `metadata.android.mode`: `android` / `skipped` / `failed`。
- Android 启动、安装或运行失败只影响 `metadata.android.mode` 和 `warnings[]`,不要让整单失败。

## Credential

遇到登录墙时:
1. 写入 `workflow.json.credential_requests[]`,包含服务、字段名、原因、状态 `pending`。
2. 暂停等待用户通过前端/控制台提交。
3. 有 credential 就继续体验;没有就记录 warning 并降级到可访问范围。
4. 不把 secret 写入 `metadata.json`、`events.jsonl`、`steps/*.md` 或 `report.md`。

持久化凭据存储(全局钥匙串,跨同产品任务复用):
- 开始登录流程前,先 `python backend/scripts/email_otp.py cred-get --out-dir "$OUTPUT_DIR"`
  查本产品是否已有保存的账号;命中则直接复用,免去重复注册。
- 注册/拿到可复用账号后,`python backend/scripts/email_otp.py cred-put --out-dir "$OUTPUT_DIR"
  --label "login account" --field username=<addr> --field password=<pw>` 写入。
- `cred-list` 列出已存凭据元数据(只含 label/字段名/来源,不含 secret 值)。
- cred-get 返回的 secret 只用于当前 UI 输入或本次 tool call,绝不写进任何产物。

## Email registration

遇到登录/注册墙且 prompt 显示 `registration.email.enabled:true` 时,可优先尝试邮箱注册:

1. 先截图记录登录/注册入口,确认存在邮箱注册路径。
2. 调 `python backend/scripts/email_otp.py status` 确认 provider 可用;
   并 `cred-get --out-dir "$OUTPUT_DIR"` 检查是否已有可复用账号(有就跳过注册直接登录)。
3. 调 `python backend/scripts/email_otp.py create-address --out-dir "$OUTPUT_DIR"` 获取测试邮箱。
4. 在目标网页/客户端中填写测试邮箱和一次性随机密码;密码只用于当前 UI 输入,不得写入产物。
5. 若需要验证码,调 `python backend/scripts/email_otp.py wait-code --out-dir "$OUTPUT_DIR" --email "<email>" --timeout 90`;若需要邮箱链接,调 `wait-link`。
6. 注册成功后:先 `cred-put` 把邮箱+密码存入全局钥匙串(便于后续复用),再调
   `mark-completed --used-for web|desktop|android`;失败/跳过则调 `mark-failed` 或 `mark-skipped` 写原因。

限制:
- 每个 run 最多创建 1 个测试账号,最多等待验证码 2 轮。
- 如果 plus alias 被产品拒绝,可重新 `create-address --force-fixed` 用固定邮箱重试一次。
- 遇到 CAPTCHA、手机号必填、邀请码、人工审核、付费/绑卡、企业邮箱限制,立即停止注册并降级。
- 阶段报告和最终报告只写“使用测试邮箱完成/未完成注册及原因”,不得暴露完整邮箱、验证码、密码。
