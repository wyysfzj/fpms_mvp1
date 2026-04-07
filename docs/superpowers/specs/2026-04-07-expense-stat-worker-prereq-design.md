# Expense Stat Worker Prerequisite Design

- date: `2026-04-07`
- target: `Module 4 / SPEC 5.10.2 worker residual`
- source baseline:
  - `docs/FPMS SPEC 2.0.md`
  - `docs/FPMS_SPEC2_Final_Audit_Excluding_Document_Generation_20260406.md`
  - `docs/superpowers/specs/2026-04-06-expense-stat-carrier-design.md`

## Story Shape Classification

- `shared_file_density`: `low`
- `prereq_dependency_density`: `high`
- `be_fe_coupling`: `low`
- `evidence_cost`: `low`

## chosen_runbook

- `P0-prereq-heavy-story`

## Problem Statement

After closing the reachable `SPEC 5.10.2` slices, the remaining expense-stat residual
still includes worker-oriented semantics.

The spec expects worker-aware querying/analysis. Current product carriers only expose:

- `T_Expense.created_by`
- `T_Expense.updated_by`

Current product does **not** expose:

- a dedicated business `WorkerID` on `T_Expense`
- a frozen rule that `created_by` is equivalent to business worker ownership

The immediate task is therefore not implementation. It is to freeze whether any truthful
first-round worker slice can be derived from current carriers, or whether a future schema/
carrier prerequisite is mandatory.

## Current Evidence

- expense model:
  - `backend/app/modules/expenses/models.py`
    - `created_by`
    - `updated_by`
    - no `worker_id`
- expense query/service:
  - `backend/app/modules/expenses/service.py`
    - current filters only support `case_id / category / date / currency / status / q`
    - no worker filter semantics
- expense UI:
  - `frontend/src/modules/expenses/pages/ExpenseList.vue`
    - no worker selector
- current carrier freeze:
  - `docs/superpowers/specs/2026-04-06-expense-stat-carrier-design.md`

## Authority Freeze

### What is NOT allowed

The following pseudo-closures are rejected:

- treating `created_by` as business `WorkerID`
- treating `updated_by` as business `WorkerID`
- exposing a FE `经办人` selector that silently filters on audit columns
- claiming worker statistics closure without a truthful worker carrier

Reason:

- `created_by / updated_by` are audit trail fields
- `SPEC 5.10.2` worker semantics are business semantics, not edit-history semantics

### What current schema can support

Current schema can support:

- no truthful worker-specific expense-stat slice beyond audit metadata visibility

Current schema cannot support:

- worker filter for expense query/statistics
- worker-grouped totals
- worker-level gross-profit semantics

## Exact Conclusion

- `EXPSTAT-WORKER-PRE-01` is a pure prerequisite/authority task
- truthful worker statistics require a future carrier decision
- no current-schema product implementation should be attempted for worker semantics

## Recommended Follow-up Graph

- `EXPSTAT-WORKER-CARRIER-01`
  - decide where business worker ownership should live
- `EXPSTAT-DEPARTMENT-PRE-01`
  - separate prerequisite for department totals

## Explicit Non-closure

This prerequisite wave does not:

- implement any product behavior
- add schema or migration
- redefine `created_by` or `updated_by`
- update final audit or close decision
- absorb department residuals
