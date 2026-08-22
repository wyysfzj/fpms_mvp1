from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKeyConstraint,
    String,
    Text,
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

REVISION = "v8_w1_d2_evidence_derivation_01"
DOWN_REVISION = "v8_w1_d1_doc_evidence_version_01"
TABLE = "t_document_evidence_derivation"

COLUMN_SPECS = {
    "id": (String, 36, False, None),
    "case_id": (String, 36, False, None),
    "parent_evidence_version_id": (String, 36, False, None),
    "child_evidence_version_id": (String, 36, False, None),
    "derivation_type": (String, 64, False, None),
    "actor_id": (String, 36, False, None),
    "derived_at": (DateTime, None, False, None),
    "source_snapshot": (Text, None, False, None),
    "created_at": (DateTime, None, False, "CURRENT_TIMESTAMP"),
    "updated_at": (DateTime, None, False, "CURRENT_TIMESTAMP"),
}

FOREIGN_KEY_SPECS = {
    "fk_t_document_evidence_derivation_case_id": (
        ("case_id",),
        "t_case",
        ("id",),
        "CASCADE",
    ),
    "fk_t_document_evidence_derivation_parent_evidence_version_id": (
        ("parent_evidence_version_id",),
        "t_document_evidence_version",
        ("id",),
        None,
    ),
    "fk_t_document_evidence_derivation_child_evidence_version_id": (
        ("child_evidence_version_id",),
        "t_document_evidence_version",
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
) -> None:
    connection.execute(
        text(
            """
            INSERT INTO t_document_evidence_version
                (id, case_id, document_id, attachment_id, lineage_key, role,
                 version_number, state, creator_id, review_state, content_hash)
            VALUES
                (:id, :case_id, :document_id, :attachment_id, 'filing-main',
                 'FILING_DRAFT', :version_number, 'WORKING', 'creator-1',
                 'PENDING', :content_hash)
            """
        ),
        {
            "id": version_id,
            "case_id": case_id,
            "document_id": document_id,
            "attachment_id": attachment_id,
            "version_number": version_number,
            "content_hash": f"sha256:{version_id}",
        },
    )


def _insert_derivation(
    connection,
    *,
    derivation_id: str,
    case_id: str,
    parent_id: str,
    child_id: str,
) -> None:
    connection.execute(
        text(
            f"""
            INSERT INTO {TABLE}
                (id, case_id, parent_evidence_version_id,
                 child_evidence_version_id, derivation_type, actor_id,
                 derived_at, source_snapshot)
            VALUES
                (:id, :case_id, :parent_id, :child_id, 'PDF_TO_XML',
                 'actor-1', :derived_at, '{{"source":"parent"}}')
            """
        ),
        {
            "id": derivation_id,
            "case_id": case_id,
            "parent_id": parent_id,
            "child_id": child_id,
            "derived_at": datetime(2026, 7, 13, 11, 30, 0),
        },
    )


def _seed_versions(connection) -> None:
    _insert_case(connection, case_id="case-a")
    _insert_document(connection, document_id="document-a", case_id="case-a")
    _insert_attachment(
        connection,
        attachment_id="attachment-a",
        document_id="document-a",
    )
    _insert_version(
        connection,
        version_id="version-parent",
        case_id="case-a",
        document_id="document-a",
        attachment_id="attachment-a",
        version_number=1,
    )
    _insert_version(
        connection,
        version_id="version-child",
        case_id="case-a",
        document_id="document-a",
        attachment_id="attachment-a",
        version_number=2,
    )


def test_document_evidence_derivation_model_matches_frozen_contract(tmp_path) -> None:
    model = getattr(document_models, "DocumentEvidenceDerivation", None)
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
        isinstance(constraint, UniqueConstraint) for constraint in model.__table__.constraints
    )
    assert not any(
        isinstance(constraint, CheckConstraint) for constraint in model.__table__.constraints
    )
    assert not model.__table__.indexes

    engine = _sqlite_engine(tmp_path / "v8_w1_d2_model.db")
    try:
        Base.metadata.create_all(engine)
        assert TABLE in inspect(engine).get_table_names()
    finally:
        engine.dispose()


def test_clean_sqlite_upgrade_creates_exact_document_evidence_derivation_schema(
    tmp_path,
    monkeypatch,
) -> None:
    db_path = tmp_path / "v8_w1_d2_migration.db"
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
            item["name"]: (
                tuple(item["constrained_columns"]),
                item["referred_table"],
                tuple(item["referred_columns"]),
                item.get("options", {}).get("ondelete"),
            )
            for item in inspector.get_foreign_keys(TABLE)
        } == FOREIGN_KEY_SPECS
        assert inspector.get_unique_constraints(TABLE) == []
        assert inspector.get_indexes(TABLE) == []
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


def test_missing_parent_or_child_evidence_version_is_rejected(tmp_path, monkeypatch) -> None:
    db_path = tmp_path / "v8_w1_d2_foreign_keys.db"
    config = _alembic_config(db_path, monkeypatch)
    engine = None
    try:
        command.upgrade(config, "head")
        engine = _sqlite_engine(db_path)
        with engine.begin() as connection:
            _seed_versions(connection)
            _insert_derivation(
                connection,
                derivation_id="derivation-valid",
                case_id="case-a",
                parent_id="version-parent",
                child_id="version-child",
            )

        for derivation_id, parent_id, child_id in (
            ("derivation-missing-parent", "missing-parent", "version-child"),
            ("derivation-missing-child", "version-parent", "missing-child"),
        ):
            with pytest.raises(IntegrityError):
                with engine.begin() as connection:
                    _insert_derivation(
                        connection,
                        derivation_id=derivation_id,
                        case_id="case-a",
                        parent_id=parent_id,
                        child_id=child_id,
                    )
    finally:
        if engine is not None:
            engine.dispose()
        get_settings.cache_clear()


def test_duplicate_derivation_edges_are_not_schema_constrained(tmp_path, monkeypatch) -> None:
    db_path = tmp_path / "v8_w1_d2_no_edge_unique.db"
    config = _alembic_config(db_path, monkeypatch)
    engine = None
    try:
        command.upgrade(config, "head")
        engine = _sqlite_engine(db_path)
        with engine.begin() as connection:
            _seed_versions(connection)
            _insert_derivation(
                connection,
                derivation_id="derivation-1",
                case_id="case-a",
                parent_id="version-parent",
                child_id="version-child",
            )
            _insert_derivation(
                connection,
                derivation_id="derivation-2",
                case_id="case-a",
                parent_id="version-parent",
                child_id="version-child",
            )
    finally:
        if engine is not None:
            engine.dispose()
        get_settings.cache_clear()


def test_document_evidence_derivation_migration_is_forward_only(tmp_path, monkeypatch) -> None:
    config = _alembic_config(tmp_path / "v8_w1_d2_forward_only.db", monkeypatch)
    migration = ScriptDirectory.from_config(config).get_revision(REVISION)

    assert migration is not None
    with pytest.raises(NotImplementedError, match="forward-only"):
        migration.module.downgrade()
