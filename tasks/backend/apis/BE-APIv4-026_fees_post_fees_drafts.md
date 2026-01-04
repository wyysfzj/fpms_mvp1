# BE-APIv4-026_fees_post_fees_drafts — fees POST /fees/drafts

## Design references
- `fees/docs/fee_02_api.md` 
- `docs/execution_order_v2.md`
- `docs/02_permissions_rbac.md`
- `docs/permissions_matrix.md`

## Target
- **File:** `backend/app/modules/fees/api.py`
- **Atomic rule:** modify/create ONLY this file; implement ONLY this ONE endpoint.

## Scope decision (MVP1 – FIXED)
- Implement ONLY `POST /fees/drafts`.
- No schema changes, no new tables, no migration changes.
- Use existing ORM models only.

## Endpoint (EXACT)
- Method: `POST`
- Path: `/fees/drafts`
- Expected HTTP status: `201`

## Permission (Unified)
- Required permission: `Fee.Draft.Create`
- Enforce via: `require_perm("Fee.Draft.Create")`

## Request example
```json
{}
```

## Response example (HTTP 201)
```json
{
  "id": "string",
  "case_id": "string",
  "client_id": "string",
  "draft_type": "string",
  "currency": "string",
  "status": "string"
}
```

## Validation commands
```bash
cd backend
ruff check .
python -m py_compile app/modules/fees/api.py
```

### Curl example (expected HTTP 201)
```bash
export FPMS_TOKEN="REPLACE_ME"
curl -i -H "Authorization: Bearer $FPMS_TOKEN" -H "Content-Type: application/json" -d '{}' "http://localhost:8000/api/v1/fees/drafts"
```

## Prompt
In `backend/app/modules/fees/api.py`, implement ONLY the endpoint `POST /fees/drafts` according to `fees/docs/fee_02_api.md`.

Requirements:
- Enforce permission using `require_perm("Fee.Draft.Create")`.
- Use existing ORM models and services only.
- Return HTTP 201 on success.
- Keep request/response shapes consistent with examples above (adjust only if API doc specifies differently).

Do NOT:
- Add other endpoints
- Modify schema/migrations
- Ask clarification questions
