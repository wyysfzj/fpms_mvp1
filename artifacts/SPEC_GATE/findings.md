# SPEC ALIGNMENT GATE — Findings

## Discoveries
- Bill detail endpoint (`GET /bills/{id}`) does NOT return `amount`/`balance` fields — list endpoint required instead
- Fee draft detail endpoint (`GET /fees/drafts/{id}`) does NOT return `amount` — list endpoint required
- `BillResponse` from `POST /bills/from-drafts` only returns: id, bill_no, client_id, currency, direction, status
- GRANT_NOTICE template has no `deadline_template_code` → auto-task count is 0 (expected)
- `done_at` field is available on task detail endpoint (not on list items) — confirmed working

## Deviations
None — all spec steps implemented as specified, no workarounds needed.
