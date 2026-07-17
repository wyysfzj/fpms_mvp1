from __future__ import annotations

import json
from enum import Enum

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.core.errors import BusinessError
from app.modules.cases.lifecycle_contracts import ActivityLane
from app.modules.cases.models import Case, CaseActivityEvent, CaseActivityEventEvidence
from app.modules.documents import evidence_service
from app.modules.documents.evidence_contracts import (
    EvidenceReviewState,
    EvidenceRole,
    EvidenceVersionState,
    RegisterEvidenceVersionCommand,
)
from app.modules.documents.models import (
    DocAttachment,
    Document,
    DocumentEvidenceVersion,
)


class _ForwardEvidenceRole(str, Enum):
    FILING_FULL_WORD = "FILING_FULL_WORD"
    TRACKED_REVISED_WORD = "TRACKED_REVISED_WORD"
    FILING_COMPONENT = "FILING_COMPONENT"
    EXTERNAL_XML_PACKAGE = "EXTERNAL_XML_PACKAGE"
    OFFICIAL_SUBMISSION_LIST = "OFFICIAL_SUBMISSION_LIST"
    OFFICIAL_FINAL_PDF = "OFFICIAL_FINAL_PDF"
    SUBMITTED_XML = "SUBMITTED_XML"
    OFFICIAL_RECEIPT = "OFFICIAL_RECEIPT"
    CLIENT_LETTER_WORD = "CLIENT_LETTER_WORD"
    RAW_ATTACHMENT = "RAW_ATTACHMENT"
    FUTURE_UNLISTED_ROLE = "FUTURE_UNLISTED_ROLE"


_ORIGINAL_ROLE_VALUES = (
    EvidenceRole.FILING_FULL_WORD,
    EvidenceRole.TRACKED_REVISED_WORD,
    EvidenceRole.FILING_COMPONENT,
    EvidenceRole.EXTERNAL_XML_PACKAGE,
    EvidenceRole.OFFICIAL_SUBMISSION_LIST,
    EvidenceRole.OFFICIAL_FINAL_PDF,
    EvidenceRole.SUBMITTED_XML,
    EvidenceRole.OFFICIAL_RECEIPT,
    EvidenceRole.CLIENT_LETTER_WORD,
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


def _registration_command(
    *,
    case_id: str,
    document_id: str,
    attachment_id: str,
    role: EvidenceRole | _ForwardEvidenceRole,
    state: EvidenceVersionState,
) -> RegisterEvidenceVersionCommand:
    return RegisterEvidenceVersionCommand(
        case_id=case_id,
        document_id=document_id,
        attachment_id=attachment_id,
        lineage_key="raw-attachment-guard",
        role=role,  # type: ignore[arg-type]
        state=state,
        creator_id=_id(900),
        content_hash=f"sha256:{'a' * 64}",
    )


class _ForbiddenTransaction:
    def __init__(self) -> None:
        self.calls: list[str] = []
        self.new: tuple[object, ...] = ()

    def _fail(self, operation: str) -> None:
        self.calls.append(operation)
        pytest.fail(f"denied role/state must reject before transaction.{operation}")

    def get(self, *_args: object, **_kwargs: object) -> None:
        self._fail("get")

    def scalar(self, *_args: object, **_kwargs: object) -> None:
        self._fail("scalar")

    def add(self, *_args: object, **_kwargs: object) -> None:
        self._fail("add")

    def execute(self, *_args: object, **_kwargs: object) -> None:
        self._fail("execute")

    def flush(self, *_args: object, **_kwargs: object) -> None:
        self._fail("flush")

    def refresh(self, *_args: object, **_kwargs: object) -> None:
        self._fail("refresh")


@pytest.mark.parametrize(
    ("role", "state", "field"),
    (
        (
            EvidenceRole.RAW_ATTACHMENT,
            EvidenceVersionState.FINAL,
            "state",
        ),
        (
            _ForwardEvidenceRole.FUTURE_UNLISTED_ROLE,
            EvidenceVersionState.DRAFT,
            "role",
        ),
        (
            _ForwardEvidenceRole.FUTURE_UNLISTED_ROLE,
            EvidenceVersionState.FINAL,
            "role",
        ),
    ),
)
def test_denied_forward_role_state_rejects_before_transaction_or_activity(
    role: EvidenceRole | _ForwardEvidenceRole,
    state: EvidenceVersionState,
    field: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    if role is _ForwardEvidenceRole.FUTURE_UNLISTED_ROLE:
        monkeypatch.setattr(evidence_service, "EvidenceRole", _ForwardEvidenceRole)
    activity_calls: list[object] = []

    def forbidden_append(*args: object, **_kwargs: object) -> None:
        activity_calls.extend(args)
        pytest.fail("denied role/state must reject before activity append")

    monkeypatch.setattr(evidence_service, "append_case_activity", forbidden_append)
    command = RegisterEvidenceVersionCommand(
        case_id="00000000-0000-0000-0000-000000000001",
        document_id="00000000-0000-0000-0000-000000000002",
        attachment_id="00000000-0000-0000-0000-000000000003",
        lineage_key="raw-attachment",
        role=role,  # type: ignore[arg-type]
        state=state,
        creator_id="00000000-0000-0000-0000-000000000004",
        content_hash=f"sha256:{'a' * 64}",
    )
    transaction = _ForbiddenTransaction()

    with pytest.raises(BusinessError) as exc_info:
        evidence_service.register_evidence_version(
            command,
            transaction,  # type: ignore[arg-type]
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.code == "EVIDENCE_VERSION_INVALID"
    assert exc_info.value.details == {"field": field}
    assert transaction.calls == []
    assert transaction.new == ()
    assert activity_calls == []


@pytest.mark.parametrize("role", _ORIGINAL_ROLE_VALUES)
@pytest.mark.parametrize(
    "state",
    (EvidenceVersionState.DRAFT, EvidenceVersionState.FINAL),
)
def test_original_role_state_matrix_reaches_accepted_public_registration(
    role: EvidenceRole,
    state: EvidenceVersionState,
    session_factory: sessionmaker[Session],
) -> None:
    role_index = _ORIGINAL_ROLE_VALUES.index(role)
    state_offset = 0 if state is EvidenceVersionState.DRAFT else 1
    identity_base = 100 + role_index * 10 + state_offset
    case_id = _id(identity_base)
    document_id = _id(identity_base + 300)
    attachment_id = _id(identity_base + 600)

    with session_factory() as transaction:
        _seed_source(
            transaction,
            case_id=case_id,
            document_id=document_id,
            attachment_id=attachment_id,
        )
        result = evidence_service.register_evidence_version(
            _registration_command(
                case_id=case_id,
                document_id=document_id,
                attachment_id=attachment_id,
                role=role,
                state=state,
            ),
            transaction,
        )

        versions = transaction.scalars(
            select(DocumentEvidenceVersion).where(DocumentEvidenceVersion.case_id == case_id)
        ).all()
        activities = transaction.scalars(
            select(CaseActivityEvent).where(CaseActivityEvent.case_id == case_id)
        ).all()

        assert result.role is role
        assert result.state is state
        assert len(versions) == 1
        assert versions[0].role == role.value
        assert versions[0].state == state.value
        assert len(activities) == 1
        assert activities[0].activity_type == "DOCUMENT_EVIDENCE_VERSION_REGISTERED"
        assert activities[0].lane == ActivityLane.DOCUMENT.value
        transaction.rollback()


def test_raw_attachment_draft_persists_pending_version_and_registration_activity(
    session_factory: sessionmaker[Session],
) -> None:
    case_id = _id(1001)
    document_id = _id(1002)
    attachment_id = _id(1003)

    with session_factory() as transaction:
        _seed_source(
            transaction,
            case_id=case_id,
            document_id=document_id,
            attachment_id=attachment_id,
        )
        result = evidence_service.register_evidence_version(
            _registration_command(
                case_id=case_id,
                document_id=document_id,
                attachment_id=attachment_id,
                role=EvidenceRole.RAW_ATTACHMENT,
                state=EvidenceVersionState.DRAFT,
            ),
            transaction,
        )

        assert result.role is EvidenceRole.RAW_ATTACHMENT
        assert result.state is EvidenceVersionState.DRAFT
        assert result.review_state is EvidenceReviewState.PENDING
        transaction.commit()

    with session_factory() as verification:
        versions = verification.scalars(
            select(DocumentEvidenceVersion).where(DocumentEvidenceVersion.case_id == case_id)
        ).all()
        activities = verification.scalars(
            select(CaseActivityEvent).where(CaseActivityEvent.case_id == case_id)
        ).all()
        evidence_links = verification.scalars(
            select(CaseActivityEventEvidence).where(CaseActivityEventEvidence.case_id == case_id)
        ).all()

        assert len(versions) == 1
        stored = versions[0]
        assert stored.id == result.evidence_version_id
        assert stored.role == EvidenceRole.RAW_ATTACHMENT.value
        assert stored.state == EvidenceVersionState.DRAFT.value
        assert stored.review_state == EvidenceReviewState.PENDING.value

        assert len(activities) == 1
        activity = activities[0]
        assert activity.activity_type == "DOCUMENT_EVIDENCE_VERSION_REGISTERED"
        assert activity.lane == ActivityLane.DOCUMENT.value
        assert json.loads(activity.payload_json) == {
            "attachment_id": attachment_id,
            "document_id": document_id,
            "evidence_version_id": result.evidence_version_id,
            "lineage_key": "raw-attachment-guard",
            "review_state": EvidenceReviewState.PENDING.value,
            "role": EvidenceRole.RAW_ATTACHMENT.value,
            "state": EvidenceVersionState.DRAFT.value,
            "version_number": 1,
        }

        assert len(evidence_links) == 1
        assert evidence_links[0].activity_id == activity.id
        assert evidence_links[0].object_id == result.evidence_version_id
