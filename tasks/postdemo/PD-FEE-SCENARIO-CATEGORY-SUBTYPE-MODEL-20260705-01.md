# PD-FEE-SCENARIO-CATEGORY-SUBTYPE-MODEL-20260705-01

Story Shape Classification
- shared_file_density: medium
- prereq_dependency_density: medium
- be_fe_coupling: medium
- evidence_cost: medium
- chosen_runbook: P0-prereq-heavy-story

## Exact Closure Slice
- Enhance `FeeRate` official-fee parameter metadata so the user-confirmed document fields can be represented and queried:
  - `fee_domain`
  - `fee_section`
  - `fee_category` (`收费项目`)
  - `fee_subtype` (`细分类型`)
  - `reduction_scope`
- `FeeRate` create, update, list, and output schemas must accept and return these fields.
- Official-fee catalog seed rows must populate at least domestic application, reexamination, PCT, Hague/designation, and IC layout sample categories/subtypes where present in the approved design appendix.

## Explicit Non-Closure
- No fee calculation behavior changes.
- No new trigger-rule table.
- No deadline-rule table.
- No PCT/Hague/IC layout automatic fee generation.
- No official payment Excel, CPC/OA integration, RPA, automatic signing, or automatic payment implementation.
- No frontend UI rendering beyond type contract metadata if needed.

## Remaining Follow-Up Task IDs
- `PD-FEE-SCENARIO-DEADLINE-RULES-20260705-01`
- `PD-FEE-SCENARIO-PCT-HAGUE-TRIGGER-RULES-20260705-01`

## Allowed Files
- tasks/postdemo/PD-FEE-SCENARIO-CATEGORY-SUBTYPE-MODEL-20260705-01.md
- backend/app/modules/fees/models.py
- backend/app/modules/fees/schemas.py
- backend/app/modules/fees/service.py
- backend/app/modules/fees/api.py
- backend/alembic/versions/pd_fee_scenario_rate_metadata_01.py
- backend/scripts/seed_dev.py
- backend/tests/test_b4_fee_rate_dims.py
- backend/tests/test_official_fee_rate_catalog_seed.py
- frontend/src/api/fees.types.ts
- artifacts/PD-FEE-SCENARIO-CATEGORY-SUBTYPE-MODEL-20260705-01/**

## Verification Commands
- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py check-task tasks/postdemo/PD-FEE-SCENARIO-CATEGORY-SUBTYPE-MODEL-20260705-01.md`
- `cd backend && PYTHONPATH=. pytest tests/test_b4_fee_rate_dims.py tests/test_official_fee_rate_catalog_seed.py -q`
- `cd frontend && npm run typecheck`
- `ruff check --fix backend/app/modules/fees/models.py backend/app/modules/fees/schemas.py backend/app/modules/fees/service.py backend/app/modules/fees/api.py backend/alembic/versions/pd_fee_scenario_rate_metadata_01.py backend/scripts/seed_dev.py backend/tests/test_b4_fee_rate_dims.py backend/tests/test_official_fee_rate_catalog_seed.py`
- `ruff format backend/app/modules/fees/models.py backend/app/modules/fees/schemas.py backend/app/modules/fees/service.py backend/app/modules/fees/api.py backend/alembic/versions/pd_fee_scenario_rate_metadata_01.py backend/scripts/seed_dev.py backend/tests/test_b4_fee_rate_dims.py backend/tests/test_official_fee_rate_catalog_seed.py`
- `ruff check backend/app/modules/fees/models.py backend/app/modules/fees/schemas.py backend/app/modules/fees/service.py backend/app/modules/fees/api.py backend/alembic/versions/pd_fee_scenario_rate_metadata_01.py backend/scripts/seed_dev.py backend/tests/test_b4_fee_rate_dims.py backend/tests/test_official_fee_rate_catalog_seed.py`
- `./scripts/task_validate.sh PD-FEE-SCENARIO-CATEGORY-SUBTYPE-MODEL-20260705-01`

## Evidence Path
- artifacts/PD-FEE-SCENARIO-CATEGORY-SUBTYPE-MODEL-20260705-01/**

## Done Definition
- Targeted tests prove `FeeRate` create/update/list/output carries `fee_domain`, `fee_section`, `fee_category`, `fee_subtype`, and `reduction_scope`.
- Targeted tests prove `FeeRate` list filters can filter at least by `fee_domain` and `fee_category`.
- Official-fee seed tests prove representative catalog rows carry user-confirmed categories/subtypes.
- Task gate and evidence artifacts pass.
