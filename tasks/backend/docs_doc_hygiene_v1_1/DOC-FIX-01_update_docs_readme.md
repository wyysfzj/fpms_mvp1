# Atomic Task (v1.0)

- One task = one file = one responsibility
- No optional behavior
- Update ONLY the single target file specified by the task
- Align docs with MVP1 scope and current repo structure
- If any statement conflicts with current code or authoritative scope (docs/00_mvp1_scope.md), scope wins


# DOC-FIX-01 — Update docs/README.md: execution order + lint-safe API guidance references

## Target File (EXACTLY ONE)
- `docs/README.md`

## Purpose
Make `docs/README.md` the authoritative entrypoint that:
1) States the canonical execution order (Phase 0 → Phase 5) including Phase 3-EXT and Phase 3.5.
2) References the lint-safe Phase 3 API task template + Codex meta prompt to prevent Ruff churn.

## Required Insertions (Authoritative)

### A) Add section: "Execution Order (Authoritative)"
Insert a section that lists phases in strict order and maps to task directories:

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

Add a short gate note:
- Phase 3-EXT and Phase 3.5 MUST NOT change schema.

### B) Add section: "Phase 3 API Implementation (Lint-safe)"
Insert a short section that references:
- Template: `docs/templates/api_atomic_task_template_v4_lint_safe.md`
- Codex meta prompt: `docs/codex_prompts/phase3_api_lint_safe_meta_prompt.txt`
- Checklist: `docs/checklists/phase3_api_lint_safe_checklist.md`

Include one explicit rule:
- Permission dependency must be injected as a parameter (`_perm: None = Depends(require_perm("X.Y"))`) and not in decorator dependencies.

## Done Criteria
1) `docs/README.md` clearly contains both sections above.
2) No references to non-existent files remain.
