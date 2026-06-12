from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.modules.annuity.models import GovPayment, PayList
from app.modules.cases.models import Case
from app.modules.fees.models import FeeDraft, FeeItem, OfficialFeeChecklist
from app.modules.masterdata.clients.models import Client
from app.modules.official_workflows.models import OfficialWorkPackage

BASE = "/api/v1/official-work-packages"


def _create_fee_linkage_fixture(session_factory: sessionmaker) -> tuple[str, str, int]:
    with session_factory() as db:
        client = Client(
            id=str(uuid4()),
            client_code=f"C-{uuid4().hex[:6]}",
            name_cn="费用联动客户",
        )
        db.add(client)
        db.flush()

        case = Case(
            id=str(uuid4()),
            case_no=f"FEE-{uuid4().hex[:8].upper()}",
            case_type="NORMAL",
            patent_category="INV",
            flow_dir="CN_DOMESTIC",
            client_id=client.id,
            title_cn="费用联动 API 测试案件",
            fee_reduction="0.85",
            discount_rate=Decimal("0.8500"),
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
            total_gov=Decimal("1200.00"),
            total_service=Decimal("300.00"),
            total_misc=Decimal("0.00"),
            amount=Decimal("1500.00"),
            official_fee_reduction_note="旧系统 0 / 0.7 / 0.85 语义待客户确认",
            official_template_status="UNCONFIRMED",
            official_template_version="客户待提供",
            official_template_note="补充缴费信息模板字段待确认",
        )
        db.add_all([package, draft])
        db.flush()

        fee_item = FeeItem(
            id=str(uuid4()),
            draft_id=draft.id,
            case_id=case.id,
            fee_code="APP_FEE",
            fee_name="申请费",
            fee_type="GOV",
            amount=Decimal("1200.00"),
        )
        pay_list = PayList(
            client_id=client.id,
            pay_list_no="PL-P1-FEE-001",
            status="DRAFT",
            currency="CNY",
            planned_pay_date=date(2026, 6, 1),
            total_amount=Decimal("1200.00"),
            official_upload_template_status="UNCONFIRMED",
            official_upload_template_name="补充缴费信息模板",
            official_upload_batch_limit=500,
            official_pay_list_boundary_note="P1 只记录清单边界，不声明已匹配官方 Excel",
        )
        db.add_all([fee_item, pay_list])
        db.flush()

        db.add(
            GovPayment(
                pay_list_id=pay_list.id,
                case_id=case.id,
                fee_item_id=fee_item.id,
                status="PLANNED",
                currency="CNY",
                paid_amount=Decimal("1200.00"),
                remark=f"from_fee_item:{fee_item.id}",
            )
        )
        db.add_all(
            [
                OfficialFeeChecklist(
                    id=str(uuid4()),
                    fee_draft_id=draft.id,
                    checklist_code="FEE_REDUCTION_RATE",
                    checklist_label="费减比例解释已确认",
                    status="BLOCKED",
                    required=True,
                    blocker_reason="客户未确认 0 / 0.7 / 0.85 的含义",
                    sort_order=10,
                ),
                OfficialFeeChecklist(
                    id=str(uuid4()),
                    pay_list_id=pay_list.id,
                    checklist_code="OFFICIAL_EXCEL_TEMPLATE_COLUMNS",
                    checklist_label="官网补充缴费信息模板字段已核对",
                    status="PENDING",
                    required=True,
                    blocker_reason="客户尚未提供官方空表和成功上传样例",
                    sort_order=20,
                ),
            ]
        )
        db.commit()
        return package.id, draft.id, pay_list.id


def test_fee_linkage_api_exposes_internal_fee_and_official_template_boundaries(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    package_id, draft_id, pay_list_id = _create_fee_linkage_fixture(session_factory)

    response = client.get(f"{BASE}/{package_id}/fee-linkage", headers=auth_headers)

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["package_id"] == package_id
    assert body["payment_execution_mode"] == "MANUAL_ONLY"
    assert body["official_excel_template_ready"] is False
    assert body["official_excel_generation_allowed"] is False

    assert body["fee_drafts"][0]["id"] == draft_id
    assert body["fee_drafts"][0]["official_template_status"] == "UNCONFIRMED"
    assert "待确认" not in body["fee_drafts"][0]["official_fee_reduction_note"]
    assert body["fee_drafts"][0]["customer_fee_reduction_ratio"] == "0.85"
    assert body["fee_drafts"][0]["payable_fee_ratio"] == "0.15"
    assert body["fee_drafts"][0]["fee_reduction_conversion_status"] == "CONFIRMED"

    assert body["pay_lists"][0]["id"] == pay_list_id
    assert body["pay_lists"][0]["official_upload_template_name"] == "补充缴费信息模板"
    assert body["pay_lists"][0]["official_upload_batch_limit"] == 500
    assert body["pay_lists"][0]["manual_payment_status"] == "MANUAL_PENDING"

    checklist_codes = {item["checklist_code"] for item in body["checklist"]}
    assert "FEE_REDUCTION_RATE" in checklist_codes
    assert "OFFICIAL_EXCEL_TEMPLATE_COLUMNS" in checklist_codes

    blocker_codes = {item["blocker_code"] for item in body["customer_confirmation_blockers"]}
    assert "FEE_REDUCTION_RATE" not in blocker_codes
    assert "OFFICIAL_EXCEL_TEMPLATE_COLUMNS" in blocker_codes
    assert "FEE_RATE_SOURCE_UNCONFIRMED" in blocker_codes


def test_fee_linkage_api_returns_404_for_missing_package(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    response = client.get(f"{BASE}/{uuid4()}/fee-linkage", headers=auth_headers)

    assert response.status_code == 404, response.text
    assert response.json()["error"]["code"] == "OFFICIAL_WORK_PACKAGE_NOT_FOUND"
