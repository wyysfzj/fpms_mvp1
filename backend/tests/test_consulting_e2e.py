from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient


def _uid(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:8].upper()}"


def _assert_error(response, status_code: int, error_code: str) -> dict:
    assert response.status_code == status_code, response.text
    payload = response.json()
    assert "error" in payload, payload
    assert payload["error"].get("code") == error_code, payload
    assert payload["error"].get("message")
    return payload


def _create_client(client: TestClient, auth_headers: dict[str, str]) -> str:
    resp = client.post(
        "/api/v1/clients",
        json={"name_cn": _uid("CS-CLI"), "default_currency": "CNY"},
        headers=auth_headers,
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


def _create_consulting_case(
    client: TestClient,
    auth_headers: dict[str, str],
    *,
    client_id: str,
    case_type: str,
    case_no: str | None = None,
) -> dict:
    payload = {
        "case_no": case_no or _uid("CS-CASE"),
        "case_type": case_type,
        "client_id": client_id,
        "title_cn": f"{case_type} case",
        "primary_agent_id": _uid("AGT"),
        "recv_date": "2026-04-01",
    }
    resp = client.post("/api/v1/consulting/cases", headers=auth_headers, json=payload)
    assert resp.status_code == 201, resp.text
    return resp.json()


def test_consulting_case_creation_and_error_matrix(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    client_id = _create_client(client, auth_headers)

    consult_case_no = _uid("CONSULT")
    consult_resp = client.post(
        "/api/v1/consulting/cases",
        headers=auth_headers,
        json={
            "case_no": consult_case_no,
            "case_type": "CONSULTING",
            "client_id": client_id,
            "title_cn": "Consulting service",
            "primary_agent_id": _uid("AGT"),
            "recv_date": "2026-04-02",
        },
    )
    assert consult_resp.status_code == 201, consult_resp.text
    consult_payload = consult_resp.json()
    assert consult_payload["case_no"] == consult_case_no
    assert consult_payload["case_type"] == "CONSULTING"
    assert consult_payload["status"] == "NOT_FILED"

    search_resp = client.post(
        "/api/v1/consulting/cases",
        headers=auth_headers,
        json={
            "case_no": _uid("SEARCH"),
            "case_type": "SEARCH",
            "client_id": client_id,
            "title_cn": "Search service",
            "primary_agent_id": _uid("AGT"),
            "recv_date": "2026-04-03",
        },
    )
    assert search_resp.status_code == 201, search_resp.text
    assert search_resp.json()["case_type"] == "SEARCH"

    duplicate_resp = client.post(
        "/api/v1/consulting/cases",
        headers=auth_headers,
        json={
            "case_no": consult_case_no,
            "case_type": "CONSULTING",
            "client_id": client_id,
            "title_cn": "Duplicate",
            "primary_agent_id": _uid("AGT"),
            "recv_date": "2026-04-04",
        },
    )
    _assert_error(duplicate_resp, 409, "CASE_NO_DUPLICATE")

    invalid_type_resp = client.post(
        "/api/v1/consulting/cases",
        headers=auth_headers,
        json={
            "case_no": _uid("BADTYPE"),
            "case_type": "NORMAL",
            "client_id": client_id,
            "title_cn": "Invalid type",
            "primary_agent_id": _uid("AGT"),
            "recv_date": "2026-04-05",
        },
    )
    _assert_error(invalid_type_resp, 400, "CONSULTING_CASE_INVALID")

    missing_field_resp = client.post(
        "/api/v1/consulting/cases",
        headers=auth_headers,
        json={
            "case_no": _uid("BLANK"),
            "case_type": "CONSULTING",
            "client_id": client_id,
            "title_cn": "   ",
            "primary_agent_id": _uid("AGT"),
            "recv_date": "2026-04-06",
        },
    )
    _assert_error(missing_field_resp, 400, "CONSULTING_CASE_INVALID")

    validation_resp = client.post(
        "/api/v1/consulting/cases",
        headers=auth_headers,
        json={
            "case_no": _uid("VAL"),
            "case_type": "CONSULTING",
            "client_id": client_id,
            "title_cn": "Validation",
            "primary_agent_id": _uid("AGT"),
            "recv_date": "bad-date",
        },
    )
    _assert_error(validation_resp, 422, "VALIDATION_ERROR")


def test_consulting_fee_draft_modes_conflict_and_errors(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    client_id = _create_client(client, auth_headers)

    consult_case = _create_consulting_case(
        client,
        auth_headers,
        client_id=client_id,
        case_type="CONSULTING",
    )
    fixed_resp = client.post(
        "/api/v1/consulting/fee-drafts",
        headers=auth_headers,
        json={
            "case_id": consult_case["id"],
            "mode": "FIXED",
            "currency": "CNY",
            "fixed_fee": "500.00",
        },
    )
    assert fixed_resp.status_code == 201, fixed_resp.text
    fixed_payload = fixed_resp.json()
    assert fixed_payload["mode"] == "FIXED"
    assert fixed_payload["draft_type"] == "CONSULT_FEE"
    assert fixed_payload["created_line_count"] == 1
    assert str(fixed_payload["totals"]["amount"]) == "500.00"

    fixed_conflict_resp = client.post(
        "/api/v1/consulting/fee-drafts",
        headers=auth_headers,
        json={
            "case_id": consult_case["id"],
            "mode": "FIXED",
            "currency": "CNY",
            "fixed_fee": "500.00",
        },
    )
    _assert_error(fixed_conflict_resp, 409, "FEE_DRAFT_CONFLICT")

    search_case = _create_consulting_case(
        client,
        auth_headers,
        client_id=client_id,
        case_type="SEARCH",
    )
    hourly_resp = client.post(
        "/api/v1/consulting/fee-drafts",
        headers=auth_headers,
        json={
            "case_id": search_case["id"],
            "mode": "HOURLY",
            "currency": "CNY",
            "hourly_lines": [
                {
                    "fee_code": "SEARCH_H1",
                    "fee_name": "Search review",
                    "hours": "2",
                    "hourly_rate": "300",
                    "trace_key": "search-hourly-1",
                }
            ],
            "misc_lines": [
                {
                    "fee_code": "SEARCH_MISC",
                    "fee_name": "Translation",
                    "amount": "80",
                    "trace_key": "search-misc-1",
                }
            ],
        },
    )
    assert hourly_resp.status_code == 201, hourly_resp.text
    hourly_payload = hourly_resp.json()
    assert hourly_payload["mode"] == "HOURLY"
    assert hourly_payload["draft_type"] == "SEARCH_FEE"
    assert hourly_payload["created_line_count"] == 2
    trace_keys = {item["trace_key"] for item in hourly_payload["items"]}
    assert "search-hourly-1" in trace_keys
    assert "search-misc-1" in trace_keys

    invalid_mode_resp = client.post(
        "/api/v1/consulting/fee-drafts",
        headers=auth_headers,
        json={
            "case_id": search_case["id"],
            "mode": "UNKNOWN",
            "currency": "CNY",
        },
    )
    _assert_error(invalid_mode_resp, 400, "CONSULTING_FEE_INVALID")

    missing_case_resp = client.post(
        "/api/v1/consulting/fee-drafts",
        headers=auth_headers,
        json={
            "case_id": str(uuid4()),
            "mode": "FIXED",
            "currency": "CNY",
            "fixed_fee": "100.00",
        },
    )
    _assert_error(missing_case_resp, 404, "CASE_NOT_FOUND")

    bad_hourly_case = _create_consulting_case(
        client,
        auth_headers,
        client_id=client_id,
        case_type="SEARCH",
    )
    invalid_hourly_resp = client.post(
        "/api/v1/consulting/fee-drafts",
        headers=auth_headers,
        json={
            "case_id": bad_hourly_case["id"],
            "mode": "HOURLY",
            "currency": "CNY",
            "hourly_lines": [
                {
                    "fee_code": "SEARCH_H2",
                    "fee_name": "Invalid hours",
                    "hours": "0",
                    "hourly_rate": "100",
                }
            ],
        },
    )
    _assert_error(invalid_hourly_resp, 400, "CONSULTING_FEE_INVALID")

    validation_resp = client.post(
        "/api/v1/consulting/fee-drafts",
        headers=auth_headers,
        json={"case_id": search_case["id"]},
    )
    _assert_error(validation_resp, 422, "VALIDATION_ERROR")
