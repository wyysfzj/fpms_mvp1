# BE-MD-0005-05_t_payment — ORM model for table `t_payment`

    ## Design references
    - `backend/alembic/versions/0005_billing.py` (schema source of truth)
    - (Optional) module docs under `backend/app/modules/**/docs/` if present

    ## Target
    - **File:** `backend/app/modules/billing/models.py`
    - **Atomic rule:** modify/create ONLY this file; implement ONLY ONE ORM class for `t_payment`.

    ## Scope decision (MVP1 – FIXED)
    - Scope is FIXED for MVP1.
    - Implement ONLY the ORM class mapping to `t_payment`.
    - `__tablename__` MUST be exactly `t_payment` (lowercase, matches migration).
    - Do NOT add extra columns beyond those listed below.
    - No APIs, schemas, services, or business logic in this task.

    ## Model to implement (EXACT)

    ### Table: `t_payment`
    Recommended class name: `Payment` (name can vary, table mapping must match)

    **Columns (EXACT, from migration):**
    - `id` : `sa.String(36`  (→ `str`)
- `pay_no` : `sa.String(64`  (→ `str`)
- `client_id` : `sa.String(36`  (→ `str`)
- `pay_date` : `sa.Date(`  (→ `date`)
- `currency` : `sa.String(8`  (→ `str`)
- `amount` : `sa.Numeric(18`  (→ `Decimal`)
- `remark` : `sa.Text(`  (→ `str`)
- `created_at` : `sa.DateTime(`  (→ `datetime`)

    **Foreign keys (from migration):**
    - `t_client.id`

    **Indexes (defined in migrations):**
    - `idx_payment_client_date` on ['client_id', 'pay_date']

    ## Non-scope (explicitly excluded)
    - No relationships beyond what is needed to declare FKs (optional in MVP1)
    - No index declarations in ORM unless you choose to mirror them (not required)
    - No validation logic
    - No triggers / events
    - No changes to other tables/models

    ## Prompt
    In `backend/app/modules/billing/models.py`, implement ONE SQLAlchemy model class that maps EXACTLY to table `t_payment` as defined in `backend/alembic/versions/0005_billing.py`.

    Requirements:
    - `__tablename__ = "t_payment"`
    - Define all columns with the exact same column names
    - Keep types compatible with both SQLite (PoC) and Postgres (prod)
    - Do NOT add any extra fields
    - Do NOT ask clarification questions
