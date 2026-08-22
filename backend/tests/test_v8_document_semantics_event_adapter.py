from __future__ import annotations

from dataclasses import asdict
from datetime import date
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from app.modules.cases.models import Case, CaseActivityEvent
from app.modules.documents.extra_data import parse_document_extra_data
from app.modules.documents.models import DocTemplate, Document
from app.modules.documents.semantics import ResolvedDocumentSemantics
from app.modules.fees.models import T_GrantFeeTask


def _resolved_semantics(execution_behavior: str | None) -> ResolvedDocumentSemantics:
    return ResolvedDocumentSemantics(
        catalog_status="EXECUTABLE" if execution_behavior else "REFERENCE_ONLY",
        execution_behavior=execution_behavior,
        case_status_effect=None,
        task_template_code=None,
        requires_reply=False,
        completion_event=None,
        archive_status_restore=None,
        deadline_source_policy=None,
        fee_trigger=None,
    )


@pytest.mark.parametrize(
    ("execution_behavior", "expected_event_type"),
    [
        ("ACCEPTANCE_NOTICE", "ACCEPTANCE_NOTICE_RECORDED"),
        ("OA_REPLY", "OA_NOTICE_RECORDED"),
        ("GRANT_NOTICE", "GRANT_REGISTRATION_NOTICE_RECORDED"),
        ("APPLICATION_FEE_NOTICE", None),
        ("FEE_REDUCTION_APPROVAL_NOTICE", None),
        (None, None),
    ],
)
def test_lifecycle_event_type_is_computed_without_changing_asdict(
    execution_behavior: str | None,
    expected_event_type: str | None,
) -> None:
    semantics = _resolved_semantics(execution_behavior)

    assert semantics.lifecycle_event_type == expected_event_type
    assert asdict(semantics) == {
        "catalog_status": "EXECUTABLE" if execution_behavior else "REFERENCE_ONLY",
        "execution_behavior": execution_behavior,
        "case_status_effect": None,
        "task_template_code": None,
        "requires_reply": False,
        "completion_event": None,
        "archive_status_restore": None,
        "deadline_source_policy": None,
        "fee_trigger": None,
    }


def _create_case(
    client: TestClient,
    auth_headers: dict[str, str],
    *,
    label: str,
) -> str:
    response = client.post(
        "/api/v1/cases",
        headers=auth_headers,
        json={
            "case_no": f"V8-DOC-EVENT-{uuid4().hex[:8].upper()}",
            "case_type": "NORMAL",
            "patent_category": "INV",
            "flow_dir": "CN_DOMESTIC",
            "fee_reduction": "0",
            "title_cn": label,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def _template_id(db: Session, code: str) -> str:
    return db.execute(select(DocTemplate.id).where(DocTemplate.code == code)).scalar_one()


def _case_lifecycle_snapshot(db: Session, case_id: str) -> tuple[object, ...]:
    case = db.get(Case, case_id)
    assert case is not None
    activity_count = db.scalar(
        select(func.count())
        .select_from(CaseActivityEvent)
        .where(CaseActivityEvent.case_id == case_id)
    )
    return (
        case.status,
        case.business_stage,
        case.official_procedure_stage,
        case.legal_status,
        case.lifecycle_revision,
        activity_count,
    )


def test_ordinary_oa_create_persists_due_and_reply_without_lifecycle_effects(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    case_id = _create_case(client, auth_headers, label="OA普通创建保持证据中立")
    with session_factory() as db:
        case = db.get(Case, case_id)
        assert case is not None
        case.status = "SUB_EXAM"
        template_id = _template_id(db, "OA_IN")
        db.commit()
        before = _case_lifecycle_snapshot(db, case_id)

    response = client.post(
        "/api/v1/documents",
        headers=auth_headers,
        json={
            "case_id": case_id,
            "doc_template_id": template_id,
            "doc_type": "OFFICIAL_IN",
            "direction": "IN",
            "doc_date": "2026-07-24",
            "title": "第一次审查意见通知书",
            "official_due_date": "2026-11-21",
            "official_due_date_source": "MANUAL_OFFICIAL_NOTICE",
            "official_due_date_status": "CONFIRMED",
        },
    )

    assert response.status_code == 201, response.text
    with session_factory() as db:
        document = db.get(Document, response.json()["id"])
        assert document is not None
        due = parse_document_extra_data(document.extra_data)
        assert document.need_reply is True
        assert (
            due.official_due_date,
            due.official_due_date_source,
            due.official_due_date_status,
        ) == (
            date(2026, 11, 21),
            "MANUAL_OFFICIAL_NOTICE",
            "CONFIRMED",
        )
        assert _case_lifecycle_snapshot(db, case_id) == before


def test_grant_create_routes_task_without_generic_lifecycle_event(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    case_id = _create_case(client, auth_headers, label="授权普通创建仅保留路由元数据")
    with session_factory() as db:
        template_id = _template_id(db, "GRANT_NOTICE")
        before = _case_lifecycle_snapshot(db, case_id)

    response = client.post(
        "/api/v1/documents",
        headers=auth_headers,
        json={
            "case_id": case_id,
            "doc_template_id": template_id,
            "doc_type": "OFFICIAL_IN",
            "direction": "IN",
            "doc_date": "2026-07-24",
            "title": "授权通知书",
            "official_due_date": "2026-09-24",
            "official_due_date_source": "MANUAL_OFFICIAL_NOTICE",
            "official_due_date_status": "CONFIRMED",
        },
    )

    assert response.status_code == 201, response.text
    with session_factory() as db:
        document = db.get(Document, response.json()["id"])
        assert document is not None
        grant_task = db.scalar(
            select(T_GrantFeeTask).where(
                T_GrantFeeTask.case_id == case_id,
                T_GrantFeeTask.source_document_id == document.id,
            )
        )
        assert grant_task is not None
        assert grant_task.due_date == date(2026, 9, 24)
        assert _case_lifecycle_snapshot(db, case_id) == before


def test_ordinary_reply_create_does_not_apply_template_status_restore(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    case_id = _create_case(client, auth_headers, label="普通答复创建不恢复案件状态")
    with session_factory() as db:
        case = db.get(Case, case_id)
        assert case is not None
        case.status = "OA1"
        source_document = Document(
            id=str(uuid4()),
            case_id=case_id,
            doc_template_id=_template_id(db, "OA_IN"),
            direction="IN",
            doc_date=date(2026, 7, 23),
            title="待答复审查意见通知书",
            need_reply=True,
        )
        reply_template = DocTemplate(
            id=str(uuid4()),
            code=f"V8_REPLY_RESTORE_{uuid4().hex[:8].upper()}",
            name="普通答复状态恢复模板",
            direction="OUT",
            status_restore="ACCEPTED",
            reply_to_template_code="OA_IN",
            need_reply=False,
        )
        db.add_all([source_document, reply_template])
        db.commit()
        source_document_id = source_document.id
        reply_template_id = reply_template.id
        before = _case_lifecycle_snapshot(db, case_id)

    response = client.post(
        "/api/v1/documents",
        headers=auth_headers,
        json={
            "case_id": case_id,
            "doc_template_id": reply_template_id,
            "direction": "OUT",
            "doc_date": "2026-07-24",
            "title": "普通答复文件",
            "reply_to_id": source_document_id,
        },
    )

    assert response.status_code == 201, response.text
    with session_factory() as db:
        reply_document = db.get(Document, response.json()["id"])
        source_document = db.get(Document, source_document_id)
        assert reply_document is not None
        assert source_document is not None
        assert source_document.reply_date == date(2026, 7, 24)
        assert _case_lifecycle_snapshot(db, case_id) == before


def test_wizard_batch_oa_create_preserves_lifecycle_snapshot(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    case_id = _create_case(client, auth_headers, label="OA批量创建保持证据中立")
    with session_factory() as db:
        case = db.get(Case, case_id)
        assert case is not None
        case.status = "SUB_EXAM"
        template_id = _template_id(db, "OA_IN")
        db.commit()
        before = _case_lifecycle_snapshot(db, case_id)

    response = client.post(
        "/api/v1/documents/wizard/batch-create",
        headers=auth_headers,
        json={
            "defaults": {
                "doc_template_id": template_id,
                "direction": "IN",
                "doc_date": "2026-07-24",
                "official_due_date": "2026-11-21",
                "official_due_date_source": "MANUAL_OFFICIAL_NOTICE",
                "official_due_date_status": "CONFIRMED",
            },
            "rows": [{"case_id": case_id, "title": "批量审查意见通知书"}],
        },
    )

    assert response.status_code == 201, response.text
    document_id = response.json()["items"][0]["document"]["id"]
    with session_factory() as db:
        document = db.get(Document, document_id)
        assert document is not None
        due = parse_document_extra_data(document.extra_data)
        assert document.need_reply is True
        assert due.official_due_date == date(2026, 11, 21)
        assert _case_lifecycle_snapshot(db, case_id) == before


def test_ordinary_edit_applies_document_defaults_without_lifecycle_effects(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    case_id = _create_case(client, auth_headers, label="普通编辑保持证据中立")
    with session_factory() as db:
        case = db.get(Case, case_id)
        assert case is not None
        case.status = "SUB_EXAM"
        client_template_id = _template_id(db, "CLIENT_IN")
        oa_template_id = _template_id(db, "OA_IN")
        db.commit()

    created = client.post(
        "/api/v1/documents",
        headers=auth_headers,
        json={
            "case_id": case_id,
            "doc_template_id": client_template_id,
            "direction": "IN",
            "doc_date": "2026-07-24",
            "title": "普通编辑目标文件",
            "official_due_date": "2026-11-21",
            "official_due_date_source": "MANUAL_OFFICIAL_NOTICE",
            "official_due_date_status": "CONFIRMED",
        },
    )
    assert created.status_code == 201, created.text
    with session_factory() as db:
        before = _case_lifecycle_snapshot(db, case_id)

    response = client.put(
        f"/api/v1/documents/{created.json()['id']}",
        headers=auth_headers,
        json={"doc_template_id": oa_template_id},
    )

    assert response.status_code == 200, response.text
    assert response.json()["need_reply"] is True
    assert response.json()["official_due_date"] == "2026-11-21"
    with session_factory() as db:
        assert _case_lifecycle_snapshot(db, case_id) == before


def test_impact_preview_hides_legacy_status_authority_and_shows_exact_risk_tip(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    risk_tip = (
        "文书登记不会直接变更案件法律状态；"
        "请通过已复核证据的生命周期入口确认状态变化"
    )
    case_id = _create_case(client, auth_headers, label="预览不宣称案件状态变更")
    with session_factory() as db:
        oa_template_id = _template_id(db, "OA_IN")
        reply_template = DocTemplate(
            id=str(uuid4()),
            code=f"V8_PREVIEW_RESTORE_{uuid4().hex[:8].upper()}",
            name="预览状态恢复兼容模板",
            direction="OUT",
            status_restore="SUB_EXAM",
            need_reply=False,
        )
        source = Document(
            id=str(uuid4()),
            case_id=case_id,
            direction="IN",
            doc_date=date(2026, 7, 23),
            title="预览回复来源",
        )
        db.add_all([reply_template, source])
        db.commit()
        reply_template_id = reply_template.id
        source_id = source.id
        before = _case_lifecycle_snapshot(db, case_id)

    inbound = client.post(
        "/api/v1/documents/impact-preview",
        headers=auth_headers,
        json={
            "case_id": case_id,
            "doc_template_id": oa_template_id,
            "direction": "IN",
            "doc_date": "2026-07-24",
            "title": "审查意见通知书预览",
            "official_due_date": "2026-11-21",
            "official_due_date_source": "MANUAL_OFFICIAL_NOTICE",
            "official_due_date_status": "CONFIRMED",
        },
    )
    outbound = client.post(
        "/api/v1/documents/impact-preview",
        headers=auth_headers,
        json={
            "case_id": case_id,
            "doc_template_id": reply_template_id,
            "direction": "OUT",
            "doc_date": "2026-07-24",
            "title": "答复文件预览",
            "reply_to_id": source_id,
        },
    )

    assert inbound.status_code == 200, inbound.text
    assert outbound.status_code == 200, outbound.text
    for response in (inbound, outbound):
        payload = response.json()
        assert payload["status_impacts"] == []
        assert risk_tip in payload["risk_tips"]
    with session_factory() as db:
        assert _case_lifecycle_snapshot(db, case_id) == before
