# ENH-07-04-01 — Clients: generate UUID id on create (fix t_client.id NOT NULL)

## Context / Why
POST /api/v1/clients returns 500 with:
- sqlite3.IntegrityError: NOT NULL constraint failed: t_client.id
- SAWarning: PK column has no default generator and no explicit value passed

Root cause: service `create_client()` does not set Client.id, and ORM/DB has no default.

## Target (Atomic – FIXED)
Ensure Client.id is set to a UUID string when creating a new client.

## Allowed files (Strict allowlist)
- backend/app/modules/masterdata/clients/service.py ONLY

## Non-scope
- Do NOT change DB schema/migrations
- Do NOT change models.py
- Do NOT change schemas.py
- Do NOT change api.py

## Required change (EXACT)
In `create_client(...)`:
1) Import `uuid4` from `uuid`
2) When instantiating the Client ORM object, set:
   - `id=str(uuid4())`
3) Keep all other behavior unchanged

## Acceptance checklist
- [ ] Only service.py changed
- [ ] POST /api/v1/clients no longer throws IntegrityError
- [ ] New client is created successfully (201)
- [ ] Ruff + py_compile pass

## Evidence
```bash
curl -i -H "Authorization: Bearer $FPMS_TOKEN" -H "Content-Type: application/json" \
  -d '{"client_code":"C0001","name_cn":"测试客户","name_en":"Test Client","client_type":"CORP","default_currency":"CNY"}' \
  "http://localhost:8000/api/v1/clients"
```

## Validation (MUST RUN)
```bash
./scripts/evidence_run.sh ENH-07-04-01 lint bash -lc "cd backend && ruff check app/modules/masterdata/clients/service.py"
./scripts/evidence_run.sh ENH-07-04-01 fmt  bash -lc "cd backend && ruff format app/modules/masterdata/clients/service.py"
./scripts/evidence_run.sh ENH-07-04-01 test bash -lc "cd backend && python3 -m py_compile app/modules/masterdata/clients/service.py"
./scripts/evidence_finalize.sh ENH-07-04-01
./scripts/task_validate.sh ENH-07-04-01
```

## STOP Contract
STOP if any change outside service.py is required.
