# BE-MD-0004-01_t_fee_draft — ORM model for table `t_fee_draft`

    ## Design references
    - `backend/alembic/versions/0004_fees.py` (schema source of truth)
    - (Optional) module docs under `backend/app/modules/**/docs/` if present

    ## Target
    - **File:** `backend/app/modules/fees/models.py`
    - **Atomic rule:** modify/create ONLY this file; implement ONLY ONE ORM class for `t_fee_draft`.

    ## Scope decision (MVP1 – FIXED)
    - Scope is FIXED for MVP1.
    - Implement ONLY the ORM class mapping to `t_fee_draft`.
    - `__tablename__` MUST be exactly `t_fee_draft` (lowercase, matches migration).
    - Do NOT add extra columns beyond those listed below.
    - No APIs, schemas, services, or business logic in this task.

    ## Model to implement (EXACT)

    ### Table: `t_fee_draft`
    Recommended class name: `FeeDraft` (name can vary, table mapping must match)

    **Columns (EXACT, from migration):**
    - `id` : `sa.String(36`  (→ `str`)
- `case_id` : `sa.String(36`  (→ `str`)
- `client_id` : `sa.String(36`  (→ `str`)
- `draft_type` : `sa.String(32`  (→ `str`)
- `currency` : `sa.String(8`  (→ `str`)
- `status` : `sa.String(16`  (→ `str`)
- `total_gov` : `sa.Numeric(18`  (→ `Decimal`)
- `total_service` : `sa.Numeric(18`  (→ `Decimal`)
- `total_misc` : `sa.Numeric(18`  (→ `Decimal`)
- `amount` : `sa.Numeric(18`  (→ `Decimal`)
- `created_at` : `sa.DateTime(`  (→ `datetime`)
- `updated_at` : `sa.DateTime(`  (→ `datetime`)

    **Foreign keys (from migration):**
    - `t_case.id`
- `t_client.id`

    **Indexes (defined in migrations):**
    - `idx_fee_draft_case` on ['case_id', 'status']

    ## Non-scope (explicitly excluded)
    - No relationships beyond what is needed to declare FKs (optional in MVP1)
    - No index declarations in ORM unless you choose to mirror them (not required)
    - No validation logic
    - No triggers / events
    - No changes to other tables/models

    ## Prompt
    In `backend/app/modules/fees/models.py`, implement ONE SQLAlchemy model class that maps EXACTLY to table `t_fee_draft` as defined in `backend/alembic/versions/0004_fees.py`.

    Requirements:
    - `__tablename__ = "t_fee_draft"`
    - Define all columns with the exact same column names
    - Keep types compatible with both SQLite (PoC) and Postgres (prod)
    - Do NOT add any extra fields
    - Do NOT ask clarification questions
