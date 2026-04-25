# BATCH-A-P1-COMPLETION-01-CLOSE-AUDIT

Task ID: `BATCH-A-P1-COMPLETION-01-CLOSE-AUDIT`

Story Shape Classification:
- shared_file_density: high
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: high

chosen_runbook: `P0-prereq-heavy-story`

## Exact Closure Slice

Close-audit Batch 4 P1 completion scope for `TC-A-002`, `TC-A-007`, `TC-A-009`, and `TC-A-014` by mapping each testcase to product/backend/automation evidence and recording residual deferred product decisions.

## Explicit Non-Closure

Do not implement new backend rules, frontend UI, pytest handlers, skeleton data changes, or Playwright changes in this audit task.

## Remaining Follow-Up Task IDs

- `PRODUCT-A-GENERAL-POWER-CONTRACT-01`
- `PRODUCT-A-STRICT-COUNTRY-INVENTOR-CONTRACT-01`
- `PRODUCT-A-CLIENT-ADDRESS-ACTIVE-CONTRACT-01`
- `PRODUCT-A-CASE-SPEC-FEE-REDUCTION-RATIO-CONTRACT-01`
- `PRODUCT-A-APPLICANT-FEE-POLICY-CONTRACT-01`

## Allowed Files

- `tasks/batches/BATCH-A-P1-COMPLETION-01-CLOSE-AUDIT.md`
- `docs/automation/close_audit/BATCH-A-P1-COMPLETION-01-CLOSE-AUDIT.md`
- `artifacts/BATCH-A-P1-COMPLETION-01-CLOSE-AUDIT/**`

## Verification Commands

- `test -f tasks/batches/BATCH-A-P1-COMPLETION-01-CLOSE-AUDIT.md`
- `test -f docs/automation/close_audit/BATCH-A-P1-COMPLETION-01-CLOSE-AUDIT.md`
- `rg -n "TC-A-002|TC-A-007|TC-A-009|TC-A-014|covered|deferred" docs/automation/close_audit/BATCH-A-P1-COMPLETION-01-CLOSE-AUDIT.md`
- `./scripts/task_validate.sh BATCH-A-P1-COMPLETION-01-CLOSE-AUDIT`

## Evidence Path

- `artifacts/BATCH-A-P1-COMPLETION-01-CLOSE-AUDIT/results.jsonl`
- `artifacts/BATCH-A-P1-COMPLETION-01-CLOSE-AUDIT/summary.md`
- `artifacts/BATCH-A-P1-COMPLETION-01-CLOSE-AUDIT/git/diff.patch`
