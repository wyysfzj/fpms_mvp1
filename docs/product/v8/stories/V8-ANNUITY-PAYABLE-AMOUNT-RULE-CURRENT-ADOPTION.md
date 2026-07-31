# Story V8-ANNUITY-PAYABLE-AMOUNT-RULE-CURRENT-ADOPTION

- Risk: `PROTECTED`
- Outcome: prove on the current lean tree that the frozen annuity payable-amount rule
  derives the yearly payable amount from the full annual fee and eligible ratio while
  preserving the unreduced annual fee as the late-fee base.
- Change mode: current adoption only. The already-integrated rule slice and focused test
  satisfy the frozen contract, so this story does not modify product or test bytes and
  does not manufacture RED.
- Authority: the official-fee, reduction and provenance boundaries in
  `docs/product/v8/domain-contract.md`; the no-default and no-activation boundaries in
  `docs/product/v8/source-decision-registry.md`; frozen catalog row `132` and its exact
  task contract.
- Base: `0516701da7834ea0ca12e8c3119173da314d1096`.

## Catalog ID

- `FPMS-V8-ANNUITY-PAYABLE-AMOUNT-RULE-20260712-01`
  (ordinal `132`; exact ID is authoritative).

## Current dependency

`FPMS-V8-ANNUITY-FIRST-TEN-YEAR-REDUCTION-SCOPE-20260712-01` is current-verified by
`V8-ANNUITY-FIRST-TEN-YEAR-REDUCTION-SCOPE-CURRENT-ADOPTION` at
`1a289152ea03956ab84e305787e78c27df29e6d1`. That commit is an ancestor of this story
base, and its independent review is `APPROVED` with zero P0/P1/P2 findings.

## Exact current paths and archive comparison

- `backend/app/modules/fees/obligation_service.py`
  - current Git blob:
    `7bc3699b592e3d934649f9b34aafeabd2842efc0`
  - current SHA-256:
    `8652cb4248ff8d4c6c2a9e4f2a086feb5d741469ba3f6661716bfc8fa7dddf2e`
  - archive Git blob at `6b2ef89da447353380b99853168d4d38aaf9210a`:
    `4d634bd51abe541c27d365598526189899f56bd9`
  - archive SHA-256:
    `3d523c08b14deca0bd7f72c12778d1dbcd661d319b2f613f2d87fdbb134505b4`
  - the two constants, `AnnuityPayableAmountResult` and
    `calculate_annuity_payable_amount` exact source slice are byte-identical to archive;
    slice SHA-256:
    `087d941aef7f7e45652da9cf8ef168f479020adc6814e934f2cef56afeccf4fd`
  - the whole-module blob difference is later accepted formatting outside this closure.
- `backend/tests/test_v8_annuity_payable_amount.py`
  - current/archive Git blob:
    `270a3c859bf440b3aad2753bb9baf96eb66d1659`
  - current/archive SHA-256:
    `ac8e01e827f5c1eebe07eb6be683ac0a35087b909feb4efd69ff457403899213`

Historical PASS and RED remain comparison evidence only. Correct current product and test
bytes were retained.

## Frozen observable contract

- `calculate_annuity_payable_amount` remains keyword-only and accepts the exact
  `Decimal` inputs `full_annual_fee` and `eligible_ratio`.
- The full annual fee must be finite, positive and no greater than
  `9999999999999999.99`; invalid input raises exactly
  `ANNUITY_FULL_ANNUAL_FEE_INVALID`.
- The eligible ratio must be a finite exact `Decimal` greater than zero and no greater
  than one; invalid input raises exactly `ANNUITY_ELIGIBLE_RATIO_INVALID`.
- The payable amount is the final product of full annual fee and eligible ratio,
  quantized once to two decimal places with `ROUND_HALF_UP`. A small caller decimal
  precision cannot change a valid result.
- The immutable result preserves both exact inputs, returns the calculated payable
  amount, and keeps `late_fee_base` equal to the full annual fee. The eligible ratio
  never reduces the late-fee base.
- The rule performs no persistence, ORM/database access, I/O, clock read, source
  selection, approval write, obligation/payment write or service-receivable behavior.

This story activates no official rate, reduction approval, source, customer default or
legal conclusion.

## Current verification and independent review

Fresh pure-function verification from this worktree ran the focused test and the smallest
direct dependency regression together:

- `test_v8_annuity_payable_amount.py` plus
  `test_v8_annuity_first_ten_year_reduction_scope.py`:
  `62 passed, 1 warning`.

The warning is the inherited third-party passlib `crypt` deprecation. Neither test writes
SQLite. Scoped Ruff check-only covers the exact product and focused-test paths; exact
diff-check confirms the candidate is story-only.

An independent High reviewer must review the exact candidate range, independently rerun
the decisive tests, verify the archive/current identities and confirm the closure and
non-goals. The implementer does not approve this `PROTECTED` story.

## Non-goals and rollback

No first-ten-year policy change, late-fee percentage rule, future-annuity obligation,
second event/rate/policy, approval writer, source/rate activation, persistence, HTTP/UI,
schema/migration/seed, ledger/disposition/review edit, old taskctl/evidence mutation or
Foundation claim. Rollback reverts only this story-card commit; current product and test
bytes remain unchanged.
