# Phase 3.5 — Business Logic Tasks (MVP1) — Atomic Task Pack v1

This pack adds the MVP1-required business logic after Phase 3 APIs and Phase 3-EXT APIs:

1) Office template rendering: server-side docxtpl → docx download
   - Implement renderer + context builders
   - Wire into Billing print endpoint (already exists in Phase 3: GET /bills/{id}/print)

2) Document → Task auto-generation (minimal)
   - When registering an incoming Office Action document, auto-create tasks from TaskTemplate rules.

Execution prerequisites:
- Phase 0/1/2/3 completed
- Phase 3-EXT `T_SystemParam` / `T_LetterHead` / Template APIs exist if your print uses them
- `require_perm` is implemented and functional

Execution order (do NOT change):
1) BL-DOC-01
2) BL-DOC-02
3) BL-DOC-03
4) BL-DOC-04
5) BL-DOC-05
6) BL-TASK-01
7) BL-TASK-02

Verification after each task:
- ruff check --fix .
- ruff format .
- ruff check .
- PYTHONPATH=backend python -c "from app.main import app; print('OK')"
