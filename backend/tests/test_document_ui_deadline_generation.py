from __future__ import annotations

from uuid import uuid4


def _uid(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:8].upper()}"


def _create_case(client, auth_headers) -> str:
    client_resp = client.post(
        "/api/v1/clients",
        json={
            "name_cn": _uid("UI-OA-CLIENT"),
            "client_type": "CORPORATE",
            "default_currency": "CNY",
            "is_active": True,
        },
        headers=auth_headers,
    )
    assert client_resp.status_code == 201, client_resp.text

    case_resp = client.post(
        "/api/v1/cases",
        json={
            "case_no": _uid("UI-OA-CASE"),
            "case_type": "NORMAL",
            "patent_category": "INV",
            "flow_dir": "CN_DOMESTIC",
            "client_id": client_resp.json()["id"],
            "title_cn": "UI文书期限测试案卷",
        },
        headers=auth_headers,
    )
    assert case_resp.status_code == 201, case_resp.text
    return case_resp.json()["id"]


def _get_template(client, auth_headers, code: str) -> dict:
    resp = client.get(f"/api/v1/doc-templates?q={code}", headers=auth_headers)
    assert resp.status_code == 200, resp.text
    matches = [item for item in resp.json()["items"] if item["code"] == code]
    assert len(matches) == 1
    return matches[0]


def test_ui_generic_doc_type_uses_template_deadline_and_reply_keeps_task_open(client, auth_headers):
    case_id = _create_case(client, auth_headers)
    oa_in = _get_template(client, auth_headers, "OA_IN")
    oa_out = _get_template(client, auth_headers, "OA_OUT")

    in_resp = client.post(
        "/api/v1/documents",
        json={
            "case_id": case_id,
            "doc_template_id": oa_in["id"],
            "doc_type": "OFFICIAL_IN",
            "direction": "IN",
            "doc_date": "2026-02-01",
            "official_due_date": "2026-06-01",
            "official_due_date_source": "MANUAL_OFFICIAL_NOTICE",
            "official_due_date_status": "CONFIRMED",
            "title": "UI路径OA来文",
        },
        headers=auth_headers,
    )
    assert in_resp.status_code == 201, in_resp.text
    assert in_resp.headers.get("X-Auto-Tasks-Created") == "1"
    incoming_document_id = in_resp.json()["id"]

    tasks_resp = client.get(f"/api/v1/tasks?case_id={case_id}", headers=auth_headers)
    assert tasks_resp.status_code == 200, tasks_resp.text
    tasks = tasks_resp.json()["items"]
    oa_tasks = [task for task in tasks if task["title"] == "OA答复期限"]
    assert len(oa_tasks) == 1
    assert oa_tasks[0]["status"] == "OPEN"

    out_resp = client.post(
        "/api/v1/documents",
        json={
            "case_id": case_id,
            "doc_template_id": oa_out["id"],
            "doc_type": "OFFICIAL_OUT",
            "direction": "OUT",
            "doc_date": "2026-03-01",
            "title": "UI路径OA答复",
            "reply_to_id": incoming_document_id,
        },
        headers=auth_headers,
    )
    assert out_resp.status_code == 201, out_resp.text

    done_resp = client.get(f"/api/v1/tasks?case_id={case_id}", headers=auth_headers)
    assert done_resp.status_code == 200, done_resp.text
    done_task = next(task for task in done_resp.json()["items"] if task["id"] == oa_tasks[0]["id"])
    assert done_task["status"] == "OPEN"
