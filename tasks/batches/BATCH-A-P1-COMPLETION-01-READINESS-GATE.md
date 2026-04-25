# BATCH-A-P1-COMPLETION-01-READINESS-GATE

Task ID: `BATCH-A-P1-COMPLETION-01-READINESS-GATE`

Role: lead / worker coordinator

Story Shape Classification:
- shared_file_density: high
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: high

chosen_runbook: `P0-prereq-heavy-story`

## Exact Closure Slice

Build the Batch 4 readiness gate for A-wave P1 completion scope:

- `TC-A-002` / `A-AUTO-PY-A-MINIMAL-REQUIRED-P1-01`
- `TC-A-007` / `A-AUTO-PY-A-FOREIGN-COMBO-P1-01`
- `TC-A-009` / `A-AUTO-PY-A-SPEC-FEE-DISCOUNT-P1-01`
- `TC-A-014` / `A-AUTO-PY-A-TASK_REASSIGN-P1-01`

This task closes only:

1. Confirm testcase semantics from skeleton data.
2. Build backend capability and blocker matrix.
3. Build stale-test and allowlist matrix.
4. Build blocker drain manifest.
5. Build serialized automation landing manifest.
6. Decide which automation tasks can start now and which must wait.

## Explicit Non-Closure

This readiness gate does not implement backend rules, frontend UI, pytest handlers, skeleton data, schema, manifests, or Playwright assets. It does not remove `@skeleton_case`, does not claim any testcase PASS, and does not fake partial backend behavior as testcase closure.

## Remaining Follow-Up Task IDs

- `PRODUCT-A-CASE-A2-FULL-FIELDS-CONTRACT-01`
- `BE-A-CASE-A2-FULL-FIELDS-READINESS-01`
- `PRODUCT-A-CASE-A7-INVENTOR-ADDRESS-CONTRACT-01`
- `BE-A-CASE-A7-INVENTOR-ADDRESS-RULE-01`
- `PRODUCT-A-CASE-SPEC-FEE-DISCOUNT-CONTRACT-01`
- `BE-A-CASE-SPEC-FEE-DISCOUNT-RULE-01`
- `BE-A-APPLY-FEE-LIMIT-BASE-SOURCE-01`
- `A-AUTO-PY-A-MINIMAL-REQUIRED-P1-01`
- `A-AUTO-PY-A-FOREIGN-COMBO-P1-01`
- `A-AUTO-PY-A-SPEC-FEE-DISCOUNT-P1-01`
- `A-AUTO-PY-A-TASK_REASSIGN-P1-01`

## Allowed Files

- `tasks/batches/BATCH-A-P1-COMPLETION-01-READINESS-GATE.md`
- `tasks/batches/BATCH-A-P1-COMPLETION-01-BLOCKER-DRAIN.md`
- `tasks/batches/BATCH-A-P1-COMPLETION-01.md`
- `docs/automation/readiness/BATCH-A-P1-COMPLETION-01-READINESS-GATE.md`
- `artifacts/BATCH-A-P1-COMPLETION-01-READINESS-GATE/**`

## Verification Commands

```bash
./scripts/evidence_run.sh BATCH-A-P1-COMPLETION-01-READINESS-GATE lint /bin/zsh -lc 'test -f tasks/batches/BATCH-A-P1-COMPLETION-01-READINESS-GATE.md && test -f docs/automation/readiness/BATCH-A-P1-COMPLETION-01-READINESS-GATE.md && test -f tasks/batches/BATCH-A-P1-COMPLETION-01-BLOCKER-DRAIN.md && test -f tasks/batches/BATCH-A-P1-COMPLETION-01.md'
./scripts/evidence_run.sh BATCH-A-P1-COMPLETION-01-READINESS-GATE test /bin/zsh -lc 'rg -n "TC-A-002|TC-A-007|TC-A-009|TC-A-014|Blocker Drain Manifest|Automation Landing Readiness|product_decision_required" docs/automation/readiness/BATCH-A-P1-COMPLETION-01-READINESS-GATE.md tasks/batches/BATCH-A-P1-COMPLETION-01-BLOCKER-DRAIN.md tasks/batches/BATCH-A-P1-COMPLETION-01.md'
./scripts/evidence_run.sh BATCH-A-P1-COMPLETION-01-READINESS-GATE task_gate ./scripts/task_validate.sh BATCH-A-P1-COMPLETION-01-READINESS-GATE
```

## Evidence Path

- `artifacts/BATCH-A-P1-COMPLETION-01-READINESS-GATE/results.jsonl`
- `artifacts/BATCH-A-P1-COMPLETION-01-READINESS-GATE/summary.md`
- `artifacts/BATCH-A-P1-COMPLETION-01-READINESS-GATE/git/diff.patch`
