# PRODUCT-A-APPLY-FEE-INVALID-CONTRACT-01

## Why

TC-A-016 expects APPLY_FEE draft and item invalid-data validation. The current backend fee item API is rate-driven: an item is created from `rate_id`, then backend copies `fee_code`, `fee_name`, and `fee_type` from `FeeRate`. That means some skeleton invalid inputs cannot be expressed safely through the current API.

## Data Source

- Skeleton testcase: TC-A-016
- Backend context: `FeeDraft`, `FeeItem`, `FeeRate`, `FeeItemCreateIn`, `FeeItemUpdateIn`

## Confirmed Contract

- Empty/blank draft currency must be rejected with:
  - status: 400
  - code: `FEE_DRAFT_CURRENCY_REQUIRED`
  - details: `{ "currency": "..." }`
- Negative quantity or negative unit price must be rejected with:
  - status: 400
  - code: `FEE_ITEM_AMOUNT_INVALID`
  - details: `{ "quantity": "...", "unit_price": "..." }`
- Deleting or saving a draft into a billable state with no fee items must be rejected with:
  - status: 400
  - code: `FEE_DRAFT_ITEM_REQUIRED`
  - details: `{ "draft_id": "..." }`
- Rate currency mismatch continues to use `FEE_CURRENCY_MISMATCH`.
- Missing/disabled rate continues to use `FEE_RATE_NOT_FOUND` / `FEE_RATE_DISABLED`.

## Closed Product Decision

For Batch 3, TC-A-016 keeps the backend fee item model rate-driven. The product decision is to avoid a broad manual fee item API for this batch. Automation may assert only the backend-supported MVP validation surface below.

## Deferred Product Decisions

- `product_decision_required`: A future manual fee item API may support explicit fee code/name blank validation. It is out of Batch 3 MVP scope.
- `product_decision_required`: A future manual fee item API may support explicit fee type override/mismatch validation. It is out of Batch 3 MVP scope.
- `product_decision_required`: TC-A-016 mentions amount-zero warning and currency-change recalculation. Current API responses do not have a stable warning envelope. Product must decide whether warnings are API response fields, frontend-only prompts, or audit records.

## Backend Task Recommendation

`BE-A-APPLY-FEE-ITEM-VALIDATION-01` may safely implement only the confirmed contract above. It must not fake the branches marked `product_decision_required`.

## Automation Readiness

`A-AUTO-PY-A-APPLY-FEE-INVALID-P1-01` may proceed after `BE-A-APPLY-FEE-ITEM-VALIDATION-01` passes, but it must assert only the confirmed MVP contract and explicitly not cover deferred manual-item branches.
