# Fee Overview Upper Fee-Type Semantics Design

- date: `2026-04-06`
- target: `SPEC 5.11 upper-pane fee-type residual`
- source baseline:
  - `docs/FPMS SPEC 2.0.md`
  - `docs/superpowers/specs/2026-04-06-fee-overview-design.md`
  - `docs/superpowers/specs/2026-04-06-fee-overview-upper-implementation-design.md`

## Story Shape Classification

- `shared_file_density`: medium
- `prereq_dependency_density`: medium
- `be_fe_coupling`: medium
- `evidence_cost`: medium

## chosen_runbook

- `P0-prereq-heavy-story`

## Problem Statement

After the truthful upper-pane backend slice and the truthful `SPEC 5.11` frontend page, one residual still
remains inside `5.11.1`:

- upper-pane fee-type filtering semantics

The current upper-pane contract joins:

- `GovPayment`
- `PayList`
- `FeeItem`
- `Case`

But the only directly available `fee_type` field in that chain is `FeeItem.fee_type`, which is the billing
bucket (`GOV/SERVICE/MISC`) rather than the product category required by the spec examples such as:

- application fee
- grant fee
- annuity fee
- invalidation fee
- consulting fee

So this residual cannot be truthfully closed by reusing `FeeItem.fee_type`.

## Current Implementation Inventory

### Existing truthful slices

- dedicated upper-pane endpoint:
  - `GET /fee-overview/gov-payments`
- first-round filters already implemented:
  - `case_no`
  - `app_no`
  - `patent_no`
  - `client_id`
  - `applicant_name`
  - `paid_date_from`
  - `paid_date_to`
- frontend page now shows a truthful two-pane `费用情况查询一览`

### Why `fee_type` is still residual

- `FeeItem.fee_type` is always the narrow billing bucket and is not sufficient for the spec category filter
- `GovPayment` itself has no independent fee-category carrier
- the likely first-round authority is the fee-draft lineage:
  - `GovPayment.fee_item_id -> FeeItem.draft_id -> FeeDraft.draft_type`

## Authority Freeze

### Rejected pseudo-closures

The following must NOT be treated as truthful closure:

- exposing `FeeItem.fee_type` as the upper-pane `fee_type` filter
- faking the UI with static options that do not map to backend semantics
- reinterpreting the current page as “good enough” because it already has most other filters

### First-round authority candidate

The strongest current first-round candidate is:

- `FeeDraft.draft_type`

mapped through:

- `GovPayment -> FeeItem -> FeeDraft`

This authority is promising because it can distinguish categories such as:

- annuity
- grant
- consulting/search

without schema change.

### Remaining ambiguity to freeze

Before implementation, the mapping from `FeeDraft.draft_type` to user-visible fee-type options must be frozen.

This is necessary because:

- raw `draft_type` codes are not user-facing Chinese labels
- some spec categories may need collapsing or aliasing
- not every draft type necessarily belongs in the upper-pane gov-payment filter

## Exact Conclusion

- this residual is not a product-wide blocker
- but it is still `prereq-heavy` at the semantics level
- current next step must be:
  - `FEOVERVIEW-UPPER-FEETYPE-SPEC-01`
- likely follow-up graph:
  - `FEOVERVIEW-UPPER-FEETYPE-BE-01`
  - `FEOVERVIEW-UPPER-FEETYPE-FE-01`
  - `FEOVERVIEW-UPPER-FEETYPE-QA-01`

## Explicit Non-closure

This wave does not:

- implement any backend or frontend product behavior
- modify `/fee-overview/gov-payments`
- modify the current `费用情况查询一览` page
- add export/print
- update final audit or close decision
