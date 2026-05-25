# 03 Client Routing

目标:根据官网证据决定接下来体验哪个客户端,或降级 web-only。

## 优先级

1. Linux 客户端: `.deb` / `.AppImage` / `.rpm` / Linux tarball。
2. Windows 客户端: `.exe` / `.msi` / `Setup*.exe`,在 Linux 沙盒内尝试 Wine。
3. Android:仅当找到官方 APK 直链或官方 release asset。
4. web-only:没有可运行客户端、只有 macOS/iOS、安装失败、拿不到 APK、或登录墙无 credential。

## 不接受

- 只有 Mac App Store / `.dmg` / `.pkg`:Linux 沙盒不运行,记录为 macOS-only。
- 只有 iOS App Store:记录为 iOS-only。
- Google Play 链接:只记录证据,不抓第三方 APK。
- 非官网/非官方 release 的 APK 镜像。

## 决策记录

在 `workflow.json.clients` 中记录:
- `linux[]`
- `windows[]`
- `android[]`
- `macos[]`
- `ios[]`
- `selected`
- `web_only_reason`

## 输出

写 `steps/03_client_discovery.md`:
- 实际浏览过的下载页面。
- 所有候选客户端表格:平台、URL、证据截图、是否可运行。
- 最终路由决策和原因。
- 如果降级 web-only,明确说明触发条件。
