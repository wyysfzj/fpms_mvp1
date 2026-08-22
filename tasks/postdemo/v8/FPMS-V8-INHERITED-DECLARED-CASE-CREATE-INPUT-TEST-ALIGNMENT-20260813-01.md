# FPMS V8 Inherited Declared Case-Create Input Test Alignment

Status: `IMPLEMENTATION`
Risk: `PROTECTED`

## Observable outcome

Align the five positive/behavior-targeted case-create requests in the two catalog-declared
Row281 regression files with the current explicit `fee_reduction` request contract. Preserve all
existing field-roundtrip, foreign-case validation, address-ownership and generated-attachment
assertions.

## Exact closure

- Add only canonical `"fee_reduction": "0"` to each affected case-create request.
- Preserve the authoritative missing-field `422` coverage elsewhere.
- Run the two affected files together with the three other previously green declared regression
  files that exposed this non-overlapping tranche.

## Non-closure

- No product, schema, migration, fixture, shared conftest or lifecycle change.
- No assertion deletion, weakening, skip or xfail.
- No Row281 adoption, Row282/283 work or production activation.

## Exact allowlist

- `tasks/postdemo/v8/FPMS-V8-INHERITED-DECLARED-CASE-CREATE-INPUT-TEST-ALIGNMENT-20260813-01.md`
- `backend/tests/test_case_missing_fields_crud.py`
- `backend/tests/test_document_generated_attachment_persist.py`

## Verification

```text
cd backend && .venv/bin/pytest -q tests/test_case_missing_fields_crud.py tests/test_document_attachment_upload_metadata_api.py tests/test_document_generated_attachment_persist.py tests/test_document_wizard_template_source_resolution.py tests/test_pd_p1_letter_handoff_api.py
cd backend && .venv/bin/ruff check tests/test_case_missing_fields_crud.py tests/test_document_generated_attachment_persist.py
git diff --check -- <exact allowlist>
```

Independent High review with P0/P1/P2 `0/0/0` is required before Row281 may consume this
alignment.
