# Wave 37 Contract Freeze

## Task
- Task ID: `PE-BE-CS-05`
- Task file: `tasks/postenhancement/backend/PE-BE-CS-05.md`
- Role: Architect (`explorer`)
- Scope intent: freeze implementation contract for one atomic backend endpoint task.

## Allowlist Boundaries
- In-scope product files for implementation:
  - `backend/app/modules/consulting/api.py`
  - `backend/app/modules/consulting/service.py`
- In-scope evidence outputs:
  - `artifacts/PE-BE-CS-05/**`
- Out of scope:
  - `backend/app/modules/fees/service.py` behavior changes (already frozen by `PE-BE-CS-04`)
  - schema/model/migration edits
  - unrelated module refactors

## Endpoint Contract (`POST /consulting/fee-drafts`)
- Method/path:
  - `POST /consulting/fee-drafts`
- Success status:
  - `201 Created`
- Request body:
  - mode-driven payload for consulting/search fee draft generation.

## Request Schema Contract (Mode FIXED/HOURLY/HYBRID)
- Common required fields:
  - `case_id` (required)
  - `mode` (required; one of `FIXED`, `HOURLY`, `HYBRID`)
- Common optional fields:
  - `currency` (optional)
  - `misc_lines` (optional list of misc/reimbursable lines)
- Mode-specific inputs:
  - `FIXED`:
    - required `fixed_fee` (> 0)
    - `hourly_lines` must be absent or empty
  - `HOURLY`:
    - required non-empty `hourly_lines`
    - each hourly line requires:
      - `fee_code`
      - `fee_name`
      - `hours` (> 0)
      - `hourly_rate` (>= 0)
      - optional `trace_key`, `remark`
    - `fixed_fee` optional/ignored
  - `HYBRID`:
    - required non-empty `hourly_lines`
    - optional `fixed_fee` (>= 0)
    - total generated amount must be > 0

## Delegation Contract (to `PE-BE-CS-04`)
- API handler must delegate to consulting service entrypoint.
- Consulting service entrypoint must delegate to CS-04 strategy contract:
  - `generate_consulting_fee_draft_strategy(...)`.
- Endpoint must not re-implement amount formulas; it must rely on CS-04 deterministic strategy logic.
- Any CS-04 BusinessError should propagate as-is through standard error envelope mapping.

## Permission Contract
- Required permission:
  - `ConsultingFeeDraft.Create`
- Mandatory parameter-injection pattern:
  - `_perm: None = Depends(require_perm("ConsultingFeeDraft.Create"))`
- Do not use decorator-level `dependencies=[...]` for permission checks.

## Response Shape Contract (Generated Draft Summary)
- Success payload should return generated draft summary from service, including:
  - `draft_id`
  - `draft_type` (`CONSULT_FEE` or `SEARCH_FEE`)
  - `mode`
  - `currency`
  - `totals`:
    - `total_gov`
    - `total_service`
    - `total_misc`
    - `amount`
  - `items` (traceable line-level breakdown)
  - `created_line_count`
- Line-level item summary fields:
  - `item_id`
  - `fee_code`
  - `fee_name`
  - `fee_type`
  - `quantity`
  - `unit_price`
  - `amount`
  - `trace_key`
  - `remark`

## Success / Error Semantics
- `201`:
  - draft successfully generated from mode contract.
- `400`:
  - mode/input validation failures (invalid mode, missing fixed/hourly inputs, invalid numeric boundaries).
- `404`:
  - `case_id` not found.
- `409`:
  - conflict on open draft scope (same case/type/currency) or other strategy conflict conditions.
- `422`:
  - request schema/type validation failures.
- `401` / `403`:
  - unauthenticated / permission denied.
- Preserve existing BusinessError/FastAPI envelope conventions.

## Regression Risks
- Delegation regression:
  - bypassing CS-04 strategy in API/service layer can break deterministic formulas and traceability.
- Mode-validation regression:
  - insufficient request-mode checks can generate invalid fee drafts.
- Permission regression:
  - wrong permission code/injection pattern weakens access control.
- Contract regression:
  - missing summary/totals/items fields breaks API consumers and future CS workflow.
- Scope risk:
  - edits outside allowlist violate atomic policy.

## Acceptance Checklist
- [ ] Implementation edits only allowlisted product files:
  - `backend/app/modules/consulting/api.py`
  - `backend/app/modules/consulting/service.py`
- [ ] `POST /consulting/fee-drafts` endpoint implemented.
- [ ] Request schema supports `FIXED`/`HOURLY`/`HYBRID` with required mode-specific inputs.
- [ ] Endpoint delegates to CS-04 service strategy contract (no duplicate formula logic in API layer).
- [ ] Permission enforced with parameter-injected:
  - `Depends(require_perm("ConsultingFeeDraft.Create"))`
- [ ] Success response returns generated draft summary with totals and traceable line items.
- [ ] Error semantics align with `201/400/404/409/422` contract (+ auth `401/403`).
- [ ] Task verification passes:
  - `cd backend && pytest -q`
- [ ] Lint/format discipline passes:
  - `ruff check --fix .`
  - `ruff format .`
  - `ruff check .`
- [ ] Evidence artifacts are generated for completion claim:
  - `artifacts/PE-BE-CS-05/results.jsonl`
  - `artifacts/PE-BE-CS-05/summary.md`
  - `artifacts/PE-BE-CS-05/git/diff.patch`
