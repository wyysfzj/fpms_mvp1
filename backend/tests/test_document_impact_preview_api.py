from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient

from app.modules.cases.models import Case


def _create_applicant(client: TestClient, auth_headers: dict[str, str]) -> dict:
    suffix = uuid4().hex[:8].upper()
    response = client.post(
        "/api/v1/applicants",
        headers=auth_headers,
        json={
            "code": f"DOC-IMPACT-AP-{suffix}",
            "name_cn": f"文件影响申请人-{suffix}",
            "applicant_type": "ENTITY",
            "is_active": True,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def _create_case(client: TestClient, auth_headers: dict[str, str]) -> dict:
    applicant = _create_applicant(client, auth_headers)
    response = client.post(
        "/api/v1/cases",
        headers=auth_headers,
        json={
            "case_no": f"DOC-IMPACT-{uuid4().hex[:8].upper()}",
            "case_type": "NORMAL",
            "patent_category": "INV",
            "flow_dir": "CN_DOMESTIC",
            "title_cn": "文件影响预览测试案件",
            "status": "NOT_FILED",
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
    assert response.status_code == 201, response.text
    return response.json()


def _get_template(client: TestClient, auth_headers: dict[str, str], code: str) -> dict:
    response = client.get(
        "/api/v1/doc-templates",
        headers=auth_headers,
        params={"q": code, "page_size": 100},
    )
    assert response.status_code == 200, response.text
    matches = [item for item in response.json()["items"] if item["code"] == code]
    assert matches, f"template {code} not found"
    return matches[0]


def _create_document(
    client: TestClient,
    auth_headers: dict[str, str],
    *,
    case_id: str,
    template_id: str,
    direction: str,
    title: str,
) -> dict:
    response = client.post(
        "/api/v1/documents",
        headers=auth_headers,
        json={
            "case_id": case_id,
            "doc_template_id": template_id,
            "doc_type": "OFFICIAL_IN" if direction == "IN" else "OFFICIAL_OUT",
            "direction": direction,
            "doc_date": "2026-04-02",
            "title": title,
            "official_due_date": "2026-07-02",
            "official_due_date_source": "MANUAL_OFFICIAL_NOTICE",
            "official_due_date_status": "CONFIRMED",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_document_impact_preview_requires_auth(client: TestClient) -> None:
    response = client.post(
        "/api/v1/documents/impact-preview",
        json={
            "case_id": "missing",
            "direction": "IN",
            "doc_date": "2026-04-02",
            "title": "未授权文件",
        },
    )

    assert response.status_code == 401


def test_document_impact_preview_returns_template_impacts_without_mutating_case(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory,
) -> None:
    case_data = _create_case(client, auth_headers)
    template = _get_template(client, auth_headers, "OA_IN")

    response = client.post(
        "/api/v1/documents/impact-preview",
        headers=auth_headers,
        json={
            "case_id": case_data["id"],
            "doc_template_id": template["id"],
            "doc_type": "OFFICIAL_IN",
            "direction": "IN",
            "doc_date": "2026-04-02",
            "title": "第一次审查意见通知书",
            "official_due_date": "2026-07-02",
            "official_due_date_source": "MANUAL_OFFICIAL_NOTICE",
            "official_due_date_status": "CONFIRMED",
        },
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["case_id"] == case_data["id"]
    assert payload["template_code"] == "OA_IN"
    assert payload["confirmation_required"] is True
    assert payload["status_impacts"][0]["kind"] == "CASE_STATUS"
    assert payload["status_impacts"][0]["effect"] == "OA1"
    official_due_impact = next(
        impact for impact in payload["deadline_impacts"] if impact["kind"] == "OFFICIAL_DUE_DATE"
    )
    assert official_due_impact["effect"] == "2026-07-02"
    assert "MANUAL_OFFICIAL_NOTICE" in official_due_impact["detail"]
    assert "CONFIRMED" in official_due_impact["detail"]
    assert payload["task_impacts"][0]["kind"] == "AUTO_TASK"
    assert payload["task_impacts"][0]["effect"] == "OA_REPLY"
    assert payload["fee_impacts"] == []
    assert "案件状态将受模板影响" in payload["confirmation_items"]

    with session_factory() as db:
        case = db.query(Case).filter(Case.id == case_data["id"]).one()
        assert case.status == "NOT_FILED"


def test_document_impact_preview_reports_reply_source_file_status(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    case_data = _create_case(client, auth_headers)
    oa_in = _get_template(client, auth_headers, "OA_IN")
    oa_out = _get_template(client, auth_headers, "OA_OUT")
    source_doc = _create_document(
        client,
        auth_headers,
        case_id=case_data["id"],
        template_id=oa_in["id"],
        direction="IN",
        title="第一次审查意见通知书",
    )

    response = client.post(
        "/api/v1/documents/impact-preview",
        headers=auth_headers,
        json={
            "case_id": case_data["id"],
            "doc_template_id": oa_out["id"],
            "doc_type": "OFFICIAL_OUT",
            "direction": "OUT",
            "doc_date": "2026-04-10",
            "title": "第一次审查意见答复",
            "reply_to_id": source_doc["id"],
        },
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["template_code"] == "OA_OUT"
    assert payload["file_status_impacts"][0]["kind"] == "REPLY_SOURCE"
    assert payload["file_status_impacts"][0]["document_id"] == source_doc["id"]
    assert "回复来源文件将登记答复日期" in payload["confirmation_items"]
