# Wave 18 Contract Freeze

## Task
- Task ID: `PE-BE-CL-01`
- Task file: `tasks/postenhancement/backend/PE-BE-CL-01.md`
- Role: Architect (`explorer`)
- Scope intent: freeze implementation contract for one atomic backend service task.

## Allowlist Boundaries
- In-scope product file for implementation:
  - `backend/app/modules/collections/service.py`
- In-scope evidence outputs:
  - `artifacts/PE-BE-CL-01/**`
- Out of scope:
  - `backend/app/modules/collections/api.py` (belongs to `PE-BE-CL-02/03/04/05`)
  - router wiring, schema/model/migration edits
  - unrelated module refactors

## Service Contract
- Service responsibility:
  - filter overdue bills as of a cutoff date
  - group by customer and cutoff-date context
  - generate dunning batch head + line snapshots
- Minimum input assumptions:
  - `to_date` (cutoff date, required)
  - optional customer filter (`client_id` or client set)
  - optional include/exclude rules for bill statuses
- Minimum output assumptions:
  - list of generated (or reused) dunning batches with per-batch summary
  - snapshot lines linked to each batch
  - deterministic result for same input set

## Expected Data Semantics
- Overdue bill definition at snapshot time:
  - `bill.due_date <= to_date`
  - bill has unpaid balance (`balance > 0`)
  - settled/cancelled or non-collectable statuses excluded by rule
- Dunning head semantics:
  - one head per customer per cutoff context
  - `total_amt` equals sum of included bill outstanding balances at snapshot time
  - status initialized to open-state for follow-up workflow
- Dunning line semantics:
  - one line per included overdue bill in the batch
  - line outstanding amount is a snapshot value (must not be mutated by later collections)
  - bill may appear again in future rounds with a new snapshot line (different batch/time)

## Idempotency / Duplicate Policy Assumptions
- Duplicate key assumption:
  - `(client_id, to_date, eligible-bill-snapshot)` defines one logical generation result.
- Re-run behavior with identical input:
  - must not create duplicate head/line rows.
  - service should either:
    - return existing batch(es) idempotently, or
    - no-op with explicit duplicate indicator.
- Multi-round policy:
  - new rounds are allowed for later cutoff dates.
  - same cutoff repeated generation should not duplicate snapshot rows.

## Error / Status Semantics
- `400` business validation:
  - invalid cutoff/payload/filter semantics
  - invalid dunning state operation (`DUNNING_BATCH_STATE_INVALID`)
- `404` not found:
  - requested customer/batch scope not found (when caller passes explicit target IDs)
  - reserved code alignment: `DUNNING_BATCH_NOT_FOUND`
- `409` conflict (optional strict mode):
  - duplicate generation request when implementation chooses conflict over idempotent reuse
- Service should raise domain errors compatible with post-enhancement BusinessError envelope mapping when called by API layer.

## Regression Risks
- Snapshot integrity risk:
  - using live bill balance references instead of frozen snapshot values breaks historical dunning accuracy.
- Duplicate batch risk:
  - reruns creating multiple heads/lines for same cutoff context inflate totals and confuse follow-up actions.
- Filter drift risk:
  - overdue criteria mismatches (due-date/balance/status) produce under/over-inclusion.
- Aggregation risk:
  - wrong customer grouping or total calculation corrupts batch summaries.
- Scope risk:
  - edits outside `backend/app/modules/collections/service.py` violate atomic policy.

## Acceptance Checklist
- [ ] Implementation edits only allowlisted product file for `PE-BE-CL-01`.
- [ ] Service filters overdue bills by cutoff date and unpaid balance.
- [ ] Service groups by customer + cutoff and generates dunning head/line snapshots.
- [ ] Head totals match sum of line outstanding snapshots.
- [ ] Idempotent/duplicate policy prevents duplicate head+line generation for repeated same-input runs.
- [ ] Error semantics align with `400/404` baseline and defined duplicate policy behavior.
- [ ] Task verification passes:
  - `cd backend && pytest -q`
- [ ] Lint/format discipline passes:
  - `ruff check --fix .`
  - `ruff format .`
  - `ruff check .`
- [ ] Evidence artifacts are generated for completion claim:
  - `artifacts/PE-BE-CL-01/results.jsonl`
  - `artifacts/PE-BE-CL-01/summary.md`
  - `artifacts/PE-BE-CL-01/git/diff.patch`
