# BE-MD-0001-01_t_case — ORM model for table `t_case`

    ## Design references
    - `backend/alembic/versions/0001_mvp1_core_tables.py` (schema source of truth)
    - (Optional) module docs under `backend/app/modules/**/docs/` if present

    ## Target
    - **File:** `backend/app/modules/cases/models.py`
    - **Atomic rule:** modify/create ONLY this file; implement ONLY ONE ORM class for `t_case`.

    ## Scope decision (MVP1 – FIXED)
    - Scope is FIXED for MVP1.
    - Implement ONLY the ORM class mapping to `t_case`.
    - `__tablename__` MUST be exactly `t_case` (lowercase, matches migration).
    - Do NOT add extra columns beyond those listed below.
    - No APIs, schemas, services, or business logic in this task.

    ## Model to implement (EXACT)

    ### Table: `t_case`
    Recommended class name: `Case` (name can vary, table mapping must match)

    **Columns (EXACT, from migration):**
    - `id` : `sa.String(36`  (→ `str`)
- `case_no` : `sa.String(64`  (→ `str`)
- `case_type` : `sa.String(32`  (→ `str`)
- `patent_category` : `sa.String(32`  (→ `str`)
- `flow_dir` : `sa.String(32`  (→ `str`)
- `client_id` : `sa.String(36`  (→ `str`)
- `title_cn` : `sa.Text(`  (→ `str`)
- `title_en` : `sa.Text(`  (→ `str`)
- `app_no` : `sa.String(64`  (→ `str`)
- `status` : `sa.String(32`  (→ `str`)
- `recv_date` : `sa.Date(`  (→ `date`)
- `filing_date` : `sa.Date(`  (→ `date`)
- `created_at` : `sa.DateTime(`  (→ `datetime`)
- `updated_at` : `sa.DateTime(`  (→ `datetime`)

    **Foreign keys (from migration):**
    - `t_client.id`

    **Indexes (defined in migrations):**
    - `idx_case_client` on ['client_id']
- `idx_case_appno` on ['app_no']

    ## Non-scope (explicitly excluded)
    - No relationships beyond what is needed to declare FKs (optional in MVP1)
    - No index declarations in ORM unless you choose to mirror them (not required)
    - No validation logic
    - No triggers / events
    - No changes to other tables/models

    ## Prompt
    In `backend/app/modules/cases/models.py`, implement ONE SQLAlchemy model class that maps EXACTLY to table `t_case` as defined in `backend/alembic/versions/0001_mvp1_core_tables.py`.

    Requirements:
    - `__tablename__ = "t_case"`
    - Define all columns with the exact same column names
    - Keep types compatible with both SQLite (PoC) and Postgres (prod)
    - Do NOT add any extra fields
    - Do NOT ask clarification questions
