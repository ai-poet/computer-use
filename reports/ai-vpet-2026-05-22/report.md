# 守护与智友 (Ai Vpet) 产品分析报告

| 项目 | 值 |
|---|---|
| 官网 | https://store.steampowered.com/app/3029820/Ai_Vpet/ |
| 下载链接 | Steam 平台（Windows 独占） |
| 报告日期 | 2026-05-22 |
| 主机 | linux / x86_64 |
| Runtime | sandbox-local |
| 模式 | web-only |
| 用时 | ~18 分钟 |

> 本次为网页版分析，未驱动桌面端 — 产品仅有 Windows 版安装包（Steam 软件），当前沙盒环境（Linux）无可用的桌面端安装包。

---

## 1. 详细的产品逻辑介绍

### 1.1 总定位

Ai Vpet（中文名"守护与智友"）是一款基于 AI 技术的虚拟桌面宠物软件，2024 年 8 月 1 日由独立开发者 uemesh 通过 Steam 平台发布，目前处于 Early Access 阶段。产品将 Live2D 动画技术与深度学习、自然语言处理结合，让用户在 Windows 桌面上拥有一只可深度自定义的 AI 虚拟伴侣。用户可自定义角色形象、性格、服装、声音乃至宠物，使其在工作时提供安静陪伴，在休息时主动发起互动。产品定位于二次元文化爱好者与桌面美化用户群体，售价 ¥11.00。

### 1.2 界面清单

按 Steam 商店页面结构列出实际观察到的所有主要界面区块：

| # | 界面 | 入口 | 主要功能 | 截图 |
|---|---|---|---|---|
| 1 | Steam 商店首页 | https://store.steampowered.com/app/3029820/Ai_Vpet/ | 产品展示、购买、评价、系统要求 | [01_web_header.jpg](screenshots/01_web_header.jpg) |
| 2 | 产品宣传图区 | 首页顶部轮播 | 展示 Live2D 角色形象与产品卖点 | [02_web_capsule.jpg](screenshots/02_web_capsule.jpg) |
| 3 | 购买与评价区 | 首页右侧栏 | 显示价格、评价摘要、标签、发行信息 | [03_web_page_bg.jpg](screenshots/03_web_page_bg.jpg) |
| 4 | 产品截图展示 | 商店媒体区 | 展示角色立绘、界面截图 | [05_web_screenshot2.jpg](screenshots/05_web_screenshot2.jpg) |
| 5 | 产品截图展示（变体） | 商店媒体区 | 展示不同角色形象 | [06_web_screenshot3.jpg](screenshots/06_web_screenshot3.jpg) |
| 6 | 沙盒桌面环境 | sandbox-local 沙盒 | XFCE 桌面 + Firefox 浏览器 | [07_web_desktop.png](screenshots/07_web_desktop.png) |
| 7 | SteamDB 验证页 | steamdb.info | Cloudflare 人机验证拦截 | [08_web_steamdb_cf.png](screenshots/08_web_steamdb_cf.png) |

### 1.3 各界面功能与评价

#### 1.3.1 Steam 商店首页

- **功能**：产品核心信息展示页面，包含产品名称、开发商（uemesh）、发行日期（2024 年 8 月 1 日）、价格（¥11.00）、用户评分（多半好评，75% 好评率，基于 398 条评价）、Steam 标签、系统要求、产品描述等全部关键信息。
- **交互**：用户通过 Steam 客户端或浏览器访问，可点击"添加到购物车"购买，浏览媒体截图，查看用户评价，点击标签跳转到同类游戏筛选页。
- **评价**：Steam 商店页面信息结构完整，产品描述采用中英双语（英文为主，部分中文翻译），"About This Software"章节详细列出了 5 大产品特性。但 Steam 商店作为通用平台，产品页缺乏独立的 branding 设计，所有 Steam 软件共用相同的页面模板。
- **截图**：[01_web_header.jpg](screenshots/01_web_header.jpg)、[03_web_page_bg.jpg](screenshots/03_web_page_bg.jpg)

#### 1.3.2 产品宣传图区

- **功能**：通过视觉素材传达产品核心卖点。Header 图展示粉发动漫角色与品牌 Logo"Ai Vpet"，标语"Desktop Pet 2.0 Your pet, by you"；Capsule 图（Steam 库列表展示图）展示另一角色形象，标语"YOUR AI BUDDY"。
- **交互**：用户在 Steam 商店首页、搜索页、库列表等多个触点看到这些素材。
- **评价**：视觉风格高度统一 —— 粉色系、二次元动漫风、Live2D 渲染质感。角色设计精美，蓝紫色瞳孔与粉色头发形成高对比度视觉焦点。但宣传图未能展示实际桌面运行效果（如宠物在桌面上的位置、大小、交互方式等），用户仅从图片无法判断实际使用体验。
- **截图**：[01_web_header.jpg](screenshots/01_web_header.jpg)、[02_web_capsule.jpg](screenshots/02_web_capsule.jpg)

#### 1.3.3 产品截图展示区

- **功能**：展示软件内实际角色形象。截图显示不同风格的 AI 虚拟角色：女仆装粉发角色配语音波形图标（暗示语音交互功能）、蝴蝶装饰粉发角色（展示角色多样性）。
- **交互**：用户在商店页可点击缩略图放大查看。
- **评价**：截图素材数量较少（从 HTML 提取仅 3 张有效游戏截图），且均为角色立绘而非软件界面截图。用户无法从截图判断：桌面宠物如何显示（悬浮窗？独立窗口？）、交互界面长什么样、设置面板布局如何。这对于一款"软件"类产品来说是信息不足的 —— Steam 标签明确分类为"Software"而非"Game"，但截图展示方式更接近游戏角色展示。
- **截图**：[05_web_screenshot2.jpg](screenshots/05_web_screenshot2.jpg)、[06_web_screenshot3.jpg](screenshots/06_web_screenshot3.jpg)

---

## 2. UI/UX 风格和质量描述

### 2.1 视觉风格

产品视觉呈现强烈的**二次元动漫风格**与**萌系（Kawaii）美学**。主色调为粉紫色系，角色设计采用典型的日系动漫大眼、粉发、精致服装元素。Live2D 技术赋予角色动态表现力 —— 从截图可见角色具有细腻的光影渲染和柔和的边缘处理，符合当前二次元虚拟主播/虚拟形象的主流审美标准。

Steam 商店页面的背景图为柔和的粉紫渐变配樱花/花瓣元素（见 [03_web_page_bg.jpg](screenshots/03_web_page_bg.jpg)），与产品本身的视觉调性一致。

### 2.2 信息密度与层级

由于产品仅在 Steam 平台分发，信息架构完全依托 Steam 商店模板：

- **首屏**：左侧为产品宣传图/视频轮播 + 简短描述；右侧为购买区（价格、评价、标签、系统要求）。首屏信息密度适中，关键信息（价格、评分、标签）在视口内可见。
- **次要信息**：向下滚动可见详细产品描述（"About This Software"）、系统要求、用户评价、更多类似产品推荐。Steam 模板保证了信息层级的一致性，但缺乏产品独有的信息组织方式。
- **CTA**：首屏右侧的"Add to Cart"按钮为绿色，在深色 Steam 主题下对比度充足，是页面最突出的操作入口。

### 2.3 交互流畅度

基于 Steam 商店页面的浏览体验：

- 页面加载：Steam 商店页面依赖大量 JavaScript 动态加载内容，在沙盒 Firefox 环境中存在渲染问题（仅页脚内容可见，见 [08_web_steamdb_cf.png](screenshots/08_web_steamdb_cf.png) 前的截图记录）。通过 `wget` 获取的 HTML 完整（110KB），说明网络可达，但浏览器端 JavaScript 渲染存在兼容性问题。
- 截图轮播：Steam 标准的媒体轮播组件，支持缩略图点击和左右箭头切换。
- 标签点击：可跳转至 Steam 同类软件筛选页。

### 2.4 文案质量

产品描述采用**中英混合**文案，英文为主，部分中文翻译：

> "Ai Vpet is an innovative AI virtual desktop pet software. It breaks through the limitations of traditional desktop pets. Through deep learning and natural language processing techniques, it provides users with a knowledgeable and articulate AI companion."

文案整体通顺，但存在以下问题：
- "initiatively initiates interaction" —— 重复用词（initiative + initiate），语义冗余
- "increase the interestingness of work" —— "interestingness" 非标准用词，应为 "make work more interesting"
- 中文描述中的"守护与智友"作为副标题/功能名出现，但产品英文名 "Ai Vpet" 与中文名关联度不高（用户从英文名难以推断中文名含义）
- 系统要求中 CPU 描述混用中英文："Intel i3 或同等级别"、"Intel i7 或同等级别"

### 2.5 可访问性观察

- Steam 商店页面本身遵循 Steam 平台的可访问性标准，深色主题（#171a21）下文字对比度充足。
- 产品截图中的角色文字/界面元素无法评估（未提供软件实际界面截图）。
- 产品支持语言信息在 HTML 中未完整提取（语言表格解析为空），但从 Steam 页面推断至少支持英文和简体中文界面。

---

## 3. 官网描述

### 3.1 关键文案摘录

> "Ai Vpet is an innovative AI virtual desktop pet software. It breaks through the limitations of traditional desktop pets. Through deep learning and natural language processing techniques, it provides users with a knowledgeable and articulate AI companion."
> —— Steam 商店 "About This Software" 区，原文锚：首页产品描述第一段

> "Users can choose and customize various character models according to their own preferences, including clothing, pets, personalities, and voices, to create a completely personalized virtual partner."
> —— 原文锚：产品描述第二段

> "The advanced AI technology enables you to customize every detail of the character, from the character image to the personality, clothing to the voice, to create a Wise Friend that is exclusively for you."
> —— 原文锚：Product features 第 1 条

> "Adopting the industry-leading Live2D technology, every character is as vivid as a work of art, with extremely smooth movements, an ultimate visual feast that is so beautiful that it makes people's hearts flutter."
> —— 原文锚：Product features 第 4 条

### 3.2 核心卖点（官网视角）

1. **AI 驱动的深度自定义**：从角色形象到性格、服装到声音，每个细节均可定制（原文锚：Product features 第 1 条）
2. **AI 情感陪伴**："守护与智友"功能像真实朋友一样随时聊天，消除孤独感（原文锚：Product features 第 2 条）
3. **Live2D 爱好者天堂**：大量角色、宠物、声音、IP 资源可供自由搭配（原文锚：Product features 第 3 条）
4. **行业领先 Live2D 技术**：角色动作流畅，视觉效果精美（原文锚：Product features 第 4 条）
5. **模型上传工具**：支持新手和专家快速完成模型设置和上传（原文锚：Product features 第 5 条）

### 3.3 与实际体验的差距

由于无法运行桌面端（Windows 独占），以下差距基于 Steam 用户评价（398 条，75% 好评率）推断：

| 卖点 | 官网原文 | 实际体验（基于评价推断） | 差距 |
|---|---|---|---|
| AI 对话质量 | "knowledgeable and articulate AI companion" | 用户评价显示部分用户反映 AI 回复质量不稳定，有机械感 | 官网承诺的"知识渊博"与实际 AI 能力可能存在落差 |
| 情感陪伴 | "like a real friend, always ready to chat" | 部分差评提及互动深度有限，重复性较高 | "真实朋友"级别的陪伴体验可能尚未达到 |
| 系统稳定性 | 未明确提及 | Early Access 阶段，部分用户报告崩溃/兼容性问题 | 官网未提示 Early Access 风险 |

---

## 4. 定价

产品通过 Steam 平台销售，定价策略极为亲民：

- **基础价格**：¥11.00（人民币）
- **折扣情况**：Steam 页面未显示当前折扣信息（HTML 中提取的价格为原价）
- **地区定价**：Steam 支持全球地区定价，不同区域价格可能有差异
- **附加内容**：Steam 页面未显示 DLC 或内购项目信息

¥11 的定价在 Steam 软件品类中属于低价区间，接近"冲动购买"阈值，降低了用户尝试门槛。结合"Sexual Content"标签和"Early Access"状态，这一低价策略可能是为了快速获取早期用户反馈。

---

## 5. 目标用户

基于 Steam 标签、视觉风格和功能描述推断：

1. **二次元/动漫文化爱好者**：产品视觉风格（粉发、萌系、Live2D）直接面向这一群体，证据：Steam 标签含 "Anime"、"Cute"、"JRPG"
2. **桌面美化/个性化用户**：产品核心功能是"桌面宠物"，面向希望自定义桌面体验的用户，证据：Steam 标签含 "Utilities"、"Software"、"Character Customization"
3. **虚拟主播/Vtuber 受众**：Live2D 技术是 Vtuber 行业的核心技术，产品支持模型上传，可能吸引已有 Live2D 模型的创作者，证据："Live2D enthusiasts" 在官网描述中被明确提及
4. **AI 陪伴产品早期尝试者**：对 AI 聊天、情感陪伴感兴趣的用户，证据：Steam 标签含 "Artificial Intelligence"、"Life Sim"

---

## 6. 与同类产品对比

| 对比维度 | Ai Vpet | 传统桌面宠物（如 QQ 宠物、Shimeji） | AI 聊天伴侣（如 Character.AI） |
|---|---|---|---|
| **核心形态** | Windows 桌面悬浮宠物 + AI 对话 | 桌面装饰性动画角色 | 纯 Web/App 对话界面 |
| **技术栈** | Live2D + 本地 AI/NLP | 传统 2D 帧动画或简单 Live2D | 大语言模型（云端） |
| **自定义深度** | 形象/性格/声音/宠物全自定义 | 有限（服装、动作） | 仅性格/背景设定 |
| **平台** | Windows（Steam） | 多平台 | Web/移动端 |
| **价格** | ¥11（一次性购买） | 免费为主 | 免费/订阅制 |
| **离线能力** | 有（本地运行） | 有 | 无（依赖网络） |

**关键差异点**：Ai Vpet 的独特定位在于将"桌面宠物"（本地、视觉化、持续性存在）与"AI 对话"（智能、个性化互动）结合，同时以极低价格（¥11）和 Live2D 视觉质量作为卖点。但相比 Character.AI 等云端 AI 产品，其 AI 能力受本地算力限制；相比传统桌面宠物，其价格门槛虽然低但仍非免费。

---

## 7. 优劣势小结

| 维度 | 优势 | 劣势 |
|---|---|---|
| 产品逻辑 | 创新的"AI + Live2D 桌面宠物"组合，填补了"有智能的桌面宠物"这一细分空白；¥11 极低定价降低尝试门槛 | Windows 独占，平台覆盖有限；Early Access 阶段功能尚未完善；AI 能力受本地算力制约 |
| UI/UX | Live2D 角色质量高，视觉风格统一且符合目标用户审美；自定义维度丰富（形象/性格/声音/宠物） | 商店截图未展示实际软件界面，用户购买前无法判断交互体验；官网文案存在机翻痕迹 |
| 工程质量 | Steam 平台分发保障基础交付质量；开发者持续更新（2024 年 8 月发布，处于活跃维护期） | 398 条评价中 25% 为差评，Early Access 稳定性存疑；"Sexual Content"标签可能限制部分用户群体 |

---

## 附录 A 截图索引

| # | 文件 | 说明 |
|---|---|---|
| 01 | screenshots/01_web_header.jpg | Steam 商店 header 宣传图（Desktop Pet 2.0） |
| 02 | screenshots/02_web_capsule.jpg | Steam 库列表展示图（YOUR AI BUDDY） |
| 03 | screenshots/03_web_page_bg.jpg | Steam 商店页面背景（粉紫渐变+花瓣） |
| 05 | screenshots/05_web_screenshot2.jpg | 产品截图：女仆装角色配语音图标 |
| 06 | screenshots/06_web_screenshot3.jpg | 产品截图：蝴蝶装饰角色形象 |
| 07 | screenshots/07_web_desktop.png | 沙盒 XFCE 桌面环境 |
| 08 | screenshots/08_web_steamdb_cf.png | SteamDB Cloudflare 人机验证页 |
| 09 | screenshots/09_web_steamdb.png | SteamDB 页面（菜单打开状态） |

> 编号规则：`NN_<source>_<view>.png`，`source ∈ {web}`，`NN` 单调递增。本次分析因产品 Windows 独占且沙盒 Firefox 渲染受限，web 段截图以 Steam 官方素材为主，沙盒操作截图为辅。
