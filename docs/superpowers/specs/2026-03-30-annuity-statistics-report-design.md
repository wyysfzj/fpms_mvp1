# RPT-ANN Design

## Story Shape Classification
- shared_file_density: medium
- prereq_dependency_density: low
- be_fe_coupling: chained (BE -> FE)
- evidence_cost: medium

## chosen_runbook
- P0-frontend-heavy-story

## Problem Statement
`RPT-ANN` is the first-round annuity statistics report slice under `P2 #13`. The approved closure is not a predictive annuity platform, but a report-style enhancement on top of the existing `annuity` module. The story must provide filterable annuity statistics on existing annuity task facts, with summary cards and a detail list, without introducing charts, export, or full payment-linkage analytics.

## Assumptions
- Landing page remains `frontend/src/modules/annuity/pages/AnnuityTaskList.vue`.
- Backend reuses `GET /annuity/tasks` and extends it with report-style summary output.
- First-round filters are limited to:
  - `client_id`
  - `case_id`
  - `country`
  - `annuity_year`
  - `task_status`
  - `payment_status`
  - `date_range`
- First-round execution may keep `payment_status` as a minimal/no-op-compatible field if full payment linkage would cross into `pay-lists / gov-payments / case-receipts`.
- First-round summary is limited to annuity-task-oriented metrics around due amount, status, and year-range facts.
- No schema or migration work is required.

## Scope
- Annuity report filters on existing annuity task facts
- Summary cards on the annuity task list page
- Existing detail list retained as the detail portion of the report

## Non-scope
- Charts
- Complex export
- Predictive reminder analysis
- `pay-lists / gov-payments / case-receipts` full payment-linkage analytics
- Independent `AnnuityReport.vue`

## Closure Slice Candidates
- `ANNRPT-BE-01`: extend `GET /annuity/tasks` contract with approved report filters and summary payload
- `ANNRPT-FE-01`: complete `AnnuityTaskList.vue` report UI using approved filters and summary cards
- `ANNRPT-QA-01`: evidence audit and story close summary

## Final Judgment
- `RPT-ANN` can be decomposed into executable atomic tasks under current constraints.
