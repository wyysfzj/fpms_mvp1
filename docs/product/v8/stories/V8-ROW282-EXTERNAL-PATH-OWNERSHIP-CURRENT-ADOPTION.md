# Story V8-ROW282-EXTERNAL-PATH-OWNERSHIP-CURRENT-ADOPTION

- Status: `CURRENT_VERIFIED` candidate pending independent adoption review.
- Risk: `PROTECTED`.
- Purpose: close three exact current-path ownership gaps before Row282 without changing
  product or test behavior.

## Exact external path sets

### `FPMS-V8-OFFICIAL-FEE-ESTIMATE-RATE-PROVIDER-20260713-01`

- `backend/app/modules/fees/official_rate_book.py`
- `backend/tests/test_v8_official_fee_estimate_rate_provider.py`

### `FPMS-V8-OFFICIAL-FEE-PREVIEW-LEGACY-TEST-MIGRATION-20260713-01`

- `backend/tests/test_official_fee_preview_api.py`

The inherited preview test was first aligned with the separately reviewed server-owned
CaseCreate status contract by removing only its obsolete caller-supplied status input. The
exact alignment commit retains all six official-fee and no-write assertions.

### `FPMS-V8-FILING-SUBMISSION-EVIDENCE-RESOLVER-20260715-01`

- `backend/app/modules/official_workflows/filing_evidence_resolver.py`
- `backend/tests/test_v8_filing_submission_evidence_resolver.py`

## Current verification

- exact three external suites: `122 passed, 4 warnings in 31.68s`;
- exact preview semantic alignment: `6 passed, 4 warnings in 4.27s`;
- scoped Ruff and exact diff-check: PASS;
- the candidate fingerprint binds all five product/test paths plus this story, its task card
  and focused adoption contract;
- independent High review and sole ledger adoption remain required.

## Authority boundary

The bytes are adopted item-specifically; none of the three external identities substitutes
for another. No product, fee, rate, filing evidence, API, schema or migration byte changes
in this adoption story. Production customer inputs remain exactly
`CONFIG_REQUIRED / PENDING / 409 NO WRITE`; TEST_ONLY remains isolated. No Row282 output or
adoption, Row283, release gate or production activation is included.
