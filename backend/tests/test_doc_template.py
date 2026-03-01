"""Tests for Batch B1: DocTemplate CRUD API endpoints.

Covers list (with filters, search, pagination), create, get-by-id, update,
duplicate-code rejection, not-found handling, and unauthorized access.
"""

from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient

BASE = "/api/v1/doc-templates"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _unique_code(prefix: str = "DT") -> str:
    return f"{prefix}-{uuid4().hex[:8]}"


def _create_template(
    client: TestClient,
    headers: dict,
    *,
    code: str | None = None,
    name: str | None = None,
    **overrides,
) -> dict:
    """Create a doc template via the API and return its JSON body."""
    code = code or _unique_code()
    name = name or f"Template {code}"
    payload = {"code": code, "name": name, **overrides}
    resp = client.post(BASE, headers=headers, json=payload)
    assert resp.status_code == 201, resp.text
    return resp.json()


# ---------------------------------------------------------------------------
# 1. List — seeded data
# ---------------------------------------------------------------------------


def test_list_doc_templates_returns_seeded(client: TestClient, auth_headers: dict) -> None:
    """GET /doc-templates returns 200, contains seeded OA_IN & CLIENT_IN with SPEC fields."""
    resp = client.get(BASE, headers=auth_headers, params={"page_size": 100})
    assert resp.status_code == 200

    data = resp.json()
    assert "items" in data
    assert data["total"] >= 5  # at least the 5 seeded templates

    codes = {t["code"] for t in data["items"]}
    assert "OA_IN" in codes
    assert "CLIENT_IN" in codes

    # Verify SPEC fields on OA_IN
    oa_in = next(t for t in data["items"] if t["code"] == "OA_IN")
    assert oa_in["need_reply"] is True
    assert oa_in["status_effect"] == "OA1"
    assert oa_in["deadline_template_code"] == "OA_REPLY"
    assert oa_in["direction"] == "IN"
    assert oa_in["enabled"] is True

    # CLIENT_IN has need_reply=False
    client_in = next(t for t in data["items"] if t["code"] == "CLIENT_IN")
    assert client_in["need_reply"] is False


# ---------------------------------------------------------------------------
# 2. List — filter by direction
# ---------------------------------------------------------------------------


def test_list_doc_templates_filter_direction(client: TestClient, auth_headers: dict) -> None:
    """?direction=IN returns only IN templates; ?direction=OUT only OUT."""
    resp_in = client.get(BASE, headers=auth_headers, params={"direction": "IN", "page_size": 100})
    assert resp_in.status_code == 200
    items_in = resp_in.json()["items"]
    assert len(items_in) >= 1
    assert all(t["direction"] == "IN" for t in items_in)

    resp_out = client.get(BASE, headers=auth_headers, params={"direction": "OUT", "page_size": 100})
    assert resp_out.status_code == 200
    items_out = resp_out.json()["items"]
    # OA_OUT is the seeded OUT template
    assert any(t["code"] == "OA_OUT" for t in items_out)
    assert all(t["direction"] == "OUT" for t in items_out)


# ---------------------------------------------------------------------------
# 3. List — filter by enabled
# ---------------------------------------------------------------------------


def test_list_doc_templates_filter_enabled(client: TestClient, auth_headers: dict) -> None:
    """?enabled=true filters correctly; disabled templates excluded."""
    # Create a disabled template to validate the filter works
    code = _unique_code("DIS")
    _create_template(client, auth_headers, code=code, enabled=False)

    resp_enabled = client.get(
        BASE, headers=auth_headers, params={"enabled": True, "page_size": 100}
    )
    assert resp_enabled.status_code == 200
    enabled_codes = {t["code"] for t in resp_enabled.json()["items"]}
    # The disabled one should NOT appear
    assert code not in enabled_codes

    resp_disabled = client.get(
        BASE, headers=auth_headers, params={"enabled": False, "page_size": 100}
    )
    assert resp_disabled.status_code == 200
    disabled_codes = {t["code"] for t in resp_disabled.json()["items"]}
    assert code in disabled_codes


# ---------------------------------------------------------------------------
# 4. List — search q
# ---------------------------------------------------------------------------


def test_list_doc_templates_search_q(client: TestClient, auth_headers: dict) -> None:
    """?q=OA returns templates with 'OA' in code or name."""
    resp = client.get(BASE, headers=auth_headers, params={"q": "OA", "page_size": 100})
    assert resp.status_code == 200
    items = resp.json()["items"]
    # At least OA_IN and OA_OUT should match
    codes = {t["code"] for t in items}
    assert "OA_IN" in codes
    assert "OA_OUT" in codes

    # Every result should contain "oa" in code or name (case-insensitive)
    for t in items:
        assert "oa" in t["code"].lower() or "oa" in t["name"].lower(), (
            f"Template {t['code']} ({t['name']}) does not match search 'OA'"
        )


# ---------------------------------------------------------------------------
# 5. Create — full payload with all SPEC fields
# ---------------------------------------------------------------------------


def test_create_doc_template(client: TestClient, auth_headers: dict) -> None:
    """POST creates template with all SPEC fields, returns 201."""
    code = _unique_code("FULL")
    payload = {
        "code": code,
        "name": f"Full Template {code}",
        "direction": "OUT",
        "enabled": True,
        "status_effect": "PENDING",
        "status_restore": "ACTIVE",
        "deadline_template_code": "OA_REPLY",
        "fee_draft_type": "GRANT_FEE",
        "fee_item_list": '[{"code": "REG", "amount": 100}]',
        "need_reply": True,
        "reply_to_template_code": "OA_IN",
        "input_fields": '[{"name": "ref", "type": "text"}]',
    }
    resp = client.post(BASE, headers=auth_headers, json=payload)
    assert resp.status_code == 201, resp.text

    body = resp.json()
    assert body["code"] == code
    assert body["direction"] == "OUT"
    assert body["enabled"] is True
    assert body["status_effect"] == "PENDING"
    assert body["status_restore"] == "ACTIVE"
    assert body["deadline_template_code"] == "OA_REPLY"
    assert body["fee_draft_type"] == "GRANT_FEE"
    assert body["fee_item_list"] == '[{"code": "REG", "amount": 100}]'
    assert body["need_reply"] is True
    assert body["reply_to_template_code"] == "OA_IN"
    assert body["input_fields"] == '[{"name": "ref", "type": "text"}]'
    assert "id" in body
    assert "created_at" in body
    assert "updated_at" in body


# ---------------------------------------------------------------------------
# 6. Create — minimal (defaults applied)
# ---------------------------------------------------------------------------


def test_create_doc_template_minimal(client: TestClient, auth_headers: dict) -> None:
    """POST with only code+name; defaults: direction=IN, enabled=True, need_reply=False."""
    code = _unique_code("MIN")
    resp = client.post(
        BASE,
        headers=auth_headers,
        json={"code": code, "name": f"Minimal {code}"},
    )
    assert resp.status_code == 201, resp.text

    body = resp.json()
    assert body["code"] == code
    assert body["direction"] == "IN"
    assert body["enabled"] is True
    assert body["need_reply"] is False
    # Optional SPEC fields should be None
    assert body["status_effect"] is None
    assert body["status_restore"] is None
    assert body["deadline_template_code"] is None
    assert body["fee_draft_type"] is None
    assert body["fee_item_list"] is None
    assert body["reply_to_template_code"] is None
    assert body["input_fields"] is None


# ---------------------------------------------------------------------------
# 7. Create — duplicate code rejected
# ---------------------------------------------------------------------------


def test_create_doc_template_duplicate_code_rejected(
    client: TestClient, auth_headers: dict
) -> None:
    """POST with an existing code returns 409."""
    code = _unique_code("DUP")
    # First create succeeds
    r1 = client.post(
        BASE,
        headers=auth_headers,
        json={"code": code, "name": "First"},
    )
    assert r1.status_code == 201, r1.text

    # Duplicate create fails
    r2 = client.post(
        BASE,
        headers=auth_headers,
        json={"code": code, "name": "Duplicate"},
    )
    assert r2.status_code == 409
    error_body = r2.json()
    assert error_body["error"]["code"] == "DOC_TEMPLATE_CODE_EXISTS"


# ---------------------------------------------------------------------------
# 8. Get by ID
# ---------------------------------------------------------------------------


def test_get_doc_template_by_id(client: TestClient, auth_headers: dict) -> None:
    """GET /doc-templates/{id} returns 200 with correct fields."""
    created = _create_template(
        client,
        auth_headers,
        status_effect="GET_TEST",
        need_reply=True,
    )
    template_id = created["id"]

    resp = client.get(f"{BASE}/{template_id}", headers=auth_headers)
    assert resp.status_code == 200

    body = resp.json()
    assert body["id"] == template_id
    assert body["code"] == created["code"]
    assert body["name"] == created["name"]
    assert body["status_effect"] == "GET_TEST"
    assert body["need_reply"] is True
    assert "created_at" in body
    assert "updated_at" in body


# ---------------------------------------------------------------------------
# 9. Get — not found
# ---------------------------------------------------------------------------


def test_get_doc_template_not_found(client: TestClient, auth_headers: dict) -> None:
    """GET /doc-templates/{nonexistent} returns 404."""
    fake_id = str(uuid4())
    resp = client.get(f"{BASE}/{fake_id}", headers=auth_headers)
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "DOC_TEMPLATE_NOT_FOUND"


# ---------------------------------------------------------------------------
# 10. Update — standard
# ---------------------------------------------------------------------------


def test_update_doc_template(client: TestClient, auth_headers: dict) -> None:
    """PUT updates specified fields, others unchanged."""
    created = _create_template(
        client,
        auth_headers,
        direction="IN",
        status_effect="BEFORE",
        need_reply=False,
    )
    template_id = created["id"]

    resp = client.put(
        f"{BASE}/{template_id}",
        headers=auth_headers,
        json={
            "name": "Updated Name",
            "status_effect": "AFTER",
            "need_reply": True,
            "fee_draft_type": "NEW_FEE",
        },
    )
    assert resp.status_code == 200, resp.text

    body = resp.json()
    assert body["name"] == "Updated Name"
    assert body["status_effect"] == "AFTER"
    assert body["need_reply"] is True
    assert body["fee_draft_type"] == "NEW_FEE"
    # Direction was not sent in update, should remain unchanged
    assert body["direction"] == "IN"
    assert body["code"] == created["code"]


# ---------------------------------------------------------------------------
# 11. Update — not found
# ---------------------------------------------------------------------------


def test_update_doc_template_not_found(client: TestClient, auth_headers: dict) -> None:
    """PUT nonexistent ID returns 404."""
    fake_id = str(uuid4())
    resp = client.put(
        f"{BASE}/{fake_id}",
        headers=auth_headers,
        json={"name": "Does Not Matter"},
    )
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "DOC_TEMPLATE_NOT_FOUND"


# ---------------------------------------------------------------------------
# 12. Update — partial (only enabled)
# ---------------------------------------------------------------------------


def test_update_doc_template_partial(client: TestClient, auth_headers: dict) -> None:
    """PUT only enabled=false; other fields unchanged."""
    created = _create_template(
        client,
        auth_headers,
        status_effect="PARTIAL_TEST",
        need_reply=True,
    )
    template_id = created["id"]

    resp = client.put(
        f"{BASE}/{template_id}",
        headers=auth_headers,
        json={"enabled": False},
    )
    assert resp.status_code == 200, resp.text

    body = resp.json()
    assert body["enabled"] is False
    # Other fields should be preserved
    assert body["code"] == created["code"]
    assert body["name"] == created["name"]
    assert body["status_effect"] == "PARTIAL_TEST"
    assert body["need_reply"] is True
    assert body["direction"] == created["direction"]


# ---------------------------------------------------------------------------
# 13. List — pagination
# ---------------------------------------------------------------------------


def test_list_doc_templates_pagination(client: TestClient, auth_headers: dict) -> None:
    """Verify page/page_size/total work correctly."""
    # Get total count first
    resp_all = client.get(BASE, headers=auth_headers, params={"page": 1, "page_size": 100})
    assert resp_all.status_code == 200
    total = resp_all.json()["total"]

    # Request page_size=2 to force pagination
    resp_p1 = client.get(BASE, headers=auth_headers, params={"page": 1, "page_size": 2})
    assert resp_p1.status_code == 200
    p1 = resp_p1.json()
    assert p1["page"] == 1
    assert p1["page_size"] == 2
    assert p1["total"] == total
    assert len(p1["items"]) == 2

    resp_p2 = client.get(BASE, headers=auth_headers, params={"page": 2, "page_size": 2})
    assert resp_p2.status_code == 200
    p2 = resp_p2.json()
    assert p2["page"] == 2
    assert p2["page_size"] == 2
    assert p2["total"] == total
    # Page 2 should have different items
    p1_ids = {t["id"] for t in p1["items"]}
    p2_ids = {t["id"] for t in p2["items"]}
    assert p1_ids.isdisjoint(p2_ids), "Page 1 and page 2 items should not overlap"


# ---------------------------------------------------------------------------
# 14. Unauthorized — no auth token
# ---------------------------------------------------------------------------


def test_doc_template_unauthorized(client: TestClient) -> None:
    """No auth token returns 401 for all doc-template endpoints."""
    # List
    resp_list = client.get(BASE)
    assert resp_list.status_code == 401

    # Create
    resp_create = client.post(BASE, json={"code": "NOAUTH", "name": "No Auth"})
    assert resp_create.status_code == 401

    # Get by ID
    resp_get = client.get(f"{BASE}/{uuid4()}")
    assert resp_get.status_code == 401

    # Update
    resp_put = client.put(f"{BASE}/{uuid4()}", json={"name": "No Auth Update"})
    assert resp_put.status_code == 401
