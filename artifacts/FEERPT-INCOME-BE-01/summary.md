# Summary

## Commands
- `python3 -m ruff check backend/app/modules/fees/api.py backend/app/modules/fees/service.py backend/app/modules/fees/schemas.py backend/tests/test_fee_report.py`
- `cd backend && pytest -q tests/test_fee_report.py`

## Results
- Extended `/fees/drafts` summary with `agent_service_amounts`.
- Implemented `T_CaseAgentSplit` first and `primary_agent_id` fallback service-fee attribution.
- Preserved existing fee report summary contract and filters.

## Notes
- This slice only attributes `total_service`.
- It does not implement billed/received/unpaid semantics or trend reporting.
