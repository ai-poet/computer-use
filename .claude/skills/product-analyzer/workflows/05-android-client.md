# 05 Android Client

目标:仅在找到官方 APK 时,追加 Android 沙盒体验。

## 前置条件

同时满足才执行:
- `android.enabled = true`
- 找到官网直链或官方 release asset APK
- Android 沙盒/模拟器可启动

否则标记 `android.mode = skipped`,继续 web-only 或桌面路径。

## 执行

1. 下载 APK 到 `downloads/`。
2. 启动 Android 沙盒。
3. 安装 APK。
4. 启动应用并截图:
   - 启动页
   - 权限弹窗
   - 主界面
   - 登录墙
   - 设置/关于/错误态中可达部分

## 安全

- 不授予高危权限,只记录弹窗文案和可见选项。
- 不创建账号。
- 不从第三方 APK 站下载。
- 安装失败、闪退或沙盒失败时,写 `metadata.android.mode = failed`,不要让整单失败。

## 输出

写 `steps/05_android_client.md`:
- APK 来源和文件路径。
- Android 沙盒启动/安装/运行结果。
- 截图索引。
- 成功体验则记录为 Android 增强证据;失败则写 warning。
