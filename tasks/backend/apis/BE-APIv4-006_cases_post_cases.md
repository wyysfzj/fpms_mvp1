# BE-APIv4-006_cases_post_cases — cases POST /cases

## Design references
- `cases/docs/case_02_api.md` 
- `docs/execution_order_v2.md`
- `docs/02_permissions_rbac.md`
- `docs/permissions_matrix.md`

## Target
- **File:** `backend/app/modules/cases/api.py`
- **Atomic rule:** modify/create ONLY this file; implement ONLY this ONE endpoint.

## Scope decision (MVP1 – FIXED)
- Implement ONLY `POST /cases`.
- No schema changes, no new tables, no migration changes.
- Use existing ORM models only.

## Endpoint (EXACT)
- Method: `POST`
- Path: `/cases`
- Expected HTTP status: `201`

## Permission (Unified)
- Required permission: `Case.Create`
- Enforce via: `require_perm("Case.Create")`

## Request example
```json
{}
```

## Response example (HTTP 201)
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

### Curl example (expected HTTP 201)
```bash
export FPMS_TOKEN="REPLACE_ME"
curl -i -H "Authorization: Bearer $FPMS_TOKEN" -H "Content-Type: application/json" -d '{}' "http://localhost:8000/api/v1/cases"
```

## Prompt
In `backend/app/modules/cases/api.py`, implement ONLY the endpoint `POST /cases` according to `cases/docs/case_02_api.md`.

Requirements:
- Enforce permission using `require_perm("Case.Create")`.
- Use existing ORM models and services only.
- Return HTTP 201 on success.
- Keep request/response shapes consistent with examples above (adjust only if API doc specifies differently).

Do NOT:
- Add other endpoints
- Modify schema/migrations
- Ask clarification questions
