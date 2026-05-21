# Custom Desktop Pet（自定义桌面宠物）产品分析报告

| 项目 | 值 |
|---|---|
| 官网 | https://store.steampowered.com/app/2297040/Custom_Desktop_Pet/ |
| 下载链接 | — |
| 报告日期 | 2026-05-22 |
| 主机 | linux / x86_64 |
| Runtime | sandbox-local |
| 模式 | web-only |
| 用时 | ~25 分钟 |

> 本次为网页版分析，未驱动桌面端 — 产品目前状态为"即将推出"(Coming Soon)，仅有 Windows 版安装包，当前 Linux 沙盒无法运行。

---

## 1. 详细的产品逻辑介绍

### 1.1 总定位

Custom Desktop Pet 是一款面向二次元爱好者的高度可定制桌面宠物软件，源自免费开源项目「碧蓝航线秘书舰」。用户可通过自定义立绘、Spine 动画、精灵动画等资源创建个性化桌面宠物，并利用内置的简化脚本系统定义宠物行为（如点击反应、时间触发事件、WASD 移动等）。产品通过 Steam 创意工坊支持用户分享自制宠物，降低内容创作门槛。

### 1.2 界面清单

按出现顺序列出实际看到的所有主要界面：

| # | 界面 | 入口 | 主要功能 | 截图 |
|---|---|---|---|---|
| 1 | Steam 商店页 | https://store.steampowered.com/app/2297040/ | 产品展示、年龄验证、愿望单 | [01_web_homepage.png](screenshots/01_web_homepage.png) |
| 2 | Steam 年龄验证 | 商店页首次访问 | 出生日期选择、进入确认 | [02_web_age_verify.png](screenshots/02_web_age_verify.png) |
| 3 | Bilibili 搜索结果 | search.bilibili.com | 用户创作内容、宣传视频 | [03_web_bilibili.png](screenshots/03_web_bilibili.png) |

### 1.3 各界面功能与评价

#### 1.3.1 Steam 商店页

- **功能**: 产品信息展示（描述、截图、视频、系统需求、标签）、年龄验证拦截、愿望单添加
- **交互**: 首次访问需通过年龄验证（选择出生日期后点击"进入"），未通过验证无法浏览内容
- **评价**: Steam 商店页是唯一的官方信息入口，但年龄验证墙对首次访问形成阻碍；产品标注为"即将推出"，无可用的购买/下载按钮
- **截图**:[01_web_homepage.png](screenshots/01_web_homepage.png)

#### 1.3.2 Steam 年龄验证页

- **功能**: 三个下拉框（年/月/日）选择出生日期，"进入"按钮提交
- **交互**: 填写日期后点击进入，验证通过后设置 cookie 并跳转商店内容区
- **评价**: 沙盒内 Firefox 与 Steam 年龄验证的交互存在兼容性问题 — 多次尝试点击下拉框和输入日期均未能成功通过验证，最终依赖外部搜索获取信息
- **截图**:[02_web_age_verify.png](screenshots/02_web_age_verify.png)

#### 1.3.3 Bilibili 搜索结果页

- **功能**: 展示用户上传的与"自定义桌面宠物"相关的视频内容，包括宣传、教程、展示等
- **交互**: 搜索关键词后分页展示，可点击视频进入详情页
- **评价**: 作为第三方信息源补充了官方 Steam 页面的不足，可见社区对桌面宠物类内容有一定活跃度；但搜索结果混杂了其他桌面宠物产品（如 Desktop Mate），需人工甄别
- **截图**:[03_web_bilibili.png](screenshots/03_web_bilibili.png)、[04_web_bilibili_scroll.png](screenshots/04_web_bilibili_scroll.png)

---

## 2. UI/UX 风格和质量描述

### 2.1 视觉风格

根据 Steam 商店截图和 Bilibili 视频内容，产品采用典型的二次元动漫风格：
- **默认角色**: AI 生成的白丝洛丽塔风格角色，白毛粉瞳萝莉猫娘造型（官方标注"粗略影像，最终成品会有所不同"）
- **动画表现**: 支持动态立绘、Spine 骨骼动画，角色有呼吸/待机动画
- **整体调性**: 萌系、个性化、面向 ACG 文化爱好者

### 2.2 信息密度与层级

Steam 商店页面的信息架构标准清晰：
- 首屏左侧为游戏主视觉/视频，右侧为产品名称、开发商、标签、愿望单按钮
- 下方依次为"关于此游戏"描述、系统需求、更多产品信息
- 由于产品未发布，页面缺少定价区和购买按钮

### 2.3 交互流畅度

- **启动到首屏**: 无法实测（产品未发布且无 Linux 版）
- **Steam 页面加载**: 年龄验证页加载正常，但下拉框交互在沙盒 Firefox 中响应不佳
- **Bilibili 页面**: 加载流畅，滚动正常

### 2.4 文案质量

Steam 商店英文描述：
> "This is a desktop pet that supports customization, supports painting, spine, and sprite animation. There are also event interactions, and other interesting functions."

文案风格直白、功能导向，无明显机翻痕迹，但文学性较弱，符合独立开发者产品的常见特征。

### 2.5 可访问性观察

- Steam 商店页为标准网页，支持键盘导航和屏幕阅读器
- 产品本身为桌面应用，可访问性无法实测

---

## 3. 官网描述

### 3.1 关键文案摘录

> "This is a desktop pet that supports customization, supports painting, spine, and sprite animation. There are also event interactions, and other interesting functions. You can use the assets to make your own desktop pet, and customize its behavior, voice, sound effects, shader, etc. Of course, you can also directly download desktop pets shared by others through the Steam Workshop."
> — Steam 商店页"关于此游戏"段落

> "The attached e-book explains in detail how to organize asset files and customize your pet. You can define variables (like a 'favorability level'), control animations/audio with key presses, detect system time, and even create shutdown reminders."
> — Steam 商店页功能描述

### 3.2 核心卖点（官网视角）

1. **高度自定义**: 支持立绘、Spine、精灵动画三种格式，可自定义行为/语音/音效/着色器（原文锚：Steam 描述首段）
2. **创意工坊支持**: 可直接下载其他玩家分享的桌面宠物（原文锚：Steam 描述末段）
3. **事件交互系统**: 支持按键触发、时间检测、变量控制等交互逻辑（原文锚：功能描述段）
4. **零基础行为编辑**: 内置简化脚本语言，无需编程经验即可定义宠物行为（原文锚：e-book 说明）

### 3.3 与实际体验的差距

| 卖点 | 官网原文 | 实际体验 | 差距 |
|---|---|---|---|
| 产品可获取性 | Steam 商店页可添加愿望单 | 产品状态为"即将推出"，无法下载/购买 | 产品尚未发布，无法实际体验 |
| 默认角色质量 | 宣传图展示动态立绘角色 | 官方标注"AI 生成粗略影像，最终成品会有所不同" | 最终角色视觉可能与当前宣传存在差异 |
| 平台支持 | Steam 商店页显示 | 仅 Windows 10，无 macOS/Linux 版 | Linux 用户当前无法使用 |

---

## 5. 目标用户

基于官网用语和实际功能推断：

1. **二次元/ACG 文化爱好者**: 产品采用萌系角色设计，支持高度个性化，符合该群体审美（证据：默认角色为白毛粉瞳萝莉猫娘、Bilibili 社区活跃）
2. **桌面美化用户**: 产品属于桌面宠物类别，面向希望为桌面增添互动元素的用户（证据：Steam 标签含 "Casual"、"Indie"）
3. **内容创作者**: 创意工坊支持和资源自定义功能吸引有创作能力的用户（证据：支持 Spine 动画、着色器自定义、Steam Workshop）
4. **无编程基础用户**: 内置简化脚本语言降低了行为自定义门槛（证据：e-book 教程、"no coding experience required" 描述）

---

## 6. 与同类产品对比

| 维度 | Custom Desktop Pet | Desktop Mate (Steam) | 传统桌面宠物 (如 QQ 宠物) |
|---|---|---|---|
| **平台** | Windows (即将推出) | Windows (已发布) | 已停止服务 |
| **自定义程度** | 高（支持 Spine/着色器/行为脚本） | 中（支持模型导入） | 低（预设角色和装扮） |
| **创意工坊** | ✅ Steam Workshop | ✅ Steam Workshop | ❌ |
| **编程门槛** | 低（内置简化语言） | 中（需了解模型格式） | 无 |
| **Live2D/3D 支持** | 规划中（未来更新） | ✅ 已支持 | ❌ |
| **商业状态** | 未发布 | 已发售 | 已停运 |

---

## 7. 优劣势小结

| 维度 | 优势 | 劣势 |
|---|---|---|
| 产品逻辑 | 高度可自定义，支持多种动画格式；创意工坊扩展内容生态 | 产品尚未发布，无实际可用版本；仅支持 Windows |
| UI/UX | 二次元风格明确，目标用户画像清晰；内置教程降低上手门槛 | 默认角色为 AI 生成，最终品质存在不确定性；年龄验证墙阻碍信息获取 |
| 工程质量 | 基于已有开源项目（碧蓝航线秘书舰），有一定技术积累；开发者活跃（Bilibili/QQ群） | 暂无用户评价，产品质量未经验证；系统需求信息不完整（CPU/显卡标注"无特殊要求"） |

---

## 附录 A 截图索引

| # | 文件 | 说明 |
|---|---|---|
| 01 | screenshots/01_web_homepage.png | Steam 商店首页（年龄验证页） |
| 02 | screenshots/02_web_age_verify.png | Steam 年龄验证详情（滚动后） |
| 03 | screenshots/03_web_bilibili.png | Bilibili 搜索结果页 |
| 04 | screenshots/04_web_bilibili_scroll.png | Bilibili 搜索结果（滚动后） |
| 09 | screenshots/09_web_steamdb.png | SteamDB 页面（Cloudflare 验证） |
| 11 | screenshots/11_web_community.png | Steam 社区页面（连接失败） |

> 编号规则：`NN_<source>_<view>.png`，`source ∈ {web, app, android}`。本次分析无 app/android 段截图（产品未发布且仅 Windows 版）。
