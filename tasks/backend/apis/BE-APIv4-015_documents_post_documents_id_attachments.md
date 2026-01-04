# BE-APIv4-015_documents_post_documents_id_attachments — documents POST /documents/{id}/attachments

## Design references
- `documents/docs/doc_02_api.md` 
- `docs/execution_order_v2.md`
- `docs/02_permissions_rbac.md`
- `docs/permissions_matrix.md`

## Target
- **File:** `backend/app/modules/documents/api.py`
- **Atomic rule:** modify/create ONLY this file; implement ONLY this ONE endpoint.

## Scope decision (MVP1 – FIXED)
- Implement ONLY `POST /documents/{id}/attachments`.
- No schema changes, no new tables, no migration changes.
- Use existing ORM models only.

## Endpoint (EXACT)
- Method: `POST`
- Path: `/documents/{id}/attachments`
- Expected HTTP status: `201`

## Permission (Unified)
- Required permission: `Doc.Attach`
- Enforce via: `require_perm("Doc.Attach")`

## Request example
```json
{}
```

## Response example (HTTP 201)
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

### Curl example (expected HTTP 201)
```bash
export FPMS_TOKEN="REPLACE_ME"
curl -i -H "Authorization: Bearer $FPMS_TOKEN" -H "Content-Type: application/json" -d '{}' "http://localhost:8000/api/v1/documents/REPLACE_ID/attachments"
```

## Prompt
In `backend/app/modules/documents/api.py`, implement ONLY the endpoint `POST /documents/{id}/attachments` according to `documents/docs/doc_02_api.md`.

Requirements:
- Enforce permission using `require_perm("Doc.Attach")`.
- Use existing ORM models and services only.
- Return HTTP 201 on success.
- Keep request/response shapes consistent with examples above (adjust only if API doc specifies differently).

Do NOT:
- Add other endpoints
- Modify schema/migrations
- Ask clarification questions
