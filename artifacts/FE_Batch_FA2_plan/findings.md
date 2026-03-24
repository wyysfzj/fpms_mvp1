# Batch FA2 — Findings Log

> Bugs, discoveries, and deviations found during execution.

---

## Backend API Filter Verification (Task #2 — backend-agent)

### Test Date: 2026-02-27

### 1. Document Direction Filter — `/api/v1/documents`
- **Status**: ✅ WORKS
- **Parameter**: `?direction=IN` or `?direction=OUT`
- **Type**: `DocumentDirection` enum (typed query param)
- **Valid values**: `IN`, `OUT`
- **Additional filters available**: `q`, `doc_template_id`, `case_id`, `client_id`, `date_from`, `date_to`
- **Test results**: ALL=0, IN=0, OUT=0 (empty DB but no errors, filter accepted)

### 2. Task Status Filter — `/api/v1/tasks`
- **Status**: ✅ WORKS
- **Parameter**: `?status=OPEN` / `?status=DONE` / `?status=CANCELLED`
- **Type**: `str | None` (free string, NOT typed as enum in API signature)
- **Valid values** (from `TaskStatus` enum): `OPEN`, `DONE`, `CANCELLED`
- **Additional filters available**: `due_from`, `due_to`, `worker_id`, `supervisor_id`, `case_id`, `client_id`
- **Test results**: ALL=0, OPEN=0, DONE=0, CANCELLED=0 (no errors)

### 3. Bill Status Filter — `/api/v1/bills`
- **Status**: ⚠️ NO STATUS FILTER EXISTS IN BACKEND
- **Finding**: The `get_bills` endpoint only accepts `page` and `page_size` parameters. There is NO `status` query parameter. Any `?status=X` param is silently ignored by FastAPI.
- **Bill model status field**: `String(24)`, default `UNSETTLED` — stored as free string, no enum defined
- **Impact**: Frontend cannot server-side filter bills by status. Options:
  1. Filter client-side only (acceptable for MVP with small datasets)
  2. Add backend filter (out of scope for FA2)
- **Recommendation**: Frontend should implement client-side filtering for bill status, or skip status filter for bills.

### 4. Fee Draft Status Filter — `/api/v1/fees/drafts`
- **Status**: ✅ WORKS
- **Parameter**: `?status=OPEN` or `?status=LOCKED`
- **Type**: `str | None` with `alias="status"` (mapped internally to `status_filter`)
- **Valid values** (from `FeeDraftStatus` enum): `OPEN`, `LOCKED`
- **Additional filters available**: `case_id`, `client_id`
- **Test results**: ALL=0, OPEN=0, LOCKED=0 (no errors)

---

## Summary Table

| Endpoint | Filter Param | Valid Values | Server-side? |
|----------|-------------|-------------|-------------|
| `/api/v1/documents` | `direction` | `IN`, `OUT` | ✅ Yes (typed enum) |
| `/api/v1/tasks` | `status` | `OPEN`, `DONE`, `CANCELLED` | ✅ Yes (string) |
| `/api/v1/bills` | `status` | N/A | ❌ No filter exists |
| `/api/v1/fees/drafts` | `status` | `OPEN`, `LOCKED` | ✅ Yes (string alias) |

## Critical Findings

### Finding #1: Bills endpoint missing status filter
**Bills endpoint missing status filter** — The frontend `BillList.vue` cannot use `?status=X` for server-side filtering. The param will be silently ignored and all bills returned regardless. Frontend must implement client-side filtering or accept no status filter for bills in FA2.

### Finding #2: TaskList.vue uses CLOSED but backend expects DONE
**Bug** — `TaskList.vue` line 20 sends `value="CLOSED"` for the "已完成" filter option, but the backend `TaskStatus` enum (`backend/app/modules/tasks/enums.py:8`) defines completed status as `DONE`, not `CLOSED`. This means filtering by "已完成" will silently return 0 results even when completed tasks exist. **Fix**: Change `value="CLOSED"` to `value="DONE"` in TaskList.vue.

---

## Task #4 — Test Agent Verification Report

### Test Date: 2026-02-27

### 1. Quality Gate
| Check | Result |
|-------|--------|
| `npm run lint` (--max-warnings 0) | ✅ PASS — 0 errors, 0 warnings |
| `npm run typecheck` (vue-tsc --noEmit) | ✅ PASS — no type errors |
| `npm run build` (vite build) | ✅ PASS — built in 3.05s, 1676 modules |

### 2. Backend Test Suite
- `pytest -q --tb=short`: **141 passed**, 3 warnings (deprecation only)
- No test failures or regressions

### 3. File Allowlist
- The 4 target files (`DocumentList.vue`, `TaskList.vue`, `BillList.vue`, `FeeDraftList.vue`) were already in the dirty set before FA2.
- No NEW files were added to the dirty set by FA2.
- ✅ PASS — no scope creep

### 4. Code Quality — Per-File Checklist

| Criteria | DocumentList | TaskList | BillList | FeeDraftList |
|----------|:---:|:---:|:---:|:---:|
| el-select filter control | ✅ L18 | ✅ L18 | ✅ L18 | ✅ L18 |
| `clearable` attribute | ✅ L18 | ✅ L18 | ✅ L18 | ✅ L18 |
| Filter wired to fetch | ✅ L132 | ✅ L170 | ✅ L127 | ✅ L137 |
| Page reset on change | ✅ L124 | ✅ L159 | ✅ L119 | ✅ L129 |
| Chinese labels | ✅ 全部/收文/发文 | ✅ 全部/待处理/已完成/已取消 | ✅ 全部/已开具/已付款/已作废 | ✅ 全部/开放/已锁定 |
| `onFilterChange()` handler | ✅ L123 | ✅ L158 | ✅ L118 | ✅ L128 |
| `filterXxx` ref typed | ✅ L120 | ✅ L155 | ✅ L115 | ✅ L125 |

### 5. API Filter Endpoint Tests (via curl)

| Endpoint | Filter | HTTP Status | Response |
|----------|--------|:-----------:|----------|
| `/api/v1/documents` | none | 200 | total: 0 |
| `/api/v1/documents?direction=IN` | IN | 200 | total: 0 |
| `/api/v1/documents?direction=OUT` | OUT | 200 | total: 0 |
| `/api/v1/tasks` | none | 200 | total: 0 |
| `/api/v1/tasks?status=OPEN` | OPEN | 200 | total: 0 |
| `/api/v1/tasks?status=DONE` | DONE | 200 | total: 0 |
| `/api/v1/bills` | none | 200 | total: 0 |
| `/api/v1/bills?status=ISSUED` | ISSUED | 200 | total: 0 (silently ignored — see Finding #1) |
| `/api/v1/fees/drafts` | none | 200 | total: 0 |
| `/api/v1/fees/drafts?status=OPEN` | OPEN | 200 | total: 0 |
| `/api/v1/fees/drafts?status=LOCKED` | LOCKED | 200 | total: 0 |

### 6. Bugs Found

1. **🐛 TaskList.vue CLOSED vs DONE mismatch** (Finding #2) — Filter value `CLOSED` doesn't match backend enum `DONE`. Completed tasks won't be filtered correctly.
2. **⚠️ BillList.vue status filter not server-side** (Finding #1) — Backend bills endpoint has no `status` query param; filter param is silently ignored. Not a frontend bug per se, but the filter dropdown gives a false impression of server-side filtering.

### 7. Overall Verdict

| Area | Status |
|------|--------|
| Quality Gate (lint/typecheck/build) | ✅ ALL PASS |
| Backend Tests (141 tests) | ✅ ALL PASS |
| File Scope | ✅ No scope creep |
| Code Structure & Patterns | ✅ Consistent across all 4 files |
| Filter Functionality | ⚠️ 2 of 4 have known issues (see bugs above) |

**Recommendation**: Fix the TaskList `CLOSED→DONE` mismatch before merging. The bills filter issue is a known backend limitation — acceptable for MVP but should be tracked as tech debt.
