# BE-MD-0005-02_t_bill_item — ORM model for table `t_bill_item`

    ## Design references
    - `backend/alembic/versions/0005_billing.py` (schema source of truth)
    - (Optional) module docs under `backend/app/modules/**/docs/` if present

    ## Target
    - **File:** `backend/app/modules/billing/models.py`
    - **Atomic rule:** modify/create ONLY this file; implement ONLY ONE ORM class for `t_bill_item`.

    ## Scope decision (MVP1 – FIXED)
    - Scope is FIXED for MVP1.
    - Implement ONLY the ORM class mapping to `t_bill_item`.
    - `__tablename__` MUST be exactly `t_bill_item` (lowercase, matches migration).
    - Do NOT add extra columns beyond those listed below.
    - No APIs, schemas, services, or business logic in this task.

    ## Model to implement (EXACT)

    ### Table: `t_bill_item`
    Recommended class name: `BillItem` (name can vary, table mapping must match)

    **Columns (EXACT, from migration):**
    - `id` : `sa.String(36`  (→ `str`)
- `bill_id` : `sa.String(36`  (→ `str`)
- `case_id` : `sa.String(36`  (→ `str`)
- `draft_id` : `sa.String(36`  (→ `str`)
- `fee_item_id` : `sa.String(36`  (→ `str`)
- `fee_code` : `sa.String(64`  (→ `str`)
- `fee_name` : `sa.String(256`  (→ `str`)
- `fee_type` : `sa.String(16`  (→ `str`)
- `year_no` : `sa.Integer(`  (→ `int`)
- `amount` : `sa.Numeric(18`  (→ `Decimal`)

    **Foreign keys (from migration):**
    - `t_bill.id`
- `t_case.id`
- `t_fee_draft.id`
- `t_fee_item.id`

    **Indexes (defined in migrations):**
    - (none; indexes may exist on other tables or not defined)

    ## Non-scope (explicitly excluded)
    - No relationships beyond what is needed to declare FKs (optional in MVP1)
    - No index declarations in ORM unless you choose to mirror them (not required)
    - No validation logic
    - No triggers / events
    - No changes to other tables/models

    ## Prompt
    In `backend/app/modules/billing/models.py`, implement ONE SQLAlchemy model class that maps EXACTLY to table `t_bill_item` as defined in `backend/alembic/versions/0005_billing.py`.

    Requirements:
    - `__tablename__ = "t_bill_item"`
    - Define all columns with the exact same column names
    - Keep types compatible with both SQLite (PoC) and Postgres (prod)
    - Do NOT add any extra fields
    - Do NOT ask clarification questions
