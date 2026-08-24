from __future__ import annotations

import hashlib
import json
import runpy
from dataclasses import replace
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, inspect, select
from sqlalchemy.orm import Session, sessionmaker
from test_v8_grant_notice_lifecycle_adapter import _grant_fixture

from app.api import deps
from app.core.errors import BusinessError
from app.modules.annuity.models import GovPayment, PayList
from app.modules.auth.models import T_User
from app.modules.billing.models import DemoFinanceCommand
from app.modules.cases.models import CaseActivityEvent, CaseActivityEventEvidence
from app.modules.documents.models import DocTemplate, Document
from app.modules.fees.demo_service import _load_bundle_snapshot
from app.modules.fees.models import (
    FeeDraft,
    FeeItem,
    FeeObligation,
    FeeObligationDraftItemLink,
    FeeObligationLine,
    FeeRate,
    OfficialRateBook,
    T_GrantFeeTask,
)
from app.modules.fees.obligation_service import get_fee_obligation
from app.modules.grant_fees import demo_official_fee
from app.modules.grant_fees import service as grant_fee_service

ROOT = Path(__file__).resolve().parents[2]
FEE_CODES = (
    "CNIPA-GRANT-REGISTRATION",
    "CNIPA-GRANT-ANNOUNCEMENT",
)
SOURCE_SNAPSHOT = json.dumps(
    {
        "schema_version": "CNIPA_RATE_SOURCE_V1",
        "sources": [
            {
                "content_sha256": hashlib.sha256(
                    b"synthetic-cnipa-official-fee-source-fixture-v1"
                ).hexdigest(),
                "document_no": None,
                "published_on": "2026-03-30",
                "retrieved_at": "2026-08-25T00:00:00Z",
                "title": "Synthetic CNIPA official fee source fixture",
                "url": (
                    "https://www.cnipa.gov.cn/art/2026/3/30/"
                    "art_1518_205552.html"
                ),
            }
        ],
    },
    ensure_ascii=False,
    sort_keys=True,
    separators=(",", ":"),
    allow_nan=False,
)
BOOK_HASH = hashlib.sha256(SOURCE_SNAPSHOT.encode("utf-8")).hexdigest()
CONFIRMED_AT = datetime(2026, 8, 23, 10, 0)
NOTICE_RECORDED_AT = datetime(2026, 7, 27, 10, 0)
BOOK_REFERENCE = "https://www.cnipa.gov.cn/art/2026/3/30/art_1518_205552.html"
BOOK_VERSION = "2026.03.30"


def _rate_row(
    *, code: str, name: str, amount: str, effective_from: date, book_id: str
) -> FeeRate:
    return FeeRate(
        id=str(uuid4()),
        fee_code=code,
        fee_name=name,
        fee_type="GOV",
        currency="CNY",
        default_amount=Decimal(amount),
        enabled=True,
        calc_mode="FIXED",
        allow_reduction=False,
        effective_from=effective_from,
        effective_to=None,
        source_doc=BOOK_REFERENCE,
        source_url=BOOK_REFERENCE,
        source_policy="CNIPA-GRANT-DEMO-V6",
        source_version=BOOK_VERSION,
        source_status="ACTIVE",
        official_rate_book_id=book_id,
    )


def _selected_rate_rows(book_id: str) -> tuple[FeeRate, FeeRate]:
    return (
        _rate_row(
            code=FEE_CODES[0],
            name="授权登记费",
            amount="900.00",
            effective_from=date(2026, 3, 30),
            book_id=book_id,
        ),
        _rate_row(
            code=FEE_CODES[1],
            name="授权公告印刷费",
            amount="50.00",
            effective_from=date(2026, 3, 30),
            book_id=book_id,
        ),
    )


@pytest.fixture
def runtime_bundle(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    helpers = runpy.run_path(str(ROOT / "backend/tests/test_demo_abc_runtime_bundle.py"))
    bundle, manifest, _manifest_sha = helpers["_valid_v6_bundle"](tmp_path)
    assert manifest["official_fee_selector"]["rate_book_sha256"] == BOOK_HASH
    assert manifest["official_fee_selector"]["fee_row_sha256s"] == {
        row.fee_code: demo_official_fee._rate_row_sha256(row)
        for row in _selected_rate_rows("runtime-selector")
    }
    manifest_sha = helpers["_write_manifest"](bundle, manifest)
    authority_sha = helpers["_authority_digest"](bundle)
    monkeypatch.setenv("FPMS_ENV", "demo")
    monkeypatch.setenv("FPMS_DEMO_SCOPE", "LOCAL_ABC_E2E")
    monkeypatch.setenv("FPMS_DEMO_RUN_PROFILE", "TECHNICAL_REHEARSAL")
    monkeypatch.setenv("FPMS_DEMO_BUNDLE_PATH", str(bundle))
    monkeypatch.setenv("FPMS_DEMO_EXPECTED_MANIFEST_SHA256", manifest_sha)
    monkeypatch.setenv("FPMS_DEMO_EXPECTED_AUTHORITY_SHA256", authority_sha)
    monkeypatch.setenv(
        "FPMS_DEMO_EXPECTED_AUTHORITY_CLASSIFICATION", "SYNTHETIC_TEST_ONLY"
    )
    _load_bundle_snapshot.cache_clear()
    yield bundle
    _load_bundle_snapshot.cache_clear()


def _seed_rate_book(transaction: Session) -> OfficialRateBook:
    actor = transaction.scalar(select(T_User).order_by(T_User.id))
    assert actor is not None
    book = OfficialRateBook(
        id=str(uuid4()),
        book_code="CNIPA-GRANT-DEMO-V6",
        version_code="2026.03.30",
        source_authority="CNIPA",
        source_reference=BOOK_REFERENCE,
        source_version=BOOK_VERSION,
        source_published_on=date(2026, 3, 30),
        source_snapshot=SOURCE_SNAPSHOT,
        source_snapshot_hash=BOOK_HASH,
        approval_status="APPROVED",
        approved_by=actor.id,
        approved_at=datetime(2026, 8, 20, 9, 0),
        effective_from=date(2026, 3, 30),
        effective_to=None,
        activation_status="ACTIVE",
        activated_by=actor.id,
        activated_at=datetime(2026, 8, 20, 9, 30),
        current_identity_key="CNIPA|CNIPA-GRANT-DEMO-V6",
    )
    transaction.add(book)
    transaction.flush()
    transaction.add_all(_selected_rate_rows(book.id))
    transaction.flush()
    return book


def _seed(transaction: Session, *, label: str = "V6", dispatch_notice: bool = True):
    case, document, task, evidence = _grant_fixture(transaction, label=label)
    task.due_date = date(2026, 11, 24)
    book = _seed_rate_book(transaction)
    if dispatch_notice:
        grant_fee_service.dispatch_grant_registration_notice(
            grant_fee_task_id=task.id,
            source_document_id=document.id,
            reviewed_evidence_version_id=evidence.id,
            expected_content_hash=evidence.content_hash,
            actor_id="demo-v6-notice-reviewer",
            recorded_at=NOTICE_RECORDED_AT,
            idempotency_key=f"demo-v6-notice-{label}",
            transaction=transaction,
        )
    transaction.commit()
    return case, document, task, evidence, book


def _counts(transaction: Session) -> tuple[int, ...]:
    models = (
        CaseActivityEvent,
        DemoFinanceCommand,
        FeeObligation,
        FeeObligationLine,
        FeeObligationDraftItemLink,
        FeeDraft,
        FeeItem,
        PayList,
        GovPayment,
    )
    return tuple(
        int(transaction.scalar(select(func.count()).select_from(model)) or 0)
        for model in models
    )


def _exact_state(transaction: Session) -> dict[str, tuple[tuple[object, ...], ...]]:
    models = (
        CaseActivityEvent,
        CaseActivityEventEvidence,
        DemoFinanceCommand,
        FeeObligation,
        FeeObligationLine,
        FeeObligationDraftItemLink,
        FeeDraft,
        FeeItem,
        PayList,
        GovPayment,
    )
    state: dict[str, tuple[tuple[object, ...], ...]] = {}
    with transaction.no_autoflush:
        for model in models:
            columns = tuple(inspect(model).columns)
            rows = transaction.execute(
                select(*(column for column in columns)).order_by(
                    *(column.asc() for column in columns)
                )
            ).all()
            state[model.__tablename__] = tuple(tuple(row) for row in rows)
    return state


def _command(task, evidence, preview, **changes: object):
    values: dict[str, object] = {
        "grant_fee_task_id": task.id,
        "preview_digest": preview.preview_digest,
        "reviewed_evidence_version_id": evidence.id,
        "expected_content_hash": evidence.content_hash,
        "confirmed_at": CONFIRMED_AT,
        "actor_id": "demo-v6-gov-reviewer",
        "idempotency_key": "demo-v6-gov-confirm-01",
        "lines": tuple(
            demo_official_fee.GrantOfficialFeeConfirmationLine(
                fee_code=line.fee_code,
                quantity=line.quantity,
                confirmed_payable_amount=line.payable_amount,
            )
            for line in preview.lines
        ),
    }
    values.update(changes)
    return demo_official_fee.ConfirmGrantOfficialFeeCommand(**values)


def test_preview_is_exact_multi_line_and_provably_write_free(
    session_factory: sessionmaker, runtime_bundle: Path
) -> None:
    with session_factory() as transaction:
        _case, _document, task, evidence, book = _seed(transaction)
        before = _exact_state(transaction)

        preview = demo_official_fee.preview_grant_official_fees(
            transaction, grant_fee_task_id=task.id
        )

        assert _exact_state(transaction) == before
        assert preview.grant_fee_task_id == task.id
        assert preview.reviewed_evidence_version_id == evidence.id
        assert preview.source_authority == "CNIPA"
        assert preview.rate_book_version == book.version_code
        assert preview.rate_book_sha256 == BOOK_HASH
        assert tuple(line.fee_code for line in preview.lines) == FEE_CODES
        assert tuple(line.payable_amount for line in preview.lines) == (
            Decimal("900.00"),
            Decimal("50.00"),
        )
        assert preview.total_payable_amount == Decimal("950.00")
        assert preview.preview_digest.startswith("sha256:")
        assert preview.preview_digest == "sha256:" + hashlib.sha256(
            preview.canonical_payload.encode("utf-8")
        ).hexdigest()


def test_preview_rejects_a_dirty_session_without_flushing_it(
    session_factory: sessionmaker, runtime_bundle: Path
) -> None:
    with session_factory() as transaction:
        _case, _document, task, _evidence, _book = _seed(transaction, label="DIRTY")
        before = _exact_state(transaction)
        task.remark = "不得由预览自动写入"

        with pytest.raises(BusinessError) as caught:
            demo_official_fee.preview_grant_official_fees(
                transaction, grant_fee_task_id=task.id
            )

        assert (caught.value.code, caught.value.status_code) == (
            "DEMO_GOV_PREVIEW_TRANSACTION_CONFLICT",
            409,
        )
        assert _exact_state(transaction) == before


def test_preview_rejects_task_due_date_drift(
    session_factory: sessionmaker, runtime_bundle: Path
) -> None:
    with session_factory() as transaction:
        _case, _document, task, _evidence, _book = _seed(
            transaction, label="DUE-DATE-DRIFT"
        )
        assert task.due_date == date(2026, 11, 24)
        task.due_date = date(2026, 11, 25)
        transaction.commit()
        before = _exact_state(transaction)

        with pytest.raises(BusinessError) as caught:
            demo_official_fee.preview_grant_official_fees(
                transaction, grant_fee_task_id=task.id
            )

        assert (caught.value.code, caught.value.status_code) == (
            "DEMO_GOV_RATE_SOURCE_CONFLICT",
            409,
        )
        assert _exact_state(transaction) == before
        assert transaction.get(T_GrantFeeTask, task.id).due_date == date(2026, 11, 25)
        assert not (transaction.new or transaction.dirty or transaction.deleted)


def test_preview_rejects_superseded_task(
    session_factory: sessionmaker, runtime_bundle: Path
) -> None:
    with session_factory() as transaction:
        case, _document, task, _evidence, _book = _seed(
            transaction, label="SUPERSEDED"
        )
        successor = T_GrantFeeTask(
            id=str(uuid4()),
            case_id=case.id,
            type="GRANT",
            due_date=task.due_date,
            source_document_id=None,
            currency="CNY",
        )
        transaction.add(successor)
        transaction.flush()
        task.superseded_by_task_id = successor.id
        transaction.commit()
        before = _exact_state(transaction)

        with pytest.raises(BusinessError) as caught:
            demo_official_fee.preview_grant_official_fees(
                transaction, grant_fee_task_id=task.id
            )

        assert (caught.value.code, caught.value.status_code) == (
            "DEMO_GOV_TASK_CONFLICT",
            409,
        )
        assert _exact_state(transaction) == before


@pytest.mark.parametrize(
    ("mutation", "code"),
    [
        (lambda _task, evidence, _book: setattr(evidence, "review_state", "PENDING"),
         "DEMO_GOV_EVIDENCE_CONFLICT"),
        (lambda _task, _evidence, book: setattr(book, "effective_to", date(2026, 8, 22)),
         "DEMO_GOV_RATE_SOURCE_CONFLICT"),
        (lambda _task, _evidence, book: setattr(book, "source_snapshot_hash", "0" * 64),
         "DEMO_GOV_RATE_SOURCE_CONFLICT"),
        (lambda _task, _evidence, book: setattr(book, "source_snapshot", '{"drift":true}'),
         "DEMO_GOV_RATE_SOURCE_CONFLICT"),
    ],
)
def test_preview_fails_closed_for_evidence_and_rate_source_drift(
    session_factory: sessionmaker,
    runtime_bundle: Path,
    mutation,
    code: str,
) -> None:
    with session_factory() as transaction:
        _case, _document, task, evidence, book = _seed(transaction, label=code)
        mutation(task, evidence, book)
        transaction.flush()
        before = _counts(transaction)
        with pytest.raises(BusinessError) as caught:
            demo_official_fee.preview_grant_official_fees(
                transaction, grant_fee_task_id=task.id
            )
        assert caught.value.code == code
        assert caught.value.status_code == 409
        assert _counts(transaction) == before


@pytest.mark.parametrize("field", ["source_doc", "source_version", "source_status"])
def test_preview_rejects_fee_rate_source_metadata_drift(
    session_factory: sessionmaker,
    runtime_bundle: Path,
    field: str,
) -> None:
    with session_factory() as transaction:
        _case, _document, task, _evidence, _book = _seed(
            transaction, label=f"RATE-{field}"
        )
        rate = transaction.scalar(
            select(FeeRate).where(FeeRate.fee_code == FEE_CODES[0])
        )
        assert rate is not None
        setattr(rate, field, "DRIFT")
        transaction.commit()

        with pytest.raises(BusinessError) as caught:
            demo_official_fee.preview_grant_official_fees(
                transaction, grant_fee_task_id=task.id
            )

        assert (caught.value.code, caught.value.status_code) == (
            "DEMO_GOV_RATE_SOURCE_CONFLICT",
            409,
        )


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("default_amount", Decimal("901.00")),
        ("fee_name", "被篡改的费用名称"),
        ("calc_mode", "TIER"),
        ("source_policy", "PENDING_CONFIRMATION_DO_NOT_EXECUTE"),
    ],
)
def test_preview_rejects_digest_unbound_rate_row_drift(
    session_factory: sessionmaker,
    runtime_bundle: Path,
    field: str,
    value: object,
) -> None:
    with session_factory() as transaction:
        _case, _document, task, _evidence, _book = _seed(
            transaction, label=f"RATE-DIGEST-{field}"
        )
        rate = transaction.scalar(
            select(FeeRate).where(FeeRate.fee_code == FEE_CODES[0])
        )
        assert rate is not None
        setattr(rate, field, value)
        transaction.commit()

        with pytest.raises(BusinessError) as caught:
            demo_official_fee.preview_grant_official_fees(
                transaction, grant_fee_task_id=task.id
            )

        assert (caught.value.code, caught.value.status_code) == (
            "DEMO_GOV_RATE_SOURCE_CONFLICT",
            409,
        )


def test_preview_requires_actionable_grant_notice_document_semantics(
    session_factory: sessionmaker, runtime_bundle: Path
) -> None:
    with session_factory() as transaction:
        _case, document, task, _evidence, _book = _seed(
            transaction, label="WRONG-DOCUMENT"
        )
        wrong_template = transaction.scalar(
            select(DocTemplate).where(DocTemplate.code != "GRANT_NOTICE")
        )
        assert wrong_template is not None
        document.doc_template_id = wrong_template.id
        transaction.commit()

        with pytest.raises(BusinessError) as caught:
            demo_official_fee.preview_grant_official_fees(
                transaction, grant_fee_task_id=task.id
            )

        assert (caught.value.code, caught.value.status_code) == (
            "DEMO_GOV_TASK_CONFLICT",
            409,
        )

        document = transaction.get(Document, document.id)
        document.doc_template_id = transaction.scalar(
            select(DocTemplate.id).where(DocTemplate.code == "GRANT_NOTICE")
        )
        task.deadline_source = None
        transaction.commit()
        with pytest.raises(BusinessError) as caught:
            demo_official_fee.preview_grant_official_fees(
                transaction, grant_fee_task_id=task.id
            )
        assert (caught.value.code, caught.value.status_code) == (
            "DEMO_GOV_TASK_CONFLICT",
            409,
        )


def test_preview_requires_persisted_grant_registration_notice_activity(
    session_factory: sessionmaker, runtime_bundle: Path
) -> None:
    with session_factory() as transaction:
        _case, _document, task, _evidence, _book = _seed(
            transaction,
            label="NO-NOTICE-ACTIVITY",
            dispatch_notice=False,
        )

        with pytest.raises(BusinessError) as caught:
            demo_official_fee.preview_grant_official_fees(
                transaction, grant_fee_task_id=task.id
            )

        assert (caught.value.code, caught.value.status_code) == (
            "DEMO_GOV_TASK_CONFLICT",
            409,
        )


def test_deeply_corrupt_notice_payload_fails_closed_as_409(
    session_factory: sessionmaker, runtime_bundle: Path
) -> None:
    with session_factory() as transaction:
        case, _document, task, _evidence, _book = _seed(
            transaction, label="DEEP-NOTICE-JSON"
        )
        notice = transaction.scalar(
            select(CaseActivityEvent).where(
                CaseActivityEvent.case_id == case.id,
                CaseActivityEvent.activity_type
                == "GRANT_REGISTRATION_NOTICE_RECORDED",
            )
        )
        assert notice is not None
        notice.payload_json = "[" * 1100 + "0" + "]" * 1100
        transaction.commit()

        with pytest.raises(BusinessError) as caught:
            demo_official_fee.preview_grant_official_fees(
                transaction, grant_fee_task_id=task.id
            )

        assert (caught.value.code, caught.value.status_code) == (
            "DEMO_GOV_TASK_CONFLICT",
            409,
        )

def test_confirmation_atomically_creates_reviewed_obligation_and_gov_only_draft(
    session_factory: sessionmaker, runtime_bundle: Path
) -> None:
    with session_factory() as transaction:
        case, _document, task, evidence, _book = _seed(transaction)
        preview = demo_official_fee.preview_grant_official_fees(
            transaction, grant_fee_task_id=task.id
        )
        command = _command(task, evidence, preview)

        first = demo_official_fee.confirm_grant_official_fees(command, transaction)
        transaction.commit()

        obligation = transaction.get(FeeObligation, first.fee_obligation_id)
        draft = transaction.get(FeeDraft, first.draft_id)
        lines = tuple(
            transaction.scalars(
                select(FeeObligationLine)
                .where(FeeObligationLine.obligation_id == obligation.id)
                .order_by(FeeObligationLine.fee_code)
            )
        )
        items = tuple(
            transaction.scalars(
                select(FeeItem).where(FeeItem.draft_id == draft.id).order_by(FeeItem.fee_code)
            )
        )
        review = transaction.get(CaseActivityEvent, first.review_activity_id)
        assert review is not None
        review_payload = json.loads(review.payload_json)
        assert get_fee_obligation(obligation.id, transaction).id == obligation.id
        instruction = transaction.scalar(
            select(CaseActivityEvent).where(
                CaseActivityEvent.case_id == case.id,
                CaseActivityEvent.activity_type == "FEE_CLIENT_INSTRUCTION_RECORDED",
            )
        )
        assert instruction is not None
        recognition = transaction.get(
            CaseActivityEvent, instruction.source_activity_id
        )
        source = transaction.get(CaseActivityEvent, recognition.source_activity_id)
        notice = transaction.get(CaseActivityEvent, source.source_activity_id)
        assert first.reused is False
        assert obligation.case_id == case.id
        assert obligation.fee_domain == "GOV"
        assert obligation.obligation_type == "GRANT_REGISTRATION_OFFICIAL_FEES"
        assert obligation.client_instruction_status == "PAY"
        assert obligation.draft_status == "CREATED"
        assert {line.fee_code for line in lines} == set(FEE_CODES)
        assert all(line.difference_review_state == "MATCHED" for line in lines)
        assert all(line.official_full_amount == line.payable_amount for line in lines)
        assert {
            row["difference_review_state"] for row in review_payload["before_lines"]
        } == {"REVIEW_REQUIRED"}
        assert {
            row["official_full_amount"] for row in review_payload["before_lines"]
        } == {None}
        assert {
            row["difference_review_state"] for row in review_payload["after_lines"]
        } == {"MATCHED"}
        assert {
            row["official_full_amount"] for row in review_payload["after_lines"]
        } == {"50.00", "900.00"}
        assert review_payload["grant_fee_task_id"] == task.id
        assert review.activity_type == (
            "GRANT_REGISTRATION_OFFICIAL_FEE_REVIEW_CONFIRMED"
        )
        assert review_payload["schema"] == (
            "FPMS_GRANT_REGISTRATION_OFFICIAL_FEE_REVIEW_CONFIRMED_V1"
        )
        assert recognition is not None
        assert source.activity_type == "DEMO_GRANT_OFFICIAL_FEE_CONFIRMED"
        assert notice.activity_type == "GRANT_REGISTRATION_NOTICE_RECORDED"
        assert recognition.sequence < review.sequence
        assert instruction.source_activity_id == recognition.id
        assert json.loads(recognition.payload_json)["obligation"][
            "source_activity_id"
        ] == review.source_activity_id
        assert draft.total_gov == draft.amount == Decimal("950.00")
        assert draft.total_service == Decimal("0.00")
        assert {item.fee_type for item in items} == {"GOV"}
        assert {item.fee_code for item in items} == set(FEE_CODES)
        assert {line.fee_code: line.source_date for line in lines} == {
            FEE_CODES[0]: date(2026, 3, 30),
            FEE_CODES[1]: date(2026, 3, 30),
        }
        assert transaction.scalar(select(func.count()).select_from(PayList)) == 0
        assert transaction.scalar(select(func.count()).select_from(GovPayment)) == 0

        replay = demo_official_fee.confirm_grant_official_fees(command, transaction)
        assert replay == replace(first, reused=True)
        assert _counts(transaction) == (6, 0, 1, 2, 2, 1, 2, 0, 0)

        with pytest.raises(BusinessError) as caught:
            grant_fee_service.validated_grant_year_official_fee_review_for_draft(
                transaction,
                grant_fee_task_id=task.id,
            )
        assert caught.value.code == "GRANT_OFFICIAL_FEE_REVIEW_STATE_CONFLICT"

        second_command = replace(
            command,
            idempotency_key="demo-v6-gov-confirm-02",
        )
        with pytest.raises(BusinessError) as caught:
            demo_official_fee.confirm_grant_official_fees(
                second_command, transaction
            )
        assert (caught.value.code, caught.value.status_code) == (
            "DEMO_GOV_CONFIRMATION_CONFLICT",
            409,
        )
        transaction.rollback()
        assert _counts(transaction) == (6, 0, 1, 2, 2, 1, 2, 0, 0)


def test_corrupt_source_payload_serialization_fails_closed_as_409(
    session_factory: sessionmaker,
    runtime_bundle: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with session_factory() as transaction:
        _case, _document, task, evidence, _book = _seed(
            transaction, label="BAD-JSON"
        )
        preview = demo_official_fee.preview_grant_official_fees(
            transaction, grant_fee_task_id=task.id
        )
        result = demo_official_fee.confirm_grant_official_fees(
            _command(task, evidence, preview), transaction
        )
        transaction.commit()
        review = transaction.get(CaseActivityEvent, result.review_activity_id)
        source = transaction.get(CaseActivityEvent, review.source_activity_id)

        def corrupt_dump(*_args, **_kwargs):
            raise ValueError("non-finite payload")

        monkeypatch.setattr(grant_fee_service.json, "dumps", corrupt_dump)
        with pytest.raises(BusinessError) as caught:
            grant_fee_service._demo_grant_official_source_context(
                transaction,
                task=task,
                activity=source,
            )

        assert (caught.value.code, caught.value.status_code) == (
            "GRANT_OFFICIAL_FEE_REVIEW_LINEAGE_CONFLICT",
            409,
        )


def test_deeply_corrupt_source_payload_fails_closed_as_409(
    session_factory: sessionmaker,
    runtime_bundle: Path,
) -> None:
    with session_factory() as transaction:
        _case, _document, task, evidence, _book = _seed(
            transaction, label="DEEP-SOURCE-JSON"
        )
        preview = demo_official_fee.preview_grant_official_fees(
            transaction, grant_fee_task_id=task.id
        )
        command = _command(task, evidence, preview)
        result = demo_official_fee.confirm_grant_official_fees(command, transaction)
        transaction.commit()
        review = transaction.get(CaseActivityEvent, result.review_activity_id)
        source = transaction.get(CaseActivityEvent, review.source_activity_id)
        source.payload_json = "[" * 1100 + "0" + "]" * 1100
        transaction.commit()

        with pytest.raises(BusinessError) as caught:
            grant_fee_service._demo_grant_official_source_context(
                transaction,
                task=task,
                activity=source,
            )
        assert (caught.value.code, caught.value.status_code) == (
            "GRANT_OFFICIAL_FEE_REVIEW_LINEAGE_CONFLICT",
            409,
        )

        with pytest.raises(BusinessError) as caught:
            demo_official_fee.confirm_grant_official_fees(
                replace(command, idempotency_key="demo-v6-deep-source-retry"),
                transaction,
            )
        assert (caught.value.code, caught.value.status_code) == (
            "DEMO_GOV_CONFIRMATION_CONFLICT",
            409,
        )


def test_deeply_corrupt_registration_review_fails_closed_as_409(
    session_factory: sessionmaker,
    runtime_bundle: Path,
) -> None:
    with session_factory() as transaction:
        _case, _document, task, evidence, _book = _seed(
            transaction, label="DEEP-REVIEW-JSON"
        )
        preview = demo_official_fee.preview_grant_official_fees(
            transaction, grant_fee_task_id=task.id
        )
        command = _command(task, evidence, preview)
        result = demo_official_fee.confirm_grant_official_fees(command, transaction)
        transaction.commit()
        review = transaction.get(CaseActivityEvent, result.review_activity_id)
        recognition = transaction.scalar(
            select(CaseActivityEvent).where(
                CaseActivityEvent.case_id == task.case_id,
                CaseActivityEvent.activity_type == "FEE_OBLIGATION_RECOGNIZED",
                CaseActivityEvent.source_activity_id == review.source_activity_id,
            )
        )
        assert recognition is not None
        obligation_lines = tuple(
            transaction.scalars(
                select(FeeObligationLine)
                .where(FeeObligationLine.obligation_id == result.fee_obligation_id)
                .order_by(
                    FeeObligationLine.fee_year_key,
                    FeeObligationLine.fee_code,
                    FeeObligationLine.id,
                )
            )
        )
        review_command = grant_fee_service.ConfirmGrantOfficialFeesCommand(
            grant_fee_task_id=task.id,
            source_activity_id=review.source_activity_id,
            obligation_id=result.fee_obligation_id,
            reviewed_evidence_version_id=evidence.id,
            expected_content_hash=evidence.content_hash,
            confirmed_at=CONFIRMED_AT,
            actor_id="demo-v6-gov-reviewer",
            idempotency_key=review.idempotency_key,
            lines=tuple(
                grant_fee_service.GrantOfficialFeeReviewLineInput(
                    obligation_line_id=line.id,
                    official_full_amount=line.official_full_amount,
                    confirmed_payable_amount=line.payable_amount,
                )
                for line in obligation_lines
            ),
        )
        review.payload_json = "[" * 1100 + "0" + "]" * 1100
        recognition.payload_json = "[" * 1100 + "0" + "]" * 1100
        transaction.commit()

        with pytest.raises(BusinessError) as caught:
            demo_official_fee.confirm_grant_official_fees(command, transaction)
        assert (caught.value.code, caught.value.status_code) == (
            "FEE_OBLIGATION_STORED_STATE_INVALID",
            409,
        )

        with pytest.raises(BusinessError) as caught:
            grant_fee_service.confirm_grant_official_fees(
                review_command, transaction
            )
        assert (caught.value.code, caught.value.status_code) == (
            "GRANT_OFFICIAL_FEE_REVIEW_IDEMPOTENCY_CONFLICT",
            409,
        )

        with pytest.raises(BusinessError) as caught:
            get_fee_obligation(result.fee_obligation_id, transaction)
        assert (caught.value.code, caught.value.status_code) == (
            "FEE_OBLIGATION_STORED_STATE_INVALID",
            409,
        )


def test_confirmation_drift_rolls_back_the_entire_composite(
    session_factory: sessionmaker, runtime_bundle: Path
) -> None:
    with session_factory() as transaction:
        _case, _document, task, evidence, _book = _seed(transaction)
        preview = demo_official_fee.preview_grant_official_fees(
            transaction, grant_fee_task_id=task.id
        )
        command = _command(task, evidence, preview)
        before = _counts(transaction)
        drifted = replace(
            command,
            lines=(
                replace(
                    command.lines[0],
                    confirmed_payable_amount=Decimal("901.00"),
                ),
                *command.lines[1:],
            ),
        )

        with pytest.raises(BusinessError) as caught:
            demo_official_fee.confirm_grant_official_fees(drifted, transaction)
        assert caught.value.status_code == 409
        transaction.rollback()
        assert _counts(transaction) == before


def test_missing_evidence_is_404_for_preview_and_confirmation(
    session_factory: sessionmaker, runtime_bundle: Path
) -> None:
    with session_factory() as transaction:
        _case, _document, task, evidence, _book = _seed(transaction)
        preview = demo_official_fee.preview_grant_official_fees(
            transaction, grant_fee_task_id=task.id
        )
        command = _command(
            task,
            evidence,
            preview,
            reviewed_evidence_version_id="missing-evidence",
        )
        with pytest.raises(BusinessError) as caught:
            demo_official_fee.confirm_grant_official_fees(command, transaction)
        assert (caught.value.code, caught.value.status_code) == (
            "DEMO_GOV_EVIDENCE_NOT_FOUND",
            404,
        )

        transaction.delete(evidence)
        transaction.flush()
        with pytest.raises(BusinessError) as caught:
            demo_official_fee.preview_grant_official_fees(
                transaction, grant_fee_task_id=task.id
            )
        assert (caught.value.code, caught.value.status_code) == (
            "DEMO_GOV_EVIDENCE_NOT_FOUND",
            404,
        )


def test_http_contract_permissions_statuses_and_validation(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
    runtime_bundle: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with session_factory() as transaction:
        _case, _document, task, evidence, _book = _seed(transaction)
        task_id = task.id
        evidence_id = evidence.id
        evidence_hash = evidence.content_hash

    preview_path = f"/api/v1/grant-fee-tasks/{task_id}/official-fee-preview"
    assert client.get(preview_path).status_code == 401
    original_permissions = deps.get_user_permissions
    monkeypatch.setattr(deps, "get_user_permissions", lambda _db, _user_id: set())
    denied = client.get(preview_path, headers=auth_headers)
    assert denied.status_code == 403
    assert denied.json()["error"]["details"]["required_perm"] == "GrantFeeTask.Read"
    monkeypatch.setattr(deps, "get_user_permissions", original_permissions)

    preview_response = client.get(preview_path, headers=auth_headers)
    assert preview_response.status_code == 200, preview_response.text
    preview = preview_response.json()
    assert "canonical_payload" not in preview
    assert {
        (line["fee_code"], line["effective_from"], line["rate_row_sha256"])
        for line in preview["lines"]
    } == {
        (row.fee_code, row.effective_from.isoformat(), demo_official_fee._rate_row_sha256(row))
        for row in _selected_rate_rows("not-digest-bound")
    }
    confirmation_path = f"/api/v1/grant-fee-tasks/{task_id}/official-fee-confirmation"
    body = {
        "preview_digest": preview["preview_digest"],
        "reviewed_evidence_version_id": evidence_id,
        "expected_content_hash": evidence_hash,
        "confirmed_at": CONFIRMED_AT.isoformat(),
        "idempotency_key": "demo-v6-gov-confirm-http",
        "lines": [
            {
                "fee_code": line["fee_code"],
                "quantity": line["quantity"],
                "confirmed_payable_amount": line["payable_amount"],
            }
            for line in preview["lines"]
        ],
    }
    assert client.post(confirmation_path, json=body).status_code == 401
    monkeypatch.setattr(
        deps, "get_user_permissions", lambda _db, _user_id: {"GrantFeeTask.Read"}
    )
    denied_write = client.post(confirmation_path, headers=auth_headers, json=body)
    assert denied_write.status_code == 403
    assert denied_write.json()["error"]["details"]["required_perm"] == "GrantFeeTask.Write"
    monkeypatch.setattr(deps, "get_user_permissions", original_permissions)
    first = client.post(confirmation_path, headers=auth_headers, json=body)
    assert first.status_code == 201, first.text
    assert first.json()["reused"] is False
    replay = client.post(confirmation_path, headers=auth_headers, json=body)
    assert replay.status_code == 200, replay.text
    assert replay.json()["reused"] is True
    assert replay.json()["draft_id"] == first.json()["draft_id"]
    drifted = json.loads(json.dumps(body))
    drifted["lines"][0]["confirmed_payable_amount"] = "901.00"
    assert client.post(confirmation_path, headers=auth_headers, json=drifted).status_code == 409

    assert client.get(
        "/api/v1/grant-fee-tasks/missing/official-fee-preview", headers=auth_headers
    ).status_code == 404
    assert client.get(
        f"/api/v1/grant-fee-tasks/{'x' * 37}/official-fee-preview", headers=auth_headers
    ).status_code == 422
    invalid = {**body, "unexpected": True}
    assert client.post(confirmation_path, headers=auth_headers, json=invalid).status_code == 422
