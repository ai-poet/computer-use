# 01 Linux Sandbox

目标:先进入 Linux 本地 Docker 沙盒,打开官网,拿到第一张证据截图。

## 步骤

1. 标记 `linux_sandbox` 为 `in_progress`。
2. 使用 `sandbox_ctl bootstrap` 创建沙盒并打开官网:

```bash
python backend/sandbox_ctl.py bootstrap "$OUTPUT_DIR" --open-browser --url "$URL"
```

3. 立即截图:

```bash
python backend/sandbox_ctl.py step screenshot "$OUTPUT_DIR" --out screenshots/01_web_homepage.png
```

4. 读取截图,确认 Firefox 真的打开了产品官网。若空白、崩溃或 cookie 弹窗遮挡,用 `click` / `key` / `scroll` 修复后再截图。
5. 写 `steps/01_linux_sandbox.md`,包含:
   - 沙盒名称/API URL
   - 首屏是否成功加载
   - 首页截图链接
   - 任何启动异常或 warning
6. 更新 `workflow.json.steps[].status = completed`。

## 规则

- Linux 镜像只假定有 Firefox,不要安装 Chromium。
- 坐标操作必须来自上一张截图。
- GUI 动作遵守 observe → act → observe:动作前后都要截图。
- 若 Linux 沙盒无法启动,本次任务失败;不要自动改回 host GUI。
