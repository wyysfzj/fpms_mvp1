# Wave 40 Contract Freeze

## Task
- Task ID: `PE-BE-QA-02`
- Task file: `tasks/postenhancement/backend/PE-BE-QA-02.md`
- Role: Architect (`explorer`)
- Scope intent: freeze global pagination-cap contract for backend list endpoints.

## Allowlist Execution Boundaries
- In-scope product files:
  - `backend/app/modules/*/api.py`
- In-scope change type:
  - list endpoint query parameter constraints only (`page_size` upper bound).
- In-scope evidence outputs:
  - `artifacts/PE-BE-QA-02/**`
- Out of scope:
  - service/repository logic changes
  - response schema changes
  - route/method/permission changes
  - sorting/filter business behavior changes
  - schema/migration/model edits

## List Endpoint Definition and Scope
- `List endpoint` for this task is defined as:
  - HTTP `GET` endpoint in `backend/app/modules/*/api.py`
  - returns a collection view
  - currently exposes both `page` and `page_size` query parameters.
- Endpoints that return lists but do not expose `page_size` are explicitly out of scope for Wave 40 (no new pagination contract introduced in this task).

### Paginated List Endpoints in Scope (Current Inventory)
- `GET /admin/users`
- `GET /annuity/tasks`
- `GET /bills`
- `GET /payments`
- `GET /cases`
- `GET /cases/export`
- `GET /dunning`
- `GET /commission`
- `GET /commission/rules`
- `GET /doc-templates`
- `GET /documents`
- `GET /expenses`
- `GET /fees/drafts`
- `GET /fees/rates`
- `GET /tasks`
- `GET /tasks/today`
- `GET /templates`

### Explicitly Out of Scope in This Task (Examples)
- `GET /task-templates` (list without page/page_size)
- `GET /letterheads` (list without page/page_size)
- `GET /system/params` (list without page/page_size)
- `GET /tasks/{task_id}/logs` (list without page/page_size)

## Pagination Cap Contract (`page_size <= 100`)
- For every in-scope endpoint, freeze parameter constraint as:
  - `page_size: int = Query(default=<existing_default>, ge=1, le=100)`
- Default value must remain unchanged unless a specific endpoint already uses a different default.
- `page` behavior remains unchanged:
  - `page: int = Query(default=1, ge=1)` (or existing equivalent).
- Cap enforcement is framework-level validation:
  - requests with `page_size > 100` return `422` validation error (existing envelope semantics).

## Non-Regression Rules
- Do not change returned payload structure (`items/page/page_size/total` or module equivalent).
- Do not change filtering, sorting, counting, or query-building logic.
- Do not alter endpoint names, HTTP methods, auth/permission behavior, or aliases.
- Do not change existing success status codes.
- Do not convert validation failures from `422` to custom `400`.
- Keep imports minimal and lint-clean if endpoint signatures are touched.

## Acceptance Checklist
- [ ] Changes are limited to allowlist pattern `backend/app/modules/*/api.py`.
- [ ] Every in-scope paginated list endpoint has `page_size` constrained with `le=100`.
- [ ] Existing `page_size` defaults are preserved.
- [ ] Non-paginated list endpoints remain unchanged in this wave.
- [ ] Response envelopes and success semantics remain unchanged.
- [ ] Validation semantics remain framework-native (`422` for out-of-range `page_size`).
- [ ] Verification passes:
  - `cd backend && pytest -q`
- [ ] Lint/format discipline passes:
  - `ruff check --fix .`
  - `ruff format .`
  - `ruff check .`
- [ ] Evidence artifacts are generated for completion claim:
  - `artifacts/PE-BE-QA-02/results.jsonl`
  - `artifacts/PE-BE-QA-02/summary.md`
  - `artifacts/PE-BE-QA-02/git/diff.patch`
