# Wave 27 Contract Freeze

## Task
- Task ID: `PE-BE-COM-05`
- Task file: `tasks/postenhancement/backend/PE-BE-COM-05.md`
- Role: Architect (`explorer`)
- Scope intent: freeze implementation contract for one atomic backend service integration task.

## Allowlist Boundaries
- In-scope product files for implementation:
  - `backend/app/modules/billing/service.py`
  - `backend/app/modules/commission/service.py`
- In-scope evidence outputs:
  - `artifacts/PE-BE-COM-05/**`
- Out of scope:
  - API route/response model changes
  - router wiring
  - schema/model/migration edits
  - unrelated module refactors

## Billing Hook Integration Contract
- Integration target:
  - billing generation chain for newly created bill records.
- Invocation point (mandatory ordering):
  - invoke commission hook only after bill persistence success in billing service.
  - for draft-based generation (`generate_bill_from_drafts`): call after `Bill` + `BillItem` write unit is committed, before returning bill object.
  - for direct/manual generation path (`generate_bill`): call after bill commit and refresh, before returning bill object.
- Input to hook:
  - `bill_id`
  - `actor_id` when available
  - execution mode flag (`strict=False` in billing chain; see strict contract below).

## Non-intrusive Failure Strategy (Mandatory)
- Primary rule:
  - commission write failure must not change bill success semantics.
- Required behavior in billing chain:
  - bill create flow remains successful if billing validations and bill writes succeed.
  - commission errors are swallowed at billing boundary with controlled logging/summary recording.
  - no rollback of already-committed successful bill write due to commission failure.
- Forbidden behavior:
  - raising commission exception to API layer in billing flow.
  - changing bill endpoint success status code/body because commission failed.

## Summary / Logging Contract (No API Contract Change)
- API response contract:
  - unchanged for existing bill endpoints (`POST /bills/from-drafts` and related bill generation paths).
  - no additional required response fields for commission outcome in this task.
- Internal observability requirement:
  - emit structured log event at info/error level for hook execution result.
  - minimum log context:
    - `bill_id`
    - hook outcome (`APPLIED`, `NOOP`, `FAILED_NON_BLOCKING`)
    - counts (`created_count`, `updated_count`, `skipped_count`) when available
    - error code/message when failed.
- Optional service-level summary return:
  - billing service may keep in-memory summary for debugging/tests, but it must not alter external API envelope.

## Strict / Non-strict Usage Expectation
- Commission service contract from `PE-BE-COM-04` is reused.
- Billing-chain invocation mode:
  - must use `strict=False` (non-intrusive integration mode).
- Strict mode policy:
  - `strict=True` remains available for direct commission service use (debug, targeted runs, future admin operations), but is not used by normal billing generation flow in this task.
- Determinism:
  - repeated bill-generation retries for same bill should still obey commission idempotency contract and avoid duplicate commission records.

## Error Semantics
- Billing API-layer semantics:
  - bill-generation errors remain owned by existing billing validations and error mappings.
  - commission integration failures do not alter successful bill-generation status codes.
- Commission hook semantics:
  - in non-strict mode, errors are converted to `FAILED_NON_BLOCKING` style summary/log outcome.
  - no unhandled exception escapes billing service due to commission processing.

## SQLite / Platform Constraints
- No schema/migration changes.
- Keep integration SQLite-safe and transaction-aware:
  - no PG-only SQL introduced.
  - no reliance on dialect-only `RETURNING`.
- Keep hook write work bounded to reduce lock contention risk.

## Regression Risks
- Intrusive failure regression:
  - commission exception bubbling can break existing bill success flow.
- Contract drift regression:
  - changing bill API payload/status violates compatibility requirement.
- Hook placement regression:
  - invoking before durable bill persistence can cause missing/invalid bill references.
- Observability gap:
  - missing outcome logs makes failure diagnosis impossible.
- Idempotency regression:
  - repeated trigger creates duplicate commission rows if COM-04 contract is not respected.
- Scope risk:
  - edits outside allowlist violate atomic task policy.

## Acceptance Checklist
- [ ] Implementation edits only allowlisted product files:
  - `backend/app/modules/billing/service.py`
  - `backend/app/modules/commission/service.py`
- [ ] Billing generation chain invokes commission hook at contracted post-persistence point(s).
- [ ] Billing chain uses non-strict commission mode (`strict=False`).
- [ ] Commission failure does not break successful bill creation result.
- [ ] Bill endpoint response contract remains unchanged (status/payload compatibility preserved).
- [ ] Hook emits structured result logs/summary context for success and failure.
- [ ] Idempotent rerun behavior for same bill remains aligned with `PE-BE-COM-04`.
- [ ] Task verification passes:
  - `cd backend && pytest -q tests/test_spec_alignment_e2e.py`
- [ ] Lint/format discipline passes:
  - `ruff check --fix .`
  - `ruff format .`
  - `ruff check .`
- [ ] Evidence artifacts are generated for completion claim:
  - `artifacts/PE-BE-COM-05/results.jsonl`
  - `artifacts/PE-BE-COM-05/summary.md`
  - `artifacts/PE-BE-COM-05/git/diff.patch`
