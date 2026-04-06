# Fee Overview Upper-Pane Implementation Design

- date: `2026-04-06`
- target slice: `SPEC 5.11 upper pane / GovPayment backend`
- authority:
  - `docs/superpowers/specs/2026-04-06-fee-overview-design.md`

## Story Shape Classification

- `shared_file_density`: medium
- `prereq_dependency_density`: low
- `be_fe_coupling`: low
- `evidence_cost`: medium

## chosen_runbook

- `P0-single-lane-story`

## Problem Statement

After the `SPEC 5.11` prerequisite freeze, the first truthful implementation-ready slice is the
upper-pane backend contract for `T_GovPayment`.

Current product only exposes:

- one flattened `/fee-unified-query`

It does not expose a dedicated upper-pane `GovPayment` list shaped around:

- `GovPayment`
- `PayList`
- `FeeItem`
- `Case`

## Exact Closure Slice

- add a dedicated backend endpoint for the `SPEC 5.11` upper pane
- return paginated `GovPayment`-based overview rows joined with:
  - `PayList`
  - `FeeItem`
  - `Case`
- support truthful first-round filters:
  - `case_no`
  - `app_no`
  - `patent_no`
  - `client_id`
  - `applicant_name`
  - `paid_date_from`
  - `paid_date_to`
- add targeted backend tests

## Assumptions

- no schema or migration is needed
- `PayList.pay_list_no` is the authority for `ListNo`
- `PayList.planned_pay_date` is the authority for `PlannedPayDate`
- `GovPayment.paid_amount` is the authority for `PaidAmt`
- `FeeItem.amount` is the first-round authority for `PlannedAmt`
- `GovPayment.official_receipt_no` is not reinterpreted as `VoucherNo`

## Explicit Non-closure

- no lower-pane `CaseReceipt` endpoint
- no frontend page changes
- no `/fee-unified-query` modification
- no fee-type filter semantics
- no export/print
- no `InvoiceNo` or `VoucherNo` write path
- no schema/migration
