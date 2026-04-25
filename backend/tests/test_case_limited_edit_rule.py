from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient


def _case_no() -> str:
    return f"A10_{uuid4().hex[:10]}"


def _create_case(client: TestClient, auth_headers: dict[str, str]) -> dict:
    response = client.post(
        "/api/v1/cases",
        json={
            "case_no": _case_no(),
            "case_type": "NORMAL",
            "patent_category": "INV",
            "flow_dir": "CN_DOMESTIC",
            "from_country": "CN",
            "title_cn": "限制修改原始标题",
            "title_en": "Limited Edit Original",
            "recv_date": "2026-04-01",
            "applicants": [
                {
                    "seq": 1,
                    "is_first": True,
                    "name_cn": "限制修改申请人",
                }
            ],
            "inventors": [{"seq": 1, "name_cn": "原始发明人"}],
        },
        headers=auth_headers,
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_limited_edit_updates_whitelist_and_preserves_blacklist(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    created = _create_case(client, auth_headers)
    case_id = created["id"]

    response = client.post(
        f"/api/v1/cases/{case_id}/limited-edit",
        json={
            "title_cn": "限制修改新标题",
            "title_en": "Limited Edit Updated",
            "spec_pages": 18,
            "draw_pages": 3,
            "claim_count": 12,
            "claim_pages": 4,
            "manuscript_words": 3456,
            "inventors": [
                {"seq": 1, "name_cn": "新发明人一"},
                {"seq": 2, "name_cn": "新发明人二", "name_en": "Inventor Two"},
            ],
            "case_no": "SHOULD_NOT_CHANGE",
            "status": "PUBLISHED",
            "filing_date": "2026-04-02",
            "app_no": "APP-SHOULD-NOT-CHANGE",
            "client_id": str(uuid4()),
        },
        headers=auth_headers,
    )

    assert response.status_code == 200, response.text
    detail = response.json()
    assert detail["id"] == case_id
    assert detail["title_cn"] == "限制修改新标题"
    assert detail["title_en"] == "Limited Edit Updated"
    assert detail["spec_pages"] == 18
    assert detail["draw_pages"] == 3
    assert detail["claim_count"] == 12
    assert detail["claim_pages"] == 4
    assert detail["manuscript_words"] == 3456
    assert [row["name_cn"] for row in detail["inventors"]] == ["新发明人一", "新发明人二"]

    assert detail["case_no"] == created["case_no"]
    assert detail["status"] == "NOT_FILED"
    assert detail["filing_date"] is None
    assert detail["app_no"] is None
    assert detail["client_id"] == created["client_id"]
    assert detail["updated_at"] is not None


def test_limited_edit_missing_case_uses_existing_error(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    response = client.post(
        f"/api/v1/cases/{uuid4()}/limited-edit",
        json={"title_cn": "不存在"},
        headers=auth_headers,
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "CASE_NOT_FOUND"
