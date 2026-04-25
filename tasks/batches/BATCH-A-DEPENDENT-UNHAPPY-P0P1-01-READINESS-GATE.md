# BATCH-A-DEPENDENT-UNHAPPY-P0P1-01-READINESS-GATE

## Story Shape Classification

- shared_file_density: high
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: high
- chosen_runbook: P0-prereq-heavy-story

## Task

- Task ID: BATCH-A-DEPENDENT-UNHAPPY-P0P1-01-READINESS-GATE
- Role: lead / worker coordinator
- Scope: Batch 3 dependent unhappy P0/P1 readiness gate and blocker drain preparation for TC-A-012, TC-A-016, TC-A-018, TC-A-020, TC-A-022, and TC-A-024.

## Exact Closure Slice

This task closes only the readiness gate for Batch 3 dependent unhappy P0/P1:

1. Build a blocker ledger for TC-A-012, TC-A-016, TC-A-018, TC-A-020, TC-A-022, and TC-A-024.
2. Build a capability matrix for backend endpoints, services, response stability, and automation entry points.
3. Build backend rule, product contract, test-maintenance, seed/config, allowlist, and state-machine reachability matrices.
4. Build an executable blocker drain manifest with one exact task file per blocker.
5. Build an automation landing manifest that only starts tasks whose blockers are clear.
6. Record evidence and gate status for the readiness task.

## Explicit Non-Closure

This task does not:

- implement pytest automation handlers
- remove any `@skeleton_case`
- modify `FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_a.py`
- modify backend service/API/schema/model files
- modify frontend UI
- modify skeleton YAML / JSON / manifest / schema / Playwright assets
- run real smoke as testcase PASS evidence
- declare any Batch 3 testcase PASS
- resolve blocker tasks without separate atomic task files and evidence

## Remaining Follow-Up Task IDs

- PRODUCT-A-APPLY-FEE-INVALID-CONTRACT-01
- BE-A-APPLY-FEE-ITEM-VALIDATION-01
- PRODUCT-A-GOV-PAYLIST-UNHAPPY-CONTRACT-01
- BE-A-PAYMENT-OFFSET-UNHAPPY-01
- BE-A-APPLY-BILL-UNHAPPY-01
- BE-A-COMMISSION-WAITPAY-THRESHOLD-READINESS-01
- A-AUTO-PY-A-BATCH-FILING-VALIDATION-P0-01
- A-AUTO-PY-A-APPLY-FEE-INVALID-P1-01
- A-AUTO-PY-A-GOV-PAYLIST-VALIDATION-P1-01
- A-AUTO-PY-A-BILL-INVALID-COMBOS-P1-01
- A-AUTO-PY-A-PAYMENT-OFFSET-VALIDATION-P1-01
- A-AUTO-PY-A-COMMISSION-WAITPAY-P1-01

## Allowed Files

- tasks/batches/BATCH-A-DEPENDENT-UNHAPPY-P0P1-01-READINESS-GATE.md
- docs/automation/readiness/BATCH-A-DEPENDENT-UNHAPPY-P0P1-01-READINESS-GATE.md
- tasks/batches/BATCH-A-DEPENDENT-UNHAPPY-P0P1-01-BLOCKER-DRAIN.md
- tasks/batches/BATCH-A-DEPENDENT-UNHAPPY-P0P1-01.md
- artifacts/BATCH-A-DEPENDENT-UNHAPPY-P0P1-01-READINESS-GATE/**

## Verification Commands

```bash
./scripts/evidence_run.sh BATCH-A-DEPENDENT-UNHAPPY-P0P1-01-READINESS-GATE discovery /bin/zsh -lc 'rg -n "TC-A-012|TC-A-016|TC-A-018|TC-A-020|TC-A-022|TC-A-024" FPMS_Automation_Skeleton_Pack/data'
./scripts/evidence_run.sh BATCH-A-DEPENDENT-UNHAPPY-P0P1-01-READINESS-GATE backend_scan /bin/zsh -lc 'rg -n "batch-filing|FeeItem|pay-lists|gov-payments|bills/from-drafts|payments|offsets|commission|WaitPay|ForceSettle" backend/app backend/tests frontend/src'
./scripts/evidence_run.sh BATCH-A-DEPENDENT-UNHAPPY-P0P1-01-READINESS-GATE stale_test_scan /bin/zsh -lc 'rg -n "_is_skeleton|handle_tc_a_012|handle_tc_a_016|handle_tc_a_018|handle_tc_a_020|handle_tc_a_022|handle_tc_a_024" FPMS_Automation_Skeleton_Pack/pytest_python/tests'
./scripts/evidence_run.sh BATCH-A-DEPENDENT-UNHAPPY-P0P1-01-READINESS-GATE lint /bin/zsh -lc 'test -f tasks/batches/BATCH-A-DEPENDENT-UNHAPPY-P0P1-01-READINESS-GATE.md && test -f docs/automation/readiness/BATCH-A-DEPENDENT-UNHAPPY-P0P1-01-READINESS-GATE.md && test -f tasks/batches/BATCH-A-DEPENDENT-UNHAPPY-P0P1-01-BLOCKER-DRAIN.md && test -f tasks/batches/BATCH-A-DEPENDENT-UNHAPPY-P0P1-01.md'
./scripts/evidence_run.sh BATCH-A-DEPENDENT-UNHAPPY-P0P1-01-READINESS-GATE test /bin/zsh -lc 'rg -n "Capability Matrix|Blocker Drain Manifest|Automation Landing|TC-A-012|TC-A-016|TC-A-018|TC-A-020|TC-A-022|TC-A-024" docs/automation/readiness/BATCH-A-DEPENDENT-UNHAPPY-P0P1-01-READINESS-GATE.md'
./scripts/evidence_run.sh BATCH-A-DEPENDENT-UNHAPPY-P0P1-01-READINESS-GATE task_gate ./scripts/task_validate.sh BATCH-A-DEPENDENT-UNHAPPY-P0P1-01-READINESS-GATE
```

## Evidence Path

- artifacts/BATCH-A-DEPENDENT-UNHAPPY-P0P1-01-READINESS-GATE/results.jsonl
- artifacts/BATCH-A-DEPENDENT-UNHAPPY-P0P1-01-READINESS-GATE/summary.md
- artifacts/BATCH-A-DEPENDENT-UNHAPPY-P0P1-01-READINESS-GATE/git/diff.patch
