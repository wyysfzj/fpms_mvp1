# Atomic Task (v1.0)

- One task = one file = one responsibility
- No optional behavior
- Do not change scope
- Follow design docs under `backend/app/modules/**/docs` if present (design wins)


# BE-DBX-0007-02 — Add table T_LetterHead (letterhead metadata)

## Purpose
Create DB table `t_letter_head` for letterhead/header/footer metadata used by template rendering. MVP1 in-scope.

## Preconditions
1) BE-DBX-0007-01 exists in repo (or repo HEAD includes it).
2) Determine current Alembic HEAD revision id.

## Output
Create ONE new Alembic migration file under:
- `backend/alembic/versions/0007_02_create_t_letter_head.py`

## Steps
1) Read current head revision id:
   - Run: `alembic heads`
   - Capture HEAD as `<PREV_HEAD_REV>`.

2) Create a new revision file:
   - Run: `alembic revision -m "0007-02 create t_letter_head"`
   - Rename to: `0007_02_create_t_letter_head.py`.

3) Edit migration:
   - Set `down_revision = "<PREV_HEAD_REV>"`.
   - Implement schema below.

## Table Schema (Authoritative)
Table: `t_letter_head`

Columns:
- `id` BIGINT PK, autoincrement
- `name` VARCHAR(120) NOT NULL
- `locale` VARCHAR(10) NULL  (e.g., "zh-CN", "en-US")
- `logo_file_path` VARCHAR(512) NULL
- `header_text` TEXT NULL
- `footer_text` TEXT NULL
- `address_block` TEXT NULL
- `phone` VARCHAR(50) NULL
- `email` VARCHAR(254) NULL
- `website` VARCHAR(254) NULL
- `is_default` BOOLEAN NOT NULL DEFAULT FALSE
- `created_by_user_id` BIGINT NULL, FK → `t_user.id` ON DELETE SET NULL
- `created_at` TIMESTAMP NOT NULL DEFAULT now()
- `updated_at` TIMESTAMP NOT NULL DEFAULT now()

Indexes / Constraints:
- Index on `is_default`
- Index on `locale`
- Do NOT enforce “only one default” at DB level in MVP1

## Alembic Implementation (Exact)
In `upgrade()`:
- `op.create_table("t_letter_head", ...)`
- `op.create_index("ix_t_letter_head_is_default", "t_letter_head", ["is_default"])`
- `op.create_index("ix_t_letter_head_locale", "t_letter_head", ["locale"])`

In `downgrade()`:
- drop indexes then drop table

## Done Criteria
1) `alembic upgrade head` succeeds.
2) `t_letter_head` exists with all columns.
3) `alembic downgrade -1` succeeds cleanly.
