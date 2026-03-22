# Batch 2 Documents + Tasks Manifest (2026-03-15)

Status: Ready for execution

Purpose:
- implement Batch 2 only
- cover the Batch 2 `Partially Implemented` scope for Documents and Tasks/Deadlines
- convert plan-driven scope into explicit atomic task files for AGENTS-compliant execution

## Covered Scope

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

The following scope is NOT authorized by this manifest:
- any `Batch 3+` work
- any `document generation` / printing / envelope / handoff-sheet implementation
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
| `BE-Enh-002A` | `tasks/postenhancement/backend/PE-BE-WD-02.md` | `worker` | Documents backend completion |
| `FE-Enh-002A` | `tasks/postenhancement/frontend/PE-FE-WD-02.md` | `worker` | Documents frontend completion |
| `BE-Enh-003A` | `tasks/postenhancement/backend/PE-BE-DL-02.md` | `worker` | Tasks/Deadlines backend completion |
| `FE-Enh-003A` | `tasks/postenhancement/frontend/PE-FE-DL-02.md` | `worker` | Tasks/Deadlines frontend completion |
| `QA-Enh-001B2` | `tasks/postenhancement/backend/PE-QA-B2-01.md` | `monitor` | Batch 2 close audit and evidence gate |

## Shared Ownership Decision

Backend shared ownership files:
- `backend/app/modules/documents/service.py`
- `backend/app/modules/documents/schemas.py`
- `backend/app/modules/tasks/service.py`
- `backend/app/modules/tasks/schemas.py`
- `backend/app/modules/tasks/task_generation_service.py`

Frontend shared ownership files:
- `frontend/src/api/documents.ts`
- `frontend/src/api/documents.types.ts`
- `frontend/src/api/tasks.ts`
- `frontend/src/api/tasks.types.ts`

Cross-domain shared ownership files:
- `backend/app/modules/documents/service.py`
- `backend/app/modules/tasks/task_generation_service.py`

Conflict decision:
- execution must remain serialized by wave
- Documents backend must complete before Documents frontend
- Tasks backend must complete before Tasks frontend
- Tasks backend must not overlap Documents backend because of document/task generation linkage
- QA close audit must run only after all four implementation tasks complete

## Dirty Worktree Note

Current worktree already contains unrelated modifications in Batch 2-adjacent files.
Execution owners must:
- keep each task strictly inside its allowlist
- isolate task diff evidence by task file
- avoid claiming unrelated dirty files as completion evidence

## Execution Waves

### Wave 1

- Role: `worker`
- Task file: `tasks/postenhancement/backend/PE-BE-WD-02.md`
- Mode: serialized

### Wave 2

- Role: `worker`
- Task file: `tasks/postenhancement/frontend/PE-FE-WD-02.md`
- Mode: serialized

### Wave 3

- Role: `worker`
- Task file: `tasks/postenhancement/backend/PE-BE-DL-02.md`
- Mode: serialized

### Wave 4

- Role: `worker`
- Task file: `tasks/postenhancement/frontend/PE-FE-DL-02.md`
- Mode: serialized

### Wave 5

- Role: `monitor`
- Task file: `tasks/postenhancement/backend/PE-QA-B2-01.md`
- Mode: serialized

## Stop Rule

- This manifest only authorizes `Batch 2`
- It does not authorize `Batch 3`
