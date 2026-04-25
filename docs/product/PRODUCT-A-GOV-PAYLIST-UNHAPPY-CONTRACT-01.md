# PRODUCT-A-GOV-PAYLIST-UNHAPPY-CONTRACT-01

## Why

TC-A-018 covers official-fee pay-list unhappy behavior. Current backend supports pay-list creation, export, marking paid, and official-payment registration, but it does not expose a stable paid-record edit/audit API or stale planned-pay-date warning contract.

## Data Source

- Skeleton testcase: TC-A-018
- Backend context: `PayList`, `PayListItem`, `GovPayment`
- Frontend context: pay-list and official-payment pages

## Confirmed Contract

- Official payment duplicate detection remains:
  - status: 409
  - code: `GOV_PAYMENT_DUPLICATE`
- Invalid official-payment inputs continue to use:
  - status: 400
  - code: `GOV_PAYMENT_INVALID`
- Pay-list state conflict continues to use:
  - status: 409
  - code: `PAY_LIST_STATE_CONFLICT`

## Closed Batch 3 Decision

For Batch 3, TC-A-018 is narrowed to the stable backend official-payment unhappy semantics that already exist. The paid-row privileged edit/audit flow remains out of scope because no update/audit endpoint exists yet.

Automation may assert:

- duplicate official payment rejected: `GOV_PAYMENT_DUPLICATE`
- invalid official payment rejected: `GOV_PAYMENT_INVALID`
- pay-list state conflict rejected: `PAY_LIST_STATE_CONFLICT`

## Deferred Product Decisions

- `product_decision_required`: Define how old a `planned_pay_date` must be before the system warns. The contract must decide whether this is a backend warning field, frontend-only warning, or blocking validation.
- `product_decision_required`: Define whether `actual_pay_date` and `invoice_no` are fields on a draft pay-list, a `GovPayment`, or only allowed during mark-paid/payment registration.
- `product_decision_required`: Define the paid `GovPayment` edit flow. The current API has no update endpoint for paid official-payment rows, so privileged edit and audit logging cannot be automated safely.

## Backend / Frontend Task Recommendation

- `BE-A-GOV-PAYLIST-UNHAPPY-01` can start only after the above decisions are resolved.
- If stale-date warning is frontend-only, create `FE-A-GOV-PAYLIST-UNHAPPY-01`.
- If paid-row edit is required, create a backend API task with an explicit audit-log model/route contract.

## Automation Readiness

`A-AUTO-PY-A-GOV-PAYLIST-VALIDATION-P1-01` may proceed with the narrowed Batch 3 assertion surface. It must not claim paid-row privileged edit/audit coverage.
