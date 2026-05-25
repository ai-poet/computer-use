---
name: product-analyzer
description: 给定产品名和官网 URL,按 Linux-first workflow 在沙盒中访问官网、发现并体验客户端、逐步写阶段报告,最后产出中文产品分析报告。触发方式:scripts/analyze_product.py 调用,或对话中“分析/拆解/评测/调研 这个产品 https://...”类请求且包含 URL。
---

# product-analyzer

本 skill 只做入口路由。详细步骤在 `workflows/` 中,按需读取,不要把所有规则一次性塞进上下文。

## 必读顺序

1. 先读 [`workflows/00-contract.md`](workflows/00-contract.md),确认输入、输出、状态文件和禁止事项。
2. 然后按当前步骤读取对应文档:
   - Linux 沙盒: [`workflows/01-linux-sandbox.md`](workflows/01-linux-sandbox.md)
   - 官网发现: [`workflows/02-website-discovery.md`](workflows/02-website-discovery.md)
   - 客户端路由: [`workflows/03-client-routing.md`](workflows/03-client-routing.md)
   - 桌面客户端: [`workflows/04-desktop-client.md`](workflows/04-desktop-client.md)
   - Android 客户端: [`workflows/05-android-client.md`](workflows/05-android-client.md)
   - web-only 深挖: [`workflows/06-web-only.md`](workflows/06-web-only.md)
   - 阶段报告与最终报告: [`workflows/07-reporting.md`](workflows/07-reporting.md)
3. 报告结构仍以 [`REPORT_TEMPLATE.md`](REPORT_TEMPLATE.md) 为准。

## 当前默认

- 默认 runtime 是 `sandbox-local`,默认环境是 Linux Docker 沙盒。
- 单任务和批量都先进入 Linux 沙盒。只有调用方显式要求 legacy host 模式时,才走本机 cua-driver。
- 客户端优先级:Linux 客户端 → Windows 客户端 + Wine → 官方 APK + Android 沙盒 → web-only。
- 只有 iOS/macOS 客户端、客户端下载/安装失败、拿不到官方 APK、或登录墙没有 credential 时,改走 web-only。

## 运行纪律

- 全程维护 TodoWrite,步骤粒度与 workflow 一致。
- 每完成一个 workflow 步骤,立刻更新 `workflow.json` 并写 `steps/NN_*.md`。
- 结束前必须写最终 `report.md`,补齐 `metadata.json`,并确保截图都被阶段报告或最终报告引用。
- hooks 会拦截 host GUI、危险 shell 抓站和不完整收尾;如果被拦,按错误信息修补产物后继续。
