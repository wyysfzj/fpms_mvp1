from __future__ import annotations

import json

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from app.modules.documents.models import DocTemplate
from scripts.seed_dev import seed_doc_templates

BASE = "/api/v1/doc-templates"


def test_seed_doc_templates_imports_customer_official_notice_catalog(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as db:
        seed_doc_templates(db)

        rows = (
            db.execute(
                select(DocTemplate)
                .where(DocTemplate.code.like("OFFICIAL_NOTICE_%"))
                .order_by(DocTemplate.code.asc())
            )
            .scalars()
            .all()
        )

        assert len(rows) == 60

        by_name = {row.name: row for row in rows}
        assert json.loads(by_name["受理通知-电子"].input_fields or "{}")["official_doc_codes"] == [
            "200101"
        ]
        assert json.loads(by_name["补正通知"].input_fields or "{}")["official_doc_codes"] == [
            "220704",
            "200029",
            "210302",
            "220302",
            "230301",
        ]
        assert json.loads(by_name["第一次审查意见通知书"].input_fields or "{}")[
            "official_doc_codes"
        ] == ["210401", "210402"]
        assert json.loads(by_name["授权通知书-电子"].input_fields or "{}")[
            "official_doc_codes"
        ] == ["200602"]
        assert json.loads(by_name["驳回决定"].input_fields or "{}")["official_doc_codes"] == [
            "210407",
            "200305",
            "210408",
        ]
        assert json.loads(by_name["年费缴费通知书"].input_fields or "{}")["official_doc_codes"] == [
            "200701"
        ]
        assert json.loads(by_name["复审通知书"].input_fields or "{}")["official_doc_codes"] == [
            "200908A",
            "200924",
        ]
        assert (
            json.loads(by_name["PCT电子提交收据"].input_fields or "{}")["official_doc_codes"] == []
        )


def test_doc_template_search_matches_official_doc_code_in_input_fields(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    create_resp = client.post(
        BASE,
        headers=auth_headers,
        json={
            "code": "OFFICIAL_NOTICE_SEARCH_PROBE",
            "name": "内部官文检索探针",
            "direction": "IN",
            "input_fields": json.dumps(
                {
                    "source": "相关流程操作-20260526 TABLE 001",
                    "official_doc_codes": ["200029"],
                },
                ensure_ascii=False,
            ),
        },
    )
    assert create_resp.status_code == 201, create_resp.text

    resp = client.get(BASE, headers=auth_headers, params={"q": "200029", "page_size": 100})

    assert resp.status_code == 200, resp.text
    assert any(item["code"] == "OFFICIAL_NOTICE_SEARCH_PROBE" for item in resp.json()["items"])
