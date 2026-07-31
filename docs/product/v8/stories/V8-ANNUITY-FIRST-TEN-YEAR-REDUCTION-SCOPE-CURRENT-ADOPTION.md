# Story V8-ANNUITY-FIRST-TEN-YEAR-REDUCTION-SCOPE-CURRENT-ADOPTION

- Risk: `PROTECTED`
- Outcome: prove on the current lean tree that the frozen first-ten-year annuity
  reduction wrapper preserves its exact annual-fee, patent-year, approval and
  provenance boundaries.
- Change mode: current adoption only; no product or test byte changes because the
  already-integrated implementation and focused test are byte-identical to archive
  commit `6b2ef89da447353380b99853168d4d38aaf9210a` and pass fresh current-tree
  verification.
- Authority: the official-fee, reduction and provenance rules in
  `docs/product/v8/domain-contract.md`; the source-precedence and no-default rules in
  `docs/product/v8/source-decision-registry.md`; frozen catalog row 131 and its exact
  task appendix.
- Base: `02c38d59ebfa29185ed1dfbea4fcd4c7164fe9e9`.

## Catalog ID

- `FPMS-V8-ANNUITY-FIRST-TEN-YEAR-REDUCTION-SCOPE-20260712-01`
  (ordinal `131`; exact ID is authoritative).

## Current dependencies

- `FPMS-V8-FEE-REDUCTION-VALIDATOR-20260712-01` is current-verified by
  `V8-FEE-FOUNDATION-CONTRACTS-CURRENT-VERIFICATION` at
  `c2c45134fdf38602617fedf0f56ecadba0f3f8c6`.
- `FPMS-V8-FEE-REDUCTION-APPROVAL-RECORD-SERVICE-20260712-01` is
  current-verified by `V8-FEE-FACT-WRITERS-CURRENT-ADOPTION` at
  `1a886c4e40b0ee6e83882c42e6eb4da561feccc7`.

Both commits are ancestors of this story base and both independent reviews are
`APPROVED` with zero P0/P1/P2 findings.

## Exact current paths and archive identity

- `backend/app/modules/fees/annuity_reduction.py`
  - current/archive Git blob:
    `b7d6917178ca8fe9423443c2fb2ea2db3a4dced8`
  - current/archive SHA-256:
    `ce627bd6b7992f0b5cdf14bdc2f01b830cd64cb552bcf7d080c042dc0a65f624`
- `backend/tests/test_v8_annuity_first_ten_year_reduction_scope.py`
  - current/archive Git blob:
    `58380b78d38bd3262cc992a2f4183675a070fb9b`
  - current/archive SHA-256:
    `60850e9a159bab4f92837ea0ee628840d0049bc1edbee60c539d0fa79e54db5f`

Historical PASS and RED remain comparison evidence only. Correct product and test bytes
were retained; no RED was manufactured.

## Frozen observable contract

- `validate_annuity_fee_reduction` is a pure, keyword-only wrapper around the accepted
  `validate_fee_reduction` contract and returns its result unchanged.
- `context.fee_year_key` and `grant_fee_year_key` are positive, exact non-boolean
  integer patent-year ordinals. The wrapper derives
  `grant_relative_year = context.fee_year_key - grant_fee_year_key + 1`.
- Only `CN_ANNUITY_FEE_INV`, `CN_ANNUITY_FEE_UM` and
  `CN_ANNUITY_FEE_DES` are accepted.
- Legal zero delegates directly without a statutory-window check. Exact legal non-zero
  ratios `0.7` and `0.85` may delegate only for inclusive relative years `1..10`.
- Wrapper validation order is patent-year shape, fee code, base-owned ratio/provenance,
  statutory window, then all remaining base-owned approval and scope validation.
- Wrapper-owned failures are limited to
  `ANNUITY_REDUCTION_INVALID_CONTEXT`,
  `ANNUITY_REDUCTION_FEE_CODE_UNSUPPORTED` and
  `ANNUITY_REDUCTION_YEAR_OUT_OF_SCOPE`. Base-owned failures retain the accepted
  `FeeReductionValidationError` surface.
- The wrapper performs no database/ORM access, I/O, clock read, mutation, logging,
  money calculation or rounding.

This story activates no official rate, source, reduction approval or customer default.

## Verification and review

Fresh pure-function verification from this worktree returned:

- focused wrapper test: `44 passed, 1 warning`;
- exact base-validator regression: `81 passed, 1 warning`.

The warning is the existing third-party passlib `crypt` deprecation. Neither command
writes SQLite, so no serialized SQLite lane was consumed.

Run scoped Ruff check-only on the exact product and focused-test paths, exact
story-only diff-check, archive/current zero-diff checks and exact-range inspection. An
independent High reviewer must review the exact commit/range and independently rerun the
decisive focused and base-validator checks. The implementer does not approve this
`PROTECTED` story.

## Non-goals and rollback

No PCT rule, official rate-book rule, second annuity rule, approval writer, source or
rate activation, obligation/payment/service-receivable behavior, persistence, HTTP/UI,
schema/migration/seed, ledger/disposition/review edit, old taskctl/evidence mutation or
Foundation claim. Rollback reverts only this story-card commit; the current product and
test bytes remain unchanged.
