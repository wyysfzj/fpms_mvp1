# FPMS-V8-ROW282-EXTERNAL-PATH-OWNERSHIP-ADOPTION-20260813-01

Status: PROTECTED / CONTRACT FROZEN / NOT STARTED

## Outcome

Adopt exact current Git ownership for the three Row282 external product nodes whose current
product/test paths are not yet co-owned by one applicable `CURRENT_VERIFIED` story:

| External identity | Exact current paths |
| --- | --- |
| `FPMS-V8-OFFICIAL-FEE-ESTIMATE-RATE-PROVIDER-20260713-01` | `backend/app/modules/fees/official_rate_book.py`, `backend/tests/test_v8_official_fee_estimate_rate_provider.py` |
| `FPMS-V8-OFFICIAL-FEE-PREVIEW-LEGACY-TEST-MIGRATION-20260713-01` | `backend/tests/test_official_fee_preview_api.py` |
| `FPMS-V8-FILING-SUBMISSION-EVIDENCE-RESOLVER-20260715-01` | `backend/app/modules/official_workflows/filing_evidence_resolver.py`, `backend/tests/test_v8_filing_submission_evidence_resolver.py` |

The current bytes are read-only. The story binds their current tree fingerprint, fresh exact
tests, reachable candidate commit and independent High review. This prerequisite does not
change product behavior or represent one external item with another.

## Non-closure

- No product/test byte, API, schema, migration, fixture, fee rule, evidence rule or source
  decision changes.
- No Row282 output/adoption, Row283, release gate or production activation.
- Customer inputs remain `CONFIG_REQUIRED / PENDING / 409 NO WRITE`; TEST_ONLY stays isolated.

## Exact allowlist

- `tasks/postdemo/v8/FPMS-V8-ROW282-EXTERNAL-PATH-OWNERSHIP-ADOPTION-20260813-01.md`
- `backend/tests/test_v8_row282_external_path_ownership_adoption.py`
- `docs/product/v8/stories/V8-ROW282-EXTERNAL-PATH-OWNERSHIP-CURRENT-ADOPTION.md`
- `docs/product/v8/reviews/V8-ROW282-EXTERNAL-PATH-OWNERSHIP-CURRENT-ADOPTION.md`
- `docs/product/v8/coverage-ledger.json`

The story fingerprint additionally binds the five exact read-only product/test paths listed
in the outcome table. `backend/uv.lock` is unrelated and untouched.

## Verification

```text
cd backend && .venv/bin/pytest -q tests/test_v8_row282_external_path_ownership_adoption.py
cd backend && .venv/bin/pytest -q tests/test_v8_official_fee_estimate_rate_provider.py tests/test_official_fee_preview_api.py tests/test_v8_filing_submission_evidence_resolver.py
cd backend && .venv/bin/ruff check tests/test_v8_row282_external_path_ownership_adoption.py
python3 scripts/v8_lean_coverage_check.py --milestone inventory --integration-sha <candidate-sha>
git diff --check -- <exact allowlist>
```

Independent High review must approve P0/P1/P2 `0/0/0` and commit only its receipt before
the separately reviewed sole ledger adoption is committed.
