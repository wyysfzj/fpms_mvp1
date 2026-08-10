from __future__ import annotations

import inspect
import json
from dataclasses import fields, is_dataclass, replace
from datetime import datetime
from decimal import Decimal
from types import SimpleNamespace
from typing import get_type_hints
from uuid import uuid4

import pytest
from pydantic import TypeAdapter, ValidationError
from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.sql.dml import Update
from test_v8_grant_notice_lifecycle_adapter import _dispatch, _grant_fixture

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
from app.modules.cases.models import Case, CaseActivityEvent, CaseActivityEventEvidence
from app.modules.fees.models import FeeObligationLine
from app.modules.fees.obligation_service import get_fee_obligation
from app.modules.grant_fees import api as grant_fee_api
from app.modules.grant_fees import schemas as grant_fee_schemas
from app.modules.grant_fees import service as grant_fee_service


def _seed(transaction: Session, *, label: str, line_count: int = 1):
    case, document, task, evidence = _grant_fixture(transaction, label=label)
    if line_count == 2:
        extra_data = json.loads(document.extra_data)
        extra_data["GrantFeeLines"].append(
            {
                "fee_name": "授权次年年费",
                "year": 2,
                "amount": "1200.00",
                "reduction_ratio": "0.85",
            }
        )
        document.extra_data = json.dumps(extra_data, ensure_ascii=False)
    source = _dispatch(
        transaction,
        task=task,
        document=document,
        evidence=evidence,
        idempotency_key=f"manual-review-source:{label}:{uuid4()}",
    )
    recognized = grant_fee_service.recognize_grant_year_annuity_obligation(
        grant_fee_service.RecognizeGrantYearAnnuityObligationCommand(
            grant_fee_task_id=task.id,
            source_activity_id=source.activity_id,
            actor_id=str(uuid4()),
            idempotency_key=f"manual-review-obligation:{label}:{uuid4()}",
        ),
        transaction,
    )
    transaction.commit()
    line = transaction.scalar(
        select(FeeObligationLine).where(
            FeeObligationLine.obligation_id == recognized.obligation.id
        )
    )
    assert line is not None
    return case, document, task, evidence, source, recognized.obligation, line


def _command(seed, **changes: object):
    case, _document, task, evidence, source, obligation, line = seed
    values: dict[str, object] = {
        "grant_fee_task_id": task.id,
        "source_activity_id": source.activity_id,
        "obligation_id": obligation.id,
        "reviewed_evidence_version_id": evidence.id,
        "expected_content_hash": evidence.content_hash,
        "confirmed_at": datetime(2026, 8, 10, 11, 30),
        "actor_id": "grant-fee-reviewer",
        "idempotency_key": "grant-official-fee-review:one",
        "lines": (
            grant_fee_service.GrantOfficialFeeReviewLineInput(
                obligation_line_id=line.id,
                official_full_amount=Decimal("1111.00"),
                confirmed_payable_amount=line.payable_amount,
            ),
        ),
    }
    values.update(changes)
    assert case.id == obligation.case_id
    return grant_fee_service.ConfirmGrantOfficialFeesCommand(**values)


def _review_activities(transaction: Session) -> tuple[CaseActivityEvent, ...]:
    return tuple(
        transaction.scalars(
            select(CaseActivityEvent).where(
                CaseActivityEvent.activity_type
                == "GRANT_YEAR_OFFICIAL_FEE_REVIEW_CONFIRMED"
            )
        )
    )


def _expect(code: str, status: int, action) -> BusinessError:
    with pytest.raises(BusinessError) as caught:
        action()
    assert caught.value.code == code
    assert caught.value.status_code == status
    return caught.value


def test_public_contract_and_http_models_are_exact() -> None:
    line_type = grant_fee_service.GrantOfficialFeeReviewLineInput
    command_type = grant_fee_service.ConfirmGrantOfficialFeesCommand
    result_type = grant_fee_service.ConfirmGrantOfficialFeesResult
    assert all(is_dataclass(value) for value in (line_type, command_type, result_type))
    assert all(value.__dataclass_params__.frozen for value in (line_type, command_type, result_type))
    assert tuple(field.name for field in fields(command_type)) == (
        "grant_fee_task_id",
        "source_activity_id",
        "obligation_id",
        "reviewed_evidence_version_id",
        "expected_content_hash",
        "confirmed_at",
        "actor_id",
        "idempotency_key",
        "lines",
    )
    assert all(
        parameter.kind is inspect.Parameter.KEYWORD_ONLY
        for parameter in inspect.signature(command_type).parameters.values()
    )
    assert get_type_hints(grant_fee_service.confirm_grant_official_fees) == {
        "command": command_type,
        "transaction": Session,
        "return": result_type,
    }
    assert grant_fee_schemas.GrantOfficialFeeReviewIn.model_config["extra"] == "forbid"
    assert grant_fee_schemas.GrantOfficialFeeReviewLineIn.model_config["extra"] == "forbid"
    assert grant_fee_schemas.GrantOfficialFeeReviewOut.model_config["extra"] == "forbid"
    assert set(grant_fee_schemas.GrantOfficialFeeReviewOut.model_fields) == {
        "grant_fee_task_id",
        "fee_obligation_id",
        "source_activity_id",
        "review_activity_id",
        "reviewed_line_ids",
        "confirmed_at",
        "idempotency_key",
        "reused",
    }
    signature = inspect.signature(grant_fee_api.post_grant_official_fee_review_endpoint)
    assert "current_user" in signature.parameters
    assert get_type_hints(grant_fee_api.post_grant_official_fee_review_endpoint)["return"] is (
        grant_fee_schemas.GrantOfficialFeeReviewOut
    )


def test_http_shape_rejects_extra_timezone_and_out_of_range_money() -> None:
    base = {
        "source_activity_id": "activity",
        "obligation_id": "obligation",
        "reviewed_evidence_version_id": "evidence",
        "expected_content_hash": f"sha256:{'a' * 64}",
        "confirmed_at": "2026-08-10T11:30:00",
        "idempotency_key": "review-key",
        "lines": [
            {
                "obligation_line_id": "line",
                "official_full_amount": "1111.00",
                "confirmed_payable_amount": "900.00",
            }
        ],
    }
    grant_fee_schemas.GrantOfficialFeeReviewIn.model_validate(base)
    for changed in (
        {**base, "extra": True},
        {**base, "confirmed_at": "2026-08-10T11:30:00+08:00"},
        {
            **base,
            "lines": [
                {
                    **base["lines"][0],
                    "official_full_amount": "10000000000000000.00",
                }
            ],
        },
    ):
        with pytest.raises(ValidationError):
            grant_fee_schemas.GrantOfficialFeeReviewIn.model_validate(changed)
    with pytest.raises(ValidationError):
        TypeAdapter(grant_fee_api.GrantFeeTaskPathId).validate_python("a\x00b")


def test_http_adapter_injects_actor_commits_and_rolls_back(monkeypatch: pytest.MonkeyPatch) -> None:
    payload = grant_fee_schemas.GrantOfficialFeeReviewIn.model_validate(
        {
            "source_activity_id": "activity",
            "obligation_id": "obligation",
            "reviewed_evidence_version_id": "evidence",
            "expected_content_hash": f"sha256:{'a' * 64}",
            "confirmed_at": "2026-08-10T11:30:00",
            "idempotency_key": "review-key",
            "lines": [
                {
                    "obligation_line_id": "line",
                    "official_full_amount": "1111.00",
                    "confirmed_payable_amount": "900.00",
                }
            ],
        }
    )
    captured: list[object] = []
    result = grant_fee_service.ConfirmGrantOfficialFeesResult(
        grant_fee_task_id="task",
        fee_obligation_id="obligation",
        source_activity_id="activity",
        review_activity_id="review",
        reviewed_line_ids=("line",),
        confirmed_at=payload.confirmed_at,
        idempotency_key="review-key",
        reused=False,
    )

    def confirm(command, transaction):
        captured.extend((command, transaction))
        return result

    db = SimpleNamespace(commits=0, rollbacks=0)
    db.commit = lambda: setattr(db, "commits", db.commits + 1)
    db.rollback = lambda: setattr(db, "rollbacks", db.rollbacks + 1)
    monkeypatch.setattr(grant_fee_api, "confirm_grant_official_fees", confirm)
    response = grant_fee_api.post_grant_official_fee_review_endpoint(
        "task",
        payload,
        None,
        SimpleNamespace(id="authenticated-operator"),
        db,
    )
    assert response.review_activity_id == "review"
    assert captured[0].actor_id == "authenticated-operator"
    assert captured[1] is db
    assert (db.commits, db.rollbacks) == (1, 0)

    monkeypatch.setattr(
        grant_fee_api,
        "confirm_grant_official_fees",
        lambda *_args: (_ for _ in ()).throw(RuntimeError("forced")),
    )
    with pytest.raises(RuntimeError, match="forced"):
        grant_fee_api.post_grant_official_fee_review_endpoint(
            "task",
            payload,
            None,
            SimpleNamespace(id="authenticated-operator"),
            db,
        )
    assert (db.commits, db.rollbacks) == (1, 1)


def test_manual_entry_is_durable_exact_and_replays_without_inference(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        seed = _seed(transaction, label="SUCCESS")
        case, document, task, evidence, source, obligation, line = seed
        before_revision = case.lifecycle_revision
        command = _command(seed)
        result = grant_fee_service.confirm_grant_official_fees(command, transaction)

        transaction.refresh(line)
        activity = transaction.get(CaseActivityEvent, result.review_activity_id)
        assert activity is not None
        assert result.reused is False
        assert result.reviewed_line_ids == (line.id,)
        assert line.official_full_amount == Decimal("1111.00")
        assert line.official_full_amount != line.payable_amount / line.reduction_ratio
        assert line.difference_review_state == "MATCHED"
        assert line.payable_amount == Decimal("900.00")
        assert line.source_amount == Decimal("900.00")
        assert line.updated_by == command.actor_id
        assert line.updated_at == command.confirmed_at
        assert activity.case_id == case.id
        assert activity.source_activity_id == source.activity_id
        assert activity.actor_id == activity.reviewer_id == command.actor_id
        assert activity.occurred_at == activity.effective_at == command.confirmed_at
        assert activity.sequence == before_revision + 1
        assert (
            transaction.scalar(
                select(func.count())
                .select_from(CaseActivityEventEvidence)
                .where(CaseActivityEventEvidence.activity_id == activity.id)
            )
            == 2
        )
        payload = json.loads(activity.payload_json)
        assert set(payload) == {
            "schema",
            "case_id",
            "grant_fee_task_id",
            "obligation_id",
            "source_activity_id",
            "source_document_id",
            "reviewed_evidence_version_id",
            "reviewed_evidence_content_hash",
            "confirmed_at",
            "review_basis",
            "before_lines",
            "after_lines",
        }
        assert payload["schema"] == "FPMS_GRANT_YEAR_OFFICIAL_FEE_REVIEW_CONFIRMED_V1"
        assert payload["review_basis"] == "AUTHORIZED_OPERATOR_MANUAL_ENTRY"
        assert payload["source_document_id"] == document.id
        assert payload["reviewed_evidence_version_id"] == evidence.id
        assert payload["before_lines"][0]["official_full_amount"] is None
        assert payload["before_lines"][0]["difference_review_state"] == "REVIEW_REQUIRED"
        assert payload["after_lines"][0]["official_full_amount"] == "1111.00"
        assert payload["after_lines"][0]["difference_review_state"] == "MATCHED"
        detail = get_fee_obligation(obligation.id, transaction)
        assert detail.lines[0].official_full_amount == Decimal("1111.00")
        assert detail.lines[0].difference_review_state.value == "MATCHED"

        replay = grant_fee_service.confirm_grant_official_fees(command, transaction)
        assert replay == replace(result, reused=True)
        assert len(_review_activities(transaction)) == 1
        grant_fee_service.validated_grant_year_official_fee_review_for_draft(
            transaction,
            grant_fee_task_id=task.id,
        )

        transaction.commit()
        case = transaction.get(Case, case.id)
        assert case is not None
        previous = LifecycleProjection(
            business_stage=BusinessStage(case.business_stage),
            official_procedure_stage=OfficialProcedureStage(case.official_procedure_stage),
            legal_status=LegalStatus(case.legal_status),
            lifecycle_verification_status=ConfirmationStatus(
                case.lifecycle_verification_status
            ),
        )
        current = replace(previous, business_stage=BusinessStage.GRANT_REGISTRATION_IN_PROGRESS)
        append_case_activity(
            LifecycleEventCommand(
                case_id=case.id,
                event_type="GRANT_REGISTRATION_STARTED",
                lane=ActivityLane.LIFECYCLE,
                effective_at=datetime(2026, 8, 10, 12, 0),
                occurred_at=datetime(2026, 8, 10, 12, 0),
                evidence_refs=(),
                actor_id="later-lifecycle-actor",
                idempotency_key="later-lifecycle-after-grant-review",
                confirmation_status=ConfirmationStatus.CONFIRMED,
                payload={"schema": "TEST_LATER_LIFECYCLE_V1"},
            ),
            transaction,
            previous_projection=previous,
            current_projection=current,
            legacy_case_status=case.status,
        )
        transaction.commit()
        later_replay = grant_fee_service.confirm_grant_official_fees(command, transaction)
        assert later_replay == replace(result, reused=True)
        grant_fee_service.validated_grant_year_official_fee_review_for_draft(
            transaction,
            grant_fee_task_id=task.id,
        )


def test_wrong_key_drift_dirty_transaction_and_lineage_fail_closed(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        seed = _seed(transaction, label="CONFLICTS")
        command = _command(seed)
        result = grant_fee_service.confirm_grant_official_fees(command, transaction)
        _expect(
            "GRANT_OFFICIAL_FEE_REVIEW_IDEMPOTENCY_CONFLICT",
            409,
            lambda: grant_fee_service.confirm_grant_official_fees(
                replace(
                    command,
                    lines=(replace(command.lines[0], official_full_amount=Decimal("1112.00")),),
                ),
                transaction,
            ),
        )
        _expect(
            "GRANT_OFFICIAL_FEE_REVIEW_STATE_CONFLICT",
            409,
            lambda: grant_fee_service.confirm_grant_official_fees(
                replace(command, idempotency_key="grant-official-fee-review:two"),
                transaction,
            ),
        )
        activity = transaction.get(CaseActivityEvent, result.review_activity_id)
        assert activity is not None
        activity.payload_json = activity.payload_json.replace("1111.00", "1113.00")
        transaction.commit()
        _expect(
            "GRANT_OFFICIAL_FEE_REVIEW_IDEMPOTENCY_CONFLICT",
            409,
            lambda: grant_fee_service.confirm_grant_official_fees(command, transaction),
        )

    with session_factory() as transaction:
        seed = _seed(transaction, label="DIRTY")
        transaction.add(Case(id=str(uuid4()), case_no=str(uuid4()), status="OPEN"))
        _expect(
            "GRANT_OFFICIAL_FEE_REVIEW_TRANSACTION_CONFLICT",
            409,
            lambda: grant_fee_service.confirm_grant_official_fees(_command(seed), transaction),
        )


def test_exact_complete_line_order_and_current_evidence_are_fail_closed(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        seed = _seed(transaction, label="TWO-LINES", line_count=2)
        lines = tuple(
            transaction.scalars(
                select(FeeObligationLine)
                .where(FeeObligationLine.obligation_id == seed[-2].id)
                .order_by(
                    FeeObligationLine.fee_year_key,
                    FeeObligationLine.fee_code,
                    FeeObligationLine.id,
                )
            )
        )
        assert len(lines) == 2
        command_lines = tuple(
            grant_fee_service.GrantOfficialFeeReviewLineInput(
                obligation_line_id=line.id,
                official_full_amount=Decimal(f"{1100 + index}.00"),
                confirmed_payable_amount=line.payable_amount,
            )
            for index, line in enumerate(lines)
        )
        command = replace(_command(seed), lines=command_lines)
        _expect(
            "GRANT_OFFICIAL_FEE_REVIEW_LINEAGE_CONFLICT",
            409,
            lambda: grant_fee_service.confirm_grant_official_fees(
                replace(command, lines=tuple(reversed(command_lines))),
                transaction,
            ),
        )
        result = grant_fee_service.confirm_grant_official_fees(command, transaction)
        assert result.reviewed_line_ids == tuple(line.id for line in lines)
        assert all(line.difference_review_state == "MATCHED" for line in lines)

    with session_factory() as transaction:
        seed = _seed(transaction, label="STALE-EVIDENCE")
        seed[3].review_state = "PENDING"
        transaction.commit()
        _expect(
            "GRANT_OFFICIAL_FEE_REVIEW_LINEAGE_CONFLICT",
            409,
            lambda: grant_fee_service.confirm_grant_official_fees(_command(seed), transaction),
        )


def test_failed_line_cas_is_409_and_caller_rollback_is_atomic(
    session_factory: sessionmaker,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original_execute = Session.execute

    def fail_line_update(self, statement, *args, **kwargs):
        if isinstance(statement, Update) and statement.table.name == "t_fee_obligation_line":
            return SimpleNamespace(rowcount=0)
        return original_execute(self, statement, *args, **kwargs)

    with session_factory() as transaction:
        seed = _seed(transaction, label="CAS")
        line_id = seed[-1].id
        monkeypatch.setattr(Session, "execute", fail_line_update)
        _expect(
            "GRANT_OFFICIAL_FEE_REVIEW_CONCURRENCY_CONFLICT",
            409,
            lambda: grant_fee_service.confirm_grant_official_fees(_command(seed), transaction),
        )
        transaction.rollback()
        line = transaction.get(FeeObligationLine, line_id)
        assert line is not None
        assert line.official_full_amount is None
        assert line.difference_review_state == "REVIEW_REQUIRED"
        assert _review_activities(transaction) == ()


def test_missing_named_objects_use_exact_404_boundary(session_factory: sessionmaker) -> None:
    with session_factory() as transaction:
        seed = _seed(transaction, label="MISSING-EVIDENCE")
        _expect(
            "GRANT_OFFICIAL_FEE_REVIEW_LINK_NOT_FOUND",
            404,
            lambda: grant_fee_service.confirm_grant_official_fees(
                replace(_command(seed), reviewed_evidence_version_id="missing-evidence"),
                transaction,
            ),
        )
    with session_factory() as transaction:
        seed = _seed(transaction, label="MISSING-OBLIGATION")
        _expect(
            "GRANT_OFFICIAL_FEE_REVIEW_LINK_NOT_FOUND",
            404,
            lambda: grant_fee_service.confirm_grant_official_fees(
                replace(_command(seed), obligation_id="missing-obligation"),
                transaction,
            ),
        )
    with session_factory() as transaction:
        seed = _seed(transaction, label="MISSING-LINE")
        _expect(
            "GRANT_OFFICIAL_FEE_REVIEW_LINK_NOT_FOUND",
            404,
            lambda: grant_fee_service.confirm_grant_official_fees(
                replace(
                    _command(seed),
                    lines=(
                        replace(_command(seed).lines[0], obligation_line_id="missing-line"),
                    ),
                ),
                transaction,
            ),
        )
    with session_factory() as transaction:
        seed = _seed(transaction, label="MISSING-RECOGNITION")
        recognition = next(
            activity
            for activity in transaction.scalars(
                select(CaseActivityEvent).where(
                    CaseActivityEvent.activity_type == "FEE_OBLIGATION_RECOGNIZED"
                )
            )
            if json.loads(activity.payload_json).get("obligation_id") == seed[-2].id
        )
        assert recognition is not None
        recognition.activity_type = "REMOVED_RECOGNITION"
        transaction.commit()
        _expect(
            "GRANT_OFFICIAL_FEE_REVIEW_LINK_NOT_FOUND",
            404,
            lambda: grant_fee_service.confirm_grant_official_fees(_command(seed), transaction),
        )


def test_corrupt_recognition_and_duplicate_obligation_review_block_replay_and_draft_seam(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        seed = _seed(transaction, label="CORRUPT-RECOGNITION")
        command = _command(seed)
        grant_fee_service.confirm_grant_official_fees(command, transaction)
        transaction.commit()
        recognition = transaction.scalar(
            select(CaseActivityEvent).where(
                CaseActivityEvent.activity_type == "FEE_OBLIGATION_RECOGNIZED"
            )
        )
        assert recognition is not None
        recognition_payload = json.loads(recognition.payload_json)
        recognition_payload["schema"] = "CORRUPT"
        recognition.payload_json = json.dumps(
            recognition_payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        transaction.commit()
        _expect(
            "GRANT_OFFICIAL_FEE_REVIEW_LINEAGE_CONFLICT",
            409,
            lambda: grant_fee_service.confirm_grant_official_fees(command, transaction),
        )
        _expect(
            "GRANT_OFFICIAL_FEE_REVIEW_LINEAGE_CONFLICT",
            409,
            lambda: grant_fee_service.validated_grant_year_official_fee_review_for_draft(
                transaction,
                grant_fee_task_id=seed[2].id,
            ),
        )

    with session_factory() as transaction:
        seed = _seed(transaction, label="DUPLICATE-REVIEW")
        command = _command(seed)
        result = grant_fee_service.confirm_grant_official_fees(command, transaction)
        transaction.commit()
        review = transaction.get(CaseActivityEvent, result.review_activity_id)
        case = transaction.get(Case, seed[0].id)
        assert review is not None and case is not None
        duplicate_payload = json.loads(review.payload_json)
        duplicate_payload["grant_fee_task_id"] = "different-task"
        duplicate = CaseActivityEvent(
            id=str(uuid4()),
            case_id=case.id,
            sequence=case.lifecycle_revision + 1,
            lane=review.lane,
            activity_type=review.activity_type,
            source_activity_id=review.source_activity_id,
            occurred_at=datetime(2026, 8, 10, 11, 31),
            effective_at=datetime(2026, 8, 10, 11, 31),
            confirmation_status=review.confirmation_status,
            old_business_stage=review.old_business_stage,
            new_business_stage=review.new_business_stage,
            old_official_procedure_stage=review.old_official_procedure_stage,
            new_official_procedure_stage=review.new_official_procedure_stage,
            old_legal_status=review.old_legal_status,
            new_legal_status=review.new_legal_status,
            actor_id=review.actor_id,
            reviewer_id=review.reviewer_id,
            idempotency_key="duplicate-obligation-review",
            payload_json=json.dumps(
                duplicate_payload,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ),
        )
        case.lifecycle_revision += 1
        transaction.add(duplicate)
        transaction.commit()
        _expect(
            "GRANT_OFFICIAL_FEE_REVIEW_LINEAGE_CONFLICT",
            409,
            lambda: grant_fee_service.validated_grant_year_official_fee_review_for_draft(
                transaction,
                grant_fee_task_id=seed[2].id,
            ),
        )


def test_caller_rollback_removes_activity_and_line_transition(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        seed = _seed(transaction, label="ROLLBACK")
        line_id = seed[-1].id
        grant_fee_service.confirm_grant_official_fees(_command(seed), transaction)
        assert len(_review_activities(transaction)) == 1
        transaction.rollback()
        line = transaction.get(FeeObligationLine, line_id)
        assert line is not None
        assert line.official_full_amount is None
        assert line.difference_review_state == "REVIEW_REQUIRED"
        assert _review_activities(transaction) == ()
