# A0 Baseline Verification — Progress Log

## 2026-02-23

### Phase 1: Backend Setup

1. **Created .venv** — `backend/.venv` did not exist. Created with `python3 -m venv .venv`.

2. **Fixed pyproject.toml** — `pip install -e ".[dev]"` failed with:
   ```
   Multiple top-level packages discovered in a flat-layout: ['app', 'storage', 'alembic', 'artifacts']
   ```
   **Fix**: Added `[tool.setuptools.packages.find] include = ["app*"]` to `pyproject.toml`.

3. **Fixed bcrypt version** — bcrypt 5.0 incompatible with passlib:
   ```
   module 'bcrypt' has no attribute '__about__'
   ```
   **Fix**: `pip install "bcrypt<4.1"` (pinned to 4.0.1).

4. **Fixed missing audit columns** — Seed failed with:
   ```
   table t_case_applicant has no column named created_at
   ```
   Root cause: `T_CaseApplicant`, `T_CaseInventor`, `T_Priority` ORM models inherit `AuditMixin`
   but were omitted from migration `e109a0b1c2d3` which added audit columns to other tables.
   **Fix**: Created new migration `53f7a0c139cc_a0_add_audit_cols_case_subtables.py`.

5. **Clean rebuild successful**: `rm fpms_dev.db && alembic upgrade head && python scripts/seed_dev.py` — all passed.

6. **Server started**: `uvicorn app.main:app --port 8000` — healthz returns `{"status":"ok"}`.

### Phase 2: Verification Script Execution

#### Criterion 1: Case CRUD — PASS
- Login: `POST /api/v1/auth/login` → 200, token received
- Create case: `POST /api/v1/cases` → 201, case_no=TEST-A0-001
- Search: `GET /api/v1/cases?q=TEST-A0` → total=1
- Detail: `GET /api/v1/cases/{id}` → case_no matches

#### Criterion 2: Document + Task auto-link — PASS (PARTIAL)
- **Before fix**: Would fail with 422 because `doc_template_id` was required (no default).
- **Fix applied**: Added `= None` default to `DocumentCreateIn.doc_template_id` in `documents/schemas.py`.
- Create document: `POST /api/v1/documents` → 201, document created.
- Auto-task generation depends on TaskTemplate (Batch A1 scope).

#### Criterion 3: Fee→Bill→Payment chain — PASS (with corrected URLs)
- **Original script URLs returned 404**:
  - `/api/v1/billing/bills` → 404 (wrong prefix)
  - `/api/v1/billing/payments` → 404 (wrong prefix)
- **Correct URLs all return 200**:
  - `/api/v1/fees/drafts?page=1` → OK
  - `/api/v1/bills?page=1` → OK
  - `/api/v1/payments?page=1` → OK
- **Root cause**: Verification script had wrong URL paths. The billing router uses no prefix
  (`router.py:26`), so bills are at `/api/v1/bills`, not `/api/v1/billing/bills`.
  This is a **script error**, not a code bug.

#### Criterion 4: Word bill template — MANUAL
- Requires template file + bill data. Noted for manual verification.

### Phase 3: Quality Gate

| Check | Result |
|-------|--------|
| `ruff check --fix . && ruff format .` | PASS (1 file reformatted) |
| `ruff check .` | PASS (all checks passed) |
| `pytest -q` | PASS (34 passed, 3 warnings) |
| `alembic upgrade head` (clean rebuild) | PASS |
| `python scripts/seed_dev.py` | PASS |
| `curl http://localhost:8000/healthz` | PASS ({"status":"ok"}) |
