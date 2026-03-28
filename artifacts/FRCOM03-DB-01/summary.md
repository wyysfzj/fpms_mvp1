# FRCOM03-DB-01 evidence

Final verification set from the updated task file:
- `ruff check backend/alembic/versions/frcom03_db_01_create_t_case_agent_split.py backend/app/modules/cases/models.py`
- `cd backend && python3 -c "import sys; sys.path.insert(0, '.'); from sqlalchemy import inspect; from app.db.session import get_engine; from app.db.base import Base; import app.models  # noqa: F401; engine = get_engine(); tables = set(inspect(engine).get_table_names()); assert 't_case_agent_split' in tables; assert 't_case_agent_split' in Base.metadata.tables"`
- `cd backend && alembic upgrade heads`
- `./scripts/task_validate.sh FRCOM03-DB-01`

All four commands passed. Ruff emitted the existing pyproject deprecation warning, but it did not affect the result.

Scope remained limited to the persistence/model slice only.
