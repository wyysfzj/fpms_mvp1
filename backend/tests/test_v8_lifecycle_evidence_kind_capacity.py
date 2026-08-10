from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import (
    CheckConstraint,
    ForeignKeyConstraint,
    UniqueConstraint,
    create_engine,
    event,
    func,
    inspect,
    select,
)
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.core.errors import BusinessError
from app.modules.cases.lifecycle_activity_service import append_case_activity
from app.modules.cases.lifecycle_contracts import (
    ActivityLane,
    BusinessStage,
    ConfirmationStatus,
    EvidenceReference,
    LegalStatus,
    LifecycleEventCommand,
    LifecycleProjection,
    OfficialProcedureStage,
)
from app.modules.cases.models import Case, CaseActivityEvent, CaseActivityEventEvidence

REVISION = "v8_d4_evidence_kind_capacity_01"
DOWN_REVISION = "v8_d4_legacy_fee_provenance_01"
CURRENT_HEAD = "v8_d31_overlay_conflict_01"
TABLE = "t_case_activity_event_evidence"
CASE_ID = "case-evidence-kind-capacity"
EVIDENCE_KIND = "MANUAL_EXTERNAL_SUBMISSION_RECORD"
CAPTURED_AT = datetime(2026, 7, 18, 9, 0)

FILING_PREPARATION = LifecycleProjection(
    business_stage=BusinessStage.FILING_PREPARATION,
    official_procedure_stage=OfficialProcedureStage.NOT_SUBMITTED,
    legal_status=LegalStatus.NOT_ESTABLISHED,
    lifecycle_verification_status=ConfirmationStatus.CONFIRMED,
)
WAITING_RECEIPT = LifecycleProjection(
    business_stage=BusinessStage.WAITING_EXTERNAL_RECEIPT,
    official_procedure_stage=OfficialProcedureStage.SUBMITTED_WAITING_RECEIPT,
    legal_status=LegalStatus.APPLICATION_PENDING,
    lifecycle_verification_status=ConfirmationStatus.CONFIRMED,
)


def _case() -> Case:
    return Case(
        id=CASE_ID,
        case_no="CASE-EVIDENCE-KIND-CAPACITY",
        status="FILING_PREPARATION",
        business_stage=FILING_PREPARATION.business_stage.value,
        official_procedure_stage=FILING_PREPARATION.official_procedure_stage.value,
        legal_status=FILING_PREPARATION.legal_status.value,
        lifecycle_verification_status=FILING_PREPARATION.lifecycle_verification_status.value,
        lifecycle_revision=0,
    )


def _command(evidence_kind: str) -> LifecycleEventCommand:
    return LifecycleEventCommand(
        case_id=CASE_ID,
        event_type="FILING_EXTERNAL_SUBMISSION_RECORDED",
        lane=ActivityLane.LIFECYCLE,
        effective_at=datetime(2026, 7, 18, 9, 5),
        evidence_refs=(
            EvidenceReference(
                case_id=CASE_ID,
                evidence_kind=evidence_kind,
                object_type="CaseActivityEvent",
                object_id="submission-activity-evidence",
                content_hash=f"sha256:{'a' * 64}",
                captured_at=CAPTURED_AT,
            ),
        ),
        actor_id="actor-evidence-kind-capacity",
        idempotency_key=f"evidence-kind-capacity:{len(evidence_kind)}",
        confirmation_status=ConfirmationStatus.CONFIRMED,
        payload={},
    )


def _append(transaction: Session, evidence_kind: str) -> None:
    append_case_activity(
        _command(evidence_kind),
        transaction,
        previous_projection=FILING_PREPARATION,
        current_projection=WAITING_RECEIPT,
        legacy_case_status="WAITING_EXTERNAL_RECEIPT",
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


def test_exact_external_submission_evidence_kind_persists_unchanged(
    session_factory: sessionmaker,
) -> None:
    assert len(EVIDENCE_KIND) == 33
    with session_factory() as transaction:
        transaction.add(_case())
        transaction.commit()

        _append(transaction, EVIDENCE_KIND)

        link = transaction.scalar(select(CaseActivityEventEvidence))
        assert link is not None
        assert link.evidence_kind == EVIDENCE_KIND
        assert link.object_type == "CaseActivityEvent"


@pytest.mark.parametrize("evidence_kind", ("", "x" * 65))
def test_empty_or_65_character_evidence_kind_fails_before_persistence(
    session_factory: sessionmaker,
    evidence_kind: str,
) -> None:
    with session_factory() as transaction:
        transaction.add(_case())
        transaction.commit()

        with pytest.raises(BusinessError) as captured:
            _append(transaction, evidence_kind)

        assert captured.value.code == "LIFECYCLE_EVIDENCE_INVALID"
        assert captured.value.status_code == 400
        assert (
            transaction.scalar(select(func.count()).select_from(CaseActivityEvent)) == 0
        )
        assert (
            transaction.scalar(
                select(func.count()).select_from(CaseActivityEventEvidence)
            )
            == 0
        )


def test_model_exposes_64_character_evidence_kind() -> None:
    evidence_kind = CaseActivityEventEvidence.__table__.c.evidence_kind

    assert evidence_kind.type.length == 64
    assert evidence_kind.nullable is False


def test_clean_sqlite_head_widens_only_evidence_kind_and_preserves_constraints(
    tmp_path,
    monkeypatch,
) -> None:
    db_path = tmp_path / "v8_delta4_evidence_kind_capacity.db"
    config = _alembic_config(db_path, monkeypatch)
    engine = None
    try:
        script = ScriptDirectory.from_config(config)
        assert tuple(script.get_heads()) == (CURRENT_HEAD,)
        assert REVISION in {
            item.revision for item in script.walk_revisions(base="base", head=CURRENT_HEAD)
        }
        migration = script.get_revision(REVISION)
        assert migration is not None
        assert migration.down_revision == DOWN_REVISION
        assert migration.module.revision == REVISION
        assert migration.module.down_revision == DOWN_REVISION

        command.upgrade(config, "head")
        engine = _sqlite_engine(db_path)
        inspector = inspect(engine)
        columns = {column["name"]: column for column in inspector.get_columns(TABLE)}
        assert getattr(columns["evidence_kind"]["type"], "length", None) == 64
        assert columns["evidence_kind"]["nullable"] is False
        assert tuple(inspector.get_pk_constraint(TABLE)["constrained_columns"]) == ("id",)
        assert {
            item["name"]: tuple(item["column_names"])
            for item in inspector.get_unique_constraints(TABLE)
        } == {
            "uq_t_case_activity_event_evidence_link": (
                "case_id",
                "activity_id",
                "evidence_kind",
                "object_type",
                "object_id",
            )
        }
        assert {
            item["name"]: (
                tuple(item["constrained_columns"]),
                item["referred_table"],
                tuple(item["referred_columns"]),
                item.get("options", {}).get("ondelete"),
            )
            for item in inspector.get_foreign_keys(TABLE)
        } == {
            "fk_t_case_activity_event_evidence_activity_same_case": (
                ("case_id", "activity_id"),
                "t_case_activity_event",
                ("case_id", "id"),
                None,
            )
        }
        assert inspector.get_indexes(TABLE) == []
        assert inspector.get_check_constraints(TABLE) == []

        assert not any(
            isinstance(constraint, CheckConstraint)
            for constraint in CaseActivityEventEvidence.__table__.constraints
        )
        assert sum(
            isinstance(constraint, UniqueConstraint)
            for constraint in CaseActivityEventEvidence.__table__.constraints
        ) == 1
        assert sum(
            isinstance(constraint, ForeignKeyConstraint)
            for constraint in CaseActivityEventEvidence.__table__.constraints
        ) == 1

        with pytest.raises(NotImplementedError, match="forward-only"):
            migration.module.downgrade()
    finally:
        if engine is not None:
            engine.dispose()
        get_settings.cache_clear()
