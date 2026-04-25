# PRODUCT-A-APPLY-FEE-DRAFT-CONTRACT-01

## Why

`TC-A-015` requires a stable APPLY_FEE draft generation behavior. The current backend has generic `FeeDraft`, `FeeItem`, and `FeeRate` CRUD, but the automation needs a deterministic rule for domestic invention application-fee drafts.

This document freezes the minimal contract for backend implementation and later pytest automation.

## Data Source

- Skeleton testcase: `TC-A-015`
- Wave: A
- Priority: P0
- Topic: A4 application-fee draft generation
- Expected behavior:
  - one APPLY_FEE draft is created
  - FeeItems are created
  - official fee uses fee reduction
  - excess claim fee uses claims beyond 10
  - service fee can use discount
  - totals are stable

## API Contract

Backend should expose one stable generation endpoint:

- Method: `POST`
- Path: `/api/v1/fees/drafts/apply-fee/generate`
- Request:

```json
{
  "case_id": "...",
  "currency": "CNY",
  "discount_rate": 0.0
}
```

Rules:

- `case_id` is required.
- `currency` defaults to `CNY` when omitted.
- `discount_rate` defaults to the case `discount_rate` when omitted, otherwise `0`.
- The endpoint generates or returns the open APPLY_FEE draft for the case.

Response should use existing FeeDraft response shape where possible and include enough fields for automation to query items through existing item endpoints.

## Required Case Fields

For MVP Batch 2, the generation rule supports:

- `case_type = NORMAL`
- `flow_dir = CN_DOMESTIC`
- `patent_category = INV`
- `claim_count`
- `fee_reduction`
- `client_id`
- valid applicants

If a case is not a supported domestic invention case, backend returns a stable business error:

- status: `400`
- code: `APPLY_FEE_UNSUPPORTED_CASE`
- details: `case_id`, `case_type`, `flow_dir`, `patent_category`

## FeeRate Contract

The rule uses existing `FeeRate` rows. Required rate codes:

- `APPLY_BASE_GOV`
  - fee_type: `GOV`
  - calc_mode: `FIXED`
  - official base fee before reduction
- `APPLY_EXCESS_CLAIM`
  - fee_type: `GOV`
  - calc_mode: `PER_CLAIM`
  - applies only to claims beyond 10
- `APPLY_SERVICE`
  - fee_type: `SERVICE`
  - calc_mode: `FIXED`
  - service fee before discount

All rates must match the requested currency and be enabled.

If any required FeeRate is missing, backend returns:

- status: `409`
- code: `APPLY_FEE_RATE_MISSING`
- details: `missing_fee_codes`, `currency`

## Calculation Contract

### Claim Count

- If `claim_count` is null, treat it as 0.
- `excess_claim_count = max(claim_count - 10, 0)`.
- For `claim_count = 12`, `excess_claim_count = 2`.

### Fee Reduction

`fee_reduction` is stored as a decimal-like ratio string on case data.

- `0.15` means the payer pays 15% of the official fee.
- If absent or invalid, use `1.00`.
- Applies to GOV fee items only.
- Does not apply to SERVICE fee items.

### Discount

`discount_rate` is a decimal ratio from 0 to 1.

- `0.10` means 10% discount.
- Applies to SERVICE fee item only.
- Does not apply to GOV fee items.

### Amounts

- Base GOV amount = `APPLY_BASE_GOV.amount * fee_reduction_ratio`.
- Excess claim GOV amount = `APPLY_EXCESS_CLAIM.amount * excess_claim_count * fee_reduction_ratio`.
- Service amount = `APPLY_SERVICE.amount * (1 - discount_rate)`.
- Currency: request currency, default `CNY`.
- Rounding: use existing Decimal behavior and store two-decimal-compatible values.

## FeeDraft Contract

Generated draft fields:

- `draft_type = APPLY_FEE`
- `status = OPEN`
- `case_id = request.case_id`
- `client_id = case.client_id`
- `currency = request currency`
- `total_amount = sum(FeeItem.amount)`

Idempotency:

- If an OPEN APPLY_FEE draft already exists for the same case and currency, return it and do not create duplicate FeeItems.
- LOCKED or downstream-billed drafts are not rewritten by this MVP generation endpoint.

## FeeItem Contract

Generated items:

1. Base official fee:
   - `fee_type = GOV`
   - `fee_code = APPLY_BASE_GOV`
   - amount follows the reduction rule
2. Excess claim official fee:
   - `fee_type = GOV`
   - `fee_code = APPLY_EXCESS_CLAIM`
   - only created when `excess_claim_count > 0`
3. Service fee:
   - `fee_type = SERVICE`
   - `fee_code = APPLY_SERVICE`
   - amount follows the discount rule

Each item should retain `rate_id` where existing model/API supports it.

## Automation Assertion Surface

`TC-A-015` automation should assert:

- generation endpoint returns success
- one OPEN APPLY_FEE draft exists
- at least one GOV FeeItem and one SERVICE FeeItem exist
- `APPLY_EXCESS_CLAIM` exists when claim_count is 12
- GOV items reflect fee reduction
- SERVICE item reflects discount
- draft total equals sum of item amounts
- rerun is idempotent for OPEN draft

## Non-Goals

- no pay-list generation
- no bill generation
- no payment or offset
- no commission
- no jurisdiction-specific full fee schedule
- no frontend UI contract
