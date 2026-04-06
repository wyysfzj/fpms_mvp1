# Fee Overview Upper-Pane Implementation Plan

- date: `2026-04-06`
- target slice: `FEOVERVIEW-UPPER-BE-01`

## Story Shape Classification

- `shared_file_density`: medium
- `prereq_dependency_density`: low
- `be_fe_coupling`: low
- `evidence_cost`: medium

## chosen_runbook

- `P0-single-lane-story`

## Batch Manifest

### `FEOVERVIEW-UPPER-BE-01`

- exact closure slice:
  - add the dedicated `SPEC 5.11` upper-pane backend endpoint for `GovPayment` overview rows
  - join `GovPayment` with `PayList`, `FeeItem`, `Case`
  - support first-round upper-pane filters:
    - `case_no`
    - `app_no`
    - `patent_no`
    - `client_id`
    - `applicant_name`
    - `paid_date_from`
    - `paid_date_to`
  - cover the contract with targeted backend tests
- explicit non-closure:
  - no lower pane
  - no frontend changes
  - no `/fee-unified-query` modifications
  - no fee-type filter semantics
  - no export/print
  - no schema/migration
- allowlist:
  - `backend/app/modules/billing/api.py`
  - `backend/app/modules/billing/service.py`
  - `backend/app/modules/billing/schemas.py`
  - `backend/tests/test_fee_overview_upper_api.py`
- verification:
  - `python3 -m ruff check backend/app/modules/billing/api.py backend/app/modules/billing/service.py backend/app/modules/billing/schemas.py backend/tests/test_fee_overview_upper_api.py`
  - `cd backend && pytest -q tests/test_fee_overview_upper_api.py`
  - `./scripts/task_validate.sh FEOVERVIEW-UPPER-BE-01`
- evidence path:
  - `artifacts/FEOVERVIEW-UPPER-BE-01/**`
- remaining follow-up task ids:
  - `FEOVERVIEW-LOWER-BE-01`
  - `FEOVERVIEW-FE-01`
  - `FEOVERVIEW-QA-01`

### `FEOVERVIEW-UPPER-QA-01`

- exact closure slice:
  - audit evidence, gates, and scope compliance for the upper-pane backend slice
- explicit non-closure:
  - no product-code changes
  - no close-decision update
- allowlist:
  - task/docs/artifacts only
- verification:
  - `./scripts/task_validate.sh FEOVERVIEW-UPPER-BE-01`
  - `./scripts/task_validate.sh FEOVERVIEW-UPPER-QA-01`
- evidence path:
  - `artifacts/FEOVERVIEW-UPPER-QA-01/**`
- remaining follow-up task ids:
  - `FEOVERVIEW-LOWER-BE-01`
  - `FEOVERVIEW-FE-01`
  - `FEOVERVIEW-QA-01`

## Serialized Shared-file Decisions

- `backend/app/modules/billing/api.py|service.py|schemas.py|backend/tests/test_fee_overview_upper_api.py` -> upper BE wave only
