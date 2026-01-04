# Atomic Task (v1.0)

- One task = one file = one responsibility
- No optional behavior
- Do not change scope
- Follow design docs under `backend/app/modules/**/docs` if present (design wins)


# BE-APIX-99-01 — Seed MVP1 Roles + Permission Codes (Minimal, no Permission table)

## Purpose
Seed MVP1 roles and permission-code mapping without introducing new permission tables.

## Preconditions
1) Auth/RBAC core tables exist and are migrated (e.g., `t_user`, `t_role`, `t_user_role`).
2) Project has an existing seed mechanism (Alembic data migration or startup seeder). Use existing convention.

## Output
Implement exactly ONE seed entrypoint using existing convention.

## Seed Content (Authoritative)
Roles:
- Admin
- Staff

Permission codes (minimum set for Phase 3-EXT endpoints):
- AdminUser.Read, AdminUser.Create, AdminUser.Edit
- SystemParam.Read, SystemParam.Edit
- Template.Read, Template.Create
- LetterHead.Read, LetterHead.Create

Role assignment:
- Admin has all permissions
- Staff has read-only (`*.Read`) unless design docs explicitly grant more

## Rules
- Idempotent: re-running seed does not create duplicates.
- Do not hardcode weak passwords in code. Use env/config or existing policy.

## Done Criteria
1) Fresh DB can be migrated then seeded without manual steps.
2) Admin user can call Phase 3-EXT endpoints (200).
3) Staff user without edit permissions receives 403 for edit endpoints.
