# BATCH-B-BLOCKER-DRAIN-02

Batch ID: `BATCH-B-BLOCKER-DRAIN-02`

Story Shape Classification:
- shared_file_density: high
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: high

chosen_runbook: `P0-prereq-heavy-story`

## Goal

Continue B-wave blocker drain after `BATCH-B-CLOSE-AUDIT-01`.

## Critical Rules

- One atomic task equals one exact task file path.
- Do not implement pytest automation handlers in this batch.
- Do not modify `FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_b.py`.
- Shared backend files and SQLite write tests must be serialized.
- Product ambiguity must be closed by PRODUCT tasks before backend guessing.

## Execution Order

### Wave 1: OfficialDueDate

Task ID: `BE-B-OFFICIAL-DUE-DATE-TASK-GENERATION-01`

Task file: `tasks/backend/business_logic/BE-B-OFFICIAL-DUE-DATE-TASK-GENERATION-01.md`

Exact closure slice:
- Parse `OfficialDueDate` from document `extra_data`.
- Use `OfficialDueDate` as generated task `due_date`.
- Preserve generated task `base_date` as document `doc_date`.
- Preserve internal deadline/reminder calculations from the effective due date.
- Return stable `DOCUMENT_OFFICIAL_DUE_DATE_INVALID` for invalid values.

Allowed files:
- `tasks/backend/business_logic/BE-B-OFFICIAL-DUE-DATE-TASK-GENERATION-01.md`
- `backend/app/modules/tasks/task_generation_service.py`
- `backend/app/modules/documents/service.py`
- `backend/tests/test_b_official_due_date_task_generation.py`
- `artifacts/BE-B-OFFICIAL-DUE-DATE-TASK-GENERATION-01/**`

Status: `EXECUTED_PASS`

### Wave 2: OA Finance Split

Do not implement as one mega task.

Follow-up task candidates:
- `BE-B-OA-FEE-DRAFT-READINESS-01`
- `BE-B-OA-BILL-PAYMENT-READINESS-01`
- `BE-B-OA-COMMISSION-READINESS-01`

Each task must have its own exact closure slice and allowlist before execution.

Executed in this batch:
- `BE-B-OA-FEE-DRAFT-READINESS-01`: PASS

Remaining:
- `BE-B-OA-BILL-PAYMENT-READINESS-01`
- `BE-B-OA-COMMISSION-READINESS-01`

### Wave 3: NeedReply/Deadline Product Contract

Task ID: `PRODUCT-B-NEED-REPLY-DEADLINE-EDIT-CONTRACT-01`

Status: `EXECUTED_PASS`

Decision:
- `TC-B-013` requires explicit reply-task action semantics before backend implementation.
- Follow-up backend task: `BE-B-NEED-REPLY-DEADLINE-EDIT-RULE-01`.

## Evidence

- `artifacts/BATCH-B-BLOCKER-DRAIN-02/results.jsonl`
- `artifacts/BATCH-B-BLOCKER-DRAIN-02/summary.md`
- `artifacts/BATCH-B-BLOCKER-DRAIN-02/git/diff.patch`
