from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
from types import SimpleNamespace
from unittest.mock import Mock
from uuid import UUID

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.core.errors import BusinessError
from app.modules.cases import lifecycle_projection
from app.modules.cases.lifecycle_contracts import (
    ActivityLane,
    BusinessStage,
    ConfirmationStatus,
    OfficialProcedureStage,
)
from app.modules.cases.models import Case, CaseActivityEvent, CaseActivityEventEvidence
from app.modules.documents import evidence_service
from app.modules.documents.evidence_contracts import (
    EvidenceReviewState,
    EvidenceRole,
    EvidenceVersionResult,
    EvidenceVersionState,
    RegisterEvidenceVersionCommand,
)
from app.modules.documents.evidence_service import register_evidence_version
from app.modules.documents.models import (
    DocAttachment,
    Document,
    DocumentEvidenceVersion,
)


def _id(value: int) -> str:
    return f"00000000-0000-0000-0000-{value:012d}"


def _seed_source(
    transaction: Session,
    *,
    case_id: str,
    document_id: str,
    attachment_id: str,
) -> None:
    transaction.add_all(
        [
            Case(id=case_id, case_no=f"CASE-{case_id[-12:]}"),
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


def _command(
    *,
    case_id: str,
    document_id: str,
    attachment_id: str,
    lineage_key: str = "filing-main",
    state: EvidenceVersionState = EvidenceVersionState.DRAFT,
) -> RegisterEvidenceVersionCommand:
    return RegisterEvidenceVersionCommand(
        case_id=case_id,
        document_id=document_id,
        attachment_id=attachment_id,
        lineage_key=lineage_key,
        role=EvidenceRole.FILING_FULL_WORD,
        state=state,
        creator_id=_id(900),
        content_hash=f"sha256:{'a' * 64}",
    )


def test_rejects_wrong_command_object_and_subclass_before_attribute_access(
    session_factory: sessionmaker[Session],
) -> None:
    case_id = _id(60)
    document_id = _id(61)
    attachment_id = _id(62)
    valid_command = _command(
        case_id=case_id,
        document_id=document_id,
        attachment_id=attachment_id,
    )

    class RegisterEvidenceVersionCommandSubclass(RegisterEvidenceVersionCommand):
        pass

    command_values = {
        field: getattr(valid_command, field)
        for field in (
            "case_id",
            "document_id",
            "attachment_id",
            "lineage_key",
            "role",
            "state",
            "creator_id",
            "content_hash",
        )
    }
    invalid_commands = (
        object(),
        SimpleNamespace(**command_values),
        RegisterEvidenceVersionCommandSubclass(**command_values),
    )

    with session_factory() as transaction:
        _seed_source(
            transaction,
            case_id=case_id,
            document_id=document_id,
            attachment_id=attachment_id,
        )

        for invalid_command in invalid_commands:
            with pytest.raises(BusinessError) as exc_info:
                register_evidence_version(
                    invalid_command,  # type: ignore[arg-type]
                    transaction,
                )

            assert exc_info.value.code == "EVIDENCE_VERSION_INVALID"
            assert exc_info.value.status_code == 400
            assert exc_info.value.details == {"field": "command"}

        assert transaction.scalars(select(DocumentEvidenceVersion)).all() == []
        assert transaction.scalars(select(CaseActivityEvent)).all() == []
        assert transaction.scalars(select(CaseActivityEventEvidence)).all() == []


@pytest.mark.parametrize(
    ("field", "enum_type"),
    (
        ("role", EvidenceRole),
        ("state", EvidenceVersionState),
    ),
)
def test_rejects_non_exact_enum_before_lookup_or_write(
    field: str,
    enum_type: type[EvidenceRole] | type[EvidenceVersionState],
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    invalid_command = replace(
        _command(
            case_id=_id(63),
            document_id=_id(64),
            attachment_id=_id(65),
        ),
        **{field: Mock(spec=enum_type)},
    )

    with session_factory() as transaction:

        def forbidden_lookup(*_args: object, **_kwargs: object) -> None:
            pytest.fail("invalid enum values must reject before transaction lookup")

        monkeypatch.setattr(transaction, "get", forbidden_lookup)

        with pytest.raises(BusinessError) as exc_info:
            register_evidence_version(invalid_command, transaction)

        assert exc_info.value.code == "EVIDENCE_VERSION_INVALID"
        assert exc_info.value.status_code == 400
        assert exc_info.value.details == {"field": field}
        assert list(transaction.new) == []


def test_registers_one_immutable_version_with_frozen_projection_without_commit(
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    case_id = _id(1)
    document_id = _id(2)
    attachment_id = _id(3)

    with session_factory() as transaction:
        _seed_source(
            transaction,
            case_id=case_id,
            document_id=document_id,
            attachment_id=attachment_id,
        )
        command = _command(
            case_id=case_id,
            document_id=document_id,
            attachment_id=attachment_id,
            state=EvidenceVersionState.FINAL,
        )
        case = transaction.get(Case, case_id)
        assert case is not None
        case.status = "ACCEPTED"
        case.business_stage = BusinessStage.PROSECUTION_MANAGEMENT.value
        case.official_procedure_stage = OfficialProcedureStage.ACCEPTED.value
        case.legal_status = None
        case.lifecycle_verification_status = ConfirmationStatus.CONFIRMED.value
        case.lifecycle_revision = 0
        transaction.commit()

        def forbidden_commit() -> None:
            pytest.fail("register_evidence_version must not commit")

        def forbidden_legacy_projection(*_args: object, **_kwargs: object) -> None:
            pytest.fail("register_evidence_version must not call the legacy adapter")

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

        result = register_evidence_version(command, transaction)

        assert isinstance(result, EvidenceVersionResult)
        UUID(result.evidence_version_id)
        assert result == EvidenceVersionResult(
            evidence_version_id=result.evidence_version_id,
            case_id=case_id,
            document_id=document_id,
            attachment_id=attachment_id,
            lineage_key="filing-main",
            role=EvidenceRole.FILING_FULL_WORD,
            version_number=1,
            state=EvidenceVersionState.FINAL,
            creator_id=_id(900),
            review_state=EvidenceReviewState.PENDING,
            reviewer_id=None,
            reviewed_at=None,
            final_submitted_at=None,
            content_hash=f"sha256:{'a' * 64}",
            is_current=True,
            is_final=True,
        )
        with pytest.raises(FrozenInstanceError):
            result.version_number = 2  # type: ignore[misc]

        stored = transaction.get(DocumentEvidenceVersion, result.evidence_version_id)
        assert stored is not None
        assert stored.current_identity_key == f"{case_id}|filing-main"
        assert stored.review_state == EvidenceReviewState.PENDING.value
        assert stored.reviewer_id is None
        assert stored.reviewed_at is None
        assert stored.final_submitted_at is None

        versions = transaction.scalars(select(DocumentEvidenceVersion)).all()
        activities = transaction.scalars(select(CaseActivityEvent)).all()
        evidence_links = transaction.scalars(select(CaseActivityEventEvidence)).all()
        assert versions == [stored]
        assert len(activities) == 1
        assert len(evidence_links) == 1

        activity = activities[0]
        assert activity.case_id == case_id
        assert activity.sequence == 1
        assert activity.lane == ActivityLane.DOCUMENT.value
        assert activity.activity_type == "DOCUMENT_EVIDENCE_VERSION_REGISTERED"
        assert activity.source_activity_id is None
        assert activity.occurred_at == stored.created_at
        assert activity.effective_at == stored.created_at
        assert activity.confirmation_status == ConfirmationStatus.CONFIRMED.value
        assert activity.old_business_stage == BusinessStage.PROSECUTION_MANAGEMENT.value
        assert activity.new_business_stage == BusinessStage.PROSECUTION_MANAGEMENT.value
        assert activity.old_official_procedure_stage == OfficialProcedureStage.ACCEPTED.value
        assert activity.new_official_procedure_stage == OfficialProcedureStage.ACCEPTED.value
        assert activity.old_legal_status is None
        assert activity.new_legal_status is None
        assert activity.actor_id == command.creator_id
        assert activity.reviewer_id is None
        assert activity.idempotency_key == (
            f"document-evidence-version:{result.evidence_version_id}"
        )
        assert activity.supersedes_event_id is None
        assert activity.payload_json == (
            '{"attachment_id":"'
            f"{attachment_id}"
            '","document_id":"'
            f"{document_id}"
            '","evidence_version_id":"'
            f"{result.evidence_version_id}"
            '","lineage_key":"filing-main","review_state":"PENDING",'
            '"role":"FILING_FULL_WORD","state":"FINAL","version_number":1}'
        )

        evidence_link = evidence_links[0]
        assert evidence_link.case_id == case_id
        assert evidence_link.activity_id == activity.id
        assert evidence_link.evidence_kind == "DOCUMENT_EVIDENCE_VERSION"
        assert evidence_link.object_type == "DocumentEvidenceVersion"
        assert evidence_link.object_id == result.evidence_version_id
        assert evidence_link.content_hash == stored.content_hash
        assert evidence_link.captured_at == stored.created_at

        transaction.expire_all()
        updated_case = transaction.get(Case, case_id)
        assert updated_case is not None
        assert updated_case.status == "ACCEPTED"
        assert updated_case.business_stage == BusinessStage.PROSECUTION_MANAGEMENT.value
        assert updated_case.official_procedure_stage == OfficialProcedureStage.ACCEPTED.value
        assert updated_case.legal_status is None
        assert updated_case.lifecycle_verification_status == ConfirmationStatus.CONFIRMED.value
        assert updated_case.lifecycle_revision == 1
        transaction.rollback()

    with session_factory() as verification:
        assert verification.get(DocumentEvidenceVersion, result.evidence_version_id) is None
        assert verification.scalars(select(CaseActivityEvent)).all() == []
        assert verification.scalars(select(CaseActivityEventEvidence)).all() == []
        original_case = verification.get(Case, case_id)
        assert original_case is not None
        assert original_case.status == "ACCEPTED"
        assert original_case.business_stage == BusinessStage.PROSECUTION_MANAGEMENT.value
        assert original_case.official_procedure_stage == OfficialProcedureStage.ACCEPTED.value
        assert original_case.legal_status is None
        assert original_case.lifecycle_verification_status == ConfirmationStatus.CONFIRMED.value
        assert original_case.lifecycle_revision == 0


def test_rejects_document_from_another_case(
    session_factory: sessionmaker[Session],
) -> None:
    requested_case_id = _id(10)
    document_case_id = _id(11)
    document_id = _id(12)
    attachment_id = _id(13)

    with session_factory() as transaction:
        transaction.add(Case(id=requested_case_id, case_no="CASE-REQUESTED"))
        _seed_source(
            transaction,
            case_id=document_case_id,
            document_id=document_id,
            attachment_id=attachment_id,
        )

        with pytest.raises(BusinessError) as exc_info:
            register_evidence_version(
                _command(
                    case_id=requested_case_id,
                    document_id=document_id,
                    attachment_id=attachment_id,
                ),
                transaction,
            )

        assert exc_info.value.status_code == 400
        assert transaction.scalars(select(DocumentEvidenceVersion)).all() == []
        assert transaction.scalars(select(CaseActivityEvent)).all() == []
        assert transaction.scalars(select(CaseActivityEventEvidence)).all() == []


def test_rejects_attachment_from_a_document_in_another_case(
    session_factory: sessionmaker[Session],
) -> None:
    requested_case_id = _id(20)
    requested_document_id = _id(21)
    requested_attachment_id = _id(22)
    other_case_id = _id(23)
    other_document_id = _id(24)
    other_attachment_id = _id(25)

    with session_factory() as transaction:
        _seed_source(
            transaction,
            case_id=requested_case_id,
            document_id=requested_document_id,
            attachment_id=requested_attachment_id,
        )
        _seed_source(
            transaction,
            case_id=other_case_id,
            document_id=other_document_id,
            attachment_id=other_attachment_id,
        )

        with pytest.raises(BusinessError) as exc_info:
            register_evidence_version(
                _command(
                    case_id=requested_case_id,
                    document_id=requested_document_id,
                    attachment_id=other_attachment_id,
                ),
                transaction,
            )

        assert exc_info.value.status_code == 400
        assert transaction.scalars(select(DocumentEvidenceVersion)).all() == []
        assert transaction.scalars(select(CaseActivityEvent)).all() == []
        assert transaction.scalars(select(CaseActivityEventEvidence)).all() == []


def test_allocates_next_positive_version_within_case_and_lineage_only(
    session_factory: sessionmaker[Session],
) -> None:
    case_id = _id(30)
    document_id = _id(31)
    attachment_id = _id(32)
    other_case_id = _id(33)
    other_document_id = _id(34)
    other_attachment_id = _id(35)
    current_identity = f"{case_id}|filing-main"

    with session_factory() as transaction:
        _seed_source(
            transaction,
            case_id=case_id,
            document_id=document_id,
            attachment_id=attachment_id,
        )
        _seed_source(
            transaction,
            case_id=other_case_id,
            document_id=other_document_id,
            attachment_id=other_attachment_id,
        )
        prior = DocumentEvidenceVersion(
            id=_id(36),
            case_id=case_id,
            document_id=document_id,
            attachment_id=attachment_id,
            lineage_key="filing-main",
            role=EvidenceRole.FILING_FULL_WORD.value,
            version_number=1,
            state=EvidenceVersionState.DRAFT.value,
            creator_id=_id(901),
            review_state=EvidenceReviewState.PENDING.value,
            reviewer_id=None,
            reviewed_at=None,
            final_submitted_at=None,
            content_hash=f"sha256:{'b' * 64}",
            current_identity_key=current_identity,
        )
        transaction.add_all(
            [
                prior,
                DocumentEvidenceVersion(
                    id=_id(37),
                    case_id=case_id,
                    document_id=document_id,
                    attachment_id=attachment_id,
                    lineage_key="oa-reply",
                    role=EvidenceRole.TRACKED_REVISED_WORD.value,
                    version_number=9,
                    state=EvidenceVersionState.DRAFT.value,
                    creator_id=_id(901),
                    review_state=EvidenceReviewState.PENDING.value,
                    content_hash=f"sha256:{'c' * 64}",
                    current_identity_key=None,
                ),
                DocumentEvidenceVersion(
                    id=_id(38),
                    case_id=other_case_id,
                    document_id=other_document_id,
                    attachment_id=other_attachment_id,
                    lineage_key="filing-main",
                    role=EvidenceRole.FILING_FULL_WORD.value,
                    version_number=7,
                    state=EvidenceVersionState.DRAFT.value,
                    creator_id=_id(901),
                    review_state=EvidenceReviewState.PENDING.value,
                    content_hash=f"sha256:{'d' * 64}",
                    current_identity_key=None,
                ),
            ]
        )
        transaction.flush()

        result = register_evidence_version(
            _command(
                case_id=case_id,
                document_id=document_id,
                attachment_id=attachment_id,
            ),
            transaction,
        )

        assert result.version_number == 2
        assert result.is_current is False
        assert result.is_final is False
        assert prior.version_number == 1
        assert prior.content_hash == f"sha256:{'b' * 64}"
        assert prior.current_identity_key == current_identity
        stored = transaction.get(DocumentEvidenceVersion, result.evidence_version_id)
        assert stored is not None
        assert stored.current_identity_key is None
        assert transaction.scalars(
            select(DocumentEvidenceVersion)
            .where(DocumentEvidenceVersion.case_id == case_id)
            .where(DocumentEvidenceVersion.lineage_key == "filing-main")
            .order_by(DocumentEvidenceVersion.version_number)
        ).all() == [prior, stored]


def test_append_error_propagates_and_caller_rollback_removes_the_version(
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    case_id = _id(40)
    document_id = _id(41)
    attachment_id = _id(42)
    append_error = BusinessError(
        code="LIFECYCLE_REVISION_CONFLICT",
        message="append failed",
        status_code=409,
    )

    with session_factory() as transaction:
        _seed_source(
            transaction,
            case_id=case_id,
            document_id=document_id,
            attachment_id=attachment_id,
        )
        case = transaction.get(Case, case_id)
        assert case is not None
        case.lifecycle_revision = 0
        transaction.commit()

        def fail_append(*_args: object, **_kwargs: object) -> None:
            raise append_error

        monkeypatch.setattr(
            evidence_service,
            "append_case_activity",
            fail_append,
            raising=False,
        )

        with pytest.raises(BusinessError) as exc_info:
            register_evidence_version(
                _command(
                    case_id=case_id,
                    document_id=document_id,
                    attachment_id=attachment_id,
                ),
                transaction,
            )

        assert exc_info.value is append_error
        transaction.rollback()

    with session_factory() as verification:
        assert verification.scalars(select(DocumentEvidenceVersion)).all() == []
        assert verification.scalars(select(CaseActivityEvent)).all() == []
        assert verification.scalars(select(CaseActivityEventEvidence)).all() == []
        original_case = verification.get(Case, case_id)
        assert original_case is not None
        assert original_case.status == "NOT_FILED"
        assert original_case.lifecycle_revision == 0


def test_unknown_stored_projection_fails_closed_before_version_insertion(
    session_factory: sessionmaker[Session],
) -> None:
    case_id = _id(50)
    document_id = _id(51)
    attachment_id = _id(52)

    with session_factory() as transaction:
        _seed_source(
            transaction,
            case_id=case_id,
            document_id=document_id,
            attachment_id=attachment_id,
        )
        case = transaction.get(Case, case_id)
        assert case is not None
        case.business_stage = "UNKNOWN_STAGE"
        case.lifecycle_revision = 0
        transaction.commit()

        with pytest.raises(BusinessError) as exc_info:
            register_evidence_version(
                _command(
                    case_id=case_id,
                    document_id=document_id,
                    attachment_id=attachment_id,
                ),
                transaction,
            )

        assert exc_info.value.code == "LIFECYCLE_PROJECTION_CONFLICT"
        assert exc_info.value.status_code == 409
        assert transaction.scalars(select(DocumentEvidenceVersion)).all() == []
        assert transaction.scalars(select(CaseActivityEvent)).all() == []
        assert transaction.scalars(select(CaseActivityEventEvidence)).all() == []
        transaction.rollback()
