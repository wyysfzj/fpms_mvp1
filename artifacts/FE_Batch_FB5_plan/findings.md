# FB5 Batch — Findings

## Backend Dependency Check
- Backend A5 Case Filter Params: **CONFIRMED** in `backend/app/modules/cases/api.py`
- All 8 params: client_id, status, case_type, patent_category, flow_dir, filing_date_from, filing_date_to, primary_agent_id

## Critical Issue: CaseListParams in wrong file
- `CaseListParams` interface lives in `cases.types.ts` (NOT in allowlist)
- Only `cases.ts` and `CaseList.vue` are in allowlist
- Need resolution: add cases.types.ts to allowlist OR define filter params inline

## Existing CaseList.vue Patterns
- Already has a stepFilter from route query (client-side filtering)
- Uses getCases() with only page/page_size
- Uses PaginationBar, LoadingBlock, EmptyState, ApiErrorBanner components
- Uses ZH labels and workflow module

## Bugs Found
(none yet)

## Deviations
(none yet)
