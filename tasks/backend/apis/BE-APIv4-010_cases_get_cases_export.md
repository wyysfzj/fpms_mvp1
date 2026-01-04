# BE-APIv4-010_cases_get_cases_export — cases GET /cases/export

## Design references
- `cases/docs/case_02_api.md` 
- `docs/execution_order_v2.md`
- `docs/02_permissions_rbac.md`
- `docs/permissions_matrix.md`

## Target
- **File:** `backend/app/modules/cases/api.py`
- **Atomic rule:** modify/create ONLY this file; implement ONLY this ONE endpoint.

## Scope decision (MVP1 – FIXED)
- Implement ONLY `GET /cases/export`.
- No schema changes, no new tables, no migration changes.
- Use existing ORM models only.

## Endpoint (EXACT)
- Method: `GET`
- Path: `/cases/export`
- Expected HTTP status: `200`

## Permission (Unified)
- Required permission: `Case.Export`
- Enforce via: `require_perm("Case.Export")`

## Request example
```json
{}
```

## Response example (HTTP 200)
```json
{
  "items": [
    {
      "id": "string",
      "case_no": "string",
      "case_type": "string",
      "patent_category": "string"
    }
  ],
  "page": 1,
  "page_size": 20,
  "total": 1
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
curl -i -H "Authorization: Bearer $FPMS_TOKEN" "http://localhost:8000/api/v1/cases/export"
```

## Prompt
In `backend/app/modules/cases/api.py`, implement ONLY the endpoint `GET /cases/export` according to `cases/docs/case_02_api.md`.

Requirements:
- Enforce permission using `require_perm("Case.Export")`.
- Use existing ORM models and services only.
- Return HTTP 200 on success.
- Keep request/response shapes consistent with examples above (adjust only if API doc specifies differently).

Do NOT:
- Add other endpoints
- Modify schema/migrations
- Ask clarification questions
