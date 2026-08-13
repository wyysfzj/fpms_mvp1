# FPMS-V8-INHERITED-OFFICIAL-FEE-PREVIEW-CASE-STATUS-TEST-ALIGNMENT-20260813-01

Status: MECHANICAL / CONTRACT FROZEN / RED OBSERVED

## Outcome

Align the inherited official-fee preview test's CaseCreate helper with the separately
reviewed current CaseCreate contract: callers do not submit lifecycle `status`; the server
initializes it. Remove only the obsolete `"status": "NOT_FILED"` request member so the six
official-fee assertions reach their intended behavior.

## Non-closure

No product, fee rule, rate, expectation, fixture value, response assertion, source decision,
Row282 adoption, Row283 or release change.

## Exact allowlist

- `tasks/postdemo/v8/FPMS-V8-INHERITED-OFFICIAL-FEE-PREVIEW-CASE-STATUS-TEST-ALIGNMENT-20260813-01.md`
- `backend/tests/test_official_fee_preview_api.py`

## Verification

```text
cd backend && .venv/bin/pytest -q tests/test_official_fee_preview_api.py
cd backend && .venv/bin/ruff check tests/test_official_fee_preview_api.py
git diff --check -- backend/tests/test_official_fee_preview_api.py tasks/postdemo/v8/FPMS-V8-INHERITED-OFFICIAL-FEE-PREVIEW-CASE-STATUS-TEST-ALIGNMENT-20260813-01.md
```

RED is the exact six `422 VALIDATION_ERROR body.status none_required` failures. GREEN must
retain every official-fee/no-write assertion and may not edit production code.
