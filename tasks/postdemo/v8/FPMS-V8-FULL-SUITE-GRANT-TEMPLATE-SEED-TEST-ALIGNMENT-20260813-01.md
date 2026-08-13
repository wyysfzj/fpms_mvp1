# FPMS V8 Full-Suite Grant Template Seed Test Alignment

Status: `IMPLEMENTATION`
Risk: `PROTECTED`

## Observable outcome

Align the inherited grant-fee notice source seed test with its exact current seeding seam. The
test must still prove creation, idempotency, unique durable carriers, source resolution and real
DOCX rendering in an isolated temporary storage root.

## Exact RED and closure

The inherited test currently points `seed_dev.BASE_DIR` at an empty temporary directory and calls
the broad `seed_doc_templates`. The current broad seeder validates all eight reviewed format-letter
files before any format-letter mutation and correctly fails closed with
`FORMAT_LETTER_TEMPLATE_MISSING:FORMAT_LETTER_001`. The grant source behavior is therefore never
reached.

This task may only replace those two broad calls with the existing exact
`seed_grant_fee_notice_template_source` seam, flush each result in the same caller-owned
transaction, and assert first-call creation plus second-call idempotency. All carrier, path,
resolution and rendered-DOCX assertions remain unchanged.

## Non-closure

- No product, seed implementation, template asset, schema, migration, shared fixture/conftest or
  format-letter validation change.
- No skip, xfail, assertion deletion, copied unrelated template dataset or fallback generation.
- No claim over the other Final-matrix failures or Row283 close/release.

## Exact allowlist

- `tasks/postdemo/v8/FPMS-V8-FULL-SUITE-GRANT-TEMPLATE-SEED-TEST-ALIGNMENT-20260813-01.md`
- `backend/tests/test_grant_fee_notice_template_source_seed.py`

## Verification and acceptance

Run the inherited focused test with current grant-fee notice document and format-letter seed
authority tests, scoped Ruff, format-check and exact diff-check. Independent High review must
approve P0/P1/P2 `0/0/0` before continuing.

## Current verification result

The inherited focused test plus grant-fee notice document and format-letter seed authority suites
completed `21 passed` in `10.52s`, with four pre-existing dependency/Pydantic warnings. Scoped
Ruff, format-check and exact diff-check pass.
