from __future__ import annotations

from decimal import Decimal
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.modules.annuity.models import PayList
from app.modules.cases.models import Case
from app.modules.fees.models import FeeDraft, OfficialFeeChecklist
from app.modules.masterdata.clients.models import Client
from app.modules.official_workflows.models import OfficialWorkPackage

BASE = "/api/v1/official-work-packages"


def _create_fee_conversion_fixture(
    session_factory: sessionmaker,
    *,
    fee_reduction: str | None,
    checklist_blocked: bool = False,
) -> str:
    with session_factory() as db:
        client = Client(
            id=str(uuid4()),
            client_code=f"C-{uuid4().hex[:6]}",
            name_cn="费减转换客户",
        )
        db.add(client)
        db.flush()

        case = Case(
            id=str(uuid4()),
            case_no=f"FRC-{uuid4().hex[:8].upper()}",
            case_type="NORMAL",
            patent_category="INV",
            flow_dir="CN_DOMESTIC",
            client_id=client.id,
            title_cn="费减转换测试案件",
            fee_reduction=fee_reduction,
        )
        db.add(case)
        db.flush()

        package = OfficialWorkPackage(
            id=str(uuid4()),
            case_id=case.id,
            package_kind="FILING_PREP",
            status="READY_FOR_EXTERNAL_SUBMIT",
            external_system="CNIPA_WEB",
        )
        draft = FeeDraft(
            id=str(uuid4()),
            case_id=case.id,
            client_id=client.id,
            draft_type="APPLY_FEE",
            currency="CNY",
            status="OPEN",
            total_gov=Decimal("900.00"),
            total_service=Decimal("0.00"),
            total_misc=Decimal("0.00"),
            amount=Decimal("900.00"),
            official_fee_reduction_note="旧系统 0 / 0.7 / 0.85 语义待客户确认",
            official_template_status="UNCONFIRMED",
        )
        db.add_all([package, draft])
        db.flush()

        pay_list = PayList(
            client_id=client.id,
            pay_list_no=f"PL-{uuid4().hex[:6].upper()}",
            status="DRAFT",
            currency="CNY",
            total_amount=Decimal("900.00"),
        )
        db.add(pay_list)
        db.flush()

        if checklist_blocked:
            db.add(
                OfficialFeeChecklist(
                    id=str(uuid4()),
                    fee_draft_id=draft.id,
                    checklist_code="FEE_REDUCTION_RATE",
                    checklist_label="费减比例解释已确认",
                    status="BLOCKED",
                    required=True,
                    blocker_reason="客户未确认 0 / 0.7 / 0.85 的含义",
                    sort_order=10,
                )
            )

        db.commit()
        return package.id


@pytest.mark.parametrize(
    ("fee_reduction", "customer_ratio", "payable_ratio"),
    [
        ("0.85", "0.85", "0.15"),
        ("0.7", "0.7", "0.3"),
        (None, "0", "1.0"),
    ],
)
def test_fee_linkage_converts_customer_reduction_ratio_to_payable_ratio(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
    fee_reduction: str | None,
    customer_ratio: str,
    payable_ratio: str,
) -> None:
    package_id = _create_fee_conversion_fixture(
        session_factory,
        fee_reduction=fee_reduction,
    )

    response = client.get(f"{BASE}/{package_id}/fee-linkage", headers=auth_headers)

    assert response.status_code == 200, response.text
    draft = response.json()["fee_drafts"][0]
    assert draft["customer_fee_reduction_ratio"] == customer_ratio
    assert draft["payable_fee_ratio"] == payable_ratio
    assert draft["fee_reduction_conversion_status"] == "CONFIRMED"
    assert "减免比例" in draft["fee_reduction_conversion_note"]


def test_fee_linkage_does_not_report_answered_fee_reduction_semantics_as_blocked(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    package_id = _create_fee_conversion_fixture(
        session_factory,
        fee_reduction="0.85",
        checklist_blocked=True,
    )

    response = client.get(f"{BASE}/{package_id}/fee-linkage", headers=auth_headers)

    assert response.status_code == 200, response.text
    body = response.json()
    blocker_codes = {item["blocker_code"] for item in body["customer_confirmation_blockers"]}
    assert "FEE_REDUCTION_RATE" not in blocker_codes
