# BE-MD-0005-04_t_offset — ORM model for table `t_offset`

    ## Design references
    - `backend/alembic/versions/0005_billing.py` (schema source of truth)
    - (Optional) module docs under `backend/app/modules/**/docs/` if present

    ## Target
    - **File:** `backend/app/modules/billing/models.py`
    - **Atomic rule:** modify/create ONLY this file; implement ONLY ONE ORM class for `t_offset`.

    ## Scope decision (MVP1 – FIXED)
    - Scope is FIXED for MVP1.
    - Implement ONLY the ORM class mapping to `t_offset`.
    - `__tablename__` MUST be exactly `t_offset` (lowercase, matches migration).
    - Do NOT add extra columns beyond those listed below.
    - No APIs, schemas, services, or business logic in this task.

    ## Model to implement (EXACT)

    ### Table: `t_offset`
    Recommended class name: `Offset` (name can vary, table mapping must match)

    **Columns (EXACT, from migration):**
    - `id` : `sa.String(36`  (→ `str`)
- `payment_line_id` : `sa.String(36`  (→ `str`)
- `bill_id` : `sa.String(36`  (→ `str`)
- `offset_amt` : `sa.Numeric(18`  (→ `Decimal`)
- `offset_date` : `sa.Date(`  (→ `date`)
- `is_reversed` : `sa.Boolean(`  (→ `bool`)
- `reversed_at` : `sa.DateTime(`  (→ `datetime`)

    **Foreign keys (from migration):**
    - `t_payment_line.id`
- `t_bill.id`

    **Indexes (defined in migrations):**
    - `idx_offset_bill` on ['bill_id']

    ## Non-scope (explicitly excluded)
    - No relationships beyond what is needed to declare FKs (optional in MVP1)
    - No index declarations in ORM unless you choose to mirror them (not required)
    - No validation logic
    - No triggers / events
    - No changes to other tables/models

    ## Prompt
    In `backend/app/modules/billing/models.py`, implement ONE SQLAlchemy model class that maps EXACTLY to table `t_offset` as defined in `backend/alembic/versions/0005_billing.py`.

    Requirements:
    - `__tablename__ = "t_offset"`
    - Define all columns with the exact same column names
    - Keep types compatible with both SQLite (PoC) and Postgres (prod)
    - Do NOT add any extra fields
    - Do NOT ask clarification questions
