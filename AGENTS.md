# AGENTS — FPMS MVP1 (Authoritative)

This file defines the authoritative execution rules for Codex/Agent working on this repository.
Agent MUST follow these rules without exception.

---

## 1) Atomic Task Discipline

- Implement EXACTLY ONE task file per execution.
- One task = one endpoint OR one service OR one doc change.
- Do NOT implement multiple endpoints in one run.
- Do NOT proactively refactor unrelated code.
- When asked “which task to implement”, always request/confirm the exact task file path.

---

## 2) Phase Constraints

### Phase 3 (Domain APIs)
- No database schema changes.
- No Alembic migration edits (except Phase 0-EXT compatibility fixes explicitly requested).
- Use existing ORM models only.
- Implement endpoints only in module-level `api.py`.
- Preserve existing response envelope conventions.

### Phase 3.1 (API Extensions — `tasks/backend/apis_ext/`)
- Same constraints as Phase 3.
- Only implement tasks under `tasks/backend/apis_ext/`.

### Phase 3.5 (Business Logic — `tasks/backend/business_logic/`)
- Service-layer logic only.
- No schema changes.
- Allowed:
  - docxtpl rendering
  - context builders
  - Document → Task auto-generation
- API wiring may be updated ONLY where explicitly required by the task.

---

## 3) Router Wiring (Module-level, One-time)

- Router wiring is module-level and one-time.
- Do NOT rewire routers when adding endpoints within an already-wired module.
- Only add `include_router(...)` when entering a module for the FIRST time.
- Router wiring changes are limited to `backend/app/api/router.py` unless a task explicitly requires otherwise.

---

## 4) Authorization & Permission Enforcement

- Permission enforcement is mandatory for all protected endpoints.
- NEVER use `Depends(require_perm(...))` inside decorator `dependencies=[...]`.
- ALWAYS inject permission as a function parameter:

```python
_perm: None = Depends(require_perm("Title.Action"))
```

- Permission codes MUST follow `Title.Action` naming.

---

## 5) FastAPI Status Code Semantics (MANDATORY)

### 204 No Content
- MUST NOT return a response body.
- MUST NOT define `response_model` for 204 routes.
- Handler must end with:
  - `return None` OR
  - `return Response(status_code=204)`

### 201 Created
- MUST return created resource or its identifier (unless task says otherwise).

### GET
- MUST NOT require a request body.

### Error semantics (use consistently)
- 400: business validation failure (explicit message)
- 401: unauthenticated
- 403: permission denied
- 404: resource not found
- 409: conflict / missing configuration
- 422: validation error (FastAPI)

Before finishing any task, self-check:
- Is the response body compatible with declared `status_code`?

---

## 6) Ruff / Lint Discipline

Code MUST pass:
- `ruff check --fix .`
- `ruff format .`
- `ruff check .`

Imports must remain minimal and ordered; remove unused imports.

---

## 7) Response Envelope Discipline

- Do NOT invent new response envelopes.
- Follow existing module conventions.

---

## 8) SQLite PoC Compatibility (MVP1 REQUIRED)

MVP1 PoC uses SQLite. Code and migrations MUST remain SQLite-compatible.

### 8.1 Timestamp defaults (REQUIRED)
- Do NOT use `now()` in migrations or `server_default`.
- Use `server_default=sa.text("CURRENT_TIMESTAMP")` for created_at/updated_at.

### 8.2 Autoincrement primary keys (REQUIRED)
- SQLite autoincrement works only with `INTEGER PRIMARY KEY`.
- For PoC, prefer `Integer` PK everywhere.
- Do NOT use BigInteger PK expecting autoincrement.
- Keep PK/FK types aligned (e.g., do NOT point String PKs from BigInteger FKs).
- If UUID PK is used, UUID MUST be generated in application code (`uuid4`) and stored as TEXT.

### 8.3 Foreign keys must be enabled (REQUIRED)
- SQLite foreign keys are not guaranteed unless enabled.
- Engine creation MUST set `PRAGMA foreign_keys=ON` on every connection (SQLAlchemy connect event).

### 8.4 Dialect-specific SQL is prohibited in PoC
Do NOT introduce PG-only functions/types:
- `uuid_generate_v4()`, `gen_random_uuid()`
- `ILIKE`
- `date_trunc(...)`, `timezone(...)`, `interval '...'`
- `JSONB`, `ARRAY`, `CITEXT`
If needed, implement SQLite-safe alternatives (lower()+LIKE; app-side date math; store JSON as TEXT).

### 8.5 Do not rely on RETURNING for correctness
- Do not assume RETURNING support; use `session.flush()` to obtain PK values after insert.

### 8.6 Concurrency note (PoC)
- SQLite uses file locks. Keep write transactions short.
- If “database is locked” occurs, prefer reducing concurrency; WAL/retry may be considered later.

---

## 9) Forward-only Migrations Policy

Some migrations intentionally do NOT support downgrade.
- Do NOT attempt to rely on `alembic downgrade base` in dev workflows.
- For clean rebuild on SQLite dev:
  1) Delete the SQLite db file (and -wal/-shm if present)
  2) Run `alembic upgrade head`

---

## 10) Seeding (MVP1 Required)

- Seeding MUST be idempotent and bootstrap-safe.
- Avoid deadlocks: seed must be runnable when no users OR no Admin role exists.
- After any SQLite DB rebuild, seed MUST be re-run and token must be refreshed (log in again).

---

## 11) Required Agent Output (End of each execution)

Agent MUST explicitly state:
- Which task/runbook was executed
- Which file(s) were modified
- Verification commands + expected status codes

---

## 12) Evidence & Gates (EOS Bootstrap — MVP1 Enhancement)

To make AI-first execution auditable and deterministic, every task MAY create/update evidence under:

- `artifacts/<TASK-ID>/**`

This is **non-product output** and is explicitly allowed for all tasks, even when a task’s code scope is restricted to a single source file.

Rules:
- Do NOT store secrets/PII in artifacts logs.
- Artifacts should be generated by wrapper scripts (see `scripts/evidence_run.sh`).
- Evidence is required for tasks that claim completion:
  - `artifacts/<TASK-ID>/results.jsonl` (commands + rc)
  - `artifacts/<TASK-ID>/summary.md` (human-readable evidence summary)
  - `artifacts/<TASK-ID>/git/diff.patch` (scoped diff)

Gates:
- Task Gate: `./scripts/task_validate.sh <TASK-ID>`
- Release Gate: `./scripts/release_gate.sh`
