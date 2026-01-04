# BE-API-EXAMPLE-0001 — Client Contacts — List (Lint-safe v4)

## Purpose
Implement exactly ONE API endpoint: list contacts for a client.
Constraints:
- No schema changes
- Uses existing ORM models only
- Implement in module-level `api.py` (Approach A)
- Must pass `ruff check .`

## Preconditions
1) ORM models exist: `ClientContact` mapped to `t_client_contact`.
2) Router for module is included in app router.
3) `require_perm` is implemented and functional.
4) `get_db` dependency exists.

## Target File (Single)
- `backend/app/modules/masterdata/clients/api.py`

## Endpoint
- Method: GET
- Path: `/clients/{client_id}/contacts`
- Permission: `Client.Read`

## Request
- Path param: `client_id` (int)

## Response (200)
Return list of contacts:
```json
{
  "items": [
    {"id": 1, "client_id": 10, "contact_name": "Alice", "email": "a@example.com", "is_primary": true}
  ],
  "total": 1
}
```
If the codebase does not use `{items,total}`, return a plain list. Do not invent new envelopes.

## Lint-safe rules (MANDATORY)
- Do not use decorator `dependencies=[Depends(require_perm(...))]`
- Inject permission dependency as a function parameter

## Required import order (example)
```python
from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.deps import require_perm
from app.models.client_contact import ClientContact
```

## Implementation notes
- Filter by `ClientContact.client_id == client_id`
- Order by `id` ascending
- Return response per example
- 404 if client does not exist ONLY if the codebase already validates client existence in similar endpoints; otherwise skip extra lookups.

## Curl Smoke Test
```bash
curl -s -X GET "http://localhost:8000/clients/10/contacts" \
  -H "Authorization: Bearer <TOKEN>"
```

## Done Criteria
1) Endpoint reachable.
2) Without permission -> 403.
3) `ruff check .` passes.
