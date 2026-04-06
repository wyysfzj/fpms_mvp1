# Fee Overview Frontend Implementation Design

- date: `2026-04-06`
- target slice: `SPEC 5.11 frontend page`
- authority:
  - `docs/superpowers/specs/2026-04-06-fee-overview-design.md`

## Story Shape Classification

- `shared_file_density`: medium
- `prereq_dependency_density`: low
- `be_fe_coupling`: medium
- `evidence_cost`: medium

## chosen_runbook

- `P0-frontend-heavy-story`

## Problem Statement

`SPEC 5.11` now has truthful upper-pane and lower-pane backend endpoints, but the frontend user path still
shows the legacy unified list. That page shape is not materially equivalent to the required two-pane fee
overview.

## Exact Closure Slice

- keep the existing route path
- replace the legacy unified-query user path with a truthful two-pane fee overview page
- connect the upper pane to:
  - `GET /fee-overview/gov-payments`
- connect the lower pane to:
  - `GET /fee-overview/case-receipts`
- expose only the first-round filters that backend currently supports
- update menu text so the user-visible entry matches the implemented product

## Assumptions

- no router rewiring is required
- no schema or migration is required
- page-level closure does not require export/print
- first-round FE must not fake unsupported upper-pane `fee_type` filtering

## Explicit Non-closure

- no backend changes
- no export/print
- no `/fee-unified-query` backend deletion
- no close-decision update
- no `SPEC 5.11` fee-type parity claim for the upper pane
