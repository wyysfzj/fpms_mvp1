from __future__ import annotations

from datetime import date
from pathlib import Path
from uuid import UUID

import pytest
from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKeyConstraint,
    Index,
    String,
    Text,
    UniqueConstraint,
    create_engine,
    event,
    inspect,
    text,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.mixins import AuditMixin
from app.modules.auth import models as auth_models
from app.modules.fees import models as fee_models

REVISION = "v8_w4_official_rate_book_01"
DOWN_REVISION = "v8_post_w1_customer_decision_gate_01"
CURRENT_HEAD = "v8_d31_overlay_conflict_01"
TABLE = "t_fee_rate_book"
RATE_TABLE = "t_fee_rate"

COLUMNS = (
    "id",
    "book_code",
    "version_code",
    "source_authority",
    "source_reference",
    "source_version",
    "source_published_on",
    "source_snapshot",
    "source_snapshot_hash",
    "approval_status",
    "approved_by",
    "approved_at",
    "effective_from",
    "effective_to",
    "activation_status",
    "activated_by",
    "activated_at",
    "current_identity_key",
    "created_at",
    "updated_at",
    "created_by",
    "updated_by",
)

STRING_LENGTHS = {
    "id": 36,
    "book_code": 64,
    "version_code": 128,
    "source_authority": 32,
    "source_reference": 512,
    "source_version": 128,
    "source_snapshot_hash": 64,
    "approval_status": 32,
    "approved_by": 36,
    "activation_status": 32,
    "activated_by": 36,
    "current_identity_key": 128,
    "created_by": 36,
    "updated_by": 36,
}

NULLABILITY = {
    "id": False,
    "book_code": False,
    "version_code": False,
    "source_authority": False,
    "source_reference": False,
    "source_version": False,
    "source_published_on": False,
    "source_snapshot": False,
    "source_snapshot_hash": False,
    "approval_status": False,
    "approved_by": True,
    "approved_at": True,
    "effective_from": False,
    "effective_to": True,
    "activation_status": False,
    "activated_by": True,
    "activated_at": True,
    "current_identity_key": True,
    "created_at": False,
    "updated_at": False,
    "created_by": True,
    "updated_by": True,
}

SERVER_DEFAULTS = {
    "approval_status": "'PENDING'",
    "activation_status": "'INACTIVE'",
    "created_at": "CURRENT_TIMESTAMP",
    "updated_at": "CURRENT_TIMESTAMP",
}

UNIQUE_SPECS = {
    "uq_t_fee_rate_book_series_version": (
        "source_authority",
        "book_code",
        "version_code",
    ),
    "uq_t_fee_rate_book_current_identity_key": ("current_identity_key",),
}

FOREIGN_KEY_SPECS = {
    "fk_t_fee_rate_book_approved_by": (
        ("approved_by",),
        ("t_user.id",),
        "RESTRICT",
    ),
    "fk_t_fee_rate_book_activated_by": (
        ("activated_by",),
        ("t_user.id",),
        "RESTRICT",
    ),
}

CHECK_SPECS = {
    "ck_t_fee_rate_book_source_authority": "source_authority = 'CNIPA'",
    "ck_t_fee_rate_book_source_hash": "length(source_snapshot_hash) = 64",
    "ck_t_fee_rate_book_effective_interval": (
        "effective_to IS NULL OR effective_to >= effective_from"
    ),
    "ck_t_fee_rate_book_approval_status": (
        "approval_status IN ('PENDING', 'APPROVED', 'REJECTED')"
    ),
    "ck_t_fee_rate_book_approval_tuple": (
        "(approval_status = 'PENDING' AND approved_by IS NULL AND approved_at IS NULL) "
        "OR (approval_status IN ('APPROVED', 'REJECTED') "
        "AND approved_by IS NOT NULL AND approved_at IS NOT NULL)"
    ),
    "ck_t_fee_rate_book_activation_status": (
        "activation_status IN ('INACTIVE', 'ACTIVE', 'RETIRED')"
    ),
    "ck_t_fee_rate_book_activation_tuple": (
        "(activation_status = 'INACTIVE' AND activated_by IS NULL "
        "AND activated_at IS NULL AND current_identity_key IS NULL) "
        "OR (activation_status = 'ACTIVE' AND approval_status = 'APPROVED' "
        "AND approved_by IS NOT NULL AND approved_at IS NOT NULL "
        "AND activated_by IS NOT NULL AND activated_at IS NOT NULL "
        "AND current_identity_key = source_authority || '|' || book_code) "
        "OR (activation_status = 'RETIRED' AND approval_status = 'APPROVED' "
        "AND approved_by IS NOT NULL AND approved_at IS NOT NULL "
        "AND activated_by IS NOT NULL AND activated_at IS NOT NULL "
        "AND current_identity_key IS NULL)"
    ),
}

INDEX_SPECS = {
    "ix_t_fee_rate_book_series_interval": (
        "source_authority",
        "book_code",
        "activation_status",
        "effective_from",
        "effective_to",
    ),
}

RATE_LINK_FK_SPEC = {
    "fk_t_fee_rate_official_rate_book_id": (
        ("official_rate_book_id",),
        ("t_fee_rate_book.id",),
        "RESTRICT",
    )
}

RATE_LINK_CHECK_SPEC = {
    "ck_t_fee_rate_official_book_gov_only": ("official_rate_book_id IS NULL OR fee_type = 'GOV'")
}

RATE_LINK_INDEX_SPEC = {"ix_t_fee_rate_official_rate_book_id": ("official_rate_book_id",)}

SYNTHETIC_REFERENCE = "https://www.cnipa.gov.cn/test/synthetic-rate-book"
SYNTHETIC_SNAPSHOT = (
    '{"schema_version":"CNIPA_RATE_SOURCE_V1","sources":['
    '{"content_sha256":"bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",'
    '"document_no":null,"published_on":"2026-07-13",'
    '"retrieved_at":"2026-07-13T00:00:00Z",'
    '"title":"Synthetic schema fixture",'
    f'"url":"{SYNTHETIC_REFERENCE}"}}]}}'
)


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


def _normalized_sql(value) -> str:
    return " ".join(str(value).split())


def _normalized_default(value) -> str | None:
    if value is None:
        return None
    return str(value).strip("()")


def _model_fk_specs(table) -> dict[str, tuple[tuple[str, ...], tuple[str, ...], str | None]]:
    return {
        constraint.name: (
            tuple(element.parent.name for element in constraint.elements),
            tuple(element.target_fullname for element in constraint.elements),
            constraint.ondelete,
        )
        for constraint in table.constraints
        if isinstance(constraint, ForeignKeyConstraint)
    }


def _model_check_specs(table) -> dict[str, str]:
    return {
        constraint.name: _normalized_sql(constraint.sqltext)
        for constraint in table.constraints
        if isinstance(constraint, CheckConstraint)
    }


def _model_index_specs(table) -> dict[str, tuple[str, ...]]:
    return {
        index.name: tuple(column.name for column in index.columns)
        for index in table.indexes
        if isinstance(index, Index) and not index.unique
    }


def _reflected_fk_specs(inspector, table_name: str):
    return {
        item["name"]: (
            tuple(item["constrained_columns"]),
            tuple(f"{item['referred_table']}.{column}" for column in item["referred_columns"]),
            item.get("options", {}).get("ondelete"),
        )
        for item in inspector.get_foreign_keys(table_name)
    }


def _reflected_check_specs(inspector, table_name: str):
    return {
        item["name"]: _normalized_sql(item["sqltext"])
        for item in inspector.get_check_constraints(table_name)
    }


def _reflected_index_specs(inspector, table_name: str):
    return {
        item["name"]: tuple(item["column_names"])
        for item in inspector.get_indexes(table_name)
        if not item.get("unique")
    }


def _insert_user(connection, *, user_id: str = "approver-1") -> None:
    connection.execute(
        text(
            """
            INSERT INTO t_user (id, username, password_hash)
            VALUES (:id, :username, 'not-used')
            """
        ),
        {"id": user_id, "username": user_id},
    )


def _book_values(book_id: str, **overrides) -> dict[str, object]:
    values: dict[str, object] = {
        "id": book_id,
        "book_code": f"SYNTHETIC-{book_id.upper()}",
        "version_code": "SYNTHETIC-V1",
        "source_authority": "CNIPA",
        "source_reference": SYNTHETIC_REFERENCE,
        "source_version": "SYNTHETIC-SCHEMA-FIXTURE",
        "source_published_on": "2026-07-13",
        "source_snapshot": SYNTHETIC_SNAPSHOT,
        "source_snapshot_hash": "a" * 64,
        "approval_status": "PENDING",
        "approved_by": None,
        "approved_at": None,
        "effective_from": "2026-07-13",
        "effective_to": None,
        "activation_status": "INACTIVE",
        "activated_by": None,
        "activated_at": None,
        "current_identity_key": None,
    }
    values.update(overrides)
    return values


def _insert_book(connection, *, book_id: str, **overrides) -> None:
    connection.execute(
        text(
            f"""
            INSERT INTO {TABLE}
                (id, book_code, version_code, source_authority,
                 source_reference, source_version, source_published_on,
                 source_snapshot, source_snapshot_hash, approval_status,
                 approved_by, approved_at, effective_from, effective_to,
                 activation_status, activated_by, activated_at,
                 current_identity_key)
            VALUES
                (:id, :book_code, :version_code, :source_authority,
                 :source_reference, :source_version, :source_published_on,
                 :source_snapshot, :source_snapshot_hash, :approval_status,
                 :approved_by, :approved_at, :effective_from, :effective_to,
                 :activation_status, :activated_by, :activated_at,
                 :current_identity_key)
            """
        ),
        _book_values(book_id, **overrides),
    )


def _insert_fee_rate(
    connection,
    *,
    rate_id: str,
    fee_type: str,
    official_rate_book_id: str | None,
) -> None:
    connection.execute(
        text(
            f"""
            INSERT INTO {RATE_TABLE}
                (id, fee_code, fee_name, fee_type, currency, default_amount,
                 enabled, source_status, official_rate_book_id)
            VALUES
                (:id, :fee_code, :fee_name, :fee_type, 'CNY', NULL,
                 1, 'SYNTHETIC', :official_rate_book_id)
            """
        ),
        {
            "id": rate_id,
            "fee_code": f"SYNTHETIC-{rate_id.upper()}",
            "fee_name": "Synthetic schema fixture",
            "fee_type": fee_type,
            "official_rate_book_id": official_rate_book_id,
        },
    )


def test_official_rate_book_model_matches_exact_frozen_contract() -> None:
    model = getattr(fee_models, "OfficialRateBook", None)
    assert model is not None, "OfficialRateBook ORM carrier is absent"
    table = model.__table__

    assert model.__tablename__ == TABLE
    assert tuple(table.columns.keys()) == COLUMNS
    assert AuditMixin not in model.__mro__
    assert not model.__mapper__.relationships

    for column_name, length in STRING_LENGTHS.items():
        column = table.c[column_name]
        assert isinstance(column.type, String)
        assert column.type.length == length
    assert isinstance(table.c.source_snapshot.type, Text)
    for column_name in ("source_published_on", "effective_from", "effective_to"):
        assert isinstance(table.c[column_name].type, Date)
    for column_name in ("approved_at", "activated_at", "created_at", "updated_at"):
        assert isinstance(table.c[column_name].type, DateTime)
        assert table.c[column_name].type.timezone is False

    assert {column.name: column.nullable for column in table.columns} == NULLABILITY
    assert table.c.id.default is not None
    assert table.c.id.server_default is None
    for column in table.columns:
        if column.name == "id":
            continue
        assert column.default is None
        actual_default = (
            _normalized_default(column.server_default.arg)
            if column.server_default is not None
            else None
        )
        assert actual_default == SERVER_DEFAULTS.get(column.name)

    assert tuple(table.primary_key.columns.keys()) == ("id",)
    assert {
        constraint.name: tuple(constraint.columns.keys())
        for constraint in table.constraints
        if isinstance(constraint, UniqueConstraint)
    } == UNIQUE_SPECS
    assert _model_fk_specs(table) == FOREIGN_KEY_SPECS
    assert _model_check_specs(table) == {
        name: _normalized_sql(sql) for name, sql in CHECK_SPECS.items()
    }
    assert _model_index_specs(table) == INDEX_SPECS


def test_fee_rate_model_has_only_the_frozen_compatibility_link() -> None:
    table = fee_models.FeeRate.__table__
    column = table.c.get("official_rate_book_id")

    assert column is not None, "FeeRate.official_rate_book_id is absent"
    assert isinstance(column.type, String)
    assert column.type.length == 36
    assert column.nullable is True
    assert column.default is None
    assert column.server_default is None
    assert {
        name: spec for name, spec in _model_fk_specs(table).items() if name in RATE_LINK_FK_SPEC
    } == RATE_LINK_FK_SPEC
    assert {
        name: spec
        for name, spec in _model_check_specs(table).items()
        if name in RATE_LINK_CHECK_SPEC
    } == {name: _normalized_sql(sql) for name, sql in RATE_LINK_CHECK_SPEC.items()}
    assert {
        name: spec
        for name, spec in _model_index_specs(table).items()
        if name in RATE_LINK_INDEX_SPEC
    } == RATE_LINK_INDEX_SPEC


def test_migration_identity_is_frozen_reachable_and_forward_only(monkeypatch, tmp_path) -> None:
    config = _alembic_config(tmp_path / "identity.db", monkeypatch)
    script = ScriptDirectory.from_config(config)
    migration = script.get_revision(REVISION)

    assert migration is not None, "official-rate-book migration is absent"
    assert script.get_heads() == [CURRENT_HEAD]
    assert REVISION in {
        item.revision for item in script.walk_revisions(base="base", head=CURRENT_HEAD)
    }
    assert migration.down_revision == DOWN_REVISION
    assert migration.module.revision == REVISION
    assert migration.module.down_revision == DOWN_REVISION
    assert migration.module.branch_labels is None
    assert migration.module.depends_on is None

    with pytest.raises(NotImplementedError, match="This is a forward-only migration"):
        migration.module.downgrade()

    get_settings.cache_clear()


def test_clean_sqlite_upgrade_creates_exact_rate_book_and_link_schema(
    tmp_path,
    monkeypatch,
) -> None:
    db_path = tmp_path / "official_rate_book_clean.db"
    config = _alembic_config(db_path, monkeypatch)
    engine = None
    try:
        command.upgrade(config, "head")
        engine = _sqlite_engine(db_path)
        inspector = inspect(engine)

        columns = inspector.get_columns(TABLE)
        by_name = {column["name"]: column for column in columns}
        assert tuple(column["name"] for column in columns) == COLUMNS
        for column_name, length in STRING_LENGTHS.items():
            assert isinstance(by_name[column_name]["type"], String)
            assert by_name[column_name]["type"].length == length
        assert isinstance(by_name["source_snapshot"]["type"], Text)
        for column_name in ("source_published_on", "effective_from", "effective_to"):
            assert isinstance(by_name[column_name]["type"], Date)
        for column_name in ("approved_at", "activated_at", "created_at", "updated_at"):
            assert isinstance(by_name[column_name]["type"], DateTime)

        assert {name: column["nullable"] for name, column in by_name.items()} == NULLABILITY
        assert {
            name: _normalized_default(column["default"])
            for name, column in by_name.items()
            if column["default"] is not None
        } == SERVER_DEFAULTS
        assert inspector.get_pk_constraint(TABLE)["constrained_columns"] == ["id"]
        assert {
            item["name"]: tuple(item["column_names"])
            for item in inspector.get_unique_constraints(TABLE)
        } == UNIQUE_SPECS
        assert _reflected_fk_specs(inspector, TABLE) == FOREIGN_KEY_SPECS
        assert _reflected_check_specs(inspector, TABLE) == {
            name: _normalized_sql(sql) for name, sql in CHECK_SPECS.items()
        }
        assert _reflected_index_specs(inspector, TABLE) == INDEX_SPECS

        rate_columns = {column["name"]: column for column in inspector.get_columns(RATE_TABLE)}
        link = rate_columns.get("official_rate_book_id")
        assert link is not None
        assert isinstance(link["type"], String)
        assert link["type"].length == 36
        assert link["nullable"] is True
        assert link["default"] is None
        assert {
            name: spec
            for name, spec in _reflected_fk_specs(inspector, RATE_TABLE).items()
            if name in RATE_LINK_FK_SPEC
        } == RATE_LINK_FK_SPEC
        assert {
            name: spec
            for name, spec in _reflected_check_specs(inspector, RATE_TABLE).items()
            if name in RATE_LINK_CHECK_SPEC
        } == {name: _normalized_sql(sql) for name, sql in RATE_LINK_CHECK_SPEC.items()}
        assert {
            name: spec
            for name, spec in _reflected_index_specs(inspector, RATE_TABLE).items()
            if name in RATE_LINK_INDEX_SPEC
        } == RATE_LINK_INDEX_SPEC
    finally:
        if engine is not None:
            engine.dispose()
        get_settings.cache_clear()


def test_application_uuid_appears_after_flush_without_insert_returning(
    tmp_path,
    monkeypatch,
) -> None:
    db_path = tmp_path / "official_rate_book_uuid.db"
    config = _alembic_config(db_path, monkeypatch)
    command.upgrade(config, "head")
    engine = _sqlite_engine(db_path)
    engine.dialect.insert_returning = False
    try:
        with Session(engine) as session:
            candidate = fee_models.OfficialRateBook(
                book_code="SYNTHETIC-UUID",
                version_code="SYNTHETIC-V1",
                source_authority="CNIPA",
                source_reference=SYNTHETIC_REFERENCE,
                source_version="SYNTHETIC-SCHEMA-FIXTURE",
                source_published_on=date(2026, 7, 13),
                source_snapshot=SYNTHETIC_SNAPSHOT,
                source_snapshot_hash="a" * 64,
                effective_from=date(2026, 7, 13),
            )
            session.add(candidate)
            session.flush()

            assert str(UUID(candidate.id)) == candidate.id
            assert len(candidate.id) == 36
            assert (
                session.scalar(
                    text(f"SELECT count(*) FROM {TABLE} WHERE id = :id"),
                    {"id": candidate.id},
                )
                == 1
            )
            session.rollback()
    finally:
        engine.dispose()
        get_settings.cache_clear()


def test_sqlite_constraints_enforce_frozen_carrier_identities_and_tuples(
    tmp_path,
    monkeypatch,
) -> None:
    db_path = tmp_path / "official_rate_book_constraints.db"
    config = _alembic_config(db_path, monkeypatch)
    command.upgrade(config, "head")
    engine = _sqlite_engine(db_path)
    try:
        with engine.begin() as connection:
            _insert_user(connection)
            _insert_book(connection, book_id="valid-inactive")

        invalid_rows = (
            {"book_id": "invalid-authority", "source_authority": "WIPO"},
            {"book_id": "invalid-hash", "source_snapshot_hash": "a" * 63},
            {
                "book_id": "invalid-interval",
                "effective_from": "2026-07-13",
                "effective_to": "2026-07-12",
            },
            {"book_id": "invalid-status", "approval_status": "UNKNOWN"},
            {"book_id": "invalid-approval", "approval_status": "APPROVED"},
            {
                "book_id": "invalid-active-current",
                "approval_status": "APPROVED",
                "approved_by": "approver-1",
                "approved_at": "2026-07-13 10:00:00",
                "activation_status": "ACTIVE",
                "activated_by": "approver-1",
                "activated_at": "2026-07-13 11:00:00",
                "current_identity_key": "WRONG|IDENTITY",
            },
        )
        for kwargs in invalid_rows:
            with pytest.raises(IntegrityError), engine.begin() as connection:
                _insert_book(connection, **kwargs)

        with engine.begin() as connection:
            _insert_book(
                connection,
                book_id="series-original",
                book_code="SYNTHETIC-SERIES",
                version_code="SYNTHETIC-V1",
            )
        with pytest.raises(IntegrityError), engine.begin() as connection:
            _insert_book(
                connection,
                book_id="series-duplicate",
                book_code="SYNTHETIC-SERIES",
                version_code="SYNTHETIC-V1",
            )

        with engine.begin() as connection:
            _insert_book(
                connection,
                book_id="active-original",
                book_code="SYNTHETIC-ACTIVE-SERIES",
                version_code="SYNTHETIC-V1",
                approval_status="APPROVED",
                approved_by="approver-1",
                approved_at="2026-07-13 10:00:00",
                activation_status="ACTIVE",
                activated_by="approver-1",
                activated_at="2026-07-13 11:00:00",
                current_identity_key="CNIPA|SYNTHETIC-ACTIVE-SERIES",
            )
        with pytest.raises(IntegrityError), engine.begin() as connection:
            _insert_book(
                connection,
                book_id="active-duplicate",
                book_code="SYNTHETIC-ACTIVE-SERIES",
                version_code="SYNTHETIC-V2",
                approval_status="APPROVED",
                approved_by="approver-1",
                approved_at="2026-07-13 10:00:00",
                activation_status="ACTIVE",
                activated_by="approver-1",
                activated_at="2026-07-13 11:00:00",
                current_identity_key="CNIPA|SYNTHETIC-ACTIVE-SERIES",
            )

        with engine.begin() as connection:
            _insert_book(
                connection,
                book_id="history-null-1",
                book_code="SYNTHETIC-HISTORY",
                version_code="SYNTHETIC-V1",
            )
            _insert_book(
                connection,
                book_id="history-null-2",
                book_code="SYNTHETIC-HISTORY",
                version_code="SYNTHETIC-V2",
            )
    finally:
        engine.dispose()
        get_settings.cache_clear()


def test_fee_rate_link_is_nullable_gov_only_and_restricts_provenance_deletion(
    tmp_path,
    monkeypatch,
) -> None:
    db_path = tmp_path / "official_rate_book_link.db"
    config = _alembic_config(db_path, monkeypatch)
    command.upgrade(config, "head")
    engine = _sqlite_engine(db_path)
    try:
        with engine.begin() as connection:
            _insert_book(connection, book_id="linked-book")
            _insert_fee_rate(
                connection,
                rate_id="linked-gov-rate",
                fee_type="GOV",
                official_rate_book_id="linked-book",
            )
            linked_book_id = connection.scalar(
                text(f"SELECT official_rate_book_id FROM {RATE_TABLE} WHERE id = 'linked-gov-rate'")
            )
            assert linked_book_id == "linked-book"

        with pytest.raises(IntegrityError), engine.begin() as connection:
            _insert_fee_rate(
                connection,
                rate_id="missing-book-rate",
                fee_type="GOV",
                official_rate_book_id="missing-book",
            )

        with pytest.raises(IntegrityError), engine.begin() as connection:
            _insert_fee_rate(
                connection,
                rate_id="linked-service-rate",
                fee_type="SERVICE",
                official_rate_book_id="linked-book",
            )

        with pytest.raises(IntegrityError), engine.begin() as connection:
            connection.execute(text(f"DELETE FROM {TABLE} WHERE id = 'linked-book'"))
    finally:
        engine.dispose()
        get_settings.cache_clear()


def test_upgrade_from_frozen_predecessor_preserves_all_legacy_fee_rate_values(
    tmp_path,
    monkeypatch,
) -> None:
    db_path = tmp_path / "official_rate_book_legacy.db"
    config = _alembic_config(db_path, monkeypatch)
    command.upgrade(config, DOWN_REVISION)
    engine = _sqlite_engine(db_path)
    try:
        with engine.begin() as connection:
            connection.execute(
                text(
                    f"""
                    INSERT INTO {RATE_TABLE}
                        (id, fee_code, fee_name, fee_type, currency,
                         default_amount, enabled, source_doc, source_url,
                         source_policy, source_version, source_status)
                    VALUES
                        ('legacy-gov', 'SYNTHETIC-LEGACY-GOV',
                         'Synthetic legacy GOV fixture', 'GOV', 'CNY', NULL,
                         1, 'customer-fixture', 'https://example.test/gov',
                         'fixture-policy', 'fixture-v1', 'UNVERIFIED'),
                        ('legacy-service', 'SYNTHETIC-LEGACY-SERVICE',
                         'Synthetic legacy SERVICE fixture', 'SERVICE', 'CNY', NULL,
                         0, 'customer-fixture', 'https://example.test/service',
                         'fixture-policy', 'fixture-v2', 'CUSTOMER')
                    """
                )
            )
            before = [
                dict(row)
                for row in connection.execute(
                    text(f"SELECT * FROM {RATE_TABLE} ORDER BY id")
                ).mappings()
                if row["id"] in {"legacy-gov", "legacy-service"}
            ]
            assert len(before) == 2
    finally:
        engine.dispose()

    command.upgrade(config, REVISION)
    engine = _sqlite_engine(db_path)
    try:
        with engine.connect() as connection:
            after_rows = [
                dict(row)
                for row in connection.execute(
                    text(f"SELECT * FROM {RATE_TABLE} ORDER BY id")
                ).mappings()
                if row["id"] in {"legacy-gov", "legacy-service"}
            ]
            after_without_link = [
                {key: value for key, value in row.items() if key != "official_rate_book_id"}
                for row in after_rows
            ]

            assert after_without_link == before
            assert all(row["official_rate_book_id"] is None for row in after_rows)
            assert connection.scalar(text(f"SELECT count(*) FROM {TABLE}")) == 0
    finally:
        engine.dispose()
        get_settings.cache_clear()


_ = auth_models
