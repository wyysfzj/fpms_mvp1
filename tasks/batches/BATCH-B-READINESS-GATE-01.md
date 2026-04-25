# BATCH-B-READINESS-GATE-01

Task ID: `BATCH-B-READINESS-GATE-01`

Story Shape Classification:
- shared_file_density: high
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: high

chosen_runbook: `P0-prereq-heavy-story`

## Exact Closure Slice

Discover B-wave backend/product/test-maintenance/seed/state/env blockers before automation landing, build the B-wave capability matrices, and author the blocker drain manifest.

## Explicit Non-Closure

Do not implement B handlers, remove `@skeleton_case`, modify `wave_b.py`, modify backend/frontend code, modify skeleton YAML/JSON/schema data, or claim any B testcase PASS.

## Remaining Follow-Up Task IDs

- `BATCH-B-BLOCKER-DRAIN-01`
- `BATCH-B-AUTOMATION-LANDING-01`
- `BATCH-B-CLOSE-AUDIT-01`

## Allowed Files

- `tasks/batches/BATCH-B-READINESS-GATE-01.md`
- `docs/automation/readiness/BATCH-B-READINESS-GATE-01.md`
- `tasks/batches/BATCH-B-BLOCKER-DRAIN-01.md`
- `artifacts/BATCH-B-READINESS-GATE-01/**`

## Verification Commands

- `test -f tasks/batches/BATCH-B-READINESS-GATE-01.md`
- `test -f docs/automation/readiness/BATCH-B-READINESS-GATE-01.md`
- `test -f tasks/batches/BATCH-B-BLOCKER-DRAIN-01.md`
- `rg -n "TC-B-001|TC-B-003|TC-B-004|TC-B-006|TC-B-007|TC-B-008|TC-B-011|BE-B-DOCUMENT-TEST-MAINT-01|PRODUCT-B-OA-WIZARD-CONTRACT-01|BLOCKED" docs/automation/readiness/BATCH-B-READINESS-GATE-01.md tasks/batches/BATCH-B-BLOCKER-DRAIN-01.md`
- `./scripts/task_validate.sh BATCH-B-READINESS-GATE-01`

## Evidence Path

- `artifacts/BATCH-B-READINESS-GATE-01/results.jsonl`
- `artifacts/BATCH-B-READINESS-GATE-01/summary.md`
- `artifacts/BATCH-B-READINESS-GATE-01/git/diff.patch`
