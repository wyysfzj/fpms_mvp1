# Expense Stat Department Prerequisite Design

- date: `2026-04-07`
- target: `Module 4 / SPEC 5.10.2 department residual`
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
still includes department-oriented totals.

Current product carriers expose:

- `T_Expense.case_id`
- `T_Expense.client_id`
- `T_Expense.category`
- `T_Expense.amount`
- `T_Expense.created_by / updated_by`

Current product does **not** expose:

- a department field on `T_Expense`
- a truthful department carrier on currently-used expense statistics joins
- a frozen rule mapping existing client/case metadata to billing department totals

The immediate task is therefore not implementation. It is to freeze whether any truthful
department slice can be derived from current carriers, or whether a future carrier decision
is mandatory.

## Current Evidence

- expense model:
  - `backend/app/modules/expenses/models.py`
    - no `department_id`
    - no department text/code field
- expense service/statistics:
  - `backend/app/modules/expenses/service.py`
    - current grouped stats only derive case/client/gross-profit
    - no department grouping source
- case/client data used by expense stats:
  - `backend/app/modules/cases/models.py`
  - `backend/app/modules/masterdata/clients/models.py`
    - no truthful department carrier consumed by current expense statistics path
- expense UI:
  - `frontend/src/modules/expenses/pages/ExpenseList.vue`
    - no department selector
    - no department grouped totals

## Authority Freeze

### What is NOT allowed

The following pseudo-closures are rejected:

- grouping by arbitrary client buckets and calling them department totals
- grouping by case ownership and calling it department totals
- deriving department from unrelated master-data labels without a frozen business carrier
- exposing a FE `部门` filter without truthful backend authority

Reason:

- `SPEC 5.10.2` department totals are business semantics
- current expense statistics path has no faithful department carrier

### What current schema can support

Current schema can support:

- no truthful department-specific expense-stat slice beyond existing case/client totals

Current schema cannot support:

- department filter for expense query/statistics
- department-grouped totals
- department-level gross-profit semantics

## Exact Conclusion

- `EXPSTAT-DEPARTMENT-PRE-01` is a pure prerequisite/authority task
- truthful department statistics require a future carrier decision
- no current-schema product implementation should be attempted for department semantics

## Recommended Follow-up Graph

- `EXPSTAT-DEPARTMENT-CARRIER-01`
  - decide where business department ownership should live

## Explicit Non-closure

This prerequisite wave does not:

- implement any product behavior
- add schema or migration
- fake department totals using existing unrelated fields
- update final audit or close decision
- absorb worker residuals
