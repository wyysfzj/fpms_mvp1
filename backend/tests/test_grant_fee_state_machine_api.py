from __future__ import annotations

from datetime import date
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from app.modules.fees.models import T_GrantFeeTask

STATE_BASE = "/api/v1/grant-fee-tasks"


def _uid(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:8].upper()}"


def _create_case(client: TestClient, auth_headers: dict[str, str]) -> str:
    resp = client.post(
        "/api/v1/cases",
        json={
            "case_no": _uid("GFSM-CASE"),
            "case_type": "NORMAL",
            "patent_category": "INV",
            "flow_dir": "CN_DOMESTIC",
            "title_cn": "Grant Fee State Machine Case",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


def _insert_task(
    session_factory: sessionmaker,
    *,
    case_id: str,
    **overrides,
) -> str:
    with session_factory() as db:
        task = T_GrantFeeTask(
            case_id=case_id,
            due_date=overrides.pop("due_date", date(2026, 4, 30)),
            gov_fee_amt=overrides.pop("gov_fee_amt", 0),
            service_fee_amt=overrides.pop("service_fee_amt", 0),
            currency=overrides.pop("currency", "CNY"),
            client_instruction=overrides.pop("client_instruction", "NONE"),
            notify_count=overrides.pop("notify_count", 0),
            draft_generated=overrides.pop("draft_generated", False),
            notice_sent=overrides.pop("notice_sent", False),
            is_overdue=overrides.pop("is_overdue", False),
            remark=overrides.pop("remark", None),
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        return task.id


def _assert_state(
    payload: dict,
    *,
    task_id: str,
    case_id: str,
    state: str,
    allowed_actions: list[str],
) -> None:
    assert payload["task_id"] == task_id
    assert payload["case_id"] == case_id
    assert payload["state"] == state
    assert payload["allowed_actions"] == allowed_actions
    assert set(payload) == {
        "task_id",
        "case_id",
        "state",
        "client_instruction",
        "notify_count",
        "draft_generated",
        "notice_sent",
        "is_overdue",
        "allowed_actions",
    }


def test_grant_fee_state_machine_exposes_open_state_and_actions(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    case_id = _create_case(client, auth_headers)
    task_id = _insert_task(session_factory, case_id=case_id)

    resp = client.get(f"{STATE_BASE}/{task_id}/state", headers=auth_headers)
    assert resp.status_code == 200, resp.text
    _assert_state(
        resp.json(),
        task_id=task_id,
        case_id=case_id,
        state="OPEN",
        allowed_actions=["mark_waiting_client"],
    )


def test_grant_fee_state_machine_supports_pay_and_done_flow(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    case_id = _create_case(client, auth_headers)
    task_id = _insert_task(session_factory, case_id=case_id)

    waiting_resp = client.put(
        f"{STATE_BASE}/{task_id}/state",
        headers=auth_headers,
        json={"action": "mark_waiting_client"},
    )
    assert waiting_resp.status_code == 200, waiting_resp.text
    _assert_state(
        waiting_resp.json(),
        task_id=task_id,
        case_id=case_id,
        state="WAITING_CLIENT",
        allowed_actions=["record_pay_instruction", "record_abandon_instruction"],
    )

    ready_resp = client.put(
        f"{STATE_BASE}/{task_id}/state",
        headers=auth_headers,
        json={"action": "record_pay_instruction"},
    )
    assert ready_resp.status_code == 200, ready_resp.text
    _assert_state(
        ready_resp.json(),
        task_id=task_id,
        case_id=case_id,
        state="READY_TO_DRAFT",
        allowed_actions=["mark_draft_generated"],
    )

    draft_resp = client.put(
        f"{STATE_BASE}/{task_id}/state",
        headers=auth_headers,
        json={"action": "mark_draft_generated"},
    )
    assert draft_resp.status_code == 200, draft_resp.text
    _assert_state(
        draft_resp.json(),
        task_id=task_id,
        case_id=case_id,
        state="DRAFT_GENERATED",
        allowed_actions=["mark_done"],
    )

    done_resp = client.put(
        f"{STATE_BASE}/{task_id}/state",
        headers=auth_headers,
        json={"action": "mark_done"},
    )
    assert done_resp.status_code == 200, done_resp.text
    _assert_state(
        done_resp.json(),
        task_id=task_id,
        case_id=case_id,
        state="DONE",
        allowed_actions=[],
    )

    with session_factory() as db:
        task = db.execute(select(T_GrantFeeTask).where(T_GrantFeeTask.id == task_id)).scalar_one()

    assert task.notice_sent is True
    assert task.draft_generated is True
    assert task.notify_count == 4


def test_grant_fee_state_machine_supports_abandon_flow_and_rejects_invalid_transition(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    case_id = _create_case(client, auth_headers)
    task_id = _insert_task(session_factory, case_id=case_id)

    waiting_resp = client.put(
        f"{STATE_BASE}/{task_id}/state",
        headers=auth_headers,
        json={"action": "mark_waiting_client"},
    )
    assert waiting_resp.status_code == 200, waiting_resp.text

    abandon_resp = client.put(
        f"{STATE_BASE}/{task_id}/state",
        headers=auth_headers,
        json={"action": "record_abandon_instruction"},
    )
    assert abandon_resp.status_code == 200, abandon_resp.text
    _assert_state(
        abandon_resp.json(),
        task_id=task_id,
        case_id=case_id,
        state="DONE",
        allowed_actions=[],
    )

    invalid_resp = client.put(
        f"{STATE_BASE}/{task_id}/state",
        headers=auth_headers,
        json={"action": "mark_waiting_client"},
    )
    assert invalid_resp.status_code == 400, invalid_resp.text
    invalid_payload = invalid_resp.json()
    assert invalid_payload["error"]["code"] == "GRANT_FEE_STATE_TRANSITION_INVALID"


def test_grant_fee_state_machine_returns_not_found_for_missing_task(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    missing_state_resp = client.get(
        f"{STATE_BASE}/missing-task/state",
        headers=auth_headers,
    )
    assert missing_state_resp.status_code == 404, missing_state_resp.text
    assert missing_state_resp.json()["error"]["code"] == "GRANT_FEE_TASK_NOT_FOUND"

    missing_update_resp = client.put(
        f"{STATE_BASE}/missing-task/state",
        headers=auth_headers,
        json={"action": "mark_waiting_client"},
    )
    assert missing_update_resp.status_code == 404, missing_update_resp.text
    assert missing_update_resp.json()["error"]["code"] == "GRANT_FEE_TASK_NOT_FOUND"
