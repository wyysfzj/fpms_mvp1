# BE-MD-0003-03_t_task_template — ORM model for table `t_task_template`

    ## Design references
    - `backend/alembic/versions/0003_tasks.py` (schema source of truth)
    - (Optional) module docs under `backend/app/modules/**/docs/` if present

    ## Target
    - **File:** `backend/app/modules/tasks/models.py`
    - **Atomic rule:** modify/create ONLY this file; implement ONLY ONE ORM class for `t_task_template`.

    ## Scope decision (MVP1 – FIXED)
    - Scope is FIXED for MVP1.
    - Implement ONLY the ORM class mapping to `t_task_template`.
    - `__tablename__` MUST be exactly `t_task_template` (lowercase, matches migration).
    - Do NOT add extra columns beyond those listed below.
    - No APIs, schemas, services, or business logic in this task.

    ## Model to implement (EXACT)

    ### Table: `t_task_template`
    Recommended class name: `TaskTemplate` (name can vary, table mapping must match)

    **Columns (EXACT, from migration):**
    - `id` : `sa.String(36`  (→ `str`)
- `code` : `sa.String(64`  (→ `str`)
- `name` : `sa.String(256`  (→ `str`)
- `enabled` : `sa.Boolean(`  (→ `bool`)

    **Foreign keys (from migration):**
    - (none)

    **Indexes (defined in migrations):**
    - (none; indexes may exist on other tables or not defined)

    ## Non-scope (explicitly excluded)
    - No relationships beyond what is needed to declare FKs (optional in MVP1)
    - No index declarations in ORM unless you choose to mirror them (not required)
    - No validation logic
    - No triggers / events
    - No changes to other tables/models

    ## Prompt
    In `backend/app/modules/tasks/models.py`, implement ONE SQLAlchemy model class that maps EXACTLY to table `t_task_template` as defined in `backend/alembic/versions/0003_tasks.py`.

    Requirements:
    - `__tablename__ = "t_task_template"`
    - Define all columns with the exact same column names
    - Keep types compatible with both SQLite (PoC) and Postgres (prod)
    - Do NOT add any extra fields
    - Do NOT ask clarification questions
