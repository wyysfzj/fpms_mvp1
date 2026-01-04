# BE-MD-0001-02_t_client — ORM model for table `t_client`

    ## Design references
    - `backend/alembic/versions/0001_mvp1_core_tables.py` (schema source of truth)
    - (Optional) module docs under `backend/app/modules/**/docs/` if present

    ## Target
    - **File:** `backend/app/modules/masterdata/clients/models.py`
    - **Atomic rule:** modify/create ONLY this file; implement ONLY ONE ORM class for `t_client`.

    ## Scope decision (MVP1 – FIXED)
    - Scope is FIXED for MVP1.
    - Implement ONLY the ORM class mapping to `t_client`.
    - `__tablename__` MUST be exactly `t_client` (lowercase, matches migration).
    - Do NOT add extra columns beyond those listed below.
    - No APIs, schemas, services, or business logic in this task.

    ## Model to implement (EXACT)

    ### Table: `t_client`
    Recommended class name: `Client` (name can vary, table mapping must match)

    **Columns (EXACT, from migration):**
    - `id` : `sa.String(36`  (→ `str`)
- `client_code` : `sa.String(64`  (→ `str`)
- `name_cn` : `sa.String(256`  (→ `str`)
- `name_en` : `sa.String(256`  (→ `str`)
- `client_type` : `sa.String(32`  (→ `str`)
- `default_currency` : `sa.String(8`  (→ `str`)
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
    In `backend/app/modules/masterdata/clients/models.py`, implement ONE SQLAlchemy model class that maps EXACTLY to table `t_client` as defined in `backend/alembic/versions/0001_mvp1_core_tables.py`.

    Requirements:
    - `__tablename__ = "t_client"`
    - Define all columns with the exact same column names
    - Keep types compatible with both SQLite (PoC) and Postgres (prod)
    - Do NOT add any extra fields
    - Do NOT ask clarification questions
