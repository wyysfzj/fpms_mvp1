from __future__ import annotations

import inspect
import json
from dataclasses import FrozenInstanceError, fields, is_dataclass, replace
from datetime import date, datetime, timezone
from decimal import Decimal
from hashlib import sha256
from typing import get_type_hints

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from app.core.errors import BusinessError
from app.modules.cases.models import Case
from app.modules.documents.evidence_contracts import EvidenceReviewState, EvidenceVersionState
from app.modules.documents.models import DocAttachment, Document, DocumentEvidenceVersion
from app.modules.fees.fee_reduction import FeeReductionApprovalScopeType
from app.modules.fees.fee_reduction_approval_service import (
    FeeReductionApprovalRecordDisposition,
    RecordFeeReductionApprovalCommand,
    RecordFeeReductionApprovalResult,
    record_fee_reduction_approval,
)
from app.modules.fees.models import FeeReductionApproval

CONFIRMED_AT = datetime(2026, 7, 14, 9, 30)
EFFECTIVE_FROM = date(2026, 7, 1)
CONTENT_HASH = "sha256:" + "a" * 64


def _id(value: int) -> str:
    return f"00000000-0000-0000-0000-{value:012d}"


def _canonical(value: object) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def _digest(value: str) -> str:
    return sha256(value.encode("utf-8")).hexdigest()


def _seed_case_and_evidence(
    transaction: Session,
    *,
    case_id: str = _id(1),
    evidence_id: str = _id(2),
    state: str = EvidenceVersionState.FINAL.value,
    review_state: str = EvidenceReviewState.APPROVED.value,
    current: bool = True,
    content_hash: str = CONTENT_HASH,
) -> DocumentEvidenceVersion:
    transaction.add(Case(id=case_id, case_no=f"CASE-{case_id[-12:]}"))
    document_id = _id(int(evidence_id[-12:]) + 1000)
    attachment_id = _id(int(evidence_id[-12:]) + 2000)
    transaction.add(Document(id=document_id, case_id=case_id))
    transaction.flush()
    transaction.add(
        DocAttachment(
            id=attachment_id,
            document_id=document_id,
            file_name="fee-reduction.pdf",
            file_path="/evidence/fee-reduction.pdf",
        )
    )
    transaction.flush()
    version = DocumentEvidenceVersion(
        id=evidence_id,
        case_id=case_id,
        document_id=document_id,
        attachment_id=attachment_id,
        lineage_key="fee-reduction",
        role="OFFICIAL_NOTICE",
        version_number=1,
        state=state,
        creator_id=_id(700),
        review_state=review_state,
        reviewer_id=_id(701) if review_state == EvidenceReviewState.APPROVED.value else None,
        reviewed_at=CONFIRMED_AT if review_state == EvidenceReviewState.APPROVED.value else None,
        final_submitted_at=CONFIRMED_AT,
        content_hash=content_hash,
        current_identity_key=f"{case_id}|fee-reduction" if current else None,
    )
    transaction.add(version)
    transaction.commit()
    return version


def _command(**changes: object) -> RecordFeeReductionApprovalCommand:
    values: dict[str, object] = {
        "case_id": _id(1),
        "scope_type": FeeReductionApprovalScopeType.CASE,
        "applicant_ids": (_id(10),),
        "eligibility_attributes_version": "customer-confirmation-v1",
        "eligibility_attributes_json": _canonical({_id(10): {"kind": "个人", "收入": 1}}),
        "reduction_ratio": Decimal("0.85"),
        "fee_codes": ("APPLICATION", "ANNUITY"),
        "fee_year_from": 1,
        "fee_year_to": 3,
        "effective_from": EFFECTIVE_FROM,
        "effective_to": date(2027, 6, 30),
        "source_evidence_version_id": _id(2),
        "expected_source_content_hash": CONTENT_HASH,
        "confirmed_at": CONFIRMED_AT,
        "confirmed_by": _id(900),
    }
    values.update(changes)
    return RecordFeeReductionApprovalCommand(**values)  # type: ignore[arg-type]


def _rows(transaction: Session) -> list[FeeReductionApproval]:
    return list(transaction.scalars(select(FeeReductionApproval).order_by(FeeReductionApproval.id)))


def _assert_error(
    transaction: Session,
    command: object,
    *,
    code: str,
    status: int,
    field: str | None = None,
) -> BusinessError:
    before = [(row.id, row.updated_at) for row in _rows(transaction)]
    with pytest.raises(BusinessError) as caught:
        record_fee_reduction_approval(command, transaction)  # type: ignore[arg-type]
    error = caught.value
    assert (error.code, error.status_code) == (code, status)
    if field is not None:
        assert error.details == {"field": field}
    assert [(row.id, row.updated_at) for row in _rows(transaction)] == before
    assert transaction.in_transaction()
    return error


def test_public_contract_is_exact_frozen_slotted_keyword_only_and_synchronous() -> None:
    assert tuple(
        (member.name, member.value) for member in FeeReductionApprovalRecordDisposition
    ) == (("CREATED", "CREATED"), ("REUSED", "REUSED"))
    assert issubclass(FeeReductionApprovalRecordDisposition, str)

    expected_command = (
        ("case_id", str),
        ("scope_type", FeeReductionApprovalScopeType),
        ("applicant_ids", tuple[str, ...]),
        ("eligibility_attributes_version", str),
        ("eligibility_attributes_json", str),
        ("reduction_ratio", Decimal),
        ("fee_codes", tuple[str, ...]),
        ("fee_year_from", int | None),
        ("fee_year_to", int | None),
        ("effective_from", date),
        ("effective_to", date | None),
        ("source_evidence_version_id", str),
        ("expected_source_content_hash", str),
        ("confirmed_at", datetime),
        ("confirmed_by", str),
    )
    expected_result = (
        ("approval_id", str),
        ("scope_type", FeeReductionApprovalScopeType),
        ("case_id", str | None),
        ("applicant_set_key", str | None),
        ("reduction_ratio", Decimal),
        ("fee_codes", tuple[str, ...]),
        ("fee_scope_snapshot", str),
        ("fee_scope_hash", str),
        ("fee_year_from", int | None),
        ("fee_year_to", int | None),
        ("effective_from", date),
        ("effective_to", date | None),
        ("source_evidence_version_id", str),
        ("confirmation_status", str),
        ("confirmed_at", datetime),
        ("confirmed_by", str),
        ("eligibility_snapshot", str),
        ("eligibility_snapshot_hash", str),
        ("approval_identity_key", str),
        ("disposition", FeeReductionApprovalRecordDisposition),
    )
    for data_type, expected in (
        (RecordFeeReductionApprovalCommand, expected_command),
        (RecordFeeReductionApprovalResult, expected_result),
    ):
        assert is_dataclass(data_type)
        assert data_type.__dataclass_params__.frozen is True
        hints = get_type_hints(data_type)
        assert tuple((field.name, hints[field.name]) for field in fields(data_type)) == expected
        assert all(field.kw_only for field in fields(data_type))
        assert "__slots__" in data_type.__dict__
        with pytest.raises(FrozenInstanceError):
            _command().case_id = _id(99)

    signature = inspect.signature(record_fee_reduction_approval)
    assert tuple(signature.parameters) == ("command", "transaction")
    assert all(
        parameter.kind is inspect.Parameter.POSITIONAL_OR_KEYWORD
        for parameter in signature.parameters.values()
    )
    hints = get_type_hints(record_fee_reduction_approval)
    assert hints == {
        "command": RecordFeeReductionApprovalCommand,
        "transaction": Session,
        "return": RecordFeeReductionApprovalResult,
    }


@pytest.mark.parametrize(
    ("scope_type", "applicant_ids", "ratio"),
    (
        (FeeReductionApprovalScopeType.CASE, (_id(10),), Decimal("0.85")),
        (
            FeeReductionApprovalScopeType.APPLICANT_SET,
            (_id(11), _id(10)),
            Decimal("0.70"),
        ),
    ),
)
def test_creation_persists_exact_service_owned_facts_and_keeps_outer_transaction_open(
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
    scope_type: FeeReductionApprovalScopeType,
    applicant_ids: tuple[str, ...],
    ratio: Decimal,
) -> None:
    attributes = {applicant_id: {"label": applicant_id[-2:]} for applicant_id in applicant_ids}
    command = _command(
        scope_type=scope_type,
        applicant_ids=applicant_ids,
        reduction_ratio=ratio,
        eligibility_attributes_json=_canonical(attributes),
        fee_codes=("ANNUITY", "APPLICATION"),
    )
    with session_factory() as transaction:
        _seed_case_and_evidence(transaction)
        commit = transaction.commit
        rollback = transaction.rollback
        close = transaction.close
        monkeypatch.setattr(transaction, "commit", lambda: pytest.fail("outer commit called"))
        monkeypatch.setattr(transaction, "rollback", lambda: pytest.fail("outer rollback called"))
        monkeypatch.setattr(transaction, "close", lambda: pytest.fail("outer close called"))
        result = record_fee_reduction_approval(command, transaction)

        expected_fee_snapshot = _canonical(
            {
                "fee_codes": ["ANNUITY", "APPLICATION"],
                "schema": "FPMS_FEE_REDUCTION_FEE_SCOPE_V1",
            }
        )
        expected_eligibility = _canonical(
            {
                "applicants": [
                    {"applicant_id": applicant_id, "attributes": attributes[applicant_id]}
                    for applicant_id in sorted(applicant_ids)
                ],
                "attributes_version": "customer-confirmation-v1",
                "schema": "FPMS_FEE_REDUCTION_ELIGIBILITY_V1",
            }
        )
        expected_eligibility_hash = _digest(expected_eligibility)
        expected_set_key = (
            _digest(
                _canonical(
                    {
                        "applicant_ids": sorted(applicant_ids),
                        "eligibility_snapshot_hash": expected_eligibility_hash,
                        "schema": "FPMS_FEE_REDUCTION_APPLICANT_SET_V1",
                    }
                )
            )
            if scope_type is FeeReductionApprovalScopeType.APPLICANT_SET
            else None
        )
        scope_id = (
            command.case_id
            if scope_type is FeeReductionApprovalScopeType.CASE
            else expected_set_key
        )
        expected_identity = _digest(
            _canonical(
                {
                    "effective_from": "2026-07-01",
                    "effective_to": "2027-06-30",
                    "fee_scope_hash": _digest(expected_fee_snapshot),
                    "fee_year_from": 1,
                    "fee_year_to": 3,
                    "reduction_ratio": f"{ratio:.4f}",
                    "schema": "FPMS_FEE_REDUCTION_APPROVAL_IDENTITY_V1",
                    "scope_id": scope_id,
                    "scope_type": scope_type.value,
                    "source_evidence_version_id": command.source_evidence_version_id,
                }
            )
        )
        assert result.disposition is FeeReductionApprovalRecordDisposition.CREATED
        assert result.scope_type is scope_type
        assert result.case_id == (
            command.case_id if scope_type is FeeReductionApprovalScopeType.CASE else None
        )
        assert result.applicant_set_key == expected_set_key
        assert result.reduction_ratio == ratio.quantize(Decimal("0.0001"))
        assert result.fee_codes == ("ANNUITY", "APPLICATION")
        assert result.fee_scope_snapshot == expected_fee_snapshot
        assert result.fee_scope_hash == _digest(expected_fee_snapshot)
        assert result.eligibility_snapshot == expected_eligibility
        assert result.eligibility_snapshot_hash == expected_eligibility_hash
        assert result.approval_identity_key == expected_identity
        assert result.confirmation_status == "CONFIRMED"
        assert transaction.in_transaction()
        row = transaction.get(FeeReductionApproval, result.approval_id)
        assert row is not None
        assert (row.created_by, row.updated_by) == (command.confirmed_by, command.confirmed_by)
        assert row.confirmed_at == command.confirmed_at
        monkeypatch.setattr(transaction, "commit", commit)
        monkeypatch.setattr(transaction, "rollback", rollback)
        monkeypatch.setattr(transaction, "close", close)
        transaction.rollback()


@pytest.mark.parametrize(
    ("changes", "field"),
    (
        ({"case_id": " "}, "case_id"),
        ({"case_id": "x" * 37}, "case_id"),
        ({"scope_type": "CASE"}, "scope_type"),
        ({"applicant_ids": [_id(10)]}, "applicant_ids"),
        ({"applicant_ids": (_id(10), _id(10))}, "applicant_ids"),
        ({"applicant_ids": ()}, "applicant_ids"),
        ({"eligibility_attributes_version": " v1"}, "eligibility_attributes_version"),
        ({"eligibility_attributes_json": "{}"}, "eligibility_attributes_json"),
        ({"eligibility_attributes_json": '{"a":{},"a":{}}'}, "eligibility_attributes_json"),
        (
            {"eligibility_attributes_json": '{"%s":{"nested":{"a":1,"a":2}}}' % _id(10)},
            "eligibility_attributes_json",
        ),
        (
            {"eligibility_attributes_json": '{"%s":{"n":NaN}}' % _id(10)},
            "eligibility_attributes_json",
        ),
        (
            {"eligibility_attributes_json": '{"%s":{"text":"\\ud800"}}' % _id(10)},
            "eligibility_attributes_json",
        ),
        ({"eligibility_attributes_json": "[]"}, "eligibility_attributes_json"),
        ({"reduction_ratio": "0.85"}, "reduction_ratio"),
        ({"reduction_ratio": 0.85}, "reduction_ratio"),
        ({"reduction_ratio": Decimal("NaN")}, "reduction_ratio"),
        ({"reduction_ratio": Decimal("0.5")}, "reduction_ratio"),
        ({"fee_codes": []}, "fee_codes"),
        ({"fee_codes": ()}, "fee_codes"),
        ({"fee_codes": ("ANNUITY", "ANNUITY")}, "fee_codes"),
        ({"fee_codes": ("ANNUITY ",)}, "fee_codes"),
        ({"fee_year_from": 1, "fee_year_to": None}, "fee_year_to"),
        ({"fee_year_from": None, "fee_year_to": 1}, "fee_year_from"),
        ({"fee_year_from": True, "fee_year_to": 1}, "fee_year_from"),
        ({"fee_year_from": 0, "fee_year_to": 1}, "fee_year_from"),
        ({"fee_year_from": 3, "fee_year_to": 2}, "fee_year_to"),
        ({"effective_from": datetime(2026, 7, 1)}, "effective_from"),
        ({"effective_to": datetime(2026, 7, 1)}, "effective_to"),
        ({"effective_to": date(2026, 6, 30)}, "effective_to"),
        ({"source_evidence_version_id": " evidence"}, "source_evidence_version_id"),
        ({"expected_source_content_hash": "hash\x00bad"}, "expected_source_content_hash"),
        ({"confirmed_at": datetime(2026, 7, 14, tzinfo=timezone.utc)}, "confirmed_at"),
        ({"confirmed_by": "actor "}, "confirmed_by"),
    ),
)
def test_invalid_inputs_are_write_free(
    session_factory: sessionmaker[Session], changes: dict[str, object], field: str
) -> None:
    with session_factory() as transaction:
        _seed_case_and_evidence(transaction)
        _assert_error(
            transaction,
            replace(_command(), **changes),
            code="FEE_REDUCTION_APPROVAL_INVALID",
            status=400,
            field=field,
        )


def test_ratio_zero_fails_before_any_query_or_write(
    session_factory: sessionmaker[Session], monkeypatch: pytest.MonkeyPatch
) -> None:
    with session_factory() as transaction:
        command = _command(reduction_ratio=Decimal("0"))
        monkeypatch.setattr(
            transaction,
            "execute",
            lambda *_args, **_kwargs: pytest.fail("ratio zero queried the database"),
        )
        monkeypatch.setattr(
            transaction,
            "get",
            lambda *_args, **_kwargs: pytest.fail("ratio zero queried the database"),
        )
        error = _assert_error(
            transaction,
            command,
            code="FEE_REDUCTION_APPROVAL_NOT_REQUIRED",
            status=400,
        )
        assert error.details == {"field": "reduction_ratio"}


@pytest.mark.parametrize(
    ("ratio", "applicant_ids", "field"),
    (
        (Decimal("0.85"), (_id(10), _id(11)), "applicant_ids"),
        (Decimal("0.7"), (_id(10),), "applicant_ids"),
    ),
)
def test_ratio_applicant_count_rules_are_strict(
    session_factory: sessionmaker[Session],
    ratio: Decimal,
    applicant_ids: tuple[str, ...],
    field: str,
) -> None:
    attributes = {applicant_id: {} for applicant_id in applicant_ids}
    with session_factory() as transaction:
        _seed_case_and_evidence(transaction)
        _assert_error(
            transaction,
            _command(
                reduction_ratio=ratio,
                applicant_ids=applicant_ids,
                eligibility_attributes_json=_canonical(attributes),
            ),
            code="FEE_REDUCTION_APPROVAL_INVALID",
            status=400,
            field=field,
        )


@pytest.mark.parametrize(
    ("seed", "command_changes", "code", "status"),
    (
        (None, {"case_id": _id(99)}, "CASE_NOT_FOUND", 404),
        ("normal", {"source_evidence_version_id": _id(99)}, "EVIDENCE_VERSION_NOT_FOUND", 404),
        ("other_case", {}, "FEE_REDUCTION_APPROVAL_CONFLICT", 409),
        ("draft", {}, "FEE_REDUCTION_APPROVAL_CONFLICT", 409),
        ("pending", {}, "FEE_REDUCTION_APPROVAL_CONFLICT", 409),
        ("not_current", {}, "FEE_REDUCTION_APPROVAL_CONFLICT", 409),
        ("malformed_current", {}, "FEE_REDUCTION_APPROVAL_CONFLICT", 409),
        (
            "normal",
            {"expected_source_content_hash": "wrong"},
            "FEE_REDUCTION_APPROVAL_CONFLICT",
            409,
        ),
    ),
)
def test_creation_requires_exact_case_final_approved_current_evidence_and_hash(
    session_factory: sessionmaker[Session],
    seed: str | None,
    command_changes: dict[str, object],
    code: str,
    status: int,
) -> None:
    with session_factory() as transaction:
        if seed == "normal":
            _seed_case_and_evidence(transaction)
        elif seed == "other_case":
            _seed_case_and_evidence(transaction, case_id=_id(3))
            transaction.add(Case(id=_id(1), case_no="CASE-TARGET"))
            transaction.commit()
        elif seed == "draft":
            _seed_case_and_evidence(transaction, state=EvidenceVersionState.DRAFT.value)
        elif seed == "pending":
            _seed_case_and_evidence(transaction, review_state=EvidenceReviewState.PENDING.value)
        elif seed == "not_current":
            _seed_case_and_evidence(transaction, current=False)
        elif seed == "malformed_current":
            version = _seed_case_and_evidence(transaction)
            version.lineage_key = " fee-reduction"
            version.current_identity_key = f"{version.case_id}| fee-reduction"
            transaction.commit()
        _assert_error(
            transaction,
            _command(**command_changes),
            code=code,
            status=status,
        )


@pytest.mark.parametrize(
    "evidence_changes",
    (
        {"reviewer_id": None},
        {"reviewer_id": " reviewer"},
        {"reviewer_id": "reviewer\x00bad"},
        {"reviewer_id": "\ud800"},
        {"reviewer_id": _id(700)},
        {"reviewed_at": None},
        {"reviewed_at": datetime(2026, 7, 14, tzinfo=timezone.utc)},
    ),
)
def test_approved_evidence_requires_a_consistent_independent_review_carrier(
    session_factory: sessionmaker[Session],
    evidence_changes: dict[str, object],
) -> None:
    with session_factory() as transaction:
        version = _seed_case_and_evidence(transaction)
        for field, value in evidence_changes.items():
            setattr(version, field, value)
        _assert_error(
            transaction,
            _command(),
            code="FEE_REDUCTION_APPROVAL_CONFLICT",
            status=409,
        )


@pytest.mark.parametrize(
    ("changes", "field"),
    (
        ({"case_id": "\ud800"}, "case_id"),
        (
            {
                "applicant_ids": ("\ud800",),
                "eligibility_attributes_json": '{"\\ud800":{}}',
            },
            "applicant_ids",
        ),
        ({"eligibility_attributes_version": "\ud800"}, "eligibility_attributes_version"),
        ({"fee_codes": ("\ud800",)}, "fee_codes"),
        ({"source_evidence_version_id": "\ud800"}, "source_evidence_version_id"),
        ({"expected_source_content_hash": "\ud800"}, "expected_source_content_hash"),
        ({"confirmed_by": "\ud800"}, "confirmed_by"),
    ),
)
def test_required_canonical_string_contributors_reject_lone_surrogates(
    session_factory: sessionmaker[Session],
    changes: dict[str, object],
    field: str,
) -> None:
    with session_factory() as transaction:
        _seed_case_and_evidence(transaction)
        _assert_error(
            transaction,
            replace(_command(), **changes),
            code="FEE_REDUCTION_APPROVAL_INVALID",
            status=400,
            field=field,
        )


def test_exact_replay_reuses_immutable_history_after_evidence_supersession_and_conflicts_on_changed_projection(
    session_factory: sessionmaker[Session],
) -> None:
    with session_factory() as transaction:
        version = _seed_case_and_evidence(transaction)
        command = _command()
        created = record_fee_reduction_approval(command, transaction)
        transaction.commit()
        row = transaction.get(FeeReductionApproval, created.approval_id)
        assert row is not None
        timestamps = (row.created_at, row.updated_at)

        version.current_identity_key = None
        transaction.commit()
        reused = record_fee_reduction_approval(command, transaction)
        assert reused.approval_id == created.approval_id
        assert reused.disposition is FeeReductionApprovalRecordDisposition.REUSED
        assert (row.created_at, row.updated_at) == timestamps
        assert len(_rows(transaction)) == 1

        _assert_error(
            transaction,
            replace(command, confirmed_by=_id(901)),
            code="FEE_REDUCTION_APPROVAL_CONFLICT",
            status=409,
        )


def test_distinct_overlapping_approvals_are_retained_without_current_or_supersede_behavior(
    session_factory: sessionmaker[Session],
) -> None:
    with session_factory() as transaction:
        _seed_case_and_evidence(transaction)
        first = record_fee_reduction_approval(_command(), transaction)
        second = record_fee_reduction_approval(
            _command(
                effective_from=date(2026, 8, 1),
                effective_to=date(2027, 8, 1),
            ),
            transaction,
        )
        assert first.approval_id != second.approval_id
        assert len(_rows(transaction)) == 2
        assert not hasattr(FeeReductionApproval, "is_current")
        assert not hasattr(FeeReductionApproval, "supersedes_approval_id")


@pytest.mark.parametrize("winner_mode", ("exact", "conflicting", "absent"))
def test_unique_identity_race_uses_one_savepoint_and_reuses_only_exact_winner(
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
    winner_mode: str,
) -> None:
    import app.modules.fees.fee_reduction_approval_service as service

    with session_factory() as transaction:
        _seed_case_and_evidence(transaction)
        command = _command()
        expected = record_fee_reduction_approval(command, transaction)
        seeded_row = transaction.get(FeeReductionApproval, expected.approval_id)
        assert seeded_row is not None
        transaction.delete(seeded_row)
        transaction.commit()
        winner = FeeReductionApproval(
            id=_id(500),
            scope_type=expected.scope_type.value,
            case_id=expected.case_id,
            applicant_set_key=expected.applicant_set_key,
            reduction_ratio=expected.reduction_ratio,
            fee_scope_snapshot=expected.fee_scope_snapshot,
            fee_scope_hash=expected.fee_scope_hash,
            fee_year_from=expected.fee_year_from,
            fee_year_to=expected.fee_year_to,
            effective_from=expected.effective_from,
            effective_to=expected.effective_to,
            source_evidence_version_id=expected.source_evidence_version_id,
            confirmation_status="CONFIRMED",
            confirmed_at=expected.confirmed_at,
            confirmed_by=expected.confirmed_by,
            eligibility_snapshot=expected.eligibility_snapshot,
            eligibility_snapshot_hash=expected.eligibility_snapshot_hash,
            approval_identity_key=expected.approval_identity_key,
            created_by=expected.confirmed_by,
            updated_by=expected.confirmed_by,
        )
        if winner_mode == "conflicting":
            winner.confirmed_by = _id(999)

        query_calls = 0

        def identity_rows(_transaction: Session, _identity: str) -> list[FeeReductionApproval]:
            nonlocal query_calls
            query_calls += 1
            if query_calls == 1 or winner_mode == "absent":
                return []
            return [winner]

        flush_calls = 0

        def flush(*_args: object, **_kwargs: object) -> None:
            nonlocal flush_calls
            flush_calls += 1
            if flush_calls == 2:
                raise IntegrityError("simulated unique race", {}, Exception())
            original_flush(*_args, **_kwargs)

        monkeypatch.setattr(service, "_identity_rows", identity_rows)
        original_begin_nested = transaction.begin_nested
        savepoint_calls = 0

        def begin_nested():
            nonlocal savepoint_calls
            savepoint_calls += 1
            return original_begin_nested()

        monkeypatch.setattr(transaction, "begin_nested", begin_nested)
        original_flush = transaction.flush
        monkeypatch.setattr(transaction, "flush", flush)
        commit = transaction.commit
        rollback = transaction.rollback
        close = transaction.close
        monkeypatch.setattr(transaction, "commit", lambda: pytest.fail("outer commit called"))
        monkeypatch.setattr(transaction, "rollback", lambda: pytest.fail("outer rollback called"))
        monkeypatch.setattr(transaction, "close", lambda: pytest.fail("outer close called"))

        if winner_mode == "exact":
            result = record_fee_reduction_approval(command, transaction)
            assert result.approval_id == winner.id
            assert result.disposition is FeeReductionApprovalRecordDisposition.REUSED
        else:
            _assert_error(
                transaction,
                command,
                code="FEE_REDUCTION_APPROVAL_CONFLICT",
                status=409,
            )
        assert query_calls == 2
        assert savepoint_calls == 1
        assert flush_calls == 2
        monkeypatch.setattr(transaction, "commit", commit)
        monkeypatch.setattr(transaction, "rollback", rollback)
        monkeypatch.setattr(transaction, "close", close)
