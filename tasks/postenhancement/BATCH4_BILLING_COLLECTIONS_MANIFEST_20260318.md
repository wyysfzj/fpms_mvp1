# Batch 4 Billing / Collections Manifest (2026-03-18)

Status: Ready for execution

Purpose:
- convert Batch 4 Cluster C5 into explicit atomic tasks before implementation
- keep execution inside Batch 4 only
- avoid cluster-sized task definitions and ambiguous close claims

## Covered Scope

### In Scope for Batch 4 Implementation

- `US-BL-02`
- `US-BL-06`
- `US-BL-07`
- `FR-BL-01`
- `FR-BL-03`
- `FR-BL-07`
- `FR-BL-08`
- `FR-BL-09`

### Explicitly Excluded

- any `Batch 5+` commission / consulting implementation
- any `document generation` / export / print / notice-letter generation
- direct repair work for `Fully / Missing / N/A` items
- unrelated billing redesign
- schema changes unless a task file explicitly allows them

## Freeze Summary

Feasible now:
- manual bill API and page contract hardening
- bad-debt / dunning generation / list visibility refinement
- prepayment and offset visibility refinement using existing payment/offset structures

High-risk but still Batch 4:
- `US-BL-07 / FR-BL-09`
- `US-BL-06 / FR-BL-07 / FR-BL-08`

Reason:
- these items touch shared `billing` / `collections` semantics and dirty frontend API files
- they remain in Batch 4, but must run in serialized ownership and must not expand into Batch 5 commission logic or document generation

## Atomic Task Mapping

| Follow-up ID | Atomic Task File Path | Owner Role | Notes |
|---|---|---|---|
| `BE-Enh-006A` | `tasks/postenhancement/backend/PE-BE-BL-01.md` | `worker` | Manual bill backend contract slice |
| `FE-Enh-005A` | `tasks/postenhancement/frontend/PE-FE-BL-01.md` | `worker` | Manual bill frontend form slice |
| `BE-Enh-007A` | `tasks/postenhancement/backend/PE-BE-BL-02.md` | `worker` | Bad-debt / dunning backend slice |
| `FE-Enh-005B` | `tasks/postenhancement/frontend/PE-FE-BL-02.md` | `worker` | Dunning frontend visibility slice |
| `BE-Enh-007B` | `tasks/postenhancement/backend/PE-BE-BL-03.md` | `worker` | Prepayment / offset backend visibility slice |
| `FE-Enh-005C` | `tasks/postenhancement/frontend/PE-FE-BL-03.md` | `worker` | Prepayment / offset frontend visibility slice |
| `QA-Enh-001B4` | `tasks/postenhancement/backend/PE-QA-B4-01.md` | `monitor` | Batch 4 final close audit with item-to-slice ledger |

## Shared Ownership Decision

Backend shared ownership files:
- `backend/app/modules/billing/api.py`
- `backend/app/modules/billing/service.py`
- `backend/app/modules/billing/schemas.py`
- `backend/app/modules/collections/api.py`
- `backend/app/modules/collections/service.py`
- `backend/app/modules/**/schemas.py`

Frontend shared ownership files:
- `frontend/src/api/billing.ts`
- `frontend/src/api/billing.types.ts`
- `frontend/src/api/collections.ts`
- `frontend/src/api/collections.types.ts`

Conflict decision:
- execution remains serialized by wave
- manual bill tasks run before dunning / prepayment tasks
- QA close audit runs only after all six implementation tasks complete

## Execution Waves

### Wave 1
- Role: `worker`
- Task file: `tasks/postenhancement/backend/PE-BE-BL-01.md`
- Mode: serialized

### Wave 2
- Role: `worker`
- Task file: `tasks/postenhancement/frontend/PE-FE-BL-01.md`
- Mode: serialized

### Wave 3
- Role: `worker`
- Task file: `tasks/postenhancement/backend/PE-BE-BL-02.md`
- Mode: serialized

### Wave 4
- Role: `worker`
- Task file: `tasks/postenhancement/frontend/PE-FE-BL-02.md`
- Mode: serialized

### Wave 5
- Role: `worker`
- Task file: `tasks/postenhancement/backend/PE-BE-BL-03.md`
- Mode: serialized

### Wave 6
- Role: `worker`
- Task file: `tasks/postenhancement/frontend/PE-FE-BL-03.md`
- Mode: serialized

### Wave 7
- Role: `monitor`
- Task file: `tasks/postenhancement/backend/PE-QA-B4-01.md`
- Mode: serialized

## Stop Rule

- This manifest only authorizes `Batch 4`
- It does not authorize `Batch 5`
