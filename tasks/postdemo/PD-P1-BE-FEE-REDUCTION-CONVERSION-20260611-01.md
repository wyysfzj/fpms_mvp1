# PD-P1-BE-FEE-REDUCTION-CONVERSION-20260611-01 — Fee reduction conversion contract

## Exact Closure Slice

Expose structured P1 fee-reduction conversion in fee linkage so customer old-system reduction ratios convert to system payable ratios: `0.85 -> 0.15`, `0.7 -> 0.3`, and no reduction -> `1.0`.

## Explicit Non-Closure

No frontend UI. No fee-rate seeding from unreadable screenshots. No official Excel export compatibility claim. No payment execution. No global reinterpretation of existing apply-fee payable-ratio contracts.

## Remaining Follow-Up Task IDs

- `PD-P1-FE-FEE-REDUCTION-CONVERSION-20260611-01`
- `PD-P1-E2E-ANSWER-DELTA-LIVE-20260611-01`

## Allowed Files

- `backend/app/modules/official_workflows/schemas.py`
- `backend/app/modules/official_workflows/service.py`
- `backend/tests/test_pd_p1_fee_linkage_api.py`
- `backend/tests/test_pd_p1_fee_reduction_conversion.py`
- `tasks/postdemo/PD-P1-BE-FEE-REDUCTION-CONVERSION-20260611-01.md`
- `artifacts/PD-P1-BE-FEE-REDUCTION-CONVERSION-20260611-01/**`

## Verification Commands

- `ruff check --fix backend/app/modules/official_workflows/schemas.py backend/app/modules/official_workflows/service.py backend/tests/test_pd_p1_fee_linkage_api.py backend/tests/test_pd_p1_fee_reduction_conversion.py`
- `ruff format backend/app/modules/official_workflows/schemas.py backend/app/modules/official_workflows/service.py backend/tests/test_pd_p1_fee_linkage_api.py backend/tests/test_pd_p1_fee_reduction_conversion.py`
- `ruff check backend/app/modules/official_workflows/schemas.py backend/app/modules/official_workflows/service.py backend/tests/test_pd_p1_fee_linkage_api.py backend/tests/test_pd_p1_fee_reduction_conversion.py`
- `cd backend && pytest -q tests/test_pd_p1_fee_reduction_conversion.py tests/test_pd_p1_fee_linkage_api.py`
- `./scripts/task_validate.sh PD-P1-BE-FEE-REDUCTION-CONVERSION-20260611-01`

## Acceptance

- Fee linkage response includes customer reduction ratio, computed payable ratio, and a Chinese explanation.
- `0.85` maps to `0.15`; `0.7` maps to `0.3`; blank/none maps to `1.0`.
- Customer fee semantics are no longer reported as待确认, while official rate source/template compatibility can remain pending.
