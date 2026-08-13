from __future__ import annotations

import json
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from app.modules.documents.models import DocTemplate
from app.modules.fees.models import FeeDraft, FeeItem


def _create_case(client: TestClient, auth_headers: dict[str, str]) -> dict:
    response = client.post(
        "/api/v1/cases",
        headers=auth_headers,
        json={
            "case_no": f"ADDGAP-GRANT-DRAFT-{uuid4().hex[:8].upper()}",
            "case_type": "NORMAL",
            "patent_category": "INV",
            "flow_dir": "CN_DOMESTIC",
            "fee_reduction": "0",
            "title_cn": "授权自动草单门禁测试案件",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def _create_template(
    session_factory: sessionmaker,
    *,
    executable_grant: bool,
) -> str:
    with session_factory() as db:
        suffix = uuid4().hex[:8].upper()
        if executable_grant:
            template = DocTemplate(
                id=str(uuid4()),
                code=f"GRANT_GATE_ALIAS_{suffix}",
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
        else:
            template = DocTemplate(
                id=str(uuid4()),
                code=f"CUSTOM_FEE_{suffix}",
                name="普通费用文档",
                direction="IN",
                fee_draft_type="CUSTOM_FEE",
                fee_item_list=json.dumps(
                    [
                        {
                            "fee_code": "CUSTOM_SERVICE",
                            "fee_name": "普通服务费",
                            "fee_type": "SERVICE",
                            "amount": "125.00",
                        }
                    ],
                    ensure_ascii=False,
                ),
            )
        db.add(template)
        db.commit()
        return template.id


def test_executable_grant_registration_does_not_auto_create_generic_draft(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    case = _create_case(client, auth_headers)
    template_id = _create_template(session_factory, executable_grant=True)

    response = client.post(
        "/api/v1/documents",
        headers=auth_headers,
        json={
            "case_id": case["id"],
            "doc_template_id": template_id,
            "direction": "IN",
            "doc_date": "2026-07-11",
            "title": "授权通知书",
            "official_due_date": "2026-08-28",
            "official_due_date_source": "MANUAL_OFFICIAL_NOTICE",
            "official_due_date_status": "CONFIRMED",
        },
    )

    assert response.status_code == 201, response.text
    assert response.headers.get("X-Auto-Fee-Draft-Created") is None
    with session_factory() as db:
        drafts = list(
            db.execute(select(FeeDraft).where(FeeDraft.case_id == case["id"])).scalars().all()
        )
        assert drafts == []


def test_malformed_canonical_grant_registration_fails_closed_without_generic_draft(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    case = _create_case(client, auth_headers)
    with session_factory() as db:
        template = db.execute(
            select(DocTemplate).where(DocTemplate.code == "GRANT_NOTICE")
        ).scalar_one()
        template.input_fields = "{malformed-system-metadata"
        template.fee_draft_type = "GRANT_FEE"
        template_id = template.id
        db.commit()

    response = client.post(
        "/api/v1/documents",
        headers=auth_headers,
        json={
            "case_id": case["id"],
            "doc_template_id": template_id,
            "direction": "IN",
            "doc_date": "2026-07-11",
            "title": "元数据损坏的授权通知书",
            "official_due_date": "2026-08-28",
            "official_due_date_source": "MANUAL_OFFICIAL_NOTICE",
            "official_due_date_status": "CONFIRMED",
        },
    )

    assert response.status_code == 201, response.text
    assert response.headers.get("X-Auto-Fee-Draft-Created") is None
    with session_factory() as db:
        drafts = list(
            db.execute(select(FeeDraft).where(FeeDraft.case_id == case["id"])).scalars().all()
        )
        assert drafts == []


def test_non_grant_b3_fee_linking_remains_unchanged(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    case = _create_case(client, auth_headers)
    template_id = _create_template(session_factory, executable_grant=False)

    response = client.post(
        "/api/v1/documents",
        headers=auth_headers,
        json={
            "case_id": case["id"],
            "doc_template_id": template_id,
            "direction": "IN",
            "doc_date": "2026-07-11",
            "title": "普通费用文档",
        },
    )

    assert response.status_code == 201, response.text
    draft_id = response.headers.get("X-Auto-Fee-Draft-Created")
    assert draft_id is not None
    with session_factory() as db:
        draft = db.get(FeeDraft, draft_id)
        assert draft is not None
        assert draft.draft_type == "CUSTOM_FEE"
        assert draft.total_service == 125
        assert draft.amount == 125
        items = list(
            db.execute(select(FeeItem).where(FeeItem.draft_id == draft_id)).scalars().all()
        )
        assert len(items) == 1
        assert items[0].fee_code == "CUSTOM_SERVICE"
        assert items[0].amount == 125
