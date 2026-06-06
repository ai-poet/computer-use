# 03 Client Routing

目标:根据官网证据决定接下来体验哪个客户端,或降级 web-only。

## 优先级

1. Linux 客户端: `.deb` / `.AppImage` / `.rpm` / Linux tarball。
2. Windows 客户端: `.exe` / `.msi` / `Setup*.exe`,在 Linux 沙盒内尝试 Wine。
3. Android:仅当找到官方 APK 直链或官方 release asset。
4. web-only:没有可运行客户端、只有 macOS/iOS、安装失败、拿不到 APK、或登录墙既无 credential 也无法完成系统测试邮箱注册。

## 不接受

- 只有 Mac App Store / `.dmg` / `.pkg`:Linux 沙盒不运行,记录为 macOS-only。
- 只有 iOS App Store:记录为 iOS-only。
- Google Play 链接:只记录证据,不抓第三方 APK。
- 非官网/非官方 release 的 APK 镜像。

## 登录墙路由

发现可运行客户端后不要因为登录墙立即 web-only:

1. 先确认是否有邮箱注册入口。
2. 若 prompt 显示 `registration.email.enabled:true`,按 `00-contract.md` 的 Email registration 流程尝试一次测试邮箱注册。
3. 邮箱注册成功:继续对应 Linux/Windows/Android 客户端体验。
4. 邮箱注册不可用、验证码超时、CAPTCHA、强制手机号、邀请码或付费绑卡:记录原因,再降级 web-only。

## 决策记录

在 `workflow.json.clients` 中记录:
- `linux[]`
- `windows[]`
- `android[]`
- `macos[]`
- `ios[]`
- `selected`
- `web_only_reason`
- `registration.status` / `registration.failure_reason`

## 输出

写 `steps/03_client_discovery.md`:
- 实际浏览过的下载页面。
- 所有候选客户端表格:平台、URL、证据截图、是否可运行。
- 最终路由决策和原因。
- 如果降级 web-only,明确说明触发条件。
