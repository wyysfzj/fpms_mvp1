# RPT-CASE Design

## Story Shape Classification
- shared_file_density: medium
- prereq_dependency_density: low
- be_fe_coupling: chained (BE -> FE)
- evidence_cost: medium

## chosen_runbook
- P0-frontend-heavy-story

## Problem Statement
`RPT-CASE` is the first-round case statistics report slice under `P2 #13`. The approved closure is not a separate BI platform, but a report-style enhancement on top of the existing `cases` module. The story must provide filterable case statistics on existing case facts, with summary cards and a detail list, without introducing charts, maps, or export features.

## Assumptions
- Landing page remains `frontend/src/modules/cases/pages/CaseList.vue`.
- Backend reuses the `GET /cases` list contract and extends it with report-style summary output.
- First-round filters are limited to:
  - `client_id`
  - `status`
  - `case_type`
  - `patent_category`
  - `country`
  - `agent_id`
  - `date_range`
- First-round summary is limited to quantity / status / type / time-range oriented metrics.
- No schema or migration work is required.

## Scope
- Case report filters on existing case facts
- Summary cards on the case list page
- Existing detail list retained as the detail portion of the report

## Non-scope
- Charts
- Maps
- Complex export
- BI shell / unified reports center
- Potential opportunity / lead / conversion analytics

## Closure Slice Candidates
- `CASERPT-BE-01`: extend `GET /cases` contract with approved report filters and summary payload
- `CASERPT-FE-01`: complete `CaseList.vue` report UI using approved filters and summary cards
- `CASERPT-QA-01`: evidence audit and story close summary

## Final Judgment
- `RPT-CASE` can be decomposed into executable atomic tasks under current constraints.
