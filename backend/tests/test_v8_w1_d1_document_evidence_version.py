from __future__ import annotations

from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKeyConstraint,
    Integer,
    String,
    UniqueConstraint,
    create_engine,
    event,
    inspect,
    text,
)
from sqlalchemy.exc import IntegrityError

from app.core.config import get_settings
from app.db.base import Base
from app.modules.documents import models as document_models

REVISION = "v8_w1_d1_doc_evidence_version_01"
DOWN_REVISION = "v8_w1_l3_activity_evidence_01"
TABLE = "t_document_evidence_version"

COLUMN_SPECS = {
    "id": (String, 36, False, None),
    "case_id": (String, 36, False, None),
    "document_id": (String, 36, False, None),
    "attachment_id": (String, 36, False, None),
    "lineage_key": (String, 128, False, None),
    "role": (String, 64, False, None),
    "version_number": (Integer, None, False, None),
    "state": (String, 32, False, None),
    "creator_id": (String, 36, False, None),
    "review_state": (String, 32, False, None),
    "reviewer_id": (String, 36, True, None),
    "reviewed_at": (DateTime, None, True, None),
    "final_submitted_at": (DateTime, None, True, None),
    "content_hash": (String, 128, False, None),
    "current_identity_key": (String, 256, True, None),
    "created_at": (DateTime, None, False, "CURRENT_TIMESTAMP"),
    "updated_at": (DateTime, None, False, "CURRENT_TIMESTAMP"),
}

UNIQUE_SPECS = {"uq_t_document_evidence_version_current_identity_key": ("current_identity_key",)}

FOREIGN_KEY_SPECS = {
    "fk_t_document_evidence_version_case_id": (
        ("case_id",),
        "t_case",
        ("id",),
        "CASCADE",
    ),
    "fk_t_document_evidence_version_document_id": (
        ("document_id",),
        "t_document",
        ("id",),
        "CASCADE",
    ),
    "fk_t_document_evidence_version_attachment_id": (
        ("attachment_id",),
        "t_doc_attachment",
        ("id",),
        None,
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
            "file_path": f"/evidence/{attachment_id}.pdf",
        },
    )


def _insert_version(
    connection,
    *,
    version_id: str,
    case_id: str,
    document_id: str,
    attachment_id: str,
    version_number: int,
    current_identity_key: str | None,
) -> None:
    connection.execute(
        text(
            f"""
            INSERT INTO {TABLE}
                (id, case_id, document_id, attachment_id, lineage_key, role,
                 version_number, state, creator_id, review_state, content_hash,
                 current_identity_key)
            VALUES
                (:id, :case_id, :document_id, :attachment_id, 'filing-main',
                 'FILING_DRAFT', :version_number, 'WORKING', 'creator-1',
                 'PENDING', :content_hash, :current_identity_key)
            """
        ),
        {
            "id": version_id,
            "case_id": case_id,
            "document_id": document_id,
            "attachment_id": attachment_id,
            "version_number": version_number,
            "content_hash": f"sha256:{version_id}",
            "current_identity_key": current_identity_key,
        },
    )


def _seed_source_rows(connection) -> None:
    _insert_case(connection, case_id="case-a")
    _insert_document(connection, document_id="document-a", case_id="case-a")
    _insert_attachment(
        connection,
        attachment_id="attachment-a",
        document_id="document-a",
    )


def test_document_evidence_version_model_matches_frozen_contract(tmp_path) -> None:
    model = getattr(document_models, "DocumentEvidenceVersion", None)
    assert model is not None
    assert model.__tablename__ == TABLE
    assert set(model.__table__.columns.keys()) == set(COLUMN_SPECS)

    columns = model.__table__.c
    for name, (expected_type, length, nullable, server_default) in COLUMN_SPECS.items():
        column = columns[name]
        assert isinstance(column.type, expected_type)
        assert getattr(column.type, "length", None) == length
        assert column.nullable is nullable
        assert getattr(column.type, "timezone", False) is False
        if server_default is None:
            assert column.server_default is None
        else:
            assert column.server_default is not None
            assert getattr(column.server_default.arg, "text", None) == server_default

    assert columns.id.default is not None
    assert "created_by" not in columns
    assert "updated_by" not in columns

    unique_specs = {
        constraint.name: tuple(column.name for column in constraint.columns)
        for constraint in model.__table__.constraints
        if isinstance(constraint, UniqueConstraint)
    }
    assert unique_specs == UNIQUE_SPECS

    foreign_key_specs = {
        constraint.name: (
            tuple(element.parent.name for element in constraint.elements),
            constraint.referred_table.name,
            tuple(element.column.name for element in constraint.elements),
            constraint.ondelete,
        )
        for constraint in model.__table__.constraints
        if isinstance(constraint, ForeignKeyConstraint)
    }
    assert foreign_key_specs == FOREIGN_KEY_SPECS
    assert not any(
        isinstance(constraint, CheckConstraint) for constraint in model.__table__.constraints
    )
    assert not model.__table__.indexes

    engine = _sqlite_engine(tmp_path / "v8_w1_d1_model.db")
    try:
        Base.metadata.create_all(engine)
        assert TABLE in inspect(engine).get_table_names()
    finally:
        engine.dispose()


def test_clean_sqlite_upgrade_creates_exact_document_evidence_version_schema(
    tmp_path,
    monkeypatch,
) -> None:
    db_path = tmp_path / "v8_w1_d1_migration.db"
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
        assert set(columns) == set(COLUMN_SPECS)

        for name, (expected_type, length, nullable, server_default) in COLUMN_SPECS.items():
            column = columns[name]
            assert isinstance(column["type"], expected_type)
            assert getattr(column["type"], "length", None) == length
            assert column["nullable"] is nullable
            assert column["default"] == server_default

        assert tuple(inspector.get_pk_constraint(TABLE)["constrained_columns"]) == ("id",)
        assert {
            item["name"]: tuple(item["column_names"])
            for item in inspector.get_unique_constraints(TABLE)
        } == UNIQUE_SPECS
        assert {
            item["name"]: (
                tuple(item["constrained_columns"]),
                item["referred_table"],
                tuple(item["referred_columns"]),
                item.get("options", {}).get("ondelete"),
            )
            for item in inspector.get_foreign_keys(TABLE)
        } == FOREIGN_KEY_SPECS
        assert inspector.get_indexes(TABLE) == []
        assert inspector.get_check_constraints(TABLE) == []
    finally:
        if engine is not None:
            engine.dispose()
        get_settings.cache_clear()


def test_all_three_parent_foreign_keys_are_enforced(tmp_path, monkeypatch) -> None:
    db_path = tmp_path / "v8_w1_d1_foreign_keys.db"
    config = _alembic_config(db_path, monkeypatch)
    engine = None
    try:
        command.upgrade(config, "head")
        engine = _sqlite_engine(db_path)
        with engine.begin() as connection:
            _seed_source_rows(connection)
            _insert_version(
                connection,
                version_id="version-valid",
                case_id="case-a",
                document_id="document-a",
                attachment_id="attachment-a",
                version_number=1,
                current_identity_key="case-a|filing-main",
            )

        for version_id, case_id, document_id, attachment_id in (
            ("version-missing-case", "missing-case", "document-a", "attachment-a"),
            ("version-missing-document", "case-a", "missing-document", "attachment-a"),
            ("version-missing-attachment", "case-a", "document-a", "missing-attachment"),
        ):
            with pytest.raises(IntegrityError):
                with engine.begin() as connection:
                    _insert_version(
                        connection,
                        version_id=version_id,
                        case_id=case_id,
                        document_id=document_id,
                        attachment_id=attachment_id,
                        version_number=2,
                        current_identity_key=None,
                    )
    finally:
        if engine is not None:
            engine.dispose()
        get_settings.cache_clear()


def test_current_identity_rejects_duplicate_non_null_and_accepts_multiple_nulls(
    tmp_path,
    monkeypatch,
) -> None:
    db_path = tmp_path / "v8_w1_d1_current_identity.db"
    config = _alembic_config(db_path, monkeypatch)
    engine = None
    try:
        command.upgrade(config, "head")
        engine = _sqlite_engine(db_path)
        with engine.begin() as connection:
            _seed_source_rows(connection)
            _insert_version(
                connection,
                version_id="version-current",
                case_id="case-a",
                document_id="document-a",
                attachment_id="attachment-a",
                version_number=1,
                current_identity_key="case-a|filing-main",
            )
            _insert_version(
                connection,
                version_id="version-history-1",
                case_id="case-a",
                document_id="document-a",
                attachment_id="attachment-a",
                version_number=2,
                current_identity_key=None,
            )
            _insert_version(
                connection,
                version_id="version-history-2",
                case_id="case-a",
                document_id="document-a",
                attachment_id="attachment-a",
                version_number=3,
                current_identity_key=None,
            )

        with pytest.raises(IntegrityError):
            with engine.begin() as connection:
                _insert_version(
                    connection,
                    version_id="version-duplicate-current",
                    case_id="case-a",
                    document_id="document-a",
                    attachment_id="attachment-a",
                    version_number=4,
                    current_identity_key="case-a|filing-main",
                )
    finally:
        if engine is not None:
            engine.dispose()
        get_settings.cache_clear()


def test_document_evidence_version_migration_is_forward_only(tmp_path, monkeypatch) -> None:
    config = _alembic_config(tmp_path / "v8_w1_d1_forward_only.db", monkeypatch)
    migration = ScriptDirectory.from_config(config).get_revision(REVISION)

    assert migration is not None
    with pytest.raises(NotImplementedError, match="forward-only"):
        migration.module.downgrade()
