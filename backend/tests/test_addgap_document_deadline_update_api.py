from __future__ import annotations

import json
from datetime import date
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from app.modules.documents.models import Document

DOCUMENT_BASE = "/api/v1/documents"


def _create_case(client: TestClient, auth_headers: dict[str, str]) -> str:
    suffix = uuid4().hex[:8].upper()
    response = client.post(
        "/api/v1/cases",
        headers=auth_headers,
        json={
            "case_no": f"DDL-UPDATE-{suffix}",
            "case_type": "NORMAL",
            "patent_category": "INV",
            "flow_dir": "CN_DOMESTIC",
            "title_cn": f"期限更新接口案件-{suffix}",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def _create_document(
    client: TestClient,
    auth_headers: dict[str, str],
    case_id: str,
    *,
    title: str,
    extra_data: str | None = None,
    deadline: tuple[str, str, str] | None = None,
) -> dict:
    payload = {
        "case_id": case_id,
        "direction": "IN",
        "doc_date": "2026-07-11",
        "title": title,
        "extra_data": extra_data,
    }
    if deadline is not None:
        payload.update(
            {
                "official_due_date": deadline[0],
                "official_due_date_source": deadline[1],
                "official_due_date_status": deadline[2],
            }
        )
    response = client.post(DOCUMENT_BASE, headers=auth_headers, json=payload)
    assert response.status_code == 201, response.text
    return response.json()


def _seed_legacy_document(
    session_factory: sessionmaker,
    case_id: str,
    *,
    title: str,
    due_date: str,
) -> str:
    with session_factory() as db:
        document = Document(
            case_id=case_id,
            direction="IN",
            doc_date=date(2026, 7, 11),
            title=title,
            extra_data=json.dumps(
                {
                    "OfficialDueDate": due_date,
                    "description": "历史说明",
                    "unknown": {"preserved": True},
                },
                ensure_ascii=False,
            ),
        )
        db.add(document)
        db.commit()
        return document.id


def test_put_document_confirms_missing_or_same_legacy_deadline_and_preserves_unknown_data(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    case_id = _create_case(client, auth_headers)
    missing = _create_document(
        client,
        auth_headers,
        case_id,
        title="未设置官方期限",
        extra_data='{"description":"旧说明","unknown":{"keep":true}}',
    )

    missing_response = client.put(
        f"{DOCUMENT_BASE}/{missing['id']}",
        headers=auth_headers,
        json={
            "official_due_date": "2026-10-08",
            "official_due_date_source": "MANUAL_OFFICIAL_NOTICE",
            "official_due_date_status": "CONFIRMED",
            "description": "官方期限已确认",
        },
    )
    assert missing_response.status_code == 200, missing_response.text
    missing_body = missing_response.json()
    assert missing_body["official_due_date"] == "2026-10-08"
    assert missing_body["official_due_date_source"] == "MANUAL_OFFICIAL_NOTICE"
    assert missing_body["official_due_date_status"] == "CONFIRMED"
    assert missing_body["description"] == "官方期限已确认"
    assert json.loads(missing_body["extra_data"])["unknown"] == {"keep": True}

    legacy_id = _seed_legacy_document(
        session_factory,
        case_id,
        title="待确认历史期限",
        due_date="2026-10-20",
    )
    legacy_response = client.put(
        f"{DOCUMENT_BASE}/{legacy_id}",
        headers=auth_headers,
        json={
            "official_due_date": "2026-10-20",
            "official_due_date_source": "IMPORTED_OFFICIAL_NOTICE",
            "official_due_date_status": "CONFIRMED",
        },
    )
    assert legacy_response.status_code == 200, legacy_response.text
    legacy_body = legacy_response.json()
    assert legacy_body["official_due_date"] == "2026-10-20"
    assert legacy_body["official_due_date_source"] == "IMPORTED_OFFICIAL_NOTICE"
    assert legacy_body["official_due_date_status"] == "CONFIRMED"
    assert legacy_body["description"] == "历史说明"
    assert json.loads(legacy_body["extra_data"])["unknown"] == {"preserved": True}

    ordinary_response = client.put(
        f"{DOCUMENT_BASE}/{legacy_id}",
        headers=auth_headers,
        json={"title": "普通编辑保留已确认期限"},
    )
    assert ordinary_response.status_code == 200, ordinary_response.text
    assert ordinary_response.json()["official_due_date"] == "2026-10-20"
    assert ordinary_response.json()["official_due_date_status"] == "CONFIRMED"


def test_put_document_rejects_confirmed_override_and_legacy_date_change(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    case_id = _create_case(client, auth_headers)
    confirmed = _create_document(
        client,
        auth_headers,
        case_id,
        title="已确认期限",
        extra_data='{"unknown":"keep"}',
        deadline=("2026-11-01", "MANUAL_OFFICIAL_NOTICE", "CONFIRMED"),
    )
    conflict_payloads = [
        {"official_due_date": None},
        {"official_due_date_source": None},
        {"official_due_date_status": None},
        {
            "official_due_date": "2026-11-02",
            "official_due_date_source": "MANUAL_OFFICIAL_NOTICE",
            "official_due_date_status": "CONFIRMED",
        },
        {
            "official_due_date": None,
            "official_due_date_source": None,
            "official_due_date_status": None,
        },
        {
            "extra_data": (
                '{"OfficialDueDate":"2026-11-03",'
                '"OfficialDueDateSource":"MANUAL_OFFICIAL_NOTICE",'
                '"OfficialDueDateStatus":"CONFIRMED"}'
            )
        },
    ]
    for payload in conflict_payloads:
        response = client.put(
            f"{DOCUMENT_BASE}/{confirmed['id']}",
            headers=auth_headers,
            json=payload,
        )
        assert response.status_code == 409, response.text
        assert response.json()["error"]["code"] == "DOCUMENT_DEADLINE_OVERRIDE_REQUIRED"

    legacy_id = _seed_legacy_document(
        session_factory,
        case_id,
        title="历史期限不得换日",
        due_date="2026-12-01",
    )
    legacy_change_response = client.put(
        f"{DOCUMENT_BASE}/{legacy_id}",
        headers=auth_headers,
        json={
            "official_due_date": "2026-12-02",
            "official_due_date_source": "IMPORTED_OFFICIAL_NOTICE",
            "official_due_date_status": "CONFIRMED",
        },
    )
    assert legacy_change_response.status_code == 409, legacy_change_response.text
    assert legacy_change_response.json()["error"]["code"] == "DOCUMENT_DEADLINE_OVERRIDE_REQUIRED"

    with session_factory() as db:
        stored_confirmed = db.execute(
            select(Document).where(Document.id == confirmed["id"])
        ).scalar_one()
        stored_legacy = db.execute(select(Document).where(Document.id == legacy_id)).scalar_one()
        assert json.loads(stored_confirmed.extra_data)["OfficialDueDate"] == "2026-11-01"
        assert json.loads(stored_confirmed.extra_data)["unknown"] == "keep"
        assert json.loads(stored_legacy.extra_data)["OfficialDueDate"] == "2026-12-01"


def test_put_document_maps_carrier_shape_and_cross_field_errors_without_writing(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    case_id = _create_case(client, auth_headers)
    document = _create_document(
        client,
        auth_headers,
        case_id,
        title="期限错误映射",
        extra_data='{"unknown":{"keep":true}}',
    )
    invalid_requests = [
        (
            {"official_due_date": "2026-10-08"},
            400,
            "DOCUMENT_DEADLINE_INVALID",
        ),
        (
            {
                "extra_data": (
                    '{"OfficialDueDate":"2026-10-08",'
                    '"OfficialDueDateSource":"MANUAL_OFFICIAL_NOTICE"}'
                )
            },
            400,
            "DOCUMENT_DEADLINE_INVALID",
        ),
        (
            {"extra_data": '{"OfficialDueDate":"2026-10-08"}'},
            400,
            "DOCUMENT_DEADLINE_INVALID",
        ),
        (
            {
                "extra_data": (
                    '{"OfficialDueDate":"2026-99-99",'
                    '"OfficialDueDateSource":"MANUAL_OFFICIAL_NOTICE",'
                    '"OfficialDueDateStatus":"CONFIRMED"}'
                )
            },
            422,
            "DOCUMENT_EXTRA_DATA_INVALID",
        ),
        (
            {
                "official_due_date": "2026-10-08",
                "official_due_date_source": "GUESSED",
                "official_due_date_status": "CONFIRMED",
            },
            422,
            "VALIDATION_ERROR",
        ),
    ]
    for payload, expected_status, expected_code in invalid_requests:
        response = client.put(
            f"{DOCUMENT_BASE}/{document['id']}",
            headers=auth_headers,
            json=payload,
        )
        assert response.status_code == expected_status, response.text
        assert response.json()["error"]["code"] == expected_code

    with session_factory() as db:
        stored = db.execute(select(Document).where(Document.id == document["id"])).scalar_one()
        assert stored.extra_data == '{"unknown":{"keep":true}}'
