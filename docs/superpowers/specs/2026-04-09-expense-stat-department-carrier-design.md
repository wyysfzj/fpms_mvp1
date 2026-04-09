# Expense Stat Department Carrier Design

- date: `2026-04-09`
- target: `Module 4 / SPEC 5.10.2 department carrier authority`
- source baseline:
  - `docs/FPMS SPEC 2.0.md`
  - `docs/FPMS_SPEC2_Final_Audit_Excluding_Document_Generation_20260406.md`
  - `docs/superpowers/specs/2026-04-07-expense-stat-department-prereq-design.md`
  - `docs/superpowers/specs/2026-04-09-expense-stat-carrier-authority-design.md`

## Story Shape Classification

- `shared_file_density`: `low`
- `prereq_dependency_density`: `high`
- `be_fe_coupling`: `schema-authority first`
- `evidence_cost`: `low`

## chosen_runbook

- `P0-prereq-heavy-story`

## Problem Statement

`SPEC 5.10.2` requires `每部门支出`.

Current product exposes no truthful department carrier in the expense statistics path:

- no `department_id` on `T_Expense`
- no department field on `T_User`
- no frozen rule mapping case/client ownership to billing department totals

The task here is to freeze where department ownership should eventually live before any
schema or product implementation is attempted.

## Current Evidence

- `backend/app/modules/expenses/models.py`
  - no `department_id`
  - no department code/name field
- `backend/app/modules/expenses/service.py`
  - no department grouping source
- `frontend/src/modules/expenses/pages/ExpenseList.vue`
  - no department selector
- `backend/app/modules/auth/models.py`
  - `T_User` has no department field
- `backend/app/modules/masterdata/clients/models.py`
  - `Client` has no truthful department field
- `backend/app/modules/cases/models.py`
  - no frozen department business carrier consumed by expense statistics

## Carrier Candidates

### Candidate A: `T_Expense.department_id`

Pros:

- most direct mapping to department totals on the expense record
- avoids accidental derivation from unrelated case/client/user metadata
- supports future grouped totals directly

Cons:

- requires schema and migration
- requires create/edit contract changes
- requires null/backfill policy

### Candidate B: derive department from `T_User`

Rejected as current first-round authority:

- current `T_User` model has no department field
- would require a separate organization carrier first
- still would not by itself prove that the user department equals expense billing department

### Candidate C: derive department from `T_Case` or `T_Client`

Rejected:

- no frozen rule maps case/client ownership to expense department semantics
- risks inventing arbitrary aggregates

## Authority Choice

Recommended truthful authority:

- future business department ownership should live on `T_Expense.department_id`

Reason:

- the spec asks for expense-level grouped totals
- a direct expense carrier is the least ambiguous first-round business authority
- current user/case/client models do not provide a faithful department mapping

## Schema Direction

Future schema lane should plan:

- add nullable `department_id` to `t_expense`
- exact FK target is still a downstream modeling choice:
  - either future department master table
  - or another explicitly introduced organization carrier
- this authority freeze only establishes that the carrier belongs to `T_Expense`

## Backfill Direction

Recommended first round:

- null-first policy for historical expenses
- no automatic backfill from:
  - client buckets
  - case ownership
  - user roles
  - arbitrary labels in master data

## Seed / Bootstrap Implication

- no immediate seed change required at prerequisite stage
- future implementation may require:
  - organization/department seed data if a department table is later introduced

## Exact Conclusion

- `EXPSTAT-DEPARTMENT-CARRIER-01` closes the department authority question
- truthful future direction is:
  - department ownership belongs on `T_Expense`
  - nullable first round
  - no fake backfill from existing metadata
- no product implementation should start until a separate schema lane is approved

## Explicit Non-closure

This prerequisite wave does not:

- define worker authority
- add schema or migration
- add FE `部门` selector
- add department statistics product behavior
- update final audit / close decision
