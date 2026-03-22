# Batch 5 Commission / Consulting Manifest (2026-03-21)

Status: Executed with adjusted close scope

Purpose:
- convert Batch 5 Cluster C6 + C7 into explicit atomic tasks before implementation
- keep execution inside Batch 5 only
- preserve exact closure slices and explicit non-closure boundaries
- record the later approved scope-adjustment that narrows Batch 5 close scope to commission items only

## Covered Scope

### In Scope for Batch 5 Implementation

- `US-COM-02`
- `US-COM-06`
- `FR-COM-02`
- `FR-COM-06`
- `FR-COM-07`

### Moved Out of Adjusted Batch 5 Close Scope

- `US-CS-01`
- `US-CS-05`
- `FR-CS-01`
- `FR-CS-06`

### Explicitly Excluded

- any post-Batch-5 work
- `document generation` / export / print / template rendering
- direct repair work for `Fully / Missing / N/A` items
- unrelated billing / cases redesign
- schema changes unless a task file explicitly allows them

## Freeze Summary

Feasible now:
- commission auto-generation path expansion on existing billing hooks
- commission settlement `S1_Done / S2_Done` completion semantics
- commission report/query completeness and UI visibility refinement

Blocked at original freeze:
- `US-CS-01 / FR-CS-01`
  - current `Case` model does not carry consulting/search-specific attributes
  - current no-schema Batch 5 assumption does not permit adding durable storage

Deferred at original freeze:
- `US-CS-05 / FR-CS-06`
  - existing cross-module chain spans `consulting + billing + commission`
  - no single schema-safe exact closure slice is yet approved

Scope-adjustment decision:
- see `docs/FPMS_Batch5_Scope_Adjustment_20260321.md`
- adjusted Batch 5 close scope keeps only the commission rows below
- consulting/search rows are moved out of Batch 5 close scope and are not counted in the final close decision

## Atomic Task Mapping

| Follow-up ID | Atomic Task File Path | Owner Role | Notes |
|---|---|---|---|
| `BE-Enh-008A` | `tasks/postenhancement/backend/PE-BE-COM-01.md` | `worker` | Manual bill path commission auto-generation slice |
| `FE-Enh-006A` | `tasks/postenhancement/frontend/PE-FE-COM-01.md` | `worker` | Commission list stage / settleability visibility slice |
| `BE-Enh-008B` | `tasks/postenhancement/backend/PE-BE-COM-02.md` | `worker` | Settlement generation marks `S1_Done / S2_Done` slice |
| `FE-Enh-006B` | `tasks/postenhancement/frontend/PE-FE-COM-02.md` | `worker` | Settlement page stage completion visibility slice |
| `BE-Enh-008C` | `tasks/postenhancement/backend/PE-BE-COM-03.md` | `worker` | Settlement report completeness slice |
| `FE-Enh-006C` | `tasks/postenhancement/frontend/PE-FE-COM-03.md` | `worker` | Settlement report UI completeness slice |
| `BE-Enh-009A` | `Moved out by scope adjustment` | `worker` | `US-CS-01 / FR-CS-01` removed from adjusted Batch 5 close scope |
| `BE-Enh-009B` | `Moved out by scope adjustment` | `worker` | `US-CS-05 / FR-CS-06` removed from adjusted Batch 5 close scope |
| `QA-Enh-001B5` | `tasks/postenhancement/backend/PE-QA-B5-01.md` | `monitor` | Batch 5 final close audit with item-to-slice ledger |

## Shared Ownership Decision

Backend shared ownership files:
- `backend/app/modules/commission/api.py`
- `backend/app/modules/commission/service.py`
- `backend/app/modules/consulting/api.py`
- `backend/app/modules/consulting/service.py`
- `backend/app/modules/billing/service.py`
- `backend/app/modules/cases/service.py`
- `backend/app/modules/**/schemas.py`

Frontend shared ownership files:
- `frontend/src/api/commission.ts`
- `frontend/src/api/commission.types.ts`
- `frontend/src/api/consulting.ts`
- `frontend/src/api/consulting.types.ts`

Conflict decision:
- execution remains serialized by wave
- all `commission` backend tasks run before frontend tasks that consume the changed contract
- `consulting` rows stay blocked/deferred and are not executable under this manifest
- QA close audit runs only after all executable implementation tasks complete

## Execution Waves

### Wave 1
- Role: `worker`
- Task file: `tasks/postenhancement/backend/PE-BE-COM-01.md`
- Mode: serialized

### Wave 2
- Role: `worker`
- Task file: `tasks/postenhancement/frontend/PE-FE-COM-01.md`
- Mode: serialized

### Wave 3
- Role: `worker`
- Task file: `tasks/postenhancement/backend/PE-BE-COM-02.md`
- Mode: serialized

### Wave 4
- Role: `worker`
- Task file: `tasks/postenhancement/frontend/PE-FE-COM-02.md`
- Mode: serialized

### Wave 5
- Role: `worker`
- Task file: `tasks/postenhancement/backend/PE-BE-COM-03.md`
- Mode: serialized

### Wave 6
- Role: `worker`
- Task file: `tasks/postenhancement/frontend/PE-FE-COM-03.md`
- Mode: serialized

### Wave 7
- Role: `monitor`
- Task file: `tasks/postenhancement/backend/PE-QA-B5-01.md`
- Mode: serialized

## Stop Rule

- This manifest only authorizes `Batch 5`
- It does not authorize any later batch
- adjusted Batch 5 close scope is commission-only
- consulting/search residual scope has been moved out by `docs/FPMS_Batch5_Scope_Adjustment_20260321.md`
