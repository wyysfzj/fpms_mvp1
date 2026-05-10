from __future__ import annotations

from decimal import Decimal
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.modules.cases.models import Case
from app.modules.fees.models import FeeDraft
from app.modules.masterdata.clients.models import Client


def _uid(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:8].upper()}"


def _create_case_with_draft(
    session_factory: sessionmaker,
    *,
    case_no: str,
    amount: Decimal,
) -> tuple[str, str]:
    with session_factory() as db:
        client_row = Client(name_cn=_uid("费用客户"), default_currency="CNY")
        db.add(client_row)
        db.flush()

        case = Case(
            case_no=case_no,
            case_type="NORMAL",
            patent_category="INV",
            flow_dir="CN_DOMESTIC",
            client_id=client_row.id,
            title_cn="费用草稿案号筛选测试",
        )
        db.add(case)
        db.flush()

        draft = FeeDraft(
            case_id=case.id,
            client_id=client_row.id,
            draft_type="GRANT_FEE",
            currency="CNY",
            status="LOCKED",
            total_service=amount,
            amount=amount,
        )
        db.add(draft)
        db.commit()
        return case.id, draft.id


def test_fee_draft_list_filters_by_visible_case_no(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    target_case_no = _uid("RUI")
    target_case_id, target_draft_id = _create_case_with_draft(
        session_factory,
        case_no=target_case_no,
        amount=Decimal("120.00"),
    )
    other_case_id, other_draft_id = _create_case_with_draft(
        session_factory,
        case_no=_uid("RUI"),
        amount=Decimal("99.00"),
    )

    response = client.get(
        "/api/v1/fees/drafts",
        headers=auth_headers,
        params={"case_no": target_case_no, "page": 1, "page_size": 20},
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["total"] == 1
    assert [item["id"] for item in payload["items"]] == [target_draft_id]
    assert payload["items"][0]["case_id"] == target_case_id
    assert payload["items"][0]["case_no"] == target_case_no
    assert other_case_id != target_case_id
    assert other_draft_id != target_draft_id
