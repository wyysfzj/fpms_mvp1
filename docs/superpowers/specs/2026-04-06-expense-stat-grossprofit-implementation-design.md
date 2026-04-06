# Expense Gross-Profit Implementation Design

- date: `2026-04-06`
- target slice: `SPEC 5.10.2 gross-profit reachable subset`
- authority:
  - `docs/superpowers/specs/2026-04-06-expense-stat-grossprofit-design.md`

## Story Shape Classification

- `shared_file_density`: medium
- `prereq_dependency_density`: low
- `be_fe_coupling`: medium
- `evidence_cost`: medium

## chosen_runbook

- `P0-frontend-heavy-story`

## Problem Statement

After the gross-profit semantics freeze, the first truthful implementation-ready slice is:

- case-level gross-profit summary
- grouped by `(case_id, currency)`
- using `CaseReceipt.received_amt - Expense.amount`

The current expense module already exposes grouped expense summaries, but it does not yet expose
or render any receipt-backed gross-profit summary.

## Exact Closure Slice

- extend `GET /expenses?include_stats=true` to return case-level `gross_profit_amounts`
- compute each row from:
  - expense totals from `T_Expense`
  - receipt totals from `T_CaseReceipt.received_amt`
  - matching on `case_id` and `currency`
- render gross-profit grouped summary cards on `ExpenseList.vue`
- add targeted backend tests

## Assumptions

- first-round output is case-level only
- first-round output is currency-safe and does not auto-convert
- rows without a `case_id` stay out of this gross-profit slice
- `CaseReceipt.received_amt` is the receipt-side authority for this slice

## Explicit Non-closure

- no client-level gross-profit
- no department-level gross-profit
- no worker-level gross-profit
- no FX conversion
- no `SPEC 5.11` two-pane fee overview
- no `GovPayment` integration
- no expense create/edit changes
