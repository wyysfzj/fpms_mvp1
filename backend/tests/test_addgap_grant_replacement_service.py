from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from uuid import uuid4

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from app.core.errors import BusinessError
from app.modules.cases.models import Case
from app.modules.documents.models import DocTemplate, Document
from app.modules.documents.official_notice_catalog import seed_grant_official_notice_catalog
from app.modules.documents.schemas import DocumentCreateIn
from app.modules.documents.service import create_document
from app.modules.fees.models import T_GrantFeeTask
from app.modules.grant_fees import service as grant_service


def _replacement_service():
    service = getattr(grant_service, "replace_grant_fee_task_with_notice", None)
    assert callable(service), "atomic grant replacement service is missing"
    return service


def _document_payload(
    *,
    case_id: str,
    template_id: str,
    title: str = "更正后的授权通知书",
    due_date: date = date(2026, 9, 15),
    direction: str = "IN",
) -> DocumentCreateIn:
    return DocumentCreateIn(
        case_id=case_id,
        doc_template_id=template_id,
        direction=direction,
        doc_date=date(2026, 7, 15),
        title=title,
        ref_no="GRANT-REPLACEMENT-001",
        official_due_date=due_date,
        official_due_date_source="MANUAL_OFFICIAL_NOTICE",
        official_due_date_status="CONFIRMED",
        description="客户确认的更正授权通知",
    )


def _create_old_task(db: Session) -> tuple[Case, DocTemplate, Document, T_GrantFeeTask]:
    seed_grant_official_notice_catalog(db)
    case = Case(
        id=str(uuid4()),
        case_no=f"ADDGAP-GRANT-REPLACE-{uuid4().hex[:8].upper()}",
        case_type="NORMAL",
        patent_category="INV",
        flow_dir="CN_DOMESTIC",
        title_cn="授权通知替换服务测试案件",
        status="NOT_FILED",
    )
    db.add(case)
    db.flush()
    template = db.execute(
        select(DocTemplate).where(DocTemplate.code == "OFFICIAL_NOTICE_009")
    ).scalar_one()
    source = create_document(
        db,
        DocumentCreateIn(
            case_id=case.id,
            doc_template_id=template.id,
            direction="IN",
            doc_date=date(2026, 7, 11),
            title="原授权通知书",
            ref_no="GRANT-ORIGINAL-001",
            official_due_date=date(2026, 8, 28),
            official_due_date_source="IMPORTED_OFFICIAL_NOTICE",
            official_due_date_status="CONFIRMED",
        ),
    )
    old_task = grant_service.ensure_grant_fee_task_for_notice_document(
        db,
        document=source,
        template=template,
    )
    assert old_task is not None
    old_task.gov_fee_amt = Decimal("1234.00")
    old_task.service_fee_amt = Decimal("56.00")
    old_task.notice_sent = True
    old_task.notify_count = 1
    db.commit()
    return case, template, source, old_task


def _counts(db: Session, *, case_id: str) -> tuple[int, int]:
    document_count = db.execute(
        select(func.count()).select_from(Document).where(Document.case_id == case_id)
    ).scalar_one()
    task_count = db.execute(
        select(func.count()).select_from(T_GrantFeeTask).where(T_GrantFeeTask.case_id == case_id)
    ).scalar_one()
    return document_count, task_count


def test_replacement_atomically_creates_lineage_and_same_request_reuses(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as db:
        case, template, _source, old_task = _create_old_task(db)
        payload = _document_payload(case_id=case.id, template_id=template.id)

        first = _replacement_service()(
            db,
            task_id=old_task.id,
            request_key="grant-replacement-request-001",
            reason="官方重新发文并更正缴费期限",
            replacement_document=payload,
            actor_id="reviewer-user-001",
        )

        assert first.reused is False
        assert first.superseded_task_id == old_task.id
        assert first.document.case_id == case.id
        assert first.replacement_task.source_document_id == first.document.id
        assert first.replacement_task.due_date == date(2026, 9, 15)
        assert first.replacement_task.deadline_source == "MANUAL_OFFICIAL_NOTICE"
        assert first.replacement_task.deadline_confirmed_at is not None
        assert first.replacement_task.superseded_by_task_id is None
        assert _counts(db, case_id=case.id) == (2, 2)

        refreshed_old = db.get(T_GrantFeeTask, old_task.id)
        assert refreshed_old is not None
        assert refreshed_old.superseded_by_task_id == first.replacement_task.id
        assert refreshed_old.supersede_reason == "官方重新发文并更正缴费期限"
        assert refreshed_old.superseded_at is not None
        assert refreshed_old.superseded_by == "reviewer-user-001"
        assert refreshed_old.supersede_request_key == "grant-replacement-request-001"
        assert refreshed_old.gov_fee_amt == Decimal("1234.00")
        assert refreshed_old.service_fee_amt == Decimal("56.00")
        assert refreshed_old.notice_sent is True
        assert refreshed_old.notify_count == 1

        retry = _replacement_service()(
            db,
            task_id=old_task.id,
            request_key="grant-replacement-request-001",
            reason="官方重新发文并更正缴费期限",
            replacement_document=payload,
            actor_id="reviewer-user-001",
        )

        assert retry.reused is True
        assert retry.document.id == first.document.id
        assert retry.replacement_task.id == first.replacement_task.id
        assert _counts(db, case_id=case.id) == (2, 2)


@pytest.mark.parametrize(
    ("reason", "title"),
    [
        ("不同替换原因", "更正后的授权通知书"),
        ("官方重新发文并更正缴费期限", "冲突的替换文件标题"),
    ],
)
def test_same_request_key_with_conflicting_payload_returns_409_without_writes(
    session_factory: sessionmaker,
    reason: str,
    title: str,
) -> None:
    with session_factory() as db:
        case, template, _source, old_task = _create_old_task(db)
        original_payload = _document_payload(case_id=case.id, template_id=template.id)
        _replacement_service()(
            db,
            task_id=old_task.id,
            request_key="grant-replacement-conflict-001",
            reason="官方重新发文并更正缴费期限",
            replacement_document=original_payload,
            actor_id="reviewer-user-001",
        )

        with pytest.raises(BusinessError) as exc_info:
            _replacement_service()(
                db,
                task_id=old_task.id,
                request_key="grant-replacement-conflict-001",
                reason=reason,
                replacement_document=_document_payload(
                    case_id=case.id,
                    template_id=template.id,
                    title=title,
                ),
                actor_id="reviewer-user-001",
            )

        assert exc_info.value.status_code == 409
        assert exc_info.value.code == "GRANT_REPLACEMENT_IDEMPOTENCY_CONFLICT"
        assert _counts(db, case_id=case.id) == (2, 2)


def test_same_request_replays_after_template_semantics_drift(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as db:
        case, template, _source, old_task = _create_old_task(db)
        payload = _document_payload(case_id=case.id, template_id=template.id)
        first = _replacement_service()(
            db,
            task_id=old_task.id,
            request_key="grant-replacement-stable-replay",
            reason="官方重新发文并更正缴费期限",
            replacement_document=payload,
            actor_id="reviewer-user-001",
        )
        template.input_fields = None
        db.commit()

        replay = _replacement_service()(
            db,
            task_id=old_task.id,
            request_key="grant-replacement-stable-replay",
            reason="官方重新发文并更正缴费期限",
            replacement_document=payload,
            actor_id="reviewer-user-001",
        )

        assert replay.reused is True
        assert replay.document.id == first.document.id
        assert replay.replacement_task.id == first.replacement_task.id
        assert _counts(db, case_id=case.id) == (2, 2)


def test_request_key_owned_by_another_old_task_returns_global_conflict(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as db:
        first_case, first_template, _first_source, first_old = _create_old_task(db)
        second_case, second_template, _second_source, second_old = _create_old_task(db)
        _replacement_service()(
            db,
            task_id=first_old.id,
            request_key="grant-replacement-global-key",
            reason="第一案件的授权替换",
            replacement_document=_document_payload(
                case_id=first_case.id,
                template_id=first_template.id,
            ),
            actor_id="reviewer-user-001",
        )

        with pytest.raises(BusinessError) as exc_info:
            _replacement_service()(
                db,
                task_id=second_old.id,
                request_key="grant-replacement-global-key",
                reason="第二案件试图复用全局键",
                replacement_document=_document_payload(
                    case_id=second_case.id,
                    template_id=second_template.id,
                ),
                actor_id="reviewer-user-002",
            )

        assert exc_info.value.status_code == 409
        assert exc_info.value.code == "GRANT_REPLACEMENT_IDEMPOTENCY_CONFLICT"
        assert _counts(db, case_id=first_case.id) == (2, 2)
        assert _counts(db, case_id=second_case.id) == (1, 1)


def test_replacement_rejects_business_shape_and_non_grant_semantics_before_writes(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as db:
        case, template, _source, old_task = _create_old_task(db)
        other_case = Case(
            id=str(uuid4()),
            case_no=f"ADDGAP-GRANT-OTHER-{uuid4().hex[:8].upper()}",
            case_type="NORMAL",
            patent_category="INV",
            flow_dir="CN_DOMESTIC",
            title_cn="不允许的其他案件",
            status="NOT_FILED",
        )
        db.add(other_case)
        db.commit()
        baseline_counts = _counts(db, case_id=case.id)

        for request_key, reason, payload in (
            (
                "",
                "有效原因",
                _document_payload(case_id=case.id, template_id=template.id),
            ),
            (
                "grant-replacement-shape-002",
                "   ",
                _document_payload(case_id=case.id, template_id=template.id),
            ),
            (
                "grant-replacement-shape-003",
                "有效原因",
                _document_payload(case_id=other_case.id, template_id=template.id),
            ),
            (
                "grant-replacement-shape-004",
                "有效原因",
                _document_payload(
                    case_id=case.id,
                    template_id=template.id,
                    direction="OUT",
                ),
            ),
            (
                "grant-replacement-shape-005",
                "有效原因",
                _document_payload(case_id=case.id, template_id=template.id).model_copy(
                    update={"title": "   "}
                ),
            ),
            (
                "grant-replacement-shape-006",
                "有效原因",
                _document_payload(case_id=case.id, template_id=template.id).model_copy(
                    update={"ref_no": None}
                ),
            ),
        ):
            with pytest.raises(BusinessError) as exc_info:
                _replacement_service()(
                    db,
                    task_id=old_task.id,
                    request_key=request_key,
                    reason=reason,
                    replacement_document=payload,
                    actor_id="reviewer-user-001",
                )
            assert exc_info.value.status_code == 400

        reference_template = db.execute(
            select(DocTemplate).where(DocTemplate.code == "OFFICIAL_NOTICE_010")
        ).scalar_one()
        with pytest.raises(BusinessError) as exc_info:
            _replacement_service()(
                db,
                task_id=old_task.id,
                request_key="grant-replacement-reference-only",
                reason="尝试使用参考目录",
                replacement_document=_document_payload(
                    case_id=case.id,
                    template_id=reference_template.id,
                ),
                actor_id="reviewer-user-001",
            )

        assert exc_info.value.status_code == 409
        assert exc_info.value.code == "GRANT_REPLACEMENT_TEMPLATE_INVALID"
        assert _counts(db, case_id=case.id) == baseline_counts


def test_replacement_requires_existing_confirmed_active_lineage(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as db:
        case, template, _source, old_task = _create_old_task(db)
        payload = _document_payload(case_id=case.id, template_id=template.id)

        with pytest.raises(BusinessError) as missing_exc:
            _replacement_service()(
                db,
                task_id="missing-grant-task",
                request_key="grant-replacement-missing",
                reason="不存在的旧任务",
                replacement_document=payload,
                actor_id="reviewer-user-001",
            )
        assert missing_exc.value.status_code == 404
        assert missing_exc.value.code == "GRANT_FEE_TASK_NOT_FOUND"

        old_task.deadline_confirmed_at = None
        db.commit()
        with pytest.raises(BusinessError) as legacy_exc:
            _replacement_service()(
                db,
                task_id=old_task.id,
                request_key="grant-replacement-legacy",
                reason="不允许替换未确认期限时间的旧任务",
                replacement_document=payload,
                actor_id="reviewer-user-001",
            )
        assert legacy_exc.value.status_code == 409
        assert legacy_exc.value.code == "GRANT_REPLACEMENT_LINEAGE_CONFLICT"
        assert _counts(db, case_id=case.id) == (1, 1)

        old_task.deadline_confirmed_at = datetime.now()
        old_task.deadline_source = None
        db.commit()
        with pytest.raises(BusinessError) as source_deadline_exc:
            _replacement_service()(
                db,
                task_id=old_task.id,
                request_key="grant-replacement-legacy-deadline-source",
                reason="不允许替换未确认期限来源的旧任务",
                replacement_document=payload,
                actor_id="reviewer-user-001",
            )
        assert source_deadline_exc.value.status_code == 409
        assert source_deadline_exc.value.code == "GRANT_REPLACEMENT_LINEAGE_CONFLICT"
        assert _counts(db, case_id=case.id) == (1, 1)

        old_task.deadline_source = "IMPORTED_OFFICIAL_NOTICE"
        old_task.source_document_id = None
        db.commit()
        with pytest.raises(BusinessError) as source_exc:
            _replacement_service()(
                db,
                task_id=old_task.id,
                request_key="grant-replacement-legacy-source",
                reason="不允许替换无来源旧任务",
                replacement_document=payload,
                actor_id="reviewer-user-001",
            )
        assert source_exc.value.status_code == 409
        assert source_exc.value.code == "GRANT_REPLACEMENT_LINEAGE_CONFLICT"
        assert _counts(db, case_id=case.id) == (1, 1)


def test_replacement_rolls_back_document_task_and_old_lineage_when_commit_fails(
    session_factory: sessionmaker,
    monkeypatch,
) -> None:
    with session_factory() as db:
        case, template, _source, old_task = _create_old_task(db)
        case_id = case.id
        old_task_id = old_task.id

        def fail_commit() -> None:
            raise RuntimeError("forced replacement commit failure")

        monkeypatch.setattr(db, "commit", fail_commit)
        with pytest.raises(RuntimeError, match="forced replacement commit failure"):
            _replacement_service()(
                db,
                task_id=old_task_id,
                request_key="grant-replacement-rollback",
                reason="用于验证原子回滚",
                replacement_document=_document_payload(
                    case_id=case_id,
                    template_id=template.id,
                ),
                actor_id="reviewer-user-001",
            )

    with session_factory() as verify_db:
        assert _counts(verify_db, case_id=case_id) == (1, 1)
        unchanged_old = verify_db.get(T_GrantFeeTask, old_task_id)
        assert unchanged_old is not None
        assert unchanged_old.superseded_by_task_id is None
        assert unchanged_old.supersede_request_key is None
        assert unchanged_old.supersede_reason is None
        assert unchanged_old.superseded_at is None
        assert unchanged_old.superseded_by is None
