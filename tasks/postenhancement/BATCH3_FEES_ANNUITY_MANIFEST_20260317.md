# Batch 3 Fees / Annuity Manifest (2026-03-17)

Status: Ready for execution

Purpose:
- convert Batch 3 Cluster C4 into explicit atomic tasks before implementation
- keep execution inside Batch 3 only
- avoid the oversized task failures seen in Batch 1 and Batch 2

## Covered Scope

### In Scope for Batch 3 Implementation

- `US-FE-02`
- `US-FE-03`
- `US-FE-04`
- `US-FE-05`
- `US-FE-06`
- `US-FE-08`
- `FR-FE-03`
- `FR-FE-04`
- `FR-FE-05`
- `FR-FE-06`
- `FR-FE-07`
- `FR-FE-09`

### Explicitly Excluded

- any `Batch 4+` bill / collections / commission implementation
- any `document generation` / export / print / notice-letter generation
- direct repair work for `Fully / Missing / N/A` items
- unrelated UI redesign
- schema changes unless a task file explicitly allows them

## Freeze Summary

Feasible now:
- fee rate calculation modes and reduction/discount behavior
- annuity task instruction / draft / pay-list / gov-payment chain
- fee draft and annuity frontend visibility / status / query parity
- fee overview and case-receipt visibility using existing billing receipt structures

High-risk but still Batch 3:
- `US-FE-06 / FR-FE-07`
- `US-FE-08 / FR-FE-09`

Reason:
- these items touch existing receipt and overview paths that live partly in billing shared logic
- they remain in Batch 3, but must run in serialized ownership and must not expand into Batch 4 bill-offset / dunning / commission logic

## Atomic Task Mapping

| Follow-up ID | Atomic Task File Path | Owner Role | Notes |
|---|---|---|---|
| `BE-Enh-004A` | `tasks/postenhancement/backend/PE-BE-FE-03.md` | `worker` | Fees backend: calc modes, reduction/discount, fee draft amount rules |
| `FE-Enh-004A` | `tasks/postenhancement/frontend/PE-FE-FE-03.md` | `worker` | Fees frontend: rate config and draft/detail/query parity |
| `BE-Enh-004B` | `tasks/postenhancement/backend/PE-BE-AN-08.md` | `worker` | Annuity backend: draft -> pay list -> gov payment -> instruction/status closure |
| `FE-Enh-004B` | `tasks/postenhancement/frontend/PE-FE-AN-06.md` | `worker` | Annuity frontend: task list, pay list, gov payment closure |
| `BE-Enh-005A` | `tasks/postenhancement/backend/PE-BE-FE-04.md` | `worker` | Receipt + fee overview backend follow-up within Batch 3 boundary |
| `FE-Enh-004C` | `tasks/postenhancement/frontend/PE-FE-FE-04.md` | `worker` | Receipt + fee overview frontend follow-up within Batch 3 boundary |
| `QA-Enh-001B3` | `tasks/postenhancement/backend/PE-QA-B3-01.md` | `monitor` | Batch 3 final close audit |

## Shared Ownership Decision

Backend shared ownership files:
- `backend/app/modules/fees/service.py`
- `backend/app/modules/fees/api.py`
- `backend/app/modules/fees/schemas.py`
- `backend/app/modules/annuity/service.py`
- `backend/app/modules/annuity/api.py`
- `backend/app/modules/tasks/task_generation_service.py`
- `backend/app/modules/billing/api.py`
- `backend/app/modules/billing/schemas.py`

Frontend shared ownership files:
- `frontend/src/api/fees.ts`
- `frontend/src/api/fees.types.ts`
- `frontend/src/api/annuity.ts`
- `frontend/src/api/annuity.types.ts`
- `frontend/src/api/billing.ts`
- `frontend/src/api/billing.types.ts`

Conflict decision:
- execution remains serialized by wave
- receipt / overview tasks run after fees + annuity core tasks
- QA close audit runs only after all six implementation tasks complete

## Execution Waves

### Wave 1
- Role: `worker`
- Task file: `tasks/postenhancement/backend/PE-BE-FE-03.md`
- Mode: serialized

### Wave 2
- Role: `worker`
- Task file: `tasks/postenhancement/frontend/PE-FE-FE-03.md`
- Mode: serialized

### Wave 3
- Role: `worker`
- Task file: `tasks/postenhancement/backend/PE-BE-AN-08.md`
- Mode: serialized

### Wave 4
- Role: `worker`
- Task file: `tasks/postenhancement/frontend/PE-FE-AN-06.md`
- Mode: serialized

### Wave 5
- Role: `worker`
- Task file: `tasks/postenhancement/backend/PE-BE-FE-04.md`
- Mode: serialized

### Wave 6
- Role: `worker`
- Task file: `tasks/postenhancement/frontend/PE-FE-FE-04.md`
- Mode: serialized

### Wave 7
- Role: `monitor`
- Task file: `tasks/postenhancement/backend/PE-QA-B3-01.md`
- Mode: serialized

## Stop Rule

- This manifest only authorizes `Batch 3`
- It does not authorize `Batch 4`
