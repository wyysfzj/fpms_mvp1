from __future__ import annotations

from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import IntegrityError

from app.core.config import get_settings
from app.modules.official_workflows.models import OfficialWorkPackage

REVISION = "addgap_workpkg_resolve_key_01"
DOWN_REVISION = "frfe04_block_struct_cols_01"


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


def test_official_work_package_model_declares_nullable_unique_resolve_key() -> None:
    column = OfficialWorkPackage.__table__.c.resolve_key

    assert column.nullable is True
    assert column.type.length == 128
    assert {
        index.name
        for index in OfficialWorkPackage.__table__.indexes
        if index.unique and tuple(item.name for item in index.columns) == ("resolve_key",)
    } == {"ux_t_official_work_package_resolve_key"}


def test_clean_sqlite_upgrade_creates_resolve_key_and_unique_index(
    tmp_path,
    monkeypatch,
) -> None:
    db_path = tmp_path / "workpkg_resolve_key_clean.db"
    config = _alembic_config(db_path, monkeypatch)
    engine = None
    try:
        migration = ScriptDirectory.from_config(config).get_revision(REVISION)
        assert migration is not None
        assert migration.down_revision == DOWN_REVISION
        command.upgrade(config, "head")
        engine = create_engine(f"sqlite:///{db_path}", future=True)
        inspector = inspect(engine)
        columns = {
            column["name"]: column for column in inspector.get_columns("t_official_work_package")
        }
        indexes = {
            index["name"]: index for index in inspector.get_indexes("t_official_work_package")
        }

        assert columns["resolve_key"]["nullable"] is True
        assert columns["resolve_key"]["type"].length == 128
        assert indexes["ux_t_official_work_package_resolve_key"]["unique"] == 1
        assert indexes["ux_t_official_work_package_resolve_key"]["column_names"] == ["resolve_key"]
    finally:
        if engine is not None:
            engine.dispose()
        get_settings.cache_clear()


def test_migration_backfills_supported_package_identities_only(
    tmp_path,
    monkeypatch,
) -> None:
    db_path = tmp_path / "workpkg_resolve_key_backfill.db"
    config = _alembic_config(db_path, monkeypatch)
    engine = None
    try:
        command.upgrade(config, DOWN_REVISION)
        engine = create_engine(f"sqlite:///{db_path}", future=True)
        with engine.begin() as connection:
            connection.execute(
                text(
                    """
                    INSERT INTO t_official_work_package
                        (id, case_id, package_kind, source_document_id)
                    VALUES
                        ('pkg-filing', 'case-a', 'FILING_PREP', NULL),
                        ('pkg-oa', 'case-a', 'OA_REPLY', 'doc-oa-1'),
                        ('pkg-other', 'case-a', 'OTHER_KIND', NULL)
                    """
                )
            )

        command.upgrade(config, "head")

        with engine.connect() as connection:
            rows = connection.execute(
                text("SELECT id, resolve_key FROM t_official_work_package ORDER BY id")
            ).all()
        assert dict(rows) == {
            "pkg-filing": "FILING_PREP:case-a",
            "pkg-oa": "OA_REPLY:doc-oa-1",
            "pkg-other": None,
        }
    finally:
        if engine is not None:
            engine.dispose()
        get_settings.cache_clear()


@pytest.mark.parametrize(
    ("packages", "duplicate_key"),
    [
        (
            [
                ("pkg-filing-1", "case-a", "FILING_PREP", None),
                ("pkg-filing-2", "case-a", "FILING_PREP", None),
            ],
            "FILING_PREP:case-a",
        ),
        (
            [
                ("pkg-oa-1", "case-a", "OA_REPLY", "doc-oa-1"),
                ("pkg-oa-2", "case-a", "OA_REPLY", "doc-oa-1"),
            ],
            "OA_REPLY:doc-oa-1",
        ),
    ],
)
def test_duplicate_identity_preflight_fails_before_schema_mutation(
    tmp_path,
    monkeypatch,
    packages,
    duplicate_key,
) -> None:
    db_path = tmp_path / f"duplicate_{duplicate_key.split(':', 1)[0].lower()}.db"
    config = _alembic_config(db_path, monkeypatch)
    engine = None
    try:
        command.upgrade(config, DOWN_REVISION)
        engine = create_engine(f"sqlite:///{db_path}", future=True)
        with engine.begin() as connection:
            connection.execute(
                text(
                    """
                    INSERT INTO t_official_work_package
                        (id, case_id, package_kind, source_document_id)
                    VALUES
                        (:id, :case_id, :package_kind, :source_document_id)
                    """
                ),
                [
                    {
                        "id": package_id,
                        "case_id": case_id,
                        "package_kind": package_kind,
                        "source_document_id": source_document_id,
                    }
                    for package_id, case_id, package_kind, source_document_id in packages
                ],
            )

        with pytest.raises(RuntimeError, match=duplicate_key):
            command.upgrade(config, "head")

        assert "resolve_key" not in {
            column["name"] for column in inspect(engine).get_columns("t_official_work_package")
        }
        with engine.connect() as connection:
            assert (
                connection.execute(text("SELECT version_num FROM alembic_version")).scalar_one()
                == DOWN_REVISION
            )
    finally:
        if engine is not None:
            engine.dispose()
        get_settings.cache_clear()


def test_oa_package_without_source_identity_fails_before_schema_mutation(
    tmp_path,
    monkeypatch,
) -> None:
    db_path = tmp_path / "missing_oa_source.db"
    config = _alembic_config(db_path, monkeypatch)
    engine = None
    try:
        command.upgrade(config, DOWN_REVISION)
        engine = create_engine(f"sqlite:///{db_path}", future=True)
        with engine.begin() as connection:
            connection.execute(
                text(
                    """
                    INSERT INTO t_official_work_package
                        (id, case_id, package_kind, source_document_id)
                    VALUES ('pkg-oa-missing', 'case-a', 'OA_REPLY', NULL)
                    """
                )
            )

        with pytest.raises(RuntimeError, match="pkg-oa-missing.*source_document_id"):
            command.upgrade(config, "head")

        assert "resolve_key" not in {
            column["name"] for column in inspect(engine).get_columns("t_official_work_package")
        }
        with engine.connect() as connection:
            assert (
                connection.execute(text("SELECT version_num FROM alembic_version")).scalar_one()
                == DOWN_REVISION
            )
    finally:
        if engine is not None:
            engine.dispose()
        get_settings.cache_clear()


def test_unique_index_rejects_duplicate_resolve_key(tmp_path, monkeypatch) -> None:
    db_path = tmp_path / "duplicate_resolve_key.db"
    config = _alembic_config(db_path, monkeypatch)
    engine = None
    try:
        command.upgrade(config, "head")
        engine = create_engine(f"sqlite:///{db_path}", future=True)
        insert = text(
            """
            INSERT INTO t_official_work_package
                (id, case_id, package_kind, resolve_key)
            VALUES (:id, :case_id, 'OTHER_KIND', 'FILING_PREP:case-a')
            """
        )
        with engine.begin() as connection:
            connection.execute(insert, {"id": "pkg-first", "case_id": "case-a"})

        with pytest.raises(IntegrityError):
            with engine.begin() as connection:
                connection.execute(insert, {"id": "pkg-second", "case_id": "case-b"})
    finally:
        if engine is not None:
            engine.dispose()
        get_settings.cache_clear()
