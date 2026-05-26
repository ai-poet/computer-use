# Product Analyzer Console - UI/UX 改进方案

## 1. 当前问题诊断

### 1.1 全局层面

| 问题 | 严重程度 | 说明 |
|------|---------|------|
| 配色单调 | 高 | 仅 `#235789` 蓝色 + 灰白，无辅助色、无语义色层次，所有面板视觉权重相同 |
| 无暗色模式 | 高 | 长时间盯控制台的用户（开发者/分析师）在弱光环境下体验差 |
| 无过渡动画 | 中 | 状态切换、面板出现/消失都是瞬间跳变，缺乏流畅感 |
| 响应式薄弱 | 中 | 900px 断点仅做简单堆叠，侧边栏在移动端完全展开占用全屏 |
| 字体无层次 | 低 | 全站 15px 基础字号，标题、正文、辅助信息无区分 |

### 1.2 逐组件分析

#### ConsolePage（页面骨架）
- 四宫格布局 `grid-template-columns: 0.8fr 1.2fr`，ReportPanel 跨全列，但 Workflow + Log 高度不对齐
- 无全局 loading 状态，首次进入时各面板为空或显示占位文字
- 无错误边界，API 失败时页面白屏或卡住

#### TopBar
- 产品名和 URL 挤在一起，URL 过长时无截断/折叠
- 暂停/继续按钮永远 `disabled`，用户不知道功能是否存在
- 无状态指示器（运行中/暂停/完成），用户无法一眼看出当前任务状态
- 无面包屑或返回入口

#### RunSidebar
- 新建表单三个 input 无标签（仅靠 placeholder），可访问性差
- 无表单验证反馈，提交失败时用户不知道哪错了
- 任务列表无搜索/筛选，任务多时需要滚动很久
- 任务卡片信息密度低：只显示产品名 + 当前步骤，缺少状态图标、时间、进度
- 无空状态设计，`runs` 为空时只显示空白
- 刷新按钮和新建按钮视觉层级混乱

#### WorkflowPanel
- 只有小圆点表示状态，无进度条或完成百分比
- 步骤之间无连接线，看不出先后顺序和依赖关系
- 无步骤展开/折叠，所有 summary 一次性展示，信息过载
- `in_progress` 步骤无动画（如脉冲、呼吸灯），不够醒目
- 步骤标题和 summary 之间无视觉分隔

#### LogPanel
- `<pre>` 标签显示原始文本，无语法高亮（即使只是简单的时间戳/级别着色）
- 日志不会自动滚动到底部，用户需要手动滚动
- 无日志级别筛选（info/warn/error）
- 无复制/下载日志按钮
- 最大高度 420px 固定，大屏显示器浪费空间

#### CredentialPanel
- 表单字段固定为 username/password，不够灵活（有些产品需要 API Key、Token 等）
- 提交后无成功/失败反馈
- 无字段验证（空值、格式检查）
- 已提交的 credential 无历史记录展示

#### ReportPanel
- **最严重问题**：用 `<pre>` 显示原始 Markdown，标题、列表、代码块全部变成纯文本，完全无法阅读
- 无目录导航，长报告需要手动滚动
- 无导出/打印按钮
- 截图引用在 Markdown 中以 `![...](...)` 形式出现，但无实际图片渲染

---

## 2. 设计原则

### 2.1 核心原则

1. **信息密集但清晰** - 控制台类工具需要在一屏内展示大量信息，通过视觉层级和留白让信息可消化
2. **状态即界面** - 用颜色、动画、图标让用户无需阅读文字就能感知系统状态
3. **暗色优先** - 默认暗色模式（开发者场景），亮色模式作为可选
4. **渐进披露** - 不一次性展示所有信息，通过交互（hover、click）按需展开
5. **即时反馈** - 每个操作都有视觉响应，不超过 100ms

### 2.2 设计参考

- **Vercel Dashboard** - 暗色模式、卡片布局、状态指示
- **GitHub Actions** - Workflow 步骤可视化、日志展示
- **Linear** - 简洁的侧边栏、任务列表、表单设计
- **Stripe Dashboard** - 信息密度、表格、状态徽章

---

## 3. 颜色系统

### 3.1 亮色模式

```
Background
  bg-primary:   #ffffff      (主背景)
  bg-secondary: #f8fafc      (次级背景、侧边栏、卡片hover)
  bg-tertiary:  #f1f5f9      (输入框背景、代码块)
  bg-elevated:  #ffffff      (浮层、下拉菜单)

Surface (卡片、面板)
  surface:      #ffffff
  surface-hover:#f8fafc
  surface-active:#f1f5f9

Border
  border-subtle:#e2e8f0      (分割线、卡片边框)
  border-default:#cbd5e1     (输入框边框)
  border-strong:#94a3b8      (聚焦状态)

Text
  text-primary:   #0f172a    (标题、主文本)
  text-secondary: #475569    (正文、描述)
  text-tertiary:  #94a3b8    (辅助信息、placeholder)
  text-inverse:   #ffffff    (深色背景上的文字)

Primary (品牌色)
  primary-50:  #eff6ff
  primary-100: #dbeafe
  primary-200: #bfdbfe
  primary-300: #93c5fd
  primary-400: #60a5fa
  primary-500: #3b82f6      (主按钮、链接、active状态)
  primary-600: #2563eb      (hover状态)
  primary-700: #1d4ed8      (pressed状态)

Semantic Colors
  success-50:  #f0fdf4
  success-500: #22c55e      (完成、成功)
  success-600: #16a34a

  warning-50:  #fffbeb
  warning-500: #f59e0b      (警告、进行中)
  warning-600: #d97706

  error-50:    #fef2f2
  error-500:   #ef4444      (错误、失败)
  error-600:   #dc2626

  info-50:     #eff6ff
  info-500:    #3b82f6      (信息、提示)

Status-specific
  status-running:    #3b82f6   (蓝色脉冲)
  status-pending:    #94a3b8   (灰色)
  status-completed:  #22c55e   (绿色)
  status-failed:     #ef4444   (红色)
  status-paused:     #f59e0b   (黄色)
```

### 3.2 暗色模式

```
Background
  bg-primary:   #0a0f1a      (主背景 - 深蓝黑)
  bg-secondary: #111827      (侧边栏、次级背景)
  bg-tertiary:  #1e293b      (输入框、代码块)
  bg-elevated:  #1e293b      (浮层)

Surface
  surface:      #111827
  surface-hover:#1e293b
  surface-active:#334155

Border
  border-subtle:  #1e293b
  border-default: #334155
  border-strong:  #475569

Text
  text-primary:   #f1f5f9
  text-secondary: #94a3b8
  text-tertiary:  #64748b
  text-inverse:   #0f172a

Primary (暗色下更亮更饱和)
  primary-500: #60a5fa
  primary-600: #3b82f6
  primary-700: #2563eb

Semantic (暗色下保持辨识度)
  success-500: #4ade80
  warning-500: #fbbf24
  error-500:   #f87171
  info-500:    #60a5fa
```

### 3.3 模式切换

- 默认跟随系统 `prefers-color-scheme`
- 提供手动切换按钮（TopBar 右上角）
- 选择持久化到 `localStorage`
- 切换时添加 200ms 过渡动画

---

## 4. 间距和字体规范

### 4.1 间距系统 (4px 基线)

```
space-1:  4px   (图标内边距、紧凑间距)
space-2:  8px   (行内元素间距、小按钮padding)
space-3:  12px  (卡片内边距、表单字段间距)
space-4:  16px  (面板padding、段落间距)
space-5:  20px  (区块间距)
space-6:  24px  (大区块间距)
space-8:  32px  (页面级间距)
space-10: 40px  (大模块间距)
space-12: 48px  (最大间距)
```

### 4.2 字体规范

```
Font Family
  sans:  Inter, ui-sans-serif, system-ui, -apple-system, sans-serif
  mono:  JetBrains Mono, Fira Code, ui-monospace, monospace

Font Size
  text-xs:   12px / 16px   (标签、徽章、时间戳)
  text-sm:   13px / 18px   (辅助文字、表格内容)
  text-base: 14px / 20px   (正文、输入框)
  text-lg:   16px / 24px   (小标题、卡片标题)
  text-xl:   18px / 28px   (面板标题)
  text-2xl:  20px / 28px   (页面标题)
  text-3xl:  24px / 32px   (品牌名、大标题)

Font Weight
  normal:   400
  medium:   500  (按钮、标签)
  semibold: 600  (标题、强调)
  bold:     700  (品牌、大标题)

Line Height
  tight:  1.25  (标题)
  normal: 1.5   (正文)
  relaxed: 1.75 (长文本、报告)
```

### 4.3 圆角规范

```
radius-sm:  4px   (小按钮、标签、输入框)
radius-md:  6px   (按钮、卡片)
radius-lg:  8px   (面板、大卡片)
radius-xl:  12px  (模态框、浮层)
radius-full: 9999px (徽章、头像)
```

### 4.4 阴影规范

```
shadow-sm:  0 1px 2px rgba(0,0,0,0.05)      (卡片默认)
shadow-md:  0 4px 6px rgba(0,0,0,0.07)      (hover、下拉)
shadow-lg:  0 10px 15px rgba(0,0,0,0.1)     (模态框)
shadow-glow: 0 0 20px rgba(59,130,246,0.15) (运行中状态)
```

---

## 5. 逐组件改进方案

### 5.1 ConsolePage（页面骨架）

**改进内容：**
- 添加全局 `AppProvider` 包裹主题上下文
- 增加全局 loading 状态：首次加载 runs 时显示骨架屏（Skeleton）
- 增加错误边界（ErrorBoundary）：API 失败时显示友好错误页，带重试按钮
- 调整布局：侧边栏固定宽度 280px，主内容区自适应
- 大屏（>=1400px）时 Workflow + Log 并排，Report 下方全宽；中屏（900-1400px）保持当前；小屏（<900px）侧边栏可折叠为图标栏
- 添加全局 toast 通知容器（右上角）

**新增状态：**
- `isLoading` - 首次加载
- `error` - 全局错误
- `toast` - 通知消息

### 5.2 TopBar

**改进内容：**
- 左侧：产品名（20px semibold）+ 状态徽章（运行中/暂停/完成/失败）
- URL 移到第二行，14px 灰色，过长时截断并显示 `...`，hover 显示完整 tooltip
- 右侧操作区：
  - 暗色/亮色切换按钮（太阳/月亮图标）
  - 暂停/继续按钮（根据 run 状态动态启用/禁用）
  - 刷新按钮（旋转动画）
  - 设置按钮（下拉菜单：日志级别、自动滚动开关）
- 添加底部进度条（当任务运行时显示细蓝色进度条）
- 高度从 86px 调整为 64px，更紧凑

**新增元素：**
- `StatusBadge` 组件（见 6.4）
- 进度条 `<div className="h-0.5 bg-primary-500 transition-all">`

### 5.3 RunSidebar

**改进内容：**

**品牌区：**
- ShieldCheck 图标 + "Analyzer" 文字，添加版本号标签（如 v1.2.0）

**新建表单：**
- 每个输入框添加 `<label>` 标签，提升可访问性
- 产品名输入框：添加字符计数器（限制 80 字符）
- URL 输入框：实时验证 URL 格式，无效时边框变红并显示错误信息
- 下载链接输入框：可选，折叠在 "高级选项" 下，默认隐藏
- 提交按钮：加载状态显示 spinner，禁用重复提交
- 添加表单级错误提示（如 "产品名不能为空"）

**任务列表：**
- 顶部添加搜索框（实时过滤产品名）
- 添加筛选标签：全部 / 运行中 / 已完成 / 失败
- 任务卡片重新设计：
  ```
  [状态图标] 产品名                    [时间]
             当前步骤 / 模式           [进度条]
  ```
- 状态图标：圆形，带颜色（绿/蓝/黄/红）
- 进度条：细条，显示完成百分比
- Hover 效果：背景色变化，显示操作按钮（删除、查看详情）
- 空状态：显示插图 + "暂无分析任务，点击上方新建开始"（见 6.2）
- 加载状态：骨架屏 3-5 条（见 6.3）

**新增元素：**
- 搜索输入框
- 筛选标签组
- 任务卡片进度条

### 5.4 WorkflowPanel

**改进内容：**
- 步骤之间添加连接线（竖线），已完成段绿色，进行中段蓝色动画，未开始段灰色
- 小圆点升级为状态图标：
  - pending: 空心圆
  - in_progress: 蓝色实心圆 + 脉冲动画
  - completed: 绿色对勾
  - failed: 红色叉号
  - skipped: 灰色虚线圆
- 步骤标题加粗，summary 正常字重，两者间距加大
- 添加步骤序号（1, 2, 3...）
- 每个步骤可点击展开/折叠，显示详细信息（开始时间、耗时、输出摘要）
- 面板顶部添加进度百分比（如 "3/7 步骤已完成"）
- 添加预估剩余时间（如果有历史数据）

**动画效果：**
- 步骤完成时：圆点从灰变绿，带 300ms 过渡
- 进行中步骤：脉冲动画 `animation: pulse 2s infinite`
- 展开/折叠：高度过渡 200ms

### 5.5 LogPanel

**改进内容：**
- 保留 `<pre>` 但添加语法高亮：
  - 时间戳：灰色
  - `[INFO]` / `[WARN]` / `[ERROR]`：绿/黄/红
  - JSON 内容：结构化高亮（key 蓝色，string 绿色，number 橙色）
- 添加工具栏：
  - 日志级别筛选按钮组（All / Info / Warn / Error）
  - 自动滚动开关（默认开启）
  - 复制全部按钮
  - 清空按钮
  - 下载日志按钮（.log 文件）
- 自动滚动到底部（当用户没有手动向上滚动时）
- 添加行号
- 最大高度改为 `calc(100vh - 400px)`，自适应屏幕
- 空状态："等待事件..." 居中显示，带脉冲动画

**新增元素：**
- 工具栏
- 行号
- 日志级别筛选

### 5.6 CredentialPanel

**改进内容：**
- 表单字段动态化：根据 `pending.fields` 渲染对应输入框（不固定 username/password）
- 每个字段显示标签和说明
- 添加字段验证：
  - 必填字段不能为空
  - 邮箱格式验证
  - URL 格式验证
  - 密码最小长度
- 提交按钮状态：
  - 默认："加密保存并提交"
  - 提交中：显示 spinner + "提交中..."
  - 成功：绿色对勾 + "已提交"，2 秒后恢复
  - 失败：红色提示 + 重试按钮
- 已提交的 credential 显示为只读卡片（可折叠）
- 添加安全提示："凭证将加密存储，仅用于本次分析"

### 5.7 ReportPanel

**改进内容：**
- **核心改进**：用 `MarkdownRenderer` 组件替代 `<pre>`（见 6.5）
- 渲染后的报告包含：
  - 标题层级（H1-H4）带锚点
  - 列表（有序/无序）
  - 代码块（带语法高亮和复制按钮）
  - 表格
  - 引用块
  - 图片（截图画廊，见 6.1）
- 添加左侧目录导航（TOC），点击跳转对应章节
- 工具栏：
  - 导出 Markdown 按钮
  - 打印按钮
  - 展开/折叠全部按钮
- 报告生成中：显示骨架屏或 "报告生成中..." 带进度指示
- 空状态："最终报告尚未生成，请等待分析完成"（见 6.2）

---

## 6. 新增组件设计

### 6.1 ScreenshotGallery（截图画廊）

**用途**：在报告中展示产品截图，支持放大查看

**设计：**
```
+------------------------------------------+
|  截图索引 (8张)          [网格视图 ▼]    |
+------------------------------------------+
| +------+ +------+ +------+ +------+      |
| |      | |      | |      | |      |      |
| | 01   | | 02   | | 03   | | 04   |      |
| |web   | |web   | |app   | |app   |      |
| +------+ +------+ +------+ +------+      |
| +------+ +------+ +------+ +------+      |
| | 05   | | 06   | | 07   | | 08   |      |
| |android| |android| |web  | |web   |      |
| +------+ +------+ +------+ +------+      |
+------------------------------------------+
```

**功能：**
- 网格视图（默认）：4 列缩略图，带标签（web/app/android）
- 列表视图：详细信息（文件名、尺寸、来源）
- 点击缩略图打开 Lightbox 全屏查看
- Lightbox 支持左右切换、缩放、下载
- 空状态："暂无截图"

**Props：**
```typescript
interface ScreenshotGalleryProps {
  screenshots: {
    id: string;
    url: string;
    source: 'web' | 'app' | 'android';
    label: string;
    width?: number;
    height?: number;
  }[];
  viewMode?: 'grid' | 'list';
}
```

### 6.2 EmptyState（空状态）

**用途**：数据为空时的友好提示

**设计：**
```
+------------------------------------------+
|                                          |
|            [插图/图标]                   |
|                                          |
|         暂无分析任务                     |
|    点击左侧"新建"按钮开始产品分析        |
|                                          |
|         [+ 新建分析任务]                 |
|                                          |
+------------------------------------------+
```

**变体：**
- `empty` - 无数据（默认）
- `search` - 搜索无结果（带清除搜索按钮）
- `error` - 加载失败（带重试按钮）
- `loading` - 加载中（spinner）

**Props：**
```typescript
interface EmptyStateProps {
  variant: 'empty' | 'search' | 'error' | 'loading';
  title: string;
  description?: string;
  action?: {
    label: string;
    onClick: () => void;
  };
  icon?: LucideIcon;
}
```

### 6.3 LoadingState（加载状态）

**用途**：数据加载时的骨架屏

**设计：**
- 骨架屏：灰色脉冲块，模拟内容形状
- Spinner：旋转圆环，用于按钮/小区域加载
- 进度条：线性进度，用于长时间操作

**变体：**
- `skeleton` - 骨架屏（卡片、列表、文本行）
- `spinner` - 旋转图标（小区域）
- `progress` - 进度条（大区域）
- `skeleton-text` - 文本行骨架（3-5 行）
- `skeleton-card` - 卡片骨架（带标题、内容、操作区）

**Props：**
```typescript
interface LoadingStateProps {
  variant: 'skeleton' | 'spinner' | 'progress';
  count?: number;        // skeleton 行数
  progress?: number;     // 0-100
}
```

### 6.4 StatusBadge（状态徽章）

**用途**：统一的状态指示组件

**设计：**
```
[● 运行中]  [● 已完成]  [● 失败]  [● 暂停]
 蓝色        绿色        红色      黄色
```

**状态映射：**
| 状态 | 颜色 | 图标 | 动画 |
|------|------|------|------|
| running | primary-500 | 实心圆 | 脉冲 |
| pending | slate-400 | 空心圆 | 无 |
| completed | success-500 | 对勾 | 无 |
| failed | error-500 | 叉号 | 无 |
| paused | warning-500 | 暂停 | 无 |
| cancelled | slate-500 | 禁止 | 无 |

**Props：**
```typescript
interface StatusBadgeProps {
  status: 'running' | 'pending' | 'completed' | 'failed' | 'paused' | 'cancelled';
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;   // 是否显示文字
  pulse?: boolean;       // 是否脉冲动画
}
```

### 6.5 MarkdownRenderer（Markdown 渲染器）

**用途**：将 Markdown 文本渲染为富文本 HTML

**设计：**
- 使用 `react-markdown` + `remark-gfm` 支持 GitHub Flavored Markdown
- 代码块用 `react-syntax-highlighter` 高亮
- 自定义组件映射：

```typescript
const components = {
  h1: ({ children }) => <h1 className="text-2xl font-bold mt-8 mb-4">{children}</h1>,
  h2: ({ children }) => <h2 className="text-xl font-semibold mt-6 mb-3">{children}</h2>,
  h3: ({ children }) => <h3 className="text-lg font-medium mt-4 mb-2">{children}</h3>,
  p: ({ children }) => <p className="text-base leading-relaxed mb-4">{children}</p>,
  ul: ({ children }) => <ul className="list-disc pl-6 mb-4">{children}</ul>,
  ol: ({ children }) => <ol className="list-decimal pl-6 mb-4">{children}</ol>,
  li: ({ children }) => <li className="mb-1">{children}</li>,
  code: ({ inline, children }) => inline 
    ? <code className="bg-tertiary px-1.5 py-0.5 rounded text-sm">{children}</code>
    : <CodeBlock code={children} />,
  blockquote: ({ children }) => <blockquote className="border-l-4 border-primary-500 pl-4 italic my-4">{children}</blockquote>,
  table: ({ children }) => <table className="w-full border-collapse my-4">{children}</table>,
  img: ({ src, alt }) => <img src={src} alt={alt} className="max-w-full rounded-lg my-4" />,
  a: ({ href, children }) => <a href={href} className="text-primary-500 hover:underline" target="_blank">{children}</a>,
};
```

**CodeBlock 子组件：**
- 显示语言标签
- 复制按钮（点击后变对勾 2 秒）
- 行号（可选）
- 暗色/亮色主题适配

**Props：**
```typescript
interface MarkdownRendererProps {
  content: string;
  showToc?: boolean;      // 是否显示目录
  onHeadingClick?: (id: string) => void;
}
```

---

## 7. 交互改进

### 7.1 悬停效果

| 元素 | 悬停效果 |
|------|---------|
| 按钮 | 背景色变深，translateY(-1px)，阴影加深 |
| 卡片/面板 | 边框颜色加深，阴影出现 |
| 任务列表项 | 背景变为 bg-secondary，显示操作按钮 |
| 表格行 | 背景变为 bg-secondary |
| 链接 | 颜色变深，下划线出现 |
| 图标按钮 | 背景出现圆形底色 |

**过渡参数：**
- 时长：150ms
- 缓动：cubic-bezier(0.4, 0, 0.2, 1)
- 属性：background-color, border-color, box-shadow, transform, color

### 7.2 过渡动画

**页面级：**
- 暗色/亮色切换：200ms，所有颜色属性过渡
- 侧边栏展开/折叠：250ms，width 过渡

**组件级：**
- 面板出现：fade-in + slide-up，200ms
- 模态框出现：backdrop fade-in 150ms，内容 scale(0.95)→scale(1) + fade-in 200ms
- Toast 出现：slide-in from right，300ms；消失：fade-out，200ms
- 下拉菜单：fade-in + slide-down，150ms

**微交互：**
- 按钮点击：scale(0.97)，100ms
- 开关切换：translateX 过渡，200ms
- 复选框：scale(0.9)→scale(1)，150ms
- 脉冲动画（运行中）：opacity 0.5→1，2s infinite

### 7.3 表单验证

**实时验证（onBlur）：**
- 产品名：必填，1-80 字符
- URL：必填，有效 URL 格式（https:// 开头）
- 下载链接：可选，如填写则验证 URL 格式

**视觉反馈：**
- 验证中：输入框右侧显示 spinner
- 验证通过：输入框边框变绿，右侧显示对勾图标
- 验证失败：输入框边框变红，下方显示错误信息（红色 13px）
- 提交时：所有字段重新验证，失败字段自动聚焦

**错误信息样式：**
```
+------------------------------------------+
| 产品名 [输入内容                    ] ✓  |
+------------------------------------------+
| 官网 URL [输入内容                  ] ✗  |
| 请输入有效的 URL（以 https:// 开头）      |
+------------------------------------------+
```

### 7.4 键盘快捷键

| 快捷键 | 功能 |
|--------|------|
| Ctrl/Cmd + K | 聚焦搜索框 |
| Ctrl/Cmd + N | 新建分析任务 |
| Ctrl/Cmd + R | 刷新任务列表 |
| Esc | 关闭模态框/下拉菜单/全屏预览 |
| Ctrl/Cmd + Shift + L | 切换暗色/亮色模式 |

### 7.5 滚动行为

- 日志面板：自动滚动到底部（除非用户手动向上滚动）
- 报告面板：点击 TOC 平滑滚动到对应章节
- 任务列表：选中任务自动滚动到可视区域

---

## 8. 响应式设计

### 8.1 断点

```
sm: 640px   (手机横屏)
md: 768px   (平板)
lg: 1024px  (小桌面)
xl: 1280px  (桌面)
2xl: 1536px (大桌面)
```

### 8.2 布局适配

**大桌面（>=1280px）：**
- 侧边栏 280px 固定展开
- 主内容区 2 列网格（Workflow + Log 上排，Report 下排全宽）
- 最大内容宽度 1400px，居中

**桌面（1024-1280px）：**
- 侧边栏 240px
- 主内容区 2 列网格

**平板（768-1024px）：**
- 侧边栏可折叠为 64px 图标栏
- 主内容区单列
- 报告面板全宽

**手机（<768px）：**
- 侧边栏完全隐藏，通过汉堡菜单触发（抽屉式从左侧滑出）
- 单列布局
- 底部固定快捷操作栏（新建、刷新）
- 任务列表全屏显示

### 8.3 触摸适配

- 按钮最小点击区域 44x44px
- 滑动操作：任务列表项左滑显示删除按钮
- 下拉刷新：任务列表下拉刷新
- 捏合缩放：截图预览支持捏合缩放

---

## 9. 图标系统

继续使用 `lucide-react`，按场景规范使用：

| 场景 | 图标 | 说明 |
|------|------|------|
| 品牌 | ShieldCheck | 保持现有 |
| 新建 | Play | 保持现有 |
| 刷新 | RefreshCcw | 保持现有，添加旋转动画 |
| 暂停 | Pause | 保持现有 |
| 继续 | Play | 保持现有 |
| 日志 | Terminal | 保持现有 |
| 报告 | FileText | 保持现有 |
| 凭证 | KeyRound | 替换 Image，更准确 |
| 搜索 | Search | 新增 |
| 设置 | Settings | 新增 |
| 暗色/亮色 | Sun / Moon | 新增 |
| 复制 | Copy / Check | 新增 |
| 下载 | Download | 新增 |
| 删除 | Trash2 | 新增 |
| 展开/折叠 | ChevronDown / ChevronUp | 新增 |
| 关闭 | X | 新增 |
| 警告 | AlertTriangle | 新增 |
| 信息 | Info | 新增 |
| 成功 | CheckCircle2 | 新增 |
| 错误 | XCircle | 新增 |
| 截图 | Image | 保持现有 |
| 链接 | ExternalLink | 新增 |
| 日历 | Calendar | 新增（显示时间）|
| 时钟 | Clock | 新增（显示耗时）|

---

## 10. Tailwind CSS v4 配置建议

### 10.1 安装

```bash
npm install -D tailwindcss @tailwindcss/vite
```

### 10.2 Vite 配置

```typescript
// vite.config.ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    host: '127.0.0.1',
    port: 5173,
    proxy: {
      '/api': 'http://127.0.0.1:8765'
    }
  }
});
```

### 10.3 CSS 入口

```css
/* src/styles.css */
@import "tailwindcss";

@theme {
  /* 颜色 */
  --color-bg-primary: #ffffff;
  --color-bg-secondary: #f8fafc;
  --color-bg-tertiary: #f1f5f9;

  --color-surface: #ffffff;
  --color-surface-hover: #f8fafc;

  --color-border-subtle: #e2e8f0;
  --color-border-default: #cbd5e1;
  --color-border-strong: #94a3b8;

  --color-text-primary: #0f172a;
  --color-text-secondary: #475569;
  --color-text-tertiary: #94a3b8;
  --color-text-inverse: #ffffff;

  --color-primary-50: #eff6ff;
  --color-primary-100: #dbeafe;
  --color-primary-500: #3b82f6;
  --color-primary-600: #2563eb;
  --color-primary-700: #1d4ed8;

  --color-success-50: #f0fdf4;
  --color-success-500: #22c55e;
  --color-success-600: #16a34a;

  --color-warning-50: #fffbeb;
  --color-warning-500: #f59e0b;
  --color-warning-600: #d97706;

  --color-error-50: #fef2f2;
  --color-error-500: #ef4444;
  --color-error-600: #dc2626;

  /* 暗色模式颜色 */
  --color-dark-bg-primary: #0a0f1a;
  --color-dark-bg-secondary: #111827;
  --color-dark-bg-tertiary: #1e293b;

  --color-dark-surface: #111827;
  --color-dark-surface-hover: #1e293b;

  --color-dark-border-subtle: #1e293b;
  --color-dark-border-default: #334155;
  --color-dark-border-strong: #475569;

  --color-dark-text-primary: #f1f5f9;
  --color-dark-text-secondary: #94a3b8;
  --color-dark-text-tertiary: #64748b;

  /* 字体 */
  --font-sans: Inter, ui-sans-serif, system-ui, -apple-system, sans-serif;
  --font-mono: JetBrains Mono, Fira Code, ui-monospace, monospace;

  /* 间距 */
  --spacing-1: 4px;
  --spacing-2: 8px;
  --spacing-3: 12px;
  --spacing-4: 16px;
  --spacing-5: 20px;
  --spacing-6: 24px;
  --spacing-8: 32px;

  /* 圆角 */
  --radius-sm: 4px;
  --radius-md: 6px;
  --radius-lg: 8px;
  --radius-xl: 12px;
}

/* 暗色模式 */
.dark {
  --color-bg-primary: var(--color-dark-bg-primary);
  --color-bg-secondary: var(--color-dark-bg-secondary);
  --color-bg-tertiary: var(--color-dark-bg-tertiary);
  --color-surface: var(--color-dark-surface);
  --color-surface-hover: var(--color-dark-surface-hover);
  --color-border-subtle: var(--color-dark-border-subtle);
  --color-border-default: var(--color-dark-border-default);
  --color-border-strong: var(--color-dark-border-strong);
  --color-text-primary: var(--color-dark-text-primary);
  --color-text-secondary: var(--color-dark-text-secondary);
  --color-text-tertiary: var(--color-dark-text-tertiary);
  --color-text-inverse: #0f172a;
}

/* 基础样式 */
body {
  font-family: var(--font-sans);
  background-color: var(--color-bg-primary);
  color: var(--color-text-primary);
}

/* 自定义动画 */
@keyframes pulse-ring {
  0% { transform: scale(0.8); opacity: 0.5; }
  100% { transform: scale(2); opacity: 0; }
}

@keyframes skeleton {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}

.animate-pulse-ring {
  animation: pulse-ring 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

.animate-skeleton {
  background: linear-gradient(90deg, var(--color-bg-secondary) 25%, var(--color-bg-tertiary) 50%, var(--color-bg-secondary) 75%);
  background-size: 200% 100%;
  animation: skeleton 1.5s ease-in-out infinite;
}

/* 滚动条样式 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: var(--color-border-default);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: var(--color-border-strong);
}

/* 选中文字样式 */
::selection {
  background: var(--color-primary-100);
  color: var(--color-primary-700);
}
```

### 10.4 依赖包建议

```json
{
  "dependencies": {
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "lucide-react": "^0.468.0",
    "react-markdown": "^9.0.0",
    "remark-gfm": "^4.0.0",
    "react-syntax-highlighter": "^15.6.0"
  },
  "devDependencies": {
    "@types/react": "^19.0.0",
    "@types/react-dom": "^19.0.0",
    "@types/react-syntax-highlighter": "^15.5.13",
    "@vitejs/plugin-react": "^5.0.0",
    "tailwindcss": "^4.0.0",
    "@tailwindcss/vite": "^4.0.0",
    "typescript": "^5.7.0",
    "vite": "^6.0.0"
  }
}
```

### 10.5 目录结构调整建议

```
web/src/
├── main.tsx
├── App.tsx                    # 新增：主题 Provider + 错误边界
├── styles.css                 # Tailwind 入口 + 自定义样式
├── types.ts
├── api.ts
├── lib/
│   └── utils.ts               # 新增：cn() 工具函数（clsx + tailwind-merge）
├── context/
│   └── ThemeContext.tsx       # 新增：暗色/亮色模式上下文
├── hooks/
│   ├── useRuns.ts
│   ├── useRunStream.ts
│   └── useTheme.ts            # 新增：主题 hook
├── components/
│   ├── ui/                    # 新增：基础 UI 组件
│   │   ├── Button.tsx
│   │   ├── Input.tsx
│   │   ├── Badge.tsx
│   │   ├── Card.tsx
│   │   ├── Skeleton.tsx
│   │   ├── Spinner.tsx
│   │   ├── EmptyState.tsx
│   │   ├── StatusBadge.tsx
│   │   └── Toast.tsx
│   ├── layout/
│   │   ├── TopBar.tsx
│   │   ├── RunSidebar.tsx
│   │   └── MobileNav.tsx      # 新增：移动端导航
│   ├── panels/
│   │   ├── WorkflowPanel.tsx
│   │   ├── LogPanel.tsx
│   │   ├── CredentialPanel.tsx
│   │   └── ReportPanel.tsx
│   ├── report/
│   │   ├── MarkdownRenderer.tsx
│   │   ├── CodeBlock.tsx
│   │   ├── TableOfContents.tsx
│   │   └── ScreenshotGallery.tsx
│   └── providers/
│       └── ThemeProvider.tsx
└── pages/
    └── ConsolePage.tsx
```

---

## 11. 实施优先级

### P0（核心体验，必须做）
1. MarkdownRenderer 组件 - 报告无法阅读是最大痛点
2. 暗色模式 - 开发者场景刚需
3. StatusBadge + Workflow 改进 - 状态可视化
4. 表单验证 - 基础可用性

### P1（重要体验，尽快做）
5. EmptyState + LoadingState - 空/加载状态
6. LogPanel 改进（高亮、工具栏、自动滚动）
7. RunSidebar 搜索/筛选
8. 响应式改进（移动端可折叠侧边栏）

### P2（锦上添花，有空做）
9. ScreenshotGallery - 截图预览
10. 键盘快捷键
11. 触摸手势
12. 动画细节打磨

---

## 12. 验收标准

- [ ] 报告可正常阅读（Markdown 渲染正确）
- [ ] 暗色/亮色模式可切换，无闪烁
- [ ] Workflow 步骤有清晰的状态指示和进度感
- [ ] 表单有实时验证和错误反馈
- [ ] 空状态和加载状态有友好提示
- [ ] 移动端侧边栏可正常折叠/展开
- [ ] 所有交互有即时视觉反馈（hover、click）
- [ ] 日志自动滚动，支持级别筛选
- [ ] 截图可在报告中预览和放大
- [ ] 无控制台报错，无样式冲突
