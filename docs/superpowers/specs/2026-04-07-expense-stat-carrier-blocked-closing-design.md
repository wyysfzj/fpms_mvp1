# Expense Stat Carrier-Blocked Closing Design

- date: `2026-04-07`
- target: `Module 4 / SPEC 5.10.2 remaining residuals`
- source baseline:
  - `docs/FPMS SPEC 2.0.md`
  - `docs/FPMS_SPEC2_Final_Audit_Excluding_Document_Generation_20260406.md`
  - `docs/superpowers/specs/2026-04-06-expense-stat-carrier-design.md`
  - `docs/superpowers/specs/2026-04-07-expense-stat-worker-prereq-design.md`
  - `docs/superpowers/specs/2026-04-07-expense-stat-department-prereq-design.md`

## Story Shape Classification

- `shared_file_density`: `low`
- `prereq_dependency_density`: `high`
- `be_fe_coupling`: `no immediate implementation lane`
- `evidence_cost`: `low`

## chosen_runbook

- `P0-prereq-heavy-story`

## Problem Statement

Module 4 remains `Partially Implemented` only because the remaining `SPEC 5.10.2`
residuals are now fully narrowed to carrier-blocked business semantics:

- worker-level filtering / worker statistics
- per-department expense totals

Current committed product state already closes all truthful reachable slices on the
existing schema:

- per-case expense totals
- per-client expense totals
- case-level same-currency gross-profit

The next truthful work is no longer product implementation. It is future carrier
decision work for worker and department semantics, followed by a later close-audit
once those carrier decisions are materially implemented.

## Scope

- freeze future planning for the remaining carrier-blocked residuals
- record one-task-per-slice future batch manifest
- define exact future close-audit boundary

## Explicit Non-scope

- no product implementation
- no schema/migration now
- no final-audit update now
- no reopening of already-closed case/client/gross-profit slices

## Authority Summary

### Closed reachable slices

- `每案总支出`
- `每客户支出`
- first-round `案件毛利分析`

### Blocked residuals

- `EXPSTAT-WORKER`
  - blocked until a truthful business worker carrier exists
- `EXPSTAT-DEPARTMENT`
  - blocked until a truthful department carrier exists

## Exact Conclusion

- there is no immediate product implementation lane left under current schema
- future work must be split into:
  - one worker carrier-decision story
  - one department carrier-decision story
  - one later close-audit story

## Recommended Follow-up Graph

- `EXPSTAT-WORKER-CARRIER-01`
  - decide where business worker ownership should live
- `EXPSTAT-DEPARTMENT-CARRIER-01`
  - decide where business department ownership should live
- `EXPSTAT-CLOSE-01`
  - refresh final-audit / close decision only after truthful carrier-backed product behavior exists
