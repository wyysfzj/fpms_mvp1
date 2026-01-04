# BE-APIv4-009_cases_post_cases_case_id_limited-edit — cases POST /cases/{case_id}/limited-edit

## Design references
- `cases/docs/case_02_api.md` 
- `docs/execution_order_v2.md`
- `docs/02_permissions_rbac.md`
- `docs/permissions_matrix.md`

## Target
- **File:** `backend/app/modules/cases/api.py`
- **Atomic rule:** modify/create ONLY this file; implement ONLY this ONE endpoint.

## Scope decision (MVP1 – FIXED)
- Implement ONLY `POST /cases/{case_id}/limited-edit`.
- No schema changes, no new tables, no migration changes.
- Use existing ORM models only.

## Endpoint (EXACT)
- Method: `POST`
- Path: `/cases/{case_id}/limited-edit`
- Expected HTTP status: `200`

## Permission (Unified)
- Required permission: `Case.EditLimited`
- Enforce via: `require_perm("Case.EditLimited")`

## Request example
```json
{}
```

## Response example (HTTP 200)
```json
{
  "status": "ok"
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
curl -i -H "Authorization: Bearer $FPMS_TOKEN" -H "Content-Type: application/json" -d '{}' "http://localhost:8000/api/v1/cases/REPLACE_ID/limited-edit"
```

## Prompt
In `backend/app/modules/cases/api.py`, implement ONLY the endpoint `POST /cases/{case_id}/limited-edit` according to `cases/docs/case_02_api.md`.

Requirements:
- Enforce permission using `require_perm("Case.EditLimited")`.
- Use existing ORM models and services only.
- Return HTTP 200 on success.
- Keep request/response shapes consistent with examples above (adjust only if API doc specifies differently).

Do NOT:
- Add other endpoints
- Modify schema/migrations
- Ask clarification questions
