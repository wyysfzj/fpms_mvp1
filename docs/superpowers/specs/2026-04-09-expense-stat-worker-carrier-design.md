# Expense Stat Worker Carrier Design

- date: `2026-04-09`
- target: `Module 4 / SPEC 5.10.2 worker carrier authority`
- source baseline:
  - `docs/FPMS SPEC 2.0.md`
  - `docs/FPMS_SPEC2_Final_Audit_Excluding_Document_Generation_20260406.md`
  - `docs/superpowers/specs/2026-04-07-expense-stat-worker-prereq-design.md`
  - `docs/superpowers/specs/2026-04-09-expense-stat-carrier-authority-design.md`

## Story Shape Classification

- `shared_file_density`: `low`
- `prereq_dependency_density`: `high`
- `be_fe_coupling`: `schema-authority first`
- `evidence_cost`: `low`

## chosen_runbook

- `P0-prereq-heavy-story`

## Problem Statement

`SPEC 5.10.2` requires expense querying/statistics by `经手人`.

Current product exposes no truthful business worker carrier in the expense statistics path:

- `T_Expense.created_by`
- `T_Expense.updated_by`

Both are audit fields, not business worker ownership. The task here is to freeze which
business entity and field should eventually carry worker semantics before any schema or
product implementation is attempted.

## Current Evidence

- `backend/app/modules/expenses/models.py`
  - no `worker_id`
  - only `created_by / updated_by`
- `backend/app/modules/expenses/service.py`
  - no worker filter or worker-grouped statistics
- `frontend/src/modules/expenses/pages/ExpenseList.vue`
  - no worker selector
- `backend/app/modules/cases/models.py`
  - `primary_agent_id`
  - `draftor_id`
  - neither field is frozen as expense-handler semantics
- `backend/app/modules/auth/models.py`
  - user identity exists
  - no extra business mapping that would rescue current expense path

## Carrier Candidates

### Candidate A: `T_Expense.worker_id`

Pros:

- most faithful mapping to expense-level `经手人`
- one expense may truthfully belong to a different worker than the broader case owner
- supports future query/stat/grouping semantics directly

Cons:

- requires schema and migration
- requires create/edit contract changes
- requires null/backfill policy

### Candidate B: derive from `T_Case.primary_agent_id`

Rejected as default authority:

- case primary agent is case-level ownership, not necessarily expense handler
- one case may contain translation/database/travel expenses handled by different people

### Candidate C: derive from `T_Case.draftor_id`

Rejected as default authority:

- drafting role is not expense-handler semantics
- not all expense categories are drafting-related

### Candidate D: derive from `created_by / updated_by`

Rejected:

- audit fields are not business worker semantics

## Authority Choice

Recommended truthful authority:

- future business worker ownership should live on `T_Expense.worker_id`

Reason:

- the spec talks about expense query/statistics
- expense-level business ownership is the narrowest truthful carrier
- any case-level or audit-level derivation creates pseudo-closure risk

## Schema Direction

Future schema lane should plan:

- add nullable `worker_id` to `t_expense`
- likely FK to `t_user.id`
- keep first round nullable to avoid fake backfill

## Backfill Direction

Recommended first round:

- null-first policy for historical expenses
- no automatic backfill from:
  - `created_by`
  - `updated_by`
  - `primary_agent_id`
  - `draftor_id`
- if business requires population, it should happen through explicit manual/business-approved
  backfill rules in a later task

## Seed / Bootstrap Implication

- no immediate seed change required at prerequisite stage
- future implementation may need:
  - user picker source integrity
  - validation that selected `worker_id` exists

## Exact Conclusion

- `EXPSTAT-WORKER-CARRIER-01` closes the worker authority question
- truthful future direction is:
  - `T_Expense.worker_id`
  - nullable first round
  - no fake backfill
- no product implementation should start until a separate schema lane is approved

## Explicit Non-closure

This prerequisite wave does not:

- define department authority
- add schema or migration
- add FE `经手人` selector
- add worker statistics product behavior
- update final audit / close decision
