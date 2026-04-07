# Final Audit Truth Refresh Design

- date: `2026-04-07`
- target: `docs/FPMS_SPEC2_Final_Audit_Excluding_Document_Generation_20260406.md`
- source baseline:
  - `docs/FPMS SPEC 2.0.md`
  - `docs/FPMS_SPEC2_Final_Audit_Excluding_Document_Generation_20260406.md`
  - committed product evidence after `2026-04-06`

## Story Shape Classification

- `shared_file_density`: `low`
- `prereq_dependency_density`: `low`
- `be_fe_coupling`: `doc-only close audit after committed product slices`
- `evidence_cost`: `low`

## chosen_runbook

- `P0-single-lane-story`

## Problem Statement

The final audit ledger dated `2026-04-06` is now stale relative to committed product state.

Since that audit was written, the workspace has already closed several residuals with real
product behavior:

- Module 2 `3.8.1` `has_attachment` filter
- Module 3 `4.9 / FR-DL-09` list-level export/print workflows
- Module 4 `5.11` two-pane fee overview
- Module 6 `FR-COM-07` commission report export

The final audit ledger must now be refreshed so it no longer reports already-closed slices
as residual gaps, and so the remaining Module 4 expense-statistics gap is narrowed to the
truthful residuals that still remain.

## Scope

- Refresh `docs/FPMS_SPEC2_Final_Audit_Excluding_Document_Generation_20260406.md`
- Update overall residual summary
- Update Module 2 status and evidence
- Update Module 3 status and evidence
- Update Module 4 residual wording to current truthful remaining gaps
- Update Module 6 status/rationale only if needed for consistency
- Update Module 8 inherited residual summary
- Update final remaining-gap list and final judgment

## Explicit Non-scope

- No product-code changes
- No refresh review update
- No mitigation ledger update
- No new residual implementation
- No reinterpretation that stretches beyond committed product evidence

## Current Product Evidence to Honor

### Module 2

- `GET /api/v1/documents?...&has_attachment=true|false`
- `frontend/src/modules/documents/pages/DocumentList.vue`
- `backend/tests/test_document_specific_search_api.py`

### Module 3

- `GET /api/v1/tasks/export`
- `GET /api/v1/tasks/print`
- `GET /api/v1/tasks/special/search/export`
- `GET /api/v1/tasks/special/search/print`
- `frontend/src/modules/tasks/pages/TaskList.vue`
- `frontend/src/modules/tasks/pages/TaskSpecialSearch.vue`
- targeted export/print tests

### Module 4

- `GET /api/v1/expenses?include_stats=true` now has:
  - `case_amounts`
  - `client_amounts`
  - `gross_profit_amounts`
- `SPEC 5.11` dual-pane fee overview is already closed
- truthful residuals still remain around worker / department / broader aggregation depth

### Module 6

- `GET /api/v1/commission/reports/settlement/export`
- `frontend` `导出报表` user path
- targeted export tests

## Truth Refresh Rules

- Remove any residual that now has real backend + frontend + test evidence.
- Do not over-close Module 4:
  - `per-case expense total` is closed
  - `per-client expense total` is closed
  - first-round case-level same-currency gross-profit is closed
  - `worker` and `per-department` remain residual because carrier authority is still not closed
- Keep the audit grounded in committed product behavior only.

## Exact Closure Slice

- `AUDIT-TRUTH-REFRESH-01`
  - refresh the final audit ledger so it truthfully matches current committed product state

## Design Conclusion

- `可在当前约束下拆成可执行原子任务`
