# GF-BILL-VIS-QA-01

- chosen_runbook: `P0-frontend-heavy-story`
- exact closure slice: validate `GF-BILL-VIS-BE-01` and `GF-BILL-VIS-FE-01` evidence, scope, and task gates
- explicit non-closure: no product-code changes
- allowlist:
  - `artifacts/GF-BILL-VIS-BE-01`
  - `artifacts/GF-BILL-VIS-FE-01`
  - `artifacts/GF-BILL-VIS-QA-01`
- verification:
  - `./scripts/task_validate.sh GF-BILL-VIS-BE-01`
  - `./scripts/task_validate.sh GF-BILL-VIS-FE-01`
  - `./scripts/task_validate.sh GF-BILL-VIS-QA-01`
- evidence path: `artifacts/GF-BILL-VIS-QA-01`
- remaining follow-up task ids: `None`
