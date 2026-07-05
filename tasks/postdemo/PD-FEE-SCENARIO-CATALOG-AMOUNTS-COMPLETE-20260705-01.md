# PD-FEE-SCENARIO-CATALOG-AMOUNTS-COMPLETE-20260705-01

Story Shape Classification
- shared_file_density: low
- prereq_dependency_density: medium
- be_fe_coupling: low
- evidence_cost: medium
- chosen_runbook: P0-single-lane-story

## Exact Closure Slice
- Complete the official-fee catalog seed for the user-confirmed parameter rows that were still underrepresented:
  - patent term compensation request fee: `200`
  - compensation-period annuity fee: `8000`
  - Hague/design international registration China designation fee first, second, and third installments: `4100`, `7600`, `15000`
  - IC layout design fee rows from the copied standard.
- Encode Hague first/second installments as reducible and third installment as not reducible.
- Keep all rows as `GOV` official-fee parameters with source metadata, category/subtype metadata, and disabled/pending status unless already safely executable.

## Explicit Non-Closure
- No fee calculation behavior changes.
- No automatic PCT/Hague/IC/compensation fee generation.
- No new database schema.
- No API or UI behavior changes.
- No official payment, CPC/OA, RPA, automatic signing, or automatic payment.

## Remaining Follow-Up Task IDs
- `PD-FEE-SCENARIO-PCT-HAGUE-TRIGGER-RULES-20260705-01`
- `PD-FEE-SCENARIO-IC-LAYOUT-TRIGGER-RULES-20260705-01`

## Allowed Files
- tasks/postdemo/PD-FEE-SCENARIO-CATALOG-AMOUNTS-COMPLETE-20260705-01.md
- backend/scripts/seed_dev.py
- backend/tests/test_official_fee_rate_catalog_seed.py
- artifacts/PD-FEE-SCENARIO-CATALOG-AMOUNTS-COMPLETE-20260705-01/**

## Verification Commands
- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py check-task tasks/postdemo/PD-FEE-SCENARIO-CATALOG-AMOUNTS-COMPLETE-20260705-01.md`
- `cd backend && PYTHONPATH=. pytest tests/test_official_fee_rate_catalog_seed.py -q`
- `ruff check --fix backend/scripts/seed_dev.py backend/tests/test_official_fee_rate_catalog_seed.py`
- `ruff format backend/scripts/seed_dev.py backend/tests/test_official_fee_rate_catalog_seed.py`
- `ruff check backend/scripts/seed_dev.py backend/tests/test_official_fee_rate_catalog_seed.py`
- `./scripts/task_validate.sh PD-FEE-SCENARIO-CATALOG-AMOUNTS-COMPLETE-20260705-01`

## Evidence Path
- artifacts/PD-FEE-SCENARIO-CATALOG-AMOUNTS-COMPLETE-20260705-01/**

## Done Definition
- Targeted seed test proves compensation request and compensation-period annuity amounts are present.
- Targeted seed test proves Hague first/second/third installment rows are present and only the third is not reducible.
- Targeted seed test proves IC layout rows from the copied standard are present under `fee_domain=IC_LAYOUT`.
- Task gate and evidence artifacts pass.
