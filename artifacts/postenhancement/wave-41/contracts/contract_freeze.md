# Wave 41 Contract Freeze

## Task
- Task ID: `PE-BE-WIRE-01`
- Task file: `tasks/postenhancement/backend/PE-BE-WIRE-01.md`
- Role: Architect (`explorer`)
- Scope intent: freeze one-time API router wiring for newly added backend modules.

## Allowlist Boundaries
- In-scope product file:
  - `backend/app/api/router.py`
- In-scope change type:
  - add missing module router imports
  - add corresponding `api_router.include_router(...)` calls
- In-scope evidence outputs:
  - `artifacts/PE-BE-WIRE-01/**`
- Out of scope:
  - any `backend/app/modules/*/api.py` endpoint changes
  - app/main wiring changes
  - permission, schema, service, model, migration changes
  - edits to files other than `backend/app/api/router.py`

## One-Time Router Wiring Contract
- Add the following module routers to `backend/app/api/router.py` (as available in repository):
  - `app.modules.annuity.api` -> `annuity_router`
  - `app.modules.collections.api` -> `collections_router`
  - `app.modules.commission.api` -> `commission_router`
  - `app.modules.consulting.api` -> `consulting_router`
  - `app.modules.expenses.api` -> `expenses_router`
- Include each exactly once using module-level wiring pattern:
  - `api_router.include_router(<module_router>, tags=[<Tag>])`
- No extra prefix is introduced for these modules (match current convention where module routes already contain full path in endpoint declarations).

## Prefix / Tags Style and Ordering Convention
- Preserve existing style:
  - single top-level `api_router = APIRouter()`
  - one `include_router(...)` call per module
  - `tags` as one-item title-case list.
- Tag naming contract for new modules:
  - `annuity_router` -> `tags=["Annuity"]`
  - `collections_router` -> `tags=["Collections"]`
  - `commission_router` -> `tags=["Commission"]`
  - `consulting_router` -> `tags=["Consulting"]`
  - `expenses_router` -> `tags=["Expenses"]`
- Ordering contract:
  - keep existing include order unchanged
  - append new module includes after existing `billing_router` include
  - append in deterministic module order:
    1. `annuity_router`
    2. `collections_router`
    3. `commission_router`
    4. `consulting_router`
    5. `expenses_router`

## Duplicate-Prevention Contract
- Do not add duplicate imports for the same module router.
- Do not add duplicate `include_router(...)` calls for any router (existing or new).
- Contract check criterion:
  - each router symbol appears once in import section and once in include section.

## Non-Regression Constraints
- Existing routes remain wire-compatible and unchanged.
- Existing tags/prefixes for already wired modules remain unchanged.
- `app/main.py` continues to load `api_router` without additional changes.
- Wiring remains a single-file change in `backend/app/api/router.py`.

## Acceptance Checklist
- [ ] Only `backend/app/api/router.py` is edited.
- [ ] All required new module routers are imported (`annuity/collections/commission/consulting/expenses`).
- [ ] All required new module routers are included exactly once in `api_router`.
- [ ] Existing include order is preserved; new includes are appended in frozen deterministic order.
- [ ] Tag names follow frozen contract and existing style.
- [ ] No duplicate import/include router entries exist.
- [ ] `backend/app/api/router.py` compiles:
  - `cd backend && python3 -m py_compile app/api/router.py`
- [ ] Regression verification passes:
  - `cd backend && pytest -q`
- [ ] Lint/format discipline passes:
  - `ruff check --fix .`
  - `ruff format .`
  - `ruff check .`
- [ ] Evidence artifacts are generated for completion claim:
  - `artifacts/PE-BE-WIRE-01/results.jsonl`
  - `artifacts/PE-BE-WIRE-01/summary.md`
  - `artifacts/PE-BE-WIRE-01/git/diff.patch`
