# BE-APIv4-016_documents_get_documents_id_attachments_att_id_download — documents GET /documents/{id}/attachments/{att_id}/download

## Design references
- `documents/docs/doc_02_api.md` 
- `docs/execution_order_v2.md`
- `docs/02_permissions_rbac.md`
- `docs/permissions_matrix.md`

## Target
- **File:** `backend/app/modules/documents/api.py`
- **Atomic rule:** modify/create ONLY this file; implement ONLY this ONE endpoint.

## Scope decision (MVP1 – FIXED)
- Implement ONLY `GET /documents/{id}/attachments/{att_id}/download`.
- No schema changes, no new tables, no migration changes.
- Use existing ORM models only.

## Endpoint (EXACT)
- Method: `GET`
- Path: `/documents/{id}/attachments/{att_id}/download`
- Expected HTTP status: `200`

## Permission (Unified)
- Required permission: `Doc.Attach`
- Enforce via: `require_perm("Doc.Attach")`

## Request example
```json
{}
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
curl -i -H "Authorization: Bearer $FPMS_TOKEN" "http://localhost:8000/api/v1/documents/REPLACE_ID/attachments/REPLACE_ID/download"
```

## Prompt
In `backend/app/modules/documents/api.py`, implement ONLY the endpoint `GET /documents/{id}/attachments/{att_id}/download` according to `documents/docs/doc_02_api.md`.

Requirements:
- Enforce permission using `require_perm("Doc.Attach")`.
- Use existing ORM models and services only.
- Return HTTP 200 on success.
- Keep request/response shapes consistent with examples above (adjust only if API doc specifies differently).

Do NOT:
- Add other endpoints
- Modify schema/migrations
- Ask clarification questions
