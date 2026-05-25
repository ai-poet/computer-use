# 05 Android Client

目标:仅在找到官方 APK 时,追加 Android 沙盒体验。Android 沙盒是独立于 Linux Firefox 沙盒的第二个 sandbox,不要复用 Linux 桌面 sandbox。

## 前置条件

同时满足才执行:
- `android.enabled = true`
- 找到官网直链或官方 release asset APK
- 本地已准备 Docker/QEMU Android 镜像 `trycua/cua-qemu-android:latest`
- Android 沙盒可通过 Cua Sandbox SDK 启动

否则标记 `android.mode = skipped`,继续 web-only 或桌面路径。

## 镜像准备

调用 Android 虚拟机前必须先准备镜像:

```bash
docker pull --platform=linux/amd64 trycua/cua-qemu-android:latest
```

Apple Silicon / arm64 Mac 必须带 `--platform=linux/amd64`;不要依赖 Docker 自动选择 arm64 manifest。

只在已经找到官方 APK 后才启动 Android sandbox。不要为了“看看有没有 Android”提前拉起 Android 虚拟机;客户端发现阶段只记录官网/官方 release 里的 Android 证据。

## SDK 启动方式

优先按 Cua Sandbox SDK 创建**持久** Android sandbox,方便断点、截图和清理。不要用 `Sandbox.ephemeral(...)` 做主流程。

```python
from cua import Image, Sandbox

image = Image.from_registry("trycua/cua-qemu-android:latest")
sb = await Sandbox.create(image, name=android_name, local=True)
try:
    png = await sb.screenshot()
finally:
    await sb.disconnect()
```

如果 SDK/镜像版本明确支持 `Image.android(version="14", kind="vm")`,也可以使用:

```python
from cua import Image, Sandbox

image = Image.android(version="14", kind="vm")
sb = await Sandbox.create(image, name=android_name, local=True)
```

## 执行

1. 下载 APK 到 `downloads/`。
2. 启动独立 Android sandbox。
3. 安装 APK。优先参考 SDK image builder:

```python
from cua import Image, Sandbox

image = Image.from_registry("trycua/cua-qemu-android:latest").apk_install([apk_path])
sb = await Sandbox.create(image, name=android_name, local=True)
```

若 image builder 安装失败或不适配当前 SDK,再连接后降级为:

```python
await sb.shell.run(f"adb install -r {apk_path}", timeout=180)
```

4. 启动应用并截图:
   - 启动页
   - 权限弹窗
   - 主界面
   - 登录墙
   - 设置/关于/错误态中可达部分

Android UI 操作优先使用移动端接口和截图:

```python
await sb.mobile.tap(x, y)
await sb.mobile.swipe(x1, y1, x2, y2)
await sb.mobile.type_text("example")
await sb.mobile.back()
await sb.mobile.home()
png = await sb.screenshot()
```

只有移动端接口不可用时,才使用 `sb.shell.run("adb shell input ...")` 作为降级。

## 安全

- 不授予高危权限,只记录弹窗文案和可见选项。
- 不创建账号。
- 不从第三方 APK 站下载。
- 安装失败、闪退或 Android sandbox 失败时,写 `metadata.android.mode = failed`,不要让整单失败。
- Android 失败只影响 `metadata.android.mode` 和 warning;继续用 Linux Firefox web-only 或已有桌面证据完成报告。

## 输出

写 `steps/05_android_client.md`:
- APK 来源和文件路径。
- Android 沙盒启动/安装/运行结果。
- sandbox 名称、镜像来源和是否使用 `Image.from_registry` / `Image.android`。
- 截图索引。
- 成功体验则记录为 Android 增强证据;失败则写 warning。
