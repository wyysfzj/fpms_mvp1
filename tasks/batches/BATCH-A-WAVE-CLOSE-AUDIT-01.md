# BATCH-A-WAVE-CLOSE-AUDIT-01

Task ID: `BATCH-A-WAVE-CLOSE-AUDIT-01`

Story Shape Classification:
- shared_file_density: high
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: high

chosen_runbook: `P0-prereq-heavy-story`

## Exact Closure Slice

Audit A wave `TC-A-001` through `TC-A-024` by mapping testcase ids to existing product/backend/automation evidence, checking handler skeleton state, recording targeted verification, and issuing a go/no-go decision for entering the next wave.

## Explicit Non-Closure

Do not implement new backend rules, frontend UI, pytest handlers, skeleton data changes, Playwright changes, or testcase assertion changes in this audit task.

## Remaining Follow-Up Task IDs

- `BATCH-A-TC010-LIMITED-EDIT-READINESS-01`
- `A-AUTO-PY-A-LIMITED-EDIT-P0-01`

## Allowed Files

- `tasks/batches/BATCH-A-WAVE-CLOSE-AUDIT-01.md`
- `docs/automation/close_audit/BATCH-A-WAVE-CLOSE-AUDIT-01.md`
- `artifacts/BATCH-A-WAVE-CLOSE-AUDIT-01/**`

## Verification Commands

- `test -f tasks/batches/BATCH-A-WAVE-CLOSE-AUDIT-01.md`
- `test -f docs/automation/close_audit/BATCH-A-WAVE-CLOSE-AUDIT-01.md`
- `rg -n "TC-A-001|TC-A-010|NO-GO|A-AUTO-PY-A-LIMITED-EDIT-P0-01" docs/automation/close_audit/BATCH-A-WAVE-CLOSE-AUDIT-01.md`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && python3 - <<'PY' ...`
- `./scripts/task_validate.sh BATCH-A-WAVE-CLOSE-AUDIT-01`

## Evidence Path

- `artifacts/BATCH-A-WAVE-CLOSE-AUDIT-01/results.jsonl`
- `artifacts/BATCH-A-WAVE-CLOSE-AUDIT-01/summary.md`
- `artifacts/BATCH-A-WAVE-CLOSE-AUDIT-01/git/diff.patch`
