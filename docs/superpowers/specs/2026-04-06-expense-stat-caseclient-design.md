# Expense Case/Client Stats Design

- date: `2026-04-06`
- target slice: `SPEC 5.10.2 reachable subset`
- authority:
  - `docs/superpowers/specs/2026-04-06-expense-stat-carrier-design.md`

## Story Shape Classification

- `shared_file_density`: medium
- `prereq_dependency_density`: low
- `be_fe_coupling`: medium
- `evidence_cost`: medium

## chosen_runbook

- `P0-frontend-heavy-story`

## Problem Statement

The expense module currently shows only:

- total count
- total amount
- category counts

But the reachable portion of `SPEC 5.10.2` requires real grouped statistics for:

- per-case total expense
- per-client total expense

These two grouped summaries are implementation-ready on existing carriers.

## Exact Closure Slice

- extend `GET /expenses?include_stats=true` to return:
  - `case_amounts`
  - `client_amounts`
- render both grouped summaries on `ExpenseList.vue`
- add targeted backend tests

## Assumptions

- client totals may derive from:
  - `Expense.client_id`, else
  - linked `Case.client_id`
- no schema change is required
- worker, department, and gross-profit remain out of scope

## Explicit Non-closure

- no worker filter
- no per-department totals
- no gross-profit analysis
- no export/reporting
- no expense create/edit changes

