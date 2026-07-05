# PD-FEE-SCENARIO-RATE-METADATA-20260705-01

## Story Shape Classification

- shared_file_density: medium
- prereq_dependency_density: low
- be_fe_coupling: low
- evidence_cost: medium
- chosen_runbook: P0-prereq-heavy-story

## Exact Closure Slice

Enhance `FeeRate` so official fee rate parameters can carry auditable source metadata required by the finalized post-demo fee design:

- Persist nullable metadata fields on `t_fee_rate`:
  - `source_doc`
  - `source_url`
  - `source_policy`
  - `source_version`
  - `source_status`
- `FeeRate` create, update, and output schemas must accept and return those fields.
- `GET /api/v1/fees/rates` list output must include those fields.
- The migration must be SQLite-compatible, idempotent, forward-only, and must not change existing fee calculation behavior.

## Explicit Non-Closure

- No application fee calculation changes.
- No official fee seed data import.
- No source document parser.
- No frontend changes.
- No annuity, grant-fee, OA, PCT, file-trigger fee preview, PayList, GovPayment, billing, receipt, or commission behavior changes.
- No non-official fee design or implementation.

## Remaining Follow-Up Task IDs

- `PD-FEE-SCENARIO-ANNUITY-GOV-RATE-20260705-01`
- `PD-FEE-SCENARIO-GRANT-GOV-RATE-20260705-01`
- `PD-FEE-SCENARIO-OFFICIAL-FEE-PREVIEW-20260705-01`
- `PD-FEE-SCENARIO-FEE-NODE-UI-20260705-01`
- `PD-FEE-SCENARIO-E2E-VERIFY-20260705-01`

## Allowed Files

- `tasks/postdemo/PD-FEE-SCENARIO-RATE-METADATA-20260705-01.md`
- `backend/app/modules/fees/models.py`
- `backend/app/modules/fees/schemas.py`
- `backend/app/modules/fees/service.py`
- `backend/app/modules/fees/api.py`
- `backend/alembic/versions/pd_fee_scenario_rate_metadata_01.py`
- `backend/tests/test_b4_fee_rate_dims.py`
- `artifacts/PD-FEE-SCENARIO-RATE-METADATA-20260705-01/**`

## Verification Commands

- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py check-task tasks/postdemo/PD-FEE-SCENARIO-RATE-METADATA-20260705-01.md`
- `cd backend && PYTHONPATH=. pytest tests/test_b4_fee_rate_dims.py -q`
- `ruff check --fix backend/app/modules/fees/models.py backend/app/modules/fees/schemas.py backend/app/modules/fees/service.py backend/app/modules/fees/api.py backend/alembic/versions/pd_fee_scenario_rate_metadata_01.py backend/tests/test_b4_fee_rate_dims.py`
- `ruff format backend/app/modules/fees/models.py backend/app/modules/fees/schemas.py backend/app/modules/fees/service.py backend/app/modules/fees/api.py backend/alembic/versions/pd_fee_scenario_rate_metadata_01.py backend/tests/test_b4_fee_rate_dims.py`
- `ruff check backend/app/modules/fees/models.py backend/app/modules/fees/schemas.py backend/app/modules/fees/service.py backend/app/modules/fees/api.py backend/alembic/versions/pd_fee_scenario_rate_metadata_01.py backend/tests/test_b4_fee_rate_dims.py`
- `./scripts/task_validate.sh PD-FEE-SCENARIO-RATE-METADATA-20260705-01`

## Evidence Path

- `artifacts/PD-FEE-SCENARIO-RATE-METADATA-20260705-01/`

## Done Definition

- Targeted tests prove source metadata can be created, updated, listed, and returned by `FeeRateOut`.
- Migration upgrades a fresh SQLite test DB.
- Task gate passes with required evidence.
