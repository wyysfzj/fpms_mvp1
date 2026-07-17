from __future__ import annotations

import inspect
import json
from dataclasses import FrozenInstanceError, fields, is_dataclass, replace
from datetime import datetime, timezone
from typing import get_type_hints
from unittest.mock import Mock

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.core.errors import BusinessError
from app.modules.cases import lifecycle_projection
from app.modules.cases.lifecycle_contracts import (
    ActivityLane,
    BusinessStage,
    ConfirmationStatus,
    LegalStatus,
    OfficialProcedureStage,
)
from app.modules.cases.models import Case, CaseActivityEvent, CaseActivityEventEvidence
from app.modules.documents import evidence_service
from app.modules.documents.evidence_contracts import (
    EvidenceDerivationType,
    EvidenceReviewState,
    EvidenceRole,
    EvidenceVersionState,
)
from app.modules.documents.evidence_service import (
    SwitchCurrentEvidenceVersionCommand,
    SwitchCurrentEvidenceVersionResult,
    switch_current_evidence_version,
)
from app.modules.documents.models import (
    DocAttachment,
    Document,
    DocumentEvidenceDerivation,
    DocumentEvidenceVersion,
)

SWITCHED_AT = datetime(2026, 7, 13, 10, 30)
LINEAGE_KEY = "filing-main"


def _id(value: int) -> str:
    return f"00000000-0000-0000-0000-{value:012d}"


def _seed_case(transaction: Session, *, case_id: str = _id(1)) -> Case:
    case = Case(
        id=case_id,
        case_no=f"CASE-{case_id[-12:]}",
        status="ACCEPTED",
        business_stage=BusinessStage.PROSECUTION_MANAGEMENT.value,
        official_procedure_stage=OfficialProcedureStage.ACCEPTED.value,
        legal_status=LegalStatus.APPLICATION_PENDING.value,
        lifecycle_verification_status=ConfirmationStatus.CONFIRMED.value,
        lifecycle_revision=0,
    )
    transaction.add(case)
    transaction.flush()
    return case


def _seed_version(
    transaction: Session,
    *,
    case_id: str,
    version_id: str,
    ordinal: int,
    lineage_key: str = LINEAGE_KEY,
    state: str = EvidenceVersionState.DRAFT.value,
    review_state: str = EvidenceReviewState.PENDING.value,
    is_current: bool = False,
    content_hash: str | None = None,
) -> DocumentEvidenceVersion:
    version_seed = int(version_id[-12:])
    document_id = _id(100_000 + version_seed * 2)
    attachment_id = _id(100_001 + version_seed * 2)
    transaction.add(Document(id=document_id, case_id=case_id))
    transaction.flush()
    transaction.add(
        DocAttachment(
            id=attachment_id,
            document_id=document_id,
            file_name=f"version-{ordinal}.docx",
            file_path=f"/evidence/version-{ordinal}.docx",
        )
    )
    transaction.flush()
    version = DocumentEvidenceVersion(
        id=version_id,
        case_id=case_id,
        document_id=document_id,
        attachment_id=attachment_id,
        lineage_key=lineage_key,
        role=EvidenceRole.FILING_FULL_WORD.value,
        version_number=ordinal,
        state=state,
        creator_id=_id(800),
        review_state=review_state,
        reviewer_id=None,
        reviewed_at=None,
        final_submitted_at=None,
        content_hash=content_hash or f"sha256:{ordinal:064x}",
        current_identity_key=f"{case_id}|{lineage_key}" if is_current else None,
    )
    transaction.add(version)
    transaction.flush()
    return version


def _seed_switch_fixture(
    transaction: Session,
    *,
    case_id: str = _id(1),
    current_id: str = _id(2),
    target_id: str = _id(3),
    current_state: str = EvidenceVersionState.DRAFT.value,
    target_state: str = EvidenceVersionState.DRAFT.value,
    target_review_state: str = EvidenceReviewState.PENDING.value,
) -> tuple[Case, DocumentEvidenceVersion, DocumentEvidenceVersion]:
    case = _seed_case(transaction, case_id=case_id)
    current = _seed_version(
        transaction,
        case_id=case_id,
        version_id=current_id,
        ordinal=1,
        state=current_state,
        is_current=True,
    )
    target = _seed_version(
        transaction,
        case_id=case_id,
        version_id=target_id,
        ordinal=2,
        state=target_state,
        review_state=target_review_state,
    )
    transaction.commit()
    return case, current, target


def _command(
    *,
    case_id: str = _id(1),
    current_id: str = _id(2),
    target_id: str = _id(3),
    actor_id: str = _id(900),
    switched_at: datetime = SWITCHED_AT,
    idempotency_key: str = "switch-1",
) -> SwitchCurrentEvidenceVersionCommand:
    return SwitchCurrentEvidenceVersionCommand(
        case_id=case_id,
        expected_current_evidence_version_id=current_id,
        target_evidence_version_id=target_id,
        actor_id=actor_id,
        switched_at=switched_at,
        idempotency_key=idempotency_key,
    )


def _assert_error(
    expected_code: str,
    expected_status: int,
    callable_: object,
) -> BusinessError:
    with pytest.raises(BusinessError) as exc_info:
        callable_()  # type: ignore[operator]
    error = exc_info.value
    assert (error.code, error.status_code) == (expected_code, expected_status)
    return error


def _activity_count(transaction: Session) -> int:
    return len(transaction.scalars(select(CaseActivityEvent)).all())


def test_public_contract_is_exact_frozen_slotted_and_keyword_only() -> None:
    expected_command_fields = (
        ("case_id", str),
        ("expected_current_evidence_version_id", str),
        ("target_evidence_version_id", str),
        ("actor_id", str),
        ("switched_at", datetime),
        ("idempotency_key", str),
    )
    expected_result_fields = (
        ("case_id", str),
        ("lineage_key", str),
        ("previous_current_evidence_version_id", str),
        ("current_evidence_version_id", str),
        ("activity_id", str),
        ("activity_sequence", int),
        ("lifecycle_revision", int),
        ("switched_at", datetime),
        ("idempotency_key", str),
        ("reused", bool),
    )

    for data_type, expected_fields in (
        (SwitchCurrentEvidenceVersionCommand, expected_command_fields),
        (SwitchCurrentEvidenceVersionResult, expected_result_fields),
    ):
        assert is_dataclass(data_type)
        assert data_type.__dataclass_params__.frozen is True
        type_hints = get_type_hints(data_type)
        assert tuple((field.name, type_hints[field.name]) for field in fields(data_type)) == (
            expected_fields
        )
        assert all(field.kw_only for field in fields(data_type))
        assert "__slots__" in data_type.__dict__
        assert all(
            parameter.kind is inspect.Parameter.KEYWORD_ONLY
            for parameter in inspect.signature(data_type).parameters.values()
        )

    signature = inspect.signature(switch_current_evidence_version)
    assert tuple(signature.parameters) == ("command", "transaction")
    assert all(
        parameter.kind is inspect.Parameter.POSITIONAL_OR_KEYWORD
        for parameter in signature.parameters.values()
    )


def test_switch_moves_only_current_identity_and_appends_exact_document_activity(
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with session_factory() as transaction:
        case, current, target = _seed_switch_fixture(transaction)
        immutable_before = {
            version.id: (
                version.case_id,
                version.document_id,
                version.attachment_id,
                version.lineage_key,
                version.role,
                version.version_number,
                version.state,
                version.creator_id,
                version.review_state,
                version.reviewer_id,
                version.reviewed_at,
                version.final_submitted_at,
                version.content_hash,
            )
            for version in (current, target)
        }
        commit = Mock(side_effect=AssertionError("service must not commit"))
        rollback = Mock(side_effect=AssertionError("service must not roll back"))
        monkeypatch.setattr(transaction, "commit", commit)
        monkeypatch.setattr(transaction, "rollback", rollback)

        def forbidden_projection(*_args: object, **_kwargs: object) -> str:
            raise AssertionError("legacy projection adapter must not be called")

        monkeypatch.setattr(
            lifecycle_projection,
            "project_legacy_case_status",
            forbidden_projection,
        )

        result = switch_current_evidence_version(_command(), transaction)

        assert result == SwitchCurrentEvidenceVersionResult(
            case_id=_id(1),
            lineage_key=LINEAGE_KEY,
            previous_current_evidence_version_id=_id(2),
            current_evidence_version_id=_id(3),
            activity_id=result.activity_id,
            activity_sequence=1,
            lifecycle_revision=1,
            switched_at=SWITCHED_AT,
            idempotency_key="switch-1",
            reused=False,
        )
        with pytest.raises(FrozenInstanceError):
            result.reused = True  # type: ignore[misc]
        assert commit.call_count == rollback.call_count == 0

        versions = transaction.scalars(
            select(DocumentEvidenceVersion).order_by(DocumentEvidenceVersion.version_number)
        ).all()
        assert [version.current_identity_key for version in versions] == [
            None,
            f"{_id(1)}|{LINEAGE_KEY}",
        ]
        for version in versions:
            assert immutable_before[version.id] == (
                version.case_id,
                version.document_id,
                version.attachment_id,
                version.lineage_key,
                version.role,
                version.version_number,
                version.state,
                version.creator_id,
                version.review_state,
                version.reviewer_id,
                version.reviewed_at,
                version.final_submitted_at,
                version.content_hash,
            )

        activity = transaction.scalars(select(CaseActivityEvent)).one()
        assert activity.id == result.activity_id
        assert activity.sequence == 1
        assert activity.lane == ActivityLane.DOCUMENT.value
        assert activity.activity_type == "DOCUMENT_EVIDENCE_CURRENT_VERSION_SWITCHED"
        assert activity.effective_at == activity.occurred_at == SWITCHED_AT
        assert activity.actor_id == _id(900)
        assert activity.reviewer_id is None
        assert activity.source_activity_id is None
        assert activity.supersedes_event_id is None
        assert activity.confirmation_status == ConfirmationStatus.CONFIRMED.value
        assert activity.idempotency_key == "document-current-version:switch-1"
        assert json.loads(activity.payload_json) == {
            "current_evidence_version_id": _id(3),
            "lineage_key": LINEAGE_KEY,
            "previous_current_evidence_version_id": _id(2),
        }
        assert all(
            old == new
            for old, new in (
                (activity.old_business_stage, activity.new_business_stage),
                (
                    activity.old_official_procedure_stage,
                    activity.new_official_procedure_stage,
                ),
                (activity.old_legal_status, activity.new_legal_status),
            )
        )

        links = transaction.scalars(
            select(CaseActivityEventEvidence).order_by(CaseActivityEventEvidence.object_id)
        ).all()
        assert [
            (
                link.case_id,
                link.activity_id,
                link.evidence_kind,
                link.object_type,
                link.object_id,
                link.content_hash,
                link.captured_at,
            )
            for link in links
        ] == [
            (
                _id(1),
                result.activity_id,
                "DOCUMENT_EVIDENCE_VERSION",
                "DocumentEvidenceVersion",
                _id(2),
                current.content_hash,
                SWITCHED_AT,
            ),
            (
                _id(1),
                result.activity_id,
                "DOCUMENT_EVIDENCE_VERSION",
                "DocumentEvidenceVersion",
                _id(3),
                target.content_hash,
                SWITCHED_AT,
            ),
        ]

        transaction.expire(case)
        assert (
            case.status,
            case.business_stage,
            case.official_procedure_stage,
            case.legal_status,
            case.lifecycle_verification_status,
            case.lifecycle_revision,
        ) == (
            "ACCEPTED",
            BusinessStage.PROSECUTION_MANAGEMENT.value,
            OfficialProcedureStage.ACCEPTED.value,
            LegalStatus.APPLICATION_PENDING.value,
            ConfirmationStatus.CONFIRMED.value,
            1,
        )
        Session.rollback(transaction)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("case_id", ""),
        ("case_id", "x" * 37),
        ("expected_current_evidence_version_id", " "),
        ("expected_current_evidence_version_id", "x" * 37),
        ("target_evidence_version_id", ""),
        ("target_evidence_version_id", "x" * 37),
        ("actor_id", " "),
        ("actor_id", "x" * 37),
        ("idempotency_key", ""),
        ("idempotency_key", "x" * 101),
        ("switched_at", datetime(2026, 7, 13, tzinfo=timezone.utc)),
    ],
)
def test_malformed_commands_fail_in_frozen_field_order(
    session_factory: sessionmaker[Session], field: str, value: object
) -> None:
    with session_factory() as transaction:
        error = _assert_error(
            "EVIDENCE_CURRENT_INVALID",
            400,
            lambda: switch_current_evidence_version(
                replace(_command(), **{field: value}),  # type: ignore[arg-type]
                transaction,
            ),
        )
        assert error.details == {"field": field}
        assert _activity_count(transaction) == 0


def test_exact_command_type_same_ids_and_non_datetime_are_rejected_first(
    session_factory: sessionmaker[Session],
) -> None:
    with session_factory() as transaction:
        error = _assert_error(
            "EVIDENCE_CURRENT_INVALID",
            400,
            lambda: switch_current_evidence_version(object(), transaction),  # type: ignore[arg-type]
        )
        assert error.details == {"field": "command"}

        error = _assert_error(
            "EVIDENCE_CURRENT_INVALID",
            400,
            lambda: switch_current_evidence_version(
                replace(_command(), switched_at="2026-07-13"),  # type: ignore[arg-type]
                transaction,
            ),
        )
        assert error.details == {"field": "switched_at"}

        error = _assert_error(
            "EVIDENCE_CURRENT_INVALID",
            400,
            lambda: switch_current_evidence_version(
                replace(_command(), target_evidence_version_id=_id(2)), transaction
            ),
        )
        assert error.details == {"field": "target_evidence_version_id"}


@pytest.mark.parametrize(
    ("missing", "code"),
    [
        ("case", "CASE_NOT_FOUND"),
        ("expected", "EXPECTED_EVIDENCE_VERSION_NOT_FOUND"),
        ("target", "TARGET_EVIDENCE_VERSION_NOT_FOUND"),
    ],
)
def test_lookup_order_uses_exact_not_found_codes(
    session_factory: sessionmaker[Session], missing: str, code: str
) -> None:
    with session_factory() as transaction:
        if missing != "case":
            _seed_case(transaction)
        if missing == "target":
            _seed_version(
                transaction,
                case_id=_id(1),
                version_id=_id(2),
                ordinal=1,
                is_current=True,
            )
        _assert_error(
            code,
            404,
            lambda: switch_current_evidence_version(_command(), transaction),
        )
        assert _activity_count(transaction) == 0


def test_case_lineage_projection_state_and_rejected_guards_are_fail_closed(
    session_factory: sessionmaker[Session],
) -> None:
    scenarios = (
        ("wrong_case", "EVIDENCE_CURRENT_CASE_MISMATCH", 400),
        ("wrong_lineage", "EVIDENCE_CURRENT_LINEAGE_MISMATCH", 409),
        ("bad_projection", "LIFECYCLE_PROJECTION_CONFLICT", 409),
        ("bad_verification", "LIFECYCLE_PROJECTION_CONFLICT", 409),
        ("bad_current_state", "EVIDENCE_CURRENT_STATE_CONFLICT", 409),
        ("bad_current_review", "EVIDENCE_CURRENT_STATE_CONFLICT", 409),
        ("bad_target_state", "EVIDENCE_CURRENT_STATE_CONFLICT", 409),
        ("bad_target_review", "EVIDENCE_CURRENT_STATE_CONFLICT", 409),
        ("rejected_target", "EVIDENCE_CURRENT_REJECTED", 409),
    )
    for index, (scenario, code, status) in enumerate(scenarios, start=1):
        case_id = _id(100 + index)
        current_id = _id(200 + index * 2)
        target_id = _id(201 + index * 2)
        with session_factory() as transaction:
            case, current, target = _seed_switch_fixture(
                transaction,
                case_id=case_id,
                current_id=current_id,
                target_id=target_id,
            )
            if scenario == "wrong_case":
                other_case = _seed_case(transaction, case_id=_id(500 + index))
                target.case_id = other_case.id
            elif scenario == "wrong_lineage":
                target.lineage_key = "oa-reply"
            elif scenario == "bad_projection":
                case.business_stage = "UNKNOWN_STAGE"
            elif scenario == "bad_verification":
                case.lifecycle_verification_status = "UNKNOWN_VERIFICATION"
            elif scenario == "bad_current_state":
                current.state = "UNKNOWN_STATE"
            elif scenario == "bad_current_review":
                current.review_state = "UNKNOWN_REVIEW"
            elif scenario == "bad_target_state":
                target.state = "UNKNOWN_STATE"
            elif scenario == "bad_target_review":
                target.review_state = "UNKNOWN_REVIEW"
            else:
                target.review_state = EvidenceReviewState.REJECTED.value
            transaction.flush()
            command = _command(
                case_id=case_id,
                current_id=current_id,
                target_id=target_id,
            )

            _assert_error(
                code,
                status,
                lambda command=command: switch_current_evidence_version(command, transaction),
            )
            assert _activity_count(transaction) == 0
            transaction.rollback()


def test_receipt_link_locks_only_a_final_current_parent(
    session_factory: sessionmaker[Session],
) -> None:
    with session_factory() as transaction:
        _case, current, target = _seed_switch_fixture(
            transaction,
            current_state=EvidenceVersionState.FINAL.value,
        )
        transaction.add(
            DocumentEvidenceDerivation(
                id=_id(20),
                case_id=_id(1),
                parent_evidence_version_id=current.id,
                child_evidence_version_id=target.id,
                derivation_type=EvidenceDerivationType.RECEIPT_LINK.value,
                actor_id=_id(901),
                derived_at=datetime(2026, 7, 13, 10),
                source_snapshot="{}",
            )
        )
        transaction.flush()
        _assert_error(
            "EVIDENCE_CURRENT_RECEIPT_LOCKED",
            409,
            lambda: switch_current_evidence_version(_command(), transaction),
        )
        assert current.current_identity_key == f"{_id(1)}|{LINEAGE_KEY}"
        assert target.current_identity_key is None
        assert _activity_count(transaction) == 0

    with session_factory() as transaction:
        _seed_switch_fixture(
            transaction,
            case_id=_id(30),
            current_id=_id(31),
            target_id=_id(32),
            current_state=EvidenceVersionState.FINAL.value,
        )
        result = switch_current_evidence_version(
            _command(case_id=_id(30), current_id=_id(31), target_id=_id(32)),
            transaction,
        )
        assert result.reused is False


@pytest.mark.parametrize(
    "review_state",
    [EvidenceReviewState.PENDING.value, EvidenceReviewState.APPROVED.value],
)
def test_pending_and_approved_targets_are_both_switchable(
    session_factory: sessionmaker[Session], review_state: str
) -> None:
    with session_factory() as transaction:
        _seed_switch_fixture(transaction, target_review_state=review_state)
        result = switch_current_evidence_version(_command(), transaction)
        assert result.current_evidence_version_id == _id(3)
        assert result.reused is False


@pytest.mark.parametrize(
    ("current_key", "target_key", "code"),
    [
        (None, None, "EVIDENCE_CURRENT_NOT_FOUND"),
        ("wrong-holder", None, "EVIDENCE_CURRENT_CONFLICT"),
        ("expected", "already-current", "EVIDENCE_CURRENT_CONFLICT"),
    ],
)
def test_current_identity_guards_are_exact(
    session_factory: sessionmaker[Session],
    current_key: str | None,
    target_key: str | None,
    code: str,
) -> None:
    with session_factory() as transaction:
        _case, current, target = _seed_switch_fixture(transaction)
        current.current_identity_key = (
            f"{_id(1)}|{LINEAGE_KEY}"
            if current_key == "expected"
            else None
            if current_key == "wrong-holder"
            else current_key
        )
        target.current_identity_key = target_key
        transaction.flush()
        if current_key == "wrong-holder":
            _seed_version(
                transaction,
                case_id=_id(1),
                version_id=_id(4),
                ordinal=3,
                is_current=True,
            )
        _assert_error(
            code,
            409,
            lambda: switch_current_evidence_version(_command(), transaction),
        )
        assert _activity_count(transaction) == 0


def test_stale_expected_current_fails_compare_and_swap_without_activity(
    session_factory: sessionmaker[Session],
) -> None:
    with session_factory() as setup:
        _seed_switch_fixture(setup)
        _seed_version(
            setup,
            case_id=_id(1),
            version_id=_id(4),
            ordinal=3,
        )
        setup.commit()

    with session_factory() as stale:
        stale_current = stale.get(DocumentEvidenceVersion, _id(2))
        assert stale_current is not None
        assert stale_current.current_identity_key == f"{_id(1)}|{LINEAGE_KEY}"
        with session_factory() as winner:
            switch_current_evidence_version(_command(), winner)
            winner.commit()

        _assert_error(
            "EVIDENCE_CURRENT_CONFLICT",
            409,
            lambda: switch_current_evidence_version(
                _command(target_id=_id(4), idempotency_key="stale-switch"), stale
            ),
        )
        assert _activity_count(stale) == 1


def test_exact_replay_remains_historical_after_later_switch_and_changed_fact_conflicts(
    session_factory: sessionmaker[Session],
) -> None:
    with session_factory() as transaction:
        _seed_switch_fixture(transaction)
        _seed_version(
            transaction,
            case_id=_id(1),
            version_id=_id(4),
            ordinal=3,
        )
        transaction.commit()

        first_command = _command()
        first = switch_current_evidence_version(first_command, transaction)
        transaction.commit()
        later = switch_current_evidence_version(
            _command(
                current_id=_id(3),
                target_id=_id(4),
                switched_at=datetime(2026, 7, 13, 11),
                idempotency_key="switch-2",
            ),
            transaction,
        )
        transaction.commit()

        replay = switch_current_evidence_version(first_command, transaction)
        assert replay == replace(first, reused=True)
        assert replay.activity_id != later.activity_id
        assert _activity_count(transaction) == 2
        assert transaction.get(DocumentEvidenceVersion, _id(4)).current_identity_key == (
            f"{_id(1)}|{LINEAGE_KEY}"
        )

        _assert_error(
            "LIFECYCLE_IDEMPOTENCY_CONFLICT",
            409,
            lambda: switch_current_evidence_version(
                replace(first_command, actor_id=_id(901)), transaction
            ),
        )
        assert _activity_count(transaction) == 2
        assert transaction.get(DocumentEvidenceVersion, _id(4)).current_identity_key == (
            f"{_id(1)}|{LINEAGE_KEY}"
        )


def test_replay_changed_nonexistent_version_retains_lookup_priority(
    session_factory: sessionmaker[Session],
) -> None:
    with session_factory() as transaction:
        _seed_switch_fixture(transaction)
        first_command = _command()
        switch_current_evidence_version(first_command, transaction)
        transaction.commit()

        _assert_error(
            "TARGET_EVIDENCE_VERSION_NOT_FOUND",
            404,
            lambda: switch_current_evidence_version(
                replace(first_command, target_evidence_version_id=_id(99)), transaction
            ),
        )
        assert _activity_count(transaction) == 1


def test_caller_rollback_removes_switch_activity_links_and_revision(
    session_factory: sessionmaker[Session],
) -> None:
    with session_factory() as transaction:
        _seed_switch_fixture(transaction)
        result = switch_current_evidence_version(_command(), transaction)
        assert _activity_count(transaction) == 1
        assert len(transaction.scalars(select(CaseActivityEventEvidence)).all()) == 2
        transaction.rollback()

    with session_factory() as verification:
        assert verification.get(DocumentEvidenceVersion, _id(2)).current_identity_key == (
            f"{_id(1)}|{LINEAGE_KEY}"
        )
        assert verification.get(DocumentEvidenceVersion, _id(3)).current_identity_key is None
        assert verification.get(Case, _id(1)).lifecycle_revision == 0
        assert verification.get(CaseActivityEvent, result.activity_id) is None
        assert verification.scalars(select(CaseActivityEventEvidence)).all() == []


def test_append_error_propagates_and_caller_rollback_restores_everything(
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    append_error = BusinessError("APPEND_FAILED", "append failed", status_code=409)
    with session_factory() as transaction:
        _seed_switch_fixture(transaction)
        monkeypatch.setattr(
            evidence_service,
            "append_case_activity",
            Mock(side_effect=append_error),
        )
        with pytest.raises(BusinessError) as exc_info:
            switch_current_evidence_version(_command(), transaction)
        assert exc_info.value is append_error
        transaction.rollback()

    with session_factory() as verification:
        assert verification.get(DocumentEvidenceVersion, _id(2)).current_identity_key == (
            f"{_id(1)}|{LINEAGE_KEY}"
        )
        assert verification.get(DocumentEvidenceVersion, _id(3)).current_identity_key is None
        assert verification.get(Case, _id(1)).lifecycle_revision == 0
        assert verification.scalars(select(CaseActivityEvent)).all() == []
        assert verification.scalars(select(CaseActivityEventEvidence)).all() == []
