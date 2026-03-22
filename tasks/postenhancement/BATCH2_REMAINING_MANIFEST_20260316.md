# Batch 2 Remaining Manifest (2026-03-16)

Status: Ready for execution

Purpose:
- complete the remaining feasible Batch 2 scope after the first partial execution
- replace oversized Batch 2 task files with smaller atomic follow-up tasks
- keep all execution inside Batch 2 only

## Covered Remaining Scope

### Documents

- `US-WD-01`
- `US-WD-02`
- `US-WD-03`
- `US-WD-04`
- `US-WD-06`
- `FR-WD-01`
- `FR-WD-03`
- `FR-WD-04`
- `FR-WD-07`

### Tasks / Deadlines

- `US-DL-01`
- `US-DL-02`
- `US-DL-03`
- `US-DL-04`
- `US-DL-05`
- `US-DL-07`
- `FR-DL-01`
- `FR-DL-02`
- `FR-DL-04`
- `FR-DL-05`
- `FR-DL-06`
- `FR-DL-08`

## Explicitly Excluded Scope

- any `Batch 3+` work
- any `document generation` / printing / export / certificate / envelope / handoff-sheet implementation
- `FR-WD-02`
- `US-WD-07`
- `FR-WD-08`
- `FR-WD-09`
- `US-DL-06`
- `FR-DL-07`
- direct repair work for `Fully / Missing / N/A` items

## Atomic Task Mapping

| Follow-up ID | Atomic Task File Path | Owner Role | Notes |
|---|---|---|---|
| `BE-Enh-002B` | `tasks/postenhancement/backend/PE-BE-WD-03.md` | `worker` | Documents backend defaults + reply/deadline follow-up |
| `FE-Enh-002B` | `tasks/postenhancement/frontend/PE-FE-WD-03.md` | `worker` | Documents frontend defaults/detail follow-up |
| `BE-Enh-003B` | `tasks/postenhancement/backend/PE-BE-DL-03.md` | `worker` | Tasks backend views + today follow-up |
| `FE-Enh-003B` | `tasks/postenhancement/frontend/PE-FE-DL-03.md` | `worker` | Tasks frontend views + today follow-up |
| `QA-Enh-001B2R` | `tasks/postenhancement/backend/PE-QA-B2-02.md` | `monitor` | Batch 2 final close audit |

## Shared Ownership Decision

Backend shared ownership files:
- `backend/app/modules/documents/service.py`
- `backend/app/modules/documents/schemas.py`
- `backend/app/modules/tasks/service.py`
- `backend/app/modules/tasks/schemas.py`
- `backend/app/modules/tasks/task_generation_service.py`
- `backend/app/modules/tasks/api.py`

Frontend shared ownership files:
- `frontend/src/api/documents.ts`
- `frontend/src/api/documents.types.ts`
- `frontend/src/api/tasks.ts`
- `frontend/src/api/tasks.types.ts`

Conflict decision:
- execution remains serialized by wave
- documents backend before documents frontend
- tasks backend before tasks frontend
- QA close audit runs only after all four implementation tasks complete

## Execution Waves

### Wave 1
- Role: `worker`
- Task file: `tasks/postenhancement/backend/PE-BE-WD-03.md`
- Mode: serialized

### Wave 2
- Role: `worker`
- Task file: `tasks/postenhancement/frontend/PE-FE-WD-03.md`
- Mode: serialized

### Wave 3
- Role: `worker`
- Task file: `tasks/postenhancement/backend/PE-BE-DL-03.md`
- Mode: serialized

### Wave 4
- Role: `worker`
- Task file: `tasks/postenhancement/frontend/PE-FE-DL-03.md`
- Mode: serialized

### Wave 5
- Role: `monitor`
- Task file: `tasks/postenhancement/backend/PE-QA-B2-02.md`
- Mode: serialized

## Stop Rule

- This manifest only authorizes the remaining `Batch 2` scope
- It does not authorize `Batch 3`
