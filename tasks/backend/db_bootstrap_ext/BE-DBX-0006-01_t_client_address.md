# Atomic Task (v1.0)

- One task = one file = one responsibility
- No optional behavior
- Do not change scope
- Follow design docs under `backend/app/modules/**/docs` if present (design wins)


# BE-DBX-0006-01 — Add table T_ClientAddress (client addresses)

## Purpose
Create DB table `t_client_address` to store one-to-many addresses for a client. MVP1 in-scope.

## Preconditions
1) Current DB migrations 0001–0005 already exist and `alembic upgrade head` succeeds.
2) Determine current Alembic HEAD revision id (must be used as `down_revision`).

## Output
Create ONE new Alembic migration file under:
- `backend/alembic/versions/0006_01_create_t_client_address.py` (or equivalent naming that keeps 0006-01 ordering)

## Steps
1) Read current head revision id:
   - Run: `alembic heads`
   - Capture the single HEAD revision id as `<PREV_HEAD_REV>`.

2) Create a new revision file:
   - Run: `alembic revision -m "0006-01 create t_client_address"`
   - Locate the generated file under `backend/alembic/versions/`.
   - Rename it to: `0006_01_create_t_client_address.py`.

3) Edit the migration file:
   - Set `down_revision = "<PREV_HEAD_REV>"`.
   - Implement `upgrade()` to create table `t_client_address`.
   - Implement `downgrade()` to drop table `t_client_address`.

## Table Schema (Authoritative)
Table: `t_client_address`

Columns:
- `id` BIGINT PK, autoincrement
- `client_id` BIGINT NOT NULL, FK → `t_client.id` ON DELETE CASCADE
- `address_type` VARCHAR(32) NOT NULL
- `line1` VARCHAR(255) NOT NULL
- `line2` VARCHAR(255) NULL
- `city` VARCHAR(100) NULL
- `state` VARCHAR(100) NULL
- `postal_code` VARCHAR(20) NULL
- `country` VARCHAR(2) NULL
- `is_primary` BOOLEAN NOT NULL DEFAULT FALSE
- `created_at` TIMESTAMP NOT NULL DEFAULT now()
- `updated_at` TIMESTAMP NOT NULL DEFAULT now()

Indexes / Constraints:
- Index on `client_id`
- Do NOT add unique constraints

## Alembic Implementation (Exact)
In `upgrade()`:
- `op.create_table("t_client_address", ...)`
- `sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True)`
- `sa.Column("client_id", sa.BigInteger(), sa.ForeignKey("t_client.id", ondelete="CASCADE"), nullable=False)`
- Define all other columns exactly as schema above
- `op.create_index("ix_t_client_address_client_id", "t_client_address", ["client_id"])`

In `downgrade()`:
- `op.drop_index("ix_t_client_address_client_id", table_name="t_client_address")`
- `op.drop_table("t_client_address")`

## Done Criteria
1) `alembic upgrade head` succeeds.
2) DB contains table `t_client_address` with all columns above.
3) `alembic downgrade -1` succeeds and removes the table cleanly.
