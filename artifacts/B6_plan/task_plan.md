# B6 — Search & Filter Enhancement — Task Plan

## Status: PLANNED (Ready for implementation)

## Batch Scope
Add client_id filters to document/task lists. Add case_no to document response.
Add client_name to task response. Cross-entity joins for better search.

## Team Composition
| Role | Agent Name | Status |
|------|-----------|--------|
| Architect | architect | Done |
| Backend Impl | backend-impl | Pending |
| Test Agent | test-agent | Pending |
| Reviewer | reviewer | Pending |

## Task Decomposition

| ID | Task | Files Changed | Owner | Status |
|----|------|--------------|-------|--------|
| B6-1 | Add `client_id` filter to Document list | `documents/service.py`, `documents/api.py` | backend-impl | pending |
| B6-2 | Add `case_no` to Document list response | `documents/schemas.py`, `documents/api.py` | backend-impl | pending |
| B6-3 | Add `client_id` filter to Task list | `tasks/service.py`, `tasks/api.py` | backend-impl | pending |
| B6-4 | Add `client_name` to Task list response | `tasks/api.py` | backend-impl | pending |
| B6-5 | Write tests for all B6 changes | `tests/test_b6_search_filters.py` | test-agent | pending |

## Execution Order
B6-1 through B6-4 are independent — implement in single pass.
B6-5 depends on B6-1..B6-4 completion.

## Files Changed (Total: 6)
1. `backend/app/modules/documents/service.py` — Add `client_id` param + Case join filter
2. `backend/app/modules/documents/api.py` — Add `client_id` Query param, import Case, batch-resolve `case_no`
3. `backend/app/modules/documents/schemas.py` — Add `case_no: str | None = None` to `DocumentOut`
4. `backend/app/modules/tasks/service.py` — Handle `client_id` in filters dict with Case join
5. `backend/app/modules/tasks/api.py` — Add `client_id` Query param, extend batch-resolve for `client_name`
6. `backend/tests/test_b6_search_filters.py` — NEW file, 8 test cases

## No DB Migration Needed
All changes are application-level Python code only.

## Implementation Details

### B6-1: Document list `client_id` filter
- `documents/service.py`: Add `client_id: str | None = None` param to `list_documents()`. If provided, `stmt = stmt.join(Case, Document.case_id == Case.id).where(Case.client_id == client_id)`. Case already imported.
- `documents/api.py`: Add `client_id: str | None = Query(default=None)` to `get_documents()`, pass through to service.

### B6-2: Document list `case_no` response field
- `documents/schemas.py`: Add `case_no: str | None = None` to `DocumentOut` (after `case_id`).
- `documents/api.py`: Import `Case` from cases.models. After `list_documents()` call, batch-resolve:
  ```python
  case_ids = {doc.case_id for doc in documents if doc.case_id}
  case_no_map: dict[str, str] = {}
  if case_ids:
      cases = db.query(Case.id, Case.case_no).filter(Case.id.in_(case_ids)).all()
      case_no_map = {c.id: c.case_no for c in cases}
  ```
  Add `case_no=case_no_map.get(document.case_id)` to each DocumentOut.

### B6-3: Task list `client_id` filter
- `tasks/service.py`: In `list_tasks()`, add `client_id = filters.get("client_id")`. If provided, `stmt = stmt.join(Case, Task.case_id == Case.id).where(Case.client_id == client_id)`. Case already imported.
- `tasks/api.py`: Add `client_id: str | None = Query(default=None)` to `get_tasks()`, add `"client_id": client_id` to filters dict.

### B6-4: Task list `client_name` response field
- `tasks/api.py`: Extend existing batch-resolve to also query `Case.client_id`. Then batch-resolve `Client.name_cn` for all unique client_ids. Add `"client_name"` to each item dict. Client already imported.

### B6-5: Tests
- New file `tests/test_b6_search_filters.py` with 8 tests covering:
  - Document list includes case_no
  - Document list filter by client_id (positive + negative)
  - Task list includes client_name
  - Task list filter by client_id (positive + negative)
  - Combined filter tests

## Quality Gate
```bash
cd backend && ruff check --fix . && ruff format . && ruff check . && pytest -q
```
