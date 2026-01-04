# BE-APIv4-008_cases_put_cases_case_id — cases PUT /cases/{case_id}

## Design references
- `cases/docs/case_02_api.md` 
- `docs/execution_order_v2.md`
- `docs/02_permissions_rbac.md`
- `docs/permissions_matrix.md`

## Target
- **File:** `backend/app/modules/cases/api.py`
- **Atomic rule:** modify/create ONLY this file; implement ONLY this ONE endpoint.

## Scope decision (MVP1 – FIXED)
- Implement ONLY `PUT /cases/{case_id}`.
- No schema changes, no new tables, no migration changes.
- Use existing ORM models only.

## Endpoint (EXACT)
- Method: `PUT`
- Path: `/cases/{case_id}`
- Expected HTTP status: `200`

## Permission (Unified)
- Required permission: `Case.Edit`
- Enforce via: `require_perm("Case.Edit")`

## Request example
```json
{
  "case_no": "string",
  "case_type": "string"
}
```

## Response example (HTTP 200)
```json
{
  "id": "string",
  "case_no": "string",
  "case_type": "string",
  "patent_category": "string",
  "flow_dir": "string",
  "client_id": "string"
}
```

## Validation commands
```bash
cd backend
ruff check .
python -m py_compile app/modules/cases/api.py
```

### Curl example (expected HTTP 200)
```bash
export FPMS_TOKEN="REPLACE_ME"
curl -i -X PUT -H "Authorization: Bearer $FPMS_TOKEN" -H "Content-Type: application/json" -d '{"case_no": "string", "case_type": "string"}' "http://localhost:8000/api/v1/cases/REPLACE_ID"
```

## Prompt
In `backend/app/modules/cases/api.py`, implement ONLY the endpoint `PUT /cases/{case_id}` according to `cases/docs/case_02_api.md`.

Requirements:
- Enforce permission using `require_perm("Case.Edit")`.
- Use existing ORM models and services only.
- Return HTTP 200 on success.
- Keep request/response shapes consistent with examples above (adjust only if API doc specifies differently).

Do NOT:
- Add other endpoints
- Modify schema/migrations
- Ask clarification questions
