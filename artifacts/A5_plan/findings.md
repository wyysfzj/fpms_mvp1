# A5 Batch — Findings

## Initial Analysis
- GET /cases already has `client_id`, `status`, `date_from`/`date_to` (on recv_date) — these are DONE
- GET /cases does NOT use service.py list_cases — query is built inline in api.py
- GET /cases/export is a near-copy of GET /cases query logic — both need same filters
- `ilike` is used for keyword search in api.py (SQLite supports this via LIKE being case-insensitive)

## Implementation Notes
- `filing_date` is not settable via API (neither POST create nor PUT update) — tests use direct ORM insert
- Dual maintenance: filter logic duplicated between api.py inline queries and service.py — pre-existing tech debt, out of scope

## Bugs Found
- None in A5 scope
