from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, datetime
from re import fullmatch
from typing import Literal, NoReturn

from pydantic import BaseModel, ConfigDict, Field, StrictStr, field_validator
from sqlalchemy.orm import Session

from app.core.errors import BusinessError
from app.modules.cases.lifecycle_contracts import (
    ActivityLane,
    ConfirmationStatus,
    EvidenceReference,
    LifecycleEventCommand,
    LifecycleTransitionResult,
)
from app.modules.cases.lifecycle_service import apply_lifecycle_event
from app.modules.cases.models import Case
from app.modules.documents.extra_data import DocumentExtraDataError, parse_document_extra_data
from app.modules.documents.models import Document, DocumentEvidenceVersion

_CANONICAL_HASH_PATTERN = r"sha256:[0-9a-f]{64}"


class PreliminaryExaminationStartIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    evidence_version_id: str = Field(strict=True)
    effective_at: datetime
    occurred_at: datetime | None = None
    idempotency_key: str = Field(strict=True)

    @field_validator("effective_at", "occurred_at")
    @classmethod
    def require_naive_business_time(cls, value: datetime | None) -> datetime | None:
        if value is not None and value.tzinfo is not None:
            raise ValueError("business time must be naive")
        return value


class PreliminaryExaminationPassIn(PreliminaryExaminationStartIn):
    pass


class RectificationNoticeIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    evidence_version_id: StrictStr
    effective_at: datetime
    occurred_at: datetime | None = None
    idempotency_key: StrictStr

    @field_validator("evidence_version_id", mode="before")
    @classmethod
    def require_exact_evidence_version_id(cls, value: object) -> str:
        if (
            type(value) is not str
            or not value
            or value != value.strip()
            or len(value) > 36
        ):
            raise ValueError("evidence_version_id must be an exact nonempty identifier")
        return value

    @field_validator("idempotency_key", mode="before")
    @classmethod
    def require_exact_idempotency_key(cls, value: object) -> str:
        if (
            type(value) is not str
            or not value
            or value != value.strip()
            or len(value) > 128
        ):
            raise ValueError("idempotency_key must be an exact nonempty identifier")
        return value

    @field_validator("effective_at", "occurred_at", mode="before")
    @classmethod
    def require_datetime_input(cls, value: object) -> object:
        if value is not None and type(value) not in {str, datetime}:
            raise ValueError("business time must be an ISO datetime")
        return value

    @field_validator("effective_at", "occurred_at")
    @classmethod
    def require_naive_business_time(cls, value: datetime | None) -> datetime | None:
        if value is not None and (type(value) is not datetime or value.tzinfo is not None):
            raise ValueError("business time must be naive")
        return value


class PublicationNoticeIn(RectificationNoticeIn):
    pass


class SubstantiveExaminationStartIn(RectificationNoticeIn):
    pass


class ReexaminationStartIn(RectificationNoticeIn):
    pass


class ApplicationRejectionIn(RectificationNoticeIn):
    evidence_kind: Literal[
        "REJECTION_DECISION",
        "REEXAMINATION_FINAL_REJECTION_DECISION",
    ]


class ApplicationWithdrawalIn(RectificationNoticeIn):
    confirmation_evidence_version_id: StrictStr

    @field_validator("confirmation_evidence_version_id", mode="before")
    @classmethod
    def require_exact_confirmation_evidence_version_id(cls, value: object) -> str:
        if (
            type(value) is not str
            or not value
            or value != value.strip()
            or len(value) > 36
        ):
            raise ValueError(
                "confirmation_evidence_version_id must be an exact nonempty identifier"
            )
        return value


class ApplicationAbandonmentIn(RectificationNoticeIn):
    evidence_kind: Literal[
        "DEEMED_ABANDONMENT_NOTICE",
        "RIGHT_ABANDONMENT_CONFIRMATION",
    ]


class ApplicationRestorationIn(RectificationNoticeIn):
    restored_official_procedure_stage: Literal[
        "SUBMISSION_CONFIRMED_WAITING_ACCEPTANCE",
        "ACCEPTED",
        "PRELIMINARY_EXAMINATION",
        "RECTIFICATION_RESPONSE",
        "PUBLISHED",
        "SUBSTANTIVE_EXAMINATION",
        "OFFICE_ACTION_RESPONSE",
        "REEXAMINATION",
        "GRANT_REGISTRATION",
    ]


@dataclass(frozen=True, slots=True, kw_only=True)
class StartPreliminaryExaminationCommand:
    document_id: str
    evidence_version_id: str
    actor_id: str
    effective_at: datetime
    occurred_at: datetime | None
    idempotency_key: str


@dataclass(frozen=True, slots=True, kw_only=True)
class StartPreliminaryExaminationResult:
    case_id: str
    document_id: str
    evidence_version_id: str
    activity_id: str
    activity_sequence: int
    lifecycle_revision: int
    effective_at: datetime
    occurred_at: datetime | None
    idempotency_key: str
    reused: bool


@dataclass(frozen=True, slots=True, kw_only=True)
class PassPreliminaryExaminationCommand:
    document_id: str
    evidence_version_id: str
    actor_id: str
    effective_at: datetime
    occurred_at: datetime | None
    idempotency_key: str


@dataclass(frozen=True, slots=True, kw_only=True)
class PassPreliminaryExaminationResult:
    case_id: str
    document_id: str
    evidence_version_id: str
    activity_id: str
    activity_sequence: int
    lifecycle_revision: int
    effective_at: datetime
    occurred_at: datetime | None
    idempotency_key: str
    reused: bool


@dataclass(frozen=True, slots=True, kw_only=True)
class RecordPublicationNoticeCommand:
    document_id: str
    evidence_version_id: str
    actor_id: str
    effective_at: datetime
    occurred_at: datetime | None
    idempotency_key: str


@dataclass(frozen=True, slots=True, kw_only=True)
class RecordPublicationNoticeResult:
    case_id: str
    document_id: str
    evidence_version_id: str
    activity_id: str
    activity_sequence: int
    lifecycle_revision: int
    effective_at: datetime
    occurred_at: datetime | None
    idempotency_key: str
    reused: bool


@dataclass(frozen=True, slots=True, kw_only=True)
class StartSubstantiveExaminationCommand:
    document_id: str
    evidence_version_id: str
    actor_id: str
    effective_at: datetime
    occurred_at: datetime | None
    idempotency_key: str


@dataclass(frozen=True, slots=True, kw_only=True)
class StartSubstantiveExaminationResult:
    case_id: str
    document_id: str
    evidence_version_id: str
    activity_id: str
    activity_sequence: int
    lifecycle_revision: int
    effective_at: datetime
    occurred_at: datetime | None
    idempotency_key: str
    reused: bool


@dataclass(frozen=True, slots=True, kw_only=True)
class StartReexaminationCommand:
    document_id: str
    evidence_version_id: str
    actor_id: str
    effective_at: datetime
    occurred_at: datetime | None
    idempotency_key: str


@dataclass(frozen=True, slots=True, kw_only=True)
class StartReexaminationResult:
    case_id: str
    document_id: str
    evidence_version_id: str
    activity_id: str
    activity_sequence: int
    lifecycle_revision: int
    effective_at: datetime
    occurred_at: datetime | None
    idempotency_key: str
    reused: bool


@dataclass(frozen=True, slots=True, kw_only=True)
class RecordRectificationNoticeCommand:
    document_id: str
    evidence_version_id: str
    actor_id: str
    effective_at: datetime
    occurred_at: datetime | None
    idempotency_key: str


@dataclass(frozen=True, slots=True, kw_only=True)
class RecordRectificationNoticeResult:
    case_id: str
    document_id: str
    evidence_version_id: str
    activity_id: str
    activity_sequence: int
    lifecycle_revision: int
    official_due_date: date
    official_due_date_source: str
    official_due_date_status: str
    idempotency_key: str
    reused: bool


@dataclass(frozen=True, slots=True, kw_only=True)
class RecordApplicationRejectionCommand:
    document_id: str
    evidence_version_id: str
    evidence_kind: str
    actor_id: str
    effective_at: datetime
    occurred_at: datetime | None
    idempotency_key: str


@dataclass(frozen=True, slots=True, kw_only=True)
class RecordApplicationWithdrawalCommand:
    document_id: str
    evidence_version_id: str
    confirmation_evidence_version_id: str
    actor_id: str
    effective_at: datetime
    occurred_at: datetime | None
    idempotency_key: str


@dataclass(frozen=True, slots=True, kw_only=True)
class RecordApplicationAbandonmentCommand:
    document_id: str
    evidence_version_id: str
    evidence_kind: str
    actor_id: str
    effective_at: datetime
    occurred_at: datetime | None
    idempotency_key: str


@dataclass(frozen=True, slots=True, kw_only=True)
class RecordApplicationRestorationCommand:
    document_id: str
    evidence_version_id: str
    restored_official_procedure_stage: str
    actor_id: str
    effective_at: datetime
    occurred_at: datetime | None
    idempotency_key: str


@dataclass(frozen=True, slots=True, kw_only=True)
class TerminalLifecycleEvidenceResult:
    case_id: str
    document_id: str
    evidence_version_id: str
    activity_id: str
    activity_sequence: int
    lifecycle_revision: int
    effective_at: datetime
    occurred_at: datetime | None
    idempotency_key: str
    reused: bool


@dataclass(frozen=True, slots=True, kw_only=True)
class ApplicationWithdrawalEvidenceResult(TerminalLifecycleEvidenceResult):
    confirmation_evidence_version_id: str


def _evidence_relation_mismatch() -> None:
    raise BusinessError(
        "PRELIMINARY_START_EVIDENCE_RELATION_MISMATCH",
        "初步审查来源证据与案件或文件不匹配",
        details={"field": "evidence_version_id"},
        status_code=400,
    )


def _evidence_conflict() -> None:
    raise BusinessError(
        "PRELIMINARY_START_EVIDENCE_CONFLICT",
        "初步审查来源证据状态无效",
        details={"field": "evidence_version_id"},
        status_code=409,
    )


def _pass_evidence_relation_mismatch() -> None:
    raise BusinessError(
        "PRELIMINARY_PASS_EVIDENCE_RELATION_MISMATCH",
        "初步审查合格证据与案件或文件不匹配",
        details={"field": "evidence_version_id"},
        status_code=400,
    )


def _pass_evidence_conflict() -> None:
    raise BusinessError(
        "PRELIMINARY_PASS_EVIDENCE_CONFLICT",
        "初步审查合格证据状态无效",
        details={"field": "evidence_version_id"},
        status_code=409,
    )


def _publication_evidence_relation_mismatch() -> None:
    raise BusinessError(
        "PUBLICATION_NOTICE_EVIDENCE_RELATION_MISMATCH",
        "公布通知书证据与案件或文件不匹配",
        details={"field": "evidence_version_id"},
        status_code=400,
    )


def _publication_evidence_conflict() -> None:
    raise BusinessError(
        "PUBLICATION_NOTICE_EVIDENCE_CONFLICT",
        "公布通知书证据状态无效",
        details={"field": "evidence_version_id"},
        status_code=409,
    )


def _substantive_evidence_relation_mismatch() -> None:
    raise BusinessError(
        "SUBSTANTIVE_START_EVIDENCE_RELATION_MISMATCH",
        "实质审查开始证据与案件或文件不匹配",
        details={"field": "evidence_version_id"},
        status_code=400,
    )


def _substantive_evidence_conflict() -> None:
    raise BusinessError(
        "SUBSTANTIVE_START_EVIDENCE_CONFLICT",
        "实质审查开始证据状态无效",
        details={"field": "evidence_version_id"},
        status_code=409,
    )


def _reexamination_evidence_relation_mismatch() -> None:
    raise BusinessError(
        "REEXAMINATION_START_EVIDENCE_RELATION_MISMATCH",
        "复审开始证据与案件或文件不匹配",
        details={"field": "evidence_version_id"},
        status_code=400,
    )


def _reexamination_evidence_conflict() -> None:
    raise BusinessError(
        "REEXAMINATION_START_EVIDENCE_CONFLICT",
        "复审开始证据状态无效",
        details={"field": "evidence_version_id"},
        status_code=409,
    )


def _rectification_deadline_conflict() -> NoReturn:
    raise BusinessError(
        "RECTIFICATION_NOTICE_DEADLINE_CONFLICT",
        "补正通知书官方期限无效或未经确认",
        details={"field": "OfficialDueDate"},
        status_code=409,
    )


def _rectification_evidence_relation_mismatch() -> NoReturn:
    raise BusinessError(
        "RECTIFICATION_NOTICE_EVIDENCE_RELATION_MISMATCH",
        "补正通知书证据与案件或文件不匹配",
        details={"field": "evidence_version_id"},
        status_code=400,
    )


def _rectification_evidence_conflict() -> NoReturn:
    raise BusinessError(
        "RECTIFICATION_NOTICE_EVIDENCE_CONFLICT",
        "补正通知书证据状态无效",
        details={"field": "evidence_version_id"},
        status_code=409,
    )


def _terminal_relation_mismatch(code: str, message: str) -> NoReturn:
    raise BusinessError(
        code,
        message,
        details={"field": "evidence_version_id"},
        status_code=400,
    )


def _terminal_evidence_conflict(code: str, message: str) -> NoReturn:
    raise BusinessError(
        code,
        message,
        details={"field": "evidence_version_id"},
        status_code=409,
    )


def _invalid_rectification_command(field: str) -> NoReturn:
    raise BusinessError(
        "LIFECYCLE_EVENT_INVALID",
        "生命周期事件参数无效",
        details={"field": field},
        status_code=400,
    )


def _valid_stored_id(value: object) -> bool:
    return type(value) is str and bool(value) and value == value.strip() and len(value) <= 36


def _require_rectification_command(command: RecordRectificationNoticeCommand) -> None:
    if type(command) is not RecordRectificationNoticeCommand:
        _invalid_rectification_command("command")
    for field, limit in (
        ("document_id", 36),
        ("evidence_version_id", 36),
        ("actor_id", 36),
        ("idempotency_key", 128),
    ):
        value = getattr(command, field)
        if (
            type(value) is not str
            or not value
            or value != value.strip()
            or len(value) > limit
        ):
            _invalid_rectification_command(field)
    if type(command.effective_at) is not datetime or command.effective_at.tzinfo is not None:
        _invalid_rectification_command("effective_at")
    if command.occurred_at is not None and (
        type(command.occurred_at) is not datetime or command.occurred_at.tzinfo is not None
    ):
        _invalid_rectification_command("occurred_at")


def _require_rectification_evidence(
    version: DocumentEvidenceVersion,
    *,
    case_id: str,
    document_id: str,
) -> None:
    if version.case_id != case_id or version.document_id != document_id:
        _rectification_evidence_relation_mismatch()
    if (
        not _valid_stored_id(version.id)
        or not _valid_stored_id(version.case_id)
        or not _valid_stored_id(version.document_id)
        or type(version.lineage_key) is not str
        or not version.lineage_key
        or version.lineage_key != version.lineage_key.strip()
        or len(version.lineage_key) > 128
        or version.role != "OFFICIAL_FINAL_PDF"
        or version.state != "FINAL"
        or version.review_state != "APPROVED"
        or not _valid_stored_id(version.creator_id)
        or not _valid_stored_id(version.reviewer_id)
        or version.creator_id == version.reviewer_id
        or type(version.reviewed_at) is not datetime
        or version.reviewed_at.tzinfo is not None
        or type(version.content_hash) is not str
        or fullmatch(_CANONICAL_HASH_PATTERN, version.content_hash) is None
        or version.current_identity_key != f"{case_id}|{version.lineage_key}"
    ):
        _rectification_evidence_conflict()


def _require_eligible_evidence(
    version: DocumentEvidenceVersion,
    *,
    case_id: str,
    document_id: str,
    relation_mismatch: Callable[[], None],
    evidence_conflict: Callable[[], None],
) -> None:
    if (
        not _valid_stored_id(version.id)
        or not _valid_stored_id(version.case_id)
        or not _valid_stored_id(version.document_id)
        or not _valid_stored_id(version.attachment_id)
        or type(version.lineage_key) is not str
        or not version.lineage_key
        or version.lineage_key != version.lineage_key.strip()
        or len(version.lineage_key) > 128
    ):
        evidence_conflict()
    if version.case_id != case_id or version.document_id != document_id:
        relation_mismatch()
    if (
        version.role != "OFFICIAL_FINAL_PDF"
        or version.state != "FINAL"
        or version.review_state != "APPROVED"
        or not _valid_stored_id(version.creator_id)
        or not _valid_stored_id(version.reviewer_id)
        or version.creator_id == version.reviewer_id
        or type(version.reviewed_at) is not datetime
        or version.reviewed_at.tzinfo is not None
        or type(version.content_hash) is not str
        or fullmatch(_CANONICAL_HASH_PATTERN, version.content_hash) is None
        or version.current_identity_key != f"{case_id}|{version.lineage_key}"
    ):
        evidence_conflict()


def _apply_preliminary_evidence_event(
    command: (
        StartPreliminaryExaminationCommand
        | PassPreliminaryExaminationCommand
        | RecordPublicationNoticeCommand
        | StartSubstantiveExaminationCommand
        | StartReexaminationCommand
    ),
    transaction: Session,
    *,
    event_type: str,
    evidence_kind: str,
    relation_mismatch: Callable[[], None],
    evidence_conflict: Callable[[], None],
) -> tuple[Document, DocumentEvidenceVersion, LifecycleTransitionResult]:
    document = transaction.get(Document, command.document_id)
    if document is None:
        raise BusinessError(
            "DOCUMENT_NOT_FOUND",
            "文件不存在",
            status_code=404,
        )
    if not _valid_stored_id(document.id) or not _valid_stored_id(document.case_id):
        evidence_conflict()

    case = transaction.get(Case, document.case_id)
    if case is None:
        raise BusinessError(
            "CASE_NOT_FOUND",
            "案件不存在",
            status_code=404,
        )

    version = transaction.get(DocumentEvidenceVersion, command.evidence_version_id)
    if version is None:
        raise BusinessError(
            "EVIDENCE_VERSION_NOT_FOUND",
            "证据版本不存在",
            status_code=404,
        )
    _require_eligible_evidence(
        version,
        case_id=document.case_id,
        document_id=document.id,
        relation_mismatch=relation_mismatch,
        evidence_conflict=evidence_conflict,
    )

    transition = apply_lifecycle_event(
        LifecycleEventCommand(
            case_id=document.case_id,
            event_type=event_type,
            lane=ActivityLane.LIFECYCLE,
            effective_at=command.effective_at,
            occurred_at=command.occurred_at,
            evidence_refs=(
                EvidenceReference(
                    case_id=document.case_id,
                    evidence_kind=evidence_kind,
                    object_type="DocumentEvidenceVersion",
                    object_id=version.id,
                    content_hash=version.content_hash,
                    captured_at=version.reviewed_at,
                ),
            ),
            actor_id=command.actor_id,
            reviewer_id=None,
            idempotency_key=command.idempotency_key,
            source_activity_id=None,
            supersedes_event_id=None,
            confirmation_status=ConfirmationStatus.CONFIRMED,
            payload={},
        ),
        transaction,
    )
    return document, version, transition


def start_preliminary_examination_from_evidence(
    command: StartPreliminaryExaminationCommand,
    transaction: Session,
) -> StartPreliminaryExaminationResult:
    document, version, transition = _apply_preliminary_evidence_event(
        command,
        transaction,
        event_type="PRELIMINARY_EXAMINATION_STARTED",
        evidence_kind="PRELIMINARY_EXAMINATION_SOURCE",
        relation_mismatch=_evidence_relation_mismatch,
        evidence_conflict=_evidence_conflict,
    )
    return StartPreliminaryExaminationResult(
        case_id=document.case_id,
        document_id=document.id,
        evidence_version_id=version.id,
        activity_id=transition.activity_id,
        activity_sequence=transition.sequence,
        lifecycle_revision=transition.lifecycle_revision,
        effective_at=command.effective_at,
        occurred_at=command.occurred_at,
        idempotency_key=command.idempotency_key,
        reused=transition.reused,
    )


def pass_preliminary_examination_from_evidence(
    command: PassPreliminaryExaminationCommand,
    transaction: Session,
) -> PassPreliminaryExaminationResult:
    document, version, transition = _apply_preliminary_evidence_event(
        command,
        transaction,
        event_type="PRELIMINARY_EXAMINATION_PASSED",
        evidence_kind="PRELIMINARY_EXAMINATION_PASS_NOTICE",
        relation_mismatch=_pass_evidence_relation_mismatch,
        evidence_conflict=_pass_evidence_conflict,
    )
    return PassPreliminaryExaminationResult(
        case_id=document.case_id,
        document_id=document.id,
        evidence_version_id=version.id,
        activity_id=transition.activity_id,
        activity_sequence=transition.sequence,
        lifecycle_revision=transition.lifecycle_revision,
        effective_at=command.effective_at,
        occurred_at=command.occurred_at,
        idempotency_key=command.idempotency_key,
        reused=transition.reused,
    )


def record_publication_notice_from_evidence(
    command: RecordPublicationNoticeCommand,
    transaction: Session,
) -> RecordPublicationNoticeResult:
    document, version, transition = _apply_preliminary_evidence_event(
        command,
        transaction,
        event_type="PUBLICATION_NOTICE_RECORDED",
        evidence_kind="PUBLICATION_NOTICE",
        relation_mismatch=_publication_evidence_relation_mismatch,
        evidence_conflict=_publication_evidence_conflict,
    )
    return RecordPublicationNoticeResult(
        case_id=document.case_id,
        document_id=document.id,
        evidence_version_id=version.id,
        activity_id=transition.activity_id,
        activity_sequence=transition.sequence,
        lifecycle_revision=transition.lifecycle_revision,
        effective_at=command.effective_at,
        occurred_at=command.occurred_at,
        idempotency_key=command.idempotency_key,
        reused=transition.reused,
    )


def start_substantive_examination_from_evidence(
    command: StartSubstantiveExaminationCommand,
    transaction: Session,
) -> StartSubstantiveExaminationResult:
    document, version, transition = _apply_preliminary_evidence_event(
        command,
        transaction,
        event_type="SUBSTANTIVE_EXAMINATION_STARTED",
        evidence_kind="SUBSTANTIVE_EXAMINATION_SOURCE",
        relation_mismatch=_substantive_evidence_relation_mismatch,
        evidence_conflict=_substantive_evidence_conflict,
    )
    return StartSubstantiveExaminationResult(
        case_id=document.case_id,
        document_id=document.id,
        evidence_version_id=version.id,
        activity_id=transition.activity_id,
        activity_sequence=transition.sequence,
        lifecycle_revision=transition.lifecycle_revision,
        effective_at=command.effective_at,
        occurred_at=command.occurred_at,
        idempotency_key=command.idempotency_key,
        reused=transition.reused,
    )


def start_reexamination_from_evidence(
    command: StartReexaminationCommand,
    transaction: Session,
) -> StartReexaminationResult:
    document, version, transition = _apply_preliminary_evidence_event(
        command,
        transaction,
        event_type="REEXAMINATION_STARTED",
        evidence_kind="REEXAMINATION_SOURCE",
        relation_mismatch=_reexamination_evidence_relation_mismatch,
        evidence_conflict=_reexamination_evidence_conflict,
    )
    return StartReexaminationResult(
        case_id=document.case_id,
        document_id=document.id,
        evidence_version_id=version.id,
        activity_id=transition.activity_id,
        activity_sequence=transition.sequence,
        lifecycle_revision=transition.lifecycle_revision,
        effective_at=command.effective_at,
        occurred_at=command.occurred_at,
        idempotency_key=command.idempotency_key,
        reused=transition.reused,
    )


def record_rectification_notice_from_evidence(
    command: RecordRectificationNoticeCommand,
    transaction: Session,
) -> RecordRectificationNoticeResult:
    _require_rectification_command(command)

    with transaction.no_autoflush:
        document = transaction.get(Document, command.document_id)
        if document is None:
            raise BusinessError(
                "DOCUMENT_NOT_FOUND",
                "文件不存在",
                status_code=404,
            )
        if transaction.get(Case, document.case_id) is None:
            raise BusinessError(
                "CASE_NOT_FOUND",
                "案件不存在",
                status_code=404,
            )
        version = transaction.get(DocumentEvidenceVersion, command.evidence_version_id)
        if version is None:
            raise BusinessError(
                "EVIDENCE_VERSION_NOT_FOUND",
                "证据版本不存在",
                status_code=404,
            )

        try:
            deadline = parse_document_extra_data(document.extra_data)
        except DocumentExtraDataError:
            _rectification_deadline_conflict()
        if (
            type(deadline.official_due_date) is not date
            or deadline.official_due_date_source
            not in {"MANUAL_OFFICIAL_NOTICE", "IMPORTED_OFFICIAL_NOTICE"}
            or deadline.official_due_date_status != "CONFIRMED"
        ):
            _rectification_deadline_conflict()
        _require_rectification_evidence(
            version,
            case_id=document.case_id,
            document_id=document.id,
        )

    transition = apply_lifecycle_event(
        LifecycleEventCommand(
            case_id=document.case_id,
            event_type="RECTIFICATION_NOTICE_RECORDED",
            lane=ActivityLane.LIFECYCLE,
            effective_at=command.effective_at,
            occurred_at=command.occurred_at,
            evidence_refs=(
                EvidenceReference(
                    case_id=document.case_id,
                    evidence_kind="RECTIFICATION_NOTICE",
                    object_type="DocumentEvidenceVersion",
                    object_id=version.id,
                    content_hash=version.content_hash,
                    captured_at=version.reviewed_at,
                ),
            ),
            actor_id=command.actor_id,
            reviewer_id=None,
            idempotency_key=command.idempotency_key,
            source_activity_id=None,
            supersedes_event_id=None,
            confirmation_status=ConfirmationStatus.CONFIRMED,
            payload={
                "official_due_date": deadline.official_due_date.isoformat(),
                "official_due_date_source": deadline.official_due_date_source,
                "official_due_date_status": deadline.official_due_date_status,
            },
        ),
        transaction,
    )
    return RecordRectificationNoticeResult(
        case_id=document.case_id,
        document_id=document.id,
        evidence_version_id=version.id,
        activity_id=transition.activity_id,
        activity_sequence=transition.sequence,
        lifecycle_revision=transition.lifecycle_revision,
        official_due_date=deadline.official_due_date,
        official_due_date_source=deadline.official_due_date_source,
        official_due_date_status=deadline.official_due_date_status,
        idempotency_key=command.idempotency_key,
        reused=transition.reused,
    )


def _apply_single_terminal_evidence_event(
    command: (
        RecordApplicationRejectionCommand
        | RecordApplicationAbandonmentCommand
        | RecordApplicationRestorationCommand
    ),
    transaction: Session,
    *,
    event_type: str,
    evidence_kind: str,
    payload: dict[str, str],
    relation_code: str,
    relation_message: str,
    conflict_code: str,
    conflict_message: str,
) -> tuple[Document, DocumentEvidenceVersion, LifecycleTransitionResult]:
    def relation_mismatch() -> None:
        _terminal_relation_mismatch(relation_code, relation_message)

    def evidence_conflict() -> None:
        _terminal_evidence_conflict(conflict_code, conflict_message)

    document = transaction.get(Document, command.document_id)
    if document is None:
        raise BusinessError("DOCUMENT_NOT_FOUND", "文件不存在", status_code=404)
    if not _valid_stored_id(document.id) or not _valid_stored_id(document.case_id):
        evidence_conflict()
    if transaction.get(Case, document.case_id) is None:
        raise BusinessError("CASE_NOT_FOUND", "案件不存在", status_code=404)

    version = transaction.get(DocumentEvidenceVersion, command.evidence_version_id)
    if version is None:
        raise BusinessError("EVIDENCE_VERSION_NOT_FOUND", "证据版本不存在", status_code=404)
    _require_eligible_evidence(
        version,
        case_id=document.case_id,
        document_id=document.id,
        relation_mismatch=relation_mismatch,
        evidence_conflict=evidence_conflict,
    )

    transition = apply_lifecycle_event(
        LifecycleEventCommand(
            case_id=document.case_id,
            event_type=event_type,
            lane=ActivityLane.LIFECYCLE,
            effective_at=command.effective_at,
            occurred_at=command.occurred_at,
            evidence_refs=(
                EvidenceReference(
                    case_id=document.case_id,
                    evidence_kind=evidence_kind,
                    object_type="DocumentEvidenceVersion",
                    object_id=version.id,
                    content_hash=version.content_hash,
                    captured_at=version.reviewed_at,
                ),
            ),
            actor_id=command.actor_id,
            reviewer_id=None,
            idempotency_key=command.idempotency_key,
            source_activity_id=None,
            supersedes_event_id=None,
            confirmation_status=ConfirmationStatus.CONFIRMED,
            payload=payload,
        ),
        transaction,
    )
    return document, version, transition


def _terminal_result(
    *,
    document: Document,
    version: DocumentEvidenceVersion,
    transition: LifecycleTransitionResult,
    effective_at: datetime,
    occurred_at: datetime | None,
    idempotency_key: str,
) -> TerminalLifecycleEvidenceResult:
    return TerminalLifecycleEvidenceResult(
        case_id=document.case_id,
        document_id=document.id,
        evidence_version_id=version.id,
        activity_id=transition.activity_id,
        activity_sequence=transition.sequence,
        lifecycle_revision=transition.lifecycle_revision,
        effective_at=effective_at,
        occurred_at=occurred_at,
        idempotency_key=idempotency_key,
        reused=transition.reused,
    )


def record_application_rejection_from_evidence(
    command: RecordApplicationRejectionCommand,
    transaction: Session,
) -> TerminalLifecycleEvidenceResult:
    document, version, transition = _apply_single_terminal_evidence_event(
        command,
        transaction,
        event_type="APPLICATION_REJECTION_CONFIRMED",
        evidence_kind=command.evidence_kind,
        payload={},
        relation_code="APPLICATION_REJECTION_EVIDENCE_RELATION_MISMATCH",
        relation_message="驳回决定证据与案件或文件不匹配",
        conflict_code="APPLICATION_REJECTION_EVIDENCE_CONFLICT",
        conflict_message="驳回决定证据状态无效",
    )
    return _terminal_result(
        document=document,
        version=version,
        transition=transition,
        effective_at=command.effective_at,
        occurred_at=command.occurred_at,
        idempotency_key=command.idempotency_key,
    )


def record_application_abandonment_from_evidence(
    command: RecordApplicationAbandonmentCommand,
    transaction: Session,
) -> TerminalLifecycleEvidenceResult:
    document, version, transition = _apply_single_terminal_evidence_event(
        command,
        transaction,
        event_type="APPLICATION_ABANDONMENT_CONFIRMED",
        evidence_kind=command.evidence_kind,
        payload={},
        relation_code="APPLICATION_ABANDONMENT_EVIDENCE_RELATION_MISMATCH",
        relation_message="申请放弃证据与案件或文件不匹配",
        conflict_code="APPLICATION_ABANDONMENT_EVIDENCE_CONFLICT",
        conflict_message="申请放弃证据状态无效",
    )
    return _terminal_result(
        document=document,
        version=version,
        transition=transition,
        effective_at=command.effective_at,
        occurred_at=command.occurred_at,
        idempotency_key=command.idempotency_key,
    )


def record_application_restoration_from_evidence(
    command: RecordApplicationRestorationCommand,
    transaction: Session,
) -> TerminalLifecycleEvidenceResult:
    document, version, transition = _apply_single_terminal_evidence_event(
        command,
        transaction,
        event_type="APPLICATION_RIGHT_RESTORATION_CONFIRMED",
        evidence_kind="APPLICATION_RIGHT_RESTORATION_DECISION",
        payload={
            "restored_official_procedure_stage": command.restored_official_procedure_stage
        },
        relation_code="APPLICATION_RESTORATION_EVIDENCE_RELATION_MISMATCH",
        relation_message="申请权利恢复决定证据与案件或文件不匹配",
        conflict_code="APPLICATION_RESTORATION_EVIDENCE_CONFLICT",
        conflict_message="申请权利恢复决定证据状态无效",
    )
    return _terminal_result(
        document=document,
        version=version,
        transition=transition,
        effective_at=command.effective_at,
        occurred_at=command.occurred_at,
        idempotency_key=command.idempotency_key,
    )


def record_application_withdrawal_from_evidence(
    command: RecordApplicationWithdrawalCommand,
    transaction: Session,
) -> ApplicationWithdrawalEvidenceResult:
    def relation_mismatch() -> None:
        _terminal_relation_mismatch(
            "APPLICATION_WITHDRAWAL_EVIDENCE_RELATION_MISMATCH",
            "申请撤回证据与案件或文件不匹配",
        )

    def evidence_conflict() -> None:
        _terminal_evidence_conflict(
            "APPLICATION_WITHDRAWAL_EVIDENCE_CONFLICT",
            "申请撤回证据状态无效",
        )

    document = transaction.get(Document, command.document_id)
    if document is None:
        raise BusinessError("DOCUMENT_NOT_FOUND", "文件不存在", status_code=404)
    if not _valid_stored_id(document.id) or not _valid_stored_id(document.case_id):
        evidence_conflict()
    if transaction.get(Case, document.case_id) is None:
        raise BusinessError("CASE_NOT_FOUND", "案件不存在", status_code=404)

    request_version = transaction.get(
        DocumentEvidenceVersion,
        command.evidence_version_id,
    )
    confirmation_version = transaction.get(
        DocumentEvidenceVersion,
        command.confirmation_evidence_version_id,
    )
    if request_version is None or confirmation_version is None:
        raise BusinessError("EVIDENCE_VERSION_NOT_FOUND", "证据版本不存在", status_code=404)
    _require_eligible_evidence(
        request_version,
        case_id=document.case_id,
        document_id=document.id,
        relation_mismatch=relation_mismatch,
        evidence_conflict=evidence_conflict,
    )
    if (
        request_version.id == confirmation_version.id
        or confirmation_version.case_id != document.case_id
    ):
        relation_mismatch()
    _require_eligible_evidence(
        confirmation_version,
        case_id=document.case_id,
        document_id=confirmation_version.document_id,
        relation_mismatch=relation_mismatch,
        evidence_conflict=evidence_conflict,
    )

    transition = apply_lifecycle_event(
        LifecycleEventCommand(
            case_id=document.case_id,
            event_type="APPLICATION_WITHDRAWAL_CONFIRMED",
            lane=ActivityLane.LIFECYCLE,
            effective_at=command.effective_at,
            occurred_at=command.occurred_at,
            evidence_refs=(
                EvidenceReference(
                    case_id=document.case_id,
                    evidence_kind="APPLICATION_WITHDRAWAL_REQUEST",
                    object_type="DocumentEvidenceVersion",
                    object_id=request_version.id,
                    content_hash=request_version.content_hash,
                    captured_at=request_version.reviewed_at,
                ),
                EvidenceReference(
                    case_id=document.case_id,
                    evidence_kind="APPLICATION_WITHDRAWAL_OFFICIAL_CONFIRMATION",
                    object_type="DocumentEvidenceVersion",
                    object_id=confirmation_version.id,
                    content_hash=confirmation_version.content_hash,
                    captured_at=confirmation_version.reviewed_at,
                ),
            ),
            actor_id=command.actor_id,
            reviewer_id=None,
            idempotency_key=command.idempotency_key,
            source_activity_id=None,
            supersedes_event_id=None,
            confirmation_status=ConfirmationStatus.CONFIRMED,
            payload={},
        ),
        transaction,
    )
    return ApplicationWithdrawalEvidenceResult(
        case_id=document.case_id,
        document_id=document.id,
        evidence_version_id=request_version.id,
        confirmation_evidence_version_id=confirmation_version.id,
        activity_id=transition.activity_id,
        activity_sequence=transition.sequence,
        lifecycle_revision=transition.lifecycle_revision,
        effective_at=command.effective_at,
        occurred_at=command.occurred_at,
        idempotency_key=command.idempotency_key,
        reused=transition.reused,
    )
