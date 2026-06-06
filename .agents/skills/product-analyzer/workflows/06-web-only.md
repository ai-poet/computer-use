# 06 Web-Only Experience

目标:当客户端不可运行或需要补足证据时,把网页当作主要体验对象完整探索。

## 触发

- 只有 macOS/iOS 客户端。
- 没有 Linux/Windows 客户端。
- Windows + Wine 安装或启动失败。
- Android 没有官方 APK 或 Android 沙盒失败。
- 登录墙既无 credential 也无法完成系统测试邮箱注册。

## 浏览范围

- 首页完整滚动。
- 功能页/演示页。
- Pricing。
- Docs / Help / Changelog。
- FAQ / Blog / About。
- 登录入口,只观察不绕过。
- 若 prompt 显示 `registration.email.enabled:true` 且网页端存在邮箱注册入口,可尝试一次系统测试邮箱注册来观察可访问功能;没有客户端时仍保持 `metadata.mode = web-only`。
- 可交互 demo:输入、提交、切 tab、播放、错误输入。
- 语言切换器。

## 邮箱注册边界

- 每个 run 最多 1 个测试账号,最多等待验证码 2 轮。
- 遇到 CAPTCHA、手机号必填、邀请码、付费绑卡或企业邮箱限制,立即停止并记录原因。
- 报告只写注册是否完成及原因,不暴露完整邮箱、验证码、密码。

## 截图

web-only 模式至少 6 张代表性截图,除非网站不可访问。截图覆盖不同页面/状态,不要只截同一首页区域。

## 输出

写 `steps/06_web_experience.md`:
- 网页体验路径。
- 关键界面与截图。
- 产品能力、限制和官网文案。
- 降级原因。
- 若网站本身不可访问,记录访问失败证据与第三方信息是否使用。
