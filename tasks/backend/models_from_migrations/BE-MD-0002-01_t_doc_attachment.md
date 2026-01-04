# BE-MD-0002-01_t_doc_attachment — ORM model for table `t_doc_attachment`

    ## Design references
    - `backend/alembic/versions/0002_documents.py` (schema source of truth)
    - (Optional) module docs under `backend/app/modules/**/docs/` if present

    ## Target
    - **File:** `backend/app/modules/documents/models.py`
    - **Atomic rule:** modify/create ONLY this file; implement ONLY ONE ORM class for `t_doc_attachment`.

    ## Scope decision (MVP1 – FIXED)
    - Scope is FIXED for MVP1.
    - Implement ONLY the ORM class mapping to `t_doc_attachment`.
    - `__tablename__` MUST be exactly `t_doc_attachment` (lowercase, matches migration).
    - Do NOT add extra columns beyond those listed below.
    - No APIs, schemas, services, or business logic in this task.

    ## Model to implement (EXACT)

    ### Table: `t_doc_attachment`
    Recommended class name: `DocAttachment` (name can vary, table mapping must match)

    **Columns (EXACT, from migration):**
    - `id` : `sa.String(36`  (→ `str`)
- `document_id` : `sa.String(36`  (→ `str`)
- `file_name` : `sa.String(256`  (→ `str`)
- `file_path` : `sa.Text(`  (→ `str`)
- `mime_type` : `sa.String(128`  (→ `str`)
- `file_size` : `sa.Integer(`  (→ `int`)
- `uploaded_at` : `sa.DateTime(`  (→ `datetime`)

    **Foreign keys (from migration):**
    - `t_document.id`

    **Indexes (defined in migrations):**
    - (none; indexes may exist on other tables or not defined)

    ## Non-scope (explicitly excluded)
    - No relationships beyond what is needed to declare FKs (optional in MVP1)
    - No index declarations in ORM unless you choose to mirror them (not required)
    - No validation logic
    - No triggers / events
    - No changes to other tables/models

    ## Prompt
    In `backend/app/modules/documents/models.py`, implement ONE SQLAlchemy model class that maps EXACTLY to table `t_doc_attachment` as defined in `backend/alembic/versions/0002_documents.py`.

    Requirements:
    - `__tablename__ = "t_doc_attachment"`
    - Define all columns with the exact same column names
    - Keep types compatible with both SQLite (PoC) and Postgres (prod)
    - Do NOT add any extra fields
    - Do NOT ask clarification questions
