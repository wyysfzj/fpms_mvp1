# Fee Overview Lower-Pane Implementation Plan

- date: `2026-04-06`
- target slice: `FEOVERVIEW-LOWER-BE-01`

## Story Shape Classification

- `shared_file_density`: medium
- `prereq_dependency_density`: low
- `be_fe_coupling`: low
- `evidence_cost`: medium

## chosen_runbook

- `P0-single-lane-story`

## Batch Manifest

### `FEOVERVIEW-LOWER-BE-01`

- exact closure slice:
  - add the dedicated `SPEC 5.11` lower-pane backend endpoint for paginated `CaseReceipt` overview rows
  - join `CaseReceipt` with `Case`
  - support first-round filters:
    - `case_no`
    - `app_no`
    - `patent_no`
    - `client_id`
    - `applicant_name`
    - `fee_type`
    - `receipt_date_from`
    - `receipt_date_to`
  - cover the contract with targeted backend tests
- explicit non-closure:
  - no upper pane changes
  - no frontend changes
  - no `/fee-unified-query` modifications
  - no export/print
  - no schema/migration
- allowlist:
  - `backend/app/modules/billing/api.py`
  - `backend/app/modules/billing/service.py`
  - `backend/app/modules/billing/schemas.py`
  - `backend/tests/test_fee_overview_lower_api.py`
- verification:
  - `python3 -m ruff check backend/app/modules/billing/api.py backend/app/modules/billing/service.py backend/app/modules/billing/schemas.py backend/tests/test_fee_overview_lower_api.py`
  - `cd backend && pytest -q tests/test_fee_overview_lower_api.py`
  - `./scripts/task_validate.sh FEOVERVIEW-LOWER-BE-01`
- evidence path:
  - `artifacts/FEOVERVIEW-LOWER-BE-01/**`
- remaining follow-up task ids:
  - `FEOVERVIEW-FE-01`
  - `FEOVERVIEW-QA-01`

### `FEOVERVIEW-LOWER-QA-01`

- exact closure slice:
  - audit evidence, gates, and scope compliance for the lower-pane backend slice
- explicit non-closure:
  - no product-code changes
  - no close-decision update
- allowlist:
  - task/docs/artifacts only
- verification:
  - `./scripts/task_validate.sh FEOVERVIEW-LOWER-BE-01`
  - `./scripts/task_validate.sh FEOVERVIEW-LOWER-QA-01`
- evidence path:
  - `artifacts/FEOVERVIEW-LOWER-QA-01/**`
- remaining follow-up task ids:
  - `FEOVERVIEW-FE-01`
  - `FEOVERVIEW-QA-01`

## Serialized Shared-file Decisions

- `backend/app/modules/billing/api.py|service.py|schemas.py|backend/tests/test_fee_overview_lower_api.py` -> lower BE wave only
