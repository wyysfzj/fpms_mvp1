# Fee Overview Lower-Pane Implementation Design

- date: `2026-04-06`
- target slice: `SPEC 5.11 lower pane / CaseReceipt backend`
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

After the upper-pane backend slice, the next truthful implementation-ready slice is the lower-pane
backend contract for `T_CaseReceipt`.

Current product only exposes:

- one flattened `/fee-unified-query`

It does not expose a dedicated lower-pane `CaseReceipt` list shaped around:

- `CaseReceipt`
- `Case`

## Exact Closure Slice

- add a dedicated backend endpoint for the `SPEC 5.11` lower pane
- return paginated `CaseReceipt`-based overview rows joined with:
  - `Case`
- support truthful first-round filters:
  - `case_no`
  - `app_no`
  - `patent_no`
  - `client_id`
  - `applicant_name`
  - `fee_type`
  - `receipt_date_from`
  - `receipt_date_to`
- add targeted backend tests

## Assumptions

- no schema or migration is needed
- `CaseReceipt.last_receipt_date` is the first-round authority for `ReceiptDate`
- `CaseReceipt.due_date` is the first-round authority for `DueDate`
- `CaseReceipt.invoice_no` is the first-round authority for `InvoiceNo`
- `CaseReceipt` lower-pane first round does not need bill joins

## Explicit Non-closure

- no upper pane changes
- no frontend page changes
- no `/fee-unified-query` modification
- no export/print
- no schema/migration
- no close-decision update
