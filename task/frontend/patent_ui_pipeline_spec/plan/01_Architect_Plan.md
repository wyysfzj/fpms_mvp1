# Patent UI Pipeline Dashboard — Implementation Plan

**Author**: Architect Agent
**Date**: 2026-02-22
**Status**: Approved by Team Lead

---

## 1. Executive Summary

This plan covers the implementation of a Pipeline Dashboard UI for the FPMS system, transforming the existing simple KPI-grid + todo-table dashboard into a three-layer Pipeline Dashboard that visualizes the complete business flow: **Client → Case → Task/Doc → FeeDraft → Bill → Payment → Offset**.

**Scope:**
- **Dashboard overhaul**: Replace 4 KPI cards + todo table with 4-card Pipeline visualization (top), a split-grid body with Action Center (left, 1.4fr) and Financial Loop (right, 1fr)
- **Financial Loop module**: New frontend component showing pending offset payments, overdue bills, and pending bills — the most significant net-new work
- **CSS token reconciliation**: Merge spec CSS into existing project via new `pipeline.css` file + token aliases
- **Backend API enrichment**: Enhance `GET /bills`, `GET /payments`, `GET /tasks`, `GET /cases` list endpoints to return fields needed for the dashboard
- **New Case drawer**: Slide-over drawer triggered from the first Pipeline card
- **All UI text**: Simplified Chinese

**Out of scope** (deferred):
- Case Detail page stepper (受理→初审→公布→实审→授权)
- Cases/Tasks list page visual redesign (cosmetic polish)
- Backend aggregation endpoints (frontend client-side reduce for MVP)
- Auto-refresh / real-time updates

---

## 2. Gap Analysis: Spec vs Current State

### 2.1 Dashboard Layer

| Spec Requirement | Current State | Gap | Priority |
|---|---|---|---|
| 4 Pipeline Cards with colored bars, pipe-bar/pipe-num/pipe-label | 4 simple KpiCard (label+value only) | Major component rewrite | P0 |
| Pipeline card 1 opens New Case drawer | Card is not clickable | Wire click + drawer | P0 |
| Pipeline card 2 shows urgent count badge | No urgent breakdown | Frontend filter on due_date | P1 |
| Pipeline card 3 shows unbilled draft sum (¥) | Shows `billsTotal` count only | Fee-draft sum aggregation | P0 |
| Pipeline card 4 shows unallocated payment sum | Not implemented | Payment aggregation logic | P0 |
| Split grid: Action Center (1.4fr) + Financial Loop (1fr) | Single full-width todo table | **New layout + Financial Loop** | P0 |
| Action Center: case-tag, client name, rel-tag, deadline badge | Table shows title, truncated case_id, due_date, status | Rewrite as list-item layout | P0 |
| Financial Loop: payment offset rows, overdue/pending bills | **Does not exist** | Build from scratch | P0 |

### 2.2 Backend Data Gaps

| Data Needed | Current Endpoint Response | Gap |
|---|---|---|
| Bill amount, balance, status, due_date | `GET /bills` returns `{id, bill_no, client_id, currency}` only | Must add 6 fields |
| Payment amount, currency | `GET /payments` returns `{id, pay_no, client_id, pay_date}` only | Must add 2 fields |
| Task case_no | `GET /tasks` has case_id but no case_no | Must add via JOIN |
| Case client_name | `GET /cases` has client_id but no client_name | Must add via JOIN |

### 2.3 Frontend Type Readiness

The frontend types are **already prepared** for enriched backend data:
- `BillListItem` (billing.types.ts:7-18) already has `client_name?`, `status`, `amount`, `balance`, `due_date?`
- `mapBillListItem()` (billing.ts:80-93) already maps these fields — backend just needs to send them
- `Task` (tasks.types.ts:5-17) already has `case_no?: string`
- Only `BackendTask` interface + `mapTask()` in tasks.ts need `case_no` passthrough

### 2.4 CSS Gap

| Spec Provides | Project Has | Reconciliation |
|---|---|---|
| `--primary`, `--warning`, `--danger`, `--success`, `--purple` | `--color-primary`, `--color-success`, `--color-danger` | Add `--color-warning`, `--color-purple`; create aliases |
| `.pipeline-grid`, `.pipe-card`, `.split-grid`, `.panel`, `.finance-row`, `.drawer-*` | `.kpi-grid`, `.kpi-card`, `.data-panel` | New `pipeline.css` file (additive, no overwrite) |
| `body.mode-immersive .dashboard-only { display: none }` | Immersive mode works via CSS variables | Add `.dashboard-only` hide rule |

---

## 3. Financial Loop Module — Detailed Design

### 3.1 Data Flow

```
Dashboard.vue onMounted
  │
  ├── fetchFinanceData()
  │     ├── getBills({ page_size: 50 })         ← requires BE-01 enrichment
  │     ├── getPayments({ page_size: 20 })      ← requires BE-02 enrichment
  │     │
  │     └── Client-side processing:
  │           1. overdueBills[] ← status=UNSETTLED AND due_date < today
  │           2. pendingBills[] ← status=UNSETTLED AND due_date >= today
  │           3. recentPayments[] ← all recent payments (shown as "待核销")
  │
  └── Render FinancePanel.vue
        ├── PaymentRow (green highlight, .finance-highlight)
        │     amount, "待核销 Payment" badge, date, "→ 关联账单" link
        ├── OverdueBillRow (.badge.urgent)
        │     bill_no, amount, "已逾期 N 天"
        └── PendingBillRow (.badge.warn)
              bill_no, amount, "待付款"
```

### 3.2 Component Structure

```
frontend/src/modules/dashboard/
  components/
    PipeCard.vue          ← NEW: pipeline card with colored bar
    ActionCenter.vue      ← NEW: left panel with enriched task list
    FinancePanel.vue      ← NEW: right panel with financial loop items
    FinanceRow.vue        ← NEW: single finance event row
    NewCaseDrawer.vue     ← NEW: slide-over case creation drawer
    KpiCard.vue           ← KEEP: may be retained for non-pipeline use
    TodoTable.vue         ← KEEP: may be retained for non-pipeline use
  pages/
    Dashboard.vue         ← MODIFIED: orchestrate new pipeline layout
  dashboard.api.ts        ← MODIFIED: add pipeline KPI + finance data fetchers
```

### 3.3 FinanceItem Interface

```typescript
interface FinanceItem {
  type: 'payment' | 'overdue_bill' | 'pending_bill'
  id: string
  label: string          // bill_no or "Payment #PAY-001"
  amount: number
  currency: string
  client_name?: string
  badge_text: string     // "待核销 Payment" | "已逾期 3 天" | "待付款"
  badge_class: 'urgent' | 'warn' | 'normal'
  date?: string
  highlight: boolean     // green background for payment rows
  action_label?: string  // "→ 关联账单 (Offset)"
  action_route?: string  // router-link target
}
```

---

## 4. Task Decomposition (17 Atomic Tasks)

### Phase 0: Backend API Enrichment (4 tasks)

#### BE-01: Enrich `GET /bills` list response
- **File**: `backend/app/modules/billing/api.py` → `get_bills()`
- **Change**: Add `status`, `amount`, `balance`, `due_date`, `bill_date` to each item dict. Add `client_name` via LEFT JOIN to `Client` on `bill.client_id`.
- **Current**: Returns `{id, bill_no, client_id, currency}` only
- **Frontend impact**: `mapBillListItem()` already handles these fields — no frontend change needed
- **Test**: Verify `GET /api/v1/bills` returns enriched fields

#### BE-02: Enrich `GET /payments` list response
- **File**: `backend/app/modules/billing/api.py` → `get_payments()`
- **Change**: Add `amount`, `currency` to each item dict
- **Current**: Returns `{id, pay_no, client_id, pay_date}` only
- **Frontend impact**: `mapPayment()` already handles `amount` via `asNumber()`
- **Test**: Verify `GET /api/v1/payments` returns amount and currency

#### BE-03: Enrich task list with `case_no`
- **File**: `backend/app/modules/tasks/api.py` → task list query
- **Change**: Add LEFT JOIN to `t_case` to populate `case_no` field in response
- **Frontend**: Update `BackendTask` interface + `mapTask()` in `frontend/src/api/tasks.ts` to pass through `case_no`
- **Test**: Verify `GET /api/v1/tasks` items include case_no

#### BE-04: Enrich case list with `client_name`
- **File**: `backend/app/modules/cases/api.py` → case list query
- **Change**: Add LEFT JOIN to `t_client` to populate `client_name` field
- **Test**: Verify `GET /api/v1/cases` items include client_name

---

### Phase 1: CSS Foundation (2 tasks)

#### FE-CSS-01: Add missing design tokens to variables.css
- **File**: `frontend/src/styles/variables.css`
- **Add tokens**:
  ```css
  --color-warning: #F59E0B;
  --color-purple: #8B5CF6;
  --color-primary-light: #EFF6FF;
  ```
- **Add spec alias block** so spec CSS class names work:
  ```css
  --primary: var(--color-primary);
  --success: var(--color-success);
  --warning: var(--color-warning);
  --danger: var(--color-danger);
  --purple: var(--color-purple);
  ```
- **Immersive overrides**: Also add aliases to `body.mode-immersive` block

#### FE-CSS-02: Create pipeline.css with all component styles
- **New file**: `frontend/src/styles/pipeline.css`
- **Import**: Add `import './styles/pipeline.css'` in `frontend/src/main.ts` after dashboard.css
- **Content** (adapted from spec `components.css`, using project variable names):
  - `.pipeline-grid` (4 columns, 24px gap, 140px height)
  - `.pipe-card`, `.pipe-bar`, `.pipe-num`, `.pipe-label`, `.pipe-hint`
  - `.split-grid` (1.4fr 1fr, 24px gap)
  - `.panel`, `.panel-header`, `.panel-title`, `.panel-link`
  - `.list-item`, `.task-title`, `.task-sub-row`
  - `.case-tag` (monospace, pill)
  - `.badge.urgent`, `.badge.warn` (colored bg + border)
  - `.rel-tag.doc`, `.rel-tag.fee` (blue/purple variants)
  - `.finance-row`, `.finance-highlight`, `.money-text`
  - `.drawer-backdrop`, `.drawer-panel`, `.drawer-header`, `.drawer-body`, `.drawer-footer`
  - `.back-btn`
  - `body.mode-immersive .dashboard-only { display: none !important; }`
  - `@media (max-width: 1100px)` responsive breakpoints

---

### Phase 2: Pipeline Cards (3 tasks)

#### FE-PIPE-01: Create PipeCard.vue component
- **New file**: `frontend/src/modules/dashboard/components/PipeCard.vue`
- **Props**: `barColor: string`, `value: string | number`, `label: string`, `hint?: string`, `badge?: { text: string, class: string }`
- **Template**: `.pipe-card > .pipe-bar[style="background:barColor"] + .pipe-num + .pipe-label + .pipe-hint`
- **Emits**: `@click`

#### FE-PIPE-02: Add pipeline KPI fetcher to dashboard.api.ts
- **File**: `frontend/src/modules/dashboard/dashboard.api.ts`
- **Add**: `fetchPipelineKpi()` function
- **Calls** (parallel):
  - `getCases({ page_size: 1 })` → `newCasesCount = total`
  - `getTasks({ page_size: 1, status: 'OPEN' })` → `pendingTasksCount = total`
  - `getFeeDrafts({ status: 'OPEN', page_size: 200 })` → sum `amount` fields → `unbilledDraftsAmount`
  - `getPayments({ page_size: 200 })` → sum `amount` fields → `unallocatedPaymentsAmount`
- **Returns**: `PipelineKpi` interface

#### FE-PIPE-03: Rewrite Dashboard.vue with pipeline layout
- **File**: `frontend/src/modules/dashboard/pages/Dashboard.vue`
- **Replace** `kpi-grid` → `pipeline-grid` with 4 PipeCard instances
- **Add** `split-grid` → ActionCenter (left) + FinancePanel (right)
- **Wire** PipeCard clicks: card1→drawer, card2→`/tasks`, card3→`/fees/drafts`, card4→`/billing/payments`
- **Wrap** panels in `<div class="dashboard-only">`
- **Skeleton loading** for pipeline cards + panels
- **Depends on**: All Phase 1-5 components

---

### Phase 3: Action Center (2 tasks)

#### FE-ACTION-01: Create ActionCenter.vue component
- **New file**: `frontend/src/modules/dashboard/components/ActionCenter.vue`
- **Props**: `tasks: EnrichedTask[]`, `loading: boolean`
- **Template**:
  ```
  .panel
    .panel-header → "待办任务" + "查看全部 →" link
    .list-item (v-for)
      .case-tag  → case_no (monospace)
      .task-title → title
      span       → client_name
      .rel-tag   → doc/fee (based on document_id)
      .badge     → deadline (urgent/warn/normal, computed from due_date)
  ```
- **Row click**: `router.push('/cases/' + task.case_id)`

#### FE-ACTION-02: Add enriched task fetcher
- **File**: `frontend/src/modules/dashboard/dashboard.api.ts`
- **Add**: `fetchEnrichedTasks()` function
- **Logic**:
  1. Fetch OPEN tasks (page_size=10)
  2. After BE-03: backend returns `case_no` directly
  3. Collect unique `case_id`s → batch fetch cases → get `client_id`s → batch fetch clients
  4. Join `client_name` client-side
  5. Compute `deadline_class`: urgent (<=3 days), warn (<=7 days), normal
- **Returns**: `EnrichedTask[]` with `case_no`, `client_name`, `deadline_class`, `deadline_text`
- **Depends on**: BE-03

---

### Phase 4: Financial Loop (2 tasks)

#### FE-FIN-01: Create FinancePanel.vue + FinanceRow.vue
- **New files**: `frontend/src/modules/dashboard/components/FinancePanel.vue`, `FinanceRow.vue`
- **FinancePanel**: `.panel > .panel-header("财务状况") > FinanceRow[] (v-for)`
- **FinanceRow**: `.list-item > .finance-row` with:
  - Left: label (bill_no or pay_no) + date
  - Right: `.money-text` (monospace amount) + `.badge` (urgent/warn/normal)
  - Conditional `.finance-highlight` class on payment rows (green bg)
- **Max 5 items** displayed

#### FE-FIN-02: Implement finance data fetcher
- **File**: `frontend/src/modules/dashboard/dashboard.api.ts`
- **Add**: `fetchFinanceData()` function
- **Logic**:
  1. Call `getBills({ page_size: 50 })` (requires BE-01)
  2. Call `getPayments({ page_size: 20 })` (requires BE-02)
  3. Classify:
     - Overdue bills: `status === 'UNSETTLED' && due_date < today`
     - Pending bills: `status === 'UNSETTLED' && due_date >= today`
     - Recent payments: all (shown as "待核销")
  4. Build `FinanceItem[]` sorted: payments (green) → overdue (red) → pending (yellow)
  5. Cap at 5 items
- **Depends on**: BE-01, BE-02

---

### Phase 5: New Case Drawer (2 tasks)

#### FE-DRAWER-01: Create NewCaseDrawer.vue
- **New file**: `frontend/src/modules/dashboard/components/NewCaseDrawer.vue`
- **Props**: `visible: boolean` (v-model)
- **Emits**: `update:visible`, `created(caseId: string)`
- **Template**:
  ```
  .drawer-backdrop(:class="{ open: visible }" @click.self="close")
    .drawer-panel
      .drawer-header → "新建案件"
      .drawer-body
        form-group: 客户 (el-select remote search, getClients)
        form-group: 案件类型 (el-select: 发明专利/实用新型/外观设计)
        form-group: 案件标题 (textarea)
      .drawer-footer
        btn-outline: 取消
        btn-primary: 创建案件
  ```
- **Submit**: calls `createCase()`, emits `created` with new case ID
- **Close**: ESC key, backdrop click, cancel button
- **Transition**: CSS `transform: translateX(100%)` → `translateX(0)`

#### FE-DRAWER-02: Wire drawer into Dashboard.vue
- **File**: `frontend/src/modules/dashboard/pages/Dashboard.vue`
- **Add**: `showDrawer` ref, `<NewCaseDrawer v-model:visible="showDrawer" @created="onCaseCreated" />`
- **PipeCard 1 click** → `showDrawer = true`
- **onCaseCreated** → `router.push('/cases/' + caseId)`
- **Depends on**: FE-PIPE-03, FE-DRAWER-01

---

### Phase 6: Labels & Type Updates (2 tasks)

#### FE-LABELS-01: Add pipeline Chinese labels
- **File**: `frontend/src/constants/labels.zh.ts`
- **Add sections**:
  ```typescript
  pipeline: {
    newCases: '新委托',
    pendingTasks: '待办任务',
    urgentSuffix: '绝限',
    unbilledDrafts: '待出账草稿',
    unallocated: '待核销',
  },
  actionCenter: {
    title: '待办任务',
    viewAll: '查看全部 →',
    relDoc: '关联文书',
    relFee: '关联费用',
    deadlineUrgent: '绝限: 剩{n}天',
    deadlineWarn: '剩{n}天',
  },
  finance: {
    title: '财务状况',
    pendingOffset: '待核销',
    overdue: '已逾期{n}天',
    pending: '待付款',
    offsetLink: '→ 关联账单',
  },
  drawer: {
    title: '新建案件',
    client: '客户',
    caseType: '案件类型',
    caseTitle: '案件标题',
    cancel: '取消',
    create: '创建案件',
  }
  ```

#### FE-TYPES-01: Update frontend API mappers for enriched responses
- **File**: `frontend/src/api/tasks.ts`
  - Add `case_no?: string | null` to `BackendTask` interface
  - Add `case_no: input.case_no || undefined` to `mapTask()` return
- **File**: `frontend/src/api/billing.ts` — verify `mapBillListItem` works (already does, no change expected)

---

## 5. Priority & Dependency Graph

```
Phase 0 (Backend — can run in parallel with Phase 1)
  BE-01 ──┐
  BE-02 ──┼──→ Phase 4 (FE-FIN-02)
  BE-03 ──┼──→ Phase 3 (FE-ACTION-02) + Phase 6 (FE-TYPES-01)
  BE-04 ──┘

Phase 1 (CSS — no dependencies, immediate start)
  FE-CSS-01 ──→ FE-CSS-02 ──→ All frontend component phases

Phase 2 (Pipeline Cards — depends on FE-CSS-02)
  FE-PIPE-01 ──→ FE-PIPE-02 ──→ FE-PIPE-03

Phase 3 (Action Center — depends on FE-CSS-02 + BE-03)
  FE-ACTION-01 ──→ FE-ACTION-02

Phase 4 (Finance Panel — depends on FE-CSS-02 + BE-01 + BE-02)
  FE-FIN-01 ──→ FE-FIN-02

Phase 5 (Drawer — depends on FE-CSS-02)
  FE-DRAWER-01 ──→ FE-DRAWER-02

Phase 6 (Labels/Types — minimal dependencies)
  FE-LABELS-01    (no dependencies)
  FE-TYPES-01     (depends on BE-03 being planned)

Assembly:
  All components ──→ FE-PIPE-03 (Dashboard.vue rewrite)
  FE-PIPE-03 + FE-DRAWER-01 ──→ FE-DRAWER-02 (wire drawer)
```

**Recommended execution order:**
1. **Wave 1** (parallel): BE-01, BE-02, BE-03, BE-04, FE-CSS-01, FE-LABELS-01
2. **Wave 2**: FE-CSS-02 (after FE-CSS-01)
3. **Wave 3** (parallel): FE-PIPE-01, FE-ACTION-01, FE-FIN-01, FE-DRAWER-01, FE-TYPES-01
4. **Wave 4** (parallel): FE-PIPE-02, FE-ACTION-02, FE-FIN-02
5. **Wave 5**: FE-PIPE-03 (dashboard assembly — integrates everything)
6. **Wave 6**: FE-DRAWER-02 (wire drawer into assembled dashboard)

---

## 6. API Contract Draft

### 6.1 Enhanced `GET /api/v1/bills` Response Item

```json
{
  "id": "uuid",
  "bill_no": "BILL-2023-109",
  "client_id": "uuid",
  "client_name": "小米移动",
  "currency": "CNY",
  "status": "UNSETTLED",
  "amount": "8500.00",
  "balance": "8500.00",
  "due_date": "2023-11-10",
  "bill_date": "2023-10-15"
}
```

### 6.2 Enhanced `GET /api/v1/payments` Response Item

```json
{
  "id": "uuid",
  "pay_no": "PAY-2023-055",
  "client_id": "uuid",
  "pay_date": "2023-11-12",
  "currency": "CNY",
  "amount": "50000.00"
}
```

### 6.3 Enhanced `GET /api/v1/tasks` Response Item

```json
{
  "id": "uuid",
  "case_id": "uuid",
  "case_no": "P2310-008",
  "title": "答复第一次审查意见 (OA1)",
  "due_date": "2023-11-15",
  "status": "OPEN",
  "worker_id": null,
  "supervisor_id": null,
  "remark": null,
  "created_at": "2023-10-01T00:00:00",
  "updated_at": "2023-10-01T00:00:00"
}
```

### 6.4 Enhanced `GET /api/v1/cases` Response Item

```json
{
  "id": "uuid",
  "case_no": "P2310-008",
  "case_type": "NORMAL",
  "client_id": "uuid",
  "client_name": "蔚来汽车",
  "title_cn": "一种激光雷达避障系统",
  "status": "ACTIVE"
}
```

---

## 7. Style C Immersive Mode — Switching Mechanism

### 7.1 Already Implemented (No Changes Needed)

- `useUIStore` manages `mode` state ('work' | 'immersive') with body class toggle
- `ModeToggle.vue` shows only on routes with `meta.supportsFocusMode: true`
- `variables.css` has `body.mode-immersive` overrides (teal primary, warm grey bg, serif font)
- `layout.css` has immersive rules (sidebar width→0, header height→0)

### 7.2 What Needs to Be Added

1. **Dashboard-only wrapper**: Wrap pipeline cards and split-grid in `<div class="dashboard-only">`
2. **CSS rule** (in pipeline.css):
   ```css
   body.mode-immersive .dashboard-only { display: none !important; }
   ```
3. Dashboard is NOT a `supportsFocusMode` route → ModeToggle won't appear there (correct behavior)

---

## 8. Impacted Files List

### Frontend — Modified

| File | Change |
|------|--------|
| `frontend/src/styles/variables.css` | Add `--color-warning`, `--color-purple`, `--color-primary-light`, spec aliases |
| `frontend/src/main.ts` | Add `import './styles/pipeline.css'` |
| `frontend/src/modules/dashboard/pages/Dashboard.vue` | Major rewrite: pipeline layout with all new components |
| `frontend/src/modules/dashboard/dashboard.api.ts` | Add `fetchPipelineKpi()`, `fetchEnrichedTasks()`, `fetchFinanceData()` |
| `frontend/src/constants/labels.zh.ts` | Add pipeline/actionCenter/finance/drawer label sections |
| `frontend/src/api/tasks.ts` | Add `case_no` to `BackendTask` interface + `mapTask()` |
| `frontend/src/api/billing.ts` | Verify mappers handle enriched response (likely no change) |

### Frontend — New Files

| File | Description |
|------|-------------|
| `frontend/src/styles/pipeline.css` | Pipeline, split-grid, finance, drawer, badge, tag styles |
| `frontend/src/modules/dashboard/components/PipeCard.vue` | Pipeline card with colored bar |
| `frontend/src/modules/dashboard/components/ActionCenter.vue` | Left panel: enriched task list |
| `frontend/src/modules/dashboard/components/FinancePanel.vue` | Right panel: financial loop |
| `frontend/src/modules/dashboard/components/FinanceRow.vue` | Single finance event row |
| `frontend/src/modules/dashboard/components/NewCaseDrawer.vue` | Slide-over case creation drawer |

### Backend — Modified

| File | Change |
|------|--------|
| `backend/app/modules/billing/api.py` | Enrich `get_bills()` + `get_payments()` list item dicts |
| `backend/app/modules/tasks/api.py` | Add LEFT JOIN to t_case for case_no in task list |
| `backend/app/modules/cases/api.py` | Add LEFT JOIN to t_client for client_name in case list |

---

## 9. Test Strategy

### 9.1 Backend Tests (pytest)

| Test | File | Description |
|------|------|-------------|
| test_bills_list_enriched | `backend/tests/test_billing_api.py` | Verify `GET /bills` returns amount, balance, status, due_date, client_name |
| test_payments_list_enriched | `backend/tests/test_billing_api.py` | Verify `GET /payments` returns amount, currency |
| test_tasks_list_with_case_no | `backend/tests/test_tasks_api.py` | Verify `GET /tasks` items include case_no |
| test_cases_list_with_client_name | `backend/tests/test_cases_api.py` | Verify `GET /cases` items include client_name |

### 9.2 Frontend Manual Smoke Tests

| Test | Expected Result |
|------|-----------------|
| Pipeline cards render | 4 cards with blue/yellow/purple/green top bars, correct values |
| Pipeline card 1 click | Opens New Case drawer |
| Pipeline card 2 click | Navigates to `/tasks` |
| Pipeline card 3 click | Navigates to `/fees/drafts` |
| Pipeline card 4 click | Navigates to `/billing/payments` |
| Action Center | Shows tasks with monospace case-tags, client names, deadline badges |
| Action Center row click | Navigates to `/cases/:id` |
| Finance Panel | Shows payment rows (green), overdue bills (red badge), pending bills (yellow badge) |
| New Case drawer submit | Creates case, navigates to case detail |
| New Case drawer cancel | Drawer closes, no side effects |
| Responsive 1100px | Pipeline: 4col→2col; Split grid: 2col→1col |

### 9.3 Quality Gates

```bash
# Frontend
cd frontend && npm run lint && npm run typecheck && npm run build

# Backend
cd backend && ruff check --fix . && ruff format . && pytest -q
```

---

## 10. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Backend enrichment breaks existing frontend mapping | Medium | High | Frontend `mapBillListItem()` already handles enriched fields; run full test suite |
| Fee draft sum with large datasets | Low | Medium | Cap `page_size=200`; display "近期" qualifier; TODO for backend aggregation |
| Payment "unallocated" inaccuracy | Medium | Medium | Show all recent payments as "待核销" for MVP; document limitation |
| CSS token conflicts | Low | Medium | Alias strategy: spec vars → project vars; no renaming |
| Font loading (JetBrains Mono, Noto Serif SC) | Low | Low | Already referenced in existing CSS; verify Google Fonts import |

---

## 11. Resolved Ambiguities

| Ambiguity | Resolution |
|-----------|-----------|
| Split grid ratio (2fr 1fr vs 1.4fr 1fr) | Use `1.4fr 1fr` per spec components.css (authoritative) |
| CSS strategy (merge vs separate) | New `pipeline.css` file + token aliases in `variables.css` |
| Task enrichment approach | Backend adds `case_no` (BE-03); frontend joins `client_name` client-side |
| Financial aggregation | Frontend-only for MVP; client-side reduce on bill/payment lists |
| "New Cases" metric (本周 vs total) | Show total count for MVP (no `created_after` filter available) |
| Payment "unallocated" detection | Show all recent payments as "待核销" for MVP |
| Case Detail stepper | Out of scope; track as separate task |
