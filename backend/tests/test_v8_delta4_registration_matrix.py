from __future__ import annotations

from enum import Enum

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.core.errors import BusinessError
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


class _FutureEvidenceRole(str, Enum):
    FUTURE_UNLISTED_ROLE = "FUTURE_UNLISTED_ROLE"


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
    role: EvidenceRole | _FutureEvidenceRole,
    state: EvidenceVersionState,
) -> RegisterEvidenceVersionCommand:
    return RegisterEvidenceVersionCommand(
        case_id=case_id,
        document_id=document_id,
        attachment_id=attachment_id,
        lineage_key="delta4-registration-matrix",
        role=role,  # type: ignore[arg-type]
        state=state,
        creator_id=_id(900),
        content_hash=f"sha256:{'a' * 64}",
    )


@pytest.mark.parametrize(
    ("role", "state", "identity_base"),
    (
        (EvidenceRole.GENERATED_ATTACHMENT, EvidenceVersionState.DRAFT, 100),
        (EvidenceRole.OA_STRUCTURED_ATTACHMENT, EvidenceVersionState.DRAFT, 200),
        (EvidenceRole.OA_STRUCTURED_ATTACHMENT, EvidenceVersionState.FINAL, 300),
    ),
)
def test_new_allowed_role_state_reaches_accepted_public_registration(
    role: EvidenceRole,
    state: EvidenceVersionState,
    identity_base: int,
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    case_id = _id(identity_base)
    document_id = _id(identity_base + 1)
    attachment_id = _id(identity_base + 2)

    with session_factory() as transaction:
        _seed_source(
            transaction,
            case_id=case_id,
            document_id=document_id,
            attachment_id=attachment_id,
        )

        def forbidden_commit() -> None:
            pytest.fail("register_evidence_version must not commit")

        monkeypatch.setattr(transaction, "commit", forbidden_commit)
        result = evidence_service.register_evidence_version(
            _command(
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
        evidence_links = transaction.scalars(
            select(CaseActivityEventEvidence).where(CaseActivityEventEvidence.case_id == case_id)
        ).all()

        assert result.role is role
        assert result.state is state
        assert result.review_state is EvidenceReviewState.PENDING
        assert len(versions) == 1
        assert versions[0].role == role.value
        assert versions[0].state == state.value
        assert versions[0].review_state == EvidenceReviewState.PENDING.value
        assert len(activities) == 1
        assert activities[0].activity_type == "DOCUMENT_EVIDENCE_VERSION_REGISTERED"
        assert len(evidence_links) == 1
        assert evidence_links[0].activity_id == activities[0].id
        assert evidence_links[0].object_id == result.evidence_version_id
        transaction.rollback()


def test_generated_attachment_final_rejects_state_before_transaction_or_activity(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    activity_calls: list[object] = []

    def forbidden_append(*args: object, **_kwargs: object) -> None:
        activity_calls.extend(args)
        pytest.fail("denied role/state must reject before activity append")

    monkeypatch.setattr(evidence_service, "append_case_activity", forbidden_append)
    transaction = _ForbiddenTransaction()

    with pytest.raises(BusinessError) as exc_info:
        evidence_service.register_evidence_version(
            _command(
                case_id=_id(401),
                document_id=_id(402),
                attachment_id=_id(403),
                role=EvidenceRole.GENERATED_ATTACHMENT,
                state=EvidenceVersionState.FINAL,
            ),
            transaction,  # type: ignore[arg-type]
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.code == "EVIDENCE_VERSION_INVALID"
    assert exc_info.value.details == {"field": "state"}
    assert transaction.calls == []
    assert transaction.new == ()
    assert activity_calls == []


@pytest.mark.parametrize(
    "state",
    (EvidenceVersionState.DRAFT, EvidenceVersionState.FINAL),
)
def test_future_unlisted_role_rejects_role_before_transaction_or_activity(
    state: EvidenceVersionState,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(evidence_service, "EvidenceRole", _FutureEvidenceRole)
    activity_calls: list[object] = []

    def forbidden_append(*args: object, **_kwargs: object) -> None:
        activity_calls.extend(args)
        pytest.fail("denied role/state must reject before activity append")

    monkeypatch.setattr(evidence_service, "append_case_activity", forbidden_append)
    transaction = _ForbiddenTransaction()

    with pytest.raises(BusinessError) as exc_info:
        evidence_service.register_evidence_version(
            _command(
                case_id=_id(501),
                document_id=_id(502),
                attachment_id=_id(503),
                role=_FutureEvidenceRole.FUTURE_UNLISTED_ROLE,
                state=state,
            ),
            transaction,  # type: ignore[arg-type]
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.code == "EVIDENCE_VERSION_INVALID"
    assert exc_info.value.details == {"field": "role"}
    assert transaction.calls == []
    assert transaction.new == ()
    assert activity_calls == []
