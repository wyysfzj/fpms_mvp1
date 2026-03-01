# FPMS MVP1 Frontend Development Plan (Vue3 + TS + Pinia + Element Plus + Vite) — UI‑Aligned (v2)

> v2 修订点：  
> 1) **补齐 FE‑1‑01 的 Allowlist**（此前版本只保留了 Acceptance Criteria，导致参考不完备）。  
> 2) 新增 **“核心 CSS 变量（Tokens）与关键布局逻辑（Layout Logic）”** 作为后续 atomic tasks 的统一参照（来源：`reference/case_detail.html`）。fileciteturn1file1L10-L36  
> 3) 将 App Shell 的验收标准整合为“功能项 + 视觉项 + 约束项（禁 inline magic numbers）”。

---

## 0. 文档元信息
- **范围**：FPMS MVP1 Web 前端（对接已稳定的后端模块与 API 规范）
- **后端基址**：`http://localhost:8000/api/v1`
- **关键后端约束**：
  - JWT Bearer：`Authorization: Bearer <token>`
  - Error envelope：`{"error":{"code","message","details"}}`
  - List pagination：`{items, page, page_size, total}`
  - 常见状态码：401/403/422/409/200/201
- **执行原则**：AI‑EOS（Atomic / Evidence / Gated / No speculation / Stop on mismatch）

---

## 1) MVP1 成功标准（前端验收目标）
前端验收以**可复现业务链路**定义（FE‑3 需提供 UI smoke steps）：

1. **案卷链路可用**
   - 登录 → 案卷列表检索 → 新建案卷 → 案卷详情（tabs）→ 更新案卷字段（Formalities 全量 / Agent limited）
2. **文书与时限链路可用**
   - 案卷下登记来文/去文（document）→ 上传附件 → 任务队列可见/可创建任务 → 关闭/重开任务 → 今日提醒页可用
3. **费用到开票链路可用**
   - 维护收费标准（rate）→ 创建 fee draft → 添加 items → lock → 生成 bill → 打印 bill（下载/打开）
4. **回款/冲抵链路可用**
   - 登记 payment → offsets（以实际后端字段为准，不做假 UI）→ 案卷 receipts 汇总可查看

---

## 2) UI 风格规范（强约束：后续所有 atomic tasks 必须遵循）

### 2.1 设计目标：专利律师事务所的“现代 + 专业 + 高信息密度”
- **可信、克制**：冷静科技蓝为默认主色；界面稳定、可审计。
- **高效率**：列表/表格为主要载体，密度偏紧凑但可读。
- **强阅读体验**：长文本（权利要求、OA、答复）支持 Focus Mode（沉浸/专注模式），提升阅读与撰写体验。

### 2.2 双模式体系（Work / Focus）
UI 提供两种模式（默认 Work Mode；长文/撰写场景可切换 Focus Mode）：

- **Work Mode（默认：Modern Tech）**
  - 主色科技蓝、冷灰背景、白色面板、明确分割线
- **Focus Mode（沉浸/专注：Warm + Serif）**
  - 主色 Teal、暖灰护眼背景、弱化边框与阴影，阅读字体改衬线
  - 隐藏 Sidebar/Header、内容居中并收窄，形成“纸张感”阅读流

参考样例明确：Focus Mode 通过 `body.mode-immersive` 覆盖变量，并将 Sidebar/Header 尺寸置 0 来“视觉隐藏”。fileciteturn1file2L13-L29

### 2.3 核心 CSS Tokens（必须落地到 `src/styles/tokens.css`）
> 目标：避免页面内散落 magic numbers；所有颜色/尺寸/阴影/字体来自 tokens。

#### 2.3.1 Work Mode Tokens（基线）
按样例的核心变量抽象：fileciteturn1file1L10-L36
- Colors
  - `--fpms-color-primary: #2563EB;`（科技蓝）
  - `--fpms-bg-body: #F1F5F9;`
  - `--fpms-bg-panel: #FFFFFF;`
  - `--fpms-border: #E2E8F0;`
  - `--fpms-text-main: #1E293B;`
  - `--fpms-text-sub: #64748B;`
- Fonts
  - `--fpms-font-ui: "Inter", system-ui, sans-serif;`
  - `--fpms-font-read: "Inter", system-ui, sans-serif;`
  - `--fpms-font-mono: "JetBrains Mono", monospace;`
- Dimensions
  - `--fpms-sidebar-width: 240px;`
  - `--fpms-header-height: 60px;`
  - `--fpms-page-padding: 30px;`
  - `--fpms-radius: 6px;`
- Effects/Motion
  - `--fpms-shadow: 0 1px 3px 0 rgba(0,0,0,0.1);`
  - `--fpms-transition: all 0.4s cubic-bezier(0.25,0.8,0.25,1);`

> **兼容别名（推荐）**：为方便从样例迁移，可在 tokens.css 同时定义别名：  
> `--color-primary: var(--fpms-color-primary)` 等，使样例 class 可直接复用（不强制，但建议）。

#### 2.3.2 Focus Mode Tokens（`body.mode-immersive` 覆盖）
样例中 Focus Mode 的覆盖规则：fileciteturn1file1L38-L54
- `--fpms-color-primary: #0D9488;`
- `--fpms-bg-body: #F5F5F4;`
- `--fpms-bg-panel: #F5F5F4;`
- `--fpms-border: transparent;`
- `--fpms-text-main: #292524;`
- `--fpms-text-sub: #78716C;`
- `--fpms-font-read: "Noto Serif SC", serif;`
- `--fpms-sidebar-width: 0px;`（隐藏侧栏）
- `--fpms-header-height: 0px;`（隐藏顶栏）
- `--fpms-shadow: none;`

#### 2.3.3 Element Plus 变量映射（最小集合，强制）
将 tokens 映射到 Element Plus CSS Variables（以确保组件自动对齐风格）：
- `--el-color-primary: var(--fpms-color-primary);`
- `--el-bg-color: var(--fpms-bg-panel);`
- `--el-text-color-primary: var(--fpms-text-main);`
- `--el-text-color-regular: var(--fpms-text-sub);`
- `--el-border-color: var(--fpms-border);`
- `--el-border-radius-base: var(--fpms-radius);`

### 2.4 关键布局逻辑（后续实现必须对齐）
这些是样例中对“律所风格 + 双模式”的关键结构逻辑（作为实现约束）。

#### 2.4.1 App Shell 基本结构（Work Mode）
样例采用 body flex：Sidebar + MainContainer；MainContainer 内为 Header + ScrollContent。fileciteturn1file11L3-L56
- `body { height: 100vh; overflow: hidden; display: flex; }`
- `.sidebar { width: var(--sidebar-width); border-right: 1px solid var(--color-border); }`
- `.main-container { flex: 1; display: flex; flex-direction: column; }`
- `.top-header { height: var(--header-height); padding: 0 30px; border-bottom: 1px solid var(--color-border); }`fileciteturn1file0L11-L21
- `.content-scroll { flex: 1; padding: 30px; overflow-y: auto; }`fileciteturn1file0L33-L39

#### 2.4.2 Focus Mode 的“隐藏 + 阅读流”转换
Focus Mode 下：Header/Sidebar 变 0，高级信息（timeline、side-panel）隐藏，内容居中收窄。fileciteturn1file0L24-L44
- `body.mode-immersive .top-header { height: 0; opacity: 0; border-bottom: none; }`
- `body.mode-immersive .content-scroll { padding: 40px 15% 0 15%; }`
- `body.mode-immersive .timeline-wrapper { display: none; }`fileciteturn1file6L24-L27
- 两栏 → 单栏：`content-grid` 从 grid 切换为 block。fileciteturn1file3L15-L21
- 右侧 side-panel 隐藏：`body.mode-immersive .side-panel { display: none; }`fileciteturn1file3L48-L51
- 阅读区限制宽度、增大字号行高：max-width 760px、font-size 18、line-height 2.0。fileciteturn1file3L38-L43

#### 2.4.3 交互细节（用于后续任务验收）
- 搜索框 pill：border-radius 99px，宽 300px。fileciteturn1file0L28-L31
- Mode Toggle：固定右上角 pill button（hover 上浮 + 阴影）。fileciteturn1file5L12-L32

### 2.5 约束（为避免“风格跑偏”）
- 禁止在业务页面内硬编码颜色/阴影/圆角/间距（magic numbers）。
- 优先使用：
  - class + tokens（CSS variables）
  - Element Plus 组件（其变量已被 tokens 映射）
- inline style 仅允许在“临时调试”阶段出现；在 atomic task 完成前必须清理。

---

## 3) 工程与对接规范（后续任务必须遵循）
### 3.1 API Client（单一入口）
所有请求必须通过 `src/api/http.ts`：
- baseURL：`VITE_API_BASE_URL`（必须包含 `/api/v1`）
- 注入 Bearer token
- 错误归一化为 `ApiError { status, code, message, details?, requestId? }`
- 捕获 `X-Request-ID`
- 401 全局回登录（不允许页面各自处理 401）

### 3.2 会话（Pinia）
- Token key：`fpms_token`
- 启动 restore
- logout 清理 token + store

### 3.3 分页（统一类型）
列表页必须使用 `{ items, page, page_size, total }`，分页组件与 API 参数一致。

---

## 4) 分阶段交付计划（Atomic Task Register）
> 每个任务都是 PR-sized，并具备：
> - File Allowlist（精确到文件/目录）
> - Quality Gates：lint + typecheck + build
> - Evidence Log：命令与关键输出
> - Stop Condition：遇到 endpoint mismatch/CORS/auth 缺失 → 立即停止并提出最小修复任务

---

# Phase FE‑0：Bootstrapping & Standards

## FE‑0‑00：修复 Vite 入口 + 建立质量门禁 + 注入 UI Token 基线
**目标**
1) 项目可运行（dev/build）  
2) 项目具备 lint/typecheck 门禁  
3) 建立 UI Tokens + Base 样式（为后续“统一风格”打底）

**File Allowlist**
- `index.html`（新增；引入字体链接）
- `package.json`（新增 scripts：lint/typecheck；加入必要 devDeps）
- `tsconfig.json`（必要时）
- `vite.config.ts`（必要时）
- `src/vite-env.d.ts`（新增）
- `src/styles/tokens.css`（新增：tokens + Element Plus 变量映射 + Focus Mode 覆盖）
- `src/styles/base.css`（新增：全局 reset/背景/字体应用/滚动区域基础；尊重 reduced motion）
- `src/main.ts`（导入 `tokens.css/base.css`）
- ESLint config files（选择一种：`.eslintrc.cjs` 或 `eslint.config.js`）
- Evidence：`task/frontend/FE-0/FE-0-00_evidence.md`

**Quality Gates**
- `npm run lint`
- `npm run typecheck`（`vue-tsc --noEmit`）
- `npm run build`

**Acceptance Criteria**
- `npm run dev` 可启动并渲染页面
- `npm run build` 生成 `dist/`
- 页面背景/字体来自 tokens（可通过浏览器检查 CSS variables 验证）
- Focus Mode token 覆盖可通过给 body 手动加 `mode-immersive` 验证（无需做 UI 开关）

---

## FE‑0‑01：Auth + Session + API Client 归一化 + 路由守卫（闭环）
（保持不变，略）

---

# Phase FE‑1：Layout + Navigation + Global Error UX（UI 强对齐样例）

## FE‑1‑01：现代化 App Shell（Element Plus Layout + Sidebar + Header）+ 对齐样例风格
> v2：补齐 Allowlist，并将“功能项 + 视觉项 + 约束项”统一写入验收标准，兼容旧版与新版描述。

**Allowlist**
- `src/layout/MainLayout.vue`
- `src/components/layout/*`
- `src/components/nav/*`（若需抽离 sidebar 菜单项）
- `src/components/header/*`（若需抽离 header 子组件）
- `src/styles/*`
- `src/App.vue`

**Acceptance Criteria**
- **结构（功能项）**
  - Sidebar 使用 `el-menu`（支持折叠可选）
  - Header：系统名 + 面包屑/标题 + 用户下拉（logout）
  - 主内容区统一 padding/背景，内容区可滚动
- **视觉（样例对齐项）**
  - Sidebar 宽度默认 240px（来自 token），hover/active 外观对齐样例（hover 背景、active 背景与主色）。fileciteturn1file11L14-L35
  - Header 高度 60px（来自 token），左右 padding 30px（来自 token 或变量），包含搜索 pill（UI 可先放占位）。fileciteturn1file0L11-L31
  - Content 区 padding 默认 30px（来自 token），并支持 Focus Mode 的收窄阅读流（先支持 body class；toggle 在 FE‑1‑04）。fileciteturn1file0L33-L44
- **约束（必须）**
  - 移除 inline style 与 magic numbers：所有颜色/间距/圆角/阴影来自 tokens + class 驱动
  - `prefers-reduced-motion` 下不强制动画

## FE‑1‑02：RBAC-aware Navigation（best-effort + 403 兜底）
同原计划；菜单外观必须遵循 tokens（禁硬编码颜色）。

## FE‑1‑03：统一错误 UX（401/403/422/409）
同原计划；错误呈现组件在 Work/Focus Mode 下都需可读（不冲突）。

## FE‑1‑04：Focus Mode 基础设施（全局开关 + 持久化 + 可访问性）
**Allowlist（建议）**
- `src/stores/ui.ts`（或 `src/stores/app.ts`，用于 mode 状态与持久化）
- `src/components/layout/ModeToggle.vue`
- `src/main.ts`（启动时 restore mode 并设置 body class）
- `src/styles/tokens.css`（若需补充 mode 相关变量）
- `src/router/index.ts`（如需按路由 meta 控制 toggle 可见）

**Acceptance Criteria**
- mode 状态持久化：localStorage（例如 key：`fpms_ui_mode`，值：`work|immersive`）
- `body` 上切换 `mode-immersive` class
- Toggle 按钮可访问：`aria-pressed`、键盘可达
- 仅在“长文页面”（如 Case Claims / Official docs）显示 toggle（通过 route meta 控制）

---

## 5) 统一质量门禁（每个原子任务必须提供 Evidence Log）
每个任务必须运行并记录：
1) `npm run lint`
2) `npm run typecheck`
3) `npm run build`

Evidence Log 写入：
- `task/frontend/<phase>/<task_id>_evidence.md`

---

## 6) Stop Conditions（遇到即停止，提出最小修复任务）
- endpoint 与 docs/OpenAPI 不一致
- CORS 阻塞
- login 返回结构不同（token 字段名差异）
- 关键字段（如 offsets 所需字段）无法获取导致链路不可完成

遇到上述情况：停止当前任务，输出“最小修复任务”（含 allowlist + gates + evidence），不得做猜测性 workaround。
