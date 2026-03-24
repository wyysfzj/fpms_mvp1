# Wave 32 Contract Freeze

## Task
- Task ID: `PE-BE-COM-10`
- Task file: `tasks/postenhancement/backend/PE-BE-COM-10.md`
- Role: Architect (`explorer`)
- Scope intent: freeze implementation contract for one atomic backend endpoint task.

## Allowlist Boundaries
- In-scope product files for implementation:
  - `backend/app/modules/commission/api.py`
  - `backend/app/modules/commission/service.py`
- In-scope evidence outputs:
  - `artifacts/PE-BE-COM-10/**`
- Out of scope:
  - router wiring
  - schema/model/migration edits
  - unrelated module refactors

## Endpoint Contract (`GET /commission/reports/settlement`)
- Method/path:
  - `GET /commission/reports/settlement`
- Request body:
  - none (GET must not require body)
- Success status:
  - `200 OK`

## Aggregation Dimensions (Mandatory)
- Agent dimension:
  - aggregate totals by `agent_id`.
- Case dimension:
  - aggregate totals by `case_id`.
- Time dimension:
  - aggregate totals by time bucket derived from selected report date field.
  - default bucket granularity: monthly (`YYYY-MM`).

## Filter Params and Date-range Handling
- Core filters:
  - `agent_id` (optional)
  - `case_id` (optional)
  - `currency` (optional)
  - `settlement_status` (optional)
  - `line_status` (optional)
- Time filter params:
  - `date_from` (optional date)
  - `date_to` (optional date)
  - `time_field` (optional enum-like string):
    - `settleable_date` (from commission)
    - `settlement_period` (from settlement header period context)
    - `line_created_at` (from settlement line timestamp)
  - default `time_field`: `line_created_at`
- Date-range semantics:
  - boundaries are inclusive.
  - open-ended range is allowed (`date_from` only or `date_to` only).
  - if both provided and `date_from > date_to`, return `400` business validation.
- Data source for report rows:
  - settlement lines joined with settlement header and commission row to ensure aggregation uses generated settlement facts.

## Permission Contract
- Required permission:
  - `CommissionReport.Read`
- Mandatory parameter-injection pattern:
  - `_perm: None = Depends(require_perm("CommissionReport.Read"))`
- Do not use decorator-level `dependencies=[...]` for permission checks.

## Response Shape (Aggregated Totals + Details)
- Top-level response contract:
  - `filters` (effective filters used)
  - `totals`
  - `by_agent`
  - `by_case`
  - `by_time`
  - `details`
- `totals`:
  - `line_count`
  - `total_amount`
- `by_agent` item:
  - `agent_id`
  - `line_count`
  - `total_amount`
- `by_case` item:
  - `case_id`
  - `line_count`
  - `total_amount`
- `by_time` item:
  - `time_bucket`
  - `line_count`
  - `total_amount`
- `details` item (report drill-down row):
  - `settlement_id`
  - `settlement_no`
  - `commission_id`
  - `agent_id`
  - `case_id`
  - `amount`
  - `currency`
  - `line_status`
  - `settlement_status`
  - `settleable_date`
  - `period_from`
  - `period_to`
  - `created_at`

## Semantics / Determinism
- Aggregations must be internally consistent:
  - sum(`details.amount`) equals `totals.total_amount`.
  - grouped totals must reconcile with top-level totals for selected dataset.
- Empty-result behavior:
  - return `200` with zero totals and empty arrays (not `404`).
- Stable ordering:
  - `details` should be deterministically ordered (e.g., by `created_at`, then id) for reproducible report output.

## Error Semantics
- `400`:
  - business validation errors (invalid range/time_field/filter combos).
- `422`:
  - query type/schema validation failures (FastAPI).
- `401` / `403`:
  - unauthenticated / permission denied.
- Preserve existing BusinessError/FastAPI envelope conventions.

## Regression Risks
- Aggregation drift:
  - inconsistent grouping logic can produce totals that do not reconcile.
- Date-filter drift:
  - wrong field binding or boundary handling causes over/under-inclusion.
- Permission regression:
  - wrong permission code or injection style breaks access control.
- Contract regression:
  - missing required aggregates (`by_agent/by_case/by_time`) breaks reporting consumers.
- Scope risk:
  - edits outside allowlist violate atomic policy.

## Acceptance Checklist
- [ ] Implementation edits only allowlisted product files:
  - `backend/app/modules/commission/api.py`
  - `backend/app/modules/commission/service.py`
- [ ] `GET /commission/reports/settlement` endpoint implemented.
- [ ] Aggregation includes required dimensions:
  - by agent
  - by case
  - by time
- [ ] Filter params and inclusive date-range handling implemented with deterministic validation.
- [ ] Permission enforced with parameter-injected:
  - `Depends(require_perm("CommissionReport.Read"))`
- [ ] Response shape includes aggregated totals plus detailed rows.
- [ ] Empty-result behavior returns `200` with zero/empty aggregates.
- [ ] Task verification passes:
  - `cd backend && pytest -q`
- [ ] Lint/format discipline passes:
  - `ruff check --fix .`
  - `ruff format .`
  - `ruff check .`
- [ ] Evidence artifacts are generated for completion claim:
  - `artifacts/PE-BE-COM-10/results.jsonl`
  - `artifacts/PE-BE-COM-10/summary.md`
  - `artifacts/PE-BE-COM-10/git/diff.patch`
