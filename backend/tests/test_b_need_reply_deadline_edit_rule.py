from __future__ import annotations

from fastapi.testclient import TestClient

from tests.test_b2_reply_chain import (
    _create_case,
    _create_document,
    _get_doc_template_by_code,
    _get_task_logs,
    _get_tasks_for_document,
)


def _create_oa_in_document_with_task(
    client: TestClient,
    auth_headers: dict[str, str],
) -> tuple[dict, dict, dict]:
    case = _create_case(client, auth_headers)
    template = _get_doc_template_by_code(client, auth_headers, "OA_IN")
    document = _create_document(
        client,
        auth_headers,
        case["id"],
        direction="IN",
        doc_template_id=template["id"],
        title="NeedReply edit source",
        official_due_date="2026-04-15",
        official_due_date_source="MANUAL_OFFICIAL_NOTICE",
        official_due_date_status="CONFIRMED",
    )
    tasks = _get_tasks_for_document(client, auth_headers, case["id"], document["id"])
    assert len(tasks) == 1
    assert tasks[0]["status"] == "OPEN"
    return case, document, tasks[0]


def _assert_error(response, status_code: int, error_code: str) -> None:
    assert response.status_code == status_code, response.text
    payload = response.json()
    assert payload["error"]["code"] == error_code


def test_need_reply_false_requires_explicit_reply_task_action(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    _case, document, _task = _create_oa_in_document_with_task(client, auth_headers)

    response = client.put(
        f"/api/v1/documents/{document['id']}",
        json={"need_reply": False},
        headers=auth_headers,
    )

    _assert_error(response, 400, "DOCUMENT_REPLY_TASK_ACTION_REQUIRED")


def test_need_reply_cancel_action_cancels_open_reply_task(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    case, document, task = _create_oa_in_document_with_task(client, auth_headers)

    response = client.put(
        f"/api/v1/documents/{document['id']}",
        json={"need_reply": False, "reply_task_action": "CANCEL"},
        headers=auth_headers,
    )
    assert response.status_code == 200, response.text
    assert response.json()["need_reply"] is False

    tasks = _get_tasks_for_document(client, auth_headers, case["id"], document["id"])
    assert tasks[0]["id"] == task["id"]
    assert tasks[0]["status"] == "CANCELLED"
    logs = _get_task_logs(client, auth_headers, task["id"])
    assert any(log["action"] == "CANCEL" for log in logs)


def test_reply_task_update_action_updates_deadline_fields(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    case, document, task = _create_oa_in_document_with_task(client, auth_headers)

    response = client.put(
        f"/api/v1/documents/{document['id']}",
        json={
            "reply_task_action": "UPDATE",
            "reply_task_due_date": "2026-05-20",
            "reply_task_internal_due_date": "2026-05-10",
            "reply_task_remind1": "2026-05-01",
            "reply_task_remind2": "2026-05-05",
            "reply_task_remind3": "2026-05-08",
        },
        headers=auth_headers,
    )
    assert response.status_code == 200, response.text

    tasks = _get_tasks_for_document(client, auth_headers, case["id"], document["id"])
    updated_task = tasks[0]
    assert updated_task["id"] == task["id"]
    assert updated_task["status"] == "OPEN"
    assert updated_task["due_date"] == "2026-05-20"
    assert updated_task["internal_due_date"] == "2026-05-10"
    assert updated_task["remind1"] == "2026-05-01"
    assert updated_task["remind2"] == "2026-05-05"
    assert updated_task["remind3"] == "2026-05-08"
    logs = _get_task_logs(client, auth_headers, task["id"])
    assert any(log["action"] == "UPDATE" for log in logs)
