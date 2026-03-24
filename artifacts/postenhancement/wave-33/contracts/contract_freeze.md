# Wave 33 Contract Freeze

## Task
- Task ID: `PE-BE-CS-01`
- Task file: `tasks/postenhancement/backend/PE-BE-CS-01.md`
- Role: Architect (`explorer`)
- Scope intent: freeze implementation contract for one atomic backend endpoint task.

## Allowlist Boundaries
- In-scope product files for implementation:
  - `backend/app/modules/consulting/api.py`
  - `backend/app/modules/consulting/service.py`
  - `backend/app/modules/cases/service.py`
- In-scope evidence outputs:
  - `artifacts/PE-BE-CS-01/**`
- Out of scope:
  - changes outside allowlist (including unrelated `/cases` API behavior changes)
  - schema/model/migration edits
  - router rewiring beyond first-time consulting module inclusion requirements

## Endpoint Contract (`POST /consulting/cases`)
- Method/path:
  - `POST /consulting/cases`
- Success status:
  - `201 Created`
- Success response shape (minimum):
  - `id`
  - `case_no`
  - `case_type`
  - `status`
  - `client_id`
  - `title_cn`
  - `primary_agent_id`
  - `recv_date`
  - `created_at` (or module-equivalent audit timestamp)

## Accepted `case_type` and Dedicated Validation
- Accepted values (strict):
  - `CONSULTING`
  - `SEARCH`
- Any other `case_type`:
  - reject with `400`.
- Explicit required fields (dedicated minimum for consulting/search creation):
  - `case_no` (required, non-empty, unique)
  - `case_type` (required, must be one of accepted values above)
  - `client_id` (required, non-empty)
  - `title_cn` (required, non-empty project title)
  - `primary_agent_id` (required, non-empty project owner)
  - `recv_date` (required date; project intake/start context)
- Additional validation:
  - whitespace-trim required string fields before validation.
  - keep validation deterministic; same input must produce same validation outcome.

## Permission Contract
- Required permission:
  - `ConsultingCase.Create`
- Mandatory parameter-injection pattern:
  - `_perm: None = Depends(require_perm("ConsultingCase.Create"))`
- Do not use decorator-level `dependencies=[...]` for permission checks.

## Delegation Strategy and `/cases` Non-impact Contract
- Contracted architecture choice:
  - implement dedicated endpoint path in consulting module (`/consulting/cases`).
  - creation flow may reuse shared persistence helpers in `cases/service.py`, but must not alter existing `/cases` endpoint request/response contract.
- Non-impact requirement:
  - existing `POST /cases` behavior remains backward-compatible for current consumers.
  - no forced new required fields on existing `/cases` create flow.

## Success / Error Semantics
- `201`:
  - consulting/search case created successfully with contracted response shape.
- `400`:
  - invalid `case_type`
  - missing/blank dedicated required fields
  - other deterministic business validation failures.
- `409`:
  - duplicate `case_no`.
- `422`:
  - request schema/type validation failures.
- `401` / `403`:
  - unauthenticated / permission denied.
- Preserve existing BusinessError/FastAPI envelope conventions.

## Regression Risks
- Scope regression:
  - changing existing `/cases` semantics breaks baseline clients.
- Validation regression:
  - missing dedicated required-field checks permits invalid consulting/search cases.
- Case-type drift:
  - accepting unsupported case types under `/consulting/cases` creates ambiguous routing.
- Permission regression:
  - wrong permission code or injection method breaks authorization guarantees.
- Allowlist regression:
  - touching non-allowlisted files violates atomic policy.

## Acceptance Checklist
- [ ] Implementation edits only allowlisted product files:
  - `backend/app/modules/consulting/api.py`
  - `backend/app/modules/consulting/service.py`
  - `backend/app/modules/cases/service.py`
- [ ] `POST /consulting/cases` endpoint exists and supports creation flow.
- [ ] `case_type` is restricted to `CONSULTING`/`SEARCH`.
- [ ] Dedicated required-field validation is enforced for:
  - `case_no`, `case_type`, `client_id`, `title_cn`, `primary_agent_id`, `recv_date`
- [ ] Permission enforced with parameter-injected:
  - `Depends(require_perm("ConsultingCase.Create"))`
- [ ] Existing `/cases` endpoint contract remains unchanged.
- [ ] Success/error semantics align with frozen `201/400/409/422` expectations.
- [ ] Task verification passes:
  - `cd backend && pytest -q`
- [ ] Lint/format discipline passes:
  - `ruff check --fix .`
  - `ruff format .`
  - `ruff check .`
- [ ] Evidence artifacts are generated for completion claim:
  - `artifacts/PE-BE-CS-01/results.jsonl`
  - `artifacts/PE-BE-CS-01/summary.md`
  - `artifacts/PE-BE-CS-01/git/diff.patch`
