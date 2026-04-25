# BATCH-B-CLOSE-AUDIT-01

Task ID: `BATCH-B-CLOSE-AUDIT-01`

Story Shape Classification:
- shared_file_density: high
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: high

chosen_runbook: `P0-prereq-heavy-story`

## Exact Closure Slice

Close-audit the current B-wave readiness/blocker-drain run and decide whether B-wave automation landing can start.

## Explicit Non-Closure

Do not:
- implement pytest automation handlers
- modify backend/frontend behavior
- modify skeleton data
- mark any B testcase PASS without automation evidence and real smoke

## Remaining Follow-Up Task IDs

- `BE-B-OFFICIAL-DUE-DATE-TASK-GENERATION-01`
- `BE-B-OA-FEE-DRAFT-READINESS-01`
- `BE-B-OA-BILL-PAYMENT-READINESS-01`
- `BE-B-OA-COMMISSION-READINESS-01`
- `PRODUCT-B-NEED-REPLY-DEADLINE-EDIT-CONTRACT-01`

## Allowed Files

- `tasks/batches/BATCH-B-CLOSE-AUDIT-01.md`
- `docs/automation/close_audit/BATCH-B-CLOSE-AUDIT-01.md`
- `artifacts/BATCH-B-CLOSE-AUDIT-01/**`

## Verification Commands

```bash
test -f tasks/batches/BATCH-B-CLOSE-AUDIT-01.md
test -f docs/automation/close_audit/BATCH-B-CLOSE-AUDIT-01.md
rg -n "GO/NO-GO|TC-B-001|TC-B-013|BE-B-OA-FINANCE-READINESS-01|Automation Landing" docs/automation/close_audit/BATCH-B-CLOSE-AUDIT-01.md
./scripts/task_validate.sh BATCH-B-CLOSE-AUDIT-01
```

## Evidence Path

- `artifacts/BATCH-B-CLOSE-AUDIT-01/results.jsonl`
- `artifacts/BATCH-B-CLOSE-AUDIT-01/summary.md`
- `artifacts/BATCH-B-CLOSE-AUDIT-01/git/diff.patch`
