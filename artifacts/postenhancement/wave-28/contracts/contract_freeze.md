# Wave 28 Contract Freeze

## Task
- Task ID: `PE-BE-COM-06`
- Task file: `tasks/postenhancement/backend/PE-BE-COM-06.md`
- Role: Architect (`explorer`)
- Scope intent: freeze implementation contract for one atomic backend service task.

## Allowlist Boundaries
- In-scope product files for implementation:
  - `backend/app/modules/commission/service.py`
  - `backend/app/modules/billing/service.py`
- In-scope evidence outputs:
  - `artifacts/PE-BE-COM-06/**`
- Out of scope:
  - API route/response contract changes
  - router wiring
  - schema/model/migration edits
  - unrelated module refactors

## Service Contract (WaitPay / ForceSettle Recompute)
- Service responsibility:
  - recompute `t_commission.is_settleable` (and `settleable_date`) when payment progress changes after offset or reverse-offset.
- Contracted function shape (name can vary; semantics fixed):
  - input:
    - `db: Session` (required)
    - `case_ids: list[str]` (required; deduplicated non-empty set of affected cases)
    - `as_of_date: date | None` (optional; fallback to current business date)
    - `strict: bool = True` (optional)
  - output summary:
    - `processed_count`
    - `updated_count`
    - `unchanged_count`
    - `status` (`APPLIED`, `NOOP`, `FAILED_NON_BLOCKING`)
    - optional `items` details per commission row

## Settleable Decision Rules (Deterministic)
- Rule precedence:
  1. `force_settle = true`:
     - `is_settleable = true` regardless of payment ratio.
  2. `force_settle = false` and `wait_pay = true`:
     - `is_settleable = true` only when paid ratio reaches threshold.
     - threshold contract for MVP1: `paid_ratio >= 1.0` (full service-fee receipt).
  3. `force_settle = false` and `wait_pay = false`:
     - `is_settleable = true` by default.
- Status guard:
  - recompute targets open/active commission rows; rows already in terminal settled flow should not be regressed.
- `settleable_date` semantics:
  - set to `as_of_date` when transitioning from non-settleable to settleable.
  - keep existing date when row is already settleable.
  - clear date when transitioning from settleable to non-settleable.

## Required Payment-progress Data Source
- Primary and required source:
  - `t_case_receipt` aggregated by `case_id` and service fee context (`fee_type='SERVICE'`).
- Paid-ratio contract:
  - `paid_ratio = sum(received_amt) / sum(receivable_amt)` for the case service-fee scope.
  - if denominator `<= 0`, treat paid ratio as `0`.
  - clamp ratio to `[0, 1]` for deterministic evaluation.
- Bill balance context:
  - must not be the primary settleability source for COM-06 because it is not case-granular.

## Billing Flow Invocation Contract
- Recompute must be invoked in billing service at both payment-progress mutation points:
  - `create_offset(...)`
  - `reverse_offset(...)`
- Invocation timing:
  - after receipt/balance updates are durably committed for the offset operation.
  - recompute runs as a follow-up hook for affected case set from bill items (`case_id is not null`, service-fee context).
- Usage mode in billing chain:
  - call recompute with `strict=False` to preserve non-intrusive billing behavior.

## Invariants
- Billing contract unchanged:
  - existing offset/reverse endpoint status codes and response payload contract must not change.
- Non-intrusive integration:
  - recompute failure must not flip a successful offset/reverse operation into failure.
  - failures are logged/summarized for observability.
- Deterministic updates:
  - same persisted receipts + same commission rows => same recompute result.
  - rerunning recompute with unchanged data is idempotent (`updated_count=0` expected).

## Error / Status Semantics
- Strict mode (`strict=true`):
  - service may raise BusinessError for invalid context (`400`) or missing critical entities (`404`) where applicable.
- Non-strict mode (`strict=false`) in billing flow:
  - no exception propagation to billing caller.
  - return/log `FAILED_NON_BLOCKING` summary with error code/message/details.
- Preserve existing BusinessError envelope conventions; do not invent new API error shapes in this task.

## SQLite / Platform Constraints
- No schema/migration changes.
- Keep logic SQLite-safe:
  - no PG-only SQL operators/functions.
  - no reliance on `RETURNING` for correctness.
- Keep write transactions short and bounded to reduce lock risk.

## Regression Risks
- Rule-order regression:
  - incorrect force/wait/default precedence causes wrong settleability.
- Data-source regression:
  - using bill-level balance instead of case-receipt aggregates breaks per-case correctness.
- Hook-placement regression:
  - missing offset/reverse integration leaves stale commission settleability flags.
- Intrusive-failure regression:
  - recompute exceptions breaking offset/reverse success flow violate billing compatibility.
- Idempotency regression:
  - non-deterministic recompute leads to oscillating `is_settleable`/`settleable_date`.
- Scope risk:
  - edits outside allowlist violate atomic policy.

## Acceptance Checklist
- [ ] Implementation edits only allowlisted product files:
  - `backend/app/modules/commission/service.py`
  - `backend/app/modules/billing/service.py`
- [ ] Recompute service exists for WaitPay/ForceSettle settleability updates.
- [ ] Decision rules follow deterministic precedence:
  - force-settle override
  - wait-pay full-paid requirement
  - default settleable path
- [ ] Payment progress source uses case-receipt service-fee aggregates.
- [ ] Billing flow invokes recompute after both `create_offset` and `reverse_offset`.
- [ ] Billing response contract remains unchanged (non-intrusive behavior preserved).
- [ ] Recompute is deterministic and idempotent for unchanged underlying data.
- [ ] Task verification passes:
  - `cd backend && pytest -q`
- [ ] Lint/format discipline passes:
  - `ruff check --fix .`
  - `ruff format .`
  - `ruff check .`
- [ ] Evidence artifacts are generated for completion claim:
  - `artifacts/PE-BE-COM-06/results.jsonl`
  - `artifacts/PE-BE-COM-06/summary.md`
  - `artifacts/PE-BE-COM-06/git/diff.patch`
