# BATCH-A-DEPENDENT-UNHAPPY-P0P1-01-CLOSE-AUDIT

## Story Shape Classification

- shared_file_density: low
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: medium
- chosen_runbook: P0-prereq-heavy-story

## Exact Closure Slice

Audit Batch 3 dependent unhappy P0/P1 close readiness for:

- `TC-A-012`
- `TC-A-016`
- `TC-A-018`
- `TC-A-020`
- `TC-A-022`
- `TC-A-024`

This task closes only the final QA close audit:

1. Verify each in-scope testcase maps to PASS product/backend/automation evidence where applicable.
2. Verify required artifact triplets exist for the relevant tasks.
3. Verify task gates pass for relevant tasks.
4. Verify deferred product decisions are explicit and outside the approved Batch 3 MVP assertion surface.
5. Verify no backend/frontend/pytest handler/skeleton data changes are made by this close audit.

## Explicit Non-Closure

Do not implement new backend rules, frontend UI, pytest handlers, skeleton data, Playwright assets, migrations, or product behavior.

Do not reopen deferred product scope:

- TC-A-016 manual fee code/name blank branch.
- TC-A-016 manual fee type mismatch branch.
- TC-A-018 stale planned-pay-date warning.
- TC-A-018 paid official-payment edit/audit.

## Remaining Follow-Up Task IDs

- `BATCH-A-P1-COMPLETION-01-READINESS-GATE`
- `PRODUCT-A-GOV-PAYLIST-PAID-EDIT-AUDIT-CONTRACT-01`
- `PRODUCT-A-MANUAL-FEE-ITEM-CONTRACT-01`

## Allowed Files

- `tasks/batches/BATCH-A-DEPENDENT-UNHAPPY-P0P1-01-CLOSE-AUDIT.md`
- `docs/automation/close_audit/BATCH-A-DEPENDENT-UNHAPPY-P0P1-01-CLOSE-AUDIT.md`
- `artifacts/BATCH-A-DEPENDENT-UNHAPPY-P0P1-01-CLOSE-AUDIT/**`

## Verification Commands

```bash
./scripts/evidence_run.sh BATCH-A-DEPENDENT-UNHAPPY-P0P1-01-CLOSE-AUDIT lint /bin/zsh -lc 'test -f tasks/batches/BATCH-A-DEPENDENT-UNHAPPY-P0P1-01-CLOSE-AUDIT.md && test -f docs/automation/close_audit/BATCH-A-DEPENDENT-UNHAPPY-P0P1-01-CLOSE-AUDIT.md'
./scripts/evidence_run.sh BATCH-A-DEPENDENT-UNHAPPY-P0P1-01-CLOSE-AUDIT test /bin/zsh -lc './scripts/task_validate.sh BATCH-A-DEPENDENT-UNHAPPY-P0P1-01 && ./scripts/task_validate.sh A-AUTO-PY-A-BATCH-FILING-VALIDATION-P0-01 && ./scripts/task_validate.sh A-AUTO-PY-A-APPLY-FEE-INVALID-P1-01 && ./scripts/task_validate.sh A-AUTO-PY-A-GOV-PAYLIST-VALIDATION-P1-01 && ./scripts/task_validate.sh A-AUTO-PY-A-BILL-INVALID-COMBOS-P1-01 && ./scripts/task_validate.sh A-AUTO-PY-A-PAYMENT-OFFSET-VALIDATION-P1-01 && ./scripts/task_validate.sh A-AUTO-PY-A-COMMISSION-WAITPAY-P1-01'
./scripts/evidence_run.sh BATCH-A-DEPENDENT-UNHAPPY-P0P1-01-CLOSE-AUDIT task_gate ./scripts/task_validate.sh BATCH-A-DEPENDENT-UNHAPPY-P0P1-01-CLOSE-AUDIT
```

## Evidence Path

- `artifacts/BATCH-A-DEPENDENT-UNHAPPY-P0P1-01-CLOSE-AUDIT/results.jsonl`
- `artifacts/BATCH-A-DEPENDENT-UNHAPPY-P0P1-01-CLOSE-AUDIT/summary.md`
- `artifacts/BATCH-A-DEPENDENT-UNHAPPY-P0P1-01-CLOSE-AUDIT/git/diff.patch`
