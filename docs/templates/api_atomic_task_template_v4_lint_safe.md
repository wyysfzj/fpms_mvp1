# Atomic Task Template — Phase 3 API (v4) — Lint-safe Edition (Ruff)

This template is authoritative for **Phase 3 / Phase 3.1** API atomic tasks.
It is designed so that code generated from the task will pass `ruff check .` under the recommended FastAPI+Alembic configuration.

---

## Task Metadata (Fill all)
- Task ID:
- Module:
- Target file:
- Endpoint:
- Permission code (Title.Action):

---

## 1) Purpose
Implement exactly ONE FastAPI endpoint. Constraints:
- No schema changes
- Use existing ORM models only
- Implement in module-level `api.py` (Approach A)
- Code must pass `ruff check .` and `ruff format .`

---

## 2) Preconditions (Must be true)
1) Phase 2 ORM parity complete for all involved tables/models.
2) Target module directory exists and is wired into the app router.
3) `require_perm("<PermissionCode>")` exists and is functional (not NotImplementedError).
4) `get_db` (SQLAlchemy session dependency) exists and is used consistently.

---

## 3) Output (Exactly one file edited)
- Edit ONLY: `<TARGET_API_PY>`

---

## 4) Endpoint Contract
- Method: `<METHOD>`
- Path: `<PATH>`
- AuthZ: `require_perm("<PERM_CODE>")`

### Request
Describe request body/query/path parameters precisely. No optional scope.

### Response (200)
Describe response JSON shape precisely. No optional scope.

### Error Responses (Required)
- 401 Unauthorized (not authenticated)
- 403 Forbidden (missing permission)
- 404 Not Found (when id/resource not found)
- 409 Conflict (unique constraint violation, if applicable)
- 422 Validation Error (FastAPI)

---

## 5) Lint-safe Implementation Rules (MANDATORY)

### 5.1 Do NOT place permission Depends in decorator dependencies
❌ Forbidden:
```python
@router.get("/x", dependencies=[Depends(require_perm("X.Read"))])
```

✅ Required (parameter injection):
```python
@router.get("/x")
def handler(
    db: Session = Depends(get_db),
    _perm: None = Depends(require_perm("X.Read")),
):
    ...
```

### 5.2 Import order (must match)
**Always** use this order and do not introduce unused imports:

```python
from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.deps import require_perm
# from app.modules.<module>.models import <Model>  # only import what you use
```

Rules:
- `from __future__ import annotations` is always the first non-docstring statement
- Only import types you actually use (avoid F401)
- Do not import `Text/func/text` unless used in code

### 5.3 Response shape
- Prefer returning plain dicts or Pydantic models if the project already uses them.
- Do NOT invent a new response envelope. Follow existing project conventions.
- If the codebase uses `items/total`, keep it; otherwise return a list.

### 5.4 DB interaction
- Use the project’s existing session pattern.
- Use `.query()` or `select()` consistently with the repo.
- Commit only when required (create/update). Rollback on exceptions per existing convention.

### 5.5 Errors
- Raise `HTTPException` with explicit `status_code` and stable `detail` strings.
- Do not leak secrets (e.g., system param values when `is_secret=True`).

---

## 6) JSON Examples (REQUIRED)
### Request example
```json
<REQUEST_JSON>
```

### Response example (200)
```json
<RESPONSE_JSON>
```

---

## 7) Curl Smoke Test (REQUIRED)
```bash
curl -s -X <METHOD> "http://localhost:8000<PATH>" \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '<REQUEST_JSON_ONE_LINE>'
```

---

## 8) Done Criteria (REQUIRED)
1) Endpoint exists and matches method/path.
2) Permission enforced: without perm => 403.
3) `ruff check .` passes.
4) Smoke curl succeeds with valid token+perm.
