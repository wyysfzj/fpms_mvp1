# BE-MD-0001-04_t_user — ORM model for table `t_user`

    ## Design references
    - `backend/alembic/versions/0001_mvp1_core_tables.py` (schema source of truth)
    - (Optional) module docs under `backend/app/modules/**/docs/` if present

    ## Target
    - **File:** `backend/app/modules/auth/models.py`
    - **Atomic rule:** modify/create ONLY this file; implement ONLY ONE ORM class for `t_user`.

    ## Scope decision (MVP1 – FIXED)
    - Scope is FIXED for MVP1.
    - Implement ONLY the ORM class mapping to `t_user`.
    - `__tablename__` MUST be exactly `t_user` (lowercase, matches migration).
    - Do NOT add extra columns beyond those listed below.
    - No APIs, schemas, services, or business logic in this task.

    ## Model to implement (EXACT)

    ### Table: `t_user`
    Recommended class name: `User` (name can vary, table mapping must match)

    **Columns (EXACT, from migration):**
    - `id` : `sa.String(36`  (→ `str`)
- `username` : `sa.String(64`  (→ `str`)
- `display_name` : `sa.String(128`  (→ `str`)
- `password_hash` : `sa.String(255`  (→ `str`)
- `is_active` : `sa.Boolean(`  (→ `bool`)
- `created_at` : `sa.DateTime(`  (→ `datetime`)
- `updated_at` : `sa.DateTime(`  (→ `datetime`)

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
    In `backend/app/modules/auth/models.py`, implement ONE SQLAlchemy model class that maps EXACTLY to table `t_user` as defined in `backend/alembic/versions/0001_mvp1_core_tables.py`.

    Requirements:
    - `__tablename__ = "t_user"`
    - Define all columns with the exact same column names
    - Keep types compatible with both SQLite (PoC) and Postgres (prod)
    - Do NOT add any extra fields
    - Do NOT ask clarification questions
