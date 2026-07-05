# PD-FEE-SCENARIO-RATE-CATALOG-SEED-20260705-01

## Story Shape Classification

- shared_file_density: low
- prereq_dependency_density: medium
- be_fe_coupling: low
- evidence_cost: medium
- chosen_runbook: P0-single-lane-story

## Exact Closure Slice

Add an idempotent development seed for the post-demo official-fee rate catalog:

- Seed customer DOCX / Tianyue URL official-fee entries into existing `FeeRate` rows.
- Store only `fee_type=GOV` rows in this catalog.
- Preserve source metadata with `source_doc`, `source_url`, `source_policy`, `source_version`, and `source_status`.
- Distinguish executable P1.5 domestic-mainline rates from complex or policy-sensitive rates by `enabled` and `source_status`.
- Keep the seed idempotent: rerunning it updates existing rows by `fee_code` and does not duplicate them.

## Explicit Non-Closure

- No API changes.
- No frontend changes.
- No database migration or new table.
- No fee calculation implementation.
- No application-fee, annuity, grant-fee, PayList, GovPayment, billing, receipt, commission, OA, PCT direct integration, or official payment Excel implementation.
- No claim that Tianyue URL is the authoritative legal source.

## Remaining Follow-Up Task IDs

- `PD-FEE-SCENARIO-GRANT-GOV-RATE-20260705-01`
- `PD-FEE-SCENARIO-OFFICIAL-FEE-PREVIEW-20260705-01`
- `PD-FEE-SCENARIO-FEE-NODE-UI-20260705-01`
- `PD-FEE-SCENARIO-E2E-VERIFY-20260705-01`

## Allowed Files

- `tasks/postdemo/PD-FEE-SCENARIO-RATE-CATALOG-SEED-20260705-01.md`
- `backend/scripts/seed_dev.py`
- `backend/tests/test_official_fee_rate_catalog_seed.py`
- `artifacts/PD-FEE-SCENARIO-RATE-CATALOG-SEED-20260705-01/**`

## Verification Commands

- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py check-task tasks/postdemo/PD-FEE-SCENARIO-RATE-CATALOG-SEED-20260705-01.md`
- `cd backend && PYTHONPATH=. pytest tests/test_official_fee_rate_catalog_seed.py -q`
- `ruff check --fix backend/scripts/seed_dev.py backend/tests/test_official_fee_rate_catalog_seed.py`
- `ruff format backend/scripts/seed_dev.py backend/tests/test_official_fee_rate_catalog_seed.py`
- `ruff check backend/scripts/seed_dev.py backend/tests/test_official_fee_rate_catalog_seed.py`
- `./scripts/task_validate.sh PD-FEE-SCENARIO-RATE-CATALOG-SEED-20260705-01`

## Evidence Path

- `artifacts/PD-FEE-SCENARIO-RATE-CATALOG-SEED-20260705-01/`

## Done Definition

- Targeted tests prove the seed creates a GOV-only official-fee catalog with source metadata, enabled confirmed domestic-mainline rows, pending/disabled complex rows, and idempotent reruns.
