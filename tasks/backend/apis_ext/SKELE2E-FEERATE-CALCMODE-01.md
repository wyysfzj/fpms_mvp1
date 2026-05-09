# SKELE2E-FEERATE-CALCMODE-01 — Fee rate calc_mode metadata API acceptance

Task ID: `SKELE2E-FEERATE-CALCMODE-01`

## Exact Closure Slice

Update the backend FeeRate API schema so `POST /api/v1/fees/rates` and `PUT /api/v1/fees/rates/{rate_id}` accept and persist the Skeleton Pack metadata-only calc modes `BY_YEAR`, `BY_PAGES`, and `COMPOSITE`.

This task closes only:

1. Fee rate create accepts `calc_mode` values `BY_YEAR`, `BY_PAGES`, and `COMPOSITE`.
2. Fee rate update accepts the same metadata values.
3. Fee rate list/detail responses preserve the submitted `calc_mode` string and existing `calc_params`.
4. Existing supported modes `FIXED`, `PER_CLAIM`, `PER_PAGE`, and `TIER` remain accepted.

## Explicit Non-Closure

Do not implement fee calculation logic for `BY_YEAR`, `BY_PAGES`, or `COMPOSITE`.
Do not modify fee draft generation, billing, commission, readiness, frontend, database schema, migrations, seed data, or the FPMS Automation Skeleton Pack.
Do not change endpoint paths, response envelopes, permissions, or status-code semantics.

## Remaining Follow-Up Task IDs

- `SKELE2E-READINESS-CONTRACT-01`
- `SKELE2E-CASEPRIORITY-CONTRACT-01`
- `SKELE2E-BATCH-GATE-DATA-01`
- `SKELE2E-GRANTED-DATA-01`
- `SKELE2E-PAYLIST-CONTRACT-01`
- `SKELE2E-FE-STATIC-PAGEERROR-01`
- `SKELE2E-BROWSERUSE-RUNTIME-01`

## Story Shape Classification

| Field | Value |
|---|---|
| shared_file_density | Low. The task touches one enum file and one focused backend test file. |
| prereq_dependency_density | Medium. It removes the W0 fee-rate schema blocker before remaining backend E2E blockers can be isolated. |
| be_fe_coupling | Low. This is backend API acceptance behavior with no frontend surface change. |
| evidence_cost | Medium. Requires RED/GREEN backend tests, task-scoped lint, task gate, and later backend wave rerun evidence. |

chosen_runbook: `P0-prereq-heavy-story`

## Allowed Files

- `tasks/backend/apis_ext/SKELE2E-FEERATE-CALCMODE-01.md`
- `backend/app/modules/fees/enums.py`
- `backend/tests/test_b4_fee_rate_dims.py`
- `artifacts/SKELE2E-FEERATE-CALCMODE-01/**`

## Verification Commands

- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py check-task tasks/backend/apis_ext/SKELE2E-FEERATE-CALCMODE-01.md`
- `cd backend && python3 -m pytest -q tests/test_b4_fee_rate_dims.py`
- `cd backend && python3 -m ruff check --fix app/modules/fees/enums.py tests/test_b4_fee_rate_dims.py`
- `cd backend && python3 -m ruff format app/modules/fees/enums.py tests/test_b4_fee_rate_dims.py`
- `cd backend && python3 -m ruff check app/modules/fees/enums.py tests/test_b4_fee_rate_dims.py`
- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate SKELE2E-FEERATE-CALCMODE-01`
- `./scripts/task_validate.sh SKELE2E-FEERATE-CALCMODE-01`

## Evidence Path

- `artifacts/SKELE2E-FEERATE-CALCMODE-01/`

## Done Definition

- Focused backend tests prove create/list/update preserve `BY_YEAR`, `BY_PAGES`, and `COMPOSITE`.
- Focused backend tests prove unsupported calculation behavior remains the documented default-amount fallback.
- Task-scoped Ruff and pytest pass.
- Required evidence files exist and task gates pass.
