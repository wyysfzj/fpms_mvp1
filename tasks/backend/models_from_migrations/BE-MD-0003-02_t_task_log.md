# BE-MD-0003-02_t_task_log — ORM model for table `t_task_log`

    ## Design references
    - `backend/alembic/versions/0003_tasks.py` (schema source of truth)
    - (Optional) module docs under `backend/app/modules/**/docs/` if present

    ## Target
    - **File:** `backend/app/modules/tasks/models.py`
    - **Atomic rule:** modify/create ONLY this file; implement ONLY ONE ORM class for `t_task_log`.

    ## Scope decision (MVP1 – FIXED)
    - Scope is FIXED for MVP1.
    - Implement ONLY the ORM class mapping to `t_task_log`.
    - `__tablename__` MUST be exactly `t_task_log` (lowercase, matches migration).
    - Do NOT add extra columns beyond those listed below.
    - No APIs, schemas, services, or business logic in this task.

    ## Model to implement (EXACT)

    ### Table: `t_task_log`
    Recommended class name: `TaskLog` (name can vary, table mapping must match)

    **Columns (EXACT, from migration):**
    - `id` : `sa.String(36`  (→ `str`)
- `task_id` : `sa.String(36`  (→ `str`)
- `action` : `sa.String(32`  (→ `str`)
- `from_status` : `sa.String(16`  (→ `str`)
- `to_status` : `sa.String(16`  (→ `str`)
- `remark` : `sa.Text(`  (→ `str`)
- `created_at` : `sa.DateTime(`  (→ `datetime`)

    **Foreign keys (from migration):**
    - `t_task.id`

    **Indexes (defined in migrations):**
    - (none; indexes may exist on other tables or not defined)

    ## Non-scope (explicitly excluded)
    - No relationships beyond what is needed to declare FKs (optional in MVP1)
    - No index declarations in ORM unless you choose to mirror them (not required)
    - No validation logic
    - No triggers / events
    - No changes to other tables/models

    ## Prompt
    In `backend/app/modules/tasks/models.py`, implement ONE SQLAlchemy model class that maps EXACTLY to table `t_task_log` as defined in `backend/alembic/versions/0003_tasks.py`.

    Requirements:
    - `__tablename__ = "t_task_log"`
    - Define all columns with the exact same column names
    - Keep types compatible with both SQLite (PoC) and Postgres (prod)
    - Do NOT add any extra fields
    - Do NOT ask clarification questions
