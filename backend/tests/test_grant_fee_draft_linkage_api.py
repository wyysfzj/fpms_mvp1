from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

import app.api.deps as deps
from app.modules.documents.models import Document
from app.modules.fees.models import FeeDraft, FeeItem, T_GrantFeeTask
from app.modules.grant_fees.schemas import GrantFeeDraftGenerateOut
from app.modules.grant_fees.service import derive_grant_fee_task_state

STATE_BASE = "/api/v1/grant-fee-tasks"
GENERATE_PATH_SUFFIX = "/generate-draft"


def _uid(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:8].upper()}"


def _create_client(client: TestClient, auth_headers: dict[str, str]) -> dict:
    resp = client.post(
        "/api/v1/clients",
        json={
            "client_code": _uid("GFD-CLI"),
            "name_cn": _uid("GFD-CLIENT"),
            "default_currency": "CNY",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def _create_case(
    client: TestClient,
    auth_headers: dict[str, str],
    *,
    client_id: str | None = None,
) -> dict:
    payload = {
        "case_no": _uid("GFD-CASE"),
        "case_type": "NORMAL",
        "patent_category": "INV",
        "flow_dir": "CN_DOMESTIC",
        "fee_reduction": "0",
        "title_cn": "Grant Fee Draft Test Case",
    }
    if client_id:
        payload["client_id"] = client_id

    resp = client.post("/api/v1/cases", json=payload, headers=auth_headers)
    assert resp.status_code == 201, resp.text
    return resp.json()


def _insert_task(
    session_factory: sessionmaker,
    *,
    case_id: str,
    **overrides,
) -> str:
    with session_factory() as db:
        source_document = Document(
            case_id=case_id,
            doc_type="OFFICIAL",
            direction="IN",
            doc_date=date(2026, 4, 1),
            title="授权费草单来源文书",
        )
        db.add(source_document)
        db.flush()
        task = T_GrantFeeTask(
            case_id=case_id,
            due_date=overrides.pop("due_date", date(2026, 4, 30)),
            source_document_id=source_document.id,
            deadline_source="MANUAL_OFFICIAL_NOTICE",
            deadline_confirmed_at=datetime(2026, 4, 1, 9, 0),
            gov_fee_amt=overrides.pop("gov_fee_amt", Decimal("0")),
            service_fee_amt=overrides.pop("service_fee_amt", Decimal("0")),
            currency=overrides.pop("currency", "CNY"),
            client_instruction=overrides.pop("client_instruction", "PAY"),
            notify_count=overrides.pop("notify_count", 2),
            draft_generated=overrides.pop("draft_generated", False),
            notice_sent=overrides.pop("notice_sent", True),
            is_overdue=overrides.pop("is_overdue", False),
            remark=overrides.pop("remark", None),
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        return task.id


def _count_fee_drafts(
    session_factory: sessionmaker,
    *,
    case_id: str,
    draft_type: str = "GRANT_FEE",
) -> int:
    with session_factory() as db:
        return (
            db.execute(
                select(FeeDraft).where(
                    FeeDraft.case_id == case_id,
                    FeeDraft.draft_type == draft_type,
                    FeeDraft.status == "OPEN",
                )
            )
            .scalars()
            .all()
            .__len__()
        )


def _load_task(session_factory: sessionmaker, task_id: str) -> T_GrantFeeTask:
    with session_factory() as db:
        return db.execute(select(T_GrantFeeTask).where(T_GrantFeeTask.id == task_id)).scalar_one()


def _count_fee_items_for_draft(session_factory: sessionmaker, draft_id: str) -> int:
    with session_factory() as db:
        return (
            db.execute(select(FeeItem).where(FeeItem.draft_id == draft_id))
            .scalars()
            .all()
            .__len__()
        )


def _load_fee_items_for_draft(session_factory: sessionmaker, draft_id: str) -> list[FeeItem]:
    with session_factory() as db:
        return list(db.execute(select(FeeItem).where(FeeItem.draft_id == draft_id)).scalars().all())


def test_grant_fee_generate_draft_creates_fee_draft_and_items_and_marks_task_generated(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    client_row = _create_client(client, auth_headers)
    case = _create_case(client, auth_headers, client_id=client_row["id"])
    task_id = _insert_task(
        session_factory,
        case_id=case["id"],
        gov_fee_amt=Decimal("900.00"),
        service_fee_amt=Decimal("50.00"),
    )

    resp = client.post(f"{STATE_BASE}/{task_id}{GENERATE_PATH_SUFFIX}", headers=auth_headers)
    assert resp.status_code == 200, resp.text

    data = resp.json()
    assert set(data) == {
        "task_id",
        "case_id",
        "draft_id",
        "draft_type",
        "state",
        "draft_generated",
        "currency",
        "amount",
        "item_count",
        "reused",
    }
    assert GrantFeeDraftGenerateOut.model_validate(data)
    assert data["task_id"] == task_id
    assert data["case_id"] == case["id"]
    assert data["draft_type"] == "GRANT_FEE"
    assert data["state"] == "DRAFT_GENERATED"
    assert data["draft_generated"] is True
    assert data["currency"] == "CNY"
    assert Decimal(str(data["amount"])) == Decimal("900.00")
    assert data["item_count"] == 1
    assert data["reused"] is False

    with session_factory() as db:
        task = db.execute(select(T_GrantFeeTask).where(T_GrantFeeTask.id == task_id)).scalar_one()
        drafts = (
            db.execute(
                select(FeeDraft).where(
                    FeeDraft.case_id == case["id"],
                    FeeDraft.draft_type == "GRANT_FEE",
                    FeeDraft.status == "OPEN",
                )
            )
            .scalars()
            .all()
        )

    assert task.draft_generated is True
    assert derive_grant_fee_task_state(task) == "DRAFT_GENERATED"
    assert len(drafts) == 1
    draft = drafts[0]
    assert draft.client_id == client_row["id"]
    assert draft.currency == "CNY"
    assert draft.amount == Decimal("900.00")
    assert draft.total_gov == Decimal("900.00")
    assert draft.total_service == Decimal("0.00")
    items = _load_fee_items_for_draft(session_factory, draft.id)
    assert len(items) == 1
    assert items[0].fee_type == "GOV"
    assert items[0].fee_code == "GRANT_FEE_GOV"
    assert items[0].amount == Decimal("900.00")


def test_grant_fee_generate_draft_is_idempotent_for_same_task(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    client_row = _create_client(client, auth_headers)
    case = _create_case(client, auth_headers, client_id=client_row["id"])
    task_id = _insert_task(session_factory, case_id=case["id"])

    first_resp = client.post(f"{STATE_BASE}/{task_id}{GENERATE_PATH_SUFFIX}", headers=auth_headers)
    assert first_resp.status_code == 200, first_resp.text
    first_payload = first_resp.json()

    second_resp = client.post(f"{STATE_BASE}/{task_id}{GENERATE_PATH_SUFFIX}", headers=auth_headers)
    assert second_resp.status_code == 200, second_resp.text
    second_payload = second_resp.json()

    assert second_payload["reused"] is True
    assert second_payload["draft_id"] == first_payload["draft_id"]
    assert second_payload["amount"] == first_payload["amount"]
    assert second_payload["item_count"] == first_payload["item_count"]
    assert _count_fee_drafts(session_factory, case_id=case["id"]) == 1


def test_grant_fee_generate_draft_rejects_non_ready_task(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    case = _create_case(client, auth_headers)
    task_id = _insert_task(
        session_factory,
        case_id=case["id"],
        client_instruction="NONE",
        notify_count=0,
        draft_generated=False,
        notice_sent=False,
    )

    resp = client.post(f"{STATE_BASE}/{task_id}{GENERATE_PATH_SUFFIX}", headers=auth_headers)
    assert resp.status_code == 400, resp.text
    body = resp.json()
    assert body["error"]["code"] == "GRANT_FEE_DRAFT_PRECONDITION_FAILED"


def test_grant_fee_task_state_includes_deadline_preview_fields(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    case = _create_case(client, auth_headers)
    task_id = _insert_task(session_factory, case_id=case["id"])

    resp = client.get(f"{STATE_BASE}/{task_id}/state", headers=auth_headers)

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["task_id"] == task_id
    assert data["trigger_rule"] == "收到办理登记手续通知书/授权通知书"
    assert (
        data["deadline_rule"]
        == "以办理登记手续通知书/授权通知书载明期限为准；当前按授权费任务到期日展示"
    )
    assert (
        data["fee_basis"] == "授权阶段官费按授权费任务金额展示；如无授权费率则回退授权当年年费规则"
    )
    assert (
        data["fee_node_explanation"]
        == "授权费用节点：客户确认缴费后生成官费草单，缴费登记后进入授权后年费监视。"
    )


def test_grant_fee_generate_draft_requires_write_permission(
    client: TestClient,
    auth_headers: dict[str, str],
    monkeypatch,
    session_factory: sessionmaker,
) -> None:
    client_row = _create_client(client, auth_headers)
    case = _create_case(client, auth_headers, client_id=client_row["id"])
    task_id = _insert_task(session_factory, case_id=case["id"])

    def _no_perms(_db, _user_id) -> set[str]:
        return set()

    monkeypatch.setattr(deps, "get_user_permissions", _no_perms)

    resp = client.post(f"{STATE_BASE}/{task_id}{GENERATE_PATH_SUFFIX}", headers=auth_headers)
    assert resp.status_code == 403, resp.text
    assert resp.json()["error"]["details"]["required_perm"] == "GrantFeeTask.Write"
