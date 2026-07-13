from __future__ import annotations

import json
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from app.modules.documents.models import Document

DOCUMENT_BASE = "/api/v1/documents"


def test_post_document_persists_canonical_deadline_and_rejects_invalid_writes(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    suffix = uuid4().hex[:8].upper()
    case_response = client.post(
        "/api/v1/cases",
        headers=auth_headers,
        json={
            "case_no": f"DDL-CREATE-{suffix}",
            "case_type": "NORMAL",
            "patent_category": "INV",
            "flow_dir": "CN_DOMESTIC",
            "title_cn": f"期限创建接口案件-{suffix}",
        },
    )
    assert case_response.status_code == 201, case_response.text
    case_id = case_response.json()["id"]

    raw_extra_data = json.dumps(
        {
            "description": "旧说明",
            "unknown": {"preserved": True},
        },
        ensure_ascii=False,
    )
    create_response = client.post(
        DOCUMENT_BASE,
        headers=auth_headers,
        json={
            "case_id": case_id,
            "direction": "IN",
            "doc_date": "2026-07-11",
            "title": "含官方期限的收文",
            "extra_data": raw_extra_data,
            "official_due_date": "2026-10-08",
            "official_due_date_source": "MANUAL_OFFICIAL_NOTICE",
            "official_due_date_status": "CONFIRMED",
            "description": "官方期限已确认",
        },
    )

    assert create_response.status_code == 201, create_response.text
    body = create_response.json()
    expected_extra_data = (
        '{"OfficialDueDate":"2026-10-08",'
        '"OfficialDueDateSource":"MANUAL_OFFICIAL_NOTICE",'
        '"OfficialDueDateStatus":"CONFIRMED",'
        '"description":"官方期限已确认",'
        '"unknown":{"preserved":true}}'
    )
    assert body["extra_data"] == expected_extra_data
    assert body["official_due_date"] == "2026-10-08"
    assert body["official_due_date_source"] == "MANUAL_OFFICIAL_NOTICE"
    assert body["official_due_date_status"] == "CONFIRMED"
    assert body["description"] == "官方期限已确认"

    needs_confirmation_response = client.post(
        DOCUMENT_BASE,
        headers=auth_headers,
        json={
            "case_id": case_id,
            "direction": "IN",
            "doc_date": "2026-07-11",
            "title": "待确认官方期限",
            "official_due_date": "2026-10-09",
            "official_due_date_source": "IMPORTED_OFFICIAL_NOTICE",
            "official_due_date_status": "NEEDS_CONFIRMATION",
        },
    )
    assert needs_confirmation_response.status_code == 201, needs_confirmation_response.text
    assert needs_confirmation_response.json()["official_due_date_status"] == "NEEDS_CONFIRMATION"

    with session_factory() as db:
        stored = db.execute(select(Document).where(Document.id == body["id"])).scalar_one()
        assert stored.extra_data == expected_extra_data

    incomplete_response = client.post(
        DOCUMENT_BASE,
        headers=auth_headers,
        json={
            "case_id": case_id,
            "direction": "IN",
            "doc_date": "2026-07-12",
            "title": "缺少期限来源和确认状态",
            "official_due_date": "2026-10-09",
        },
    )
    assert incomplete_response.status_code == 400, incomplete_response.text
    assert incomplete_response.json()["error"]["code"] == "DOCUMENT_DEADLINE_INVALID"

    legacy_write_response = client.post(
        DOCUMENT_BASE,
        headers=auth_headers,
        json={
            "case_id": case_id,
            "direction": "IN",
            "doc_date": "2026-07-13",
            "title": "不得写入只读期限状态",
            "official_due_date": "2026-10-10",
            "official_due_date_source": "IMPORTED_OFFICIAL_NOTICE",
            "official_due_date_status": "LEGACY_UNVERIFIED",
        },
    )
    assert legacy_write_response.status_code == 422, legacy_write_response.text
    assert legacy_write_response.json()["error"]["code"] == "VALIDATION_ERROR"

    with session_factory() as db:
        invalid_documents = (
            db.execute(
                select(Document).where(
                    Document.case_id == case_id,
                    Document.title.in_(
                        [
                            "缺少期限来源和确认状态",
                            "不得写入只读期限状态",
                        ]
                    ),
                )
            )
            .scalars()
            .all()
        )
        assert invalid_documents == []


def test_post_document_validates_raw_deadline_carrier_without_rewriting_legacy_text(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    suffix = uuid4().hex[:8].upper()
    case_response = client.post(
        "/api/v1/cases",
        headers=auth_headers,
        json={
            "case_no": f"DDL-RAW-{suffix}",
            "case_type": "NORMAL",
            "patent_category": "INV",
            "flow_dir": "CN_DOMESTIC",
            "title_cn": f"原始期限载体案件-{suffix}",
        },
    )
    assert case_response.status_code == 201, case_response.text
    case_id = case_response.json()["id"]

    invalid_requests = [
        (
            "不得通过原始载体写入只读期限",
            '{"OfficialDueDate":"2026-10-10"}',
            400,
            "DOCUMENT_DEADLINE_INVALID",
        ),
        (
            "原始载体期限三元组不完整",
            ('{"OfficialDueDate":"2026-10-11","OfficialDueDateSource":"MANUAL_OFFICIAL_NOTICE"}'),
            400,
            "DOCUMENT_DEADLINE_INVALID",
        ),
        (
            "原始载体期限格式错误",
            (
                '{"OfficialDueDate":"2026-99-99",'
                '"OfficialDueDateSource":"MANUAL_OFFICIAL_NOTICE",'
                '"OfficialDueDateStatus":"CONFIRMED"}'
            ),
            422,
            "DOCUMENT_EXTRA_DATA_INVALID",
        ),
    ]
    for title, extra_data, expected_status, expected_code in invalid_requests:
        response = client.post(
            DOCUMENT_BASE,
            headers=auth_headers,
            json={
                "case_id": case_id,
                "direction": "IN",
                "doc_date": "2026-07-12",
                "title": title,
                "extra_data": extra_data,
            },
        )
        assert response.status_code == expected_status, response.text
        assert response.json()["error"]["code"] == expected_code

    confirmed_raw = (
        '{"OfficialDueDate":"2026-10-12",'
        '"OfficialDueDateSource":"MANUAL_OFFICIAL_NOTICE",'
        '"OfficialDueDateStatus":"CONFIRMED","unknown":true}'
    )
    confirmed_response = client.post(
        DOCUMENT_BASE,
        headers=auth_headers,
        json={
            "case_id": case_id,
            "direction": "IN",
            "doc_date": "2026-07-13",
            "title": "完整原始期限载体",
            "extra_data": confirmed_raw,
        },
    )
    assert confirmed_response.status_code == 201, confirmed_response.text
    assert confirmed_response.json()["extra_data"] == confirmed_raw
    assert confirmed_response.json()["official_due_date_status"] == "CONFIRMED"

    legacy_text = "历史自由文本说明"
    legacy_response = client.post(
        DOCUMENT_BASE,
        headers=auth_headers,
        json={
            "case_id": case_id,
            "direction": "IN",
            "doc_date": "2026-07-14",
            "title": "历史文本保持原样",
            "extra_data": legacy_text,
        },
    )
    assert legacy_response.status_code == 201, legacy_response.text
    assert legacy_response.json()["extra_data"] == legacy_text
    assert legacy_response.json()["description"] == legacy_text

    with session_factory() as db:
        invalid_documents = (
            db.execute(
                select(Document).where(
                    Document.case_id == case_id,
                    Document.title.in_([request[0] for request in invalid_requests]),
                )
            )
            .scalars()
            .all()
        )
        assert invalid_documents == []
