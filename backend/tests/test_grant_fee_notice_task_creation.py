from __future__ import annotations

from datetime import date
from io import BytesIO
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from app.modules.cases.models import Case
from app.modules.fees.models import T_GrantFeeTask

DOC_BASE = "/api/v1/documents"
DOC_TEMPLATE_BASE = "/api/v1/doc-templates"
CASE_BASE = "/api/v1/cases"
GRANT_FEE_TASK_BASE = "/api/v1/grant-fee-tasks/list"


def _uid(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:8].upper()}"


def _create_case(client: TestClient, auth_headers: dict[str, str]) -> dict:
    resp = client.post(
        CASE_BASE,
        json={
            "case_no": _uid("GFNT-CASE"),
            "case_type": "NORMAL",
            "patent_category": "INV",
            "flow_dir": "CN_DOMESTIC",
            "title_cn": "Grant fee notice task case",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def _get_template(client: TestClient, auth_headers: dict[str, str], code: str) -> dict:
    resp = client.get(
        DOC_TEMPLATE_BASE,
        params={"q": code, "page_size": 100},
        headers=auth_headers,
    )
    assert resp.status_code == 200, resp.text
    matches = [item for item in resp.json()["items"] if item["code"] == code]
    assert len(matches) == 1
    return matches[0]


def _create_grant_notice(
    client: TestClient,
    auth_headers: dict[str, str],
    *,
    case_id: str,
    template_id: str,
    title: str,
) -> dict:
    resp = client.post(
        DOC_BASE,
        json={
            "case_id": case_id,
            "doc_template_id": template_id,
            "direction": "IN",
            "doc_date": "2026-04-10",
            "title": title,
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def _set_case_ready_for_granted(session_factory: sessionmaker, *, case_id: str) -> None:
    with session_factory() as db:
        case = db.execute(select(Case).where(Case.id == case_id)).scalar_one()
        case.app_no = "CN202610000009"
        case.filing_date = date(2026, 3, 20)
        case.pub_no = "CN202610000009A"
        case.pub_date = date(2026, 4, 1)
        case.grant_no = "CN202610000009B"
        case.grant_date = date(2026, 8, 1)
        case.first_annuity_year = 3
        case.valid_until = date(2046, 3, 20)
        db.commit()


def test_grant_notice_document_creation_creates_one_reusable_grant_fee_task(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    case = _create_case(client, auth_headers)
    template = _get_template(client, auth_headers, "GRANT_NOTICE")

    _create_grant_notice(
        client,
        auth_headers,
        case_id=case["id"],
        template_id=template["id"],
        title="授权通知书",
    )
    _create_grant_notice(
        client,
        auth_headers,
        case_id=case["id"],
        template_id=template["id"],
        title="授权通知书-重复登记",
    )

    resp = client.get(
        GRANT_FEE_TASK_BASE,
        params={"case_id": case["id"], "page_size": 100},
        headers=auth_headers,
    )
    assert resp.status_code == 200, resp.text
    payload = resp.json()
    assert payload["total"] == 1
    assert len(payload["items"]) == 1
    item = payload["items"][0]
    assert item["case_id"] == case["id"]
    assert item["status"] == "OPEN"
    assert item["due_date"] == "2026-06-09"
    assert item["currency"] == "CNY"

    with session_factory() as db:
        tasks = (
            db.execute(select(T_GrantFeeTask).where(T_GrantFeeTask.case_id == case["id"]))
            .scalars()
            .all()
        )
        assert len(tasks) == 1
        assert tasks[0].due_date == date(2026, 6, 9)

    case_resp = client.get(f"{CASE_BASE}/{case['id']}", headers=auth_headers)
    assert case_resp.status_code == 200, case_resp.text
    assert case_resp.json()["status"] == "GRANT_PENDING"


def test_grant_notice_attachment_upload_advances_ready_case_to_granted(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    case = _create_case(client, auth_headers)
    _set_case_ready_for_granted(session_factory, case_id=case["id"])
    template = _get_template(client, auth_headers, "GRANT_NOTICE")

    document = _create_grant_notice(
        client,
        auth_headers,
        case_id=case["id"],
        template_id=template["id"],
        title="授权通知书",
    )

    pending_resp = client.get(f"{CASE_BASE}/{case['id']}", headers=auth_headers)
    assert pending_resp.status_code == 200, pending_resp.text
    assert pending_resp.json()["status"] == "GRANT_PENDING"

    upload_resp = client.post(
        f"{DOC_BASE}/{document['id']}/attachments",
        headers=auth_headers,
        files={
            "file": (
                "授权通知书.pdf",
                BytesIO(b"%PDF-1.4 demo grant notice attachment"),
                "application/pdf",
            )
        },
    )
    assert upload_resp.status_code == 201, upload_resp.text

    case_resp = client.get(f"{CASE_BASE}/{case['id']}", headers=auth_headers)
    assert case_resp.status_code == 200, case_resp.text
    assert case_resp.json()["status"] == "GRANTED"
