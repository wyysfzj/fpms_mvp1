# Universal Atomic Execution Prompt (v2) — ENH-01-02 (FPMS MVP1)

You are a coding agent executing **exactly ONE** atomic task.

## Task File (Authoritative)
- `tasks/backend/mvp1enhance/ENH-01-02.md`

## Goal
Fix the migration file (`ea0de36a1dde_add_t_role_perm.py`) to add the `created_at` column to the `t_role_perm` table.

## Hard Rules (MUST FOLLOW)
- Execute **ONLY ENH-01-02**.
- Do **NOT** add new migrations outside this task.
- Modify **ONLY** the migration file (`ea0de36a1dde_add_t_role_perm.py`) to include the `created_at` column in the `t_role_perm` table.

## Allowed Files (Strict Allowlist)
- `backend/alembic/versions/ea0de36a1dde_add_t_role_perm.py` (migration file)

## Required Change (EXACT)
1) Add the `created_at` column to the `t_role_perm` table in the migration file `ea0de36a1dde_add_t_role_perm.py`:
   ```python
   sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP"))
   ```
2) Ensure that the column is **nullable=False** and has a **server_default** set to **`CURRENT_TIMESTAMP`**.

## Verification (MUST RUN)
1) After fixing the migration file, run the following command to apply the migration:
```bash
cd backend
alembic upgrade head
```

2) Verify the schema:
```bash
sqlite3 fpms_dev.db ".schema t_role_perm"
```

## Evidence Required
Provide:
- Command outputs after running the migration.
- `git diff` showing only the migration file changes.
- Verify the `created_at` column is added by checking the schema.

## Completion Criteria
Task is DONE only if:
- `created_at` column is added to `t_role_perm` and SQLite schema reflects this change.
- Migration runs successfully with no errors.
- No other migration files are modified.

## STOP Contract
STOP if:
- Any file outside the allowlist is modified.
- The migration file is not updated correctly.
