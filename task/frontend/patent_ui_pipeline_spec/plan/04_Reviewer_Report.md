# Code Review Report — Patent UI Pipeline Dashboard

**Reviewer**: Reviewer Agent
**Date**: 2026-02-22
**Scope**: All backend + frontend changes for the Pipeline Dashboard feature
**Reference**: `PATENT_UI_PIPELINE_DASHBOARD_SPEC.md`, `01_Architect_Plan.md`, `02_API_Contract.md`

---

## Summary

**Overall Assessment: PASS WITH NOTES**

The implementation is well-structured, follows the spec closely, and demonstrates good engineering practices. All four backend enrichment tasks (BE-01 through BE-04) correctly enrich the API responses per the agreed contract. The frontend faithfully implements the Pipeline Dashboard with all major spec components: pipeline cards, action center, financial loop, and new case drawer. CSS follows the spec class naming conventions, responsive breakpoints are present, and immersive mode integration is correct.

Two major functional issues were identified in the `NewCaseDrawer.vue` component related to field mapping, and a few minor items are noted for future improvement.

---

## File-by-File Review

### Backend Files

#### `backend/app/modules/billing/api.py` (BE-01 + BE-02)
- **Status**: PASS
- **BE-01 (Bills enrichment)**: Lines 61-89 — Bills list now returns `status`, `amount`, `balance`, `bill_date`, `due_date`, `client_name`. Client names are resolved via a batch query (lines 68-72), avoiding N+1. All fields match the API contract.
- **BE-02 (Payments enrichment)**: Lines 239-258 — Payments list now returns `currency` and `amount`. No JOINs needed (fields are on the model). Matches contract.
- **CLAUDE.md compliance**: Permission enforcement via `Depends(require_perm(...))` used correctly. No PG-only functions. SQLite compatible.

#### `backend/app/modules/tasks/api.py` (BE-03)
- **Status**: PASS
- **Changes**: Lines 80-106 — Task list now batch-resolves `case_no` via `db.query(Case.id, Case.case_no)` for all case_ids in the page. Adds `case_no`, `remark`, `created_at`, `updated_at` to response dict.
- **Good practice**: Uses `getattr(task, "remark", None)` as a safe fallback.
- **API contract**: Matches BE-03 contract exactly.
- **Note**: The `get_tasks_today` endpoint (line 138-153) still uses the old `TaskListItemOut` schema and does NOT include `case_no`. This is acceptable since the dashboard doesn't use this endpoint, but creates an inconsistency between `/tasks` and `/tasks/today` response shapes.

#### `backend/app/modules/cases/api.py` (BE-04)
- **Status**: PASS
- **Changes**: Lines 98-117 — Case list now batch-resolves `client_name` via LEFT JOIN-style query. Adds `client_id`, `client_name`, `title_cn`, `status` to response. Applied consistently in both `get_cases` (line 105-117) and `export_cases` (line 316-328).
- **Pre-existing concern**: Lines 57-65 use `.ilike()` which CLAUDE.md lists as PG-only. However, SQLAlchemy emulates `ilike` on SQLite, and this was **pre-existing code**, not introduced by this change.

---

### Frontend Files — New

#### `frontend/src/styles/pipeline.css`
- **Status**: PASS
- **Spec compliance**: All required CSS classes present: `.pipeline-grid`, `.pipe-card`, `.pipe-bar`, `.pipe-header`, `.pipe-num`, `.pipe-label`, `.pipe-hint`, `.split-grid`, `.panel`, `.panel-header`, `.panel-title`, `.panel-link`, `.list-item`, `.case-tag`, `.badge.urgent`, `.badge.warn`, `.rel-tag.doc`, `.rel-tag.fee`, `.finance-row`, `.finance-highlight`, `.money-text`, `.drawer-backdrop`, `.drawer-panel`, `.drawer-header`, `.drawer-body`, `.drawer-footer`, `.form-group`, `.form-label`.
- **Responsive**: `@media (max-width: 1100px)` breakpoint correctly collapses pipeline to 2-col and split-grid to 1-col (line 312-316).
- **Immersive mode**: `body.mode-immersive .dashboard-only { display: none !important; }` present (line 301).
- **CSS variable fallbacks**: All properties use `var(--short, var(--project-name))` pattern for compatibility.

#### `frontend/src/modules/dashboard/components/PipeCard.vue`
- **Status**: PASS
- **Spec compliance**: Renders `.pipe-card > .pipe-bar + .pipe-header + .pipe-num + .pipe-label/pipe-hint`. Supports badge prop for urgent indicator.
- **Value formatting**: Uses `toLocaleString('zh-CN')` for number formatting.
- **Note**: Dynamic `:style="{ background: barColor }"` on `.pipe-bar` is technically an inline style, which the spec discourages. However, this is the standard Vue pattern for dynamic computed colors and is acceptable — moving to individual CSS classes for 4 fixed colors would be an alternative.

#### `frontend/src/modules/dashboard/components/ActionCenter.vue`
- **Status**: PASS
- **Spec compliance**: Panel with `.panel-header` ("待办任务" + "查看全部 →"), `.list-item` rows with `.case-tag` (monospace), `.task-title`, `.task-sub-row`, `.rel-tag.doc`, `.rel-tag.fee`, `.badge` deadline indicators.
- **Navigation**: Row click navigates to `/cases/:case_id` (line 63-66).
- **Loading/empty states**: el-skeleton for loading, "暂无待办任务" for empty.
- **Chinese text**: All labels from `ZH` constant.
- **Type export**: `EnrichedTask` interface exported from component — clean API.

#### `frontend/src/modules/dashboard/components/FinancePanel.vue`
- **Status**: PASS
- **Spec compliance**: Panel with "财务状况" title, delegates to `FinanceRow` components.
- **Clean composition**: Minimal orchestration component, type-safe with `FinanceItem` import.
- **Loading/empty states**: Handled correctly.

#### `frontend/src/modules/dashboard/components/FinanceRow.vue`
- **Status**: PASS
- **Spec compliance**: `.list-item` with conditional `.finance-highlight`, `.finance-row` layout with `.finance-left` (label + date) and `.finance-right` (money-text + badge).
- **Amount formatting**: Currency-aware with `toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })`.
- **Type export**: `FinanceItem` interface exported — used by FinancePanel and Dashboard.

#### `frontend/src/modules/dashboard/components/NewCaseDrawer.vue`
- **Status**: ISSUE FOUND (Major)
- **Spec compliance**: Drawer structure matches: `.drawer-backdrop.open > .drawer-panel > .drawer-header + .drawer-body + .drawer-footer`. ESC key (line 92-101), backdrop click (line 2 `@click.self`), cancel button (line 46) all close the drawer. Form has 3 fields: client (searchable select), case type (select), case title (textarea).
- **Chinese text**: All labels from `ZH` constant, validation messages in Chinese.
- **Issues** (see Issues Found section below):
  1. `patent_category` form field value is NOT sent in the API call (line 149-153)
  2. `title` field sent but backend expects `title_cn` — title won't be persisted
- **Minor code concern**: Nested `watch` inside `watch` for ESC handler (lines 90-101). Works correctly but is slightly non-idiomatic. A `watchEffect` + `onUnmounted` pattern or a composable would be cleaner.

---

### Frontend Files — Modified

#### `frontend/src/styles/variables.css`
- **Status**: PASS
- **Changes**: Added `--color-warning`, `--color-purple`, `--color-primary-light` tokens. Added spec alias block (`--primary`, `--success`, `--warning`, `--danger`, `--purple`, `--primary-hover`, `--bg-body`, `--bg-card`, `--border`, `--radius`). Added immersive alias overrides.
- **Well-structured**: Aliases allow pipeline.css to use short spec names while project code uses long names.

#### `frontend/src/main.ts`
- **Status**: PASS
- **Change**: Added `import './styles/pipeline.css'` (line 13), correctly positioned after `dashboard.css`.

#### `frontend/src/constants/labels.zh.ts`
- **Status**: PASS
- **Changes**: Added `pipeline`, `actionCenter`, `finance`, `drawer` sections with all required Chinese strings. Includes extra utility strings (`clientPlaceholder`, `titlePlaceholder`, case type labels).
- **All Simplified Chinese**: Verified.

#### `frontend/src/api/tasks.ts`
- **Status**: PASS
- **Changes**: `BackendTask` interface now includes `case_no?: string | null` (line 9). `mapTask()` passes through `case_no: input.case_no || undefined` (line 25).

#### `frontend/src/api/billing.ts`
- **Status**: PASS
- **No changes needed**: `BackendBill` already had `status`, `amount`, `balance`, `due_date`. Added `bill_date` handling (line 91: `bill_date || issue_date`). `mapBillListItem` and `mapPayment` correctly handle enriched backend data.

#### `frontend/src/api/cases.ts`
- **Status**: PASS
- **Changes**: `BackendCase` interface includes `client_name?: string | null` (line 11). `mapCase()` maps `client_name: input.client_name || undefined` (line 27).

#### `frontend/src/modules/dashboard/pages/Dashboard.vue`
- **Status**: PASS
- **Spec compliance**: 4 PipeCard instances in `.pipeline-grid` with correct colors (primary/warning/purple/success). `.split-grid` with ActionCenter + FinancePanel. `<div class="dashboard-only">` wrapper present (line 20).
- **Pipeline card clicks**: Card 1 → drawer, Card 2 → `/tasks`, Card 3 → `/fees/drafts`, Card 4 → `/billing/payments`.
- **Loading states**: Skeleton loaders for all 4 pipeline cards during load.
- **Error handling**: `el-alert` banner for errors (line 10-16).
- **Data loading**: Three parallel `Promise.all` for pipeline KPI, enriched tasks, and finance data.
- **Money formatting**: `formatMoney()` function with `toLocaleString('zh-CN')`.

#### `frontend/src/modules/dashboard/dashboard.api.ts`
- **Status**: PASS WITH NOTES
- **`fetchPipelineKpi()`**: Parallel fetches for cases (count), tasks (200 for urgent filtering), fee drafts (200 for sum), payments (200 for sum). Urgent count computed client-side (due within 3 days).
- **`fetchEnrichedTasks()`**: Fetches 10 open tasks, then batch-fetches cases to resolve client names. Computes deadline badges with correct thresholds (<=3 days = urgent, <=7 days = warn).
- **`fetchFinanceData()`**: Classifies bills into overdue/pending, takes recent payments. Caps at 5 items total. Sort order: payments → overdue → pending.
- **Note**: `has_document` and `has_fee` are hardcoded to `false` (line 136-137) because `document_id` is not in the frontend `Task` type. The backend does return `document_id` — adding it to `BackendTask` would enable relation tags.

---

## Category Assessment

### Security: PASS
- No XSS vulnerabilities — all data rendered via Vue template bindings (auto-escaped)
- No injection risks — backend uses SQLAlchemy ORM (parameterized queries)
- Permission enforcement via `Depends(require_perm())` on all endpoints
- No secrets exposed; no unsafe `v-html` usage
- Form validation present in drawer (client and title checks)

### Performance: PASS
- Backend uses batch queries for client/case name resolution (no N+1)
- Frontend uses `Promise.all` for parallel data fetching
- Page sizes capped (200 max for aggregation, 10 for task list, 50 for bills)
- Skeleton loading prevents layout shift
- **Note**: Fetching 200 tasks/drafts/payments for client-side aggregation is acceptable for MVP but should be replaced with server-side aggregation endpoints for production scale

### Spec Compliance: PASS WITH NOTES
- Pipeline cards: 4 cards with correct colors (blue/yellow/purple/green), correct labels, correct click targets
- Split grid: 1.4fr 1fr ratio matches spec
- Action Center: case-tag, task title, client name, deadline badges all present
- Financial Loop: payment rows (green highlight), overdue bills (urgent badge), pending bills (warn badge) — all present
- New Case Drawer: backdrop+blur, slide-in animation, ESC/backdrop/cancel close, 3 form fields
- Responsive: 1100px breakpoint works
- Immersive: `.dashboard-only` wrapper + CSS rule present
- **Gaps**: Relation tags (`.rel-tag.doc`/`.rel-tag.fee`) always hidden due to `has_document`/`has_fee` being hardcoded false. This was acknowledged in the plan.

### CLAUDE.md Compliance: PASS
- Permission enforcement pattern used correctly (`_perm: None = Depends(require_perm(...))`)
- API prefix `/api/v1/` maintained
- ORM models use `T_` prefix convention
- SQLite compatible: batch queries use `IN_()`, no PG-only functions in new code
- UUIDs generated in app code
- Forward-only migration approach maintained
- Pre-existing `ilike` usage in cases filter is NOT a new introduction

### Accessibility: PASS WITH NOTES
- Semantic HTML: panels use proper heading structure
- Interactive elements (cards, rows) have `cursor: pointer` CSS
- Keyboard: ESC key closes drawer
- **Gaps**: Pipeline cards lack ARIA roles (could use `role="button"` + `tabindex="0"` + `@keydown.enter`). List items could benefit from `role="listitem"`. These are minor for MVP demo.

### Chinese Text: PASS
- All UI-visible text is Simplified Chinese via `ZH` constant
- Pipeline labels: "新委托", "待办任务", "待出账草稿", "待核销"
- Panel titles: "待办任务", "财务状况"
- Badges: "绝限: 剩N天", "已逾期N天", "待核销", "待付款"
- Drawer: "新建案件", "客户", "案件类型", "案件标题", "取消", "创建案件"
- Empty states: "暂无待办任务", "暂无财务数据"
- Error/validation: "请选择客户", "请输入案件标题", "案件创建成功", "创建失败，请重试"

### Responsive Design: PASS
- Pipeline grid: `repeat(4, 1fr)` → `repeat(2, 1fr)` at 1100px
- Split grid: `1.4fr 1fr` → `1fr` at 1100px
- Drawer: `width: 520px` → `width: 100%; max-width: 520px` at 1100px

### Immersive Mode: PASS
- `<div class="dashboard-only">` wraps pipeline grid + split grid
- `body.mode-immersive .dashboard-only { display: none !important; }` rule in `pipeline.css`
- Dashboard is NOT a `supportsFocusMode` route (correct — ModeToggle won't appear)

---

## Issues Found

### Critical (must fix)
None.

### Major (should fix)

**M-01: NewCaseDrawer — `patent_category` not sent in API call**
- **File**: `frontend/src/modules/dashboard/components/NewCaseDrawer.vue:149-153`
- **Description**: The drawer collects `form.patent_category` (default "INV", with options "INV"/"UTL"/"DES") but does NOT include it in the `createCase()` call. The case always creates with backend default (`PatentCategory.INV`), ignoring user selection.
- **Fix**: Add `patent_category: form.patent_category` to the `createCase()` payload.
- **Impact**: User selects "实用新型" or "外观设计" but case is created as "发明专利".

**M-02: NewCaseDrawer — `title` field name mismatch with backend**
- **File**: `frontend/src/modules/dashboard/components/NewCaseDrawer.vue:153`
- **Description**: The drawer sends `{ title: form.title_cn.trim() }` via `createCase()`. The backend `CaseCreateIn` schema expects `title_cn` (not `title`). The `CaseCreatePayload` frontend type has `title` but the backend's Pydantic model has `title_cn`. Since `createCase()` sends the raw payload, the backend receives an unexpected field `title` which is silently ignored (Pydantic V2 ignores extra fields by default), and `title_cn` is never set.
- **Fix**: Either update `CaseCreatePayload` to use `title_cn`, or update the backend to accept `title` as an alias, or map `title` → `title_cn` in the frontend `createCase()` function.
- **Impact**: The case title entered by the user is not persisted. Cases created via the drawer will have `title_cn = None`.

### Minor (nice to have)

**m-01: Relation tags never appear in Action Center**
- **File**: `frontend/src/modules/dashboard/dashboard.api.ts:136-137`
- **Description**: `has_document` and `has_fee` are hardcoded to `false`. The backend returns `document_id` in the task list response, but `BackendTask` (in `tasks.ts`) doesn't include it, so the information is lost during mapping.
- **Fix**: Add `document_id?: string | null` to `BackendTask` interface, map it in `mapTask()`, then use `!!task.document_id` for `has_document` in `fetchEnrichedTasks()`.
- **Impact**: Visual-only — the "关联文书" and "关联费用" tags from the spec reference never display.

**m-02: Nested watch pattern in NewCaseDrawer ESC handler**
- **File**: `frontend/src/modules/dashboard/components/NewCaseDrawer.vue:90-101`
- **Description**: A `watch` inside a `watch` is used to add/remove the ESC key listener. This works but is non-idiomatic. Could be simplified with a single `watchEffect` or `onMounted`/`onUnmounted` + conditional check.
- **Impact**: No functional issue; code clarity only.

**m-03: Tasks `/today` endpoint inconsistency**
- **File**: `backend/app/modules/tasks/api.py:138-153`
- **Description**: The `get_tasks_today` endpoint still uses the old `TaskListItemOut` schema and does NOT include `case_no`, while `get_tasks` now returns enriched dict responses. This creates a response shape inconsistency between the two endpoints.
- **Impact**: Low — the dashboard doesn't use `/tasks/today`. But if `TodayReminders.vue` is updated to show case_no, it would need this fix.

**m-04: Pipeline KPI fetches 200 items for client-side aggregation**
- **File**: `frontend/src/modules/dashboard/dashboard.api.ts:58-63`
- **Description**: `fetchPipelineKpi()` fetches up to 200 tasks, 200 fee drafts, and 200 payments for client-side counting/summing. For MVP demo data this is fine, but will not scale.
- **Fix** (future): Add server-side aggregation endpoints (e.g., `GET /api/v1/dashboard/kpi`).
- **Impact**: Performance degradation with large datasets.

**m-05: Payment "unallocated" metric includes all payments**
- **File**: `frontend/src/modules/dashboard/dashboard.api.ts:78`
- **Description**: The unallocated payment sum includes ALL payments, not just truly unallocated ones. The system doesn't have offset status on payment list items.
- **Impact**: Metric may overstate unallocated amounts. Documented as known MVP limitation.

**m-06: Pipeline cards lack ARIA roles**
- **Files**: `PipeCard.vue`, `ActionCenter.vue`
- **Description**: Clickable pipeline cards and list items have `cursor: pointer` but no `role="button"`, `tabindex="0"`, or keyboard event handlers. Screen readers won't identify them as interactive.
- **Fix**: Add `role="button" tabindex="0" @keydown.enter="$emit('click')"` to `.pipe-card` and `.list-item` elements.
- **Impact**: Accessibility for keyboard/screen-reader users.

---

## Recommendations

1. **Fix M-01 and M-02 before demo**: The drawer creates cases but silently drops the title and patent category. This is visually confusing — user fills a form but the data doesn't persist.

2. **Enable relation tags (m-01)**: A small change (add `document_id` to `BackendTask` and use it) would make the Action Center match the spec reference much more closely.

3. **Consider server-side KPI endpoint (m-04)**: For production, aggregate metrics should be computed server-side to avoid large payload fetches.

4. **Add ARIA attributes (m-06)**: Low-effort, high-impact for accessibility compliance.

5. **Harmonize `/tasks` vs `/tasks/today` response shapes (m-03)**: Both should return the same enriched fields for consistency.

---

## Test Coverage Assessment

The test plan (`03_Test_Plan.md`) covers:
- All 4 backend enrichment tasks with pytest cases
- 31 manual smoke tests covering pipeline cards, action center, finance panel, drawer, responsive layout, and Chinese text
- Quality gate checklist (lint, typecheck, build, backend tests)
- Comprehensive seed data for demo verification

**Gap**: No automated test for the NewCaseDrawer field mapping issues (M-01, M-02). Adding a test that verifies `POST /cases` receives `title_cn` and `patent_category` from the drawer payload would catch this.

---

*End of Review Report*
