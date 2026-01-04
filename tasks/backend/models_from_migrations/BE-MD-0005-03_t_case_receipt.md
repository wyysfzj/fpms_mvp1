# BE-MD-0005-03_t_case_receipt — ORM model for table `t_case_receipt`

    ## Design references
    - `backend/alembic/versions/0005_billing.py` (schema source of truth)
    - (Optional) module docs under `backend/app/modules/**/docs/` if present

    ## Target
    - **File:** `backend/app/modules/billing/models.py`
    - **Atomic rule:** modify/create ONLY this file; implement ONLY ONE ORM class for `t_case_receipt`.

    ## Scope decision (MVP1 – FIXED)
    - Scope is FIXED for MVP1.
    - Implement ONLY the ORM class mapping to `t_case_receipt`.
    - `__tablename__` MUST be exactly `t_case_receipt` (lowercase, matches migration).
    - Do NOT add extra columns beyond those listed below.
    - No APIs, schemas, services, or business logic in this task.

    ## Model to implement (EXACT)

    ### Table: `t_case_receipt`
    Recommended class name: `CaseReceipt` (name can vary, table mapping must match)

    **Columns (EXACT, from migration):**
    - `id` : `sa.String(36`  (→ `str`)
- `case_id` : `sa.String(36`  (→ `str`)
- `fee_type` : `sa.String(16`  (→ `str`)
- `currency` : `sa.String(8`  (→ `str`)
- `receivable_amt` : `sa.Numeric(18`  (→ `Decimal`)
- `received_amt` : `sa.Numeric(18`  (→ `Decimal`)
- `last_receipt_date` : `sa.Date(`  (→ `date`)

    **Foreign keys (from migration):**
    - `t_case.id`

    **Indexes (defined in migrations):**
    - (none; indexes may exist on other tables or not defined)

    ## Non-scope (explicitly excluded)
    - No relationships beyond what is needed to declare FKs (optional in MVP1)
    - No index declarations in ORM unless you choose to mirror them (not required)
    - No validation logic
    - No triggers / events
    - No changes to other tables/models

    ## Prompt
    In `backend/app/modules/billing/models.py`, implement ONE SQLAlchemy model class that maps EXACTLY to table `t_case_receipt` as defined in `backend/alembic/versions/0005_billing.py`.

    Requirements:
    - `__tablename__ = "t_case_receipt"`
    - Define all columns with the exact same column names
    - Keep types compatible with both SQLite (PoC) and Postgres (prod)
    - Do NOT add any extra fields
    - Do NOT ask clarification questions
