# FB5 Batch — Task Plan

## Goal
Add a filter panel to CaseList with 8 filter parameters from backend A5.

## Backend Dependency
**Backend A5 (Case Filter Params) — CONFIRMED COMPLETE**
All 8 query params in `backend/app/modules/cases/api.py`: client_id, status, case_type, patent_category, flow_dir, filing_date_from, filing_date_to, primary_agent_id

## File Allowlist (STRICT)
| File | Action |
|------|--------|
| `frontend/src/api/cases.ts` | modify |
| `frontend/src/modules/cases/pages/CaseList.vue` | modify |

## Critical Finding
`CaseListParams` lives in `cases.types.ts` which is NOT in allowlist. Architect must resolve.

## Status
- [ ] Architect Plan approved
- [ ] Implementation complete
- [ ] Quality Gate passed
- [ ] Review Report generated
