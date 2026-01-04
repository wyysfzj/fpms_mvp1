# Atomic Task (v1.0)

- One task = one file = one responsibility
- No optional behavior
- Do not change scope
- Follow design docs under `backend/app/modules/**/docs` if present (design wins)


# BE-DBX-0007-01 — Add table T_SystemParam (global settings)

## Purpose
Create DB table `t_system_param` for MVP1 global settings (Settings minimal). MVP1 in-scope.

## Preconditions
1) Previous migrations (including 0006-01 and 0006-02) are present.
2) Determine current Alembic HEAD revision id.

## Output
Create ONE new Alembic migration file under:
- `backend/alembic/versions/0007_01_create_t_system_param.py`

## Steps
1) Read current head revision id:
   - Run: `alembic heads`
   - Capture HEAD as `<PREV_HEAD_REV>`.

2) Create a new revision file:
   - Run: `alembic revision -m "0007-01 create t_system_param"`
   - Rename to: `0007_01_create_t_system_param.py`.

3) Edit the migration:
   - Set `down_revision = "<PREV_HEAD_REV>"`.
   - Implement `upgrade()` / `downgrade()` exactly per schema below.

## Table Schema (Authoritative)
Table: `t_system_param`

Columns:
- `id` BIGINT PK, autoincrement
- `param_key` VARCHAR(120) NOT NULL
- `param_value` TEXT NOT NULL
- `value_type` VARCHAR(20) NOT NULL DEFAULT "string"  (allowed: string, int, float, bool, json)
- `description` TEXT NULL
- `is_secret` BOOLEAN NOT NULL DEFAULT FALSE
- `updated_by_user_id` BIGINT NULL, FK → `t_user.id` ON DELETE SET NULL
- `updated_at` TIMESTAMP NOT NULL DEFAULT now()
- `created_at` TIMESTAMP NOT NULL DEFAULT now()

Constraints / Indexes:
- UNIQUE(`param_key`)
- Index on `value_type`

## Alembic Implementation (Exact)
In `upgrade()`:
- `op.create_table("t_system_param", ...)`
- `sa.UniqueConstraint("param_key", name="uq_t_system_param_param_key")`
- `op.create_index("ix_t_system_param_value_type", "t_system_param", ["value_type"])`

In `downgrade()`:
- drop index then drop table

## Done Criteria
1) `alembic upgrade head` succeeds.
2) `t_system_param` exists with unique constraint on `param_key`.
3) `alembic downgrade -1` succeeds cleanly.
