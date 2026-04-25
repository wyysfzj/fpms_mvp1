# BATCH-B-BLOCKER-DRAIN-02-CLOSE-AUDIT

Task ID: `BATCH-B-BLOCKER-DRAIN-02-CLOSE-AUDIT`

Story Shape Classification:
- shared_file_density: high
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: high

chosen_runbook: `P0-prereq-heavy-story`

## Exact Closure Slice

Close-audit `BATCH-B-BLOCKER-DRAIN-02` and decide whether B-wave automation landing can start.

## Explicit Non-Closure

Do not:
- implement pytest automation handlers
- modify backend/frontend behavior
- modify skeleton data
- mark any B testcase PASS without automation evidence and real smoke

## Remaining Follow-Up Task IDs

- `BE-B-OA-BILL-PAYMENT-READINESS-01`
- `BE-B-OA-COMMISSION-READINESS-01`
- `BE-B-NEED-REPLY-DEADLINE-EDIT-RULE-01`

## Allowed Files

- `tasks/batches/BATCH-B-BLOCKER-DRAIN-02-CLOSE-AUDIT.md`
- `docs/automation/close_audit/BATCH-B-BLOCKER-DRAIN-02-CLOSE-AUDIT.md`
- `artifacts/BATCH-B-BLOCKER-DRAIN-02-CLOSE-AUDIT/**`

## Verification Commands

```bash
test -f tasks/batches/BATCH-B-BLOCKER-DRAIN-02-CLOSE-AUDIT.md
test -f docs/automation/close_audit/BATCH-B-BLOCKER-DRAIN-02-CLOSE-AUDIT.md
rg -n "GO/NO-GO|TC-B-002|TC-B-009|TC-B-013|partial automation" docs/automation/close_audit/BATCH-B-BLOCKER-DRAIN-02-CLOSE-AUDIT.md
./scripts/task_validate.sh BATCH-B-BLOCKER-DRAIN-02-CLOSE-AUDIT
```

## Evidence Path

- `artifacts/BATCH-B-BLOCKER-DRAIN-02-CLOSE-AUDIT/results.jsonl`
- `artifacts/BATCH-B-BLOCKER-DRAIN-02-CLOSE-AUDIT/summary.md`
- `artifacts/BATCH-B-BLOCKER-DRAIN-02-CLOSE-AUDIT/git/diff.patch`
