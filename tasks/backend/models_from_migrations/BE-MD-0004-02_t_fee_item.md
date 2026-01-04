# BE-MD-0004-02_t_fee_item — ORM model for table `t_fee_item`

    ## Design references
    - `backend/alembic/versions/0004_fees.py` (schema source of truth)
    - (Optional) module docs under `backend/app/modules/**/docs/` if present

    ## Target
    - **File:** `backend/app/modules/fees/models.py`
    - **Atomic rule:** modify/create ONLY this file; implement ONLY ONE ORM class for `t_fee_item`.

    ## Scope decision (MVP1 – FIXED)
    - Scope is FIXED for MVP1.
    - Implement ONLY the ORM class mapping to `t_fee_item`.
    - `__tablename__` MUST be exactly `t_fee_item` (lowercase, matches migration).
    - Do NOT add extra columns beyond those listed below.
    - No APIs, schemas, services, or business logic in this task.

    ## Model to implement (EXACT)

    ### Table: `t_fee_item`
    Recommended class name: `FeeItem` (name can vary, table mapping must match)

    **Columns (EXACT, from migration):**
    - `id` : `sa.String(36`  (→ `str`)
- `draft_id` : `sa.String(36`  (→ `str`)
- `case_id` : `sa.String(36`  (→ `str`)
- `rate_id` : `sa.String(36`  (→ `str`)
- `fee_code` : `sa.String(64`  (→ `str`)
- `fee_name` : `sa.String(256`  (→ `str`)
- `fee_type` : `sa.String(16`  (→ `str`)
- `year_no` : `sa.Integer(`  (→ `int`)
- `quantity` : `sa.Numeric(18`  (→ `Decimal`)
- `unit_price` : `sa.Numeric(18`  (→ `Decimal`)
- `amount` : `sa.Numeric(18`  (→ `Decimal`)
- `remark` : `sa.Text(`  (→ `str`)

    **Foreign keys (from migration):**
    - `t_fee_draft.id`
- `t_case.id`
- `t_fee_rate.id`

    **Indexes (defined in migrations):**
    - (none; indexes may exist on other tables or not defined)

    ## Non-scope (explicitly excluded)
    - No relationships beyond what is needed to declare FKs (optional in MVP1)
    - No index declarations in ORM unless you choose to mirror them (not required)
    - No validation logic
    - No triggers / events
    - No changes to other tables/models

    ## Prompt
    In `backend/app/modules/fees/models.py`, implement ONE SQLAlchemy model class that maps EXACTLY to table `t_fee_item` as defined in `backend/alembic/versions/0004_fees.py`.

    Requirements:
    - `__tablename__ = "t_fee_item"`
    - Define all columns with the exact same column names
    - Keep types compatible with both SQLite (PoC) and Postgres (prod)
    - Do NOT add any extra fields
    - Do NOT ask clarification questions
