from __future__ import annotations

from datetime import date
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import sessionmaker

from app.api import deps
from app.modules.cases.models import Case
from app.modules.documents.models import DocTemplate, Document
from app.modules.documents.official_notice_catalog import seed_grant_official_notice_catalog
from app.modules.documents.schemas import DocumentCreateIn
from app.modules.documents.service import create_document
from app.modules.fees.models import T_GrantFeeTask
from app.modules.grant_fees.service import ensure_grant_fee_task_for_notice_document

BASE = "/api/v1/grant-fee-tasks"


def _create_old_task(
    session_factory: sessionmaker,
) -> tuple[str, str, str, str]:
    with session_factory() as db:
        seed_grant_official_notice_catalog(db)
        case = Case(
            id=str(uuid4()),
            case_no=f"ADDGAP-GRANT-API-{uuid4().hex[:8].upper()}",
            case_type="NORMAL",
            patent_category="INV",
            flow_dir="CN_DOMESTIC",
            title_cn="授权通知替换 API 测试案件",
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
                ref_no="GRANT-API-ORIGINAL-001",
                official_due_date=date(2026, 8, 28),
                official_due_date_source="IMPORTED_OFFICIAL_NOTICE",
                official_due_date_status="CONFIRMED",
            ),
        )
        old_task = ensure_grant_fee_task_for_notice_document(
            db,
            document=source,
            template=template,
        )
        assert old_task is not None
        db.commit()
        return case.id, case.case_no, template.id, old_task.id


def _payload(template_id: str, *, request_key: str = "grant-api-replacement-001") -> dict:
    return {
        "idempotency_key": request_key,
        "reason": "官方重新发文并更正缴费期限",
        "document": {
            "doc_template_id": template_id,
            "doc_date": "2026-07-15",
            "title": "更正后的授权通知书",
            "ref_no": "GRANT-API-REPLACEMENT-001",
            "official_due_date": "2026-09-15",
            "official_due_date_source": "MANUAL_OFFICIAL_NOTICE",
            "official_due_date_status": "CONFIRMED",
            "description": "客户确认的更正授权通知",
        },
    }


def _counts(session_factory: sessionmaker, *, case_id: str) -> tuple[int, int]:
    with session_factory() as db:
        documents = db.execute(
            select(func.count()).select_from(Document).where(Document.case_id == case_id)
        ).scalar_one()
        tasks = db.execute(
            select(func.count())
            .select_from(T_GrantFeeTask)
            .where(T_GrantFeeTask.case_id == case_id)
        ).scalar_one()
        return documents, tasks


def test_replacement_notice_api_returns_explicit_composite_and_stable_200_retry(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    case_id, case_no, template_id, old_task_id = _create_old_task(session_factory)
    payload = _payload(template_id)

    first = client.post(
        f"{BASE}/{old_task_id}/replacement-notice",
        headers=auth_headers,
        json=payload,
    )

    assert first.status_code == 200, first.text
    first_body = first.json()
    assert set(first_body) == {
        "document",
        "replacement_task",
        "superseded_task_id",
        "reused",
    }
    assert first_body["superseded_task_id"] == old_task_id
    assert first_body["reused"] is False
    assert first_body["document"]["case_id"] == case_id
    assert first_body["document"]["case_no"] == case_no
    assert first_body["document"]["template_code"] == "OFFICIAL_NOTICE_009"
    assert first_body["document"]["official_due_date"] == "2026-09-15"
    assert first_body["replacement_task"]["case_id"] == case_id
    assert first_body["replacement_task"]["status"] == "OPEN"
    assert first_body["replacement_task"]["due_date"] == "2026-09-15"
    assert _counts(session_factory, case_id=case_id) == (2, 2)

    retry = client.post(
        f"{BASE}/{old_task_id}/replacement-notice",
        headers=auth_headers,
        json=payload,
    )

    assert retry.status_code == 200, retry.text
    retry_body = retry.json()
    assert retry_body["reused"] is True
    assert retry_body["document"]["id"] == first_body["document"]["id"]
    assert retry_body["replacement_task"]["task_id"] == first_body["replacement_task"]["task_id"]
    assert _counts(session_factory, case_id=case_id) == (2, 2)

    conflicting_payload = _payload(template_id)
    conflicting_payload["document"]["title"] = "冲突的替换标题"
    conflict = client.post(
        f"{BASE}/{old_task_id}/replacement-notice",
        headers=auth_headers,
        json=conflicting_payload,
    )
    assert conflict.status_code == 409, conflict.text
    assert conflict.json()["error"]["code"] == "GRANT_REPLACEMENT_IDEMPOTENCY_CONFLICT"


@pytest.mark.parametrize(
    ("permissions", "missing_permission"),
    [
        ({"Doc.Create"}, "GrantFeeTask.Write"),
        ({"GrantFeeTask.Write"}, "Doc.Create"),
    ],
)
def test_replacement_notice_api_requires_both_independent_permissions(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
    monkeypatch,
    permissions: set[str],
    missing_permission: str,
) -> None:
    case_id, _case_no, template_id, old_task_id = _create_old_task(session_factory)
    monkeypatch.setattr(deps, "get_user_permissions", lambda _db, _user_id: permissions)

    response = client.post(
        f"{BASE}/{old_task_id}/replacement-notice",
        headers=auth_headers,
        json=_payload(template_id),
    )

    assert response.status_code == 403, response.text
    assert response.json()["error"]["details"]["required_perm"] == missing_permission
    assert _counts(session_factory, case_id=case_id) == (1, 1)


def test_replacement_notice_api_derives_case_and_rejects_caller_case_id(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    case_id, _case_no, template_id, old_task_id = _create_old_task(session_factory)
    payload = _payload(template_id)
    payload["document"]["case_id"] = str(uuid4())

    response = client.post(
        f"{BASE}/{old_task_id}/replacement-notice",
        headers=auth_headers,
        json=payload,
    )

    assert response.status_code == 422, response.text
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"
    assert _counts(session_factory, case_id=case_id) == (1, 1)


def test_replacement_notice_api_preserves_business_error_statuses_and_envelope(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    case_id, _case_no, template_id, old_task_id = _create_old_task(session_factory)

    missing = client.post(
        f"{BASE}/missing-task/replacement-notice",
        headers=auth_headers,
        json=_payload(template_id),
    )
    assert missing.status_code == 404, missing.text
    assert missing.json()["error"]["code"] == "GRANT_FEE_TASK_NOT_FOUND"

    blank_title_payload = _payload(template_id)
    blank_title_payload["document"]["title"] = "   "
    blank_title = client.post(
        f"{BASE}/{old_task_id}/replacement-notice",
        headers=auth_headers,
        json=blank_title_payload,
    )
    assert blank_title.status_code == 400, blank_title.text
    assert blank_title.json()["error"]["code"] == "GRANT_REPLACEMENT_DOCUMENT_INVALID"

    unconfirmed_payload = _payload(template_id)
    del unconfirmed_payload["document"]["official_due_date"]
    del unconfirmed_payload["document"]["official_due_date_source"]
    del unconfirmed_payload["document"]["official_due_date_status"]
    unconfirmed = client.post(
        f"{BASE}/{old_task_id}/replacement-notice",
        headers=auth_headers,
        json=unconfirmed_payload,
    )
    assert unconfirmed.status_code == 409, unconfirmed.text
    assert unconfirmed.json()["error"]["code"] == "GRANT_OFFICIAL_DUE_DATE_REQUIRED"

    malformed_payload = _payload(template_id)
    malformed_payload["document"]["doc_date"] = "not-a-date"
    malformed = client.post(
        f"{BASE}/{old_task_id}/replacement-notice",
        headers=auth_headers,
        json=malformed_payload,
    )
    assert malformed.status_code == 422, malformed.text
    assert malformed.json()["error"]["code"] == "VALIDATION_ERROR"
    assert _counts(session_factory, case_id=case_id) == (1, 1)
