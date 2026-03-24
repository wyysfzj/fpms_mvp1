# Wave 17 Contract Freeze

## Task
- Task ID: `PE-BE-AN-07`
- Task file: `tasks/postenhancement/backend/PE-BE-AN-07.md`
- Role: Architect (`explorer`)
- Scope intent: freeze implementation contract for one atomic backend endpoint task.

## Allowlist Boundaries
- In-scope product files for implementation:
  - `backend/app/modules/annuity/api.py`
  - `backend/app/modules/annuity/service.py`
- In-scope evidence outputs:
  - `artifacts/PE-BE-AN-07/**`
- Out of scope:
  - router wiring (`backend/app/api/router.py`, reserved for `PE-BE-WIRE-01`)
  - schema/model/migration edits
  - unrelated module refactors

## Endpoint Contract
- Method/path:
  - `POST /gov-payments`
- Permission:
  - `GovPayment.Create`
  - must be parameter-injected:
  - `_perm: None = Depends(require_perm("GovPayment.Create"))`
- Request contract assumptions:
  - accepts gov-payment registration input tied to existing pay-list context.
  - supports fields required for paid registration/audit (for example paid amount/date, voucher/receipt references).

## Duplicate Protection Semantics (Mandatory)
- Duplicate registration for the same logical gov-payment target must be blocked deterministically.
- Duplicate detection key must include pay-list context + fee-item/case identity (or equivalent unique business tuple).
- Duplicate attempts must return business conflict semantics:
  - `409` with `GOV_PAYMENT_DUPLICATE`.
- Duplicate-protection behavior must be idempotent under retries:
  - retrying an already-applied payload must not create extra gov-payment rows.

## Pay-List Status Update Semantics (Mandatory)
- Gov-payment registration must trigger pay-list status recomputation/update for the affected pay-list.
- Status updates must be deterministic and based on linked payment completion state.
- Minimum transition assumptions:
  - incomplete registration keeps pay-list in non-paid state (for example `DRAFT`/in-progress equivalent).
  - completion condition moves pay-list to paid state (`PAID` or module-defined paid-equivalent).
- Status transition should be monotonic for this task scope:
  - no downgrade from paid state unless a separate reversal workflow explicitly handles it.
- Pay-list status update and gov-payment write should be transactionally coherent to avoid split-brain state.

## Error Semantics
- `400` business validation error:
  - invalid payload/state for registration
- `401` unauthenticated (`AUTH_REQUIRED`)
- `403` permission denied (`FORBIDDEN`)
- `404` referenced pay-list/fee-item/case not found
- `409` conflict:
  - duplicate gov-payment registration (`GOV_PAYMENT_DUPLICATE`)
- `422` request schema/type validation failure
- Business failures must use BusinessError envelope (`error.code/message/details`).

## Regression Risks
- Duplicate-control regression:
  - missing/weak uniqueness checks can produce double-registration and broken totals.
- Status-sync regression:
  - pay-list status not updated (or updated incorrectly) after registration causes workflow inconsistency.
- Transaction-order regression:
  - writing gov-payment without atomic pay-list status recompute can leave inconsistent records.
- Permission regression:
  - wrong permission code or dependency pattern causes access-control failures.
- Scope risk:
  - edits outside allowlist violate atomic policy.

## Acceptance Checklist
- [ ] Implementation edits only allowlisted product files for `PE-BE-AN-07`.
- [ ] `POST /gov-payments` endpoint exists in annuity API.
- [ ] Permission enforced via parameter-injected `GovPayment.Create`.
- [ ] Duplicate protection is implemented and returns `409 GOV_PAYMENT_DUPLICATE`.
- [ ] Gov-payment registration updates/recomputes related pay-list status deterministically.
- [ ] Error semantics align with `400/401/403/404/409/422`.
- [ ] Task verification passes:
  - `cd backend && pytest -q`
- [ ] Lint/format discipline passes:
  - `ruff check --fix .`
  - `ruff format .`
  - `ruff check .`
- [ ] Evidence artifacts are generated for completion claim:
  - `artifacts/PE-BE-AN-07/results.jsonl`
  - `artifacts/PE-BE-AN-07/summary.md`
  - `artifacts/PE-BE-AN-07/git/diff.patch`
