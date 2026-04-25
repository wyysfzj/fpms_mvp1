# PRODUCT-A-CASE-SPEC-FEE-DISCOUNT-CONTRACT-01

## Scope

This freezes the Batch 4 MVP product contract for `TC-A-009` / spec, fee reduction, and discount boundaries.

## Confirmed MVP Contract

Batch 4 automation may assert current stable backend-supported behavior:

- `spec_pages`, `draw_pages`, `claim_count`, `claim_pages`, and `manuscript_words`
  - `0` is accepted
  - positive safe large values are accepted within schema constraints
  - negative values are rejected by request validation
- `discount_rate`
  - `0` and `1` are accepted
  - values below `0` or above `1` are rejected by request validation
- persisted accepted values can be read from case detail

## FeeReduction Decision

Do not reinterpret `fee_reduction` as a decimal ratio for Batch 4.

Current contract:

- `fee_reduction` remains a string field at case save time
- save-time numeric range validation is deferred
- follow-up task id: `PRODUCT-A-FEE-REDUCTION-RATIO-CONTRACT-01`

## Applicant Kind / Fee Policy Decision

Applicant-kind vs fee-policy warning/block is `product_decision_required`.

It must not be faked by asserting unrelated applicant-kind mismatch behavior.

## Backend Readiness Contract

`BE-A-CASE-SPEC-FEE-DISCOUNT-RULE-01` should be test/readiness oriented for the MVP surface. It must not add fee-reduction ratio validation unless a product contract explicitly requires it.

## Automation Assertion Surface

`A-AUTO-PY-A-SPEC-FEE-DISCOUNT-P1-01` must assert supported numeric/spec and discount boundaries. It must not assert fee-reduction ratio rejection or fee-policy warning/block in Batch 4 MVP.
