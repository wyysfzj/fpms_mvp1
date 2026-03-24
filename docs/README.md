# Global Design Docs

Start here:

1. `00_mvp1_scope.md` — what MVP1 includes/excludes
2. `01_information_architecture.md` — pages/menu (B/S IA)
3. `02_permissions_rbac.md` — MVP1 RBAC model, core permission vocabulary, and menu-to-role expectations
4. `03_database_mvp1_subset.md` — MVP1 DB subset (from SPEC) + indexes
5. `04_backend_architecture.md` — backend layering & conventions
6. `05_frontend_architecture.md` — frontend layering & conventions
7. `06_deployment.md` — Docker + config strategy
8. `07_db_ddl_and_sqlite.md` — database definition
9. `TODO.md` — decisions pending / open questions

RBAC contract split: `02_permissions_rbac.md` owns the high-level RBAC model and role/menu expectations, `permissions_matrix.md` owns endpoint-to-permission mapping for API tasks, including export routes, and `backend/app/modules/rbac/service.py` is the executable runtime seed.

## Execution Order (Authoritative)

- Phase 0 — DB Bootstrap (0001–0005): `backend/alembic/versions/`
- Phase 0-EXT — DB Bootstrap Extension (0006/0007, if required): `tasks/backend/db_bootstrap_ext/`
- Phase 1 — Core Wiring & Auth: BE-00 / BE-01 tasks
- Phase 2 — ORM Parity: `tasks/backend/models_from_migrations/`
- Phase 3 — Domain APIs (v4 unified): `tasks/backend/apis/`
- Phase 3-EXT — MVP1 API Extensions: `tasks/backend/apis_ext/`
- Phase 3.5 — Business Logic (MVP1 Required): `tasks/backend/business_logic/`
  - Bill print docx (docxtpl)
  - Task print docx (docxtpl)
  - Document → Task auto-generation on OA register
- Phase 4 — Frontend tasks
- Phase 5 — Integration / Smoke Test

Gate note: Phase 3-EXT and Phase 3.5 MUST NOT change schema.

## Phase 3 API Implementation (Lint-safe)

Use these references when implementing Phase 3 APIs:
- Template: `docs/templates/api_atomic_task_template_v4_lint_safe.md`
- Codex meta prompt: `docs/codex_prompts/phase3_api_lint_safe_meta_prompt.txt`
- Checklist: `docs/checklists/phase3_api_lint_safe_checklist.md`

Rule: permission dependency must be injected as a parameter (`_perm: None = Depends(require_perm("X.Y"))`) and not in decorator dependencies.
