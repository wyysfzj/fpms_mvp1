# Batch FA1 — Findings Log

> Bugs, discoveries, and deviations found during execution.

---

## Backend API Verification (Task #2)

**Verified by**: backend-agent
**Date**: 2026-02-26
**Backend**: http://localhost:8000 (running, healthy)

### 1. Case Detail — `GET /api/v1/cases/{case_id}`

**Status**: PASS
**Code location**: `backend/app/modules/cases/api.py:609-742`

**Response includes sub-table arrays**:
- `applicants[]` — array of `{seq, is_first, name_cn, name_en, address_cn, address_en}`
- `inventors[]` — array of `{seq, name_cn, name_en}`
- `priorities[]` — array of `{seq, country_code, prio_no, prio_date}`

**Full response key fields**:
```
id, case_no, case_type, patent_category, flow_dir,
client_id, client_name (resolved), title_cn, title_en,
app_no, status, filing_date, recv_date,
pub_date, pub_no, grant_date, grant_no, patent_no, valid_until,
spec_pages, claim_count, has_exam_request,
primary_agent_id, second_agent_id, draftor_id,
is_fee_monitor, fee_reduction, applicant_kind,
applicants[], inventors[], priorities[],
created_at, updated_at
```

**Sample data**: Case V3-001 has 1 applicant (蔚来汽车科技有限公司), 1 inventor (张伟), 0 priorities.

### 2. Documents — `GET /api/v1/documents?case_id={case_id}`

**Status**: PASS
**Code location**: `backend/app/modules/documents/api.py:121-191`

**Query params supported**: `q`, `direction` (IN/OUT), `doc_template_id`, `case_id`, `client_id`, `date_from`, `date_to`, `page`, `page_size`

**Response schema** (`DocumentOut`):
```
id, case_id, case_no (resolved), doc_template_id, direction,
doc_date, title, ref_no, extra_data,
reply_to_id, need_reply, reply_date,
created_at, updated_at, attachments[]
```

**Note**: `case_id` filter works correctly. Returns `{items[], page, page_size, total}`. Currently 0 documents in dev DB.

### 3. Tasks — `GET /api/v1/tasks?case_id={case_id}`

**Status**: PASS
**Code location**: `backend/app/modules/tasks/api.py:98-179`

**Query params supported**: `status`, `due_from`, `due_to`, `worker_id`, `supervisor_id`, `case_id`, `client_id`, `page`, `page_size`

**Response schema** (inline dict, not Pydantic):
```
id, case_id, case_no (resolved), client_name (resolved),
document_id, task_template_id, title, due_date, internal_due_date,
worker_id, supervisor_id, remark, status,
created_at, updated_at
```

**Note**: `case_id` filter works correctly. Returns `{items[], page, page_size, total}`. Currently 0 tasks in dev DB.

### 4. Fee Drafts — `GET /api/v1/fees/drafts?case_id={case_id}`

**Status**: PASS
**Code location**: `backend/app/modules/fees/api.py:35-80`

**Query params supported**: `page`, `page_size`, `case_id`, `client_id`, `status` (alias for status_filter)

**Response schema** (`FeeDraftListItemOut`):
```
id, case_id, client_id, currency, status, amount
```

**Note**: `case_id` filter works correctly. Returns `{items[], page, page_size, total}`. Currently 0 fee drafts in dev DB.

### Summary

| Endpoint | `case_id` filter | Response shape | Status |
|----------|-----------------|---------------|--------|
| `GET /cases/{id}` | N/A (path param) | Single object with applicants/inventors/priorities arrays | PASS |
| `GET /documents?case_id=X` | Yes (Query param) | `{items[], page, page_size, total}` | PASS |
| `GET /tasks?case_id=X` | Yes (Query param) | `{items[], page, page_size, total}` | PASS |
| `GET /fees/drafts?case_id=X` | Yes (Query param) | `{items[], page, page_size, total}` | PASS |

### Issues / Notes
- **No sample related data**: Dev DB (seeded) has 13 cases but 0 documents, 0 tasks, 0 fee drafts. Frontend tab components will show empty states initially.
- **Fee draft list response is minimal**: Only returns `id, case_id, client_id, currency, status, amount` — no `case_no` or `draft_type` in list items (available in detail endpoint though).
- **Task list enriched**: Task list endpoint resolves `case_no` and `client_name` via batch queries — good for display.
- **Document list enriched**: Document list endpoint resolves `case_no` via batch query.
- All endpoints use standard paginated response shape `{items, page, page_size, total}` — frontend can use a consistent pattern.

---

## Test Verification Results (Task #4)

**Verified by**: test-agent
**Date**: 2026-02-26

### 1. Quality Gate

| Check | Result | Notes |
|-------|--------|-------|
| `npm run lint` | PASS | Zero warnings, zero errors |
| `npm run typecheck` | PASS | `vue-tsc --noEmit` clean |
| `npm run build` | PASS | Built in 3.03s, 1676 modules transformed |

### 2. Backend Tests (Regression Check)

| Check | Result | Notes |
|-------|--------|-------|
| `pytest -q --tb=short` | PASS | **141 passed**, 3 warnings (deprecation only — passlib crypt, Pydantic Field extras) |

No regressions introduced.

### 3. File Allowlist Compliance

**Status**: PASS

The 4 new component files and CaseDetail.vue were modified as expected:

| File | Status | In Allowlist? |
|------|--------|---------------|
| `frontend/src/modules/cases/pages/CaseDetail.vue` | Modified | YES |
| `frontend/src/modules/cases/components/CaseDocumentsTab.vue` | New | YES |
| `frontend/src/modules/cases/components/CaseTasksTab.vue` | New | YES |
| `frontend/src/modules/cases/components/CaseFeesTab.vue` | New | YES |
| `frontend/src/modules/cases/components/CaseClaimsTab.vue` | New | YES |

**Note**: The `git diff --name-only HEAD` also shows many pre-existing modified files from prior batches (not committed). These are NOT new changes from this FA1 batch. The FA1 implementation only touched the 5 files above. No allowlist violation.

### 4. API Endpoint Verification (Live)

Backend running at `http://localhost:8000` (healthz OK).

| Endpoint | Status | Response |
|----------|--------|----------|
| `POST /api/v1/auth/login` | PASS | Token obtained |
| `GET /api/v1/cases` | PASS | Cases returned, selected case `d74ba881-...` |
| `GET /api/v1/cases/{id}` (raw) | PASS | `applicants[]` and `inventors[]` present in response |
| `GET /api/v1/documents?case_id=X` | PASS | Paginated response, 0 items (expected — no seed data) |
| `GET /api/v1/tasks?case_id=X` | PASS | Paginated response, 0 items (expected) |
| `GET /api/v1/fees/drafts?case_id=X` | PASS | Paginated response, 0 items (expected) |

### 5. New Component Code Quality Review

#### CaseDocumentsTab.vue
- Chinese text: YES — `公文记录`, `登记公文`, `加载中...`, `暂无公文记录`, `无标题`, column labels `方向`/`标题`/`公文日期`/`创建时间`
- Imports: `../../../api/http` — relative path, CORRECT (no `@/`)
- Element Plus: `el-table`, `el-table-column`, `el-tag`, `el-button` — all used correctly
- Props: `caseId: string` — typed via `defineProps<{}>()` generic, CORRECT
- API call: `http.get('/documents', { params: { case_id: props.caseId } })` — direct http, passes case_id correctly
- Direction tag mapping: `IN` → success/收文, `OUT` → warning/发文 — logical

#### CaseTasksTab.vue
- Chinese text: YES — `任务记录`, `加载中...`, `暂无任务记录`, column labels `标题`/`状态`/`截止日期`/`执行人`
- Imports: `../../../api/http` — relative, CORRECT
- Element Plus: `el-table`, `el-table-column`, `el-tag` — correct
- Props: `caseId: string` — typed correctly
- `statusTagType()` helper: maps OPEN→warning, CLOSED→success, CANCELLED→info — reasonable
- `assigned_to` maps from `worker_id` || `supervisor_id` — shows raw IDs (not names), but acceptable for MVP

#### CaseFeesTab.vue
- Chinese text: YES — `费用记录`, `创建费用草稿`, `加载中...`, `暂无费用记录`, column labels `草稿类型`/`状态`/`币种`/`总金额`
- Imports: `../../../api/fees` + `../../../api/fees.types` — relative, CORRECT; uses typed API wrapper
- Element Plus: `el-table`, `el-table-column`, `el-tag`, `el-button` — correct
- Props: `caseId: string` — typed correctly
- Uses `getFeeDrafts({ case_id })` — proper typed API, GOOD
- **Minor note**: `draft_type` column exists but fee draft list endpoint doesn't return `draft_type` — column will be empty. Not a blocker for MVP.

#### CaseClaimsTab.vue
- Chinese text: YES — `申请人`, `暂无申请人信息`, `发明人`, `暂无发明人信息`, column labels `序号`/`中文名`/`英文名`
- Imports: none needed (pure props component)
- Element Plus: `el-table`, `el-table-column` — correct
- Props: `applicants: ClaimPerson[]`, `inventors: ClaimPerson[]` — typed correctly
- Exports `ClaimPerson` interface — imported by CaseDetail.vue, CORRECT

#### CaseDetail.vue (modifications)
- New imports (lines 190-194): All 4 tab components + `ClaimPerson` type — relative paths, CORRECT
- New state: `caseApplicants`, `caseInventors` refs (line 209-210)
- Raw API call (lines 230-236): `http.get(`/cases/${id}`)` fetches applicants/inventors separately — workaround for getCase mapper dropping these fields
- Tab panes added: claims (line 100-102), docs (line 104-106), fees (line 108-110), tasks (line 118-120)
- All tab panes pass correct props (`caseId`, `applicants`/`inventors`)

### 6. Issues Found

| Severity | Issue | Impact |
|----------|-------|--------|
| LOW | `CaseFeesTab`: `draft_type` column will be empty (field not in list endpoint) | Empty column in fees tab; cosmetic only |
| LOW | `CaseTasksTab`: `assigned_to` shows raw UUID (worker_id/supervisor_id) not username | Displays UUID instead of name; usable for MVP |
| INFO | Dev DB has 0 documents/tasks/fees — all tabs show empty state | Expected; not a bug |

### 7. Overall Verdict

| Criteria | Status |
|----------|--------|
| Quality Gate (lint + typecheck + build) | **PASS** |
| Backend Tests (no regression) | **PASS** (141/141) |
| File Allowlist Compliance | **PASS** (5/5 files) |
| API Endpoints Functional | **PASS** (all 4 endpoints) |
| Code Quality (Chinese, imports, Element Plus, props) | **PASS** |
| **OVERALL** | **PASS** |
