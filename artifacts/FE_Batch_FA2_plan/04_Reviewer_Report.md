# FA2 Review Report — List UX Polish: Filter Dropdowns

> **Reviewer**: reviewer-agent
> **Date**: 2026-02-27
> **Verdict**: **PASS WITH 1 BUG**

---

## 1. Files Reviewed

| # | File | Lines | Filter Added |
|---|------|-------|-------------|
| 1 | `frontend/src/modules/documents/pages/DocumentList.vue` | 182 | Direction (IN/OUT) |
| 2 | `frontend/src/modules/tasks/pages/TaskList.vue` | 326 | Status (OPEN/CLOSED/CANCELLED) |
| 3 | `frontend/src/modules/billing/pages/BillList.vue` | 189 | Status (ISSUED/PAID/VOID) |
| 4 | `frontend/src/modules/fees/pages/FeeDraftList.vue` | 207 | Status (OPEN/LOCKED) |

**File allowlist compliance**: PASS — exactly 4 files modified, no new files created.

---

## 2. Acceptance Criteria Checklist

| # | Criterion | Status | Notes |
|---|-----------|--------|-------|
| 1 | DocumentList has direction filter dropdown (全部/收文/发文) | :white_check_mark: PASS | Line 16-24. Values: `''`, `IN`, `OUT` |
| 2 | TaskList has status filter dropdown | :warning: BUG | Line 16-25. Uses `CLOSED` instead of `DONE`. See Bug #1 |
| 3 | BillList has status filter dropdown (全部/已开具/已付款/已作废) | :white_check_mark: PASS* | Line 16-25. Missing `UNSETTLED` option. See Deviation #1 |
| 4 | FeeDraftList has status filter dropdown (全部/开放/已锁定) | :white_check_mark: PASS | Line 16-24. Values: `''`, `OPEN`, `LOCKED` |
| 5 | All filters reset page to 1 on change | :white_check_mark: PASS | All 4 files have `onFilterChange()` with `page.value = 1` |
| 6 | All filters pass value to API call | :white_check_mark: PASS | All use `filterX.value \|\| undefined` pattern |
| 7 | All el-select have `clearable` attribute | :white_check_mark: PASS | All 4 confirmed |
| 8 | Chinese labels on all options | :white_check_mark: PASS | See label audit below |
| 9 | No new files created | :white_check_mark: PASS | All modifications to existing files |
| 10 | Quality gate (lint + typecheck + build) | :hourglass: T4 | Pending T4 results |

---

## 3. Bugs

### BUG #1: TaskList filter sends `CLOSED` instead of `DONE` (Severity: Medium)

**File**: `TaskList.vue:21`
**Code**: `<el-option label="已完成" value="CLOSED" />`
**Expected**: `<el-option label="已完成" value="DONE" />`

**Root cause**: The backend `TaskStatus` enum (`backend/app/modules/tasks/enums.py:6-9`) defines:
- `OPEN = "OPEN"`
- `DONE = "DONE"`
- `CANCELLED = "CANCELLED"`

The `close` action sets task status to `DONE`, NOT `CLOSED`. The frontend filter sends `?status=CLOSED` which matches no records in the database.

**Evidence**: The frontend's own `displayText.ts:36-38` maps:
- `CLOSED` → '已关闭'
- `DONE` → '已完成'

So the label "已完成" should use value `DONE`, not `CLOSED`.

**Impact**: Users clicking "已完成" see zero results (or all results if backend doesn't filter unknown values). The filter appears broken for completed tasks.

**Fix**: Change `value="CLOSED"` to `value="DONE"` on line 21 of TaskList.vue.

---

## 4. Deviations from Architect Plan

### Deviation #1: BillList missing UNSETTLED option (Severity: Low)

**Plan** (Section 6.3): Options should be 全部/已开具(ISSUED)/已支付(PAID)/未结清(UNSETTLED)/已作废(VOID)
**Actual**: Options are 全部/已开具(ISSUED)/已付款(PAID)/已作废(VOID) — missing UNSETTLED.

**Assessment**: Low impact. `UNSETTLED` is the default bill status per backend, so omitting it means users can't filter for unsettled bills specifically. However, per findings.md, the backend `/api/v1/bills` endpoint does NOT support status filtering at all — the param is silently ignored. So this has no functional impact until the backend is updated.

**Additional note**: BillList uses label "已付款" instead of "已支付" from `displayText.ts`. Minor label inconsistency.

### Deviation #2: TaskList has 3 options instead of planned 4 (Severity: None)

**Plan** (Section 6.2): 4 options — OPEN, IN_PROGRESS, COMPLETED, CANCELLED
**Actual**: 3 options — OPEN, CLOSED(should be DONE), CANCELLED

**Assessment**: Correct behavior. The backend `TaskStatus` enum only has 3 values (OPEN, DONE, CANCELLED). The plan included `IN_PROGRESS` and `COMPLETED` which don't exist in the backend. The implementation correctly omitted `IN_PROGRESS` — this is actually better than the plan.

### Deviation #3: Filter placement (Severity: None — Positive)

**Plan**: Insert filter inside `<div v-else class="page-table">` block (before `<el-table>`)
**Actual**: Filter is placed BEFORE the conditional blocks (error/loading/empty/table)

**Assessment**: This is **better** than the plan. The filter is always visible regardless of loading state or empty results. Users can clear a filter that returned zero results without the filter disappearing. Good UX decision.

### Deviation #4: Placeholder text (Severity: None)

**Plan**: DocumentList uses "方向", others use "全部状态"
**Actual**: All use "全部"

**Assessment**: No impact. The select starts with value `''` which selects the "全部" option, so the placeholder is never visible.

---

## 5. Iron Rules Compliance

| Rule | Status | Evidence |
|------|--------|---------|
| No `@/` alias | :white_check_mark: PASS | All imports use relative `../../../` paths |
| No inline hex colors | :white_check_mark: PASS | All CSS uses `var(--color-*)`, `var(--font-*)`, `var(--text-*)` variables |
| Element Plus only | :white_check_mark: PASS | All UI components: `el-select`, `el-option`, `el-row`, `el-col`, `el-table`, `el-tag`, `el-button` |

---

## 6. Chinese Label Audit

### DocumentList.vue
| Label | Value | Correct? |
|-------|-------|----------|
| 全部 | `''` | :white_check_mark: |
| 收文 | `IN` | :white_check_mark: |
| 发文 | `OUT` | :white_check_mark: |

### TaskList.vue
| Label | Value | Correct? |
|-------|-------|----------|
| 全部 | `''` | :white_check_mark: |
| 待处理 | `OPEN` | :white_check_mark: |
| 已完成 | `CLOSED` | :x: Should be `DONE` (Bug #1) |
| 已取消 | `CANCELLED` | :white_check_mark: |

### BillList.vue
| Label | Value | Correct? |
|-------|-------|----------|
| 全部 | `''` | :white_check_mark: |
| 已开具 | `ISSUED` | :white_check_mark: |
| 已付款 | `PAID` | :white_check_mark: (minor: displayText uses '已支付') |
| 已作废 | `VOID` | :white_check_mark: |

### FeeDraftList.vue
| Label | Value | Correct? |
|-------|-------|----------|
| 全部 | `''` | :white_check_mark: |
| 开放 | `OPEN` | :white_check_mark: |
| 已锁定 | `LOCKED` | :white_check_mark: |

---

## 7. Code Quality Assessment

### Pattern Consistency
All 4 files follow the same implementation pattern:
1. `ref` declaration for filter variable
2. `onFilterChange()` resets page to 1 and calls fetch
3. `el-row > el-col > el-select` template block with `clearable` and `@change`
4. API call passes filter as `filterX.value || undefined`

This is clean and consistent. The pattern matches the spec in `task_plan.md`.

### Type Safety
- DocumentList: `filterDirection` typed as `'' | 'IN' | 'OUT'` — good
- TaskList: `filterStatus` typed as `string` (implicit) — acceptable
- BillList: `filterStatus` typed as `string` (implicit) — acceptable
- FeeDraftList: `filterStatus` typed as `'' | FeeDraftStatus` — good, uses imported type

### Known Backend Gap
Per `findings.md`, the `GET /api/v1/bills` endpoint does NOT support `status` filtering server-side. The frontend sends the param but it's silently ignored. Bills will not be filtered until the backend is updated. This is a known and documented gap.

---

## 8. Summary

| Metric | Count |
|--------|-------|
| Files reviewed | 4 (+ 4 API wrappers, + displayText.ts, + backend enums) |
| Bugs found | 1 (TaskList `CLOSED` → should be `DONE`) |
| Deviations from plan | 4 (1 low, 3 none/positive) |
| Iron rule violations | 0 |
| File allowlist violations | 0 |

### Verdict: **PASS WITH 1 BUG**

The implementation is clean, consistent, and follows the specified pattern well. The filter placement decision (before conditional blocks) is actually an improvement over the plan.

**Required fix before merge**: TaskList.vue line 21 — change `value="CLOSED"` to `value="DONE"` to match backend `TaskStatus` enum.

**Optional improvements** (not blocking):
1. Add `UNSETTLED` option to BillList filter for completeness
2. Align BillList "已付款" label with displayText.ts "已支付"
