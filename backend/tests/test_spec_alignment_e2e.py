"""Spec-alignment E2E integration tests.

Test 1: OA workflow — Case → Doc(OA_IN) → auto-task → Doc(OA_OUT reply) → task stays open
Test 2: Billing workflow — Case → Doc(GRANT_NOTICE) → explicit fee draft → bill → payment → offset → reverse
"""

from __future__ import annotations

import uuid
from decimal import Decimal

from sqlalchemy import select

from app.modules.fees.models import T_GrantFeeTask


def _uid(prefix: str = "E2E") -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8].upper()}"


# ---------------------------------------------------------------------------
# Test 1: OA workflow end-to-end
# ---------------------------------------------------------------------------


def test_e2e_oa_workflow(client, auth_headers):
    """Full OA lifecycle: Case → OA_IN → task → OA_OUT reply → task remains open."""

    # Step 1: Create client
    cli_resp = client.post(
        "/api/v1/clients",
        json={
            "name_cn": f"E2E客户-{_uid('CLI')}",
            "name_en": "E2E Test Client",
            "client_type": "CORPORATE",
            "default_currency": "CNY",
            "is_active": True,
        },
        headers=auth_headers,
    )
    assert cli_resp.status_code == 201, f"Client create failed: {cli_resp.text}"
    client_id = cli_resp.json()["id"]

    # Step 2: Create case
    case_no = _uid("CASE")
    case_resp = client.post(
        "/api/v1/cases",
        json={
            "case_no": case_no,
            "case_type": "NORMAL",
            "patent_category": "INV",
            "flow_dir": "CN_DOMESTIC",
            "fee_reduction": "0",
            "client_id": client_id,
            "title_cn": "E2E测试案件",
        },
        headers=auth_headers,
    )
    assert case_resp.status_code == 201, f"Case create failed: {case_resp.text}"
    case_data = case_resp.json()
    case_id = case_data["id"]
    assert case_data["status"] == "NOT_FILED"

    # Step 3: Find OA_IN doc template
    tmpl_resp = client.get("/api/v1/doc-templates?q=OA_IN", headers=auth_headers)
    assert tmpl_resp.status_code == 200
    oa_in_items = [t for t in tmpl_resp.json()["items"] if t["code"] == "OA_IN"]
    assert len(oa_in_items) == 1, "OA_IN template not found"
    oa_in_tmpl = oa_in_items[0]
    assert oa_in_tmpl["status_effect"] == "OA1"
    assert oa_in_tmpl["deadline_template_code"] == "OA_REPLY"

    # Also find OA_OUT template for later use
    tmpl_resp2 = client.get("/api/v1/doc-templates?q=OA_OUT", headers=auth_headers)
    assert tmpl_resp2.status_code == 200
    oa_out_items = [t for t in tmpl_resp2.json()["items"] if t["code"] == "OA_OUT"]
    assert len(oa_out_items) == 1, "OA_OUT template not found"
    oa_out_tmpl = oa_out_items[0]

    # Step 4: Create OA_IN document
    doc_in_resp = client.post(
        "/api/v1/documents",
        json={
            "case_id": case_id,
            "doc_template_id": oa_in_tmpl["id"],
            "direction": "IN",
            "doc_date": "2026-01-15",
            "title": "E2E OA收文",
            "official_due_date": "2026-05-15",
            "official_due_date_source": "MANUAL_OFFICIAL_NOTICE",
            "official_due_date_status": "CONFIRMED",
        },
        headers=auth_headers,
    )
    assert doc_in_resp.status_code == 201, f"OA_IN doc create failed: {doc_in_resp.text}"
    doc_in_id = doc_in_resp.json()["id"]
    assert doc_in_resp.headers.get("X-Auto-Tasks-Created") == "1"

    # Step 5: Verify case status changed to OA1
    case_check = client.get(f"/api/v1/cases/{case_id}", headers=auth_headers)
    assert case_check.status_code == 200
    assert case_check.json()["status"] == "OA1"

    # Step 6: Verify auto-created task with correct dates
    tasks_resp = client.get(f"/api/v1/tasks?case_id={case_id}", headers=auth_headers)
    assert tasks_resp.status_code == 200
    tasks_data = tasks_resp.json()
    open_tasks = [t for t in tasks_data["items"] if t["status"] == "OPEN"]
    assert len(open_tasks) == 1, f"Expected 1 OPEN task, got {len(open_tasks)}"
    task = open_tasks[0]
    task_id = task["id"]
    # 2026-01-15 + 120 days = 2026-05-15
    assert str(task["due_date"]) == "2026-05-15"
    # 2026-05-15 - 14 days = 2026-05-01
    assert str(task["internal_due_date"]) == "2026-05-01"

    # Step 7: Verify task log contains AUTO_CREATE_FROM_DOCUMENT
    logs_resp = client.get(f"/api/v1/tasks/{task_id}/logs", headers=auth_headers)
    assert logs_resp.status_code == 200
    log_actions = [log["action"] for log in logs_resp.json()]
    assert "AUTO_CREATE_FROM_DOCUMENT" in log_actions

    # Step 8: Create OA_OUT document (reply to OA_IN)
    doc_out_resp = client.post(
        "/api/v1/documents",
        json={
            "case_id": case_id,
            "doc_template_id": oa_out_tmpl["id"],
            "direction": "OUT",
            "doc_date": "2026-03-01",
            "title": "E2E OA答复",
            "reply_to_id": doc_in_id,
        },
        headers=auth_headers,
    )
    assert doc_out_resp.status_code == 201, f"OA_OUT doc create failed: {doc_out_resp.text}"

    # Step 9: Verify task remains OPEN until official receipt archive
    tasks_resp2 = client.get(f"/api/v1/tasks?case_id={case_id}", headers=auth_headers)
    assert tasks_resp2.status_code == 200
    matching_tasks = [t for t in tasks_resp2.json()["items"] if t["id"] == task_id]
    assert len(matching_tasks) == 1
    assert matching_tasks[0]["status"] == "OPEN"

    # Check done_at via the detail endpoint (TaskOut has done_at)
    task_detail = client.get(f"/api/v1/tasks/{task_id}", headers=auth_headers)
    assert task_detail.status_code == 200
    task_detail_data = task_detail.json()
    assert task_detail_data["done_at"] is None

    # Step 10: Verify task log has no completion evidence before receipt archive
    logs_resp2 = client.get(f"/api/v1/tasks/{task_id}/logs", headers=auth_headers)
    assert logs_resp2.status_code == 200
    log_actions2 = [log["action"] for log in logs_resp2.json()]
    assert "AUTO_WRITEOFF" not in log_actions2

    # Step 11: Verify original doc reply_date is set
    doc_in_check = client.get(f"/api/v1/documents/{doc_in_id}", headers=auth_headers)
    assert doc_in_check.status_code == 200
    assert doc_in_check.json()["reply_date"] == "2026-03-01"

    # Step 12: Verify case appears in advanced search by client_id + status
    search_resp = client.get(
        f"/api/v1/cases?client_id={client_id}&status=OA1", headers=auth_headers
    )
    assert search_resp.status_code == 200
    found_cases = [c for c in search_resp.json()["items"] if c["id"] == case_id]
    assert len(found_cases) == 1


# ---------------------------------------------------------------------------
# Test 2: Billing workflow end-to-end
# ---------------------------------------------------------------------------


def test_e2e_billing_workflow(client, auth_headers, session_factory):
    """Financial chain: grant source → explicit draft → bill → payment → offset → reverse."""

    # Step 1: Create client
    cli_resp = client.post(
        "/api/v1/clients",
        json={
            "name_cn": f"E2E客户-{_uid('CLI')}",
            "name_en": "E2E Billing Client",
            "client_type": "CORPORATE",
            "default_currency": "CNY",
            "is_active": True,
        },
        headers=auth_headers,
    )
    assert cli_resp.status_code == 201, f"Client create failed: {cli_resp.text}"
    client_id = cli_resp.json()["id"]

    # Step 2: Create case
    case_resp = client.post(
        "/api/v1/cases",
        json={
            "case_no": _uid("CASE"),
            "case_type": "NORMAL",
            "patent_category": "INV",
            "flow_dir": "CN_DOMESTIC",
            "fee_reduction": "0",
            "client_id": client_id,
            "title_cn": "E2E计费测试案件",
        },
        headers=auth_headers,
    )
    assert case_resp.status_code == 201, f"Case create failed: {case_resp.text}"
    case_id = case_resp.json()["id"]

    # Step 3: Find GRANT_NOTICE doc template, then create document
    tmpl_resp = client.get("/api/v1/doc-templates?q=GRANT_NOTICE", headers=auth_headers)
    assert tmpl_resp.status_code == 200
    grant_items = [t for t in tmpl_resp.json()["items"] if t["code"] == "GRANT_NOTICE"]
    assert len(grant_items) == 1, "GRANT_NOTICE template not found"
    grant_tmpl = grant_items[0]

    doc_resp = client.post(
        "/api/v1/documents",
        json={
            "case_id": case_id,
            "doc_template_id": grant_tmpl["id"],
            "direction": "IN",
            "doc_date": "2026-02-01",
            "title": "E2E授权通知书",
            "official_due_date": "2026-04-15",
            "official_due_date_source": "MANUAL_OFFICIAL_NOTICE",
            "official_due_date_status": "CONFIRMED",
        },
        headers=auth_headers,
    )
    assert doc_resp.status_code == 201, f"GRANT_NOTICE doc create failed: {doc_resp.text}"
    document_id = doc_resp.json()["id"]

    # Grant registration creates its source-lineage task, but no generic fee draft.
    assert doc_resp.headers.get("X-Auto-Fee-Draft-Created") is None
    with session_factory() as db:
        grant_tasks = list(
            db.execute(select(T_GrantFeeTask).where(T_GrantFeeTask.case_id == case_id)).scalars()
        )
        assert len(grant_tasks) == 1
        assert grant_tasks[0].source_document_id == document_id
        assert grant_tasks[0].deadline_source == "MANUAL_OFFICIAL_NOTICE"
        assert str(grant_tasks[0].due_date) == "2026-04-15"
        assert grant_tasks[0].draft_generated is False

    # The grant source task is separate from the generic document-task header.
    assert doc_resp.headers.get("X-Auto-Tasks-Created") == "0"

    drafts_before = client.get(f"/api/v1/fees/drafts?case_id={case_id}", headers=auth_headers)
    assert drafts_before.status_code == 200
    assert drafts_before.json()["items"] == []

    # Step 4: Verify case status changed to GRANT_PENDING
    case_check = client.get(f"/api/v1/cases/{case_id}", headers=auth_headers)
    assert case_check.status_code == 200
    assert case_check.json()["status"] == "GRANT_PENDING"

    # Step 5: Explicitly create and verify the fee draft through the public API
    draft_create = client.post(
        "/api/v1/fees/drafts",
        json={
            "case_id": case_id,
            "client_id": client_id,
            "draft_type": "GRANT_FEE",
            "currency": "CNY",
        },
        headers=auth_headers,
    )
    assert draft_create.status_code == 201, f"Fee draft create failed: {draft_create.text}"
    fee_draft_id = draft_create.json()["id"]

    draft_detail = client.get(f"/api/v1/fees/drafts/{fee_draft_id}", headers=auth_headers)
    assert draft_detail.status_code == 200
    draft_data = draft_detail.json()
    assert draft_data["draft_type"] == "GRANT_FEE"
    assert draft_data["client_id"] == client_id

    # Step 6: Create fee rate
    rate_resp = client.post(
        "/api/v1/fees/rates",
        json={
            "fee_code": _uid("RATE"),
            "fee_name": "Grant Filing Fee",
            "fee_type": "GOV",
            "currency": "CNY",
            "default_amount": "500.00",
            "enabled": True,
        },
        headers=auth_headers,
    )
    assert rate_resp.status_code == 201, f"Fee rate create failed: {rate_resp.text}"
    rate_id = rate_resp.json()["id"]

    # Step 7: Add fee item to the explicit draft
    item_resp = client.post(
        f"/api/v1/fees/drafts/{fee_draft_id}/items",
        json={"rate_id": rate_id, "quantity": 1, "unit_price": "500.00"},
        headers=auth_headers,
    )
    assert item_resp.status_code == 201, f"Fee item create failed: {item_resp.text}"

    # Step 8: Verify draft amount via list endpoint
    drafts_list = client.get(f"/api/v1/fees/drafts?case_id={case_id}", headers=auth_headers)
    assert drafts_list.status_code == 200
    draft_in_list = next((d for d in drafts_list.json()["items"] if d["id"] == fee_draft_id), None)
    assert draft_in_list is not None, "Explicit draft not found in list"
    assert Decimal(str(draft_in_list["amount"])) == Decimal("500")

    # Step 9: Create bill from draft
    bill_no = _uid("BILL")
    bill_resp = client.post(
        "/api/v1/bills/from-drafts",
        json={"draft_ids": [fee_draft_id], "bill_no": bill_no},
        headers=auth_headers,
    )
    assert bill_resp.status_code == 201, f"Bill create failed: {bill_resp.text}"
    bill_data = bill_resp.json()
    bill_id = bill_data["id"]
    assert bill_data["status"] == "UNSETTLED"

    # Step 10: Verify bill in list with amount and balance
    bills_list = client.get("/api/v1/bills", headers=auth_headers)
    assert bills_list.status_code == 200
    bill_in_list = next((b for b in bills_list.json()["items"] if b["id"] == bill_id), None)
    assert bill_in_list is not None, "Bill not found in list"
    assert Decimal(str(bill_in_list["amount"])) == Decimal("500")
    assert Decimal(str(bill_in_list["balance"])) == Decimal("500")

    # Step 11: Create payment
    pay_resp = client.post(
        "/api/v1/payments",
        json={
            "client_id": client_id,
            "amount": "500.00",
            "pay_no": _uid("PAY"),
            "currency": "CNY",
        },
        headers=auth_headers,
    )
    assert pay_resp.status_code == 201, f"Payment create failed: {pay_resp.text}"
    payment_id = pay_resp.json()["id"]

    # Step 12: Get payment detail and verify payment line balance
    pay_detail = client.get(f"/api/v1/payments/{payment_id}", headers=auth_headers)
    assert pay_detail.status_code == 200
    pay_lines = pay_detail.json()["payment_lines"]
    assert len(pay_lines) > 0, "No payment lines"
    payment_line_id = pay_lines[0]["id"]
    assert Decimal(str(pay_lines[0]["balance_amt"])) == Decimal("500")

    # Step 13: Create offset
    offset_resp = client.post(
        "/api/v1/offsets",
        json={
            "payment_line_id": payment_line_id,
            "bill_id": bill_id,
            "offset_amt": "500.00",
            "offset_date": "2026-02-26",
        },
        headers=auth_headers,
    )
    assert offset_resp.status_code == 201, f"Offset create failed: {offset_resp.text}"
    offset_data = offset_resp.json()
    offset_id = offset_data["id"]
    assert offset_data["is_reversed"] is False

    # Step 14: Verify bill is settled
    bills_list2 = client.get("/api/v1/bills", headers=auth_headers)
    assert bills_list2.status_code == 200
    bill_after_offset = next((b for b in bills_list2.json()["items"] if b["id"] == bill_id), None)
    assert bill_after_offset is not None
    assert bill_after_offset["status"] == "SETTLED"
    assert Decimal(str(bill_after_offset["balance"])) == Decimal("0")

    # Step 15: Verify payment line allocated/balance
    pay_detail2 = client.get(f"/api/v1/payments/{payment_id}", headers=auth_headers)
    assert pay_detail2.status_code == 200
    pl_after = pay_detail2.json()["payment_lines"][0]
    assert Decimal(str(pl_after["allocated_amt"])) == Decimal("500")
    assert Decimal(str(pl_after["balance_amt"])) == Decimal("0")

    # Step 16: Verify case receipt
    receipt_resp = client.get(f"/api/v1/cases/{case_id}/receipts", headers=auth_headers)
    assert receipt_resp.status_code == 200
    assert Decimal(str(receipt_resp.json()["received_amt"])) == Decimal("500")

    # Step 17: Reverse offset
    reverse_resp = client.post(f"/api/v1/offsets/{offset_id}/reverse", headers=auth_headers)
    assert reverse_resp.status_code == 200, f"Offset reverse failed: {reverse_resp.text}"
    assert reverse_resp.json()["is_reversed"] is True

    # Step 18: Verify bill back to UNSETTLED
    bills_list3 = client.get("/api/v1/bills", headers=auth_headers)
    assert bills_list3.status_code == 200
    bill_after_reverse = next((b for b in bills_list3.json()["items"] if b["id"] == bill_id), None)
    assert bill_after_reverse is not None
    assert bill_after_reverse["status"] == "UNSETTLED"
    assert Decimal(str(bill_after_reverse["balance"])) == Decimal("500")

    # Step 19: Verify payment balance restored
    pay_detail3 = client.get(f"/api/v1/payments/{payment_id}", headers=auth_headers)
    assert pay_detail3.status_code == 200
    pl_restored = pay_detail3.json()["payment_lines"][0]
    assert Decimal(str(pl_restored["balance_amt"])) == Decimal("500")
