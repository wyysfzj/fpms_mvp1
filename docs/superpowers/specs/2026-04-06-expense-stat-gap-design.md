# Expense Stat Residual Design

- date: `2026-04-06`
- target residual: `Module 4 / SPEC 5.10.2 查询与统计`
- source baseline:
  - `docs/FPMS SPEC 2.0.md`
  - `docs/FPMS_SPEC2_Final_Audit_Excluding_Document_Generation_20260406.md`

## Story Shape Classification

- `shared_file_density`: medium
- `prereq_dependency_density`: high
- `be_fe_coupling`: medium
- `evidence_cost`: medium

## chosen_runbook

- `P0-prereq-heavy-story`

## Problem Statement

Final audit shows the current expense module only provides:

- total count
- total amount
- grouped counts/sums by category

This does not close `SPEC 5.10.2`, which requires:

- query by case/project, time range, category, worker
- summaries for:
  - per-case total expense
  - per-client / per-department expense
- gross-profit analysis using `T_CaseReceipt`

Current product evidence shows the residual is not a single visualization gap. It is a carrier-and-semantics gap:

- `T_Expense` has no worker field
- `T_Expense` has no department field
- current API contract has no worker filter
- current stats shape has no per-case / per-client / per-department aggregates
- current gross-profit semantics with `T_CaseReceipt` are not frozen

## Assumptions

- The current residual must not be stretched into “finish expense management”.
- Real product closure still requires:
  - backend contract
  - backend aggregation semantics
  - frontend user path
  - targeted tests
- However, execution must not begin until prerequisite semantics are frozen.

## Exact Conclusion

- This residual is `not ready for direct implementation`.
- It must first be treated as a prerequisite/specification program.

## Why Direct Implementation Is Rejected

### 1. Worker filter is underspecified

`SPEC 5.10.2` explicitly requires worker-based querying, but current `T_Expense` does not persist `WorkerID`.

### 2. Department aggregation is underspecified

The spec requires per-department expense totals, but there is no current department carrier on `T_Expense`, nor a frozen derivation rule.

### 3. Gross-profit semantics are not frozen

The spec requires gross-profit analysis with `T_CaseReceipt`, but current expense API does not define:

- which receipts qualify
- currency handling
- grouping granularity
- whether analysis is per case, client, or both

## Recommended Decomposition

First freeze prerequisite authority before any implementation task:

- `EXPSTAT-SPEC-01`
  - freeze exact gaps and follow-up task graph
- likely follow-up candidates:
  - `EXPSTAT-CARRIER-SPEC-01`
  - `EXPSTAT-GROSSPROFIT-SPEC-01`
  - implementation tasks only after those contracts are explicit

## Explicit Non-closure

This design wave does not:

- implement any expense statistics product behavior
- add schema or migration
- update the final audit ledger
- update any close decision
- absorb `5.11` fee overview residual

