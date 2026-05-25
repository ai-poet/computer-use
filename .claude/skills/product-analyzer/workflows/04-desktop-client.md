# 04 Desktop Client

目标:在 Linux 沙盒中体验 Linux 客户端;若没有 Linux 客户端但有 Windows 客户端,用 Wine 尝试。

## Linux 客户端

1. 下载到 `downloads/`。
2. 根据文件类型安装或运行:
   - `.deb`: `dpkg -i`,缺依赖时记录错误,可尝试 `apt-get -f install`。
   - `.AppImage`: `chmod +x` 后运行;缺 FUSE 时记录并尝试可行替代。
   - tarball:解压后找可执行入口。
3. 启动后回到 GUI 路径,用截图、点击、输入体验主要界面。

## Windows + Wine

1. 只有没有 Linux 客户端时才尝试。
2. 检查 Wine 是否存在;没有则可安装 Wine,但若安装耗时或失败超过一次,立即记录并降级 web-only。
3. 运行安装器,保留安装日志。
4. 启动应用;若显示窗口,用截图/点击体验;若闪退,记录错误和降级。

## 最少体验范围

- 启动页或主界面。
- 主要任务创建/输入/核心流程。
- 设置/账号/帮助/关于。
- 错误态或登录墙。

## Credential

如果客户端需要登录:
- 写 credential request。
- 有 credential 时继续;无 credential 时记录登录墙,转 web-only 补足官网证据。

## 输出

写 `steps/04_desktop_client.md`:
- 下载和安装过程。
- 启动结果。
- 主要界面截图。
- 可体验功能与卡点。
- 是否使 `metadata.mode = sandbox-full`;失败则写明 web-only 原因。
