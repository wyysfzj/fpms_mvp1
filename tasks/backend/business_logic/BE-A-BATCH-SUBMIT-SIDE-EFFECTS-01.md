# BE-A-BATCH-SUBMIT-SIDE-EFFECTS-01

## Task

- Task file path: `tasks/backend/business_logic/BE-A-BATCH-SUBMIT-SIDE-EFFECTS-01.md`
- Task ID: `BE-A-BATCH-SUBMIT-SIDE-EFFECTS-01`
- Role: worker
- chosen_runbook: `P0-prereq-heavy-story`

## Story Shape Classification

- shared_file_density: high
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: medium
- chosen_runbook: `P0-prereq-heavy-story`

## Exact Closure Slice

Implement real backend side effects for `POST /api/v1/cases/batch-filing/submit`:

- preserve existing batch filing status transition behavior
- when `generate_list=true`, register a stable submission-list document record
- create or trigger one idempotent `APPLY_FEE_LIMIT` open task per updated case
- keep response schema backward compatible
- preserve existing batch filing error semantics

## Explicit Non-Closure

- Do not implement `handle_tc_a_011`.
- Do not modify `FPMS_Automation_Skeleton_Pack/pytest_python/**`.
- Do not modify skeleton YAML / JSON / manifest / schema / Playwright.
- Do not modify frontend UI.
- Do not implement full `TC-A-013` deadline calculation assertions.
- Do not implement fee draft, pay list, bill, payment, or commission logic.

## Current Status

`BLOCKED`.

Discovery found a required shared API wiring change outside this task's allowlist:

- `CaseBatchFilingActionIn` already contains `generate_list`.
- `backend/app/modules/cases/api.py::submit_batch_filing` does not pass `payload.generate_list` into `execute_batch_filing`.
- This task's allowlist excludes `backend/app/modules/cases/api.py`.

Implementing the requested behavior without `api.py` would require either:

- silently modifying an unallowed file, or
- changing service semantics so documents are always created even when `generate_list=false`.

Both would violate the task prompt.

## Allowed Files

This blocked task only modified:

- `tasks/backend/business_logic/BE-A-BATCH-SUBMIT-SIDE-EFFECTS-01.md`
- `artifacts/BE-A-BATCH-SUBMIT-SIDE-EFFECTS-01/**`

## Verification Commands

Discovery commands:

```bash
rg -n "generate_list|submit_batch_filing|execute_batch_filing|CaseBatchFilingActionIn|Document\\(|APPLY_FEE_LIMIT" backend/app/modules/cases/api.py backend/app/modules/cases/service.py backend/app/modules/cases/schemas.py backend/app/modules/documents/models.py backend/app/modules/tasks/models.py backend/scripts/seed_dev.py
```

Task gate:

```bash
./scripts/task_validate.sh BE-A-BATCH-SUBMIT-SIDE-EFFECTS-01
```

## Evidence Path

- `artifacts/BE-A-BATCH-SUBMIT-SIDE-EFFECTS-01/`

## Remaining Follow-Up Task IDs

- `BE-A-BATCH-SUBMIT-SIDE-EFFECTS-02`
