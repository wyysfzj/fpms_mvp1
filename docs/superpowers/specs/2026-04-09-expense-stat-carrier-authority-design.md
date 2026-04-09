# Expense Stat Carrier Authority Design

- date: `2026-04-09`
- target: `Module 4 / SPEC 5.10.2 remaining carrier-blocked residuals`
- source baseline:
  - `docs/FPMS SPEC 2.0.md`
  - `docs/FPMS_SPEC2_Final_Audit_Excluding_Document_Generation_20260406.md`
  - `docs/superpowers/specs/2026-04-07-expense-stat-worker-prereq-design.md`
  - `docs/superpowers/specs/2026-04-07-expense-stat-department-prereq-design.md`
  - `docs/superpowers/specs/2026-04-07-expense-stat-carrier-blocked-closing-design.md`

## Story Shape Classification

- `shared_file_density`: `low`
- `prereq_dependency_density`: `high`
- `be_fe_coupling`: `no immediate implementation lane`
- `evidence_cost`: `low`

## chosen_runbook

- `P0-prereq-heavy-story`

## Problem Statement

Module 4 remains `Partially Implemented` only because `SPEC 5.10.2` still contains two
carrier-blocked business semantics:

- worker-level filtering / worker statistics
- per-department expense totals

Current product already closes all truthful reachable slices on current schema:

- `每案总支出`
- `每客户支出`
- first-round `案件毛利分析`

The next truthful work is not statistics implementation. It is carrier/schema authority
planning that decides where business worker ownership and business department ownership
should live before any later product behavior can exist.

## Current Evidence

- expense carrier:
  - `backend/app/modules/expenses/models.py`
    - `case_id`
    - `client_id`
    - `category`
    - `expense_date`
    - `currency`
    - `amount`
    - `created_by`
    - `updated_by`
    - no `worker_id`
    - no `department_id`
- expense statistics path:
  - `backend/app/modules/expenses/service.py`
    - current grouped stats only derive case/client/gross-profit
    - no worker filter semantics
    - no department grouping source
- expense UI/API:
  - `backend/app/modules/expenses/api.py`
  - `frontend/src/api/expenses.ts`
  - `frontend/src/api/expenses.types.ts`
  - `frontend/src/modules/expenses/pages/ExpenseList.vue`
    - no worker selector
    - no department selector
- related business entities:
  - `backend/app/modules/cases/models.py`
    - `primary_agent_id`
    - `draftor_id`
    - no frozen rule that either field is expense worker ownership
  - `backend/app/modules/auth/models.py`
    - no department field on `T_User`

## Worker Carrier Candidates

### Candidate A: add `worker_id` to `T_Expense`

- most direct mapping to `SPEC 5.10.2 经手人`
- keeps expense statistics semantics local to the expense record
- requires migration, create/edit contract, and backfill policy

### Candidate B: derive worker from case agent fields

- possible source fields:
  - `T_Case.primary_agent_id`
  - `T_Case.draftor_id`
- rejected for current planning as default authority:
  - case ownership is not frozen as expense-handler semantics
  - one case may contain expenses handled by different workers

### Candidate C: derive worker from audit fields

- rejected:
  - `created_by`
  - `updated_by`
- reason:
  - audit history is not business ownership

## Department Carrier Candidates

### Candidate A: add `department_id` to `T_Expense`

- most direct business carrier for department totals
- avoids accidental reuse of unrelated master data
- requires migration, UI/API contract, and backfill policy

### Candidate B: derive department from `T_User`

- currently unavailable:
  - `backend/app/modules/auth/models.py` has no department field
- could become a future design only if user/organization carrier is introduced first

### Candidate C: derive department from case/client metadata

- rejected:
  - no current frozen business rule maps case/client ownership to department totals

## Recommended Authority Choice

- worker authority should first be planned as `T_Expense.worker_id`
- department authority should first be planned as `T_Expense.department_id`

Reason:

- `SPEC 5.10.2` asks for expense query/statistics semantics
- the most truthful first-round business carrier is local to the expense record itself
- case/client/audit derivation introduces pseudo-closure risk

## Schema / Migration Implication

- truthful progress now requires a schema-authority lane
- likely future migration targets:
  - `t_expense.worker_id`
  - `t_expense.department_id`
- exact FK/nullable/backfill rules must be frozen in separate atomic prerequisite stories

## Backfill Implication

- backfill is likely required if these carriers are introduced
- backfill must not default to:
  - `created_by`
  - `updated_by`
  - arbitrary case owner
  - arbitrary client bucket
- the truthful default may need:
  - null-allowed first round
  - explicit manual cleanup workflow
  - seed/bootstrap updates if required later

## Exact Conclusion

- current remaining Module 4 residuals are ready for carrier/schema prerequisite planning
- they must stay split into two independent stories:
  - `EXPSTAT-WORKER-CARRIER-01`
  - `EXPSTAT-DEPARTMENT-CARRIER-01`
- later close-audit must remain a separate story:
  - `EXPSTAT-CLOSE-02`

## Explicit Non-closure

This planning wave does not:

- implement any product behavior
- add schema or migration
- update final audit / refresh review / mitigation ledger
- merge worker and department into one execution task
- reopen already-closed case/client/gross-profit slices
