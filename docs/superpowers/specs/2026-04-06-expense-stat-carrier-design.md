# Expense Stat Carrier Authority Design

- date: `2026-04-06`
- target: `Module 4 / SPEC 5.10.2 carrier authority`
- source baseline:
  - `docs/FPMS SPEC 2.0.md`
  - `docs/FPMS_SPEC2_Final_Audit_Excluding_Document_Generation_20260406.md`
  - `docs/superpowers/specs/2026-04-06-expense-stat-gap-design.md`

## Story Shape Classification

- `shared_file_density`: medium
- `prereq_dependency_density`: high
- `be_fe_coupling`: low
- `evidence_cost`: medium

## chosen_runbook

- `P0-prereq-heavy-story`

## Problem Statement

After freezing the overall Module 4 residual, the next unresolved question is which parts of `SPEC 5.10.2` are reachable on existing carriers and which parts require prerequisites.

The spec requires:

- query by case/project, time range, category, worker
- summary by case
- summary by client / department
- gross-profit analysis using `T_CaseReceipt`

Current product carriers are:

- `T_Expense.case_id`
- `T_Expense.client_id`
- `T_Expense.category`
- `T_Expense.expense_date`
- `T_Expense.amount`
- `T_Expense.created_by / updated_by`

Current product does **not** have:

- dedicated `WorkerID` on `T_Expense`
- any department carrier on `T_Expense`, `T_User`, or `T_Client`

## Authority Freeze

### Reachable on current carriers

The following slices can be implemented without schema change:

- per-case expense totals
- per-client expense totals
- category/date/case/client based filtering built on existing fields

### Not reachable on current carriers

The following slices are blocked and must not be faked:

- worker filter
  - `created_by` is not a faithful substitute for business `WorkerID`
- per-department expense totals
  - no department carrier exists on expense, user, or client

### Deferred semantic freeze

- gross-profit analysis with `T_CaseReceipt`
  - may be partially reachable on `case_id`
  - but still requires explicit contract for:
    - which receipts qualify
    - fee-type scope
    - currency handling
    - aggregation output shape

## Exact Conclusion

- `EXPSTAT-WORKER` requires a prerequisite carrier decision
- `EXPSTAT-DEPARTMENT` requires a prerequisite carrier decision
- `EXPSTAT-GROSSPROFIT` requires a dedicated semantics freeze
- only `EXPSTAT-CASECLIENT-01` is currently reachable for direct implementation on existing schema

## Recommended Follow-up Graph

- `EXPSTAT-CASECLIENT-01`
  - implement per-case and per-client grouped summaries on existing carriers
- `EXPSTAT-WORKER-PRE-01`
  - decide whether a real worker carrier must be added
- `EXPSTAT-DEPARTMENT-PRE-01`
  - decide whether a real department carrier must be added
- `EXPSTAT-GROSSPROFIT-SPEC-01`
  - freeze gross-profit semantics with `T_CaseReceipt`

## Explicit Non-closure

This carrier wave does not:

- implement expense statistics product behavior
- add schema or migration
- redefine `created_by` as business `WorkerID`
- fake department totals using arbitrary grouping
- update final audit or close decision

