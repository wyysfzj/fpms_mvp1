# BE-MD-0003-01_t_task — ORM model for table `t_task`

    ## Design references
    - `backend/alembic/versions/0003_tasks.py` (schema source of truth)
    - (Optional) module docs under `backend/app/modules/**/docs/` if present

    ## Target
    - **File:** `backend/app/modules/tasks/models.py`
    - **Atomic rule:** modify/create ONLY this file; implement ONLY ONE ORM class for `t_task`.

    ## Scope decision (MVP1 – FIXED)
    - Scope is FIXED for MVP1.
    - Implement ONLY the ORM class mapping to `t_task`.
    - `__tablename__` MUST be exactly `t_task` (lowercase, matches migration).
    - Do NOT add extra columns beyond those listed below.
    - No APIs, schemas, services, or business logic in this task.

    ## Model to implement (EXACT)

    ### Table: `t_task`
    Recommended class name: `Task` (name can vary, table mapping must match)

    **Columns (EXACT, from migration):**
    - `id` : `sa.String(36`  (→ `str`)
- `case_id` : `sa.String(36`  (→ `str`)
- `document_id` : `sa.String(36`  (→ `str`)
- `task_template_id` : `sa.String(36`  (→ `str`)
- `title` : `sa.Text(`  (→ `str`)
- `base_date` : `sa.Date(`  (→ `date`)
- `due_date` : `sa.Date(`  (→ `date`)
- `internal_due_date` : `sa.Date(`  (→ `date`)
- `worker_id` : `sa.String(36`  (→ `str`)
- `supervisor_id` : `sa.String(36`  (→ `str`)
- `status` : `sa.String(16`  (→ `str`)
- `done_at` : `sa.DateTime(`  (→ `datetime`)
- `created_at` : `sa.DateTime(`  (→ `datetime`)
- `updated_at` : `sa.DateTime(`  (→ `datetime`)

    **Foreign keys (from migration):**
    - `t_case.id`
- `t_document.id`
- `t_task_template.id`
- `t_user.id`
- `t_user.id`

    **Indexes (defined in migrations):**
    - `idx_task_case_due_status` on ['case_id', 'due_date', 'status']
- `idx_task_worker_due` on ['worker_id', 'due_date']

    ## Non-scope (explicitly excluded)
    - No relationships beyond what is needed to declare FKs (optional in MVP1)
    - No index declarations in ORM unless you choose to mirror them (not required)
    - No validation logic
    - No triggers / events
    - No changes to other tables/models

    ## Prompt
    In `backend/app/modules/tasks/models.py`, implement ONE SQLAlchemy model class that maps EXACTLY to table `t_task` as defined in `backend/alembic/versions/0003_tasks.py`.

    Requirements:
    - `__tablename__ = "t_task"`
    - Define all columns with the exact same column names
    - Keep types compatible with both SQLite (PoC) and Postgres (prod)
    - Do NOT add any extra fields
    - Do NOT ask clarification questions
