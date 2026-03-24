# A5 Batch — Task Plan (Draft by Lead)

## Objective
Add missing filter parameters to `GET /api/v1/cases` endpoint for advanced case search.

## Current State Analysis

### Already implemented in `api.py` GET /cases (lines 20-125):
- `q` (keyword search across case_no, title_cn, title_en, app_no)
- `case_no` (exact match)
- `app_no` (exact match)
- `client_id` (exact match)
- `status` (exact match)
- `date_from` / `date_to` (filters on `recv_date`)
- `sort_by` / `sort_dir` / `page` / `page_size`

### Missing per A5 spec:
- `case_type` (exact match)
- `patent_category` (exact match)
- `flow_dir` (exact match)
- `filing_date_from` / `filing_date_to` (filters on `filing_date`, NOT recv_date)
- `primary_agent_id` (exact match)

### Key Observation
- `api.py` GET /cases does **inline** query building (does NOT call `service.py` list_cases)
- `api.py` GET /cases/export has nearly identical query logic — both need updating
- `service.py` `list_cases()` also needs new params (for consistency + future use)

## Files to Modify
1. `backend/app/modules/cases/api.py` — Add Query params + filter logic to GET /cases AND GET /cases/export
2. `backend/app/modules/cases/service.py` — Add new params to `list_cases()` function
3. `backend/tests/test_case_search.py` — NEW: tests for all new filters

## Constraints (from spec)
- All new filters are optional: `Query(default=None)`
- Date filters use `>=` and `<=` comparison
- Follow existing filter pattern
- Do NOT change the response schema
