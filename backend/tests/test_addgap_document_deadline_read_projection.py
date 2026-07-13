from __future__ import annotations

import json
from datetime import date
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.modules.documents.models import Document

CASE_BASE = "/api/v1/cases"
CLIENT_BASE = "/api/v1/clients"
DOCUMENT_BASE = "/api/v1/documents"
TEMPLATE_BASE = "/api/v1/doc-templates"


def _create_case(client: TestClient, auth_headers: dict[str, str]) -> dict:
    suffix = uuid4().hex[:8].upper()
    client_response = client.post(
        CLIENT_BASE,
        headers=auth_headers,
        json={"client_code": f"DDL-{suffix}", "name_cn": f"期限投影客户-{suffix}"},
    )
    assert client_response.status_code == 201, client_response.text

    case_response = client.post(
        CASE_BASE,
        headers=auth_headers,
        json={
            "case_no": f"DDL-{suffix}",
            "case_type": "NORMAL",
            "patent_category": "INV",
            "flow_dir": "CN_DOMESTIC",
            "client_id": client_response.json()["id"],
            "title_cn": f"期限投影案件-{suffix}",
        },
    )
    assert case_response.status_code == 201, case_response.text
    return case_response.json()


def _get_template(client: TestClient, auth_headers: dict[str, str], code: str) -> dict:
    response = client.get(
        TEMPLATE_BASE,
        headers=auth_headers,
        params={"q": code, "page_size": 100},
    )
    assert response.status_code == 200, response.text
    matches = [item for item in response.json()["items"] if item["code"] == code]
    assert matches, f"template {code} not found"
    return matches[0]


def _assert_projection(
    document: dict,
    *,
    raw: str | None,
    due_date: str | None,
    source: str | None,
    read_status: str | None,
    description: str | None,
) -> None:
    assert document["extra_data"] == raw
    assert document["official_due_date"] == due_date
    assert document["official_due_date_source"] == source
    assert document["official_due_date_status"] == read_status
    assert document["description"] == description


def test_all_document_out_responses_project_structured_and_legacy_extra_data(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    case = _create_case(client, auth_headers)
    canonical_raw = json.dumps(
        {
            "OfficialDueDate": "2026-09-30",
            "OfficialDueDateSource": "MANUAL_OFFICIAL_NOTICE",
            "OfficialDueDateStatus": "CONFIRMED",
            "description": "官方期限已核对",
            "unknown": {"preserved": True},
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    date_only_raw = '{"OfficialDueDate":"2026-10-31","legacy":"kept"}'
    legacy_raw = "历史自由文本说明"
    scenarios = [
        (
            canonical_raw,
            "2026-09-30",
            "MANUAL_OFFICIAL_NOTICE",
            "CONFIRMED",
            "官方期限已核对",
        ),
        (date_only_raw, "2026-10-31", None, "LEGACY_UNVERIFIED", None),
        (legacy_raw, None, None, None, legacy_raw),
        (None, None, None, None, None),
    ]

    created_documents: list[dict] = []
    for index, (raw, due_date, source, read_status, description) in enumerate(scenarios, 1):
        payload = {
            "case_id": case["id"],
            "direction": "IN",
            "doc_date": f"2026-07-{index:02d}",
            "title": f"期限投影文件-{index}",
            "extra_data": raw,
        }
        if read_status == "LEGACY_UNVERIFIED":
            rejected = client.post(
                DOCUMENT_BASE,
                headers=auth_headers,
                json=payload,
            )
            assert rejected.status_code == 400, rejected.text
            assert rejected.json()["error"]["code"] == "DOCUMENT_DEADLINE_INVALID"

            document_id = str(uuid4())
            with session_factory() as db:
                db.add(
                    Document(
                        id=document_id,
                        case_id=case["id"],
                        direction="IN",
                        doc_date=date(2026, 7, index),
                        title=payload["title"],
                        extra_data=raw,
                    )
                )
                db.commit()
            response = client.get(f"{DOCUMENT_BASE}/{document_id}", headers=auth_headers)
            expected_status = 200
        else:
            response = client.post(
                DOCUMENT_BASE,
                headers=auth_headers,
                json=payload,
            )
            expected_status = 201
        assert response.status_code == expected_status, response.text
        created = response.json()
        _assert_projection(
            created,
            raw=raw,
            due_date=due_date,
            source=source,
            read_status=read_status,
            description=description,
        )
        created_documents.append(created)

    detail_response = client.get(
        f"{DOCUMENT_BASE}/{created_documents[0]['id']}", headers=auth_headers
    )
    assert detail_response.status_code == 200, detail_response.text
    _assert_projection(
        detail_response.json(),
        raw=canonical_raw,
        due_date="2026-09-30",
        source="MANUAL_OFFICIAL_NOTICE",
        read_status="CONFIRMED",
        description="官方期限已核对",
    )

    list_response = client.get(
        DOCUMENT_BASE,
        headers=auth_headers,
        params={"case_id": case["id"], "page_size": 100},
    )
    assert list_response.status_code == 200, list_response.text
    listed_by_id = {item["id"]: item for item in list_response.json()["items"]}
    for created, (raw, due_date, source, read_status, description) in zip(
        created_documents, scenarios, strict=True
    ):
        _assert_projection(
            listed_by_id[created["id"]],
            raw=raw,
            due_date=due_date,
            source=source,
            read_status=read_status,
            description=description,
        )

    updated_raw = (
        '{"OfficialDueDate":"2026-11-30",'
        '"OfficialDueDateSource":"IMPORTED_OFFICIAL_NOTICE",'
        '"OfficialDueDateStatus":"NEEDS_CONFIRMATION"}'
    )
    update_response = client.put(
        f"{DOCUMENT_BASE}/{created_documents[3]['id']}",
        headers=auth_headers,
        json={"extra_data": updated_raw},
    )
    assert update_response.status_code == 200, update_response.text
    _assert_projection(
        update_response.json(),
        raw=updated_raw,
        due_date="2026-11-30",
        source="IMPORTED_OFFICIAL_NOTICE",
        read_status="NEEDS_CONFIRMATION",
        description=None,
    )

    template = _get_template(client, auth_headers, "CLIENT_IN")
    wizard_response = client.post(
        f"{DOCUMENT_BASE}/wizard/batch-create",
        headers=auth_headers,
        json={
            "defaults": {
                "doc_template_id": template["id"],
                "direction": "IN",
                "doc_date": "2026-07-15",
                "extra_data": canonical_raw,
            },
            "rows": [{"case_id": case["id"], "title": "批量期限投影文件"}],
        },
    )
    assert wizard_response.status_code == 201, wizard_response.text
    wizard_document = wizard_response.json()["items"][0]["document"]
    _assert_projection(
        wizard_document,
        raw=canonical_raw,
        due_date="2026-09-30",
        source="MANUAL_OFFICIAL_NOTICE",
        read_status="CONFIRMED",
        description="官方期限已核对",
    )
