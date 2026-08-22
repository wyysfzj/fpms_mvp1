from __future__ import annotations

import json
from dataclasses import replace
from datetime import datetime, timezone
from unittest.mock import Mock
from uuid import UUID

import pytest
from sqlalchemy import inspect, select
from sqlalchemy.orm import Session, sessionmaker

from app.core.errors import BusinessError
from app.modules.cases import lifecycle_projection
from app.modules.cases.lifecycle_contracts import (
    ActivityLane,
    BusinessStage,
    ConfirmationStatus,
    LegalStatus,
    LifecycleEventCommand,
    LifecycleProjection,
    LifecycleTransitionResult,
    OfficialProcedureStage,
)
from app.modules.cases.models import Case, CaseActivityEvent, CaseActivityEventEvidence
from app.modules.documents import evidence_service
from app.modules.documents.evidence_contracts import (
    EvidenceDerivationResult,
    EvidenceDerivationType,
    EvidenceReviewState,
    EvidenceRole,
    EvidenceVersionState,
    RegisterEvidenceDerivationCommand,
)
from app.modules.documents.evidence_service import register_evidence_derivation
from app.modules.documents.models import (
    DocAttachment,
    Document,
    DocumentEvidenceDerivation,
    DocumentEvidenceVersion,
)


def _id(value: int) -> str:
    return f"00000000-0000-0000-0000-{value:012d}"


def _add_case(transaction: Session, *, case_id: str) -> None:
    transaction.add(Case(id=case_id, case_no=f"CASE-{case_id[-12:]}"))


def _add_version(
    transaction: Session,
    *,
    case_id: str,
    evidence_version_id: str,
    document_id: str,
    attachment_id: str,
    content_hash: str = f"sha256:{'a' * 64}",
) -> None:
    transaction.add_all(
        [
            Document(id=document_id, case_id=case_id),
            DocAttachment(
                id=attachment_id,
                document_id=document_id,
                file_name=f"{attachment_id}.docx",
                file_path=f"/evidence/{attachment_id}.docx",
            ),
        ]
    )
    transaction.flush()
    transaction.add(
        DocumentEvidenceVersion(
            id=evidence_version_id,
            case_id=case_id,
            document_id=document_id,
            attachment_id=attachment_id,
            lineage_key=f"lineage-{evidence_version_id[-12:]}",
            role=EvidenceRole.FILING_FULL_WORD.value,
            version_number=1,
            state=EvidenceVersionState.FINAL.value,
            creator_id=_id(900),
            review_state=EvidenceReviewState.PENDING.value,
            reviewer_id=None,
            reviewed_at=None,
            final_submitted_at=None,
            content_hash=content_hash,
            current_identity_key=None,
        )
    )
    transaction.flush()


def _command(
    *,
    case_id: str,
    parent_evidence_version_id: str,
    child_evidence_version_id: str,
) -> RegisterEvidenceDerivationCommand:
    return RegisterEvidenceDerivationCommand(
        case_id=case_id,
        parent_evidence_version_id=parent_evidence_version_id,
        child_evidence_version_id=child_evidence_version_id,
        derivation_type=EvidenceDerivationType.FORMAT_CONVERSION,
        actor_id=_id(901),
        derived_at=datetime(2026, 7, 13, 8, 30),
        source_snapshot='{"action":"convert","filename":"申请.xml"}',
    )


def _assert_no_derivations(transaction: Session) -> None:
    assert transaction.scalars(select(DocumentEvidenceDerivation)).all() == []


def test_registers_same_case_derivation_with_frozen_projection_without_commit(
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    case_id = _id(1)
    parent_id = _id(2)
    child_id = _id(3)

    with session_factory() as transaction:
        _add_case(transaction, case_id=case_id)
        _add_version(
            transaction,
            case_id=case_id,
            evidence_version_id=parent_id,
            document_id=_id(4),
            attachment_id=_id(5),
        )
        _add_version(
            transaction,
            case_id=case_id,
            evidence_version_id=child_id,
            document_id=_id(6),
            attachment_id=_id(7),
            content_hash=f"sha256:{'b' * 64}",
        )
        transaction.flush()
        case = transaction.get(Case, case_id)
        assert case is not None
        case.status = "ACCEPTED"
        case.business_stage = BusinessStage.PROSECUTION_MANAGEMENT.value
        case.official_procedure_stage = OfficialProcedureStage.ACCEPTED.value
        case.legal_status = LegalStatus.APPLICATION_PENDING.value
        case.lifecycle_verification_status = ConfirmationStatus.CONFIRMED.value
        case.lifecycle_revision = 0
        transaction.commit()

        command = _command(
            case_id=case_id,
            parent_evidence_version_id=parent_id,
            child_evidence_version_id=child_id,
        )
        captured_append: dict[str, object] = {}
        real_append = evidence_service.append_case_activity

        def capture_append(
            activity_command: LifecycleEventCommand,
            append_transaction: Session,
            *,
            previous_projection: LifecycleProjection,
            current_projection: LifecycleProjection,
            legacy_case_status: str,
            conflict_codes: tuple[str, ...],
        ) -> LifecycleTransitionResult:
            captured_append.update(
                command=activity_command,
                transaction=append_transaction,
                previous_projection=previous_projection,
                current_projection=current_projection,
                legacy_case_status=legacy_case_status,
                conflict_codes=conflict_codes,
            )
            return real_append(
                activity_command,
                append_transaction,
                previous_projection=previous_projection,
                current_projection=current_projection,
                legacy_case_status=legacy_case_status,
                conflict_codes=conflict_codes,
            )

        def forbidden_commit() -> None:
            pytest.fail("register_evidence_derivation must not commit")

        def forbidden_legacy_projection(*_args: object, **_kwargs: object) -> None:
            pytest.fail("register_evidence_derivation must not call the legacy adapter")

        monkeypatch.setattr(evidence_service, "append_case_activity", capture_append)
        monkeypatch.setattr(transaction, "commit", forbidden_commit)
        monkeypatch.setattr(
            evidence_service,
            "project_legacy_case_status",
            forbidden_legacy_projection,
            raising=False,
        )
        monkeypatch.setattr(
            lifecycle_projection,
            "project_legacy_case_status",
            forbidden_legacy_projection,
        )

        result = register_evidence_derivation(command, transaction)

        assert isinstance(result, EvidenceDerivationResult)
        UUID(result.evidence_derivation_id)
        assert result == EvidenceDerivationResult(
            evidence_derivation_id=result.evidence_derivation_id,
            case_id=case_id,
            parent_evidence_version_id=parent_id,
            child_evidence_version_id=child_id,
            derivation_type=EvidenceDerivationType.FORMAT_CONVERSION,
            actor_id=_id(901),
            derived_at=datetime(2026, 7, 13, 8, 30),
            source_snapshot='{"action":"convert","filename":"申请.xml"}',
        )
        stored = transaction.get(
            DocumentEvidenceDerivation,
            result.evidence_derivation_id,
        )
        assert stored is not None
        assert inspect(stored).persistent is True
        assert transaction.scalars(select(DocumentEvidenceDerivation)).all() == [stored]

        activities = transaction.scalars(select(CaseActivityEvent)).all()
        evidence_links = transaction.scalars(
            select(CaseActivityEventEvidence).order_by(CaseActivityEventEvidence.object_id)
        ).all()
        assert len(activities) == 1
        assert len(evidence_links) == 2

        activity_command = captured_append["command"]
        assert isinstance(activity_command, LifecycleEventCommand)
        assert captured_append["transaction"] is transaction
        expected_projection = LifecycleProjection(
            business_stage=BusinessStage.PROSECUTION_MANAGEMENT,
            official_procedure_stage=OfficialProcedureStage.ACCEPTED,
            legal_status=LegalStatus.APPLICATION_PENDING,
            lifecycle_verification_status=ConfirmationStatus.CONFIRMED,
        )
        assert captured_append["previous_projection"] == expected_projection
        assert captured_append["current_projection"] == expected_projection
        assert captured_append["legacy_case_status"] == "ACCEPTED"
        assert captured_append["conflict_codes"] == ()
        assert tuple(reference.object_id for reference in activity_command.evidence_refs) == (
            parent_id,
            child_id,
        )

        activity = activities[0]
        assert activity.case_id == case_id
        assert activity.sequence == 1
        assert activity.lane == ActivityLane.DOCUMENT.value
        assert activity.activity_type == "DOCUMENT_EVIDENCE_DERIVATION_REGISTERED"
        assert activity.source_activity_id is None
        assert activity.occurred_at == command.derived_at
        assert activity.effective_at == command.derived_at
        assert activity.confirmation_status == ConfirmationStatus.CONFIRMED.value
        assert activity.old_business_stage == BusinessStage.PROSECUTION_MANAGEMENT.value
        assert activity.new_business_stage == BusinessStage.PROSECUTION_MANAGEMENT.value
        assert activity.old_official_procedure_stage == OfficialProcedureStage.ACCEPTED.value
        assert activity.new_official_procedure_stage == OfficialProcedureStage.ACCEPTED.value
        assert activity.old_legal_status == LegalStatus.APPLICATION_PENDING.value
        assert activity.new_legal_status == LegalStatus.APPLICATION_PENDING.value
        assert activity.actor_id == command.actor_id
        assert activity.reviewer_id is None
        assert activity.idempotency_key == (f"document-derivation:{result.evidence_derivation_id}")
        assert activity.supersedes_event_id is None
        assert activity.payload_json == json.dumps(
            {
                "evidence_derivation_id": result.evidence_derivation_id,
                "parent_evidence_version_id": parent_id,
                "child_evidence_version_id": child_id,
                "derivation_type": EvidenceDerivationType.FORMAT_CONVERSION.value,
                "source_snapshot": command.source_snapshot,
            },
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )

        for evidence_link, expected_version, expected_hash in zip(
            evidence_links,
            (parent_id, child_id),
            (f"sha256:{'a' * 64}", f"sha256:{'b' * 64}"),
            strict=True,
        ):
            assert evidence_link.case_id == case_id
            assert evidence_link.activity_id == activity.id
            assert evidence_link.evidence_kind == "DOCUMENT_EVIDENCE_VERSION"
            assert evidence_link.object_type == "DocumentEvidenceVersion"
            assert evidence_link.object_id == expected_version
            assert evidence_link.content_hash == expected_hash
            assert evidence_link.captured_at == command.derived_at

        transaction.expire_all()
        updated_case = transaction.get(Case, case_id)
        assert updated_case is not None
        assert updated_case.status == "ACCEPTED"
        assert updated_case.business_stage == BusinessStage.PROSECUTION_MANAGEMENT.value
        assert updated_case.official_procedure_stage == OfficialProcedureStage.ACCEPTED.value
        assert updated_case.legal_status == LegalStatus.APPLICATION_PENDING.value
        assert updated_case.lifecycle_verification_status == ConfirmationStatus.CONFIRMED.value
        assert updated_case.lifecycle_revision == 1
        transaction.rollback()

    with session_factory() as verification:
        assert (
            verification.get(
                DocumentEvidenceDerivation,
                result.evidence_derivation_id,
            )
            is None
        )
        assert verification.scalars(select(CaseActivityEvent)).all() == []
        assert verification.scalars(select(CaseActivityEventEvidence)).all() == []
        original_case = verification.get(Case, case_id)
        assert original_case is not None
        assert original_case.status == "ACCEPTED"
        assert original_case.business_stage == BusinessStage.PROSECUTION_MANAGEMENT.value
        assert original_case.official_procedure_stage == OfficialProcedureStage.ACCEPTED.value
        assert original_case.legal_status == LegalStatus.APPLICATION_PENDING.value
        assert original_case.lifecycle_verification_status == ConfirmationStatus.CONFIRMED.value
        assert original_case.lifecycle_revision == 0


@pytest.mark.parametrize(
    ("missing_parent", "missing_child"),
    [(True, False), (False, True)],
)
def test_rejects_missing_parent_or_child_without_writing(
    session_factory: sessionmaker[Session],
    *,
    missing_parent: bool,
    missing_child: bool,
) -> None:
    case_id = _id(10)
    parent_id = _id(11)
    child_id = _id(12)

    with session_factory() as transaction:
        _add_case(transaction, case_id=case_id)
        if not missing_parent:
            _add_version(
                transaction,
                case_id=case_id,
                evidence_version_id=parent_id,
                document_id=_id(13),
                attachment_id=_id(14),
            )
        if not missing_child:
            _add_version(
                transaction,
                case_id=case_id,
                evidence_version_id=child_id,
                document_id=_id(15),
                attachment_id=_id(16),
            )
        transaction.flush()

        with pytest.raises(BusinessError) as exc_info:
            register_evidence_derivation(
                _command(
                    case_id=case_id,
                    parent_evidence_version_id=parent_id,
                    child_evidence_version_id=child_id,
                ),
                transaction,
            )

        assert exc_info.value.status_code == 404
        _assert_no_derivations(transaction)


@pytest.mark.parametrize("command_matches_parent", [True, False])
def test_rejects_cross_case_or_command_case_mismatch_without_writing(
    session_factory: sessionmaker[Session],
    *,
    command_matches_parent: bool,
) -> None:
    parent_case_id = _id(20)
    child_case_id = _id(21) if command_matches_parent else parent_case_id
    command_case_id = parent_case_id if command_matches_parent else _id(22)
    parent_id = _id(23)
    child_id = _id(24)

    with session_factory() as transaction:
        for case_id in {parent_case_id, child_case_id, command_case_id}:
            _add_case(transaction, case_id=case_id)
        _add_version(
            transaction,
            case_id=parent_case_id,
            evidence_version_id=parent_id,
            document_id=_id(25),
            attachment_id=_id(26),
        )
        _add_version(
            transaction,
            case_id=child_case_id,
            evidence_version_id=child_id,
            document_id=_id(27),
            attachment_id=_id(28),
        )
        transaction.flush()

        with pytest.raises(BusinessError) as exc_info:
            register_evidence_derivation(
                _command(
                    case_id=command_case_id,
                    parent_evidence_version_id=parent_id,
                    child_evidence_version_id=child_id,
                ),
                transaction,
            )

        assert exc_info.value.status_code == 400
        _assert_no_derivations(transaction)


def test_rejects_self_derivation_without_writing(
    session_factory: sessionmaker[Session],
) -> None:
    case_id = _id(30)
    version_id = _id(31)

    with session_factory() as transaction:
        _add_case(transaction, case_id=case_id)
        _add_version(
            transaction,
            case_id=case_id,
            evidence_version_id=version_id,
            document_id=_id(32),
            attachment_id=_id(33),
        )
        transaction.flush()

        with pytest.raises(BusinessError) as exc_info:
            register_evidence_derivation(
                _command(
                    case_id=case_id,
                    parent_evidence_version_id=version_id,
                    child_evidence_version_id=version_id,
                ),
                transaction,
            )

        assert exc_info.value.status_code == 400
        _assert_no_derivations(transaction)


@pytest.mark.parametrize(
    "source_snapshot",
    [
        "[]",
        '{"b":1,"a":2}',
        '{"filename":"\\u7533\\u8bf7.xml"}',
        '{"value":NaN}',
    ],
)
def test_rejects_noncanonical_json_object_snapshot_without_writing(
    session_factory: sessionmaker[Session],
    *,
    source_snapshot: str,
) -> None:
    case_id = _id(40)
    parent_id = _id(41)
    child_id = _id(42)

    with session_factory() as transaction:
        command = _command(
            case_id=case_id,
            parent_evidence_version_id=parent_id,
            child_evidence_version_id=child_id,
        )

        with pytest.raises(BusinessError) as exc_info:
            register_evidence_derivation(
                replace(command, source_snapshot=source_snapshot),
                transaction,
            )

        assert exc_info.value.status_code == 400
        _assert_no_derivations(transaction)


def test_rejects_timezone_aware_derived_at_without_writing(
    session_factory: sessionmaker[Session],
) -> None:
    command = _command(
        case_id=_id(50),
        parent_evidence_version_id=_id(51),
        child_evidence_version_id=_id(52),
    )

    with session_factory() as transaction:
        with pytest.raises(BusinessError) as exc_info:
            register_evidence_derivation(
                replace(
                    command,
                    derived_at=datetime(2026, 7, 13, 8, 30, tzinfo=timezone.utc),
                ),
                transaction,
            )

        assert exc_info.value.status_code == 400
        _assert_no_derivations(transaction)


@pytest.mark.parametrize(
    ("field", "invalid_value"),
    [
        ("case_id", ""),
        ("parent_evidence_version_id", "x" * 37),
        ("child_evidence_version_id", ""),
        ("actor_id", "x" * 37),
        ("derivation_type", "FORMAT_CONVERSION"),
    ],
)
def test_rejects_invalid_text_and_enum_fields_without_writing(
    session_factory: sessionmaker[Session],
    *,
    field: str,
    invalid_value: object,
) -> None:
    command = _command(
        case_id=_id(60),
        parent_evidence_version_id=_id(61),
        child_evidence_version_id=_id(62),
    )

    with session_factory() as transaction:
        with pytest.raises(BusinessError) as exc_info:
            register_evidence_derivation(
                replace(command, **{field: invalid_value}),
                transaction,
            )

        assert exc_info.value.status_code == 400
        _assert_no_derivations(transaction)


def test_rejects_non_exact_derivation_enum_before_lookup_or_write(
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    command = replace(
        _command(
            case_id=_id(63),
            parent_evidence_version_id=_id(64),
            child_evidence_version_id=_id(65),
        ),
        derivation_type=Mock(spec=EvidenceDerivationType),
    )

    with session_factory() as transaction:

        def forbidden_lookup(*_args: object, **_kwargs: object) -> None:
            pytest.fail("a non-exact enum must reject before transaction lookup")

        monkeypatch.setattr(transaction, "get", forbidden_lookup)

        with pytest.raises(BusinessError) as exc_info:
            register_evidence_derivation(command, transaction)

        assert exc_info.value.code == "EVIDENCE_DERIVATION_INVALID"
        assert exc_info.value.status_code == 400
        assert exc_info.value.details == {"field": "derivation_type"}
        assert list(transaction.new) == []
        assert transaction.scalars(select(DocumentEvidenceDerivation)).all() == []
        assert transaction.scalars(select(CaseActivityEvent)).all() == []
        assert transaction.scalars(select(CaseActivityEventEvidence)).all() == []


def test_append_error_propagates_and_caller_rollback_removes_all_rows(
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    case_id = _id(70)
    parent_id = _id(71)
    child_id = _id(72)
    append_error = BusinessError(
        code="LIFECYCLE_REVISION_CONFLICT",
        message="append failed",
        status_code=409,
    )

    with session_factory() as transaction:
        _add_case(transaction, case_id=case_id)
        _add_version(
            transaction,
            case_id=case_id,
            evidence_version_id=parent_id,
            document_id=_id(73),
            attachment_id=_id(74),
        )
        _add_version(
            transaction,
            case_id=case_id,
            evidence_version_id=child_id,
            document_id=_id(75),
            attachment_id=_id(76),
            content_hash=f"sha256:{'b' * 64}",
        )
        case = transaction.get(Case, case_id)
        assert case is not None
        case.status = "ACCEPTED"
        case.lifecycle_revision = 0
        transaction.commit()

        def fail_append(*_args: object, **_kwargs: object) -> None:
            raise append_error

        monkeypatch.setattr(evidence_service, "append_case_activity", fail_append)

        with pytest.raises(BusinessError) as exc_info:
            register_evidence_derivation(
                _command(
                    case_id=case_id,
                    parent_evidence_version_id=parent_id,
                    child_evidence_version_id=child_id,
                ),
                transaction,
            )

        assert exc_info.value is append_error
        transaction.rollback()

    with session_factory() as verification:
        assert verification.scalars(select(DocumentEvidenceDerivation)).all() == []
        assert verification.scalars(select(CaseActivityEvent)).all() == []
        assert verification.scalars(select(CaseActivityEventEvidence)).all() == []
        original_case = verification.get(Case, case_id)
        assert original_case is not None
        assert original_case.status == "ACCEPTED"
        assert original_case.lifecycle_revision == 0


def test_missing_case_fails_closed_before_derivation_insertion(
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    case_id = _id(80)
    parent_id = _id(81)
    child_id = _id(82)

    with session_factory() as transaction:
        _add_case(transaction, case_id=case_id)
        _add_version(
            transaction,
            case_id=case_id,
            evidence_version_id=parent_id,
            document_id=_id(83),
            attachment_id=_id(84),
        )
        _add_version(
            transaction,
            case_id=case_id,
            evidence_version_id=child_id,
            document_id=_id(85),
            attachment_id=_id(86),
        )
        real_get = transaction.get

        def get_without_case(entity: type[object], identifier: object) -> object | None:
            if entity is Case:
                return None
            return real_get(entity, identifier)

        monkeypatch.setattr(transaction, "get", get_without_case)

        with pytest.raises(BusinessError) as exc_info:
            register_evidence_derivation(
                _command(
                    case_id=case_id,
                    parent_evidence_version_id=parent_id,
                    child_evidence_version_id=child_id,
                ),
                transaction,
            )

        assert exc_info.value.code == "CASE_NOT_FOUND"
        assert exc_info.value.status_code == 404
        assert transaction.scalars(select(DocumentEvidenceDerivation)).all() == []
        assert transaction.scalars(select(CaseActivityEvent)).all() == []
        assert transaction.scalars(select(CaseActivityEventEvidence)).all() == []
        transaction.rollback()


def test_unknown_stored_projection_fails_closed_before_derivation_insertion(
    session_factory: sessionmaker[Session],
) -> None:
    case_id = _id(90)
    parent_id = _id(91)
    child_id = _id(92)

    with session_factory() as transaction:
        _add_case(transaction, case_id=case_id)
        _add_version(
            transaction,
            case_id=case_id,
            evidence_version_id=parent_id,
            document_id=_id(93),
            attachment_id=_id(94),
        )
        _add_version(
            transaction,
            case_id=case_id,
            evidence_version_id=child_id,
            document_id=_id(95),
            attachment_id=_id(96),
        )
        case = transaction.get(Case, case_id)
        assert case is not None
        case.business_stage = "UNKNOWN_STAGE"
        case.lifecycle_revision = 0
        transaction.commit()

        with pytest.raises(BusinessError) as exc_info:
            register_evidence_derivation(
                _command(
                    case_id=case_id,
                    parent_evidence_version_id=parent_id,
                    child_evidence_version_id=child_id,
                ),
                transaction,
            )

        assert exc_info.value.code == "LIFECYCLE_PROJECTION_CONFLICT"
        assert exc_info.value.status_code == 409
        assert transaction.scalars(select(DocumentEvidenceDerivation)).all() == []
        assert transaction.scalars(select(CaseActivityEvent)).all() == []
        assert transaction.scalars(select(CaseActivityEventEvidence)).all() == []
        transaction.rollback()
