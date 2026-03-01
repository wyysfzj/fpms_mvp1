# Evidence Log — DEMO-UI-02

## Task
- ID: DEMO-UI-02
- Title: Dashboard 工作台结构对齐 patent_ui.html（KPI + 待办表格 + 状态标签）
- Date: 2026-02-10
- Agent/Model: Claude Opus 4.6

## File Allowlist
- ✅ Confirmed all changes are within allowlist
- `frontend/src/modules/dashboard/pages/Dashboard.vue` — rewritten
- `frontend/src/modules/dashboard/components/KpiCard.vue` — **new**
- `frontend/src/modules/dashboard/components/TodoTable.vue` — **new**
- `frontend/src/modules/dashboard/dashboard.api.ts` — **new**
- `frontend/src/styles/dashboard.css` — **new**
- `frontend/src/main.ts` — updated (import dashboard.css)

## Commands Executed
```bash
cd frontend
npm run lint       # ✅ pass
npm run typecheck  # ✅ pass
npm run build      # ✅ pass (1640 modules, 2.84s)
```

## Key Outputs
- lint: 0 warnings, 0 errors
- typecheck: 0 errors
- build: ✓ 1640 modules transformed, built in 2.84s
- Dashboard.js chunk: 4.11 kB (up from 1.23 kB — expected due to new components)

## Changes Summary

### Dashboard.vue (rewritten)
- Structure aligned to patent_ui.html: header(title+date) → KPI grid → error banner → todo table
- Title: "工作台" with Chinese formatted date
- 4 KPI cards: 案件总数 / 待办任务 / 客户数量 / 账单总数
- TodoTable component with real task data
- Parallel loading of KPI and todo data (Promise.all)
- Loading skeleton for KPI area

### dashboard.api.ts (new)
- `fetchDashboardKpi()`: parallel calls to 5 existing endpoints (page_size=1 for count)
  - getClients, getCases, getTasks (all), getTasks (status=OPEN), getBills
- `fetchTodoTasks()`: getTasks with status=OPEN, page_size=10
- All using existing API modules (no direct http calls)
- Exports `DashboardKpi` interface

### KpiCard.vue (new)
- Props: label (string), value (number|string), sub (optional string)
- Value formatted with `toLocaleString('zh-CN')` for number grouping
- Styling via CSS variables (--color-bg-panel, --radius-card, --text-highlight etc.)

### TodoTable.vue (new)
- Props: tasks (Task[]), loading (boolean)
- Columns: 任务标题 / 关联案件 / 期限 / 状态
- Case column: shows truncated case_id with router-link (backend doesn't return case_no)
- Due date column: red text for tasks due within 3 days
- Status column: tag with Chinese labels (待处理/已完成/已取消)
- Empty state: "暂无待办任务"
- "查看全部" button links to /tasks

### dashboard.css (new)
- Layout classes: .dashboard-page, .dashboard-header, .kpi-grid, .data-panel
- All colors/sizes use CSS variables for theme compatibility
- Status tag classes: .tag-urgent, .tag-warning, .tag-normal
- .chain-link for monospace case ID links

## API Data Sources (verified)
| KPI | Endpoint | Field |
|-----|----------|-------|
| 案件总数 | GET /cases?page_size=1 | total |
| 待办任务 | GET /tasks?page_size=1&status=OPEN | total |
| 客户数量 | GET /clients?page_size=1 | total |
| 账单总数 | GET /bills?page_size=1 | total |
| 待办列表 | GET /tasks?page_size=10&status=OPEN | items |

## Manual Verification
### Steps
1. Login → /dashboard shows: title "工作台" + date, 4 KPI cards, todo table
2. KPI values loaded from real API (Network panel shows 5+ requests)
3. Theme style-b applied when VITE_DEMO_UI=1
4. Loading skeleton visible during fetch

### Results
- Gates: PASS

## UI Reference Alignment Notes
- patent_ui.html has 3 KPI cards in 3-col grid; we have 4 cards in auto-fit grid (responsive)
- patent_ui.html uses raw <table>; we use el-table (consistent with project)
- patent_ui.html status tags: 绝限警告/待答复/实审中; ours: 待处理/已完成/已取消 (matches actual task statuses)
- Tokens safety (variables.css base block unchanged): ✅

## Notes
- No `@/` path alias configured in project; all imports use relative paths
- Dashboard loads KPI and todo data in parallel for performance
- Error handling: individual promise catches, avoids full page error on partial failure
