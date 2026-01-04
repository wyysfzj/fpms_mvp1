# Atomic Task (v1.0)

- One task = one file = one responsibility
- No optional behavior
- Do not change scope
- Follow design docs under `backend/app/modules/**/docs` if present (design wins)


# BE-DBX-0006-02 — Add table T_ClientContact (client contacts)

## Purpose
Create DB table `t_client_contact` to store one-to-many contacts for a client. MVP1 in-scope.

## Preconditions
1) BE-DBX-0006-01 exists in repo (or repo HEAD includes it).
2) Determine current Alembic HEAD revision id.

## Output
Create ONE new Alembic migration file under:
- `backend/alembic/versions/0006_02_create_t_client_contact.py`

## Steps
1) Read current head revision id:
   - Run: `alembic heads`
   - Capture HEAD as `<PREV_HEAD_REV>`.

2) Create a new revision file:
   - Run: `alembic revision -m "0006-02 create t_client_contact"`
   - Rename the generated file to: `0006_02_create_t_client_contact.py`.

3) Edit the migration:
   - Set `down_revision = "<PREV_HEAD_REV>"`.
   - Implement `upgrade()` / `downgrade()` exactly per schema below.

## Table Schema (Authoritative)
Table: `t_client_contact`

Columns:
- `id` BIGINT PK, autoincrement
- `client_id` BIGINT NOT NULL, FK → `t_client.id` ON DELETE CASCADE
- `contact_name` VARCHAR(120) NOT NULL
- `email` VARCHAR(254) NULL
- `phone` VARCHAR(50) NULL
- `title` VARCHAR(120) NULL
- `department` VARCHAR(120) NULL
- `is_primary` BOOLEAN NOT NULL DEFAULT FALSE
- `notes` TEXT NULL
- `created_at` TIMESTAMP NOT NULL DEFAULT now()
- `updated_at` TIMESTAMP NOT NULL DEFAULT now()

Indexes / Constraints:
- Index on `client_id`
- Index on `email` (non-unique)

## Alembic Implementation (Exact)
In `upgrade()`:
- `op.create_table("t_client_contact", ...)`
- `op.create_index("ix_t_client_contact_client_id", "t_client_contact", ["client_id"])`
- `op.create_index("ix_t_client_contact_email", "t_client_contact", ["email"])`

In `downgrade()`:
- drop indexes then drop table

## Done Criteria
1) `alembic upgrade head` succeeds.
2) DB contains `t_client_contact` with all columns above.
3) `alembic downgrade -1` succeeds and removes the table cleanly.
