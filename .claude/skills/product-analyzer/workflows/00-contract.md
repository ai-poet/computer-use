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

## 状态更新

优先用 Python helper 更新 workflow:

```bash
python -m product_analyzer.workflow_cli ...
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
- 不绕过登录、不创建账号、不保存明文 credential。

## 模式

- 成功体验 Linux / Windows(Wine) / Android 任一客户端: `metadata.mode = "sandbox-full"`。
- 没有可运行客户端或客户端失败后只完成网页体验: `metadata.mode = "web-only"`。
- Android 结果写在 `metadata.android.mode`: `android` / `skipped` / `failed`。

## Credential

遇到登录墙时:
1. 写入 `workflow.json.credential_requests[]`,包含服务、字段名、原因、状态 `pending`。
2. 暂停等待用户通过前端/控制台提交。
3. 有 credential 就继续体验;没有就记录 warning 并降级到可访问范围。
4. 不把 secret 写入 `metadata.json`、`events.jsonl`、`steps/*.md` 或 `report.md`。
