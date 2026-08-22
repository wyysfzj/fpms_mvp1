from __future__ import annotations

import json
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime
from uuid import uuid4

import pytest
from sqlalchemy import select, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.errors import BusinessError
from app.modules.cases.models import Case
from app.modules.documents.models import DocTemplate, Document
from app.modules.fees.models import T_GrantFeeTask
from app.modules.grant_fees.service import ensure_grant_fee_task_for_notice_document


def _create_case(db: Session) -> Case:
    case = Case(
        id=str(uuid4()),
        case_no=f"ADDGAP-GRANT-{uuid4().hex[:8].upper()}",
        case_type="NORMAL",
        patent_category="INV",
        flow_dir="CN_DOMESTIC",
        title_cn="授权来源期限测试案件",
        status="GRANT_PENDING",
    )
    db.add(case)
    db.commit()
    return case


def _grant_alias_template(db: Session) -> DocTemplate:
    template = DocTemplate(
        id=str(uuid4()),
        code=f"GRANT_ALIAS_{uuid4().hex[:8].upper()}",
        name="可执行授权通知别名",
        direction="IN",
        status_effect="GRANT_PENDING",
        fee_draft_type="GRANT_FEE",
        need_reply=False,
        input_fields=json.dumps(
            {
                "catalog_kind": "OFFICIAL_NOTICE",
                "catalog_status": "EXECUTABLE",
                "execution_behavior": "GRANT_NOTICE",
                "completion_event": None,
                "archive_status_restore": None,
                "deadline_source_policy": "EXPLICIT_OFFICIAL_DUE_REQUIRED",
                "canonical_template_code": "GRANT_NOTICE",
            },
            ensure_ascii=False,
        ),
    )
    db.add(template)
    db.commit()
    return template


def _create_document(
    db: Session,
    *,
    case: Case,
    template: DocTemplate,
    due_date: date | None,
    due_source: str | None,
    due_status: str | None,
) -> Document:
    fields = {}
    if due_date is not None:
        fields["OfficialDueDate"] = due_date.isoformat()
    if due_source is not None:
        fields["OfficialDueDateSource"] = due_source
    if due_status is not None:
        fields["OfficialDueDateStatus"] = due_status
    document = Document(
        id=str(uuid4()),
        case_id=case.id,
        doc_template_id=template.id,
        doc_type="OFFICIAL_NOTICE",
        direction="IN",
        doc_date=date(2026, 7, 10),
        title="授权通知书",
        extra_data=json.dumps(fields) if fields else None,
    )
    db.add(document)
    db.commit()
    return document


def _tasks(db: Session, *, case_id: str) -> list[T_GrantFeeTask]:
    return list(
        db.execute(
            select(T_GrantFeeTask)
            .where(T_GrantFeeTask.case_id == case_id)
            .order_by(T_GrantFeeTask.created_at.asc(), T_GrantFeeTask.id.asc())
        )
        .scalars()
        .all()
    )


def test_first_executable_grant_source_uses_confirmed_explicit_due(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as db:
        case = _create_case(db)
        template = _grant_alias_template(db)
        explicit_due = date(2026, 8, 28)
        document = _create_document(
            db,
            case=case,
            template=template,
            due_date=explicit_due,
            due_source="MANUAL_OFFICIAL_NOTICE",
            due_status="CONFIRMED",
        )
        before = datetime.now()

        task = ensure_grant_fee_task_for_notice_document(
            db,
            document=document,
            template=template,
        )
        db.commit()

        assert task is not None
        assert task.due_date == explicit_due
        assert task.due_date != date(2026, 9, 8)
        assert task.source_document_id == document.id
        assert task.deadline_source == "MANUAL_OFFICIAL_NOTICE"
        assert task.deadline_confirmed_at is not None
        assert before <= task.deadline_confirmed_at <= datetime.now()
        assert [item.id for item in _tasks(db, case_id=case.id)] == [task.id]


def test_repeated_same_grant_source_reuses_one_task(session_factory: sessionmaker) -> None:
    with session_factory() as db:
        case = _create_case(db)
        template = _grant_alias_template(db)
        document = _create_document(
            db,
            case=case,
            template=template,
            due_date=date(2026, 8, 28),
            due_source="IMPORTED_OFFICIAL_NOTICE",
            due_status="CONFIRMED",
        )

        first = ensure_grant_fee_task_for_notice_document(
            db,
            document=document,
            template=template,
        )
        db.commit()
        second = ensure_grant_fee_task_for_notice_document(
            db,
            document=document,
            template=template,
        )

        assert first is not None
        assert second is not None
        assert second.id == first.id
        assert [item.id for item in _tasks(db, case_id=case.id)] == [first.id]


@pytest.mark.parametrize(
    ("due_date", "due_source", "due_status"),
    [
        (None, None, None),
        (date(2026, 8, 28), "IMPORTED_OFFICIAL_NOTICE", "NEEDS_CONFIRMATION"),
    ],
)
def test_missing_or_unconfirmed_grant_due_fails_closed(
    session_factory: sessionmaker,
    due_date,
    due_source,
    due_status,
) -> None:
    with session_factory() as db:
        case = _create_case(db)
        template = _grant_alias_template(db)
        document = _create_document(
            db,
            case=case,
            template=template,
            due_date=due_date,
            due_source=due_source,
            due_status=due_status,
        )

        with pytest.raises(BusinessError) as exc_info:
            ensure_grant_fee_task_for_notice_document(
                db,
                document=document,
                template=template,
            )

        assert exc_info.value.status_code == 409
        assert exc_info.value.code == "GRANT_OFFICIAL_DUE_DATE_REQUIRED"
        assert _tasks(db, case_id=case.id) == []


def test_different_active_grant_source_requires_explicit_replacement(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as db:
        case = _create_case(db)
        template = _grant_alias_template(db)
        first_source = _create_document(
            db,
            case=case,
            template=template,
            due_date=date(2026, 8, 28),
            due_source="MANUAL_OFFICIAL_NOTICE",
            due_status="CONFIRMED",
        )
        first_task = ensure_grant_fee_task_for_notice_document(
            db,
            document=first_source,
            template=template,
        )
        db.commit()
        second_source = _create_document(
            db,
            case=case,
            template=template,
            due_date=date(2026, 9, 15),
            due_source="MANUAL_OFFICIAL_NOTICE",
            due_status="CONFIRMED",
        )

        with pytest.raises(BusinessError) as exc_info:
            ensure_grant_fee_task_for_notice_document(
                db,
                document=second_source,
                template=template,
            )

        assert exc_info.value.status_code == 409
        assert exc_info.value.code == "GRANT_FEE_TASK_ACTIVE_SOURCE_CONFLICT"
        assert first_task is not None
        assert [item.id for item in _tasks(db, case_id=case.id)] == [first_task.id]


def test_non_grant_semantics_remain_noop(session_factory: sessionmaker) -> None:
    with session_factory() as db:
        case = _create_case(db)
        template = db.execute(
            select(DocTemplate).where(DocTemplate.code == "CLIENT_IN")
        ).scalar_one()
        document = _create_document(
            db,
            case=case,
            template=template,
            due_date=date(2026, 8, 28),
            due_source="MANUAL_OFFICIAL_NOTICE",
            due_status="CONFIRMED",
        )

        result = ensure_grant_fee_task_for_notice_document(
            db,
            document=document,
            template=template,
        )

        assert result is None
        assert _tasks(db, case_id=case.id) == []


@pytest.mark.parametrize("same_source", [True, False])
def test_true_overlapping_sqlite_writers_resolve_without_raw_lock_error(
    session_factory: sessionmaker,
    same_source: bool,
) -> None:
    with session_factory() as setup_db:
        case = _create_case(setup_db)
        template = _grant_alias_template(setup_db)
        first_source = _create_document(
            setup_db,
            case=case,
            template=template,
            due_date=date(2026, 8, 28),
            due_source="MANUAL_OFFICIAL_NOTICE",
            due_status="CONFIRMED",
        )
        second_source = first_source
        if not same_source:
            second_source = _create_document(
                setup_db,
                case=case,
                template=template,
                due_date=date(2026, 9, 15),
                due_source="IMPORTED_OFFICIAL_NOTICE",
                due_status="CONFIRMED",
            )
        case_id = case.id
        template_id = template.id
        source_ids = (first_source.id, second_source.id)

    start_barrier = threading.Barrier(2)

    def run_writer(
        source_document_id: str,
    ) -> tuple[str, str | None, str | None, bool, bool]:
        with session_factory() as db:
            db.execute(text("PRAGMA busy_timeout = 1"))
            assert db.execute(text("PRAGMA busy_timeout")).scalar_one() == 1
            document = db.get(Document, source_document_id)
            loaded_template = db.get(DocTemplate, template_id)
            assert document is not None
            assert loaded_template is not None
            outer_transaction = db.get_transaction()
            assert outer_transaction is not None
            start_barrier.wait(timeout=3)
            try:
                task = ensure_grant_fee_task_for_notice_document(
                    db,
                    document=document,
                    template=loaded_template,
                )
                assert task is not None
                transaction_preserved = (
                    db.get_transaction() is outer_transaction and outer_transaction.is_active
                )
                driver_transaction_active = (
                    db.connection().connection.driver_connection.in_transaction
                )
                time.sleep(0.4)
                db.commit()
                return (
                    "ok",
                    task.id,
                    task.source_document_id,
                    transaction_preserved,
                    driver_transaction_active,
                )
            except BusinessError as exc:
                transaction_preserved = (
                    db.get_transaction() is outer_transaction and outer_transaction.is_active
                )
                driver_transaction_active = (
                    db.connection().connection.driver_connection.in_transaction
                )
                db.rollback()
                return (
                    "business",
                    exc.code,
                    None,
                    transaction_preserved,
                    driver_transaction_active,
                )
            except Exception as exc:  # pragma: no cover - asserted through returned diagnostics
                transaction_preserved = (
                    db.get_transaction() is outer_transaction and outer_transaction.is_active
                )
                driver_transaction_active = (
                    db.connection().connection.driver_connection.in_transaction
                )
                db.rollback()
                return (
                    "raw",
                    type(exc).__name__,
                    str(exc),
                    transaction_preserved,
                    driver_transaction_active,
                )

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(run_writer, source_ids))

    assert all(result[0] != "raw" for result in results), results
    assert all(result[3] is True for result in results), results
    assert all(result[4] is True for result in results), results
    if same_source:
        assert [result[0] for result in results] == ["ok", "ok"]
        assert len({result[1] for result in results}) == 1
        assert {result[2] for result in results} == {first_source.id}
    else:
        assert sorted(result[0] for result in results) == ["business", "ok"]
        assert [result[1] for result in results if result[0] == "business"] == [
            "GRANT_FEE_TASK_ACTIVE_SOURCE_CONFLICT"
        ]

    with session_factory() as verify_db:
        tasks = _tasks(verify_db, case_id=case_id)
        assert len(tasks) == 1
        assert tasks[0].source_document_id in source_ids
