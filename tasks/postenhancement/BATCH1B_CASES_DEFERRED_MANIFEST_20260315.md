# Batch 1B Cases Deferred Manifest (2026-03-15)

Status: Ready for execution

Purpose:
- complete the remaining deferred Batch 1 Case-domain work
- finish `FR-CM-03` foreign-agent quick-create / select / backfill
- finish `FR-CM-05` bacteria deposit, PCT, and invalidation-specific fields
- allow bounded schema/model expansion scoped only to Case-domain needs

## Covered Scope

- `FR-CM-03` foreign-agent select / quick-create / backfill
- `FR-CM-05` bacteria deposit attributes
- `FR-CM-05` PCT international / national phase attributes
- `FR-CM-05` invalidation-specific attributes

## Locked Decisions

- bounded schema / model expansion is allowed for this manifest
- foreign agent reuses `T_Client`
- `T_BioDepositUnit` masterdata is out of scope; this slice stores `deposit_unit_name` as text
- execution remains inside `Batch 1`; no `Batch 2+` work is authorized

## Atomic Task Mapping

| Follow-up ID | Atomic Task File Path | Owner Role | Notes |
|---|---|---|---|
| `BE-Enh-001B-DB` | `tasks/postenhancement/backend/PE-BE-DB-CM-02.md` | `worker` | Case schema/model expansion only |
| `BE-Enh-001B` | `tasks/postenhancement/backend/PE-BE-CM-02.md` | `worker` | Case API/service/business-rule completion |
| `FE-Enh-001B` | `tasks/postenhancement/frontend/PE-FE-CM-03.md` | `worker` | Case UI completion for foreign agent / PCT / invalidation / bio deposit |
| `QA-Enh-001B` | `tasks/postenhancement/backend/PE-QA-CM-03.md` | `monitor` | Deferred Batch 1 close audit |

## Shared Ownership Decision

Backend shared ownership files:
- `backend/app/modules/cases/models.py`
- `backend/app/modules/cases/schemas.py`
- `backend/app/modules/cases/service.py`
- `backend/app/modules/cases/api.py`
- `backend/tests/test_case_fields.py`

Frontend shared ownership files:
- `frontend/src/modules/cases/pages/CaseCreate.vue`
- `frontend/src/modules/cases/pages/CaseEdit.vue`
- `frontend/src/modules/cases/pages/CaseDetail.vue`
- `frontend/src/api/cases.ts`
- `frontend/src/api/cases.types.ts`
- `frontend/src/api/clients.ts`

Conflict decision:
- execution must remain serialized
- DB task must finish before backend business task
- backend business task must finish before frontend task
- QA close audit runs only after both backend and frontend tasks complete

## Execution Waves

### Wave 1

- Role: `worker`
- Task file: `tasks/postenhancement/backend/PE-BE-DB-CM-02.md`
- Mode: serialized

### Wave 2

- Role: `worker`
- Task file: `tasks/postenhancement/backend/PE-BE-CM-02.md`
- Mode: serialized

### Wave 3

- Role: `worker`
- Task file: `tasks/postenhancement/frontend/PE-FE-CM-03.md`
- Mode: serialized

### Wave 4

- Role: `monitor`
- Task file: `tasks/postenhancement/backend/PE-QA-CM-03.md`
- Mode: serialized

## Stop Rule

- This manifest only authorizes deferred `Batch 1` scope closure
- It does not authorize `Batch 2`
