# FB2 Batch — Findings

## Backend Dependency Check
- Backend A2 Address/Contact APIs: **CONFIRMED** in `backend/app/modules/masterdata/clients/api.py`
- All 8 endpoints present (CRUD for both addresses and contacts)

## Existing Code Observations
- `ClientList.vue` handleView currently routes to `/clients/${id}/edit` — should route to `/clients/${id}` after FB2
- `ClientForm.vue` has legacy single-address/contact fields (address, phone, contact_person) — kept for backward compat, FB2 adds sub-resource management
- Router already has `/clients/new` and `/clients/:id/edit` routes

## Bugs Found
- **R1 (HIGH)**: Backend has NO `GET /clients/{client_id}` endpoint. Service function `get_client()` exists at `service.py:56` but is not wired in `api.py`. Frontend `getClient()` will 404/405. ClientForm.vue edit mode has same issue (pre-existing). **Out of FB2 scope** — needs backend fix task.
- **R3 (MED)**: Frontend `getCases()` doesn't pass `client_id` param. "关联案件" tab will use direct `http.get('/cases', { params: { client_id } })` workaround since `cases.ts` is not in allowlist.

## Deviations
- **R5 (FIXED)**: `ClientDetail.vue` RelatedCase interface had `title` field but backend returns `title_cn`/`title_en`. Fixed by team lead: updated to `title_cn || title_en || '-'`.
