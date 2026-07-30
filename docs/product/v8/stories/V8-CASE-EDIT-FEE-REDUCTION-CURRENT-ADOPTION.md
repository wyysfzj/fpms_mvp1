# Story V8-CASE-EDIT-FEE-REDUCTION-CURRENT-ADOPTION

- Risk: `PROTECTED`
- Base: `8983ea2f6f655a186593b0a4492cdafb8e4f5d5a`
- Outcome: complete the CaseEdit fee-reduction vertical so approval evidence controls
  reduced-ratio choices and unknown or absent legacy values cannot silently become
  no-reduction.
- Authority: frozen catalog rows 97 and 101, their exact task contracts, the current
  fee-reduction approval API story, and the fee-reduction/source rules in
  `docs/product/v8/domain-contract.md`.
- Change mode: row 97 archive adoption from
  `6b2ef89da447353380b99853168d4d38aaf9210a`; row 101 targeted RED followed by minimum
  current-tree GREEN.

## Catalog IDs

1. `FPMS-V8-FEE-REDUCTION-APPROVAL-CASEEDIT-UI-20260712-01` (ordinal `97`)
2. `FPMS-V8-CASE-EDIT-FEE-REDUCTION-UI-20260712-01` (ordinal `101`)

## Dependencies and scope

- Rows 95–96 create/list APIs are current-verified by
  `V8-FEE-REDUCTION-APPROVAL-API-CURRENT-ADOPTION`.
- Rows 98–100 create/update/UI behavior is current-verified by
  `V8-CASE-FEE-REDUCTION-VERTICAL-CURRENT-ADOPTION`.
- Exact product paths:
  - `frontend/src/api/fees.ts`
  - `frontend/src/api/fees.types.ts`
  - `frontend/src/modules/cases/pages/CaseEdit.vue`
- Exact decisive tests:
  - `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-fee-reduction-approval-case-edit.spec.ts`
  - `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-case-edit-fee-reduction.spec.ts`
- The existing case-status edit spec receives only an explicit `"0"` fixture value so
  its read-only legal-status successor can still exercise save.

## Observable behavior

- CaseEdit lists and records backend approval evidence and shows its source, scope, fee
  codes, fee years, effective dates, applicant set and current flag in Simplified Chinese.
- Selecting approval evidence only unlocks the same canonical `0.7` or `0.85` option; it
  never writes the case field automatically and never links an approval ID into the case
  update payload.
- Stored `"0"`, `"0.7"` and `"0.85"` are displayed unchanged. A missing, non-string or
  unknown legacy value is preserved as an explicit blocking warning while the selector
  remains unset.
- Only an explicit canonical selection clears that warning. Missing data is never coerced
  to `"0"`; service discount remains independent.
- Approval-list failure does not prevent case loading, but locks reduced-ratio selection
  fail closed.

## TDD and verification

- Row 101 RED: two Chromium tests failed on the absent unknown/missing-value warnings.
- After row 97 archive adoption, its two tests passed while the same row 101 tests
  remained RED, proving the closures were distinct.
- Combined GREEN with the existing legal-status edit successor: 5 passed.
- Exact-file ESLint passed.
- Full frontend typecheck has the same seven inherited errors on the integration base and
  story tree, with no new error in an owned path.
- Exact story diff-check must pass and an independent High reviewer must rerun decisive
  checks, review the exact commit and reattest the case-status successor.

## Non-goals and rollback

No backend, fee policy, approval applicability calculation, official rate/source
activation, applicant-policy inference, CaseCreate behavior, schema/migration, adjacent UI,
old evidence mutation, ledger edit or milestone claim. Rollback reverts only this story
commit.
