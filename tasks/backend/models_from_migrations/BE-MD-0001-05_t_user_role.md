# BE-MD-0001-05_t_user_role — ORM model for table `t_user_role`

    ## Design references
    - `backend/alembic/versions/0001_mvp1_core_tables.py` (schema source of truth)
    - (Optional) module docs under `backend/app/modules/**/docs/` if present

    ## Target
    - **File:** `backend/app/modules/auth/models.py`
    - **Atomic rule:** modify/create ONLY this file; implement ONLY ONE ORM class for `t_user_role`.

    ## Scope decision (MVP1 – FIXED)
    - Scope is FIXED for MVP1.
    - Implement ONLY the ORM class mapping to `t_user_role`.
    - `__tablename__` MUST be exactly `t_user_role` (lowercase, matches migration).
    - Do NOT add extra columns beyond those listed below.
    - No APIs, schemas, services, or business logic in this task.

    ## Model to implement (EXACT)

    ### Table: `t_user_role`
    Recommended class name: `UserRole` (name can vary, table mapping must match)

    **Columns (EXACT, from migration):**
    - `user_id` : `sa.String(36`  (→ `str`)
- `role_id` : `sa.String(36`  (→ `str`)

    **Foreign keys (from migration):**
    - `t_user.id`
- `t_role.id`

    **Indexes (defined in migrations):**
    - (none; indexes may exist on other tables or not defined)

    ## Non-scope (explicitly excluded)
    - No relationships beyond what is needed to declare FKs (optional in MVP1)
    - No index declarations in ORM unless you choose to mirror them (not required)
    - No validation logic
    - No triggers / events
    - No changes to other tables/models

    ## Prompt
    In `backend/app/modules/auth/models.py`, implement ONE SQLAlchemy model class that maps EXACTLY to table `t_user_role` as defined in `backend/alembic/versions/0001_mvp1_core_tables.py`.

    Requirements:
    - `__tablename__ = "t_user_role"`
    - Define all columns with the exact same column names
    - Keep types compatible with both SQLite (PoC) and Postgres (prod)
    - Do NOT add any extra fields
    - Do NOT ask clarification questions
