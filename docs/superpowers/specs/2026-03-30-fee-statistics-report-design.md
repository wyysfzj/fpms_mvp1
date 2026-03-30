# RPT-FEE Design

## Story Shape Classification
- shared_file_density: medium
- prereq_dependency_density: low
- be_fe_coupling: chained (BE -> FE)
- evidence_cost: medium

## chosen_runbook
- P0-frontend-heavy-story

## Problem Statement
`RPT-FEE` is the first-round fee statistics report slice under `P2 #13`. The approved closure is not a standalone BI platform, but a report-style enhancement on top of the existing `fees` module. The story must provide filterable fee statistics on existing fee draft totals and related facts, with summary cards and a detail list, without introducing charts, profit analysis, or export features.

## Assumptions
- Landing page remains `frontend/src/modules/fees/pages/FeeDraftList.vue`.
- Backend reuses `GET /fees/drafts` and extends it with report-style summary output.
- First-round filters are limited to:
  - `client_id`
  - `case_id`
  - `fee_type`
  - `currency`
  - `date_range`
  - `draft_status`
  - `bill_status`
- First-round summary is limited to service fee / government fee / total income oriented metrics.
- No schema or migration work is required.

## Scope
- Fee report filters on existing fee draft facts
- Summary cards on the fee draft list page
- Existing detail list retained as the detail portion of the report

## Non-scope
- Charts
- Complex export
- Profit-rate analysis
- Expenses / billing full reconciliation
- Predictive revenue analytics

## Closure Slice Candidates
- `FEERPT-BE-01`: extend `GET /fees/drafts` contract with approved report filters and summary payload
- `FEERPT-FE-01`: complete `FeeDraftList.vue` report UI using approved filters and summary cards
- `FEERPT-QA-01`: evidence audit and story close summary

## Final Judgment
- `RPT-FEE` can be decomposed into executable atomic tasks under current constraints.
