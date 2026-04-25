from __future__ import annotations

import json
from decimal import Decimal
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from app.modules.fees.models import FeeDraft, FeeItem

BASE = "/api/v1/documents/wizard/fee-preview"
CASE_BASE = "/api/v1/cases"
DOC_TMPL_BASE = "/api/v1/doc-templates"


def _unique_case_no() -> str:
    return f"WZF-{uuid4().hex[:8].upper()}"


def _create_applicant(client: TestClient, auth_headers: dict[str, str]) -> dict:
    suffix = uuid4().hex[:8].upper()
    resp = client.post(
        "/api/v1/applicants",
        headers=auth_headers,
        json={
            "code": f"WZF-AP-{suffix}",
            "name_cn": f"Wizard费用预览申请人-{suffix}",
            "applicant_type": "ENTITY",
            "is_active": True,
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def _create_case(client: TestClient, auth_headers: dict[str, str]) -> dict:
    applicant = _create_applicant(client, auth_headers)
    resp = client.post(
        CASE_BASE,
        headers=auth_headers,
        json={
            "case_no": _unique_case_no(),
            "case_type": "NORMAL",
            "patent_category": "INV",
            "flow_dir": "CN_DOMESTIC",
            "title_cn": "Wizard Fee Preview Case",
            "applicants": [
                {
                    "seq": 1,
                    "is_first": True,
                    "applicant_id": applicant["id"],
                    "name_cn": applicant["name_cn"],
                }
            ],
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def _create_fee_template(client: TestClient, auth_headers: dict) -> dict:
    code = f"FEE_{uuid4().hex[:8].upper()}"
    resp = client.post(
        DOC_TMPL_BASE,
        headers=auth_headers,
        json={
            "code": code,
            "name": f"费用预览模板 {code}",
            "direction": "IN",
            "enabled": True,
            "fee_draft_type": "CUSTOM_FEE",
            "fee_item_list": json.dumps(
                [
                    {
                        "code": "FEE-A",
                        "name": "项目 A",
                        "fee_type": "SERVICE",
                        "quantity": 2,
                        "unit_price": "120.50",
                        "amount": "241.00",
                        "description": "项目 A 说明",
                    },
                    {
                        "code": "FEE-B",
                        "fee_name": "项目 B",
                        "fee_type": "GOV",
                        "amount": 88,
                    },
                ],
                ensure_ascii=False,
            ),
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def _preview_fee_candidates(
    client: TestClient,
    auth_headers: dict[str, str],
    *,
    template_id: str,
    case_id: str,
    title: str,
) -> dict:
    resp = client.post(
        BASE,
        headers=auth_headers,
        json={
            "defaults": {
                "doc_template_id": template_id,
                "direction": "IN",
                "doc_date": "2026-01-15",
            },
            "rows": [{"case_id": case_id, "title": title}],
        },
    )
    assert resp.status_code == 200, resp.text
    return resp.json()


def test_document_wizard_fee_preview_success(
    client: TestClient, auth_headers: dict, session_factory: sessionmaker
) -> None:
    case = _create_case(client, auth_headers)
    template = _create_fee_template(client, auth_headers)

    payload = _preview_fee_candidates(
        client,
        auth_headers,
        template_id=template["id"],
        case_id=case["id"],
        title="费用预览文书",
    )

    assert payload["total_candidates"] == 1
    item = payload["items"][0]
    assert item["row_index"] == 1
    assert item["case_id"] == case["id"]
    assert item["case_no"] == case["case_no"]
    assert item["source_title"] == "Wizard Fee Preview Case"
    assert item["document_title"] == "费用预览文书"
    assert item["fee_draft_type"] == "CUSTOM_FEE"
    assert item["skip_this_candidate"] is False
    assert len(item["fee_items"]) == 2

    first_item = item["fee_items"][0]
    assert first_item["fee_code"] == "FEE-A"
    assert first_item["fee_name"] == "项目 A"
    assert first_item["fee_type"] == "SERVICE"
    assert Decimal(str(first_item["quantity"])) == Decimal("2")
    assert Decimal(str(first_item["unit_price"])) == Decimal("120.50")
    assert Decimal(str(first_item["amount"])) == Decimal("241.00")
    assert first_item["remark"] == "项目 A 说明"

    second_item = item["fee_items"][1]
    assert second_item["fee_code"] == "FEE-B"
    assert second_item["fee_name"] == "项目 B"
    assert second_item["fee_type"] == "GOV"
    assert second_item["remark"] is None

    with session_factory() as db:
        fee_drafts = (
            db.execute(select(FeeDraft).where(FeeDraft.case_id == case["id"])).scalars().all()
        )
        fee_items = (
            db.execute(
                select(FeeItem)
                .join(FeeDraft, FeeDraft.id == FeeItem.draft_id)
                .where(FeeDraft.case_id == case["id"])
            )
            .scalars()
            .all()
        )
        assert fee_drafts == []
        assert fee_items == []


def test_document_wizard_fee_preview_returns_empty_for_template_without_fee_type(
    client: TestClient, auth_headers: dict, session_factory: sessionmaker
) -> None:
    case = _create_case(client, auth_headers)

    resp = client.get(
        DOC_TMPL_BASE,
        headers=auth_headers,
        params={"q": "CLIENT_IN", "page_size": 100},
    )
    assert resp.status_code == 200, resp.text
    template_items = resp.json()["items"]
    template = next(item for item in template_items if item["code"] == "CLIENT_IN")

    payload = _preview_fee_candidates(
        client,
        auth_headers,
        template_id=template["id"],
        case_id=case["id"],
        title="普通来函",
    )

    assert payload["total_candidates"] == 0
    assert payload["items"] == []

    with session_factory() as db:
        fee_drafts = (
            db.execute(select(FeeDraft).where(FeeDraft.case_id == case["id"])).scalars().all()
        )
        fee_items = (
            db.execute(
                select(FeeItem)
                .join(FeeDraft, FeeDraft.id == FeeItem.draft_id)
                .where(FeeDraft.case_id == case["id"])
            )
            .scalars()
            .all()
        )
        assert fee_drafts == []
        assert fee_items == []
