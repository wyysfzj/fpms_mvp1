# BE-MD-0002-03_t_document — ORM model for table `t_document`

    ## Design references
    - `backend/alembic/versions/0002_documents.py` (schema source of truth)
    - (Optional) module docs under `backend/app/modules/**/docs/` if present

    ## Target
    - **File:** `backend/app/modules/documents/models.py`
    - **Atomic rule:** modify/create ONLY this file; implement ONLY ONE ORM class for `t_document`.

    ## Scope decision (MVP1 – FIXED)
    - Scope is FIXED for MVP1.
    - Implement ONLY the ORM class mapping to `t_document`.
    - `__tablename__` MUST be exactly `t_document` (lowercase, matches migration).
    - Do NOT add extra columns beyond those listed below.
    - No APIs, schemas, services, or business logic in this task.

    ## Model to implement (EXACT)

    ### Table: `t_document`
    Recommended class name: `Document` (name can vary, table mapping must match)

    **Columns (EXACT, from migration):**
    - `id` : `sa.String(36`  (→ `str`)
- `case_id` : `sa.String(36`  (→ `str`)
- `doc_template_id` : `sa.String(36`  (→ `str`)
- `direction` : `sa.String(8`  (→ `str`)
- `doc_date` : `sa.Date(`  (→ `date`)
- `title` : `sa.Text(`  (→ `str`)
- `ref_no` : `sa.String(128`  (→ `str`)
- `extra_data` : `sa.Text(`  (→ `str`)
- `created_at` : `sa.DateTime(`  (→ `datetime`)
- `updated_at` : `sa.DateTime(`  (→ `datetime`)

    **Foreign keys (from migration):**
    - `t_case.id`
- `t_doc_template.id`

    **Indexes (defined in migrations):**
    - `idx_doc_case_date` on ['case_id', 'doc_date']

    ## Non-scope (explicitly excluded)
    - No relationships beyond what is needed to declare FKs (optional in MVP1)
    - No index declarations in ORM unless you choose to mirror them (not required)
    - No validation logic
    - No triggers / events
    - No changes to other tables/models

    ## Prompt
    In `backend/app/modules/documents/models.py`, implement ONE SQLAlchemy model class that maps EXACTLY to table `t_document` as defined in `backend/alembic/versions/0002_documents.py`.

    Requirements:
    - `__tablename__ = "t_document"`
    - Define all columns with the exact same column names
    - Keep types compatible with both SQLite (PoC) and Postgres (prod)
    - Do NOT add any extra fields
    - Do NOT ask clarification questions
