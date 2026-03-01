"""Tests for Batch B2: Document Reply Chain + Auto Write-off.

TDD tests — written against the B2 specification. Tests may fail until
the backend implementation is complete.

Covers:
- Document reply chain fields (reply_to_id, need_reply, reply_date)
- Auto write-off: OUT document reply → close linked OPEN tasks
- DocTemplate cascade: status_effect, need_reply propagation
- Full OA lifecycle (OA_IN → task created → OA_OUT reply → task closed)
"""

from __future__ import annotations

import uuid

from fastapi.testclient import TestClient

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DOC_BASE = "/api/v1/documents"
TASK_BASE = "/api/v1/tasks"
DOC_TMPL_BASE = "/api/v1/doc-templates"
CASE_BASE = "/api/v1/cases"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _unique_case_no() -> str:
    return f"B2-{uuid.uuid4().hex[:8].upper()}"


def _create_case(client: TestClient, auth_headers: dict, **overrides) -> dict:
    """Create a test case, return response JSON."""
    payload = {
        "case_no": _unique_case_no(),
        "case_type": "NORMAL",
        "patent_category": "INV",
        "flow_dir": "CN_DOMESTIC",
        "title_cn": "B2 Test Case",
        **overrides,
    }
    resp = client.post(CASE_BASE, json=payload, headers=auth_headers)
    assert resp.status_code == 201, f"Case creation failed: {resp.text}"
    return resp.json()


def _get_doc_template_by_code(client: TestClient, auth_headers: dict, code: str) -> dict:
    """Get a doc template by code via the list API."""
    resp = client.get(
        DOC_TMPL_BASE,
        headers=auth_headers,
        params={"q": code, "page_size": 100},
    )
    assert resp.status_code == 200, f"Doc template list failed: {resp.text}"
    items = resp.json()["items"]
    match = [t for t in items if t["code"] == code]
    assert match, f"Doc template '{code}' not found in seeded data"
    return match[0]


def _create_document(
    client: TestClient,
    auth_headers: dict,
    case_id: str,
    direction: str = "IN",
    **overrides,
) -> dict:
    """Create a test document, return response JSON."""
    payload = {
        "case_id": case_id,
        "direction": direction,
        "doc_date": "2026-01-15",
        "title": f"B2 Test Doc {direction}",
        **overrides,
    }
    resp = client.post(DOC_BASE, json=payload, headers=auth_headers)
    assert resp.status_code == 201, f"Doc creation failed: {resp.text}"
    return resp.json()


def _get_tasks_for_case(client: TestClient, auth_headers: dict, case_id: str) -> list[dict]:
    """Get all tasks for a case via the task list API."""
    resp = client.get(
        TASK_BASE,
        headers=auth_headers,
        params={"case_id": case_id, "page_size": 100},
    )
    assert resp.status_code == 200, f"Task list failed: {resp.text}"
    data = resp.json()
    return data.get("items", [])


def _get_tasks_for_document(
    client: TestClient, auth_headers: dict, case_id: str, document_id: str
) -> list[dict]:
    """Get tasks linked to a specific document (filter from case tasks)."""
    all_tasks = _get_tasks_for_case(client, auth_headers, case_id)
    return [t for t in all_tasks if t.get("document_id") == document_id]


def _get_task_logs(client: TestClient, auth_headers: dict, task_id: str) -> list[dict]:
    """Get logs for a task."""
    resp = client.get(
        f"{TASK_BASE}/{task_id}/logs",
        headers=auth_headers,
    )
    assert resp.status_code == 200, f"Task logs failed: {resp.text}"
    return resp.json()


def _get_case(client: TestClient, auth_headers: dict, case_id: str) -> dict:
    """Get case details."""
    resp = client.get(f"{CASE_BASE}/{case_id}", headers=auth_headers)
    assert resp.status_code == 200, f"Get case failed: {resp.text}"
    return resp.json()


def _get_document(client: TestClient, auth_headers: dict, document_id: str) -> dict:
    """Get document details."""
    resp = client.get(f"{DOC_BASE}/{document_id}", headers=auth_headers)
    assert resp.status_code == 200, f"Get document failed: {resp.text}"
    return resp.json()


# ---------------------------------------------------------------------------
# 1. Reply chain fields on Document CRUD
# ---------------------------------------------------------------------------


def test_create_document_with_reply_fields(client: TestClient, auth_headers: dict) -> None:
    """POST document with no reply_to_id → response includes
    reply_to_id=None, need_reply in response, reply_date=None."""
    case = _create_case(client, auth_headers)
    doc = _create_document(client, auth_headers, case["id"])

    assert "reply_to_id" in doc, "Response must include reply_to_id field"
    assert doc["reply_to_id"] is None
    assert "need_reply" in doc, "Response must include need_reply field"
    assert "reply_date" in doc, "Response must include reply_date field"
    assert doc["reply_date"] is None


# ---------------------------------------------------------------------------
# 2. Reply chain auto write-off — full lifecycle
# ---------------------------------------------------------------------------


def test_reply_chain_auto_writeoff(client: TestClient, auth_headers: dict) -> None:
    """Full lifecycle: IN doc (OA_IN template) → task auto-created →
    OUT reply (OA_OUT template with reply_to_id) → task DONE + reply_date set."""
    # 1. Create case
    case = _create_case(client, auth_headers)

    # 2. Find OA_IN template (has deadline_template_code="OA_REPLY", need_reply=True)
    oa_in_tmpl = _get_doc_template_by_code(client, auth_headers, "OA_IN")

    # 3. Create IN document with OA_IN template → should auto-create task
    in_doc = _create_document(
        client,
        auth_headers,
        case["id"],
        direction="IN",
        doc_template_id=oa_in_tmpl["id"],
        title="OA Received",
    )

    # 4. Verify task was auto-created and is OPEN
    tasks = _get_tasks_for_document(client, auth_headers, case["id"], in_doc["id"])
    assert len(tasks) >= 1, (
        f"Expected at least 1 auto-created task linked to IN document, got {len(tasks)}"
    )
    task = tasks[0]
    assert task["status"] == "OPEN"

    # 5. Find OA_OUT template
    oa_out_tmpl = _get_doc_template_by_code(client, auth_headers, "OA_OUT")

    # 6. Create OUT document replying to IN doc
    _create_document(
        client,
        auth_headers,
        case["id"],
        direction="OUT",
        doc_template_id=oa_out_tmpl["id"],
        title="OA Response",
        reply_to_id=in_doc["id"],
    )

    # 7. Verify task status → DONE (auto write-off)
    tasks_after = _get_tasks_for_document(client, auth_headers, case["id"], in_doc["id"])
    assert len(tasks_after) >= 1
    for t in tasks_after:
        assert t["status"] == "DONE", (
            f"Expected task status DONE after auto write-off, got {t['status']}"
        )

    # 8. Verify original IN document reply_date is set
    in_doc_refreshed = _get_document(client, auth_headers, in_doc["id"])
    assert in_doc_refreshed.get("reply_date") is not None, (
        "reply_date should be set on the original IN document after reply"
    )


# ---------------------------------------------------------------------------
# 3. No write-off when no open tasks
# ---------------------------------------------------------------------------


def test_reply_chain_no_writeoff_if_no_open_tasks(client: TestClient, auth_headers: dict) -> None:
    """Create IN doc (no template → no auto-task), then OUT reply →
    no error, works normally."""
    case = _create_case(client, auth_headers)

    # IN doc without template → no auto-task creation
    in_doc = _create_document(
        client,
        auth_headers,
        case["id"],
        direction="IN",
        title="Simple incoming doc",
    )

    # Confirm no tasks linked to this document
    tasks = _get_tasks_for_document(client, auth_headers, case["id"], in_doc["id"])
    assert len(tasks) == 0

    # OUT reply → should succeed without error
    out_doc = _create_document(
        client,
        auth_headers,
        case["id"],
        direction="OUT",
        title="Reply to simple doc",
        reply_to_id=in_doc["id"],
    )
    assert out_doc["reply_to_id"] == in_doc["id"]


# ---------------------------------------------------------------------------
# 4. Reply only closes tasks linked to the replied document
# ---------------------------------------------------------------------------


def test_reply_chain_only_closes_linked_tasks(client: TestClient, auth_headers: dict) -> None:
    """Two IN docs on same case. Reply to first only →
    only first doc's tasks closed, second's still OPEN."""
    case = _create_case(client, auth_headers)
    oa_in_tmpl = _get_doc_template_by_code(client, auth_headers, "OA_IN")

    # Create two IN docs with OA_IN template (different doc_dates for unique tasks)
    in_doc_1 = _create_document(
        client,
        auth_headers,
        case["id"],
        direction="IN",
        doc_template_id=oa_in_tmpl["id"],
        title="OA First",
        doc_date="2026-01-10",
    )
    in_doc_2 = _create_document(
        client,
        auth_headers,
        case["id"],
        direction="IN",
        doc_template_id=oa_in_tmpl["id"],
        title="OA Second",
        doc_date="2026-02-10",
    )

    # Verify both have auto-created tasks
    tasks_1 = _get_tasks_for_document(client, auth_headers, case["id"], in_doc_1["id"])
    tasks_2 = _get_tasks_for_document(client, auth_headers, case["id"], in_doc_2["id"])
    assert len(tasks_1) >= 1, "First IN doc should have auto-created task"
    assert len(tasks_2) >= 1, "Second IN doc should have auto-created task"

    # Reply to first only
    oa_out_tmpl = _get_doc_template_by_code(client, auth_headers, "OA_OUT")
    _create_document(
        client,
        auth_headers,
        case["id"],
        direction="OUT",
        doc_template_id=oa_out_tmpl["id"],
        title="OA Response to first",
        reply_to_id=in_doc_1["id"],
    )

    # First doc's tasks → DONE
    tasks_1_after = _get_tasks_for_document(client, auth_headers, case["id"], in_doc_1["id"])
    for t in tasks_1_after:
        assert t["status"] == "DONE", f"First doc's task should be DONE, got {t['status']}"

    # Second doc's tasks → still OPEN
    tasks_2_after = _get_tasks_for_document(client, auth_headers, case["id"], in_doc_2["id"])
    for t in tasks_2_after:
        assert t["status"] == "OPEN", f"Second doc's task should remain OPEN, got {t['status']}"


# ---------------------------------------------------------------------------
# 5. Reply to nonexistent document → 404
# ---------------------------------------------------------------------------


def test_reply_to_nonexistent_document_404(client: TestClient, auth_headers: dict) -> None:
    """Create OUT doc with reply_to_id=random UUID → expect 404."""
    case = _create_case(client, auth_headers)
    fake_doc_id = str(uuid.uuid4())

    resp = client.post(
        DOC_BASE,
        headers=auth_headers,
        json={
            "case_id": case["id"],
            "direction": "OUT",
            "doc_date": "2026-01-20",
            "title": "Reply to nonexistent",
            "reply_to_id": fake_doc_id,
        },
    )
    assert resp.status_code == 404, (
        f"Expected 404 for nonexistent reply_to_id, got {resp.status_code}: {resp.text}"
    )


# ---------------------------------------------------------------------------
# 6. DocTemplate cascade — status_effect
# ---------------------------------------------------------------------------


def test_doc_template_cascade_status_effect(client: TestClient, auth_headers: dict) -> None:
    """Create doc with template that has status_effect → case status updated."""
    case = _create_case(client, auth_headers)
    # Case starts with NOT_FILED status
    case_before = _get_case(client, auth_headers, case["id"])
    assert case_before["status"] == "NOT_FILED"

    # OA_IN template has status_effect="OA1"
    oa_in_tmpl = _get_doc_template_by_code(client, auth_headers, "OA_IN")
    assert oa_in_tmpl["status_effect"] == "OA1"

    # Create doc with this template
    _create_document(
        client,
        auth_headers,
        case["id"],
        direction="IN",
        doc_template_id=oa_in_tmpl["id"],
        title="OA for status effect test",
    )

    # Case status should now be OA1
    case_after = _get_case(client, auth_headers, case["id"])
    assert case_after["status"] == "OA1", (
        f"Expected case status 'OA1' after status_effect cascade, got '{case_after['status']}'"
    )


# ---------------------------------------------------------------------------
# 7. DocTemplate cascade — need_reply
# ---------------------------------------------------------------------------


def test_doc_template_cascade_need_reply(client: TestClient, auth_headers: dict) -> None:
    """Create doc with template that has need_reply=True → doc.need_reply=True."""
    case = _create_case(client, auth_headers)

    # OA_IN template has need_reply=True
    oa_in_tmpl = _get_doc_template_by_code(client, auth_headers, "OA_IN")
    assert oa_in_tmpl["need_reply"] is True

    doc = _create_document(
        client,
        auth_headers,
        case["id"],
        direction="IN",
        doc_template_id=oa_in_tmpl["id"],
        title="OA for need_reply test",
    )

    assert doc.get("need_reply") is True, "Document should inherit need_reply=True from DocTemplate"


# ---------------------------------------------------------------------------
# 8. DocTemplate cascade — no effect when null
# ---------------------------------------------------------------------------


def test_doc_template_cascade_no_effect_when_null(client: TestClient, auth_headers: dict) -> None:
    """Create doc with template that has no status_effect → case status unchanged."""
    case = _create_case(client, auth_headers)
    case_before = _get_case(client, auth_headers, case["id"])
    original_status = case_before["status"]

    # CLIENT_IN template has no status_effect
    client_in_tmpl = _get_doc_template_by_code(client, auth_headers, "CLIENT_IN")
    assert client_in_tmpl.get("status_effect") is None

    _create_document(
        client,
        auth_headers,
        case["id"],
        direction="IN",
        doc_template_id=client_in_tmpl["id"],
        title="Client doc for no-effect test",
    )

    case_after = _get_case(client, auth_headers, case["id"])
    assert case_after["status"] == original_status, (
        f"Case status should remain '{original_status}' when template "
        f"has no status_effect, got '{case_after['status']}'"
    )


# ---------------------------------------------------------------------------
# 9. Document update — reply fields
# ---------------------------------------------------------------------------


def test_document_update_reply_fields(client: TestClient, auth_headers: dict) -> None:
    """PUT /documents/{id} with need_reply=True → verify response."""
    case = _create_case(client, auth_headers)
    doc = _create_document(client, auth_headers, case["id"])

    resp = client.put(
        f"{DOC_BASE}/{doc['id']}",
        headers=auth_headers,
        json={"need_reply": True},
    )
    assert resp.status_code == 200, f"Update failed: {resp.text}"
    updated = resp.json()
    assert updated["need_reply"] is True


# ---------------------------------------------------------------------------
# 10. Document list includes reply fields
# ---------------------------------------------------------------------------


def test_document_list_includes_reply_fields(client: TestClient, auth_headers: dict) -> None:
    """GET /documents?case_id=X → reply_to_id, need_reply, reply_date
    present in each list item."""
    case = _create_case(client, auth_headers)
    _create_document(client, auth_headers, case["id"])

    resp = client.get(
        DOC_BASE,
        headers=auth_headers,
        params={"case_id": case["id"]},
    )
    assert resp.status_code == 200
    items = resp.json()["items"]
    assert len(items) >= 1

    for item in items:
        assert "reply_to_id" in item, "List item must include reply_to_id"
        assert "need_reply" in item, "List item must include need_reply"
        assert "reply_date" in item, "List item must include reply_date"


# ---------------------------------------------------------------------------
# 11. Auto write-off task log
# ---------------------------------------------------------------------------


def test_auto_writeoff_task_log_created(client: TestClient, auth_headers: dict) -> None:
    """After auto write-off, GET /tasks/{id}/logs → log with action=AUTO_WRITEOFF."""
    case = _create_case(client, auth_headers)
    oa_in_tmpl = _get_doc_template_by_code(client, auth_headers, "OA_IN")

    # Create IN doc → auto-task
    in_doc = _create_document(
        client,
        auth_headers,
        case["id"],
        direction="IN",
        doc_template_id=oa_in_tmpl["id"],
        title="OA for log test",
    )
    tasks = _get_tasks_for_document(client, auth_headers, case["id"], in_doc["id"])
    assert len(tasks) >= 1
    task_id = tasks[0]["id"]

    # Create OUT reply → auto write-off
    oa_out_tmpl = _get_doc_template_by_code(client, auth_headers, "OA_OUT")
    _create_document(
        client,
        auth_headers,
        case["id"],
        direction="OUT",
        doc_template_id=oa_out_tmpl["id"],
        title="OA Response for log test",
        reply_to_id=in_doc["id"],
    )

    # Verify task logs contain AUTO_WRITEOFF
    logs = _get_task_logs(client, auth_headers, task_id)
    actions = [log_entry["action"] for log_entry in logs]
    assert "AUTO_WRITEOFF" in actions, f"Expected AUTO_WRITEOFF in task logs, got: {actions}"

    # Verify the writeoff log has correct status transition
    writeoff_log = next(log_entry for log_entry in logs if log_entry["action"] == "AUTO_WRITEOFF")
    assert writeoff_log["from_status"] == "OPEN"
    assert writeoff_log["to_status"] == "DONE"


# ---------------------------------------------------------------------------
# 12. Full OA lifecycle — end to end
# ---------------------------------------------------------------------------


def test_full_oa_lifecycle(client: TestClient, auth_headers: dict) -> None:
    """End-to-end: create case → OA_IN → cascade + task → OA_OUT reply → auto close."""
    # 1. Create case
    case = _create_case(client, auth_headers)
    case_detail = _get_case(client, auth_headers, case["id"])
    assert case_detail["status"] == "NOT_FILED"

    # 2. Get templates
    oa_in_tmpl = _get_doc_template_by_code(client, auth_headers, "OA_IN")
    oa_out_tmpl = _get_doc_template_by_code(client, auth_headers, "OA_OUT")

    # 3. Create OA_IN document
    #    Template config: status_effect="OA1", need_reply=True,
    #                     deadline_template_code="OA_REPLY"
    oa_in_doc = _create_document(
        client,
        auth_headers,
        case["id"],
        direction="IN",
        doc_template_id=oa_in_tmpl["id"],
        title="Official Action Received",
        doc_date="2026-01-15",
    )

    # 4a. Verify case status changed to OA1 (status_effect cascade)
    case_updated = _get_case(client, auth_headers, case["id"])
    assert case_updated["status"] == "OA1", (
        f"Case status should be 'OA1', got '{case_updated['status']}'"
    )

    # 4b. Verify document need_reply=True (need_reply cascade)
    assert oa_in_doc.get("need_reply") is True, (
        "OA_IN doc should have need_reply=True from template"
    )

    # 4c. Verify task auto-created and OPEN
    tasks = _get_tasks_for_document(client, auth_headers, case["id"], oa_in_doc["id"])
    assert len(tasks) >= 1, "OA_IN should auto-create a deadline task"
    task = tasks[0]
    assert task["status"] == "OPEN"
    assert task["document_id"] == oa_in_doc["id"]

    # 4d. Verify task has a due_date (calculated from doc_date + OA_REPLY.add_days)
    assert task.get("due_date") is not None, "Auto-created task must have a due_date"

    # 5. Create OA_OUT document — reply to OA_IN
    oa_out_doc = _create_document(
        client,
        auth_headers,
        case["id"],
        direction="OUT",
        doc_template_id=oa_out_tmpl["id"],
        title="OA Response Sent",
        doc_date="2026-03-01",
        reply_to_id=oa_in_doc["id"],
    )

    # 6a. Task status → DONE (auto write-off)
    tasks_after = _get_tasks_for_document(client, auth_headers, case["id"], oa_in_doc["id"])
    for t in tasks_after:
        assert t["status"] == "DONE", f"Task should be DONE after OA_OUT reply, got '{t['status']}'"

    # 6b. reply_date set on original IN document
    oa_in_refreshed = _get_document(client, auth_headers, oa_in_doc["id"])
    assert oa_in_refreshed.get("reply_date") is not None, (
        "OA_IN reply_date should be set after OA_OUT reply"
    )

    # 6c. OUT doc has reply_to_id pointing to IN doc
    assert oa_out_doc.get("reply_to_id") == oa_in_doc["id"]

    # 6d. Task log includes AUTO_WRITEOFF entry
    task_id = tasks[0]["id"]
    logs = _get_task_logs(client, auth_headers, task_id)
    actions = [log_entry["action"] for log_entry in logs]
    assert "AUTO_WRITEOFF" in actions, f"Task logs should include AUTO_WRITEOFF, got: {actions}"
