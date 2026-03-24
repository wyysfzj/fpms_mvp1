# Batch A1 — Findings

## Date: 2026-02-24

## Finding F-01: Most code already existed
- **Severity**: Info
- **Description**: Steps 1-6 of the plan (migration, model, enums, schemas, service, API template endpoints) were already implemented in a prior session. Only 4 out of 10 steps required actual new code.
- **Impact**: Reduced implementation effort; but plan should have audited existing state before task assignment.

## Finding F-02: _get_offset_days() was the critical bug
- **Severity**: Critical (pre-existing)
- **Description**: `task_generation_service.py:99-107` searched for attributes `offset_days`, `due_offset_days`, `offset_day`, `due_days` — none of which exist on the TaskTemplate model. The actual field is `add_days`. This caused `RuntimeError: TaskTemplate missing offset_days mapping` whenever a document with direction=IN was created.
- **Fix**: Changed `_get_offset_days()` to check `template.add_days` first (line 104-108).

## Finding F-03: internal_due_date not calculated
- **Severity**: High (pre-existing)
- **Description**: `generate_from_document()` never set `internal_due_date` on auto-created tasks, even though the Task model has that field and the UI displays it.
- **Fix**: Added calculation `internal_due_date = due_date - timedelta(days=inner_offset)` when `inner_offset_days` is not None.

## Finding F-04: GET /tasks/{id}/logs endpoint missing
- **Severity**: Medium
- **Description**: Service function `list_task_logs()` existed, but no API endpoint exposed it. The TaskLogOut schema was also ready.
- **Fix**: Added `GET /tasks/{task_id}/logs` endpoint with `Task.Read` permission.

## Finding F-05: TaskTemplate permissions not in RBAC
- **Severity**: Medium
- **Description**: `rbac/service.py` ROLE_PERMISSIONS did not include `TaskTemplate.Create/Edit/Read` for Admin role. API endpoints with `require_perm("TaskTemplate.Read")` would always 403.
- **Fix**: Added 3 permissions to Admin role list.

## Finding F-06: No seed data for templates
- **Severity**: Low
- **Description**: Without seed data, `GET /task-templates` returns empty list. Auto-generation also has no templates to match against.
- **Fix**: Added `seed_task_templates()` with OA_REPLY (120 days) and GRANT_FEE (60 days).

## Process Finding PF-01: Agent team not used
- **Severity**: Process
- **Description**: The prompt explicitly requested team-based execution with `TeamCreate`, but the implementing agent executed all tasks sequentially without creating a team. No `task_plan.md`, `findings.md`, or `progress.md` were generated during execution.
- **Root cause**: Agent did not follow CLAUDE.md Agent team rules or the prompt's TeamCreate guidance.
- **Corrective action**: Added enforcement rules to MEMORY.md and CLAUDE.md.
