from __future__ import annotations

import json
from datetime import datetime
from hashlib import sha256

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker
from test_v8_oa_out_package_atomic_link import (
    ACTOR_ID,
    _assert_failed_unit_is_absent,
    _payload,
    _seed_fixture,
)

from app.core.errors import BusinessError
from app.modules.cases.lifecycle_activity_service import append_case_activity
from app.modules.cases.lifecycle_contracts import (
    ActivityLane,
    BusinessStage,
    ConfirmationStatus,
    LegalStatus,
    LifecycleEventCommand,
    LifecycleProjection,
    OfficialProcedureStage,
)
from app.modules.cases.models import (
    Case,
    CaseActivityEvent,
    CaseActivityEventEvidence,
)
from app.modules.documents import service as documents_service
from app.modules.documents.evidence_contracts import EvidenceDerivationType
from app.modules.documents.models import (
    Document,
    DocumentEvidenceDerivation,
    DocumentEvidenceVersion,
)
from app.modules.official_workflows import service as official_workflows_service
from app.modules.official_workflows.models import OfficialWorkPackage
from app.modules.tasks.models import Task


def test_oa_out_preparation_appends_document_activity_without_central_change(
    session_factory: sessionmaker[Session],
    monkeypatch,
    tmp_path,
) -> None:
    fixture = _seed_fixture(session_factory, monkeypatch, tmp_path)

    with session_factory() as transaction:
        documents_service.create_document_wizard_batch(
            transaction,
            _payload(fixture),
            actor_id=ACTOR_ID,
        )

    with session_factory() as transaction:
        case = transaction.get(Case, fixture.case_id)
        package = transaction.get(OfficialWorkPackage, fixture.package_ids[0])
        task = transaction.get(Task, fixture.task_id)
        reply_version = transaction.scalar(
            select(DocumentEvidenceVersion).where(
                DocumentEvidenceVersion.case_id == fixture.case_id,
                DocumentEvidenceVersion.lineage_key == f"oa-reply:{fixture.source_document_id}",
            )
        )
        derivation = transaction.scalar(
            select(DocumentEvidenceDerivation).where(
                DocumentEvidenceDerivation.child_evidence_version_id == reply_version.id
            )
        )
        activities = transaction.scalars(
            select(CaseActivityEvent).where(
                CaseActivityEvent.case_id == fixture.case_id,
                CaseActivityEvent.activity_type == "OA_REPLY_PREPARED",
            )
        ).all()

        assert case is not None
        assert package is not None
        assert task is not None
        assert reply_version is not None
        assert derivation is not None
        assert len(activities) == 1
        activity = activities[0]
        assert (
            activity.sequence,
            activity.lane,
            activity.activity_type,
            activity.actor_id,
            activity.effective_at,
            activity.occurred_at,
            activity.idempotency_key,
        ) == (
            2,
            "DOCUMENT",
            "OA_REPLY_PREPARED",
            ACTOR_ID,
            derivation.derived_at,
            derivation.derived_at,
            f"oa-reply-prepared:{package.id}",
        )
        assert (
            activity.old_business_stage,
            activity.new_business_stage,
            activity.old_official_procedure_stage,
            activity.new_official_procedure_stage,
            activity.old_legal_status,
            activity.new_legal_status,
        ) == (None, None, None, None, None, None)
        assert json.loads(activity.payload_json)["center_changes"] == {}

        links = transaction.scalars(
            select(CaseActivityEventEvidence).where(
                CaseActivityEventEvidence.activity_id == activity.id
            )
        ).all()
        assert {
            (
                link.evidence_kind,
                link.object_type,
                link.object_id,
                link.content_hash,
                link.captured_at,
            )
            for link in links
        } == {
            (
                "OA_REPLY_WORK_PACKAGE",
                "OfficialWorkPackage",
                package.id,
                f"sha256:{sha256(derivation.source_snapshot.encode()).hexdigest()}",
                derivation.derived_at,
            ),
            (
                "OA_REPLY_DOCUMENT",
                "DocumentEvidenceVersion",
                reply_version.id,
                reply_version.content_hash,
                derivation.derived_at,
            ),
        }
        assert (
            case.business_stage,
            case.official_procedure_stage,
            case.legal_status,
            case.lifecycle_verification_status,
            case.lifecycle_revision,
            case.status,
        ) == (None, None, None, None, 2, "OA1")
        assert (task.status, task.done_at) == ("OPEN", None)


def test_replay_after_later_projection_change_reuses_stored_activity(
    session_factory: sessionmaker[Session],
    monkeypatch,
    tmp_path,
) -> None:
    fixture = _seed_fixture(session_factory, monkeypatch, tmp_path)

    with session_factory() as transaction:
        created = documents_service.create_document_wizard_batch(
            transaction,
            _payload(fixture),
            actor_id=ACTOR_ID,
        )
        reply_document_id = created[0][1].id

    empty_projection = LifecycleProjection(
        business_stage=None,
        official_procedure_stage=None,
        legal_status=None,
        lifecycle_verification_status=None,
    )
    later_projection = LifecycleProjection(
        business_stage=BusinessStage.OA_REPLY_IN_PROGRESS,
        official_procedure_stage=OfficialProcedureStage.OFFICE_ACTION_RESPONSE,
        legal_status=LegalStatus.APPLICATION_PENDING,
        lifecycle_verification_status=ConfirmationStatus.CONFIRMED,
    )
    with session_factory.begin() as transaction:
        original = transaction.scalar(
            select(CaseActivityEvent).where(
                CaseActivityEvent.case_id == fixture.case_id,
                CaseActivityEvent.activity_type == "OA_REPLY_PREPARED",
            )
        )
        assert original is not None
        original_activity_id = original.id
        append_case_activity(
            LifecycleEventCommand(
                case_id=fixture.case_id,
                event_type="LATER_LIFECYCLE_PROJECTION",
                lane=ActivityLane.LIFECYCLE,
                effective_at=datetime(2026, 7, 21, 9, 0),
                occurred_at=datetime(2026, 7, 21, 9, 0),
                evidence_refs=(),
                actor_id="later-lifecycle-actor",
                idempotency_key="later-lifecycle-projection",
                confirmation_status=ConfirmationStatus.CONFIRMED,
                payload={"source": "focused-replay-regression"},
            ),
            transaction,
            previous_projection=empty_projection,
            current_projection=later_projection,
            legacy_case_status="OA1",
            conflict_codes=(),
        )

    with session_factory.begin() as transaction:
        reply_document = transaction.get(Document, reply_document_id)
        assert reply_document is not None
        replay = official_workflows_service.prepare_oa_out_package_link(
            transaction,
            reply_document=reply_document,
            actor_id=ACTOR_ID,
        )
        assert replay.reused is True

    with session_factory() as transaction:
        case = transaction.get(Case, fixture.case_id)
        activities = transaction.scalars(
            select(CaseActivityEvent)
            .where(CaseActivityEvent.case_id == fixture.case_id)
            .order_by(CaseActivityEvent.sequence)
        ).all()
        prepared = [
            activity for activity in activities if activity.activity_type == "OA_REPLY_PREPARED"
        ]
        assert case is not None
        assert len(activities) == 3
        assert len(prepared) == 1
        assert prepared[0].id == original_activity_id
        assert (
            transaction.scalar(
                select(func.count())
                .select_from(CaseActivityEventEvidence)
                .where(CaseActivityEventEvidence.activity_id == original_activity_id)
            )
            == 2
        )
        assert (
            case.business_stage,
            case.official_procedure_stage,
            case.legal_status,
            case.lifecycle_verification_status,
            case.lifecycle_revision,
            case.status,
        ) == (
            BusinessStage.OA_REPLY_IN_PROGRESS.value,
            OfficialProcedureStage.OFFICE_ACTION_RESPONSE.value,
            LegalStatus.APPLICATION_PENDING.value,
            ConfirmationStatus.CONFIRMED.value,
            3,
            "OA1",
        )


def test_oa_prepared_activity_rejects_ambiguous_exact_derivation(
    session_factory: sessionmaker[Session],
    monkeypatch,
    tmp_path,
) -> None:
    fixture = _seed_fixture(session_factory, monkeypatch, tmp_path)
    real_prepare = official_workflows_service.prepare_oa_reply

    def prepare_with_ambiguous_lineage(command, transaction):
        result = real_prepare(command, transaction)
        preparations = transaction.scalars(
            select(DocumentEvidenceDerivation).where(
                DocumentEvidenceDerivation.case_id == result.case_id,
                DocumentEvidenceDerivation.parent_evidence_version_id
                == result.source_evidence_version_id,
                DocumentEvidenceDerivation.child_evidence_version_id
                == result.reply_evidence_version_id,
                DocumentEvidenceDerivation.derivation_type
                == EvidenceDerivationType.OA_REPLY_PREPARATION.value,
            )
        ).all()
        assert len(preparations) == 1
        preparation = preparations[0]
        derived_at = preparation.derived_at
        source_snapshot = preparation.source_snapshot
        preparation.derivation_type = EvidenceDerivationType.FORMAT_CONVERSION.value
        preparation.derived_at = datetime(2030, 1, 1)
        preparation.source_snapshot = '{"unrelated":true}'
        for ordinal in (1, 2):
            transaction.add(
                DocumentEvidenceDerivation(
                    id=f"duplicate-oa-preparation-{ordinal}",
                    case_id=preparation.case_id,
                    parent_evidence_version_id=preparation.parent_evidence_version_id,
                    child_evidence_version_id=preparation.child_evidence_version_id,
                    derivation_type=EvidenceDerivationType.OA_REPLY_PREPARATION.value,
                    actor_id=preparation.actor_id,
                    derived_at=derived_at,
                    source_snapshot=source_snapshot,
                )
            )
        transaction.flush()
        return result

    monkeypatch.setattr(
        official_workflows_service,
        "prepare_oa_reply",
        prepare_with_ambiguous_lineage,
    )

    with session_factory() as transaction:
        with pytest.raises(BusinessError) as raised:
            documents_service.create_document_wizard_batch(
                transaction,
                _payload(fixture),
                actor_id=ACTOR_ID,
            )

    assert (raised.value.code, raised.value.status_code) == (
        "OA_REPLY_IDENTITY_CONFLICT",
        409,
    )
    with session_factory() as transaction:
        assert (
            transaction.scalar(
                select(func.count())
                .select_from(CaseActivityEvent)
                .where(CaseActivityEvent.activity_type == "OA_REPLY_PREPARED")
            )
            == 0
        )
        assert (
            transaction.scalar(
                select(func.count())
                .select_from(DocumentEvidenceDerivation)
                .where(
                    DocumentEvidenceDerivation.derivation_type
                    == EvidenceDerivationType.OA_REPLY_PREPARATION.value
                )
            )
            == 0
        )


def test_oa_prepared_activity_rejects_wrong_case_exact_derivation(
    session_factory: sessionmaker[Session],
    monkeypatch,
    tmp_path,
) -> None:
    fixture = _seed_fixture(session_factory, monkeypatch, tmp_path)
    real_prepare = official_workflows_service.prepare_oa_reply

    def prepare_with_wrong_case_lineage(command, transaction):
        result = real_prepare(command, transaction)
        preparations = transaction.scalars(
            select(DocumentEvidenceDerivation).where(
                DocumentEvidenceDerivation.parent_evidence_version_id
                == result.source_evidence_version_id,
                DocumentEvidenceDerivation.child_evidence_version_id
                == result.reply_evidence_version_id,
                DocumentEvidenceDerivation.derivation_type
                == EvidenceDerivationType.OA_REPLY_PREPARATION.value,
            )
        ).all()
        assert len(preparations) == 1
        preparation = preparations[0]
        wrong_case = Case(
            id="wrong-case-oa-preparation",
            case_no="OA-WRONG-DERIVATION",
            status="OA1",
            fee_reduction="0",
        )
        transaction.add(wrong_case)
        transaction.flush()
        transaction.add(
            DocumentEvidenceDerivation(
                id="wrong-case-oa-preparation-edge",
                case_id=wrong_case.id,
                parent_evidence_version_id=preparation.parent_evidence_version_id,
                child_evidence_version_id=preparation.child_evidence_version_id,
                derivation_type=preparation.derivation_type,
                actor_id=preparation.actor_id,
                derived_at=preparation.derived_at,
                source_snapshot=preparation.source_snapshot,
            )
        )
        transaction.flush()
        return result

    monkeypatch.setattr(
        official_workflows_service,
        "prepare_oa_reply",
        prepare_with_wrong_case_lineage,
    )

    with session_factory() as transaction:
        with pytest.raises(BusinessError) as raised:
            documents_service.create_document_wizard_batch(
                transaction,
                _payload(fixture),
                actor_id=ACTOR_ID,
            )

    assert (raised.value.code, raised.value.status_code) == (
        "OA_REPLY_IDENTITY_CONFLICT",
        409,
    )
    _assert_failed_unit_is_absent(session_factory, fixture)
    with session_factory() as transaction:
        assert (
            transaction.scalar(
                select(func.count())
                .select_from(CaseActivityEvent)
                .where(CaseActivityEvent.activity_type == "OA_REPLY_PREPARED")
            )
            == 0
        )
