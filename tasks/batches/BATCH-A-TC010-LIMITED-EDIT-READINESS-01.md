# BATCH-A-TC010-LIMITED-EDIT-READINESS-01

## Story Shape Classification

- shared_file_density: high
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: medium
- chosen_runbook: P0-prereq-heavy-story

## Exact Closure Slice

This readiness task closes only the TC-A-010 limited-edit blocker discovery needed after `BATCH-A-WAVE-CLOSE-AUDIT-01` found `handle_tc_a_010` still skeleton.

It confirms:

- TC-A-010 is P0 smoke.
- Current backend/frontend limited-edit capability.
- Product/backend gaps before automation landing.
- Required follow-up atomic tasks and allowlists.

## Explicit Non-Closure

This readiness task does not implement backend behavior, frontend behavior, pytest handlers, or remove `@skeleton_case`.

## Remaining Follow-Up Task IDs

- PRODUCT-A-CASE-LIMITED-EDIT-CONTRACT-01
- BE-A-CASE-LIMITED-EDIT-RULE-01
- A-AUTO-PY-A-LIMITED-EDIT-P0-01
- BATCH-A-WAVE-CLOSE-AUDIT-01

## Allowed Files

- tasks/batches/BATCH-A-TC010-LIMITED-EDIT-READINESS-01.md
- docs/automation/readiness/BATCH-A-TC010-LIMITED-EDIT-READINESS-01.md
- artifacts/BATCH-A-TC010-LIMITED-EDIT-READINESS-01/**

## Verification Commands

```bash
./scripts/evidence_run.sh BATCH-A-TC010-LIMITED-EDIT-READINESS-01 lint /bin/zsh -lc 'test -f tasks/batches/BATCH-A-TC010-LIMITED-EDIT-READINESS-01.md && test -f docs/automation/readiness/BATCH-A-TC010-LIMITED-EDIT-READINESS-01.md'
./scripts/evidence_run.sh BATCH-A-TC010-LIMITED-EDIT-READINESS-01 test /bin/zsh -lc 'rg -n "TC-A-010|Capability Matrix|Blocker Ledger|Automation Landing Readiness" docs/automation/readiness/BATCH-A-TC010-LIMITED-EDIT-READINESS-01.md'
./scripts/evidence_run.sh BATCH-A-TC010-LIMITED-EDIT-READINESS-01 task_gate ./scripts/task_validate.sh BATCH-A-TC010-LIMITED-EDIT-READINESS-01
```

## Evidence Path

- artifacts/BATCH-A-TC010-LIMITED-EDIT-READINESS-01/results.jsonl
- artifacts/BATCH-A-TC010-LIMITED-EDIT-READINESS-01/summary.md
- artifacts/BATCH-A-TC010-LIMITED-EDIT-READINESS-01/git/diff.patch
