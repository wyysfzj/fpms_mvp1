# Expense Stat Close-Audit Design

- date: `2026-04-07`
- target: `Module 4 / final audit truth refresh`
- source baseline:
  - `docs/FPMS_SPEC2_Final_Audit_Excluding_Document_Generation_20260406.md`
  - `docs/superpowers/specs/2026-04-07-expense-stat-worker-prereq-design.md`
  - `docs/superpowers/specs/2026-04-07-expense-stat-department-prereq-design.md`
  - `docs/superpowers/specs/2026-04-07-expense-stat-carrier-blocked-closing-design.md`

## Story Shape Classification

- `shared_file_density`: `low`
- `prereq_dependency_density`: `low`
- `be_fe_coupling`: `doc-only close audit after committed prerequisite waves`
- `evidence_cost`: `low`

## chosen_runbook

- `P0-single-lane-story`

## Problem Statement

The final audit ledger currently still describes Module 4 as having a generic
`statistics depth` residual. After the worker prerequisite freeze, department prerequisite
freeze, and carrier-blocked result ledger, the truthful state is now narrower:

- there is no immediate implementation lane left on current schema
- the remaining residuals are carrier-blocked worker/department semantics

The audit ledger should therefore be refreshed to say that explicitly.

## Scope

- refresh Module 4 wording in the final audit ledger
- refresh Module 8 inherited residual wording
- refresh the overall remaining-gap summary and final judgment

## Explicit Non-scope

- no product-code changes
- no refresh review update
- no mitigation ledger update
- no new implementation

## Exact Closure Slice

- `EXPSTAT-CLOSE-01`
  - refresh final audit wording so remaining Module 4 gap is explicitly carrier-blocked
