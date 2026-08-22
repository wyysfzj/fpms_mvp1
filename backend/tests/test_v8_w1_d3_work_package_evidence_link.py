from __future__ import annotations

from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import (
    CheckConstraint,
    String,
    UniqueConstraint,
    create_engine,
    event,
    inspect,
    text,
)
from sqlalchemy.exc import IntegrityError

from app.core.config import get_settings
from app.modules.official_workflows import models as workflow_models

REVISION = "v8_w1_d3_workpkg_evidence_01"
DOWN_REVISION = "v8_w1_d2_evidence_derivation_01"
TABLE = "t_official_work_package_manifest"

LEGACY_COLUMNS = {
    "id",
    "package_id",
    "attachment_id",
    "official_file_role",
    "source_role_alias",
    "external_upload_position",
    "content_hash",
    "required",
    "present",
    "sort_order",
    "note",
    "created_at",
    "updated_at",
    "created_by",
    "updated_by",
}
EVIDENCE_COLUMN = "evidence_version_id"

INDEX_SPECS = {
    "ix_t_official_work_package_manifest_package_id": (("package_id",), False),
    "ix_t_official_work_package_manifest_attachment_id": (("attachment_id",), False),
    "ix_t_official_work_package_manifest_evidence_version_id": (
        ("evidence_version_id",),
        False,
    ),
}


def _sqlite_engine(db_path: Path):
    engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False},
        future=True,
    )

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, _connection_record) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    return engine


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


def _insert_case(connection, *, case_id: str) -> None:
    connection.execute(
        text("INSERT INTO t_case (id, case_no) VALUES (:id, :case_no)"),
        {"id": case_id, "case_no": case_id},
    )


def _insert_package(connection, *, package_id: str, case_id: str) -> None:
    connection.execute(
        text(
            """
            INSERT INTO t_official_work_package (id, case_id, package_kind)
            VALUES (:id, :case_id, 'FILING')
            """
        ),
        {"id": package_id, "case_id": case_id},
    )


def _insert_document(connection, *, document_id: str, case_id: str) -> None:
    connection.execute(
        text("INSERT INTO t_document (id, case_id) VALUES (:id, :case_id)"),
        {"id": document_id, "case_id": case_id},
    )


def _insert_attachment(connection, *, attachment_id: str, document_id: str) -> None:
    connection.execute(
        text(
            """
            INSERT INTO t_doc_attachment (id, document_id, file_name, file_path)
            VALUES (:id, :document_id, :file_name, :file_path)
            """
        ),
        {
            "id": attachment_id,
            "document_id": document_id,
            "file_name": f"{attachment_id}.pdf",
            "file_path": f"/legacy/{attachment_id}.pdf",
        },
    )


def _model_fk_spec(column) -> tuple[str, str | None]:
    foreign_keys = tuple(column.foreign_keys)
    assert len(foreign_keys) == 1
    foreign_key = foreign_keys[0]
    return foreign_key.target_fullname, foreign_key.ondelete


def _reflected_fk_by_column(inspector) -> dict[str, dict]:
    foreign_keys = inspector.get_foreign_keys(TABLE)
    assert len(foreign_keys) == 3
    return {item["constrained_columns"][0]: item for item in foreign_keys}


def test_manifest_model_adds_only_frozen_evidence_version_link() -> None:
    model = workflow_models.OfficialWorkPackageManifest
    assert set(model.__table__.columns.keys()) == LEGACY_COLUMNS | {EVIDENCE_COLUMN}

    evidence_column = model.__table__.c.evidence_version_id
    assert isinstance(evidence_column.type, String)
    assert evidence_column.type.length == 36
    assert evidence_column.nullable is True
    assert evidence_column.default is None
    assert evidence_column.server_default is None
    assert _model_fk_spec(evidence_column) == ("t_document_evidence_version.id", None)
    assert next(iter(evidence_column.foreign_keys)).constraint.name == (
        "fk_t_official_work_package_manifest_evidence_version_id"
    )

    attachment_column = model.__table__.c.attachment_id
    assert isinstance(attachment_column.type, String)
    assert attachment_column.type.length == 36
    assert attachment_column.nullable is True
    assert attachment_column.default is None
    assert attachment_column.server_default is None
    assert _model_fk_spec(attachment_column) == ("t_doc_attachment.id", None)

    assert {
        index.name: (tuple(column.name for column in index.columns), index.unique)
        for index in model.__table__.indexes
    } == INDEX_SPECS
    assert not any(
        isinstance(constraint, UniqueConstraint) for constraint in model.__table__.constraints
    )
    assert not any(
        isinstance(constraint, CheckConstraint) for constraint in model.__table__.constraints
    )
    assert "evidence_version" not in model.__mapper__.relationships


def test_d3_upgrade_preserves_preexisting_non_null_attachment_manifest(
    tmp_path,
    monkeypatch,
) -> None:
    db_path = tmp_path / "v8_w1_d3_legacy_attachment.db"
    config = _alembic_config(db_path, monkeypatch)
    engine = None
    try:
        command.upgrade(config, DOWN_REVISION)
        engine = _sqlite_engine(db_path)
        with engine.begin() as connection:
            _insert_case(connection, case_id="case-legacy")
            _insert_document(
                connection,
                document_id="document-legacy",
                case_id="case-legacy",
            )
            _insert_attachment(
                connection,
                attachment_id="attachment-legacy",
                document_id="document-legacy",
            )
            _insert_package(
                connection,
                package_id="package-legacy",
                case_id="case-legacy",
            )
            connection.execute(
                text(
                    f"""
                    INSERT INTO {TABLE} (id, package_id, attachment_id)
                    VALUES ('manifest-legacy-attachment', 'package-legacy',
                            'attachment-legacy')
                    """
                )
            )

        assert EVIDENCE_COLUMN not in {
            column["name"] for column in inspect(engine).get_columns(TABLE)
        }
        with engine.connect() as connection:
            pre_upgrade_row = (
                connection.execute(
                    text(
                        f"""
                    SELECT id, package_id, attachment_id
                    FROM {TABLE}
                    WHERE id = 'manifest-legacy-attachment'
                    """
                    )
                )
                .mappings()
                .one()
            )
        assert dict(pre_upgrade_row) == {
            "id": "manifest-legacy-attachment",
            "package_id": "package-legacy",
            "attachment_id": "attachment-legacy",
        }

        engine.dispose()
        engine = None
        command.upgrade(config, REVISION)

        engine = _sqlite_engine(db_path)
        with engine.connect() as connection:
            post_upgrade_row = (
                connection.execute(
                    text(
                        f"""
                    SELECT id, package_id, attachment_id, evidence_version_id
                    FROM {TABLE}
                    WHERE id = 'manifest-legacy-attachment'
                    """
                    )
                )
                .mappings()
                .one()
            )
        assert dict(post_upgrade_row) == {
            "id": "manifest-legacy-attachment",
            "package_id": "package-legacy",
            "attachment_id": "attachment-legacy",
            "evidence_version_id": None,
        }
    finally:
        if engine is not None:
            engine.dispose()
        get_settings.cache_clear()


def test_clean_sqlite_upgrade_preserves_manifest_and_adds_exact_link(
    tmp_path,
    monkeypatch,
) -> None:
    db_path = tmp_path / "v8_w1_d3_migration.db"
    config = _alembic_config(db_path, monkeypatch)
    engine = None
    try:
        migration = ScriptDirectory.from_config(config).get_revision(REVISION)
        assert migration is not None
        assert migration.down_revision == DOWN_REVISION

        command.upgrade(config, "head")
        engine = _sqlite_engine(db_path)
        inspector = inspect(engine)
        columns = {column["name"]: column for column in inspector.get_columns(TABLE)}
        assert set(columns) == LEGACY_COLUMNS | {EVIDENCE_COLUMN}

        evidence_column = columns[EVIDENCE_COLUMN]
        assert isinstance(evidence_column["type"], String)
        assert evidence_column["type"].length == 36
        assert evidence_column["nullable"] is True
        assert evidence_column["default"] is None

        attachment_column = columns["attachment_id"]
        assert isinstance(attachment_column["type"], String)
        assert attachment_column["type"].length == 36
        assert attachment_column["nullable"] is True
        assert attachment_column["default"] is None

        foreign_keys = _reflected_fk_by_column(inspector)
        evidence_fk = foreign_keys[EVIDENCE_COLUMN]
        assert evidence_fk["name"] == "fk_t_official_work_package_manifest_evidence_version_id"
        assert evidence_fk["referred_table"] == "t_document_evidence_version"
        assert tuple(evidence_fk["referred_columns"]) == ("id",)
        assert evidence_fk.get("options", {}).get("ondelete") is None

        attachment_fk = foreign_keys["attachment_id"]
        assert attachment_fk["referred_table"] == "t_doc_attachment"
        assert tuple(attachment_fk["referred_columns"]) == ("id",)
        assert attachment_fk.get("options", {}).get("ondelete") is None

        assert {
            item["name"]: (tuple(item["column_names"]), item["unique"])
            for item in inspector.get_indexes(TABLE)
        } == INDEX_SPECS
        assert inspector.get_unique_constraints(TABLE) == []
        assert inspector.get_check_constraints(TABLE) == []
        with engine.connect() as connection:
            triggers = connection.execute(
                text(
                    """
                    SELECT name FROM sqlite_master
                    WHERE type = 'trigger' AND tbl_name = :table_name
                    """
                ),
                {"table_name": TABLE},
            ).all()
        assert triggers == []
    finally:
        if engine is not None:
            engine.dispose()
        get_settings.cache_clear()


def test_legacy_null_link_is_accepted_and_missing_evidence_version_is_rejected(
    tmp_path,
    monkeypatch,
) -> None:
    db_path = tmp_path / "v8_w1_d3_foreign_key.db"
    config = _alembic_config(db_path, monkeypatch)
    engine = None
    try:
        command.upgrade(config, "head")
        engine = _sqlite_engine(db_path)
        with engine.begin() as connection:
            _insert_case(connection, case_id="case-a")
            _insert_package(connection, package_id="package-a", case_id="case-a")
            connection.execute(
                text(
                    f"""
                    INSERT INTO {TABLE} (id, package_id, attachment_id, evidence_version_id)
                    VALUES ('manifest-legacy', 'package-a', NULL, NULL)
                    """
                )
            )

        with pytest.raises(IntegrityError):
            with engine.begin() as connection:
                connection.execute(
                    text(
                        f"""
                        INSERT INTO {TABLE} (id, package_id, evidence_version_id)
                        VALUES ('manifest-missing-evidence', 'package-a', 'missing-version')
                        """
                    )
                )
    finally:
        if engine is not None:
            engine.dispose()
        get_settings.cache_clear()


def test_work_package_evidence_link_migration_is_forward_only(tmp_path, monkeypatch) -> None:
    config = _alembic_config(tmp_path / "v8_w1_d3_forward_only.db", monkeypatch)
    migration = ScriptDirectory.from_config(config).get_revision(REVISION)

    assert migration is not None
    with pytest.raises(NotImplementedError, match="forward-only"):
        migration.module.downgrade()
