# Story V8-LEGACY-FORM-STAGED-TEST-SEEDER-SUCCESSOR-CONTRACT

- Risk: `PROTECTED`.
- Outcome: keep the 22 independently accepted legacy-form activation regressions runnable after
  the production development seeder advances to the final form-022 catalog.
- Successor to: `FPMS-V8-OUT-001-CORRECTION-REPLY-20260712-01` through
  `FPMS-V8-OUT-022-FILE-COPY-REQUEST-20260712-01`.
- Authority: the 22 accepted Scheme A form classifications and their independently accepted
  stage-specific catalog seed functions.

## Exact correction

Each historical activation test for forms 001–021 must invoke its matching
`seed_official_letter_out_form_NNN_catalog` function rather than the moving production alias
`seed_doc_templates`. This preserves the exact stage the test owns: forms 001 through N are
classified and forms N+1 through 022 remain raw. The final form-022 test continues to exercise
`seed_doc_templates` and proves the production catalog has all 22 exact internal-reference scopes.

## Exact paths and verification

- `backend/tests/test_v8_out_001_activation.py` through
  `backend/tests/test_v8_out_021_activation.py`, inclusive;
- `docs/product/v8/stories/V8-LEGACY-FORM-STAGED-TEST-SEEDER-SUCCESSOR-CONTRACT.md`.

The 22-file activation suite must first fail against the moving production alias. After the
mechanical import/call correction, all 22 tests, scoped Ruff and exact diff checks must pass, then
an independent High reviewer must approve the exact candidate.

## Non-goals and rollback

No product seeder, catalog classification, decision source, form payload, official behavior,
legal status, deadline, fee, reply, API/UI, schema/migration or task/ledger disposition changes.
No test assertion is weakened or removed. Rollback restores only the historical tests' seeder
imports and calls.
