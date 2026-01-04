# BE-APIv4-014_documents_put_documents_id — documents PUT /documents/{id}

## Design references
- `documents/docs/doc_02_api.md` 
- `docs/execution_order_v2.md`
- `docs/02_permissions_rbac.md`
- `docs/permissions_matrix.md`

## Target
- **File:** `backend/app/modules/documents/api.py`
- **Atomic rule:** modify/create ONLY this file; implement ONLY this ONE endpoint.

## Scope decision (MVP1 – FIXED)
- Implement ONLY `PUT /documents/{id}`.
- No schema changes, no new tables, no migration changes.
- Use existing ORM models only.

## Endpoint (EXACT)
- Method: `PUT`
- Path: `/documents/{id}`
- Expected HTTP status: `200`

## Permission (Unified)
- Required permission: `Doc.Edit`
- Enforce via: `require_perm("Doc.Edit")`

## Request example
```json
{
  "case_id": "string",
  "doc_template_id": "string"
}
```

## Response example (HTTP 200)
```json
{
  "id": "string",
  "case_id": "string",
  "doc_template_id": "string",
  "direction": "string",
  "doc_date": "2025-01-01",
  "title": "text"
}
```

## Validation commands
```bash
cd backend
ruff check .
python -m py_compile app/modules/documents/api.py
```

### Curl example (expected HTTP 200)
```bash
export FPMS_TOKEN="REPLACE_ME"
curl -i -X PUT -H "Authorization: Bearer $FPMS_TOKEN" -H "Content-Type: application/json" -d '{"case_id": "string", "doc_template_id": "string"}' "http://localhost:8000/api/v1/documents/REPLACE_ID"
```

## Prompt
In `backend/app/modules/documents/api.py`, implement ONLY the endpoint `PUT /documents/{id}` according to `documents/docs/doc_02_api.md`.

Requirements:
- Enforce permission using `require_perm("Doc.Edit")`.
- Use existing ORM models and services only.
- Return HTTP 200 on success.
- Keep request/response shapes consistent with examples above (adjust only if API doc specifies differently).

Do NOT:
- Add other endpoints
- Modify schema/migrations
- Ask clarification questions
