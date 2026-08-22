from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient


def _create_case(client: TestClient, auth_headers: dict[str, str]) -> dict:
    suffix = uuid.uuid4().hex[:8].upper()
    applicant_response = client.post(
        "/api/v1/applicants",
        headers=auth_headers,
        json={
            "code": f"OA-OPEN-AP-{suffix}",
            "name_cn": f"OA答复保持待办申请人-{suffix}",
            "applicant_type": "ENTITY",
            "is_active": True,
        },
    )
    assert applicant_response.status_code == 201, applicant_response.text
    applicant = applicant_response.json()

    case_response = client.post(
        "/api/v1/cases",
        headers=auth_headers,
        json={
            "case_no": f"OA-OPEN-{suffix}",
            "case_type": "NORMAL",
            "patent_category": "INV",
            "flow_dir": "CN_DOMESTIC",
            "fee_reduction": "0",
            "title_cn": "OA答复保持待办测试案件",
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
    assert case_response.status_code == 201, case_response.text
    return case_response.json()


def _template(client: TestClient, auth_headers: dict[str, str], code: str) -> dict:
    response = client.get(
        "/api/v1/doc-templates",
        headers=auth_headers,
        params={"q": code, "page_size": 100},
    )
    assert response.status_code == 200, response.text
    matches = [item for item in response.json()["items"] if item["code"] == code]
    assert len(matches) == 1
    return matches[0]


def _case_tasks(client: TestClient, auth_headers: dict[str, str], case_id: str) -> list[dict]:
    response = client.get(
        "/api/v1/tasks",
        headers=auth_headers,
        params={"case_id": case_id, "page_size": 100},
    )
    assert response.status_code == 200, response.text
    return response.json()["items"]


@pytest.mark.parametrize(
    "use_oa_out_template",
    [True, False],
    ids=["oa-out-template", "generic-out-with-oa-source"],
)
def test_oa_out_defers_date_while_generic_reply_records_without_closing_oa_source(
    client: TestClient,
    auth_headers: dict[str, str],
    use_oa_out_template: bool,
) -> None:
    case = _create_case(client, auth_headers)
    oa_in = _template(client, auth_headers, "OA_IN")

    incoming_response = client.post(
        "/api/v1/documents",
        headers=auth_headers,
        json={
            "case_id": case["id"],
            "doc_template_id": oa_in["id"],
            "direction": "IN",
            "doc_date": "2026-01-15",
            "title": "第一次审查意见通知书",
            "official_due_date": "2026-04-15",
            "official_due_date_source": "MANUAL_OFFICIAL_NOTICE",
            "official_due_date_status": "CONFIRMED",
        },
    )
    assert incoming_response.status_code == 201, incoming_response.text
    incoming = incoming_response.json()

    tasks = [
        task
        for task in _case_tasks(client, auth_headers, case["id"])
        if task["document_id"] == incoming["id"]
    ]
    assert len(tasks) == 1
    task_id = tasks[0]["id"]
    assert tasks[0]["status"] == "OPEN"

    reply_payload = {
        "case_id": case["id"],
        "direction": "OUT",
        "doc_date": "2026-03-01",
        "title": "第一次审查意见答复文件",
        "reply_to_id": incoming["id"],
    }
    if use_oa_out_template:
        reply_payload["doc_template_id"] = _template(client, auth_headers, "OA_OUT")["id"]
    reply_response = client.post(
        "/api/v1/documents",
        headers=auth_headers,
        json=reply_payload,
    )
    assert reply_response.status_code == 201, reply_response.text
    assert reply_response.json()["reply_to_id"] == incoming["id"]

    task_response = client.get(f"/api/v1/tasks/{task_id}", headers=auth_headers)
    assert task_response.status_code == 200, task_response.text
    assert task_response.json()["status"] == "OPEN"
    assert task_response.json()["done_at"] is None

    logs_response = client.get(f"/api/v1/tasks/{task_id}/logs", headers=auth_headers)
    assert logs_response.status_code == 200, logs_response.text
    assert "AUTO_WRITEOFF" not in {log["action"] for log in logs_response.json()}

    incoming_response = client.get(f"/api/v1/documents/{incoming['id']}", headers=auth_headers)
    assert incoming_response.status_code == 200, incoming_response.text
    expected_reply_date = None if use_oa_out_template else "2026-03-01"
    assert incoming_response.json()["reply_date"] == expected_reply_date

    case_response = client.get(f"/api/v1/cases/{case['id']}", headers=auth_headers)
    assert case_response.status_code == 200, case_response.text
    assert case_response.json()["status"] == case["status"]


def test_ordinary_non_oa_reply_still_auto_closes_linked_task(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    case = _create_case(client, auth_headers)
    incoming_response = client.post(
        "/api/v1/documents",
        headers=auth_headers,
        json={
            "case_id": case["id"],
            "direction": "IN",
            "doc_date": "2026-01-15",
            "title": "普通客户来函",
        },
    )
    assert incoming_response.status_code == 201, incoming_response.text
    incoming = incoming_response.json()

    task_response = client.post(
        "/api/v1/tasks",
        headers=auth_headers,
        json={
            "case_id": case["id"],
            "document_id": incoming["id"],
            "title": "普通来函答复",
            "due_date": "2026-02-15",
        },
    )
    assert task_response.status_code == 201, task_response.text
    task_id = task_response.json()["id"]

    reply_response = client.post(
        "/api/v1/documents",
        headers=auth_headers,
        json={
            "case_id": case["id"],
            "direction": "OUT",
            "doc_date": "2026-01-20",
            "title": "普通客户来函答复",
            "reply_to_id": incoming["id"],
        },
    )
    assert reply_response.status_code == 201, reply_response.text

    task_response = client.get(f"/api/v1/tasks/{task_id}", headers=auth_headers)
    assert task_response.status_code == 200, task_response.text
    assert task_response.json()["status"] == "DONE"
    assert task_response.json()["done_at"] is not None

    logs_response = client.get(f"/api/v1/tasks/{task_id}/logs", headers=auth_headers)
    assert logs_response.status_code == 200, logs_response.text
    assert "AUTO_WRITEOFF" in {log["action"] for log in logs_response.json()}

    incoming_response = client.get(f"/api/v1/documents/{incoming['id']}", headers=auth_headers)
    assert incoming_response.status_code == 200, incoming_response.text
    assert incoming_response.json()["reply_date"] == "2026-01-20"

    case_response = client.get(f"/api/v1/cases/{case['id']}", headers=auth_headers)
    assert case_response.status_code == 200, case_response.text
    assert case_response.json()["status"] == "NOT_FILED"
