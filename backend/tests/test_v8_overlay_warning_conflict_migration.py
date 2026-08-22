from __future__ import annotations

import json
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, inspect, text

from app.core.config import get_settings

REVISION = "v8_d31_overlay_conflict_01"
DOWN_REVISION = "v8_d27_annuity_reduction_01"
CURRENT_HEAD = "v8_w6_service_price_book_01"


def _config(path: Path, monkeypatch) -> Config:
    url = f"sqlite:///{path}"
    monkeypatch.setenv("DATABASE_URL", url)
    get_settings.cache_clear()
    backend = Path(__file__).resolve().parents[1]
    config = Config(str(backend / "alembic.ini"))
    config.set_main_option("script_location", str(backend / "alembic"))
    config.set_main_option("sqlalchemy.url", url)
    return config


def _payload(case_id: str, status: str) -> str:
    return json.dumps(
        {
            "case_id": case_id,
            "legacy_status": status,
            "reverse_mapping": "NONE",
            "schema": "FPMS_V8_LEGACY_LIFECYCLE_IMPORT_V1",
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _insert_case(connection, case_id: str, *, status: str, revision: int) -> None:
    connection.execute(
        text(
            "INSERT INTO t_case "
            "(id, case_no, status, lifecycle_revision, legal_status, "
            "lifecycle_verification_status) "
            "VALUES (:id, :case_no, :status, :revision, :legal, :verification)"
        ),
        {
            "id": case_id,
            "case_no": f"MIG-{case_id}",
            "status": status,
            "revision": revision,
            "legal": "UNKNOWN" if revision else None,
            "verification": "LEGACY_UNVERIFIED" if revision else None,
        },
    )


def _insert_activity(
    connection,
    case_id: str,
    *,
    event_type: str,
    status: str,
    confirmation: str = "LEGACY_UNVERIFIED",
    sequence: int = 1,
) -> None:
    connection.execute(
        text(
            "INSERT INTO t_case_activity_event "
            "(id, case_id, sequence, lane, activity_type, occurred_at, effective_at, "
            "confirmation_status, old_business_stage, new_business_stage, "
            "old_official_procedure_stage, new_official_procedure_stage, old_legal_status, "
            "new_legal_status, actor_id, reviewer_id, idempotency_key, source_activity_id, "
            "supersedes_event_id, payload_json) VALUES "
            "(:id, :case_id, :sequence, 'LIFECYCLE', :event_type, :at, :at, :confirmation, "
            "NULL, NULL, NULL, NULL, NULL, :new_legal, 'migration-actor', NULL, :key, "
            "NULL, NULL, :payload)"
        ),
        {
            "id": f"activity-{case_id}-{sequence}",
            "case_id": case_id,
            "sequence": sequence,
            "event_type": event_type,
            "at": "2026-07-01 09:00:00",
            "confirmation": confirmation,
            "new_legal": "UNKNOWN" if event_type == "LEGACY_IMPORT" else None,
            "key": (
                f"v8-legacy-lifecycle-import:{case_id}"
                if event_type == "LEGACY_IMPORT"
                else f"key:{case_id}"
            ),
            "payload": _payload(case_id, status) if event_type == "LEGACY_IMPORT" else "{}",
        },
    )


def _insert_followup(connection, case_id: str) -> None:
    connection.execute(
        text(
            "INSERT INTO t_case_activity_event "
            "(id, case_id, sequence, lane, activity_type, occurred_at, effective_at, "
            "confirmation_status, old_business_stage, new_business_stage, "
            "old_official_procedure_stage, new_official_procedure_stage, old_legal_status, "
            "new_legal_status, actor_id, idempotency_key, payload_json) VALUES "
            "(:id, :case_id, 2, 'LIFECYCLE', 'GRANT_ANNOUNCEMENT_CONFIRMED', :at, :at, "
            "'CONFIRMED', NULL, NULL, NULL, NULL, 'UNKNOWN', 'PATENT_IN_FORCE', "
            "'migration-actor', :key, '{}')"
        ),
        {
            "id": f"followup-{case_id}",
            "case_id": case_id,
            "at": "2026-07-02 09:00:00",
            "key": f"followup:{case_id}",
        },
    )
    connection.execute(
        text(
            "UPDATE t_case SET status = 'GRANTED', lifecycle_revision = 2, "
            "legal_status = 'PATENT_IN_FORCE', lifecycle_verification_status = 'CONFIRMED' "
            "WHERE id = :case_id"
        ),
        {"case_id": case_id},
    )


def _insert_material_near_misses(connection) -> tuple[str, ...]:
    mutations = {
        "lane": ("lane", "DOCUMENT"),
        "confirmation": ("confirmation_status", "CONFIRMED"),
        "key": ("idempotency_key", "wrong-key"),
        "source": ("source_activity_id", "SELF"),
        "supersession": ("supersedes_event_id", "SELF"),
        "reviewer": ("reviewer_id", "reviewer"),
        "old-axis": ("old_business_stage", "NEW_CASE"),
        "new-axis": ("new_business_stage", "NEW_CASE"),
        "timestamp": ("occurred_at", "2026-07-01 08:59:59"),
        "payload-canonical": (
            "payload_json",
            '{"schema": "FPMS_V8_LEGACY_LIFECYCLE_IMPORT_V1"}',
        ),
    }
    case_ids: list[str] = []
    for name, (column, value) in mutations.items():
        case_id = f"near-{name}"
        case_ids.append(case_id)
        _insert_case(connection, case_id, status="NOT_FILED", revision=1)
        _insert_activity(
            connection,
            case_id,
            event_type="LEGACY_IMPORT",
            status="NOT_FILED",
        )
        activity_id = f"activity-{case_id}-1"
        connection.execute(
            text(f"UPDATE t_case_activity_event SET {column} = :value WHERE id = :id"),
            {"value": activity_id if value == "SELF" else value, "id": activity_id},
        )

    evidence_case = "near-evidence"
    case_ids.append(evidence_case)
    _insert_case(connection, evidence_case, status="NOT_FILED", revision=1)
    _insert_activity(
        connection,
        evidence_case,
        event_type="LEGACY_IMPORT",
        status="NOT_FILED",
    )
    connection.execute(
        text(
            "INSERT INTO t_case_activity_event_evidence "
            "(id, case_id, activity_id, evidence_kind, object_type, object_id, "
            "content_hash, captured_at) VALUES "
            "('near-evidence-link', :case_id, :activity_id, 'DOCUMENT', 'Document', "
            "'object', 'sha256:evidence', '2026-07-01 09:00:00')"
        ),
        {"case_id": evidence_case, "activity_id": f"activity-{evidence_case}-1"},
    )

    not_first = "near-not-first"
    case_ids.append(not_first)
    _insert_case(connection, not_first, status="NOT_FILED", revision=2)
    _insert_activity(
        connection,
        not_first,
        event_type="CASE_OPENED",
        status="NOT_FILED",
        confirmation="CONFIRMED",
        sequence=1,
    )
    _insert_activity(
        connection,
        not_first,
        event_type="LEGACY_IMPORT",
        status="NOT_FILED",
        sequence=2,
    )
    return tuple(case_ids)


def test_upgrade_backfills_only_exact_authoritative_history(tmp_path, monkeypatch) -> None:
    config = _config(tmp_path / "lineage-migration.db", monkeypatch)
    command.upgrade(config, DOWN_REVISION)
    engine = create_engine(config.get_main_option("sqlalchemy.url"), future=True)
    try:
        with engine.begin() as connection:
            _insert_case(connection, "exact", status="NOT_FILED", revision=1)
            _insert_activity(connection, "exact", event_type="LEGACY_IMPORT", status="NOT_FILED")
            _insert_case(connection, "exact-later", status="NOT_FILED", revision=1)
            _insert_activity(
                connection, "exact-later", event_type="LEGACY_IMPORT", status="NOT_FILED"
            )
            _insert_followup(connection, "exact-later")
            _insert_case(connection, "ordinary", status="NOT_FILED", revision=1)
            _insert_activity(
                connection,
                "ordinary",
                event_type="CASE_OPENED",
                status="NOT_FILED",
                confirmation="CONFIRMED",
            )
            _insert_case(connection, "register", status="PENDING", revision=1)
            _insert_activity(
                connection,
                "register",
                event_type="PATENT_REGISTER_STATUS_CONFIRMED",
                status="PENDING",
                confirmation="CONFIRMED",
            )
            _insert_case(connection, "bad-current", status="OUT_OF_CONTRACT", revision=1)
            _insert_activity(
                connection,
                "bad-current",
                event_type="LEGACY_IMPORT",
                status="NOT_FILED",
            )
            _insert_case(connection, "bad-payload", status="NOT_FILED", revision=1)
            _insert_activity(
                connection,
                "bad-payload",
                event_type="LEGACY_IMPORT",
                status="OUT_OF_CONTRACT",
            )
            _insert_case(connection, "broken-ledger", status="NOT_FILED", revision=2)
            _insert_activity(
                connection,
                "broken-ledger",
                event_type="LEGACY_IMPORT",
                status="NOT_FILED",
            )
            near_miss_case_ids = _insert_material_near_misses(connection)

        command.upgrade(config, REVISION)
        with engine.connect() as connection:
            carriers = connection.execute(
                text(
                    "SELECT case_id, conflict_lineage_version, conflict_code_count "
                    "FROM t_case_activity_event WHERE case_id NOT LIKE 'near-%' "
                    "ORDER BY case_id, sequence"
                )
            ).all()
            assert carriers == [
                ("bad-current", None, None),
                ("bad-payload", None, None),
                ("broken-ledger", None, None),
                ("exact", "V1", 2),
                ("exact-later", "V1", 2),
                ("exact-later", "V1", 0),
                ("ordinary", "V1", 0),
                ("register", None, None),
            ]
            assert connection.execute(
                text(
                    "SELECT case_id, code FROM t_case_activity_event_conflict "
                    "ORDER BY case_id, code"
                )
            ).all() == [
                ("exact", "LEGACY_STATUS_UNVERIFIED"),
                ("exact", "NO_REVERSE_MAPPING_AUTHORITY"),
                ("exact-later", "LEGACY_STATUS_UNVERIFIED"),
                ("exact-later", "NO_REVERSE_MAPPING_AUTHORITY"),
            ]
            near_misses = connection.execute(
                text(
                    "SELECT case_id, conflict_lineage_version, conflict_code_count, "
                    "conflict_codes_sha256 FROM t_case_activity_event "
                    "WHERE case_id LIKE 'near-%' AND activity_type = 'LEGACY_IMPORT' "
                    "ORDER BY case_id"
                )
            ).all()
            assert [row[0] for row in near_misses] == sorted(near_miss_case_ids)
            assert all(row[1:] == (None, None, None) for row in near_misses)
    finally:
        engine.dispose()
        get_settings.cache_clear()


def test_clean_head_exposes_exact_carrier_schema(tmp_path, monkeypatch) -> None:
    config = _config(tmp_path / "lineage-head.db", monkeypatch)
    script = ScriptDirectory.from_config(config)
    assert tuple(script.get_heads()) == (CURRENT_HEAD,)
    assert REVISION in {
        item.revision for item in script.walk_revisions(base="base", head=CURRENT_HEAD)
    }
    assert script.get_revision(REVISION).down_revision == DOWN_REVISION
    command.upgrade(config, "head")
    engine = create_engine(config.get_main_option("sqlalchemy.url"), future=True)
    try:
        schema = inspect(engine)
        assert tuple(
            column["name"] for column in schema.get_columns("t_case_activity_event_conflict")
        ) == ("case_id", "activity_id", "code")
        assert schema.get_pk_constraint("t_case_activity_event_conflict")[
            "constrained_columns"
        ] == ["activity_id", "code"]
        assert {
            "conflict_lineage_version",
            "conflict_code_count",
            "conflict_codes_sha256",
        } <= {column["name"] for column in schema.get_columns("t_case_activity_event")}
        with pytest.raises(NotImplementedError, match="forward-only"):
            script.get_revision(REVISION).module.downgrade()
    finally:
        engine.dispose()
        get_settings.cache_clear()
