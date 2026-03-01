# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FPMS (Fee & Practice Management System) MVP1 - A law firm management web application.

- **Backend**: Python 3.11+, FastAPI, SQLAlchemy 2.x, Pydantic 2.x, Alembic
- **Frontend**: Vue 3, TypeScript, Pinia, Element Plus, Vite
- **Database**: SQLite (dev/PoC), PostgreSQL (prod)
- **Document Generation**: docxtpl + python-docx for server-side .docx rendering

## General Rules

- Wait for the user to finish specifying all requirements before starting implementation.
- When user says "add X to the list" or is still describing requirements, pause and confirm the full scope before proceeding.
- Never start coding until the complete task specification is acknowledged.

## Development Commands

### Backend (from `backend/` directory)
```bash
# Setup
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env

# Database
alembic upgrade head              # Run migrations
python scripts/seed_dev.py        # Seed admin user (admin/admin123)

# Run
uvicorn app.main:app --reload --port 8000

# Quality
ruff check --fix . && ruff format .   # Lint and format
pytest -q                              # Run all tests
pytest tests/test_core.py -v           # Run single test file
pytest -k "test_name" -v               # Run specific test
```

### Frontend (from `frontend/` directory)
```bash
npm i && cp .env.example .env
npm run dev                    # Dev server at :5173
npm run build                  # Production build
npm run lint                   # ESLint
npm run typecheck              # TypeScript check
```

### Root Makefile shortcuts
```bash
make dev-backend    # Run FastAPI with reload
make dev-frontend   # Run Vite dev server
make lint           # Lint backend
make test           # Run backend tests
```

## Architecture

### Backend Structure (`backend/app/`)
```
app/
├── main.py              # FastAPI app factory, middleware, exception handlers
├── api/
│   ├── router.py        # Central router aggregating all modules
│   └── deps.py          # Shared dependencies: get_current_user, require_perm()
├── core/                # Cross-cutting: config, errors, security, logging, storage
├── db/
│   ├── session.py       # SQLAlchemy engine/session (SQLite FK pragma enforced)
│   └── mixins.py        # UUIDPrimaryKeyMixin, AuditMixin
└── modules/             # Domain modules (each follows same structure)
    └── <module>/
        ├── api.py       # FastAPI router with endpoints
        ├── models.py    # SQLAlchemy ORM models (T_ prefix convention)
        ├── schemas.py   # Pydantic request/response schemas
        ├── service.py   # Business logic
        └── docs/        # Module-specific design docs
```

**Modules**: auth, rbac, cases, documents, tasks, fees, billing, templates, masterdata/clients, system, admin

### Frontend Structure (`frontend/src/`)
```
src/
├── api/           # Typed API clients (axios) per domain
├── stores/        # Pinia stores (auth.ts, ui.ts)
├── modules/       # Feature modules matching backend
│   └── <module>/
│       └── pages/ # Vue components (pages)
└── router/        # Vue Router configuration
```

### Key Patterns

**Permission Enforcement** - Always use as function parameter, not in decorator:
```python
_perm: None = Depends(require_perm("Case.Create"))
```

**API Prefix**: All endpoints under `/api/v1/`

**ORM Models**: Use `T_` prefix (e.g., `T_User`, `T_Case`), inherit from `UUIDPrimaryKeyMixin` and `AuditMixin`

**Error Handling**: Use `raise_business_error(code, message, status_code=...)` from `app.core.errors`

## Critical Constraints (from AGENTS.md)

1. **Atomic Tasks**: One task = one endpoint/service/doc change per execution
2. **SQLite Compatibility Required**:
   - Use `server_default=sa.text("CURRENT_TIMESTAMP")` for timestamps
   - No PG-only functions (uuid_generate_v4, ILIKE, JSONB, ARRAY)
   - UUIDs generated in app code, stored as TEXT
   - FK pragma enforced in session.py
3. **Forward-only Migrations**: No `alembic downgrade`. For clean rebuild: delete `.db` file, then `alembic upgrade head`
4. **204 No Content**: Must NOT return body or define response_model
5. **Seeding**: Run `python scripts/seed_dev.py` after any DB rebuild

## Database Migrations

- Never trust `alembic autogenerate` output blindly — always review generated migrations before applying.
- When adding mixins (e.g., AuditMixin) to existing tables, ensure migration includes ALL new columns for ALL affected tables including sub-tables.
- If autogenerate produces destructive operations (DROP TABLE, DROP COLUMN), discard it and write the migration manually.
- Always test migrations on a fresh DB before considering them done: `rm -f fpms_dev.db && alembic upgrade head && python scripts/seed_dev.py`
- Use `batch_alter_table` for SQLite column additions; check existing cols for idempotency.

## Testing

Tests use pytest with isolated in-memory SQLite. Key fixtures in `tests/conftest.py`:
- `client`: TestClient with migrated/seeded test DB
- `auth_headers`: Dict with Bearer token for admin user

**Conventions:**
- Use function-scoped DB fixtures (not session-scoped) to avoid cross-test data conflicts like duplicate unique constraint violations.
- Do not mark tests as `xfail` unless there is a confirmed known failure — if tests pass, remove xfail markers immediately.
- Always run the full test suite after changes: `pytest --tb=short`
- Generate unique test data (e.g., unique case_no per test) to avoid collisions across tests.

## URLs

- Frontend: http://localhost:5173
- Backend API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/healthz

## Agent Team — MANDATORY Rules

When the user prompt contains keywords like "agent team", "TeamCreate", "team", "swarm", or
"parallelize", the following rules are **BLOCKING** — you MUST NOT skip them:

### 0. Delegation is Non-Negotiable
- When instructed to use agent teams, ALWAYS delegate work to spawned sub-agents via Task tool.
- **Never do implementation work directly as team lead.** The lead coordinates; agents implement.
- Each agent must produce required artifacts and pass quality gates before marking tasks complete.
- If agent spawning fails, retry once. If it fails again, log the failure in `findings.md` and proceed with direct execution as a documented fallback — not silently.

### 1. Create Team First
- Call `TeamCreate` BEFORE writing any code
- Team name should match the batch (e.g., `a1-batch`, `a2-batch`)

### 2. Artifacts Directory
- Create `artifacts/{batch_name}/` at the start
- ALL planning and review files go here, not in working directories
- Required files:
  - `task_plan.md` — task decomposition, assignments, dependency graph
  - `findings.md` — bugs, discoveries, deviations found during execution
  - `progress.md` — real-time task status tracker
  - `review_report.md` — generated by review-agent at the end

### 3. Team Composition (minimum)
| Role | Agent Type | Responsibility |
|------|-----------|---------------|
| Architect / Lead | main thread | Plan → decompose → assign → coordinate |
| Impl Agent(s) | general-purpose | Execute code changes (1-3 agents based on parallelism) |
| Review Agent | general-purpose | Read all changed files, verify acceptance criteria, write review_report.md |

### 4. Execution Flow
```
1. Lead creates artifacts/{batch}/ and writes task_plan.md
2. Lead creates TaskCreate items for each sub-task
3. Lead spawns teammate agents via Task tool with team_name
4. Teammates claim tasks, implement, mark complete
5. Lead spawns review-agent after all impl tasks done
6. Review agent reads code, checks acceptance criteria, writes review_report.md
7. Lead writes final progress.md and sends shutdown to team
```

### 5. Cross-Agent Coordination
- When backend and frontend agents need to negotiate (e.g., API contracts), ensure one agent proposes first and the other responds — do NOT have both agents wait on each other simultaneously.
- Team lead must explicitly sequence the handoff: Architect → Backend → Frontend (or vice versa).
- If an agent goes idle during cross-communication, the lead must nudge it with an explicit message rather than waiting.

### 6. Planning-with-files
- 所有 Agent 必须使用 planning-with-files 插件进行结构化规划
- Architect Agent 启动时必须先执行 /plan
- 所有 Teammate 在行动前必须阅读 task_plan.md
- 发现 bug 或新发现必须记录到 findings.md

### 7. Enforcement
- If the agent skips TeamCreate when the prompt requests it → this is a process violation
- Single-agent execution is ONLY acceptable when the prompt does NOT mention team/swarm/parallelize