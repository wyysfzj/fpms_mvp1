# Billing Bad-Debt Workflow Design

**Feature:** `Priority P1 #6` 坏账完整流程 (Billing Bad-Debt Workflow)

**Source of truth:**
- `docs/FPMS_SPEC2_2nd_Review.md`
- `docs/FPMS SPEC 2.0.md`

## Story Shape Classification

- shared_file_density: `high`
- prereq_dependency_density: `high`
- be_fe_coupling: `chained (BE -> FE -> report)`
- evidence_cost: `high`

## Chosen Runbook

- chosen_runbook: `P0-prereq-heavy-story`

**Problem Statement**

The bad-debt workflow must support a full AR billing lifecycle from a bill into bad-debt reporting. A bill may be manually marked as bad debt or converted to bad debt after partial payment. The system must create one effective bad-debt master voucher per AR bill, record multiple recovery events against that voucher, expose the voucher and recovery chain on the bill detail page, and make bad-debt status and aggregate amounts visible in existing billing/report views.

**Approved Assumptions**

- Scope is limited to `AR` bills.
- Bad debt starts from either manual marking or partial-payment bad-debt transfer.
- A bill may have only one effective bad-debt master voucher at a time.
- The bad-debt amount covers only the remaining unpaid AR balance at the time of transfer.
- The original bill keeps its native amount/balance semantics; bad debt is modeled separately.
- Recoveries are modeled as separate records linked to the master voucher, not as in-place edits to the voucher history.
- Multiple partial recoveries are allowed as long as total recovery does not exceed the voucher amount.
- First version supports new bad-debt events only; no historical migration/backfill.
- UI entry point is the bill detail page and all user-visible text must be Simplified Chinese.
- Permissions are split into `Billing.BadDebtMark` and `Billing.BadDebtRecover`.

**In Scope**

- Bill detail bad-debt action area
- Manual bad-debt mark
- Partial-payment bad-debt transfer
- Bad-debt master voucher persistence and bill linkage
- Recovery record persistence
- Bill bad-debt status/sub-status
- Bill detail display of bad-debt voucher and recovery list
- Existing billing/report list filters and core bad-debt aggregates

**Explicit Non-Scope**

- Bad-debt reversal
- Historical backfill / bulk migration / legacy cleanup
- Automatic overdue bad debt
- `AP` or non-AR bill directions
- Dedicated bad-debt workbench / standalone bad-debt pages
- Cross-bill generalized ledger redesign

**Recommended Design**

Use the existing AR bill as the source object plus two new normalized persistence structures:

- one bad-debt master voucher per bill
- many recovery records per master voucher

The bill itself carries a bad-debt status/sub-status for filtering and reporting, but core bad-debt lifecycle history remains outside the bill row.

**Compatibility Assessment**

- SQLite PoC compatibility: feasible
- Phase 3 / 3.1 / 3.5 no-schema constraints: not feasible without prerequisite work
- Shared ownership impact: high across billing, payment/offset interactions, reporting, permissions, and bill detail frontend

**Design Conclusion**

- `不可直接实现，必须先新增 prerequisite task(s)`
- If execution is constrained to Phase 3 / 3.1 / 3.5 no-schema work:
  - `受 Phase / schema / shared-ownership 约束，当前应标记 BLOCKED`

**Story-Level Closure Slice**

- AR bills can enter a bad-debt workflow from the bill detail page, generate one effective bad-debt master voucher, record multiple recoveries, expose the chain on the bill detail page, and participate in existing billing/report filters and aggregate views.

**Story-Level Non-Closure Boundary**

- Does not close bad-debt reversal, historical migration, automatic overdue bad debt, AP direction support, or standalone bad-debt workbench UI.
