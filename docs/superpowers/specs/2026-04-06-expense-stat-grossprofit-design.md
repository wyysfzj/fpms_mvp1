# Expense Gross-Profit Semantics Design

- date: `2026-04-06`
- target: `Module 4 / SPEC 5.10.2 gross-profit semantics`
- source baseline:
  - `docs/FPMS SPEC 2.0.md`
  - `docs/FPMS_SPEC2_Final_Audit_Excluding_Document_Generation_20260406.md`
  - `docs/superpowers/specs/2026-04-06-expense-stat-gap-design.md`
  - `docs/superpowers/specs/2026-04-06-expense-stat-carrier-design.md`

## Story Shape Classification

- `shared_file_density`: medium
- `prereq_dependency_density`: high
- `be_fe_coupling`: low
- `evidence_cost`: medium

## chosen_runbook

- `P0-prereq-heavy-story`

## Problem Statement

`SPEC 5.10.2` requires that expense statistics can support gross-profit analysis using
`T_CaseReceipt` (`收款 - 支出`).

After the current-carrier freeze and the reachable `每案总支出 / 每客户支出` implementation,
the remaining unresolved question is not whether expense totals exist, but what *exactly*
counts as the receipt-side authority for a truthful gross-profit slice.

Current product has:

- expense-side carrier on `T_Expense`
- receipt-side carrier on `T_CaseReceipt`
- independent fee-overview query under `SPEC 5.11`

Current product does **not** yet have a frozen contract for:

- which `CaseReceipt` rows are included in gross-profit analysis
- whether the first-round output is case-level only or also client-level
- how currency should be handled
- how to keep this slice separate from the richer two-pane `5.11` fee overview

## Current Implementation Inventory

### Expense-side authority already present

- `GET /expenses?include_stats=true`
- grouped expense totals by case and client
- source carrier:
  - `T_Expense.case_id`
  - `T_Expense.client_id`
  - `T_Expense.amount`
  - `T_Expense.currency`

Evidence:

- `backend/app/modules/expenses/api.py`
- `backend/app/modules/expenses/service.py`
- `frontend/src/modules/expenses/pages/ExpenseList.vue`
- `backend/tests/test_expense_stats_api.py`

### Receipt-side carrier already present

- `T_CaseReceipt.receivable_amt`
- `T_CaseReceipt.received_amt`
- `T_CaseReceipt.case_id`
- `T_CaseReceipt.currency`
- `T_CaseReceipt.last_receipt_date`
- `T_CaseReceipt.is_prepayment`
- `T_CaseReceipt.is_arrears`

Evidence:

- `backend/app/modules/billing/models.py`
- `backend/app/modules/billing/service.py`
- `backend/app/modules/billing/api.py`
- `backend/app/modules/billing/schemas.py`

### Important semantic warning

`CaseReceipt.received_amt` is not a pure external-cash primitive:

- some rows are created manually through `create_case_receipt(...)`
- some rows are updated through `_allocate_offset_to_receipts(...)`
- `received_amt` can be decreased again in `_reverse_offset_from_receipts(...)`

This does not make `T_CaseReceipt` unusable. It does mean the first-round gross-profit
slice must explicitly freeze what business meaning is accepted for this report, instead
of pretending the carrier is self-evident.

## Authority Freeze

### Revenue authority for `SPEC 5.10.2`

For the expense-stat gross-profit slice, the receipt-side authority is:

- `T_CaseReceipt.received_amt`

Not:

- `receivable_amt`
- `T_GovPayment`
- `PaymentLine.allocated_amt`
- the unified `5.11` projection

Reason:

- `SPEC 5.10.2` explicitly names `T_CaseReceipt`
- `收款 - 支出` is materially a received-cash semantics, not receivable semantics

### First-round grouping scope

First-round gross-profit analysis should be frozen to:

- case-level aggregation only

Client-level gross-profit may be derivable later, but it should not be absorbed into the
same first implementation slice unless explicitly planned as a follow-up.

Reason:

- case-level is the narrowest truthful overlap between `T_Expense` and `T_CaseReceipt`
- client-level grouping risks silently absorbing receipt rows whose client projection is
  indirect or mixes multiple cases

### Receipt inclusion rule

First-round included rows:

- `T_CaseReceipt` rows with non-null `case_id`

First-round excluded special reinterpretations:

- do not filter out rows merely because `is_prepayment = true`
- do not reinterpret `is_arrears` as exclusion
- do not require `fee_type` subset narrowing unless a later spec explicitly demands it

Reason:

- `SPEC 5.10.2` asks for gross-profit readiness, not a finance-grade profitability model
- adding fee-type or status exclusions now would be an unsupported reinterpretation

### Currency rule

First-round gross-profit aggregation must remain currency-safe:

- aggregate only within the same currency bucket
- do not auto-convert currencies

Recommended first output shape:

- case-level gross-profit rows grouped by `(case_id, currency)`

Reason:

- current product has no FX conversion authority in this slice
- cross-currency subtraction would be dishonest

### Boundary with `SPEC 5.11`

`EXPSTAT-GROSSPROFIT` is **not** a substitute for `5.11`.

It must not absorb:

- the upper `T_GovPayment` pane
- the lower `T_CaseReceipt` detail-pane field set
- the two-pane fee-overview UI shape
- AppNo / PatentNo / FeeCode / VoucherNo / InvoiceNo rich overview columns as a closure requirement

`5.11` remains a separate prerequisite/design topic.

## Exact Conclusion

- `EXPSTAT-GROSSPROFIT` is not blocked by schema
- `EXPSTAT-GROSSPROFIT` is blocked by missing semantics freeze only
- after this freeze, the next truthful implementation-ready slice is:
  - case-level gross-profit summary using `CaseReceipt.received_amt - Expense.amount`, grouped by
    `(case_id, currency)`
- `SPEC 5.11` remains a separate residual and must not be merged into this story

## Recommended Follow-up Graph

- `EXPSTAT-GROSSPROFIT-BE-01`
  - add case-level gross-profit grouped summary to `GET /expenses?include_stats=true`
- `EXPSTAT-GROSSPROFIT-FE-01`
  - render gross-profit grouped summary on the expense statistics page
- `EXPSTAT-GROSSPROFIT-QA-01`
  - audit evidence and close only this gross-profit slice
- `FEOVERVIEW-SPEC-01`
  - separate prerequisite/design freeze for `SPEC 5.11`

## Explicit Non-closure

This semantics wave does not:

- implement product behavior
- add schema or migration
- redefine `5.11` as satisfied
- absorb `GovPayment` into gross-profit revenue authority
- add client-level or department-level gross-profit
- add FX conversion
- update final audit or close decision
