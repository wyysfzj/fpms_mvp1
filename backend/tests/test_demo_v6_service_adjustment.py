from __future__ import annotations

import json
import runpy
from datetime import datetime
from pathlib import Path

import pytest
from sqlalchemy import func, select
from sqlalchemy.engine import Connection
from sqlalchemy.exc import OperationalError

from app.api import deps
from app.core.errors import BusinessError
from app.modules.auth.models import T_User
from app.modules.cases.models import CaseActivityEvent
from app.modules.fees import demo_service
from app.modules.fees.models import (
    FeeDraft,
    FeeItem,
    FeeObligation,
    FeeObligationDraftItemLink,
    FeeObligationLine,
)


def _create_open_service_draft(
    client,
    auth_headers,
    session_factory,
    tmp_path: Path,
    monkeypatch,
) -> tuple[str, str, str]:
    helpers = runpy.run_path(
        str(Path(__file__).with_name("test_demo_abc_runtime_service_draft.py"))
    )
    helpers["_configure_bundle"](tmp_path, monkeypatch, integrated=True)
    client_id, case_id = helpers["_seed_case"](session_factory)
    created = client.post(
        "/api/v1/fees/demo-service-obligations",
        json={"case_id": case_id, "idempotency_key": "v6-service-source-1"},
        headers=auth_headers,
    )
    assert created.status_code == 201, created.text
    obligation_id = created.json()["obligation"]["id"]
    instruction = client.post(
        f"/api/v1/fees/obligations/{obligation_id}/instruction",
        json={"instruction": "PAY", "idempotency_key": "v6-service-pay-1"},
        headers=auth_headers,
    )
    assert instruction.status_code == 200, instruction.text
    draft = client.post(
        "/api/v1/fees/drafts",
        json={
            "case_id": case_id,
            "client_id": client_id,
            "draft_type": "GENERIC",
            "currency": "CNY",
            "obligation_id": obligation_id,
        },
        headers=auth_headers,
    )
    assert draft.status_code == 201, draft.text
    return case_id, obligation_id, draft.json()["id"]


def test_adjustable_service_item_creates_one_superseding_revision(
    client,
    auth_headers,
    session_factory,
    tmp_path,
    monkeypatch,
) -> None:
    _case_id, original_obligation_id, draft_id = _create_open_service_draft(
        client, auth_headers, session_factory, tmp_path, monkeypatch
    )
    with session_factory() as transaction:
        adjustable_item = (
            transaction.query(FeeItem)
            .filter(FeeItem.draft_id == draft_id, FeeItem.fee_code == "FWSQDJ002")
            .one()
        )
        adjustable_item_id = adjustable_item.id

    response = client.post(
        f"/api/v1/fees/drafts/{draft_id}/demo-service-adjustment",
        json={
            "item_id": adjustable_item_id,
            "expected_quantity": 1,
            "new_quantity": 2,
            "reason": "客户确认增加一份附加文件处理",
            "idempotency_key": "v6-service-adjustment-1",
        },
        headers=auth_headers,
    )

    assert response.status_code == 201, response.text
    payload = response.json()
    assert payload["original_obligation_id"] == original_obligation_id
    assert payload["superseding_obligation_id"] != original_obligation_id
    assert payload["draft_id"] == draft_id
    assert payload["before_total"] == "1500.00"
    assert payload["after_total"] == "1800.00"
    assert payload["reused"] is False

    replay = client.post(
        f"/api/v1/fees/drafts/{draft_id}/demo-service-adjustment",
        json={
            "item_id": adjustable_item_id,
            "expected_quantity": 1,
            "new_quantity": 2,
            "reason": "客户确认增加一份附加文件处理",
            "idempotency_key": "v6-service-adjustment-1",
        },
        headers=auth_headers,
    )
    assert replay.status_code == 200, replay.text
    assert replay.json() == {**payload, "reused": True}

    with session_factory() as transaction:
        original = transaction.get(FeeObligation, original_obligation_id)
        replacement = transaction.get(
            FeeObligation, payload["superseding_obligation_id"]
        )
        instruction_event = transaction.get(
            CaseActivityEvent, payload["instruction_activity_id"]
        )
        replacement_recognition = transaction.get(
            CaseActivityEvent, instruction_event.source_activity_id
        )
        adjustment_event = transaction.get(
            CaseActivityEvent, replacement_recognition.source_activity_id
        )
        original_instruction = transaction.get(
            CaseActivityEvent, adjustment_event.source_activity_id
        )
        assert adjustment_event.id == payload["adjustment_activity_id"]
        assert json.loads(original_instruction.payload_json)["obligation_id"] == (
            original_obligation_id
        )
        assert json.loads(original_instruction.payload_json)["instruction"] == "PAY"
        assert (
            original.obligation_status,
            original.client_instruction_status,
            original.draft_status,
            original.payment_status,
            original.official_evidence_status,
        ) == ("SUPERSEDED", "PAY", "NOT_CREATED", "UNPAID", "NOT_APPLICABLE")
        assert (
            replacement.obligation_status,
            replacement.client_instruction_status,
            replacement.draft_status,
            replacement.payment_status,
            replacement.official_evidence_status,
        ) == ("RECOGNIZED", "PAY", "CREATED", "UNPAID", "NOT_APPLICABLE")
        links = tuple(transaction.scalars(select(FeeObligationDraftItemLink)))
        assert len(links) == 2
        assert {
            transaction.get(
                FeeObligation,
                transaction.get(FeeObligationLine, link.obligation_line_id).obligation_id,
            ).id
            for link in links
        } == {replacement.id}
        assert (
            transaction.scalar(
                select(func.count()).select_from(CaseActivityEvent).where(
                    CaseActivityEvent.activity_type == "DEMO_SERVICE_DRAFT_ADJUSTED"
                )
            )
            == 1
        )

    second = client.post(
        f"/api/v1/fees/drafts/{draft_id}/demo-service-adjustment",
        json={
            "item_id": adjustable_item_id,
            "expected_quantity": 2,
            "new_quantity": 3,
            "reason": "再次增加处理数量",
            "idempotency_key": "v6-service-adjustment-2",
        },
        headers=auth_headers,
    )
    assert second.status_code == 409

    drift = client.post(
        f"/api/v1/fees/drafts/{draft_id}/demo-service-adjustment",
        json={
            "item_id": adjustable_item_id,
            "expected_quantity": 1,
            "new_quantity": 2,
            "reason": "改变后的原因",
            "idempotency_key": "v6-service-adjustment-1",
        },
        headers=auth_headers,
    )
    assert drift.status_code == 409
    assert client.post(
        f"/api/v1/fees/drafts/{draft_id}/lock", headers=auth_headers
    ).status_code == 200
    replay_after_lock = client.post(
        f"/api/v1/fees/drafts/{draft_id}/demo-service-adjustment",
        json={
            "item_id": adjustable_item_id,
            "expected_quantity": 1,
            "new_quantity": 2,
            "reason": "客户确认增加一份附加文件处理",
            "idempotency_key": "v6-service-adjustment-1",
        },
        headers=auth_headers,
    )
    assert replay_after_lock.status_code == 200
    assert replay_after_lock.json() == {**payload, "reused": True}


def test_adjustment_rejects_fixed_locked_and_invalid_http_boundaries(
    client,
    auth_headers,
    session_factory,
    tmp_path,
    monkeypatch,
) -> None:
    _case_id, _obligation_id, draft_id = _create_open_service_draft(
        client, auth_headers, session_factory, tmp_path, monkeypatch
    )
    with session_factory() as transaction:
        fixed_item = transaction.scalar(
            select(FeeItem).where(
                FeeItem.draft_id == draft_id,
                FeeItem.fee_code == "FWSQDJ001",
            )
        )
        assert fixed_item is not None
        fixed_id = fixed_item.id
    path = f"/api/v1/fees/drafts/{draft_id}/demo-service-adjustment"
    body = {
        "item_id": fixed_id,
        "expected_quantity": 1,
        "new_quantity": 2,
        "reason": "错误修改固定项目",
        "idempotency_key": "v6-fixed-reject",
    }
    assert client.post(path, json=body).status_code == 401
    original_permissions = deps.get_user_permissions
    monkeypatch.setattr(deps, "get_user_permissions", lambda _db, _user_id: set())
    denied = client.post(path, json=body, headers=auth_headers)
    assert denied.status_code == 403
    assert denied.json()["error"]["details"]["required_perm"] == "Fee.Draft.Edit"
    monkeypatch.setattr(deps, "get_user_permissions", original_permissions)
    assert client.post(path, json=body, headers=auth_headers).status_code == 409
    assert client.post(
        "/api/v1/fees/drafts/00000000-0000-0000-0000-000000000000/"
        "demo-service-adjustment",
        json=body,
        headers=auth_headers,
    ).status_code == 404
    assert client.post(
        path,
        json={**body, "item_id": "00000000-0000-0000-0000-000000000000"},
        headers=auth_headers,
    ).status_code == 404
    assert client.post(
        "/api/v1/fees/drafts/not-a-uuid/demo-service-adjustment",
        json=body,
        headers=auth_headers,
    ).status_code == 422
    assert client.post(
        path, json={**body, "unexpected": True}, headers=auth_headers
    ).status_code == 422
    assert client.post(
        path,
        json={**body, "reason": "english only"},
        headers=auth_headers,
    ).status_code == 422

    locked = client.post(f"/api/v1/fees/drafts/{draft_id}/lock", headers=auth_headers)
    assert locked.status_code == 200
    assert client.post(path, json=body, headers=auth_headers).status_code == 409


def test_adjustment_failure_rolls_back_every_partial_write(
    client,
    auth_headers,
    session_factory,
    tmp_path,
    monkeypatch,
) -> None:
    _case_id, _obligation_id, draft_id = _create_open_service_draft(
        client, auth_headers, session_factory, tmp_path, monkeypatch
    )
    with session_factory() as transaction:
        item = transaction.scalar(
            select(FeeItem).where(
                FeeItem.draft_id == draft_id,
                FeeItem.fee_code == "FWSQDJ002",
            )
        )
        assert item is not None
        item_id = item.id
        before = {
            "activities": transaction.scalar(
                select(func.count()).select_from(CaseActivityEvent)
            ),
            "obligations": transaction.scalar(
                select(func.count()).select_from(FeeObligation)
            ),
            "amount": transaction.get(FeeDraft, draft_id).amount,
        }

    def fail_instruction(*_args, **_kwargs):
        raise BusinessError("INJECTED", "注入失败", status_code=409)

    monkeypatch.setattr(demo_service, "record_client_instruction", fail_instruction)
    failed = client.post(
        f"/api/v1/fees/drafts/{draft_id}/demo-service-adjustment",
        json={
            "item_id": item_id,
            "expected_quantity": 1,
            "new_quantity": 2,
            "reason": "客户确认增加一份附加文件处理",
            "idempotency_key": "v6-service-adjustment-rollback",
        },
        headers=auth_headers,
    )
    assert failed.status_code == 409
    with session_factory() as transaction:
        assert transaction.scalar(
            select(func.count()).select_from(CaseActivityEvent)
        ) == before["activities"]
        assert transaction.scalar(
            select(func.count()).select_from(FeeObligation)
        ) == before["obligations"]
        assert transaction.get(FeeDraft, draft_id).amount == before["amount"]


def test_adjustment_rejects_partial_relink_state_without_new_writes(
    client,
    auth_headers,
    session_factory,
    tmp_path,
    monkeypatch,
) -> None:
    _case_id, _obligation_id, draft_id = _create_open_service_draft(
        client, auth_headers, session_factory, tmp_path, monkeypatch
    )
    with session_factory() as transaction:
        item = transaction.scalar(
            select(FeeItem).where(
                FeeItem.draft_id == draft_id,
                FeeItem.fee_code == "FWSQDJ002",
            )
        )
        link = transaction.scalar(
            select(FeeObligationDraftItemLink).where(
                FeeObligationDraftItemLink.fee_item_id == item.id
            )
        )
        item_id = item.id
        transaction.delete(link)
        transaction.commit()
        before_activities = transaction.scalar(
            select(func.count()).select_from(CaseActivityEvent)
        )
        before_obligations = transaction.scalar(
            select(func.count()).select_from(FeeObligation)
        )

    response = client.post(
        f"/api/v1/fees/drafts/{draft_id}/demo-service-adjustment",
        json={
            "item_id": item_id,
            "expected_quantity": 1,
            "new_quantity": 2,
            "reason": "客户确认增加一份附加文件处理",
            "idempotency_key": "v6-service-adjustment-partial-link",
        },
        headers=auth_headers,
    )
    assert response.status_code == 409
    with session_factory() as transaction:
        assert transaction.scalar(
            select(func.count()).select_from(CaseActivityEvent)
        ) == before_activities
        assert transaction.scalar(
            select(func.count()).select_from(FeeObligation)
        ) == before_obligations


def test_adjustment_rejects_compensating_current_item_drift(
    client,
    auth_headers,
    session_factory,
    tmp_path,
    monkeypatch,
) -> None:
    _case_id, _obligation_id, draft_id = _create_open_service_draft(
        client, auth_headers, session_factory, tmp_path, monkeypatch
    )
    with session_factory() as transaction:
        item = transaction.scalar(
            select(FeeItem).where(
                FeeItem.draft_id == draft_id,
                FeeItem.fee_code == "FWSQDJ002",
            )
        )
        item.quantity = 2
        item.unit_price = 150
        item.amount = 300
        transaction.commit()
        item_id = item.id
    response = client.post(
        f"/api/v1/fees/drafts/{draft_id}/demo-service-adjustment",
        json={
            "item_id": item_id,
            "expected_quantity": 1,
            "new_quantity": 2,
            "reason": "客户确认增加一份附加文件处理",
            "idempotency_key": "v6-service-adjustment-drift",
        },
        headers=auth_headers,
    )
    assert response.status_code == 409


def test_adjustment_rejects_canonical_source_authority_rewrite(
    client,
    auth_headers,
    session_factory,
    tmp_path,
    monkeypatch,
) -> None:
    _case_id, obligation_id, draft_id = _create_open_service_draft(
        client, auth_headers, session_factory, tmp_path, monkeypatch
    )
    with session_factory() as transaction:
        obligation = transaction.get(FeeObligation, obligation_id)
        source = transaction.get(CaseActivityEvent, obligation.source_activity_id)
        payload = json.loads(source.payload_json)
        payload["items"][1]["final_quantity"] = 3
        source.payload_json = json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        item = transaction.scalar(
            select(FeeItem).where(
                FeeItem.draft_id == draft_id,
                FeeItem.fee_code == "FWSQDJ002",
            )
        )
        transaction.commit()
        item_id = item.id
    response = client.post(
        f"/api/v1/fees/drafts/{draft_id}/demo-service-adjustment",
        json={
            "item_id": item_id,
            "expected_quantity": 1,
            "new_quantity": 3,
            "reason": "客户确认增加两份附加文件处理",
            "idempotency_key": "v6-service-adjustment-source-drift",
        },
        headers=auth_headers,
    )
    assert response.status_code == 409


def test_adjustment_maps_sqlite_write_lock_to_409(
    client,
    auth_headers,
    session_factory,
    tmp_path,
    monkeypatch,
) -> None:
    _case_id, _obligation_id, draft_id = _create_open_service_draft(
        client, auth_headers, session_factory, tmp_path, monkeypatch
    )
    with session_factory() as transaction:
        item = transaction.scalar(
            select(FeeItem).where(
                FeeItem.draft_id == draft_id,
                FeeItem.fee_code == "FWSQDJ002",
            )
        )
        actor = transaction.scalar(select(T_User).order_by(T_User.id))
        item_id = item.id
        actor_id = actor.id

    original = Connection.exec_driver_sql

    def locked(connection, statement, *args, **kwargs):
        if statement == "BEGIN IMMEDIATE":
            raise OperationalError(statement, {}, RuntimeError("database is locked"))
        return original(connection, statement, *args, **kwargs)

    monkeypatch.setattr(Connection, "exec_driver_sql", locked)
    with session_factory() as transaction:
        with pytest.raises(BusinessError) as caught:
            demo_service.adjust_demo_service_draft(
                demo_service.DemoServiceAdjustmentCommand(
                    draft_id=draft_id,
                    item_id=item_id,
                    expected_quantity=1,
                    new_quantity=2,
                    reason="客户确认增加一份附加文件处理",
                    actor_id=actor_id,
                    idempotency_key="v6-service-adjustment-locked-db",
                    adjusted_at=datetime(2026, 8, 24, 9, 0),
                ),
                transaction,
            )
    assert (caught.value.code, caught.value.status_code) == (
        "DEMO_SERVICE_ADJUSTMENT_CONFLICT",
        409,
    )


def test_adjustment_replay_rejects_canonical_durable_graph_drift(
    client,
    auth_headers,
    session_factory,
    tmp_path,
    monkeypatch,
) -> None:
    _case_id, _obligation_id, draft_id = _create_open_service_draft(
        client, auth_headers, session_factory, tmp_path, monkeypatch
    )
    with session_factory() as transaction:
        item = transaction.scalar(
            select(FeeItem).where(
                FeeItem.draft_id == draft_id,
                FeeItem.fee_code == "FWSQDJ002",
            )
        )
        item_id = item.id
    body = {
        "item_id": item_id,
        "expected_quantity": 1,
        "new_quantity": 2,
        "reason": "客户确认增加一份附加文件处理",
        "idempotency_key": "v6-service-adjustment-replay-drift",
    }
    first = client.post(
        f"/api/v1/fees/drafts/{draft_id}/demo-service-adjustment",
        json=body,
        headers=auth_headers,
    )
    assert first.status_code == 201
    with session_factory() as transaction:
        activity = transaction.get(
            CaseActivityEvent,
            first.json()["adjustment_activity_id"],
        )
        payload = json.loads(activity.payload_json)
        payload["after_digest"] = "0" * 64
        activity.payload_json = json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        transaction.commit()
    replay = client.post(
        f"/api/v1/fees/drafts/{draft_id}/demo-service-adjustment",
        json=body,
        headers=auth_headers,
    )
    assert replay.status_code == 409
