# Fee Overview Upper Fee-Type Implementation Design

- date: `2026-04-06`
- target slice: `SPEC 5.11 upper-pane fee-type implementation`
- authority:
  - `docs/superpowers/specs/2026-04-06-fee-overview-upper-feetype-design.md`

## Story Shape Classification

- `shared_file_density`: medium
- `prereq_dependency_density`: low
- `be_fe_coupling`: medium
- `evidence_cost`: medium

## chosen_runbook

- `P0-frontend-heavy-story`

## Problem Statement

The upper-pane `GovPayment` overview still lacks the truthful `fee_type` filter required by `SPEC 5.11.1`.
The semantics freeze already rejected `FeeItem.fee_type` and froze `FeeDraft.draft_type` as the first-round
authority.

## Exact Closure Slice

- extend `GET /fee-overview/gov-payments` with a truthful first-round `fee_type` filter
- implement that filter via:
  - `GovPayment -> FeeItem -> FeeDraft.draft_type`
- expose the same first-round `fee_type` selector on the upper pane of `费用情况查询一览`
- add targeted backend tests

## Assumptions

- no schema or migration is needed
- first-round fee-type options are limited to the currently distinguishable draft types:
  - `APPLY_FEE`
  - `OA_FEE`
  - `GRANT_FEE`
  - `ANNUITY_FEE`
  - `INVALID_FEE`
  - `CONSULT_FEE`
  - `SEARCH_FEE`
- the upper pane does not need a new result column for fee type

## Explicit Non-closure

- no lower-pane changes
- no result-table column expansion
- no export/print
- no close-decision update
- no schema/migration
