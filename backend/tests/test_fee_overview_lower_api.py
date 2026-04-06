from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import uuid4

from app.modules.auth.models import T_Role
from app.modules.billing.models import CaseReceipt
from app.modules.cases.models import Case, T_CaseApplicant
from app.modules.masterdata.clients.models import Client
from app.modules.rbac.models import T_RolePerm


def _seed_fee_overview_lower_rows(session_factory) -> dict[str, object]:
    client_id = str(uuid4())
    case_a_id = str(uuid4())
    case_b_id = str(uuid4())
    receipt_a_id = str(uuid4())
    receipt_b_id = str(uuid4())
    applicant_a_name = f"收款申请人甲-{uuid4().hex[:6]}"
    applicant_b_name = f"收款申请人乙-{uuid4().hex[:6]}"

    case_a_no = f"FOVL-CASE-A-{uuid4().hex[:6]}"
    case_b_no = f"FOVL-CASE-B-{uuid4().hex[:6]}"
    case_a_app_no = "CN202623450001.X"
    case_b_patent_no = "ZL202623450002.X"

    with session_factory() as db:
        client = Client(
            id=client_id,
            client_code=f"FOVL-{uuid4().hex[:8]}",
            name_cn="收款总览客户",
            name_en="Fee Overview Receipt Client",
            client_type="CLIENT",
            default_currency="CNY",
            is_active=True,
        )
        db.add(client)
        db.flush()

        case_a = Case(
            id=case_a_id,
            case_no=case_a_no,
            case_type="NORMAL",
            patent_category="INV",
            flow_dir="CN_DOMESTIC",
            client_id=client_id,
            app_no=case_a_app_no,
            patent_no="ZL202623450001.X",
        )
        case_b = Case(
            id=case_b_id,
            case_no=case_b_no,
            case_type="NORMAL",
            patent_category="INV",
            flow_dir="CN_DOMESTIC",
            client_id=client_id,
            app_no="CN202623450002.X",
            patent_no=case_b_patent_no,
        )
        db.add_all([case_a, case_b])
        db.flush()

        db.add_all(
            [
                T_CaseApplicant(
                    case_id=case_a_id,
                    seq=1,
                    is_first=True,
                    name_cn=applicant_a_name,
                    name_en="Receipt Applicant A",
                ),
                T_CaseApplicant(
                    case_id=case_b_id,
                    seq=1,
                    is_first=True,
                    name_cn=applicant_b_name,
                    name_en="Receipt Applicant B",
                ),
            ]
        )
        db.flush()

        db.add_all(
            [
                CaseReceipt(
                    id=receipt_a_id,
                    case_id=case_a_id,
                    fee_type="SERVICE",
                    currency="CNY",
                    receivable_amt=Decimal("300.00"),
                    received_amt=Decimal("200.00"),
                    last_receipt_date=date(2026, 4, 12),
                    fee_code="SRV-001",
                    fee_name="服务费",
                    year_no=2026,
                    due_date=date(2026, 4, 20),
                    is_arrears=True,
                    is_prepayment=False,
                    is_commissionable=True,
                    invoice_no="INV-SRV-001",
                ),
                CaseReceipt(
                    id=receipt_b_id,
                    case_id=case_b_id,
                    fee_type="GOV",
                    currency="CNY",
                    receivable_amt=Decimal("120.00"),
                    received_amt=Decimal("120.00"),
                    last_receipt_date=date(2026, 4, 18),
                    fee_code="GOV-001",
                    fee_name="官费",
                    year_no=None,
                    due_date=date(2026, 4, 25),
                    is_arrears=False,
                    is_prepayment=False,
                    is_commissionable=False,
                    invoice_no="INV-GOV-001",
                ),
            ]
        )
        db.commit()

    return {
        "client_id": client_id,
        "case_a_id": case_a_id,
        "case_b_id": case_b_id,
        "case_a_no": case_a_no,
        "case_b_no": case_b_no,
        "case_a_app_no": case_a_app_no,
        "case_b_patent_no": case_b_patent_no,
        "applicant_a_name": applicant_a_name,
        "applicant_b_name": applicant_b_name,
    }


def test_fee_overview_lower_lists_case_receipt_rows(
    client,
    auth_headers,
    session_factory,
) -> None:
    _seed_fee_overview_lower_rows(session_factory)

    response = client.get("/api/v1/fee-overview/case-receipts", headers=auth_headers)

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["total"] == 2
    assert len(payload["items"]) == 2

    first = payload["items"][0]
    assert first["fee_type"] in {"SERVICE", "GOV"}
    assert first["currency"] == "CNY"
    assert first["receivable_amt"] in {"300.00", "120.00"}
    assert first["received_amt"] in {"200.00", "120.00"}
    assert "receipt_date" in first
    assert "due_date" in first
    assert "invoice_no" in first


def test_fee_overview_lower_filters_by_fee_type_case_applicant_and_date(
    client,
    auth_headers,
    session_factory,
) -> None:
    seeded = _seed_fee_overview_lower_rows(session_factory)

    fee_type_resp = client.get(
        "/api/v1/fee-overview/case-receipts",
        params={"fee_type": "SERVICE", "case_no": seeded["case_a_no"]},
        headers=auth_headers,
    )
    assert fee_type_resp.status_code == 200, fee_type_resp.text
    fee_type_items = fee_type_resp.json()["items"]
    assert len(fee_type_items) == 1
    assert fee_type_items[0]["case_id"] == seeded["case_a_id"]

    applicant_resp = client.get(
        "/api/v1/fee-overview/case-receipts",
        params={"applicant_name": seeded["applicant_b_name"]},
        headers=auth_headers,
    )
    assert applicant_resp.status_code == 200, applicant_resp.text
    applicant_items = applicant_resp.json()["items"]
    assert len(applicant_items) == 1
    assert applicant_items[0]["case_id"] == seeded["case_b_id"]

    date_resp = client.get(
        "/api/v1/fee-overview/case-receipts",
        params={
            "case_no": seeded["case_b_no"],
            "receipt_date_from": "2026-04-15",
            "receipt_date_to": "2026-04-30",
        },
        headers=auth_headers,
    )
    assert date_resp.status_code == 200, date_resp.text
    date_items = date_resp.json()["items"]
    assert len(date_items) == 1
    assert date_items[0]["case_id"] == seeded["case_b_id"]


def test_fee_overview_lower_rejects_inverted_date_range(
    client,
    auth_headers,
    session_factory,
) -> None:
    _seed_fee_overview_lower_rows(session_factory)

    response = client.get(
        "/api/v1/fee-overview/case-receipts",
        params={"receipt_date_from": "2026-04-30", "receipt_date_to": "2026-04-01"},
        headers=auth_headers,
    )

    assert response.status_code == 400, response.text


def test_fee_overview_lower_requires_case_receipt_read(
    client,
    auth_headers,
    session_factory,
) -> None:
    _seed_fee_overview_lower_rows(session_factory)

    with session_factory() as db:
        admin_role = db.query(T_Role).filter(T_Role.code == "Admin").first()
        assert admin_role is not None
        binding = (
            db.query(T_RolePerm)
            .filter(
                T_RolePerm.role_id == admin_role.id,
                T_RolePerm.perm_code == "CaseReceipt.Read",
            )
            .first()
        )
        assert binding is not None
        db.delete(binding)
        db.commit()

    try:
        response = client.get("/api/v1/fee-overview/case-receipts", headers=auth_headers)
        assert response.status_code == 403, response.text
    finally:
        with session_factory() as db:
            admin_role = db.query(T_Role).filter(T_Role.code == "Admin").first()
            assert admin_role is not None
            restored = (
                db.query(T_RolePerm)
                .filter(
                    T_RolePerm.role_id == admin_role.id,
                    T_RolePerm.perm_code == "CaseReceipt.Read",
                )
                .first()
            )
            if not restored:
                db.add(
                    T_RolePerm(
                        id=str(uuid4()),
                        role_id=admin_role.id,
                        perm_code="CaseReceipt.Read",
                    )
                )
                db.commit()
