# Patent UI — Pipeline Dashboard Design Spec (for LLM agents)

**目标读者**：Codex / Gemini / Claude Code 等 coding agent  
**使用方式**：本 spec + `styles/*.css` + `reference/*.html` 作为“UI 规范与验收基准”，用于在 Vue3 SPA 中实现 Demo 级别的客户可展示界面。

---

## 1. 输入原型（Source of Truth）

本规范基于你提供的两份增强版原型（已打包在本目录 `reference/` 下）：

1) **静态稿**：`reference/newpatent_static.html`  
   - 覆盖完整的 Dashboard 视觉叙事：Pipeline + Action Center + **Financial Loop（财务状况）**
2) **带交互稿**：`reference/newpatent_interactive.html`  
   - 覆盖 SPA 交互模拟：视图切换（View Switch）、右侧抽屉（Slide-over Drawer）、详情 Drill-down、沉浸模式（Immersive）

> 注意：交互稿 Dashboard **遗漏“财务状况”面板**。本 spec 明确要求：交互实现必须把静态稿中的 Financial Loop 合并进 Dashboard。

---

## 2. UX 核心策略：Pipeline Dashboard（管道式仪表盘）

### 2.1 全景业务流（Top: Workflow Visualizer）
顶部 Pipeline 卡片组以 **数据流向**排列，使用户一眼看懂：
**Client → Case → Task/Doc → FeeDraft → Bill → Payment → Offset**

Pipeline 的设计意图不是“孤立 KPI”，而是“**业务成熟度的流动**”：
- **入口**：新委托/新建案（New Cases）
- **中段**：待办/绝限（Pending Tasks / Urgent Deadlines）
- **出账**：待出账单草稿（Unbilled Drafts）
- **回款闭环**：待核销金额（Unallocated / Pending Offset）

### 2.2 高频作业区（Left: Action Center）
左侧聚焦代理人每天最高频的工作：
- Task（期限、绝限）
- Document（关联文书）
每条任务必须显式展示 **案号 + 客户 + 关联对象 tag（Doc/Fee）+ 截止 badge**。

### 2.3 财务闭环（Right: Financial Loop）
右侧展示 FeeDraft → Bill → Payment → Offset 的财务闭环，并突出最后一步：
- **待核销（Pending Offset）**：Payment 已到帐但尚未核销到 Bill
- 逾期账单 / 待付款账单：突出风险与催收动作

---

## 3. 视觉风格（Style B）与沉浸模式（Style C）

### 3.1 默认风格：Style B（Modern Tech）
- 字体：Inter（UI），JetBrains Mono（案号/编号）
- 高密度信息排版、扁平圆角、强状态色标识（红/黄/绿/紫）
- 背景：冷灰 `--bg-body: #F1F5F9`，卡片：白底

### 3.2 沉浸模式：Style C（阅读/撰写）
通过切换 `body` class：`mode-immersive` 实现（交互稿中已给出同名机制）。

沉浸模式目标：
- 隐藏 Sidebar、Header、Right panel、Dashboard-only 元素
- 内容区宽度收敛到 `760px`（阅读最佳宽度）
- 文字切换为 `Noto Serif SC`（更适合长文阅读）

**CSS 已提供**：`styles/tokens.css`（含 `body.mode-immersive` override）

---

## 4. SPA 结构与路由映射（实现建议）

交互稿用 JS 做 view switch；真实产品用 Vue Router：

| 原型 View | SPA Route（建议） | 说明 |
|---|---|---|
| Dashboard | `/dashboard` | 默认登录后落地页 |
| Cases List | `/cases` | 高密度表格 |
| Case Detail | `/cases/:id` | Drill-down 阅读/撰写页 |
| Tasks List | `/tasks` | 交互稿预留但未实现 view；在 SPA 中应存在 |
| Clients | `/clients` | 交互稿仅展示入口；SPA 中存在 |

**关键约束**：页面跳转必须保留 SPA 性能与可预期行为，但视觉与交互细节遵循原型。

---

## 5. 页面级规范

## 5.1 Dashboard（/dashboard）

### A) 顶部 Pipeline（必须 4 卡）
卡片顺序与含义（必须一致）：
1. **New Cases**：新委托/新建案入口（点击 → 打开“新建案件抽屉”）
2. **Pending Tasks**：待办与绝限（点击 → 进入 Tasks 列表）
3. **Unbilled Drafts**：待出账草稿（点击 → 进入 FeeDraft/Billing 入口）
4. **Unallocated / Pending Offset**：待核销金额（点击 → 进入 Payments/Offsets 入口）

每张卡必须包含：
- 顶部色条（pipe-bar）：区分阶段（蓝/黄/紫/绿）
- 标题（pipe-header）
- 数值（pipe-num）：count 或 amount（¥）
- 底部说明（pipe-label 或 pipe-hint）

### B) Dashboard 主体 Split Grid（必须包含财务面板）
Dashboard 内容区必须是两栏结构：
- 左：Action Center（待办任务）
- 右：Financial Loop（财务状况）  ← **这是交互稿缺失项，必须补齐**

#### 左：待办任务（Action Center）
表现形式可以是 list 或 table，但必须具备：
- 案号 tag（monospace）
- 任务标题
- 客户名
- 关联 tag：`rel-tag doc|fee`（例如“关联文书：发文通知书”“关联费用”）
- 截止 badge：`badge urgent|warn|normal`

点击任一任务行 → Drill-down 进入 Case Detail（或 Task Detail，但必须能到达 Case Detail）。

#### 右：财务状况（Financial Loop）
至少展示 3 条“财务事件/对象”，推荐结构对齐静态稿：
1) **Payment（待核销）**：绿色高亮，显示金额 + “待核销 Payment” badge + “关联账单（Offset）”入口  
2) **Overdue Bill**：显示 Bill 编号 + 金额 + “已逾期 N 天” badge（urgent）  
3) **Pending Bill**：显示 Bill 编号 + 金额 + “待付款” badge（warn）

---

## 5.2 Cases 列表（/cases）

- 高密度 data grid / table
- 搜索与筛选区（可先做轻量：search input + 过滤 dropdown）
- 列字段（交互稿示例）：
  - 案号（monospace）
  - 客户
  - 案件名称
  - 阶段（tag：蓝/绿/…）
  - 申请日
  - 负责人
- 行 hover 高亮
- 点击行 → `/cases/:id`

---

## 5.3 Case Detail（/cases/:id）

### A) 内容区（Doc Area）
- 标题（案件名称）
- 元信息：案号、申请日等
- Stepper（受理/初审/公布/实审中/授权…），active 状态清晰
- Long-form 内容（如 Claims），使用 `--font-read`，行高 1.7+ 适合阅读

### B) 右侧面板（Right Panel）
- 绝限提醒（Deadline），红底强调
- 关联任务列表（简洁）

### C) 沉浸模式开关（Immersive Toggle）
- 仅在 Case Detail 页面显示“进入沉浸模式”按钮
- 点击切换 `body.mode-immersive`
- 离开 Case Detail 路由时必须自动退出沉浸模式（避免污染其他页面）

---

## 6. 关键交互规范（从交互稿提炼）

> 交互稿 JS 参考已打包：`scripts/spa_view_simulation.js`  
> 在 Vue 实现中对应：router navigation + drawer state + body class toggles。

### 6.1 New Case 抽屉（Slide-over Drawer）
触发：Dashboard 的第一张 Pipeline 卡（New Cases）或 Cases 列表页的 “+ 新建案件”。

交互：
- 背景变暗并 blur
- 右侧面板滑入（宽 ~500px）
- ESC / 点击遮罩 / Cancel 可关闭
- Create 成功后关闭抽屉并导航至新建 Case 的 detail

表单字段（最小集）：
- 客户选择（搜索/下拉）
- 案件类型（发明/实用/外观）
- 案件标题
- 内部案号（自动生成/只读）

### 6.2 View Switch（列表视图切换）
触发：Sidebar “案件 (Cases)” → `/cases`  
表现：内容区域切换为 data grid，保持 App Shell 不刷新。

### 6.3 Drill Down（从待办进入详情）
触发：Dashboard 待办列表点击行  
表现：进入 Case Detail，显示沉浸开关。

### 6.4 全局返回机制
在列表页与详情页顶部提供：
- Back 按钮 或 breadcrumb
- 能快速回到 Dashboard

---

## 7. 组件/样式规范（LLM 实现必须遵循）

### 7.1 禁止 inline style（Vue 侧）
原型 HTML 有 inline style；在 Vue 代码中必须改为 class + CSS（提供的 `styles/*.css`）。

### 7.2 关键 CSS 类（必须复用，不随意改名）
- Layout: `app-shell`, `sidebar`, `header`, `scroll-area`
- Pipeline: `pipeline-grid`, `pipe-card`, `pipe-bar`, `pipe-header`, `pipe-num`, `pipe-label`, `pipe-hint`
- Panels: `split-grid`, `panel`, `panel-header`, `panel-title`, `panel-link`
- Task: `list-item`, `case-tag`, `rel-tag doc|fee`, `badge urgent|warn|normal`
- Finance: `finance-row`, `finance-highlight`
- Table: `data-table`, `tag blue|green`
- Drawer: `drawer-backdrop`, `drawer-panel`, `drawer-header`, `drawer-body`, `drawer-footer`
- Detail: `case-detail-container`, `doc-area`, `right-panel-area`, `stepper`, `step active`
- Immersive: `body.mode-immersive`

---

## 8. 数据绑定建议（与后端实体关系保持一致）

本 spec 强调展示 **实体关系链与流转**，因此 Dashboard 的数据建议来自真实 API：

- New Cases：Cases（按近 7 天创建）
- Pending Tasks：Tasks（开放状态）+ urgent count（due_date 近）
- Unbilled Drafts：FeeDraft（未 lock/未出 Bill）合计金额
- Unallocated：Payments（未完全核销）合计金额

如果后端没有相应过滤/汇总接口：
- 允许前端以 list + client-side reduce 计算（分页限制下可先展示近 N 条 + 标注“近 30 天”）
- 或展示占位，但必须保留结构与视觉（Demo 友好）

---

## 9. 输出文件清单（本包）

- `PATENT_UI_PIPELINE_DASHBOARD_SPEC.md`（本文件）
- `styles/tokens.css`（CSS variables + immersive override）
- `styles/layout.css`（App Shell 布局）
- `styles/components.css`（Pipeline/Panel/Table/Drawer/Detail 等组件）
- `scripts/spa_view_simulation.js`（交互稿原始 JS 逻辑，供映射到 Vue）
- `reference/newpatent_static.html`（静态稿）
- `reference/newpatent_interactive.html`（交互稿）
