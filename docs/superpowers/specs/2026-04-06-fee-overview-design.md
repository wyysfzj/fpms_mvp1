# Fee Overview Design

- date: `2026-04-06`
- target: `Module 4 / SPEC 5.11 prerequisite authority`
- source baseline:
  - `docs/FPMS SPEC 2.0.md`
  - `docs/FPMS_SPEC2_Final_Audit_Excluding_Document_Generation_20260406.md`
  - `docs/superpowers/specs/2026-04-06-expense-stat-grossprofit-design.md`

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: high
- `be_fe_coupling`: medium
- `evidence_cost`: medium

## chosen_runbook

- `P0-prereq-heavy-story`

## Problem Statement

`SPEC 5.11` defines a `费用情况查询一览` with two distinct panes:

- upper grid: `T_GovPayment`
- lower grid: `T_CaseReceipt`

Each pane has its own query semantics, field set, and data-source contract.

Current product does not implement that structure. It has:

- one page: `统一费用查询`
- one endpoint: `/fee-unified-query`
- one flattened projection mixing payment and receipt rows

This current product path is useful, but it is not materially equivalent to `SPEC 5.11`.

## Current Implementation Inventory

### Existing product behavior

- frontend page:
  - `frontend/src/modules/billing/pages/FeeUnifiedQuery.vue`
- backend endpoint:
  - `backend/app/modules/billing/api.py` -> `GET /fee-unified-query`
- backend service:
  - `backend/app/modules/billing/service.py` -> `list_fee_unified_queries(...)`
- response schema:
  - `backend/app/modules/billing/schemas.py` -> `FeeUnifiedQueryListResponse`

### What current product actually does

- merges payment-like rows and receipt rows into one list
- filters one flattened result set by:
  - `record_type`
  - `case_id`
  - `biz_no`
  - `party_name`
  - `status`
  - `currency`
  - `date_from/date_to`
  - `amount_from/amount_to`

### Why it is not `SPEC 5.11`

It does not provide:

- a separate upper `GovPayment` pane
- a separate lower `CaseReceipt` pane
- the spec field set:
  - `AppNo`
  - `PatentNo`
  - `FeeCode`
  - `FeeName`
  - `YearNo`
  - `ListNo`
  - `VoucherNo`
  - `InvoiceNo`
  - `PlannedPayDate`
  - `PaidDate`
  - `DueDate`
- the pane-specific time-range semantics

## Authority Freeze

### Pane authority

For `SPEC 5.11`, first-class pane authority must remain:

- upper pane:
  - `T_GovPayment` joined to `T_PayList`, `T_FeeItem`, `T_Case`
- lower pane:
  - `T_CaseReceipt` joined to `T_Case`

The current unified query projection must **not** be stretched into the authority for either pane.

### Boundary with `5.10.2 gross-profit`

`EXPSTAT-GROSSPROFIT` and `SPEC 5.11` are separate residuals.

`5.11` must not be treated as:

- a richer visualization of expense stats
- a natural extension of gross-profit grouped summaries

`5.11` is its own query product with its own field contract.

### Implementation shape

This residual is not implementation-ready as one big story.

It must first be decomposed into at least:

- pane contract freeze
- upper-pane backend slice
- lower-pane/backend contract or reuse judgment
- frontend page decomposition
- QA close audit

### Current prerequisite judgment

Current repo likely has enough carriers to support a truthful first implementation without schema change:

- `GovPayment` already exists
- `CaseReceipt` already exists

But implementation is still blocked on contract/decomposition authority because:

- current unified endpoint shape is structurally wrong for the target
- field equivalence is not yet frozen
- page shape and ownership are still shared/high-risk

## Exact Conclusion

- `SPEC 5.11` is a prerequisite-heavy residual
- current unified query must not be reclassified as `almost closed`
- current next step must be:
  - `FEOVERVIEW-SPEC-01`
- likely follow-up graph:
  - `FEOVERVIEW-UPPER-BE-01`
  - `FEOVERVIEW-LOWER-BE-01`
  - `FEOVERVIEW-FE-01`
  - `FEOVERVIEW-QA-01`

## Explicit Non-closure

This wave does not:

- implement any product behavior
- modify `/fee-unified-query`
- rename the current unified page
- update final audit or close decision
- absorb `EXPSTAT-GROSSPROFIT`
