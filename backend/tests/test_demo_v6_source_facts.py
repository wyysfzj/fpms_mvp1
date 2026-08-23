from __future__ import annotations

import runpy
from pathlib import Path

from sqlalchemy import select

from app.api import deps
from app.modules.cases.models import CaseActivityEvent
from app.modules.fees.models import (
    FeeItem,
    FeeObligation,
    FeeObligationDraftItemLink,
    FeeObligationLine,
)


def test_service_draft_source_facts_are_authoritative_and_multiline(
    client,
    auth_headers,
    session_factory,
    tmp_path,
    monkeypatch,
) -> None:
    helpers = runpy.run_path(
        str(Path(__file__).with_name("test_demo_v6_service_adjustment.py"))
    )
    _case_id, _obligation_id, draft_id = helpers["_create_open_service_draft"](
        client, auth_headers, session_factory, tmp_path, monkeypatch
    )

    response = client.get(
        f"/api/v1/fees/drafts/{draft_id}/source-facts",
        headers=auth_headers,
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["draft_id"] == draft_id
    assert payload["draft_status"] == "OPEN"
    assert payload["fee_domain"] == "SERVICE"
    assert [row["fee_code"] for row in payload["lines"]] == [
        "FWSQDJ001",
        "FWSQDJ002",
    ]
    assert [row["quantity"] for row in payload["lines"]] == [1, 1]
    assert [row["unit_price"] for row in payload["lines"]] == [
        "1200.00",
        "300.00",
    ]
    assert [row["amount"] for row in payload["lines"]] == [
        "1200.00",
        "300.00",
    ]
    assert [row["adjustable"] for row in payload["lines"]] == [False, True]
    assert all(len(row["source_sha256"]) == 64 for row in payload["lines"])

    with session_factory() as transaction:
        adjustable = transaction.scalar(
            select(FeeItem).where(
                FeeItem.draft_id == draft_id,
                FeeItem.fee_code == "FWSQDJ002",
            )
        )
        assert adjustable is not None
        adjustable_id = adjustable.id
    adjusted = client.post(
        f"/api/v1/fees/drafts/{draft_id}/demo-service-adjustment",
        json={
            "item_id": adjustable_id,
            "expected_quantity": 1,
            "new_quantity": 2,
            "reason": "客户确认增加一份附加文件处理",
            "idempotency_key": "v6-source-facts-adjustment",
        },
        headers=auth_headers,
    )
    assert adjusted.status_code == 201, adjusted.text
    after = client.get(
        f"/api/v1/fees/drafts/{draft_id}/source-facts", headers=auth_headers
    )
    assert after.status_code == 200, after.text
    after_rows = {row["fee_code"]: row for row in after.json()["lines"]}
    assert after_rows["FWSQDJ002"]["quantity"] == 2
    assert after_rows["FWSQDJ002"]["amount"] == "600.00"
    assert after_rows["FWSQDJ002"]["adjustment_activity_id"] == adjusted.json()[
        "adjustment_activity_id"
    ]
    assert after_rows["FWSQDJ002"]["adjustment_reason"] == (
        "客户确认增加一份附加文件处理"
    )
    locked = client.post(f"/api/v1/fees/drafts/{draft_id}/lock", headers=auth_headers)
    assert locked.status_code == 200
    locked_facts = client.get(
        f"/api/v1/fees/drafts/{draft_id}/source-facts", headers=auth_headers
    )
    assert locked_facts.status_code == 200
    assert locked_facts.json()["draft_status"] == "LOCKED"


def test_source_facts_permission_not_found_and_validation_boundaries(
    client,
    auth_headers,
    session_factory,
    tmp_path,
    monkeypatch,
) -> None:
    helpers = runpy.run_path(
        str(Path(__file__).with_name("test_demo_v6_service_adjustment.py"))
    )
    _case_id, _obligation_id, draft_id = helpers["_create_open_service_draft"](
        client, auth_headers, session_factory, tmp_path, monkeypatch
    )
    path = f"/api/v1/fees/drafts/{draft_id}/source-facts"
    assert client.get(path).status_code == 401
    original_permissions = deps.get_user_permissions
    monkeypatch.setattr(deps, "get_user_permissions", lambda _db, _user_id: set())
    denied = client.get(path, headers=auth_headers)
    assert denied.status_code == 403
    assert denied.json()["error"]["details"]["required_perm"] == "Fee.Draft.Read"
    monkeypatch.setattr(deps, "get_user_permissions", original_permissions)
    assert client.get(
        "/api/v1/fees/drafts/00000000-0000-0000-0000-000000000000/source-facts",
        headers=auth_headers,
    ).status_code == 404
    assert client.get(
        "/api/v1/fees/drafts/not-a-uuid/source-facts", headers=auth_headers
    ).status_code == 422


def test_gov_draft_source_facts_use_active_rate_binding(
    client,
    auth_headers,
    session_factory,
    tmp_path,
    monkeypatch,
) -> None:
    helpers = runpy.run_path(
        str(Path(__file__).with_name("test_demo_v6_grant_official_fee.py"))
    )
    runtime = helpers["runtime_bundle"].__wrapped__(tmp_path, monkeypatch)
    next(runtime)
    try:
        with session_factory() as transaction:
            _case, _document, task, evidence, _book = helpers["_seed"](transaction)
            preview = helpers["demo_official_fee"].preview_grant_official_fees(
                transaction, grant_fee_task_id=task.id
            )
            result = helpers["demo_official_fee"].confirm_grant_official_fees(
                helpers["_command"](task, evidence, preview), transaction
            )
            transaction.commit()
            draft_id = result.draft_id

        response = client.get(
            f"/api/v1/fees/drafts/{draft_id}/source-facts", headers=auth_headers
        )
        assert response.status_code == 200, response.text
        payload = response.json()
        assert payload["fee_domain"] == "GOV"
        assert [row["source_authority"] for row in payload["lines"]] == [
            "CNIPA",
            "CNIPA",
        ]
        assert [row["activation_status"] for row in payload["lines"]] == [
            "APPROVED_ACTIVE",
            "APPROVED_ACTIVE",
        ]
        assert [row["adjustable"] for row in payload["lines"]] == [False, False]
        assert {row["effective_date"] for row in payload["lines"]} == {
            "2026-03-30",
            "2026-04-15",
        }
    finally:
        try:
            next(runtime)
        except StopIteration:
            pass


def test_source_facts_reject_corrupt_service_lineage(
    client,
    auth_headers,
    session_factory,
    tmp_path,
    monkeypatch,
) -> None:
    helpers = runpy.run_path(
        str(Path(__file__).with_name("test_demo_v6_service_adjustment.py"))
    )
    _case_id, _obligation_id, draft_id = helpers["_create_open_service_draft"](
        client, auth_headers, session_factory, tmp_path, monkeypatch
    )
    with session_factory() as transaction:
        item = transaction.scalar(select(FeeItem).where(FeeItem.draft_id == draft_id))
        link = transaction.scalar(
            select(FeeObligationDraftItemLink).where(
                FeeObligationDraftItemLink.fee_item_id == item.id
            )
        )
        line = transaction.get(FeeObligationLine, link.obligation_line_id)
        obligation = transaction.get(FeeObligation, line.obligation_id)
        source = transaction.get(CaseActivityEvent, obligation.source_activity_id)
        source.payload_json = "[" * 1100 + "0" + "]" * 1100
        transaction.commit()
    response = client.get(
        f"/api/v1/fees/drafts/{draft_id}/source-facts", headers=auth_headers
    )
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "DEMO_V6_DRAFT_SOURCE_FACTS_INVALID"
