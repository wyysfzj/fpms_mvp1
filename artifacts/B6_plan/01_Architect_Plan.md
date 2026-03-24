# Batch B6 — Search & Filter Enhancement — Implementation Plan

## 1. Current State Analysis

### 1.1 Task List Endpoint (`GET /api/v1/tasks`)

**Location**: `tasks/api.py:98-165`

**Current filters** (via Query params → `filters` dict → `tasks/service.py:list_tasks()`):
- `status`, `case_id`, `worker_id`, `supervisor_id`, `due_from`, `due_to`

**Batch-resolve pattern** (`tasks/api.py:139-144`):
```python
case_ids = {task.case_id for task in tasks if task.case_id}
case_no_map: dict[str, str] = {}
if case_ids:
    cases = db.query(Case.id, Case.case_no).filter(Case.id.in_(case_ids)).all()
    case_no_map = {c.id: c.case_no for c in cases}
```
Then in item dict: `"case_no": case_no_map.get(task.case_id) if task.case_id else None`

**Response format**: Raw `dict[str, Any]` — NOT using Pydantic `TaskListItemOut`. Items are built as dicts inline.

**Missing**: `client_id` filter, `client_name` in response.

### 1.2 Document List Endpoint (`GET /api/v1/documents`)

**Location**: `documents/api.py:120-180`

**Current filters** (via Query params → `documents/service.py:list_documents()`):
- `q` (text search on title/ref_no), `direction`, `doc_template_id`, `case_id`, `date_from`, `date_to`

**Response format**: Pydantic `DocumentOut` model inside `DocumentListOut(PageResult[DocumentOut])`.
- Items constructed explicitly field-by-field (api.py:162-179), NOT via `model_validate`.
- NO batch-resolve currently — no `case_no` in response.

**Missing**: `client_id` filter, `case_no` in response.

### 1.3 Key Model Relationships

```
Document.case_id → Case.id
Task.case_id → Case.id
Case.client_id → Client.id

Client.name_cn = client name (main display name)
Case.case_no = case number (unique)
```

### 1.4 Imports Already Available

| File | `Case` imported? | `Client` imported? |
|------|------------------|--------------------|
| `documents/service.py` | Yes (line 12) | No |
| `documents/api.py` | No | No |
| `tasks/service.py` | Yes (line 12) | No |
| `tasks/api.py` | Yes (line 15) | Yes (line 15) |

---

## 2. Task Decomposition

### Sub-task B6-1: Add `client_id` filter to Document list
**Files**: `documents/service.py`, `documents/api.py`

### Sub-task B6-2: Add `case_no` to Document list response
**Files**: `documents/schemas.py`, `documents/api.py`

### Sub-task B6-3: Add `client_id` filter to Task list
**Files**: `tasks/service.py`, `tasks/api.py`

### Sub-task B6-4: Add `client_name` to Task list response
**Files**: `tasks/api.py`

### Sub-task B6-5: Write tests
**Files**: `tests/test_b6_search_filters.py`

---

## 3. File-by-File Changes

### 3.1 `documents/service.py` — Add `client_id` filter

**Change**: Add `client_id` parameter to `list_documents()`, join Case table when filtering.

```python
# Add parameter (after case_id)
def list_documents(
    db: Session,
    *,
    q: str | None = None,
    direction: DocumentDirection | None = None,
    doc_template_id: str | None = None,
    case_id: str | None = None,
    client_id: str | None = None,          # <-- NEW
    date_from: date | None = None,
    date_to: date | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[Document], int]:
    stmt = select(Document)

    # ... existing filters unchanged ...

    if client_id:                           # <-- NEW BLOCK
        stmt = stmt.join(Case, Document.case_id == Case.id).where(
            Case.client_id == client_id
        )
```

**Note**: The `Case` model is already imported (line 12). The join is safe because `Document.case_id` is a NOT NULL FK to `t_case.id`, so every document has a valid case.

### 3.2 `documents/api.py` — Add `client_id` Query param + batch-resolve `case_no`

**Changes**:
1. Add `Case` import
2. Add `client_id` Query parameter to `get_documents()`
3. Pass `client_id` to `list_documents()`
4. Add batch-resolve for `case_no` (same pattern as tasks/api.py)
5. Include `case_no` in `DocumentOut` construction

```python
# Add import at top
from app.modules.cases.models import Case

# In get_documents():
#   Add parameter: client_id: str | None = Query(default=None),
#   Pass to service: client_id=client_id,

# After list_documents() call, add batch-resolve:
case_ids = {doc.case_id for doc in documents if doc.case_id}
case_no_map: dict[str, str] = {}
if case_ids:
    cases = db.query(Case.id, Case.case_no).filter(Case.id.in_(case_ids)).all()
    case_no_map = {c.id: c.case_no for c in cases}

# In DocumentOut construction, add:
#   case_no=case_no_map.get(document.case_id) if document.case_id else None,
```

### 3.3 `documents/schemas.py` — Add `case_no` to `DocumentOut`

**Change**: Add optional `case_no` field.

```python
class DocumentOut(BaseModel):
    id: str
    case_id: str
    case_no: str | None = None              # <-- NEW
    doc_template_id: str | None
    # ... rest unchanged ...
```

### 3.4 `tasks/service.py` — Add `client_id` filter

**Change**: Handle `client_id` in `list_tasks()` filters dict.

```python
def list_tasks(db, *, filters, page, page_size):
    stmt = select(Task)

    # ... existing filter extractions ...
    client_id = filters.get("client_id")    # <-- NEW

    # ... existing filter clauses ...

    if client_id:                           # <-- NEW BLOCK
        stmt = stmt.join(Case, Task.case_id == Case.id).where(
            Case.client_id == client_id
        )
```

**Note**: `Case` is already imported (line 12).

### 3.5 `tasks/api.py` — Add `client_id` Query param + batch-resolve `client_name`

**Changes**:
1. Add `client_id` Query parameter to `get_tasks()`
2. Add to filters dict
3. Extend batch-resolve: query `Case.client_id` alongside `Case.case_no`
4. Add second batch-resolve for `Client.name_cn`
5. Include `client_name` in response items

```python
# In get_tasks():
#   Add parameter: client_id: str | None = Query(default=None),
#   Add to filters dict: "client_id": client_id,

# Replace existing batch-resolve block (lines 139-144) with:
case_ids = {task.case_id for task in tasks if task.case_id}
case_no_map: dict[str, str] = {}
case_client_map: dict[str, str | None] = {}
if case_ids:
    cases = db.query(Case.id, Case.case_no, Case.client_id).filter(
        Case.id.in_(case_ids)
    ).all()
    case_no_map = {c.id: c.case_no for c in cases}
    case_client_map = {c.id: c.client_id for c in cases}

# Batch-resolve client_name
client_ids = {cid for cid in case_client_map.values() if cid}
client_name_map: dict[str, str] = {}
if client_ids:
    clients = db.query(Client.id, Client.name_cn).filter(
        Client.id.in_(client_ids)
    ).all()
    client_name_map = {c.id: c.name_cn for c in clients}

# In item dict, add:
#   "client_name": client_name_map.get(
#       case_client_map.get(task.case_id, ""), ""
#   ) if task.case_id else None,
```

**Note**: Both `Case` and `Client` are already imported in tasks/api.py.

---

## 4. Schema Changes Summary

| Schema | Field Added | Type | Default |
|--------|------------|------|---------|
| `DocumentOut` | `case_no` | `str \| None` | `None` |

**No schema change needed for Task list** — it uses raw dicts, so `client_name` is just a new key.

---

## 5. Test Strategy

Create `tests/test_b6_search_filters.py` with these test cases:

### 5.1 Document List Tests

1. **`test_document_list_includes_case_no`**
   - Create client → case → document
   - GET /documents
   - Assert `case_no` field present and correct in response items

2. **`test_document_list_filter_by_client_id`**
   - Create two clients (A, B), each with a case and documents
   - GET /documents?client_id=A
   - Assert only client A's documents returned
   - GET /documents?client_id=B
   - Assert only client B's documents returned

3. **`test_document_list_filter_by_client_id_no_results`**
   - GET /documents?client_id=nonexistent-uuid
   - Assert empty items list, total=0

### 5.2 Task List Tests

4. **`test_task_list_includes_client_name`**
   - Create client → case → task
   - GET /tasks
   - Assert `client_name` field present and equals `name_cn`

5. **`test_task_list_filter_by_client_id`**
   - Create two clients (A, B), each with a case and tasks
   - GET /tasks?client_id=A
   - Assert only client A's tasks returned
   - GET /tasks?client_id=B
   - Assert only client B's tasks returned

6. **`test_task_list_filter_by_client_id_no_results`**
   - GET /tasks?client_id=nonexistent-uuid
   - Assert empty items list, total=0

### 5.3 Combined Filter Tests

7. **`test_document_list_combined_client_id_and_direction`**
   - Create client → case → IN doc + OUT doc
   - GET /documents?client_id=X&direction=IN
   - Assert only IN docs returned

8. **`test_task_list_combined_client_id_and_status`**
   - Create client → case → OPEN task + close one
   - GET /tasks?client_id=X&status=OPEN
   - Assert only OPEN tasks returned

---

## 6. Risk Assessment

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| SQLite join performance | Low | Batch-resolve pattern avoids N+1; page size capped at 200 |
| Case with NULL client_id | Low | `client_name` defaults to None; filter excludes NULL matches |
| Duplicate joins if case_id + client_id both provided | Low | Each join is independent; SQLAlchemy handles correctly |
| Breaking existing API consumers | None | All new fields are optional (None default); new filters are optional |
| `DocumentOut` schema backward compat | None | `case_no` defaults to None; old clients simply ignore it |

---

## 7. Dependency Graph

```
B6-1 (doc client_id filter) ──┐
                               ├──→ B6-5 (tests)
B6-2 (doc case_no response)  ──┤
                               │
B6-3 (task client_id filter) ──┤
                               │
B6-4 (task client_name resp) ──┘
```

B6-1 through B6-4 are independent and can be implemented together in a single pass.
B6-5 (tests) depends on all four being complete.

---

## 8. Quality Gate

```bash
cd backend && ruff check --fix . && ruff format . && ruff check . && pytest -q
```

No migrations needed — no schema/DB changes. All changes are in Python application code only.
