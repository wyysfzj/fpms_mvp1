"""Verify that all DB tables are covered by SQLAlchemy models."""

from __future__ import annotations

import sys
from pathlib import Path
import os

from sqlalchemy import inspect

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "backend"))
os.chdir(REPO_ROOT / "backend")

from app.db.session import get_engine  # noqa: E402
from app.models import *  # noqa: F401,F403,E402  # import all to populate metadata
from app.db.base import Base  # noqa: E402

engine = get_engine()
inspector = inspect(engine)
tables_in_db = set(inspector.get_table_names())
tables_in_models = set(Base.metadata.tables.keys())

IGNORED_TABLES = {"alembic_version"}

missing_in_models = sorted((tables_in_db - IGNORED_TABLES) - tables_in_models)
extra_in_models = sorted(tables_in_models - tables_in_db)

print("DB tables:", len(tables_in_db))
print("Model tables:", len(tables_in_models))
print("Missing in models:", missing_in_models)
print("Extra in models:", extra_in_models)

assert not missing_in_models, f"Models missing tables: {missing_in_models}"
assert not extra_in_models, f"Models define non-existent tables: {extra_in_models}"
print("OK: ORM parity (table-level)")
