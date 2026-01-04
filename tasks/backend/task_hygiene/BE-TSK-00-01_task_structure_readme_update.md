# Atomic Task (v1.0)

- One task = one file = one responsibility
- No optional behavior
- Do not change scope
- Follow design docs under `backend/app/modules/**/docs` if present (design wins)


# BE-TSK-00-01 — Task Hygiene: add missing directories + update README guidance

## Purpose
Align `tasks/backend/` with authoritative task entrypoints and execution order.

## Output
Update exactly ONE file:
- `tasks/backend/README.md`

## Required README Content
Include an “Execution Order” section:
1) `tasks/backend/db_bootstrap_ext/`
2) `tasks/backend/models_from_migrations/`
3) `tasks/backend/apis/`
4) `tasks/backend/apis_ext/`
5) `tasks/backend/business_logic/` (when added)

Also include “Deprecated Tasks” guidance:
- Any root-level coarse tasks that overlap with `models_from_migrations/` are deprecated and must not be executed.

## Done Criteria
README clearly points implementers to correct directories and order.
