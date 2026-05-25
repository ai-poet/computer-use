# 02 Website Discovery

目标:在沙盒 Firefox 内真实浏览官网,收集产品定位、入口、定价/文档/下载线索。

## 必做浏览

- 首页首屏和底部。
- 导航栏中所有相关入口:Download / 下载 / Get the App / Install / Pricing / Docs / Features / Changelog / FAQ / Blog。
- Footer 的平台图标或商店链接。
- 平台切换器、语言切换器、cookie 弹窗、登录入口。

## 证据

- 每个重要页面或状态截图到 `screenshots/NN_web_<view>.png`。
- 至少保留首页、下载/安装入口、定价或功能页、登录/开始入口。
- 记录实际点击过的 URL 和页面名,供 client routing 证明不是只 grep。

## 允许的 shell

- 不用 shell 抓官网作为主路径。
- 可以在已经通过浏览器发现真实直链后,用 `wget -O downloads/... <url>` 下载安装包。
- 可以用 shell 查看文件类型、系统版本、安装日志。

## 输出

写 `steps/02_website.md`:
- 官网可访问性结论。
- 关键页面截图索引。
- 发现的下载入口和候选客户端链接。
- 官网核心文案原文,保留短引用和位置。
- 登录墙、地区限制、崩溃等 warning。
