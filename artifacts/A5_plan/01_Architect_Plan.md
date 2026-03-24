# Batch A5 — Advanced Case Search: Implementation Plan

## 1. Gap Analysis

### Already Implemented (GET /cases & GET /cases/export)

| Feature | Status | Location (api.py) |
|---------|--------|----------|
| Keyword search (`q`) across case_no, title_cn, title_en, app_no | Done | L56-65 / L376-385 |
| Exact `case_no` filter | Done | L66-67 / L386-387 |
| Exact `app_no` filter | Done | L68-69 / L388-389 |
| Exact `client_id` filter | Done | L70-71 / L390-391 |
| Exact `status` filter | Done | L72-73 / L392-393 |
| Date range on `recv_date` (`date_from`, `date_to`) | Done | L74-77 / L394-397 |
| Sorting (case_no, recv_date, filing_date, created_at) | Done | L81-94 / L401-414 |
| Pagination (page, page_size) | Done | L96 / L416 |
| Response includes: case_type, patent_category, primary_agent_id, filing_date | Done | L105-123 / L425-443 |

### Missing (Needs Implementation)

| Feature | Status | Required Change |
|---------|--------|----------------|
| Filter by `case_type` | **MISSING** | Add Query param + filter condition |
| Filter by `patent_category` | **MISSING** | Add Query param + filter condition |
| Filter by `flow_dir` | **MISSING** | Add Query param + filter condition |
| Filter by `filing_date` range (`filing_date_from`, `filing_date_to`) | **MISSING** | Add 2 Query params + filter conditions |
| Filter by `primary_agent_id` | **MISSING** | Add Query param + filter condition |

### Note on service.py

The `list_cases()` function in `service.py` (L61-109) is **NOT currently used** by the endpoints in `api.py`. The endpoints build queries directly inline. For consistency, we add the same filters to `service.py` as well.

---

## 2. API Contract — New Query Parameters

Both `GET /cases` and `GET /cases/export` will accept these new parameters:

| Parameter | Type | Filter Column | Comparison | Default |
|-----------|------|--------------|------------|---------|
| `case_type` | `str \| None` | `Case.case_type` | `==` (exact) | `None` |
| `patent_category` | `str \| None` | `Case.patent_category` | `==` (exact) | `None` |
| `flow_dir` | `str \| None` | `Case.flow_dir` | `==` (exact) | `None` |
| `filing_date_from` | `date \| None` | `Case.filing_date` | `>=` | `None` |
| `filing_date_to` | `date \| None` | `Case.filing_date` | `<=` | `None` |
| `primary_agent_id` | `str \| None` | `Case.primary_agent_id` | `==` (exact) | `None` |

All parameters use `Query(default=None)` — no breaking change to existing API consumers.

**Distinction:** Existing `date_from`/`date_to` filter on `recv_date`. New `filing_date_from`/`filing_date_to` filter on `filing_date`. These are separate date columns.

---

## 3. Verified Model Columns (models.py)

| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| `Case.case_type` | `String(32)` | NOT NULL | `'NORMAL'` |
| `Case.patent_category` | `String(32)` | NOT NULL | `'INV'` |
| `Case.flow_dir` | `String(32)` | NOT NULL | `'CN_DOMESTIC'` |
| `Case.filing_date` | `Date` | nullable | None |
| `Case.primary_agent_id` | `String(36)` | nullable | None |

All columns exist. **No migration needed.**

---

## 4. Exact Code Changes

### File 1: `backend/app/modules/cases/api.py`

#### 4.1 GET /cases (function `get_cases`, L20-125)

**Add 6 new Query params** after `date_to` (L28), before `sort_by` (L29):

```python
# AFTER existing line 28:
#     date_to: date | None = Query(default=None),
# INSERT:
    case_type: str | None = Query(default=None),
    patent_category: str | None = Query(default=None),
    flow_dir: str | None = Query(default=None),
    filing_date_from: date | None = Query(default=None),
    filing_date_to: date | None = Query(default=None),
    primary_agent_id: str | None = Query(default=None),
# BEFORE existing:
#     sort_by: str | None = Query(default=None),
```

**Add 6 new filter conditions** after `date_to` filter (L76-77), before `total = query.count()` (L79):

```python
# AFTER existing:
#     if date_to:
#         query = query.filter(Case.recv_date <= date_to)
# INSERT:
    if case_type:
        query = query.filter(Case.case_type == case_type)
    if patent_category:
        query = query.filter(Case.patent_category == patent_category)
    if flow_dir:
        query = query.filter(Case.flow_dir == flow_dir)
    if filing_date_from:
        query = query.filter(Case.filing_date >= filing_date_from)
    if filing_date_to:
        query = query.filter(Case.filing_date <= filing_date_to)
    if primary_agent_id:
        query = query.filter(Case.primary_agent_id == primary_agent_id)
# BEFORE existing:
#     total = query.count()
```

#### 4.2 GET /cases/export (function `export_cases`, L340-445)

**Identical changes.** Add the same 6 Query params after `date_to` (L348) and the same 6 filter conditions after `date_to` filter (L396-397).

#### 4.3 PUT /cases/{case_id} — Add filing_date + recv_date support (L448-569)

Currently the PUT handler does NOT handle `filing_date` or `recv_date` updates. We need this for testing and it's a reasonable gap to fill. Add after the `status` handling block (around L505):

```python
    if "filing_date" in payload:
        v = payload["filing_date"]
        case.filing_date = date.fromisoformat(v) if isinstance(v, str) else v
    if "recv_date" in payload:
        v = payload["recv_date"]
        case.recv_date = date.fromisoformat(v) if isinstance(v, str) else v
```

### File 2: `backend/app/modules/cases/service.py`

**Add import** (top of file):
```python
from datetime import date
```

**Extend `list_cases()` signature** (L61-68) with 6 new params:

```python
def list_cases(
    db: Session,
    q: str | None = None,
    client_id: str | None = None,
    status: str | None = None,
    case_type: str | None = None,        # NEW
    patent_category: str | None = None,   # NEW
    flow_dir: str | None = None,          # NEW
    filing_date_from: date | None = None, # NEW
    filing_date_to: date | None = None,   # NEW
    primary_agent_id: str | None = None,  # NEW
    page: int = 1,
    page_size: int = 20,
) -> PageResult[CaseListItem]:
```

**Add 6 filter conditions** after existing filters (after L85), before `total = query.count()` (L87):

```python
    if case_type:
        query = query.filter(Case.case_type == case_type)
    if patent_category:
        query = query.filter(Case.patent_category == patent_category)
    if flow_dir:
        query = query.filter(Case.flow_dir == flow_dir)
    if filing_date_from:
        query = query.filter(Case.filing_date >= filing_date_from)
    if filing_date_to:
        query = query.filter(Case.filing_date <= filing_date_to)
    if primary_agent_id:
        query = query.filter(Case.primary_agent_id == primary_agent_id)
```

### File 3: `backend/tests/test_case_search.py` (NEW)

See section 5 below.

---

## 5. Test Strategy

### New File: `backend/tests/test_case_search.py`

#### Test Helper Pattern (from test_case_fields.py)

```python
_COUNTER = 0
def _unique_case_no(prefix: str = "SRCH") -> str:
    global _COUNTER
    _COUNTER += 1
    return f"{prefix}_TEST_{_COUNTER:04d}"

_MINIMAL_APPLICANT = [{"seq": 1, "is_first": True, "name_cn": "Test"}]
```

#### Test Data Strategy

- Create cases via `POST /api/v1/cases` with known `case_type`, `patent_category`, `flow_dir`, `primary_agent_id`
- Set `filing_date` via `PUT /api/v1/cases/{id}` with `{"filing_date": "YYYY-MM-DD"}`
- Filter via `GET /api/v1/cases?{param}={value}&case_no={known_prefix}` to isolate from other test data
- Use unique `case_no` per test to avoid collisions

#### Test Cases (10 tests)

| # | Test Name | Description |
|---|-----------|-------------|
| 1 | `test_filter_by_case_type` | Create 2 cases (NORMAL, PCT_INTL), filter `case_type=PCT_INTL`, verify only PCT_INTL returned |
| 2 | `test_filter_by_patent_category` | Create 2 cases (INV, DES), filter `patent_category=DES`, verify only DES returned |
| 3 | `test_filter_by_flow_dir` | Create 2 cases (CN_DOMESTIC, FOREIGN_INBOUND), filter `flow_dir=FOREIGN_INBOUND`, verify only FOREIGN_INBOUND returned |
| 4 | `test_filter_by_filing_date_from` | Create case, set filing_date via PUT, filter `filing_date_from`, verify correct inclusion/exclusion |
| 5 | `test_filter_by_filing_date_to` | Same with `filing_date_to` |
| 6 | `test_filter_by_filing_date_range` | Create 3 cases with different filing_dates, filter with both from/to, verify only in-range cases |
| 7 | `test_filter_by_primary_agent_id` | Create 2 cases with different agent IDs, filter by one |
| 8 | `test_combined_filters` | Apply `case_type` + `patent_category` combo, verify AND behavior |
| 9 | `test_no_filter_backward_compat` | Omitting new params doesn't change existing behavior |
| 10 | `test_export_filters_mirror` | Apply same filters to `/cases/export`, verify same filtering |

---

## 6. Dependency Graph

```
Task 1 (Architect Plan)        ← CURRENT
    │
    ▼
Task 2 (Backend Implementation)
    │  - api.py: 6 params + 6 filters in GET /cases
    │  - api.py: 6 params + 6 filters in GET /cases/export
    │  - api.py: filing_date + recv_date in PUT handler
    │  - service.py: 6 params + 6 filters in list_cases()
    │
    ▼
Task 3 (Tests)
    │  - New file: tests/test_case_search.py (10 tests)
    │
    ▼
Task 4 (Review)
    │  - Read all changed files
    │  - Verify acceptance criteria
    │  - Write review_report.md
```

**Strictly sequential** — each task depends on the previous.

---

## 7. Risk Analysis

| # | Risk | Severity | Mitigation |
|---|------|----------|------------|
| R1 | SQLite compat — `ilike` | None | A5 filters use `==`, `>=`, `<=` only. Fully SQLite-compatible. |
| R2 | `filing_date` vs `recv_date` confusion | Low | `date_from`/`date_to` → `recv_date`; `filing_date_from`/`filing_date_to` → `filing_date`. Names are explicit. |
| R3 | `filing_date` not settable via PUT | Medium | Add `filing_date` + `recv_date` to PUT handler (4 lines). |
| R4 | Response schema change | None | Response dict (L105-123, L425-443) is NOT modified. |
| R5 | Invalid enum values in filters | Low | Returns 0 results (no error). Same as existing `status` filter behavior. |
| R6 | Test data isolation | Low | Use `_unique_case_no()` + filter by `case_no` prefix where needed. |

---

## 8. Acceptance Criteria

- [ ] `GET /cases?case_type=PCT_INTL` returns only PCT_INTL cases
- [ ] `GET /cases?patent_category=UM` returns only UM cases
- [ ] `GET /cases?flow_dir=FOREIGN_INBOUND` returns only FOREIGN_INBOUND cases
- [ ] `GET /cases?filing_date_from=2025-03-01` returns cases with filing_date >= 2025-03-01
- [ ] `GET /cases?filing_date_to=2025-03-31` returns cases with filing_date <= 2025-03-31
- [ ] `GET /cases?filing_date_from=2025-03-01&filing_date_to=2025-03-31` returns only in-range cases
- [ ] `GET /cases?primary_agent_id=UUID` returns only that agent's cases
- [ ] Combined filters work as AND (intersection)
- [ ] `GET /cases/export` supports identical filters
- [ ] Omitting all new filters preserves existing behavior (backward compatible)
- [ ] Response schema is unchanged
- [ ] All existing tests pass (`pytest --tb=short`)
- [ ] 10 new tests in `test_case_search.py` all pass
- [ ] `ruff check` and `ruff format` pass

---

## 9. Summary of Changes

| File | Change Type | Lines Added |
|------|------------|-------------|
| `app/modules/cases/api.py` | Edit (params + filters in 2 endpoints + PUT handler) | ~28 |
| `app/modules/cases/service.py` | Edit (params + filters + import) | ~20 |
| `tests/test_case_search.py` | New file | ~200 |
