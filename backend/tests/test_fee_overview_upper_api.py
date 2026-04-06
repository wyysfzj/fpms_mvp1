from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import uuid4

from app.modules.annuity.models import GovPayment, PayList
from app.modules.auth.models import T_Role
from app.modules.cases.models import Case, T_CaseApplicant
from app.modules.fees.models import FeeDraft, FeeItem
from app.modules.masterdata.clients.models import Client
from app.modules.rbac.models import T_RolePerm


def _seed_fee_overview_upper_rows(session_factory) -> dict[str, object]:
    client_id = str(uuid4())
    case_a_id = str(uuid4())
    case_b_id = str(uuid4())
    draft_a_id = str(uuid4())
    draft_b_id = str(uuid4())
    fee_item_a_id = str(uuid4())
    fee_item_b_id = str(uuid4())
    applicant_a_name = f"张三科技-{uuid4().hex[:6]}"
    applicant_b_name = f"李四集团-{uuid4().hex[:6]}"

    with session_factory() as db:
        client = Client(
            id=client_id,
            client_code=f"FOV-{uuid4().hex[:8]}",
            name_cn="费用总览客户",
            name_en="Fee Overview Client",
            client_type="CLIENT",
            default_currency="CNY",
            is_active=True,
        )
        case_a = Case(
            id=case_a_id,
            case_no=f"FOV-CASE-A-{uuid4().hex[:6]}",
            case_type="NORMAL",
            patent_category="INV",
            flow_dir="CN_DOMESTIC",
            client_id=client_id,
            app_no="CN202612340001.X",
            patent_no="ZL202612340001.X",
        )
        case_b = Case(
            id=case_b_id,
            case_no=f"FOV-CASE-B-{uuid4().hex[:6]}",
            case_type="NORMAL",
            patent_category="INV",
            flow_dir="CN_DOMESTIC",
            client_id=client_id,
            app_no="CN202612340002.X",
            patent_no="ZL202612340002.X",
        )
        db.add(client)
        db.flush()
        db.add_all([case_a, case_b])
        db.flush()

        db.add_all(
            [
                T_CaseApplicant(
                    case_id=case_a_id,
                    seq=1,
                    is_first=True,
                    name_cn=applicant_a_name,
                    name_en="Zhang San Tech",
                ),
                T_CaseApplicant(
                    case_id=case_b_id,
                    seq=1,
                    is_first=True,
                    name_cn=applicant_b_name,
                    name_en="Li Si Group",
                ),
            ]
        )

        draft_a = FeeDraft(
            id=draft_a_id,
            case_id=case_a_id,
            client_id=client_id,
            draft_type="ANNUITY_FEE",
            currency="CNY",
            total_gov=Decimal("100.00"),
            amount=Decimal("100.00"),
        )
        draft_b = FeeDraft(
            id=draft_b_id,
            case_id=case_b_id,
            client_id=client_id,
            draft_type="GRANT_FEE",
            currency="CNY",
            total_gov=Decimal("180.00"),
            amount=Decimal("180.00"),
        )
        db.add_all([draft_a, draft_b])
        db.flush()

        fee_item_a = FeeItem(
            id=fee_item_a_id,
            draft_id=draft_a_id,
            case_id=case_a_id,
            fee_type="GOV",
            fee_code="ANN-GOV-01",
            fee_name="年费官费",
            year_no=1,
            amount=Decimal("100.00"),
        )
        fee_item_b = FeeItem(
            id=fee_item_b_id,
            draft_id=draft_b_id,
            case_id=case_b_id,
            fee_type="GOV",
            fee_code="GRANT-GOV-01",
            fee_name="授权官费",
            year_no=None,
            amount=Decimal("180.00"),
        )
        db.add_all([fee_item_a, fee_item_b])
        db.flush()

        pay_list_a = PayList(
            client_id=client_id,
            pay_list_no="PL-001",
            status="PAID",
            currency="CNY",
            planned_pay_date=date(2026, 4, 5),
            paid_date=date(2026, 4, 6),
            total_amount=Decimal("100.00"),
        )
        pay_list_b = PayList(
            client_id=client_id,
            pay_list_no="PL-002",
            status="PAID",
            currency="CNY",
            planned_pay_date=date(2026, 4, 10),
            paid_date=date(2026, 4, 11),
            total_amount=Decimal("180.00"),
        )
        db.add_all([pay_list_a, pay_list_b])
        db.flush()

        db.add_all(
            [
                GovPayment(
                    pay_list_id=pay_list_a.id,
                    case_id=case_a_id,
                    fee_item_id=fee_item_a_id,
                    status="PAID",
                    currency="CNY",
                    paid_date=date(2026, 4, 6),
                    paid_amount=Decimal("95.00"),
                    official_receipt_no="OFFICIAL-001",
                ),
                GovPayment(
                    pay_list_id=pay_list_b.id,
                    case_id=case_b_id,
                    fee_item_id=fee_item_b_id,
                    status="PAID",
                    currency="CNY",
                    paid_date=date(2026, 4, 11),
                    paid_amount=Decimal("180.00"),
                    official_receipt_no="OFFICIAL-002",
                ),
            ]
        )
        db.commit()

        return {
            "client_id": client_id,
            "case_a_id": case_a_id,
            "case_b_id": case_b_id,
            "case_a_no": case_a.case_no,
            "case_b_no": case_b.case_no,
            "case_a_app_no": case_a.app_no,
            "case_b_patent_no": case_b.patent_no,
            "applicant_a_name": applicant_a_name,
            "applicant_b_name": applicant_b_name,
        }


def test_fee_overview_upper_lists_gov_payment_rows(
    client,
    auth_headers,
    session_factory,
) -> None:
    seeded = _seed_fee_overview_upper_rows(session_factory)

    response = client.get("/api/v1/fee-overview/gov-payments", headers=auth_headers)

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["total"] == 2
    assert len(payload["items"]) == 2

    first = payload["items"][0]
    assert first["case_id"] in {seeded["case_a_id"], seeded["case_b_id"]}
    assert first["list_no"] in {"PL-001", "PL-002"}
    assert first["currency"] == "CNY"
    assert first["planned_amt"] in {"100.00", "180.00"}
    assert first["paid_amt"] in {"95.00", "180.00"}
    assert first["voucher_no"] is None
    assert first["invoice_no"] is None


def test_fee_overview_upper_filters_by_case_applicant_and_date(
    client,
    auth_headers,
    session_factory,
) -> None:
    seeded = _seed_fee_overview_upper_rows(session_factory)

    case_resp = client.get(
        "/api/v1/fee-overview/gov-payments",
        params={"case_no": seeded["case_a_no"]},
        headers=auth_headers,
    )
    assert case_resp.status_code == 200, case_resp.text
    case_items = case_resp.json()["items"]
    assert len(case_items) == 1
    assert case_items[0]["case_no"] == seeded["case_a_no"]

    applicant_resp = client.get(
        "/api/v1/fee-overview/gov-payments",
        params={"applicant_name": seeded["applicant_b_name"]},
        headers=auth_headers,
    )
    assert applicant_resp.status_code == 200, applicant_resp.text
    applicant_items = applicant_resp.json()["items"]
    assert len(applicant_items) == 1
    assert applicant_items[0]["case_id"] == seeded["case_b_id"]

    date_resp = client.get(
        "/api/v1/fee-overview/gov-payments",
        params={
            "case_no": seeded["case_b_no"],
            "paid_date_from": "2026-04-07",
            "paid_date_to": "2026-04-30",
        },
        headers=auth_headers,
    )
    assert date_resp.status_code == 200, date_resp.text
    date_items = date_resp.json()["items"]
    assert len(date_items) == 1
    assert date_items[0]["case_id"] == seeded["case_b_id"]


def test_fee_overview_upper_rejects_inverted_date_range(
    client,
    auth_headers,
    session_factory,
) -> None:
    _seed_fee_overview_upper_rows(session_factory)

    response = client.get(
        "/api/v1/fee-overview/gov-payments",
        params={"paid_date_from": "2026-04-30", "paid_date_to": "2026-04-01"},
        headers=auth_headers,
    )

    assert response.status_code == 400, response.text


def test_fee_overview_upper_requires_pay_list_read(
    client,
    auth_headers,
    session_factory,
) -> None:
    _seed_fee_overview_upper_rows(session_factory)

    with session_factory() as db:
        admin_role = db.query(T_Role).filter(T_Role.code == "Admin").first()
        assert admin_role is not None
        binding = (
            db.query(T_RolePerm)
            .filter(
                T_RolePerm.role_id == admin_role.id,
                T_RolePerm.perm_code == "PayList.Read",
            )
            .first()
        )
        assert binding is not None
        db.delete(binding)
        db.commit()

    try:
        response = client.get("/api/v1/fee-overview/gov-payments", headers=auth_headers)
        assert response.status_code == 403, response.text
    finally:
        with session_factory() as db:
            admin_role = db.query(T_Role).filter(T_Role.code == "Admin").first()
            assert admin_role is not None
            restored = (
                db.query(T_RolePerm)
                .filter(
                    T_RolePerm.role_id == admin_role.id,
                    T_RolePerm.perm_code == "PayList.Read",
                )
                .first()
            )
            if not restored:
                db.add(
                    T_RolePerm(
                        id=str(uuid4()),
                        role_id=admin_role.id,
                        perm_code="PayList.Read",
                    )
                )
                db.commit()
