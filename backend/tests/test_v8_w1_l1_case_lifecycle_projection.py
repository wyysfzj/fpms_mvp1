from __future__ import annotations

from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import CheckConstraint, Integer, String, create_engine, inspect

from app.core.config import get_settings
from app.modules.cases.models import Case

REVISION = "v8_w1_l1_case_lifecycle_01"
DOWN_REVISION = "addgap_grant_lineage_01"
TABLE = "t_case"

LIFECYCLE_COLUMNS = {
    "business_stage": (String, 32),
    "official_procedure_stage": (String, 64),
    "legal_status": (String, 32),
    "lifecycle_revision": (Integer, None),
    "lifecycle_verification_status": (String, 32),
}


def _alembic_config(db_path: Path, monkeypatch) -> Config:
    db_url = f"sqlite:///{db_path}"
    monkeypatch.setenv("DATABASE_URL", db_url)
    get_settings.cache_clear()
    config = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))
    config.set_main_option(
        "script_location",
        str(Path(__file__).resolve().parents[1] / "alembic"),
    )
    config.set_main_option("sqlalchemy.url", db_url)
    return config


def test_case_model_declares_only_nullable_unconstrained_lifecycle_carriers() -> None:
    columns = Case.__table__.c

    for name, (expected_type, expected_length) in LIFECYCLE_COLUMNS.items():
        column = columns[name]
        assert isinstance(column.type, expected_type)
        assert getattr(column.type, "length", None) == expected_length
        assert column.nullable is True
        assert column.default is None
        assert column.server_default is None
        assert column.foreign_keys == set()

    lifecycle_names = set(LIFECYCLE_COLUMNS)
    assert all(
        lifecycle_names.isdisjoint(column.name for column in index.columns)
        for index in Case.__table__.indexes
    )
    assert not any(
        isinstance(constraint, CheckConstraint)
        and any(name in str(constraint.sqltext) for name in lifecycle_names)
        for constraint in Case.__table__.constraints
    )


def test_clean_sqlite_upgrade_adds_exact_lifecycle_carriers_without_constraints(
    tmp_path,
    monkeypatch,
) -> None:
    db_path = tmp_path / "v8_w1_l1_case_lifecycle.db"
    config = _alembic_config(db_path, monkeypatch)
    engine = None
    try:
        migration = ScriptDirectory.from_config(config).get_revision(REVISION)
        assert migration is not None
        assert migration.down_revision == DOWN_REVISION

        command.upgrade(config, "head")
        engine = create_engine(f"sqlite:///{db_path}", future=True)
        inspector = inspect(engine)
        columns = {column["name"]: column for column in inspector.get_columns(TABLE)}

        for name, (expected_type, expected_length) in LIFECYCLE_COLUMNS.items():
            column = columns[name]
            assert isinstance(column["type"], expected_type)
            assert getattr(column["type"], "length", None) == expected_length
            assert column["nullable"] is True
            assert column["default"] is None

        lifecycle_names = set(LIFECYCLE_COLUMNS)
        assert all(
            lifecycle_names.isdisjoint(index["column_names"])
            for index in inspector.get_indexes(TABLE)
        )
        assert all(
            lifecycle_names.isdisjoint(constraint["column_names"])
            for constraint in inspector.get_unique_constraints(TABLE)
        )
        assert not any(
            any(name in (constraint["sqltext"] or "") for name in lifecycle_names)
            for constraint in inspector.get_check_constraints(TABLE)
        )
    finally:
        if engine is not None:
            engine.dispose()
        get_settings.cache_clear()


def test_lifecycle_carrier_migration_is_forward_only(tmp_path, monkeypatch) -> None:
    config = _alembic_config(tmp_path / "v8_w1_l1_forward_only.db", monkeypatch)
    migration = ScriptDirectory.from_config(config).get_revision(REVISION)

    assert migration is not None
    with pytest.raises(NotImplementedError, match="forward-only"):
        migration.module.downgrade()
