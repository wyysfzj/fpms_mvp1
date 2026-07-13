from __future__ import annotations

import json
from datetime import date
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from app.modules.documents.models import DocTemplate, Document
from app.modules.documents.official_notice_catalog import (
    seed_oa_acceptance_official_notice_catalog,
)


def _create_case(client: TestClient, auth_headers: dict[str, str]) -> dict:
    response = client.post(
        "/api/v1/cases",
        headers=auth_headers,
        json={
            "case_no": f"ADDGAP-OA-ALIAS-REPLY-{uuid4().hex[:8].upper()}",
            "case_type": "NORMAL",
            "patent_category": "INV",
            "flow_dir": "CN_DOMESTIC",
            "title_cn": "OA 别名答复校验测试案件",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def _template_id(session_factory: sessionmaker, code: str) -> str:
    with session_factory() as db:
        return db.execute(select(DocTemplate.id).where(DocTemplate.code == code)).scalar_one()


def _activate_catalog(session_factory: sessionmaker) -> None:
    with session_factory() as db:
        seed_oa_acceptance_official_notice_catalog(db)
        db.commit()


def _create_oa_source(
    client: TestClient,
    auth_headers: dict[str, str],
    *,
    case_id: str,
    template_id: str,
    title: str,
) -> dict:
    response = client.post(
        "/api/v1/documents",
        headers=auth_headers,
        json={
            "case_id": case_id,
            "doc_template_id": template_id,
            "direction": "IN",
            "doc_date": "2026-07-11",
            "title": title,
            "official_due_date": "2026-10-11",
            "official_due_date_source": "MANUAL_OFFICIAL_NOTICE",
            "official_due_date_status": "CONFIRMED",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def _create_source_record(
    session_factory: sessionmaker,
    *,
    case_id: str,
    template_id: str,
    title: str,
) -> str:
    with session_factory() as db:
        source = Document(
            case_id=case_id,
            doc_template_id=template_id,
            direction="IN",
            doc_date=date(2026, 7, 11),
            title=title,
        )
        db.add(source)
        db.commit()
        return source.id


def _reply(
    client: TestClient,
    auth_headers: dict[str, str],
    *,
    case_id: str,
    oa_out_template_id: str,
    source_document_id: str,
) -> object:
    return client.post(
        "/api/v1/documents",
        headers=auth_headers,
        json={
            "case_id": case_id,
            "doc_template_id": oa_out_template_id,
            "direction": "OUT",
            "doc_date": "2026-08-01",
            "title": "OA 答复文件",
            "reply_to_id": source_document_id,
        },
    )


def test_oa_out_accepts_executable_oa_alias_and_literal_oa_in(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    _activate_catalog(session_factory)
    oa_out_id = _template_id(session_factory, "OA_OUT")
    alias_template_ids = [
        _template_id(session_factory, "OFFICIAL_NOTICE_003"),
        _template_id(session_factory, "OFFICIAL_NOTICE_005"),
    ]

    for index, source_template_id in enumerate(alias_template_ids, start=1):
        case = _create_case(client, auth_headers)
        source_id = _create_source_record(
            session_factory,
            case_id=case["id"],
            template_id=source_template_id,
            title=f"OA 别名来源-{index}",
        )

        response = _reply(
            client,
            auth_headers,
            case_id=case["id"],
            oa_out_template_id=oa_out_id,
            source_document_id=source_id,
        )

        assert response.status_code == 201, response.text
        assert response.json()["reply_to_id"] == source_id

    literal_case = _create_case(client, auth_headers)
    literal_source = _create_oa_source(
        client,
        auth_headers,
        case_id=literal_case["id"],
        template_id=_template_id(session_factory, "OA_IN"),
        title="literal OA_IN 来源",
    )
    literal_response = _reply(
        client,
        auth_headers,
        case_id=literal_case["id"],
        oa_out_template_id=oa_out_id,
        source_document_id=literal_source["id"],
    )

    assert literal_response.status_code == 201, literal_response.text
    tasks = client.get(
        "/api/v1/tasks",
        headers=auth_headers,
        params={"case_id": literal_case["id"], "page_size": 100},
    )
    assert tasks.status_code == 200, tasks.text
    assert [item["status"] for item in tasks.json()["items"]] == ["OPEN"]


def test_oa_out_rejects_reference_only_and_executable_non_oa_aliases(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    _activate_catalog(session_factory)
    oa_out_id = _template_id(session_factory, "OA_OUT")

    for template_code in ("OFFICIAL_NOTICE_002", "OFFICIAL_NOTICE_001"):
        case = _create_case(client, auth_headers)
        source_id = _create_source_record(
            session_factory,
            case_id=case["id"],
            template_id=_template_id(session_factory, template_code),
            title=f"非 OA 来源-{template_code}",
        )

        response = _reply(
            client,
            auth_headers,
            case_id=case["id"],
            oa_out_template_id=oa_out_id,
            source_document_id=source_id,
        )

        assert response.status_code == 400, response.text
        assert response.json()["error"]["code"] == "REPLY_TO_TEMPLATE_MISMATCH"


def test_oa_out_propagates_alias_semantics_conflict(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    _activate_catalog(session_factory)
    case = _create_case(client, auth_headers)
    with session_factory() as db:
        conflicting_template = DocTemplate(
            code=f"OA_ALIAS_CONFLICT_{uuid4().hex[:8].upper()}",
            name="OA 别名方向冲突模板",
            direction="OUT",
            enabled=True,
            status_effect="OA1",
            deadline_template_code="OA_REPLY",
            need_reply=True,
            input_fields=json.dumps(
                {
                    "archive_status_restore": "SUB_EXAM",
                    "canonical_template_code": "OA_IN",
                    "catalog_kind": "OFFICIAL_NOTICE",
                    "catalog_status": "EXECUTABLE",
                    "completion_event": "OFFICIAL_RECEIPT_ARCHIVED",
                    "deadline_source_policy": "EXPLICIT_OFFICIAL_DUE_REQUIRED",
                    "execution_behavior": "OA_REPLY",
                }
            ),
        )
        db.add(conflicting_template)
        db.commit()
        source_id = _create_source_record(
            session_factory,
            case_id=case["id"],
            template_id=conflicting_template.id,
            title="OA 别名方向冲突来源",
        )

    response = _reply(
        client,
        auth_headers,
        case_id=case["id"],
        oa_out_template_id=_template_id(session_factory, "OA_OUT"),
        source_document_id=source_id,
    )

    assert response.status_code == 409, response.text
    assert response.json()["error"]["code"] == "DOCUMENT_SEMANTICS_CONFLICT"
