from __future__ import annotations

import hashlib
import json
from dataclasses import fields
from decimal import Decimal
from inspect import signature
from typing import get_type_hints
from uuid import uuid4

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker
from test_v8_grant_notice_lifecycle_adapter import (
    _dispatch,
    _grant_fixture,
    _replacement_fixture,
)

from app.core.errors import BusinessError
from app.modules.cases.lifecycle_contracts import ActivityLane
from app.modules.cases.models import CaseActivityEvent
from app.modules.fees.models import (
    FeeDraft,
    FeeObligation,
    FeeObligationLine,
    T_GrantFeeTask,
)
from app.modules.fees.obligation_contracts import (
    FeeDifferenceReviewState,
    FeeDomain,
    FeeSourceStatus,
    RecognizeFeeObligationResult,
)


def test_grant_year_annuity_adapter_exposes_exact_frozen_public_interface() -> None:
    from app.modules.grant_fees import service

    command_type = service.RecognizeGrantYearAnnuityObligationCommand
    adapter = service.recognize_grant_year_annuity_obligation

    assert [field.name for field in fields(command_type)] == [
        "grant_fee_task_id",
        "source_activity_id",
        "actor_id",
        "idempotency_key",
    ]
    assert command_type.__dataclass_params__.frozen is True
    assert "__slots__" in command_type.__dict__
    assert tuple(signature(command_type).parameters) == (
        "grant_fee_task_id",
        "source_activity_id",
        "actor_id",
        "idempotency_key",
    )
    assert all(
        parameter.kind.name == "KEYWORD_ONLY"
        for parameter in signature(command_type).parameters.values()
    )
    assert list(get_type_hints(command_type).items()) == [
        ("grant_fee_task_id", str),
        ("source_activity_id", str),
        ("actor_id", str),
        ("idempotency_key", str),
    ]
    parameters = tuple(signature(adapter).parameters.values())
    hints = get_type_hints(adapter)
    assert [parameter.name for parameter in parameters] == ["command", "transaction"]
    assert hints == {
        "command": command_type,
        "transaction": Session,
        "return": RecognizeFeeObligationResult,
    }


@pytest.mark.parametrize(
    ("patent_category", "fee_code"),
    (
        ("INV", "CN_ANNUITY_FEE_INV"),
        ("UM", "CN_ANNUITY_FEE_UM"),
        ("DES", "CN_ANNUITY_FEE_DES"),
    ),
)
def test_recognizes_only_the_canonical_row74_snapshot_lines(
    session_factory: sessionmaker,
    monkeypatch: pytest.MonkeyPatch,
    patent_category: str,
    fee_code: str,
) -> None:
    from app.modules.grant_fees import service

    deep_commands: list[object] = []
    real_recognize = service.recognize_obligation

    def capture(command, transaction):
        deep_commands.append(command)
        return real_recognize(command, transaction)

    monkeypatch.setattr(service, "recognize_obligation", capture)

    with session_factory() as transaction:
        case, document, task, evidence = _grant_fixture(
            transaction,
            label=f"ANNUITY-{patent_category}",
        )
        case.patent_category = patent_category
        document.extra_data = (
            '{"GrantFeeLines":['
            '{"fee_name":"第二年年费","year":2,"amount":"1200.00",'
            '"reduction_ratio":"0.7"},'
            '{"fee_name":"第一年年费","year":1,"amount":"900.00",'
            '"reduction_ratio":"0"}]}'
        )
        transaction.flush()
        lifecycle = _dispatch(
            transaction,
            task=task,
            document=document,
            evidence=evidence,
            idempotency_key=f"annuity-source-{patent_category}",
        )
        transaction.flush()

        document.extra_data = "prohibited mutable source"
        task.gov_fee_amt = Decimal("999999.99")
        transaction.flush()
        result = service.recognize_grant_year_annuity_obligation(
            service.RecognizeGrantYearAnnuityObligationCommand(
                grant_fee_task_id=task.id,
                source_activity_id=lifecycle.activity_id,
                actor_id=str(uuid4()),
                idempotency_key=f"annuity-recognition-{patent_category}",
            ),
            transaction,
        )

        assert type(result) is RecognizeFeeObligationResult
        assert result.reused is False
        assert result.obligation.case_id == case.id
        assert result.obligation.fee_domain is FeeDomain.GOV
        assert result.obligation.obligation_type == "GRANT_YEAR_ANNUITY"
        assert result.obligation.due_date == task.due_date
        assert result.obligation.currency == "CNY"
        assert result.obligation.source.source_activity_id == lifecycle.activity_id
        assert result.obligation.source.source_document_id == document.id
        assert result.obligation.source.status is FeeSourceStatus.VERIFIED
        assert len(deep_commands) == 1
        assert [line.fee_year_key for line in deep_commands[0].lines] == [2, 1]
        projected = {line.fee_year_key: line for line in result.obligation.lines}
        assert list(projected) == [1, 2]
        assert set(projected) == {1, 2}
        assert projected[1].fee_code == fee_code
        assert projected[1].fee_name == "第一年年费"
        assert projected[1].payable_amount == Decimal("900.00")
        assert projected[1].source_amount == Decimal("900.00")
        assert projected[1].official_full_amount is None
        assert projected[1].reduction_ratio == Decimal("0")
        assert projected[1].source_date is None
        assert projected[1].difference_review_state is FeeDifferenceReviewState.REVIEW_REQUIRED
        assert projected[2].fee_code == fee_code
        assert projected[2].fee_name == "第二年年费"
        assert projected[2].payable_amount == Decimal("1200.00")
        assert projected[2].source_amount == Decimal("1200.00")
        assert projected[2].official_full_amount is None
        assert projected[2].reduction_ratio == Decimal("0.7")
        assert projected[2].source_date is None
        assert projected[2].difference_review_state is FeeDifferenceReviewState.REVIEW_REQUIRED
        assert transaction.scalar(select(func.count()).select_from(FeeObligation)) == 1
        assert transaction.scalar(select(func.count()).select_from(FeeObligationLine)) == 2
        assert transaction.scalar(select(func.count()).select_from(FeeDraft)) == 0
        assert (
            transaction.scalar(
                select(func.count())
                .select_from(CaseActivityEvent)
                .where(CaseActivityEvent.lane == ActivityLane.FEE.value)
            )
            == 1
        )


def _command(service, task, lifecycle, *, key: str, actor_id: str | None = None):
    return service.RecognizeGrantYearAnnuityObligationCommand(
        grant_fee_task_id=task.id,
        source_activity_id=lifecycle.activity_id,
        actor_id=actor_id or str(uuid4()),
        idempotency_key=key,
    )


def _canonical_json(value: object) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def _rewrite_snapshot(activity: CaseActivityEvent, mutate) -> None:
    payload = json.loads(activity.payload_json)
    snapshot = json.loads(payload["grant_fee_lines_snapshot"])
    mutate(snapshot)
    canonical = _canonical_json(snapshot)
    payload["grant_fee_lines_snapshot"] = canonical
    payload["grant_fee_lines_snapshot_hash"] = hashlib.sha256(canonical.encode()).hexdigest()
    activity.payload_json = _canonical_json(payload)


def _write_counts(transaction: Session) -> tuple[int, int, int, int]:
    return (
        transaction.scalar(select(func.count()).select_from(FeeObligation)) or 0,
        transaction.scalar(select(func.count()).select_from(FeeObligationLine)) or 0,
        transaction.scalar(select(func.count()).select_from(FeeDraft)) or 0,
        transaction.scalar(
            select(func.count())
            .select_from(CaseActivityEvent)
            .where(CaseActivityEvent.lane == ActivityLane.FEE.value)
        )
        or 0,
    )


@pytest.mark.parametrize(
    ("field", "invalid"),
    (
        ("grant_fee_task_id", ""),
        ("source_activity_id", " activity "),
        ("actor_id", "\x00"),
        ("idempotency_key", "x" * 129),
    ),
)
def test_command_shape_fails_before_queries(
    session_factory: sessionmaker,
    field: str,
    invalid: str,
) -> None:
    from app.modules.grant_fees import service

    values = {
        "grant_fee_task_id": "task-id",
        "source_activity_id": "activity-id",
        "actor_id": "actor-id",
        "idempotency_key": "recognize-id",
    }
    values[field] = invalid
    with session_factory() as transaction, pytest.raises(BusinessError) as caught:
        service.recognize_grant_year_annuity_obligation(
            service.RecognizeGrantYearAnnuityObligationCommand(**values),
            transaction,
        )
    assert caught.value.code == "GRANT_YEAR_ANNUITY_COMMAND_INVALID"
    assert caught.value.status_code == 400
    assert caught.value.details == {"field": field}


@pytest.mark.parametrize("category", (None, "", "inv", "PCT"))
def test_unsupported_patent_category_is_write_free(
    session_factory: sessionmaker,
    category: str | None,
) -> None:
    from app.modules.grant_fees import service

    with session_factory() as transaction:
        case, document, task, evidence = _grant_fixture(
            transaction,
            label=f"BAD-CATEGORY-{category}",
        )
        lifecycle = _dispatch(
            transaction,
            task=task,
            document=document,
            evidence=evidence,
            idempotency_key=f"bad-category-{category}",
        )
        before = _write_counts(transaction)
        case.patent_category = category
        if category is not None:
            transaction.flush()
        with pytest.raises(BusinessError) as caught:
            service.recognize_grant_year_annuity_obligation(
                _command(service, task, lifecycle, key=f"recognize-bad-{category}"),
                transaction,
            )
        assert caught.value.code == "GRANT_YEAR_ANNUITY_PATENT_CATEGORY_UNSUPPORTED"
        assert caught.value.status_code == 409
        with transaction.no_autoflush:
            assert _write_counts(transaction) == before


@pytest.mark.parametrize(
    "mutate",
    (
        lambda snapshot: snapshot.update(lines=[]),
        lambda snapshot: snapshot["lines"][0].update(fee_name=" "),
        lambda snapshot: snapshot["lines"][0].update(year=True),
        lambda snapshot: snapshot["lines"].append(dict(snapshot["lines"][0])),
        lambda snapshot: snapshot["lines"][0].update(amount=900),
        lambda snapshot: snapshot["lines"][0].update(amount="0"),
        lambda snapshot: snapshot["lines"][0].update(amount="1.001"),
        lambda snapshot: snapshot["lines"][0].update(reduction_ratio=0.7),
        lambda snapshot: snapshot["lines"][0].update(reduction_ratio="1"),
    ),
)
def test_every_invalid_frozen_line_shape_is_write_free(
    session_factory: sessionmaker,
    mutate,
) -> None:
    from app.modules.grant_fees import service

    with session_factory() as transaction:
        case, document, task, evidence = _grant_fixture(
            transaction,
            label=f"BAD-LINE-{uuid4().hex[:8]}",
        )
        lifecycle = _dispatch(
            transaction,
            task=task,
            document=document,
            evidence=evidence,
            idempotency_key=f"bad-line-{uuid4()}",
        )
        activity = transaction.get(CaseActivityEvent, lifecycle.activity_id)
        assert activity is not None
        _rewrite_snapshot(activity, mutate)
        transaction.flush()
        before = _write_counts(transaction)
        with pytest.raises(BusinessError) as caught:
            service.recognize_grant_year_annuity_obligation(
                _command(service, task, lifecycle, key=f"recognize-bad-line-{uuid4()}"),
                transaction,
            )
        assert caught.value.code == "GRANT_YEAR_ANNUITY_FEE_LINE_CONFLICT"
        assert caught.value.status_code == 409
        assert _write_counts(transaction) == before


@pytest.mark.parametrize(
    "corrupt",
    (
        "task-type",
        "activity-lane",
        "activity-status",
        "payload-due-date",
        "snapshot-hash",
        "evidence-hash",
    ),
)
def test_source_lineage_corruption_is_write_free(
    session_factory: sessionmaker,
    corrupt: str,
) -> None:
    from app.modules.grant_fees import service

    with session_factory() as transaction:
        case, document, task, evidence = _grant_fixture(
            transaction,
            label=f"BAD-SOURCE-{corrupt}",
        )
        lifecycle = _dispatch(
            transaction,
            task=task,
            document=document,
            evidence=evidence,
            idempotency_key=f"bad-source-{corrupt}",
        )
        activity = transaction.get(CaseActivityEvent, lifecycle.activity_id)
        assert activity is not None
        if corrupt == "task-type":
            task.type = "OTHER"
        elif corrupt == "activity-lane":
            activity.lane = ActivityLane.FEE.value
        elif corrupt == "activity-status":
            activity.confirmation_status = "PENDING"
        elif corrupt in {"payload-due-date", "snapshot-hash"}:
            payload = json.loads(activity.payload_json)
            if corrupt == "payload-due-date":
                payload["due_date"] = "2027-01-01"
            else:
                payload["grant_fee_lines_snapshot_hash"] = "0" * 64
            activity.payload_json = _canonical_json(payload)
        else:
            evidence.content_hash = f"sha256:{'b' * 64}"
        transaction.flush()
        before = _write_counts(transaction)
        with pytest.raises(BusinessError) as caught:
            service.recognize_grant_year_annuity_obligation(
                _command(service, task, lifecycle, key=f"recognize-bad-source-{corrupt}"),
                transaction,
            )
        assert caught.value.code == "GRANT_YEAR_ANNUITY_SOURCE_LINEAGE_CONFLICT"
        assert caught.value.status_code == 409
        assert _write_counts(transaction) == before


def test_exact_replay_and_both_idempotency_drift_paths_are_fail_closed(
    session_factory: sessionmaker,
) -> None:
    from app.modules.grant_fees import service

    with session_factory() as transaction:
        case, document, task, evidence = _grant_fixture(transaction, label="REPLAY")
        lifecycle = _dispatch(
            transaction,
            task=task,
            document=document,
            evidence=evidence,
            idempotency_key="annuity-replay-source",
        )
        actor_id = str(uuid4())
        command = _command(
            service,
            task,
            lifecycle,
            key="annuity-replay",
            actor_id=actor_id,
        )
        first = service.recognize_grant_year_annuity_obligation(command, transaction)
        counts = _write_counts(transaction)
        replay = service.recognize_grant_year_annuity_obligation(command, transaction)
        assert replay.reused is True
        assert replay.obligation.id == first.obligation.id
        assert replay.activity_id == first.activity_id
        assert _write_counts(transaction) == counts

        with pytest.raises(BusinessError):
            service.recognize_grant_year_annuity_obligation(
                _command(
                    service,
                    task,
                    lifecycle,
                    key="annuity-replay",
                    actor_id=str(uuid4()),
                ),
                transaction,
            )
        with pytest.raises(BusinessError):
            service.recognize_grant_year_annuity_obligation(
                _command(service, task, lifecycle, key="annuity-new-key"),
                transaction,
            )
        assert _write_counts(transaction) == counts


def test_direct_correction_supersedes_once_and_replays_exactly(
    session_factory: sessionmaker,
) -> None:
    from app.modules.grant_fees import service

    with session_factory() as transaction:
        case, first_document, first_task, first_evidence = _grant_fixture(
            transaction,
            label="CORRECTION",
        )
        first_lifecycle = _dispatch(
            transaction,
            task=first_task,
            document=first_document,
            evidence=first_evidence,
            idempotency_key="annuity-correction-source-1",
        )
        first = service.recognize_grant_year_annuity_obligation(
            _command(service, first_task, first_lifecycle, key="annuity-correction-1"),
            transaction,
        )
        second_document, second_task, second_evidence = _replacement_fixture(
            transaction,
            case=case,
            predecessor_task=first_task,
            label="ANNUITY",
        )
        second_lifecycle = _dispatch(
            transaction,
            task=second_task,
            document=second_document,
            evidence=second_evidence,
            idempotency_key="annuity-correction-source-2",
        )
        command = _command(
            service,
            second_task,
            second_lifecycle,
            key="annuity-correction-2",
        )
        second = service.recognize_grant_year_annuity_obligation(command, transaction)
        assert second.superseded_obligation_id == first.obligation.id
        assert second.obligation.supersedes_obligation_id == first.obligation.id
        assert second.obligation.supersede_reason == "GRANT_REGISTRATION_NOTICE_CORRECTION"
        counts = _write_counts(transaction)
        replay = service.recognize_grant_year_annuity_obligation(command, transaction)
        assert replay.reused is True
        assert replay.obligation.id == second.obligation.id
        assert _write_counts(transaction) == counts


def test_caller_rollback_removes_recognition_without_committing(
    session_factory: sessionmaker,
) -> None:
    from app.modules.grant_fees import service

    with session_factory() as setup:
        case, document, task, evidence = _grant_fixture(setup, label="ROLLBACK")
        lifecycle = _dispatch(
            setup,
            task=task,
            document=document,
            evidence=evidence,
            idempotency_key="annuity-rollback-source",
        )
        case_id = case.id
        task_id = task.id
        activity_id = lifecycle.activity_id
        setup.commit()

    with session_factory() as transaction:
        task = transaction.get(T_GrantFeeTask, task_id)
        assert task is not None
        lifecycle = type("Lifecycle", (), {"activity_id": activity_id})()
        service.recognize_grant_year_annuity_obligation(
            _command(service, task, lifecycle, key="annuity-rollback"),
            transaction,
        )
        assert _write_counts(transaction)[0] == 1
        transaction.rollback()

    with session_factory() as transaction:
        assert (
            transaction.scalar(
                select(func.count())
                .select_from(FeeObligation)
                .where(FeeObligation.case_id == case_id)
            )
            == 0
        )
