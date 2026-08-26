# FPMS-DEMO-V6-MIGRATION-HEAD-ALIGNMENT-20260826-00

Status: ACTIVE
Risk-Tier: HIGH
Closure-Tags: ["data", "migration"]
Task-Path: tasks/postdemo/FPMS-DEMO-V6-MIGRATION-HEAD-ALIGNMENT-20260826-00.md
Chosen runbook: `P0-prereq-heavy-story`

## Design References

- Approved implementation plan:
  `docs/superpowers/plans/2026-08-26-fpms-demo-v6-ui-parity-implementation.md`, exact commit
  `80bd46829eaf5f798dda9422550a583c7fa12fde`.
- Active task-scoped lean execution overlay:
  `docs/superpowers/plans/2026-08-26-fpms-demo-v6-ui-parity-lean-execution-overlay.md`.
- Governance binding repair prerequisite: exact commit `4ac0737`.

## Exact Closure Slice

Align the single `CURRENT_HEAD` expectation in
`backend/tests/test_v8_official_rate_book_schema.py` with the existing unique Alembic head
`demo_v6_gov_payment_operation_01`. The runtime migration graph is already authoritative and is not
changed.

## Fixed Scope Decision

- `shared_file_density=LOW`
- `prereq_dependency_density=HIGH`
- `be_fe_coupling=NONE`
- `evidence_cost=LOW`
- `chosen_runbook=P0-prereq-heavy-story`
- Scope expansion is denied; any migration-graph or runtime-schema defect stops this task.

## Explicit Non-Closure

- No migration, revision link, runtime schema, model, seed, API, UI, runner, or product behavior
  change.
- No adjacent test cleanup, formatting, renaming, or broad regression execution.
- Ordinal 01 and release/deployment work remain outside this task.

## Allowed Files

- `tasks/postdemo/FPMS-DEMO-V6-MIGRATION-HEAD-ALIGNMENT-20260826-00.md`
- `backend/tests/test_v8_official_rate_book_schema.py`
- `artifacts/FPMS-DEMO-V6-MIGRATION-HEAD-ALIGNMENT-20260826-00/**`

## Verification Commands

```bash
FPMS_PYTHON="${FPMS_PYTHON:-python3}"
(cd backend && "$FPMS_PYTHON" -m alembic heads)
(cd backend && "$FPMS_PYTHON" -m pytest -q tests/test_v8_official_rate_book_schema.py)
git diff --check
```

RED must show that the test expects `v8_w6_service_price_book_01` while the unique graph head is
`demo_v6_gov_payment_operation_01`. GREEN must show exactly that head and a passing focused test.
Independent review must prove a one-line test expectation change and zero migration/runtime diff.

Expected HTTP status codes: none; this is a test-only alignment task.

## Evidence Path

- `artifacts/FPMS-DEMO-V6-MIGRATION-HEAD-ALIGNMENT-20260826-00/**`

## Remaining Follow-Up Task IDs

- `FPMS-DEMO-V6-UI-PARITY-CONTRACT-20260826-01`, blocked until this task is independently accepted.

## Done Definition

The focused test reads the current unique migration head, all scoped verification and evidence
gates pass, an independent exact-commit review reports `P0/P1/P2 = 0/0/0`, and no non-closure item
or second ordinal is absorbed.

## Rollback

Run `git revert --no-edit <exact-task-sha>`. This restores only the historical test expectation and
task card; the migration graph remains unchanged.
