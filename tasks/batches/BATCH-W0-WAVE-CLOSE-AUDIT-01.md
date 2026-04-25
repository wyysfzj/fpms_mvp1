# BATCH-W0-WAVE-CLOSE-AUDIT-01

Task ID: `BATCH-W0-WAVE-CLOSE-AUDIT-01`

Story Shape Classification:
- shared_file_density: high
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: high

chosen_runbook: `P0-prereq-heavy-story`

## Exact Closure Slice

Audit the W0 P0 prerequisite slice by mapping `TC-W0-001`, `TC-W0-007`, `TC-W0-010`, and `TC-W0-014` to existing task evidence, running targeted W0 P0 real smoke, preserving the remaining W0 skeleton backlog as explicit non-closure, and issuing a next-wave readiness decision.

## Explicit Non-Closure

Do not implement or claim closure for `TC-W0-002`, `TC-W0-003`, `TC-W0-004`, `TC-W0-005`, `TC-W0-006`, `TC-W0-008`, `TC-W0-009`, `TC-W0-011`, `TC-W0-012`, or `TC-W0-013`. Do not modify backend, frontend, pytest handlers, skeleton data, or Playwright.

## Remaining Follow-Up Task IDs

- `BATCH-W0-P1P2-COMPLETION-READINESS-GATE-01`
- `BATCH-B-READINESS-GATE-01`

## Allowed Files

- `tasks/batches/BATCH-W0-WAVE-CLOSE-AUDIT-01.md`
- `docs/automation/close_audit/BATCH-W0-WAVE-CLOSE-AUDIT-01.md`
- `artifacts/BATCH-W0-WAVE-CLOSE-AUDIT-01/**`

## Verification Commands

- `test -f tasks/batches/BATCH-W0-WAVE-CLOSE-AUDIT-01.md`
- `test -f docs/automation/close_audit/BATCH-W0-WAVE-CLOSE-AUDIT-01.md`
- `rg -n "TC-W0-001|TC-W0-007|TC-W0-010|TC-W0-014|GO for W0 P0 prerequisite|NO-GO for full W0" docs/automation/close_audit/BATCH-W0-WAVE-CLOSE-AUDIT-01.md`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && FPMS_API_URL=http://127.0.0.1:8000/api/v1 FPMS_RUN_ID=LOCAL-RUN-W0-CLOSE-20260418-02 FPMS_DB_DSN= pytest tests/test_wave_w0.py -k 'TC-W0-001 or TC-W0-007 or TC-W0-010 or TC-W0-014' -q`
- `./scripts/task_validate.sh BATCH-W0-WAVE-CLOSE-AUDIT-01`

## Evidence Path

- `artifacts/BATCH-W0-WAVE-CLOSE-AUDIT-01/results.jsonl`
- `artifacts/BATCH-W0-WAVE-CLOSE-AUDIT-01/summary.md`
- `artifacts/BATCH-W0-WAVE-CLOSE-AUDIT-01/git/diff.patch`
