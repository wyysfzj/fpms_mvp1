# BATCH-A-HAPPY-MAIN-CHAIN-P0-01-READINESS-GATE

## Story Shape Classification

- shared_file_density: high
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: high
- chosen_runbook: P0-prereq-heavy-story

## Task

- Task ID: BATCH-A-HAPPY-MAIN-CHAIN-P0-01-READINESS-GATE
- Role: lead / worker coordinator
- Scope: Batch 2 Happy main chain P0 readiness gate and blocker drain preparation.

## Exact Closure Slice

This task closes only the readiness gate for Batch 2 Happy main chain P0:

1. Build a blocker ledger for TC-A-011, TC-A-013, TC-A-015, TC-A-017, TC-A-019, TC-A-021, and TC-A-023.
2. Build a capability matrix for backend endpoints, services, models, response stability, and frontend/API paths.
3. Build backend side-effect, test-maintenance, seed/config, allowlist, and state-machine reachability matrices.
4. Build an executable blocker drain manifest with one exact task file per blocker.
5. Record evidence and gate status for the readiness task.

## Explicit Non-Closure

This task does not:

- implement pytest automation handlers
- remove any `@skeleton_case`
- modify `FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_a.py`
- modify backend service/API/schema/model files
- modify frontend UI
- modify skeleton YAML / JSON / manifest / schema / Playwright assets
- run real smoke as testcase PASS evidence
- declare any Batch 2 testcase PASS
- resolve blocker tasks without separate atomic task files and evidence

## Remaining Follow-Up Task IDs

- BE-A-BATCH-FILING-TEST-MAINT-01
- BE-A-APPLY-FEE-LIMIT-TASK-FIELDS-01
- PRODUCT-A-APPLY-FEE-DRAFT-CONTRACT-01
- BE-A-APPLY-FEE-DRAFT-RULE-01
- BE-A-GOV-PAYLIST-PAYMENT-READINESS-01
- BE-A-APPLY-BILL-READINESS-01
- BE-A-PAYMENT-OFFSET-CASE-RECEIPT-READINESS-01
- BE-A-COMMISSION-RULE-SEED-READINESS-01
- A-AUTO-PY-A-BATCH-SUBMIT-P0-01
- A-AUTO-PY-A-APPLY-FEE-LIMIT-P0-01
- A-AUTO-PY-A-APPLY-FEE-DRAFT-P0-01
- A-AUTO-PY-A-GOV-PAYLIST-P0-01
- A-AUTO-PY-A-APPLY-BILL-P0-01
- A-AUTO-PY-A-PAYMENT-OFFSET-P0-01
- A-AUTO-PY-A-COMMISSION-P0-01

## Allowed Files

- tasks/batches/BATCH-A-HAPPY-MAIN-CHAIN-P0-01-READINESS-GATE.md
- docs/automation/readiness/BATCH-A-HAPPY-MAIN-CHAIN-P0-01-READINESS-GATE.md
- tasks/batches/BATCH-A-HAPPY-MAIN-CHAIN-P0-01-BLOCKER-DRAIN.md
- artifacts/BATCH-A-HAPPY-MAIN-CHAIN-P0-01-READINESS-GATE/**

## Verification Commands

```bash
./scripts/evidence_run.sh BATCH-A-HAPPY-MAIN-CHAIN-P0-01-READINESS-GATE discovery /bin/zsh -lc 'rg -n "TC-A-011|TC-A-013|TC-A-015|TC-A-017|TC-A-019|TC-A-021|TC-A-023" FPMS_Automation_Skeleton_Pack/data'
./scripts/evidence_run.sh BATCH-A-HAPPY-MAIN-CHAIN-P0-01-READINESS-GATE backend_scan /bin/zsh -lc 'rg -n "batch-filing|APPLY_FEE_LIMIT|FeeDraft|pay-lists|gov-payments|bills/from-drafts|payments|offsets|commission" backend/app backend/tests frontend/src'
./scripts/evidence_run.sh BATCH-A-HAPPY-MAIN-CHAIN-P0-01-READINESS-GATE stale_test_scan /bin/zsh -lc 'rg -n "CASE_APPLICANT_REQUIRED|applicants|batch-filing|selected_case_ids|generate_list|document_ids|created_task_ids|_is_skeleton" backend/tests FPMS_Automation_Skeleton_Pack/pytest_python/tests'
./scripts/evidence_run.sh BATCH-A-HAPPY-MAIN-CHAIN-P0-01-READINESS-GATE lint /bin/zsh -lc 'test -f tasks/batches/BATCH-A-HAPPY-MAIN-CHAIN-P0-01-READINESS-GATE.md && test -f docs/automation/readiness/BATCH-A-HAPPY-MAIN-CHAIN-P0-01-READINESS-GATE.md && test -f tasks/batches/BATCH-A-HAPPY-MAIN-CHAIN-P0-01-BLOCKER-DRAIN.md'
./scripts/evidence_run.sh BATCH-A-HAPPY-MAIN-CHAIN-P0-01-READINESS-GATE test /bin/zsh -lc 'rg -n "Blocker Drain Manifest|Capability Matrix|Test-Maintenance Matrix|Allowlist Matrix|State-Machine Reachability|TC-A-011|TC-A-013|TC-A-015|TC-A-017|TC-A-019|TC-A-021|TC-A-023" docs/automation/readiness/BATCH-A-HAPPY-MAIN-CHAIN-P0-01-READINESS-GATE.md'
./scripts/evidence_run.sh BATCH-A-HAPPY-MAIN-CHAIN-P0-01-READINESS-GATE task_gate ./scripts/task_validate.sh BATCH-A-HAPPY-MAIN-CHAIN-P0-01-READINESS-GATE
```

## Evidence Path

- artifacts/BATCH-A-HAPPY-MAIN-CHAIN-P0-01-READINESS-GATE/results.jsonl
- artifacts/BATCH-A-HAPPY-MAIN-CHAIN-P0-01-READINESS-GATE/summary.md
- artifacts/BATCH-A-HAPPY-MAIN-CHAIN-P0-01-READINESS-GATE/git/diff.patch
