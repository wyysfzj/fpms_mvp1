from __future__ import annotations

from datetime import date
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.modules.fees.models import T_GrantFeeTask

WORKLIST_BASE = "/api/v1/grant-fee-tasks/list"


def _unique_case_no() -> str:
    return f"GFWL-{uuid4().hex[:8].upper()}"


def _create_case(client: TestClient, auth_headers: dict[str, str]) -> str:
    response = client.post(
        "/api/v1/cases",
        json={
            "case_no": _unique_case_no(),
            "case_type": "NORMAL",
            "patent_category": "INV",
            "flow_dir": "CN_DOMESTIC",
            "title_cn": "Grant Fee Worklist Case",
        },
        headers=auth_headers,
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def _insert_task(
    session_factory: sessionmaker,
    *,
    case_id: str,
    due_date: date,
    client_instruction: str = "NONE",
    notify_count: int = 0,
    draft_generated: bool = False,
    notice_sent: bool = False,
    is_overdue: bool = False,
    gov_fee_amt: str = "0",
    service_fee_amt: str = "0",
    currency: str = "CNY",
) -> str:
    with session_factory() as db:
        task = T_GrantFeeTask(
            case_id=case_id,
            due_date=due_date,
            gov_fee_amt=gov_fee_amt,
            service_fee_amt=service_fee_amt,
            currency=currency,
            client_instruction=client_instruction,
            notify_count=notify_count,
            draft_generated=draft_generated,
            notice_sent=notice_sent,
            is_overdue=is_overdue,
            remark=None,
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        return task.id


def _assert_item_shape(item: dict) -> None:
    assert set(item) == {
        "task_id",
        "case_id",
        "status",
        "due_date",
        "client_instruction",
        "gov_fee_amt",
        "service_fee_amt",
        "currency",
        "draft_generated",
        "notice_sent",
        "is_overdue",
    }


def test_grant_fee_worklist_requires_read_permission(
    client: TestClient,
    auth_headers: dict[str, str],
    monkeypatch,
) -> None:
    import app.api.deps as deps

    def _no_perms(_db, _user_id) -> set[str]:
        return set()

    monkeypatch.setattr(deps, "get_user_permissions", _no_perms)

    response = client.get(WORKLIST_BASE, headers=auth_headers)

    assert response.status_code == 403, response.text
    assert response.json()["error"]["details"]["required_perm"] == "GrantFeeTask.Read"


def test_grant_fee_worklist_lists_tasks_with_projection_and_pagination(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    case_a = _create_case(client, auth_headers)
    case_b = _create_case(client, auth_headers)

    open_task_id = _insert_task(
        session_factory,
        case_id=case_a,
        due_date=date(2026, 4, 10),
        gov_fee_amt="100.00",
        service_fee_amt="50.00",
        currency="CNY",
    )
    waiting_task_id = _insert_task(
        session_factory,
        case_id=case_a,
        due_date=date(2026, 4, 12),
        client_instruction="NONE",
        notify_count=1,
        notice_sent=True,
        gov_fee_amt="120.00",
        service_fee_amt="60.00",
        currency="CNY",
        is_overdue=True,
    )
    ready_task_id = _insert_task(
        session_factory,
        case_id=case_b,
        due_date=date(2026, 4, 20),
        client_instruction="PAY",
        notify_count=2,
        notice_sent=True,
        gov_fee_amt="140.00",
        service_fee_amt="70.00",
        currency="USD",
    )
    draft_task_id = _insert_task(
        session_factory,
        case_id=case_b,
        due_date=date(2026, 5, 1),
        client_instruction="PAY",
        notify_count=3,
        draft_generated=True,
        notice_sent=True,
        gov_fee_amt="160.00",
        service_fee_amt="80.00",
        currency="USD",
    )
    done_task_id = _insert_task(
        session_factory,
        case_id=case_b,
        due_date=date(2026, 5, 5),
        client_instruction="ABANDON",
        notify_count=4,
        notice_sent=True,
        gov_fee_amt="180.00",
        service_fee_amt="90.00",
        currency="CNY",
    )

    response = client.get(
        WORKLIST_BASE,
        headers=auth_headers,
        params={"page": 1, "page_size": 2},
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert set(payload) == {"items", "page", "page_size", "total"}
    assert payload["page"] == 1
    assert payload["page_size"] == 2
    assert payload["total"] == 5
    assert len(payload["items"]) == 2

    first_item, second_item = payload["items"]
    _assert_item_shape(first_item)
    _assert_item_shape(second_item)
    assert first_item["task_id"] == open_task_id
    assert first_item["case_id"] == case_a
    assert first_item["status"] == "OPEN"
    assert second_item["task_id"] == waiting_task_id
    assert second_item["status"] == "WAITING_CLIENT"

    filtered_resp = client.get(
        WORKLIST_BASE,
        headers=auth_headers,
        params={
            "status": "READY_TO_DRAFT",
            "client_instruction": "PAY",
            "draft_generated": False,
            "is_overdue": False,
            "case_id": case_b,
            "date_from": "2026-04-01",
            "date_to": "2026-04-30",
            "page": 1,
            "page_size": 20,
        },
    )

    assert filtered_resp.status_code == 200, filtered_resp.text
    filtered_payload = filtered_resp.json()
    assert filtered_payload["total"] == 1
    assert len(filtered_payload["items"]) == 1
    filtered_item = filtered_payload["items"][0]
    _assert_item_shape(filtered_item)
    assert filtered_item["task_id"] == ready_task_id
    assert filtered_item["status"] == "READY_TO_DRAFT"
    assert filtered_item["client_instruction"] == "PAY"
    assert filtered_item["draft_generated"] is False
    assert filtered_item["is_overdue"] is False

    draft_resp = client.get(
        WORKLIST_BASE,
        headers=auth_headers,
        params={"status": "DRAFT_GENERATED", "page": 1, "page_size": 20},
    )
    assert draft_resp.status_code == 200, draft_resp.text
    draft_payload = draft_resp.json()
    assert draft_payload["total"] == 1
    assert draft_payload["items"][0]["task_id"] == draft_task_id
    assert draft_payload["items"][0]["status"] == "DRAFT_GENERATED"

    done_resp = client.get(
        WORKLIST_BASE,
        headers=auth_headers,
        params={"status": "DONE", "page": 1, "page_size": 20},
    )
    assert done_resp.status_code == 200, done_resp.text
    done_payload = done_resp.json()
    assert done_payload["total"] == 1
    assert done_payload["items"][0]["task_id"] == done_task_id
    assert done_payload["items"][0]["status"] == "DONE"


def test_grant_fee_worklist_filters_by_overdue_and_case_and_date_range(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    case_a = _create_case(client, auth_headers)
    case_b = _create_case(client, auth_headers)

    overdue_task_id = _insert_task(
        session_factory,
        case_id=case_a,
        due_date=date(2026, 3, 1),
        is_overdue=True,
        client_instruction="NONE",
        notify_count=1,
        notice_sent=True,
    )
    other_task_id = _insert_task(
        session_factory,
        case_id=case_b,
        due_date=date(2030, 6, 1),
        client_instruction="NONE",
        notify_count=0,
    )

    overdue_resp = client.get(
        WORKLIST_BASE,
        headers=auth_headers,
        params={"is_overdue": True, "case_id": case_a, "page": 1, "page_size": 20},
    )
    assert overdue_resp.status_code == 200, overdue_resp.text
    overdue_payload = overdue_resp.json()
    assert overdue_payload["total"] == 1
    assert overdue_payload["items"][0]["task_id"] == overdue_task_id
    assert overdue_payload["items"][0]["is_overdue"] is True

    case_resp = client.get(
        WORKLIST_BASE,
        headers=auth_headers,
        params={"case_id": case_b, "page": 1, "page_size": 20},
    )
    assert case_resp.status_code == 200, case_resp.text
    case_payload = case_resp.json()
    assert case_payload["total"] == 1
    assert case_payload["items"][0]["task_id"] == other_task_id
    assert case_payload["items"][0]["case_id"] == case_b

    range_resp = client.get(
        WORKLIST_BASE,
        headers=auth_headers,
        params={
            "date_from": "2030-05-01",
            "date_to": "2030-06-30",
            "page": 1,
            "page_size": 20,
        },
    )
    assert range_resp.status_code == 200, range_resp.text
    range_payload = range_resp.json()
    assert range_payload["total"] == 1
    assert range_payload["items"][0]["task_id"] == other_task_id
