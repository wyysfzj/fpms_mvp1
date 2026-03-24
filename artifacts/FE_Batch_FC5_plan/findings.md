# FC5 Findings

## Confirmed Backend Contracts
- `GET /tasks`: `client_id` filter param confirmed at `api.py:106`, `client_name` in response at `api.py:162-164`
- `GET /documents`: `client_id` filter param confirmed at `api.py:127`, no `client_name` in document response (only `case_no`)

## Pre-existing Implementation (No Duplication)
- `case_no` is already fully wired end-to-end for both tasks and documents — no work needed
- Both list pages already display `case_no` column with router-link

## Observations
- FeeDraftList.vue and BillList.vue do NOT use client_id el-select filters despite showing client columns — FC5 will be the first pages to add a client dropdown filter
- `getClients()` uses `page_size` param; using 9999 to load all clients is fine for MVP/PoC scale
- No ZH label updates needed; inline Chinese strings follow existing pattern (filters use inline strings, not ZH constants)
