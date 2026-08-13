"""Tests for Batch B3: Document→FeeDraft Auto-Linking.

Covers:
- GRANT_NOTICE registration with a confirmed due creates no generic fee draft
- GRANT_NOTICE registration creates no zero-value draft or auto-draft header
- GRANT_NOTICE registration for a client-linked case creates no generic fee draft
- No fee draft created when doc has no template
- No fee draft created for templates without fee_draft_type (e.g. CLIENT_IN)
- fee_item_list JSON → FeeItems auto-created
- Malformed fee_item_list → draft still created, no items, no crash
"""

from __future__ import annotations

import json
import uuid

from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.modules.fees.models import FeeItem

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DOC_BASE = "/api/v1/documents"
DOC_TMPL_BASE = "/api/v1/doc-templates"
CASE_BASE = "/api/v1/cases"
FEE_DRAFT_BASE = "/api/v1/fees/drafts"
CLIENT_BASE = "/api/v1/clients"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _unique(prefix: str = "B3") -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8].upper()}"


def _create_client(client: TestClient, auth_headers: dict, **overrides) -> dict:
    """Create a test client, return response JSON."""
    payload = {
        "name_cn": f"测试客户-{_unique()}",
        "client_code": _unique("CLI"),
        **overrides,
    }
    resp = client.post(CLIENT_BASE, json=payload, headers=auth_headers)
    assert resp.status_code == 201, f"Client creation failed: {resp.text}"
    return resp.json()


def _create_applicant(client: TestClient, auth_headers: dict) -> dict:
    suffix = uuid.uuid4().hex[:8].upper()
    payload = {
        "code": f"AP-{suffix}",
        "name_cn": f"B3测试申请人-{suffix}",
        "applicant_type": "ENTITY",
        "is_active": True,
    }
    resp = client.post("/api/v1/applicants", json=payload, headers=auth_headers)
    assert resp.status_code == 201, f"Applicant creation failed: {resp.text}"
    return resp.json()


def _create_case(client: TestClient, auth_headers: dict, **overrides) -> dict:
    """Create a test case, return response JSON."""
    applicant = _create_applicant(client, auth_headers)
    payload = {
        "case_no": _unique("CASE"),
        "case_type": "NORMAL",
        "patent_category": "INV",
        "flow_dir": "CN_DOMESTIC",
        "fee_reduction": "0",
        "title_cn": "B3 Test Case",
        "applicants": [
            {
                "seq": 1,
                "is_first": True,
                "applicant_id": applicant["id"],
                "name_cn": applicant["name_cn"],
            }
        ],
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


def _create_doc_template(client: TestClient, auth_headers: dict, **overrides) -> dict:
    """Create a custom doc template, return response JSON."""
    code = _unique("TMPL")
    payload = {
        "code": code,
        "name": f"Test Template {code}",
        "direction": "IN",
        **overrides,
    }
    resp = client.post(DOC_TMPL_BASE, json=payload, headers=auth_headers)
    assert resp.status_code == 201, f"DocTemplate creation failed: {resp.text}"
    return resp.json()


def _create_document_raw(
    client: TestClient,
    auth_headers: dict,
    case_id: str,
    direction: str = "IN",
    **overrides,
):
    """Create a document, return the raw httpx Response (for header inspection)."""
    payload = {
        "case_id": case_id,
        "direction": direction,
        "doc_date": "2026-02-20",
        "title": f"B3 Test Doc {direction}",
        **overrides,
    }
    resp = client.post(DOC_BASE, json=payload, headers=auth_headers)
    return resp


def _get_fee_drafts_for_case(client: TestClient, auth_headers: dict, case_id: str) -> list[dict]:
    """List fee drafts for a case."""
    resp = client.get(
        FEE_DRAFT_BASE,
        headers=auth_headers,
        params={"case_id": case_id, "page_size": 100},
    )
    assert resp.status_code == 200, f"Fee draft list failed: {resp.text}"
    return resp.json().get("items", [])


def _get_fee_draft_detail(client: TestClient, auth_headers: dict, draft_id: str) -> dict:
    """Get fee draft detail by ID."""
    resp = client.get(f"{FEE_DRAFT_BASE}/{draft_id}", headers=auth_headers)
    assert resp.status_code == 200, f"Fee draft detail failed: {resp.text}"
    return resp.json()


# ---------------------------------------------------------------------------
# 1. GRANT_NOTICE creates no generic FeeDraft
# ---------------------------------------------------------------------------


def test_grant_notice_does_not_create_generic_fee_draft(
    client: TestClient, auth_headers: dict
) -> None:
    """Confirmed GRANT_NOTICE registration creates no generic fee draft."""
    case = _create_case(client, auth_headers)
    tmpl = _get_doc_template_by_code(client, auth_headers, "GRANT_NOTICE")

    resp = _create_document_raw(
        client,
        auth_headers,
        case["id"],
        direction="IN",
        doc_template_id=tmpl["id"],
        title="授权通知书",
        official_due_date="2026-08-28",
        official_due_date_source="MANUAL_OFFICIAL_NOTICE",
        official_due_date_status="CONFIRMED",
    )
    assert resp.status_code == 201, f"Doc creation failed: {resp.text}"
    assert resp.headers.get("X-Auto-Fee-Draft-Created") is None
    assert _get_fee_drafts_for_case(client, auth_headers, case["id"]) == []


# ---------------------------------------------------------------------------
# 2. GRANT_NOTICE creates no zero-value FeeDraft
# ---------------------------------------------------------------------------


def test_grant_notice_does_not_create_zero_value_fee_draft(
    client: TestClient, auth_headers: dict
) -> None:
    """Confirmed GRANT_NOTICE registration creates no zero-value draft."""
    case = _create_case(client, auth_headers)
    tmpl = _get_doc_template_by_code(client, auth_headers, "GRANT_NOTICE")

    resp = _create_document_raw(
        client,
        auth_headers,
        case["id"],
        direction="IN",
        doc_template_id=tmpl["id"],
        title="授权通知书-fields",
        official_due_date="2026-08-28",
        official_due_date_source="MANUAL_OFFICIAL_NOTICE",
        official_due_date_status="CONFIRMED",
    )
    assert resp.status_code == 201
    assert resp.headers.get("X-Auto-Fee-Draft-Created") is None
    assert _get_fee_drafts_for_case(client, auth_headers, case["id"]) == []


# ---------------------------------------------------------------------------
# 3. Client-linked GRANT_NOTICE creates no generic FeeDraft
# ---------------------------------------------------------------------------


def test_client_linked_grant_notice_does_not_create_generic_fee_draft(
    client: TestClient, auth_headers: dict
) -> None:
    """Confirmed GRANT_NOTICE registration has no draft side effect for a client case."""
    # Create a client first
    cl = _create_client(client, auth_headers)
    client_id = cl["id"]

    # Create case with client_id
    case = _create_case(client, auth_headers, client_id=client_id)
    assert case.get("client_id") == client_id

    # Create doc with GRANT_NOTICE
    tmpl = _get_doc_template_by_code(client, auth_headers, "GRANT_NOTICE")
    resp = _create_document_raw(
        client,
        auth_headers,
        case["id"],
        direction="IN",
        doc_template_id=tmpl["id"],
        title="授权通知书-client",
        official_due_date="2026-08-28",
        official_due_date_source="MANUAL_OFFICIAL_NOTICE",
        official_due_date_status="CONFIRMED",
    )
    assert resp.status_code == 201
    assert resp.headers.get("X-Auto-Fee-Draft-Created") is None
    assert _get_fee_drafts_for_case(client, auth_headers, case["id"]) == []


# ---------------------------------------------------------------------------
# 4. No fee draft without template
# ---------------------------------------------------------------------------


def test_no_fee_draft_without_template(client: TestClient, auth_headers: dict) -> None:
    """Doc created without doc_template_id → no X-Auto-Fee-Draft-Created header."""
    case = _create_case(client, auth_headers)

    resp = _create_document_raw(
        client,
        auth_headers,
        case["id"],
        direction="IN",
        title="Plain doc without template",
    )
    assert resp.status_code == 201, f"Doc creation failed: {resp.text}"

    # No header expected
    assert "X-Auto-Fee-Draft-Created" not in resp.headers, (
        f"Should not have X-Auto-Fee-Draft-Created header, but got: "
        f"{resp.headers.get('X-Auto-Fee-Draft-Created')}"
    )

    # No fee drafts created
    drafts = _get_fee_drafts_for_case(client, auth_headers, case["id"])
    assert len(drafts) == 0, f"Expected 0 fee drafts, got {len(drafts)}"


# ---------------------------------------------------------------------------
# 5. No fee draft for template without fee_draft_type (CLIENT_IN)
# ---------------------------------------------------------------------------


def test_no_fee_draft_for_template_without_fee_type(client: TestClient, auth_headers: dict) -> None:
    """CLIENT_IN template (no fee_draft_type) → no header, no draft."""
    case = _create_case(client, auth_headers)
    tmpl = _get_doc_template_by_code(client, auth_headers, "CLIENT_IN")

    # Confirm template has no fee_draft_type
    assert tmpl.get("fee_draft_type") is None, (
        f"CLIENT_IN should have no fee_draft_type, got: {tmpl.get('fee_draft_type')}"
    )

    resp = _create_document_raw(
        client,
        auth_headers,
        case["id"],
        direction="IN",
        doc_template_id=tmpl["id"],
        title="客户来函",
    )
    assert resp.status_code == 201

    # No header
    assert "X-Auto-Fee-Draft-Created" not in resp.headers, (
        f"CLIENT_IN template should not trigger fee draft, but got header: "
        f"{resp.headers.get('X-Auto-Fee-Draft-Created')}"
    )

    # No fee drafts
    drafts = _get_fee_drafts_for_case(client, auth_headers, case["id"])
    assert len(drafts) == 0, f"Expected 0 fee drafts for CLIENT_IN, got {len(drafts)}"


# ---------------------------------------------------------------------------
# 6. fee_item_list creates FeeItems
# ---------------------------------------------------------------------------


def test_fee_item_list_creates_items(
    client: TestClient, auth_headers: dict, session_factory: sessionmaker
) -> None:
    """Custom template with fee_item_list JSON → FeeItems created correctly."""
    fee_items_json = json.dumps(
        [
            {
                "fee_code": "REG_FEE",
                "fee_name": "登记费",
                "fee_type": "GOV",
                "amount": 200,
            },
            {
                "fee_code": "PRINT_FEE",
                "fee_name": "印刷费",
                "fee_type": "GOV",
                "quantity": 1,
                "unit_price": 50,
                "amount": 50,
            },
        ]
    )

    # Create custom template with fee_item_list
    tmpl = _create_doc_template(
        client,
        auth_headers,
        fee_draft_type="CUSTOM_FEE",
        fee_item_list=fee_items_json,
    )
    assert tmpl.get("fee_draft_type") == "CUSTOM_FEE"
    assert tmpl.get("fee_item_list") == fee_items_json

    # Create case and document
    case = _create_case(client, auth_headers)
    resp = _create_document_raw(
        client,
        auth_headers,
        case["id"],
        direction="IN",
        doc_template_id=tmpl["id"],
        title="Fee item list test doc",
    )
    assert resp.status_code == 201
    draft_id = resp.headers.get("X-Auto-Fee-Draft-Created")
    assert draft_id is not None, "Expected X-Auto-Fee-Draft-Created header"

    # Query FeeItems directly from DB (no list API available)
    with session_factory() as db:
        items = db.query(FeeItem).filter(FeeItem.draft_id == draft_id).all()

    assert len(items) == 2, f"Expected 2 FeeItems, got {len(items)}"

    # Sort by fee_code for deterministic assertions
    items_sorted = sorted(items, key=lambda x: x.fee_code or "")
    item1 = items_sorted[0]  # PRINT_FEE
    item2 = items_sorted[1]  # REG_FEE

    assert item1.fee_code == "PRINT_FEE"
    assert item1.fee_name == "印刷费"
    assert item1.fee_type == "GOV"
    assert float(item1.amount) == 50.0
    assert float(item1.quantity) == 1.0
    assert float(item1.unit_price) == 50.0

    assert item2.fee_code == "REG_FEE"
    assert item2.fee_name == "登记费"
    assert item2.fee_type == "GOV"
    assert float(item2.amount) == 200.0

    # Verify case_id is set on items
    for item in items:
        assert item.case_id == case["id"]


def test_oa_fee_template_creates_service_and_gov_items_with_totals(
    client: TestClient, auth_headers: dict, session_factory: sessionmaker
) -> None:
    """OA_FEE template creates SERVICE/GOV items and stable totals."""
    fee_items_json = json.dumps(
        [
            {
                "fee_code": "OA_SERVICE",
                "fee_name": "OA服务费",
                "fee_type": "SERVICE",
                "amount": "800.00",
            },
            {
                "fee_code": "OA_GOV",
                "fee_name": "OA官费",
                "fee_type": "GOV",
                "amount": "120.00",
            },
        ],
        ensure_ascii=False,
    )
    tmpl = _create_doc_template(
        client,
        auth_headers,
        code=f"OA-FEE-{uuid.uuid4().hex[:8].upper()}",
        name="OA费用模板",
        direction="OUT",
        fee_draft_type="OA_FEE",
        fee_item_list=fee_items_json,
    )
    case = _create_case(client, auth_headers)

    resp = _create_document_raw(
        client,
        auth_headers,
        case["id"],
        direction="OUT",
        doc_template_id=tmpl["id"],
        title="OA费用答复",
    )
    assert resp.status_code == 201, resp.text
    draft_id = resp.headers.get("X-Auto-Fee-Draft-Created")
    assert draft_id is not None

    detail = _get_fee_draft_detail(client, auth_headers, draft_id)
    assert detail["draft_type"] == "OA_FEE"
    assert float(detail["total_service"]) == 800.0
    assert float(detail["total_gov"]) == 120.0
    assert float(detail["total_misc"]) == 0.0
    assert float(detail["amount"]) == 920.0

    with session_factory() as db:
        items = db.query(FeeItem).filter(FeeItem.draft_id == draft_id).all()
    assert sorted(item.fee_type for item in items) == ["GOV", "SERVICE"]


# ---------------------------------------------------------------------------
# 7. Malformed fee_item_list → draft created, no items, no crash
# ---------------------------------------------------------------------------


def test_malformed_fee_item_list_no_crash(
    client: TestClient, auth_headers: dict, session_factory: sessionmaker
) -> None:
    """Template with invalid JSON in fee_item_list → draft still created,
    no FeeItems, no crash."""
    # Create template with malformed JSON
    tmpl = _create_doc_template(
        client,
        auth_headers,
        fee_draft_type="BAD_FEE",
        fee_item_list="NOT VALID JSON {{{",
    )
    assert tmpl.get("fee_draft_type") == "BAD_FEE"

    # Create case and document — should NOT crash
    case = _create_case(client, auth_headers)
    resp = _create_document_raw(
        client,
        auth_headers,
        case["id"],
        direction="IN",
        doc_template_id=tmpl["id"],
        title="Malformed fee item list test",
    )
    assert resp.status_code == 201, (
        f"Doc creation should succeed despite malformed JSON: {resp.text}"
    )

    # Draft should still be created
    draft_id = resp.headers.get("X-Auto-Fee-Draft-Created")
    assert draft_id is not None, (
        "Fee draft should still be created even with malformed fee_item_list"
    )

    # Verify draft exists
    detail = _get_fee_draft_detail(client, auth_headers, draft_id)
    assert detail["draft_type"] == "BAD_FEE"

    # Verify no FeeItems were created
    with session_factory() as db:
        items = db.query(FeeItem).filter(FeeItem.draft_id == draft_id).all()

    assert len(items) == 0, f"Expected 0 FeeItems for malformed JSON, got {len(items)}"
