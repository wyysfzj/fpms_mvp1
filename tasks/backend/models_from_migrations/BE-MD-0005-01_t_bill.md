# BE-MD-0005-01_t_bill — ORM model for table `t_bill`

    ## Design references
    - `backend/alembic/versions/0005_billing.py` (schema source of truth)
    - (Optional) module docs under `backend/app/modules/**/docs/` if present

    ## Target
    - **File:** `backend/app/modules/billing/models.py`
    - **Atomic rule:** modify/create ONLY this file; implement ONLY ONE ORM class for `t_bill`.

    ## Scope decision (MVP1 – FIXED)
    - Scope is FIXED for MVP1.
    - Implement ONLY the ORM class mapping to `t_bill`.
    - `__tablename__` MUST be exactly `t_bill` (lowercase, matches migration).
    - Do NOT add extra columns beyond those listed below.
    - No APIs, schemas, services, or business logic in this task.

    ## Model to implement (EXACT)

    ### Table: `t_bill`
    Recommended class name: `Bill` (name can vary, table mapping must match)

    **Columns (EXACT, from migration):**
    - `id` : `sa.String(36`  (→ `str`)
- `bill_no` : `sa.String(64`  (→ `str`)
- `client_id` : `sa.String(36`  (→ `str`)
- `currency` : `sa.String(8`  (→ `str`)
- `direction` : `sa.String(8`  (→ `str`)
- `status` : `sa.String(24`  (→ `str`)
- `bill_date` : `sa.Date(`  (→ `date`)
- `due_date` : `sa.Date(`  (→ `date`)
- `total_gov` : `sa.Numeric(18`  (→ `Decimal`)
- `total_service` : `sa.Numeric(18`  (→ `Decimal`)
- `total_misc` : `sa.Numeric(18`  (→ `Decimal`)
- `amount` : `sa.Numeric(18`  (→ `Decimal`)
- `balance` : `sa.Numeric(18`  (→ `Decimal`)
- `created_at` : `sa.DateTime(`  (→ `datetime`)
- `updated_at` : `sa.DateTime(`  (→ `datetime`)

    **Foreign keys (from migration):**
    - `t_client.id`

    **Indexes (defined in migrations):**
    - `idx_bill_client_status_date` on ['client_id', 'status', 'bill_date']

    ## Non-scope (explicitly excluded)
    - No relationships beyond what is needed to declare FKs (optional in MVP1)
    - No index declarations in ORM unless you choose to mirror them (not required)
    - No validation logic
    - No triggers / events
    - No changes to other tables/models

    ## Prompt
    In `backend/app/modules/billing/models.py`, implement ONE SQLAlchemy model class that maps EXACTLY to table `t_bill` as defined in `backend/alembic/versions/0005_billing.py`.

    Requirements:
    - `__tablename__ = "t_bill"`
    - Define all columns with the exact same column names
    - Keep types compatible with both SQLite (PoC) and Postgres (prod)
    - Do NOT add any extra fields
    - Do NOT ask clarification questions
