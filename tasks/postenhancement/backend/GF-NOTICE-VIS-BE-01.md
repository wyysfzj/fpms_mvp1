# GF-NOTICE-VIS-BE-01

- chosen_runbook: `P0-frontend-heavy-story`
- exact closure slice: add `notify_count` to the grant-fee worklist projection
- explicit non-closure: no document/task generation, no state changes, no new linkage semantics
- allowlist:
  - `backend/app/modules/grant_fees/schemas.py`
  - `backend/app/modules/grant_fees/service.py`
  - `backend/tests/test_grant_fee_worklist_api.py`
- verification:
  - `python3 -m ruff format backend/app/modules/grant_fees/schemas.py backend/app/modules/grant_fees/service.py backend/tests/test_grant_fee_worklist_api.py`
  - `python3 -m ruff check backend/app/modules/grant_fees/api.py backend/app/modules/grant_fees/schemas.py backend/app/modules/grant_fees/service.py backend/tests/test_grant_fee_worklist_api.py`
  - `cd backend && pytest -q tests/test_grant_fee_worklist_api.py`
- evidence path: `artifacts/GF-NOTICE-VIS-BE-01`
- remaining follow-up task ids:
  - `GF-NOTICE-VIS-FE-01`
  - `GF-NOTICE-VIS-QA-01`

