# AI‑EOS PROMPT — DEMO‑UI‑02
## Title
DEMO‑UI‑02: Dashboard 工作台结构对齐 `reference/patent_ui.html`（KPI 卡片 + 待办表格 + 状态标签视觉）

## Context
当前 `/dashboard` 仍是 smoke test（例如“客户总数卡片”），不具备 Demo 的视觉冲击与业务叙事。需要对齐 `patent_ui.html` 的工作台结构与视觉（KPI、待办、tag）。

## Objective (Closed-loop)
1) 重做 `frontend/src/modules/dashboard/pages/Dashboard.vue` 的结构，使其观感对齐 `reference/patent_ui.html` 工作台：
   - 顶部区（标题/日期/辅助提示）
   - KPI 卡片区（4~6）
   - 待办表格（今日/近期任务）
   - 状态标签（el-tag 或自定义 tag）视觉对齐
2) KPI 必须至少 2 个来自真实 API 的 `total`（用 list endpoints `page_size=1` 取 total，不新增后端）。
3) 待办表格使用真实任务数据（优先 `tasks/today` 或现有 tasks list）。
4) 必须适配 DEMO‑UI‑00 的主题切换（A/B/C）——不写死颜色，使用 CSS 变量/ tokens / Element Plus variables。

## Non‑Goals (hard)
- 不新增后端接口
- 不在 Dashboard 引入复杂图表库
- 不重构其他模块页面

## File Allowlist (ONLY modify/add these)
- `frontend/src/modules/dashboard/pages/Dashboard.vue` (update)
- `frontend/src/modules/dashboard/components/KpiCard.vue` (new)
- `frontend/src/modules/dashboard/components/TodoTable.vue` (new)
- `frontend/src/modules/dashboard/dashboard.api.ts` (new; aggregates existing API calls)
- `frontend/src/styles/dashboard.css` (new; class-based, token-driven)
- `frontend/src/main.ts` (update ONLY if needed to import dashboard.css globally)
- Evidence:
  - `task/frontend/DEMO-UI/DEMO-UI-02_evidence.md`

If more files are needed: STOP and propose smallest follow-up task.

## Implementation Steps
### 1) Read `reference/patent_ui.html` and copy the “layout language”
- Identify:
  - KPI card proportions, typography, spacing
  - table density (row height, header style)
  - tag styles (active/paused/overdue etc)
- Implement equivalent structure using Element Plus `el-card` / `el-table` / `el-tag` (or lightweight divs if needed).

### 2) Implement dashboard.api aggregator
- Create `dashboard.api.ts` to fetch in parallel:
  - clients total
  - cases total
  - tasks today count (or tasks total)
  - optional: documents total / bills total (if existing list endpoints are stable)
- Use existing shared API modules (do not call fetch directly).
- Always handle loading/empty/error states.

### 3) Build KPI cards
- `KpiCard.vue` props:
  - title (中文)
  - value (number/string)
  - delta/secondary (optional)
  - status (optional)
- Use CSS variables for accent color (no hard-coded hex inside component).

### 4) Build Todo table
- `TodoTable.vue`:
  - columns: 标题/关联案件/截止日期/状态
  - status rendered as tag
  - row click -> navigate to task/case if available

### 5) Wire into Dashboard.vue
- Replace old smoke content.
- Ensure page still mounts inside MainLayout and works after login redirect to `/dashboard`.

### 6) Manual Verification
- 登录后 `/dashboard` 第一屏视觉对齐 `patent_ui.html`（截图对比）
- 切换主题 A/B/C 后 Dashboard 视觉明显变化且不破版
- Network 面板可看到 dashboard 的真实请求（至少 3 个）
- Loading/empty 状态不闪烁

## Gates (mandatory)
```bash
cd frontend
npm run lint
npm run typecheck
npm run build
```

## Evidence Log (mandatory)
Write `task/frontend/DEMO-UI/DEMO-UI-02_evidence.md`:
- Dashboard screenshots (A/B/C each)
- 2+ KPI 来源证明（Network 或 console log）
- Gates outputs
