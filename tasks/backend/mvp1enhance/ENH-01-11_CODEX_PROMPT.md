# Universal Atomic Execution Prompt (v2) — ENH-01-11 (FPMS MVP1)

You are a coding agent executing **exactly ONE** atomic task.

## Task File (Authoritative)
- `tasks/backend/mvp1enhance/ENH-01-11.md`

## Goal
Relocate `T_RolePerm` ORM definition to `backend/app/modules/auth/models.py` (align with existing `T_Role`),
and convert `backend/app/modules/rbac/models.py` into a minimal re-export shim to avoid duplicate ORM model definitions.

## Hard Rules (MUST FOLLOW)
- Execute ONLY ENH-01-11.
- Modify ONLY the allowlisted files.
- Do NOT add migrations in this task.
- Do NOT change any endpoints/routers.
- Do NOT change auth/RBAC behavior.
- Do NOT introduce new dependencies.
- Keep SQLite-safe defaults (`CURRENT_TIMESTAMP`) and UUID/TEXT PK.

## Allowed Files (Strict Allowlist)
- `backend/app/modules/auth/models.py`
- `backend/app/modules/rbac/models.py`

If any other file is required, STOP and report.

## Required Steps
1) Ensure `T_RolePerm` is defined in `auth/models.py` as the single authoritative ORM model.
2) Replace `rbac/models.py` with a minimal shim re-exporting `T_RolePerm` from `app.modules.auth.models`.
3) Run verification commands (scoped to these files only).

## Verification (MUST RUN)
```bash
cd backend
ruff check app/modules/auth/models.py app/modules/rbac/models.py
ruff format app/modules/auth/models.py app/modules/rbac/models.py
python3 -m py_compile app/modules/auth/models.py
python3 -m py_compile app/modules/rbac/models.py
cd ..
```

## Evidence (MUST PROVIDE)
- Command outputs
- `git diff` showing ONLY the two allowlisted files changed
- Confirmation there is only one ORM definition of `T_RolePerm`

## STOP Contract
STOP if you need to edit migrations or any file outside allowlist.
