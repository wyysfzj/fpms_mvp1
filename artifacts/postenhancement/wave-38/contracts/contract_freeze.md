# Wave 38 Contract Freeze

## Task
- Task ID: `PE-BE-CS-06`
- Task file: `tasks/postenhancement/backend/PE-BE-CS-06.md`
- Role: Architect (`explorer`)
- Scope intent: freeze implementation contract for one atomic backend service integration task.

## Allowlist Boundaries
- In-scope product files for implementation:
  - `backend/app/modules/consulting/service.py`
  - `backend/app/modules/commission/service.py`
  - `backend/app/modules/billing/service.py`
- In-scope evidence outputs:
  - `artifacts/PE-BE-CS-06/**`
- Out of scope:
  - API response contract changes for existing billing endpoints
  - schema/model/migration edits
  - unrelated module refactors

## Integration Goal
- Ensure consulting/search billing flow writes commission records using existing commission rule matching and places records into settleable-candidate lifecycle.
- Preserve existing billing success semantics (non-intrusive commission side effects).

## Trigger Points and Service Call Chain
- Primary trigger point:
  - after successful bill generation from consulting/search fee drafts in billing flow.
- Mandatory chain (conceptual):
  1. consulting module produces draft (`CONSULT_FEE`/`SEARCH_FEE`) via CS-05/CS-04 path.
  2. billing module generates bill from draft(s) and commits bill + bill items.
  3. billing invokes commission apply hook (non-blocking):
     - `billing.service -> commission.service.apply_commission_for_bill(strict=False)`.
  4. billing invokes settleable recompute hook (non-blocking) for affected service case ids:
     - `billing.service -> commission.service.recompute_commission_settleable(strict=False)`.
- Scope note:
  - apply/recompute hook logic must work for consulting/search cases as well as existing normal flows; no special-case breakage.

## Required Behavior
- Commission write behavior:
  - for eligible consulting/search SERVICE bill lines, create or update `t_commission` rows per rule matching contract.
  - no duplicate commission rows for same deterministic key on rerun.
- Settleable-candidate behavior:
  - generated commission rows must be processed through settleable recompute lifecycle.
  - for rows where `force_settle=true` or `wait_pay=false`, candidates can become settleable immediately after recompute.
  - for `wait_pay=true`, rows remain non-settleable until payment progress satisfies threshold per COM-06 contract.

## Non-intrusive Failure Strategy vs Billing Success Path
- Non-intrusive principle:
  - commission apply/recompute failures must not fail a successful billing transaction.
- Required behavior:
  - billing returns success if bill creation itself succeeds.
  - commission apply/recompute exceptions are handled in non-blocking mode with structured logging.
  - no API envelope/status-code change on bill endpoints due to commission side-effect failure.
- Strict mode usage expectation:
  - billing path uses non-strict mode (`strict=False`) for both apply and recompute.
  - strict mode remains available for direct/internal diagnostic use only.

## Error Semantics
- Billing-facing semantics:
  - billing validation and write errors preserve existing billing codes/contracts.
  - commission side-effect failures are converted to non-blocking outcomes and logged.
- Commission service semantics (for reference):
  - strict mode may raise business errors (`400/404/409` as defined by commission contracts).
  - non-strict mode returns failure summary (`FAILED_NON_BLOCKING`) without propagating exception.

## Regression Risks
- Chain regression:
  - missing hook call for consulting/search bills causes no commission records for that business line.
- Candidate regression:
  - missing recompute call leaves newly written commission rows stuck out of settleable lifecycle.
- Intrusive-failure regression:
  - propagated side-effect errors break billing success path.
- Idempotency regression:
  - repeated bill generation/retry creates duplicate commission rows.
- Scope risk:
  - edits outside allowlist violate atomic policy.

## Acceptance Checklist
- [ ] Implementation edits only allowlisted product files:
  - `backend/app/modules/consulting/service.py`
  - `backend/app/modules/commission/service.py`
  - `backend/app/modules/billing/service.py`
- [ ] Consulting/search billing path invokes commission apply hook after bill persistence.
- [ ] Commission records are created/updated for eligible consulting/search SERVICE bill content.
- [ ] Settleable recompute runs for affected case ids so records enter settleable-candidate lifecycle.
- [ ] Billing success path remains non-intrusive to commission side-effect failures.
- [ ] Non-blocking error logs/summaries are emitted for side-effect failures.
- [ ] Existing billing API status/payload contracts remain unchanged.
- [ ] Task verification passes:
  - `cd backend && pytest -q`
- [ ] Lint/format discipline passes:
  - `ruff check --fix .`
  - `ruff format .`
  - `ruff check .`
- [ ] Evidence artifacts are generated for completion claim:
  - `artifacts/PE-BE-CS-06/results.jsonl`
  - `artifacts/PE-BE-CS-06/summary.md`
  - `artifacts/PE-BE-CS-06/git/diff.patch`
