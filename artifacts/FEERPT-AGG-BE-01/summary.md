# Summary

## Commands
- `python3 -m ruff format backend/app/modules/fees/schemas.py backend/app/modules/fees/service.py backend/tests/test_fee_report.py`
- `python3 -m ruff check backend/app/modules/fees/api.py backend/app/modules/fees/service.py backend/app/modules/fees/schemas.py backend/tests/test_fee_report.py`
- `cd backend && pytest -q tests/test_fee_report.py`

## Results
- Added grouped fee-report summary carriers: `client_amounts`, `case_type_amounts`, `country_amounts`.
- Preserved existing `/fees/drafts` list contract and total summary fields.
- Verified grouped summary semantics with targeted regression coverage.

## Notes
- Country summary uses `to_country` first, then `from_country`, otherwise `未填写`.
- This slice does not include agent-attributed income, billed/received/unpaid semantics, or趋势统计.
