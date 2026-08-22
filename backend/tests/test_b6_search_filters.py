"""B6 — Search & Filter Enhancement tests.

Tests for:
- client_id filter on documents
- client_id filter on tasks
- case_no in document list response
- client_name in task list response
"""

from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient

# ---------------------------------------------------------------------------
# Helpers — create test data via API
# ---------------------------------------------------------------------------


def _create_client(
    client: TestClient,
    auth_headers: dict[str, str],
    name_cn: str,
) -> dict:
    """Create a client and return the JSON response."""
    resp = client.post(
        "/api/v1/clients",
        headers=auth_headers,
        json={"name_cn": name_cn},
    )
    assert resp.status_code == 201, f"client create failed: {resp.text}"
    return resp.json()


def _create_case(
    client: TestClient,
    auth_headers: dict[str, str],
    client_id: str,
    case_no: str,
) -> dict:
    """Create a case linked to a client and return the JSON response."""
    resp = client.post(
        "/api/v1/cases",
        headers=auth_headers,
        json={
            "case_no": case_no,
            "fee_reduction": "0",
            "client_id": client_id,
            "title_cn": f"Test case {case_no}",
        },
    )
    assert resp.status_code == 201, f"case create failed: {resp.text}"
    return resp.json()


def _create_document(
    client: TestClient,
    auth_headers: dict[str, str],
    case_id: str,
    direction: str = "IN",
    title: str | None = None,
) -> dict:
    """Create a document linked to a case and return the JSON response."""
    resp = client.post(
        "/api/v1/documents",
        headers=auth_headers,
        json={
            "case_id": case_id,
            "direction": direction,
            "doc_date": "2025-01-15",
            "title": title or f"Doc-{uuid4().hex[:8]}",
        },
    )
    assert resp.status_code == 201, f"document create failed: {resp.text}"
    return resp.json()


def _create_task(
    client: TestClient,
    auth_headers: dict[str, str],
    case_id: str,
    title: str | None = None,
) -> dict:
    """Create a task linked to a case and return the JSON response."""
    resp = client.post(
        "/api/v1/tasks",
        headers=auth_headers,
        json={
            "case_id": case_id,
            "title": title or f"Task-{uuid4().hex[:8]}",
            "due_date": "2025-06-01",
        },
    )
    assert resp.status_code == 201, f"task create failed: {resp.text}"
    return resp.json()


# ---------------------------------------------------------------------------
# 1. Document list includes case_no
# ---------------------------------------------------------------------------


def test_document_list_includes_case_no(client: TestClient, auth_headers: dict) -> None:
    tag = uuid4().hex[:8]
    cl = _create_client(client, auth_headers, name_cn=f"CaseNoClient-{tag}")
    case_no = f"CN-{tag}"
    case = _create_case(client, auth_headers, client_id=cl["id"], case_no=case_no)
    _create_document(client, auth_headers, case_id=case["id"])

    resp = client.get(
        "/api/v1/documents",
        headers=auth_headers,
        params={"case_id": case["id"]},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1
    item = data["items"][0]
    assert "case_no" in item
    assert item["case_no"] == case_no


# ---------------------------------------------------------------------------
# 2. Document list — filter by client_id
# ---------------------------------------------------------------------------


def test_document_list_filter_by_client_id(client: TestClient, auth_headers: dict) -> None:
    tag = uuid4().hex[:8]

    # Client A
    cl_a = _create_client(client, auth_headers, name_cn=f"DocFilterA-{tag}")
    case_a = _create_case(client, auth_headers, client_id=cl_a["id"], case_no=f"DFA-{tag}")
    doc_a = _create_document(client, auth_headers, case_id=case_a["id"], title=f"DocA-{tag}")

    # Client B
    cl_b = _create_client(client, auth_headers, name_cn=f"DocFilterB-{tag}")
    case_b = _create_case(client, auth_headers, client_id=cl_b["id"], case_no=f"DFB-{tag}")
    _create_document(client, auth_headers, case_id=case_b["id"], title=f"DocB-{tag}")

    # Filter by client A
    resp = client.get(
        "/api/v1/documents",
        headers=auth_headers,
        params={"client_id": cl_a["id"]},
    )
    assert resp.status_code == 200
    data = resp.json()
    ids = [item["id"] for item in data["items"]]
    assert doc_a["id"] in ids
    # Ensure none from client B
    for item in data["items"]:
        assert item["case_id"] == case_a["id"]


# ---------------------------------------------------------------------------
# 3. Document list — filter by non-existent client_id
# ---------------------------------------------------------------------------


def test_document_list_filter_by_client_id_no_results(
    client: TestClient, auth_headers: dict
) -> None:
    fake_id = str(uuid4())
    resp = client.get(
        "/api/v1/documents",
        headers=auth_headers,
        params={"client_id": fake_id},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 0
    assert data["items"] == []


# ---------------------------------------------------------------------------
# 4. Task list includes client_name
# ---------------------------------------------------------------------------


def test_task_list_includes_client_name(client: TestClient, auth_headers: dict) -> None:
    tag = uuid4().hex[:8]
    client_name = f"TaskNameClient-{tag}"
    cl = _create_client(client, auth_headers, name_cn=client_name)
    case = _create_case(client, auth_headers, client_id=cl["id"], case_no=f"TN-{tag}")
    _create_task(client, auth_headers, case_id=case["id"])

    resp = client.get(
        "/api/v1/tasks",
        headers=auth_headers,
        params={"case_id": case["id"]},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1
    item = data["items"][0]
    assert "client_name" in item
    assert item["client_name"] == client_name


# ---------------------------------------------------------------------------
# 5. Task list — filter by client_id
# ---------------------------------------------------------------------------


def test_task_list_filter_by_client_id(client: TestClient, auth_headers: dict) -> None:
    tag = uuid4().hex[:8]

    # Client A
    cl_a = _create_client(client, auth_headers, name_cn=f"TaskFilterA-{tag}")
    case_a = _create_case(client, auth_headers, client_id=cl_a["id"], case_no=f"TFA-{tag}")
    task_a = _create_task(client, auth_headers, case_id=case_a["id"], title=f"TaskA-{tag}")

    # Client B
    cl_b = _create_client(client, auth_headers, name_cn=f"TaskFilterB-{tag}")
    case_b = _create_case(client, auth_headers, client_id=cl_b["id"], case_no=f"TFB-{tag}")
    _create_task(client, auth_headers, case_id=case_b["id"], title=f"TaskB-{tag}")

    # Filter by client A
    resp = client.get(
        "/api/v1/tasks",
        headers=auth_headers,
        params={"client_id": cl_a["id"]},
    )
    assert resp.status_code == 200
    data = resp.json()
    ids = [item["id"] for item in data["items"]]
    assert task_a["id"] in ids
    # Ensure none from client B
    for item in data["items"]:
        assert item["case_id"] == case_a["id"]


# ---------------------------------------------------------------------------
# 6. Task list — filter by non-existent client_id
# ---------------------------------------------------------------------------


def test_task_list_filter_by_client_id_no_results(client: TestClient, auth_headers: dict) -> None:
    fake_id = str(uuid4())
    resp = client.get(
        "/api/v1/tasks",
        headers=auth_headers,
        params={"client_id": fake_id},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 0
    assert data["items"] == []


# ---------------------------------------------------------------------------
# 7. Document list — combined client_id + direction filter
# ---------------------------------------------------------------------------


def test_document_list_combined_client_id_and_direction(
    client: TestClient, auth_headers: dict
) -> None:
    tag = uuid4().hex[:8]
    cl = _create_client(client, auth_headers, name_cn=f"CombDoc-{tag}")
    case = _create_case(client, auth_headers, client_id=cl["id"], case_no=f"CD-{tag}")
    doc_in = _create_document(
        client, auth_headers, case_id=case["id"], direction="IN", title=f"IN-{tag}"
    )
    _create_document(client, auth_headers, case_id=case["id"], direction="OUT", title=f"OUT-{tag}")

    resp = client.get(
        "/api/v1/documents",
        headers=auth_headers,
        params={"client_id": cl["id"], "direction": "IN"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1
    ids = [item["id"] for item in data["items"]]
    assert doc_in["id"] in ids
    # All returned documents should be direction=IN
    for item in data["items"]:
        assert item["direction"] == "IN"


# ---------------------------------------------------------------------------
# 8. Task list — combined client_id + status filter
# ---------------------------------------------------------------------------


def test_task_list_combined_client_id_and_status(client: TestClient, auth_headers: dict) -> None:
    tag = uuid4().hex[:8]
    cl = _create_client(client, auth_headers, name_cn=f"CombTask-{tag}")
    case = _create_case(client, auth_headers, client_id=cl["id"], case_no=f"CT-{tag}")

    # Create two tasks — both start as OPEN
    task_open = _create_task(client, auth_headers, case_id=case["id"], title=f"Open-{tag}")
    task_closed = _create_task(client, auth_headers, case_id=case["id"], title=f"Close-{tag}")

    # Close the second task
    resp = client.post(
        f"/api/v1/tasks/{task_closed['id']}/close",
        headers=auth_headers,
        json={"remark": "test close"},
    )
    assert resp.status_code == 200

    # Filter: client_id + status=OPEN
    resp = client.get(
        "/api/v1/tasks",
        headers=auth_headers,
        params={"client_id": cl["id"], "status": "OPEN"},
    )
    assert resp.status_code == 200
    data = resp.json()
    ids = [item["id"] for item in data["items"]]
    assert task_open["id"] in ids
    assert task_closed["id"] not in ids
    for item in data["items"]:
        assert item["status"] == "OPEN"
