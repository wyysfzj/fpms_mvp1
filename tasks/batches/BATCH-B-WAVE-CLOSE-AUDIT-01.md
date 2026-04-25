# BATCH-B-WAVE-CLOSE-AUDIT-01

## Story Shape Classification

- shared_file_density: medium
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: high
- chosen_runbook: P0-prereq-heavy-story

## Exact Closure Slice

Audit B wave closure after `BATCH-B-AUTOMATION-LANDING-02`: map every B-wave testcase to product/backend/automation evidence, run final targeted B-wave verification, and state GO / NO-GO for the next wave.

## Explicit Non-Closure

Do not implement new product behavior. Do not modify backend, frontend, handlers, skeleton data, or Playwright. Evidence-only and close-audit docs are in scope.

## Allowed Files

- `tasks/batches/BATCH-B-WAVE-CLOSE-AUDIT-01.md`
- `docs/automation/close_audit/BATCH-B-WAVE-CLOSE-AUDIT-01.md`
- `artifacts/BATCH-B-WAVE-CLOSE-AUDIT-01/**`

## Verification Commands

- `test -f docs/automation/close_audit/BATCH-B-WAVE-CLOSE-AUDIT-01.md`
- `rg -n "TC-B-001|TC-B-002|TC-B-003|TC-B-004|TC-B-005|TC-B-006|TC-B-007|TC-B-008|TC-B-009|TC-B-010|TC-B-011|TC-B-012|TC-B-013" docs/automation/close_audit/BATCH-B-WAVE-CLOSE-AUDIT-01.md`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_wave_b.py -q`
- `./scripts/task_validate.sh BATCH-B-WAVE-CLOSE-AUDIT-01`

## Evidence Path

- `artifacts/BATCH-B-WAVE-CLOSE-AUDIT-01/results.jsonl`
- `artifacts/BATCH-B-WAVE-CLOSE-AUDIT-01/summary.md`
- `artifacts/BATCH-B-WAVE-CLOSE-AUDIT-01/git/diff.patch`

## Remaining Follow-Up Task IDs

None
