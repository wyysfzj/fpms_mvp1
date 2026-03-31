"""Tests for the billing payment + receipt unified query contract."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import uuid4

from app.modules.auth.models import T_Role
from app.modules.billing.models import CaseReceipt, Payment, PaymentLine
from app.modules.cases.models import Case
from app.modules.masterdata.clients.models import Client
from app.modules.rbac.models import T_RolePerm


def _seed_fee_unified_query_rows(session_factory) -> dict[str, str]:
    client_id = str(uuid4())
    case_id = str(uuid4())
    payment_id = str(uuid4())
    receipt_id = str(uuid4())

    with session_factory() as db:
        client = Client(
            id=client_id,
            client_code=f"UNIFIED-{uuid4().hex[:8]}",
            name_cn="统一测试客户",
            name_en="Unified Test Client",
            client_type="CLIENT",
            default_currency="CNY",
            is_active=True,
        )
        case = Case(
            id=case_id,
            case_no=f"UNIFIED-CASE-{uuid4().hex[:8]}",
            case_type="NORMAL",
            patent_category="INV",
            flow_dir="CN_DOMESTIC",
            client_id=client_id,
        )
        payment = Payment(
            id=payment_id,
            pay_no="PAY-001",
            client_id=client_id,
            pay_date=date(2026, 3, 1),
            currency="CNY",
            amount=Decimal("100.00"),
            remark="付款备注",
        )
        payment_line = PaymentLine(
            payment_id=payment_id,
            case_id=case_id,
            raw_amount=Decimal("100.00"),
            allocated_amt=Decimal("0.00"),
            balance_amt=Decimal("100.00"),
        )
        receipt = CaseReceipt(
            id=receipt_id,
            case_id=case_id,
            fee_type="SERVICE",
            currency="CNY",
            receivable_amt=Decimal("120.00"),
            received_amt=Decimal("80.00"),
            last_receipt_date=date(2026, 3, 2),
            fee_code="FEE-001",
            year_no=2026,
            is_arrears=True,
            invoice_no="INV-001",
            is_commissionable=False,
            remark="收款备注",
        )

        db.add(client)
        db.flush()
        db.add(case)
        db.flush()
        db.add(payment)
        db.flush()
        db.add(payment_line)
        db.add(receipt)
        db.commit()

    return {
        "client_id": client_id,
        "case_id": case_id,
        "payment_id": payment_id,
        "receipt_id": receipt_id,
    }


def _seed_fee_unified_query_status_rows(session_factory) -> dict[str, str]:
    client_id = str(uuid4())
    client_name = f"状态测试客户-{uuid4().hex[:8]}"
    settled_case_id = str(uuid4())
    prepayment_case_id = str(uuid4())
    settled_receipt_id = str(uuid4())
    prepayment_receipt_id = str(uuid4())

    with session_factory() as db:
        client = Client(
            id=client_id,
            client_code=f"STATUS-{uuid4().hex[:8]}",
            name_cn=client_name,
            name_en="Status Test Client",
            client_type="CLIENT",
            default_currency="CNY",
            is_active=True,
        )
        settled_case = Case(
            id=settled_case_id,
            case_no=f"STATUS-CASE-SETTLED-{uuid4().hex[:8]}",
            case_type="NORMAL",
            patent_category="INV",
            flow_dir="CN_DOMESTIC",
            client_id=client_id,
        )
        prepayment_case = Case(
            id=prepayment_case_id,
            case_no=f"STATUS-CASE-PREPAY-{uuid4().hex[:8]}",
            case_type="NORMAL",
            patent_category="INV",
            flow_dir="CN_DOMESTIC",
            client_id=client_id,
        )
        settled_receipt = CaseReceipt(
            id=settled_receipt_id,
            case_id=settled_case_id,
            fee_type="SERVICE",
            currency="CNY",
            receivable_amt=Decimal("100.00"),
            received_amt=Decimal("100.00"),
            last_receipt_date=date(2030, 1, 15),
            fee_code="FEE-SETTLED",
            year_no=2030,
            is_arrears=True,
            is_prepayment=False,
            invoice_no="INV-SETTLED",
            is_commissionable=False,
            remark="已结清收款",
        )
        prepayment_receipt = CaseReceipt(
            id=prepayment_receipt_id,
            case_id=prepayment_case_id,
            fee_type="SERVICE",
            currency="CNY",
            receivable_amt=Decimal("100.00"),
            received_amt=Decimal("120.00"),
            last_receipt_date=date(2030, 1, 16),
            fee_code="FEE-PREPAY",
            year_no=2030,
            is_arrears=False,
            is_prepayment=False,
            invoice_no="INV-PREPAY",
            is_commissionable=False,
            remark="预收款",
        )

        db.add(client)
        db.flush()
        db.add(settled_case)
        db.flush()
        db.add(prepayment_case)
        db.flush()
        db.add(settled_receipt)
        db.add(prepayment_receipt)
        db.commit()

    return {
        "client_id": client_id,
        "party_name": client_name,
        "settled_receipt_id": settled_receipt_id,
        "prepayment_receipt_id": prepayment_receipt_id,
    }


def _seed_fee_unified_query_payment_case_rows(session_factory) -> dict[str, str]:
    client_id = str(uuid4())
    client_name = f"多案卷测试客户-{uuid4().hex[:8]}"
    case_a_id = str(uuid4())
    case_b_id = str(uuid4())
    multi_payment_id = str(uuid4())
    single_payment_id = str(uuid4())

    with session_factory() as db:
        client = Client(
            id=client_id,
            client_code=f"PAYCASE-{uuid4().hex[:8]}",
            name_cn=client_name,
            name_en="Payment Case Test Client",
            client_type="CLIENT",
            default_currency="CNY",
            is_active=True,
        )
        case_a = Case(
            id=case_a_id,
            case_no=f"PAYCASE-A-{uuid4().hex[:8]}",
            case_type="NORMAL",
            patent_category="INV",
            flow_dir="CN_DOMESTIC",
            client_id=client_id,
        )
        case_b = Case(
            id=case_b_id,
            case_no=f"PAYCASE-B-{uuid4().hex[:8]}",
            case_type="NORMAL",
            patent_category="INV",
            flow_dir="CN_DOMESTIC",
            client_id=client_id,
        )
        multi_payment = Payment(
            id=multi_payment_id,
            pay_no="PAY-MULTI-001",
            client_id=client_id,
            pay_date=date(2030, 2, 1),
            currency="CNY",
            amount=Decimal("200.00"),
            remark="多案卷付款",
        )
        single_payment = Payment(
            id=single_payment_id,
            pay_no="PAY-SINGLE-001",
            client_id=client_id,
            pay_date=date(2030, 2, 2),
            currency="CNY",
            amount=Decimal("80.00"),
            remark="单案卷付款",
        )

        db.add(client)
        db.flush()
        db.add(case_a)
        db.flush()
        db.add(case_b)
        db.flush()
        db.add(multi_payment)
        db.flush()
        db.add(
            PaymentLine(
                payment_id=multi_payment_id,
                case_id=case_a_id,
                raw_amount=Decimal("100.00"),
                allocated_amt=Decimal("0.00"),
                balance_amt=Decimal("100.00"),
            )
        )
        db.add(
            PaymentLine(
                payment_id=multi_payment_id,
                case_id=case_b_id,
                raw_amount=Decimal("100.00"),
                allocated_amt=Decimal("0.00"),
                balance_amt=Decimal("100.00"),
            )
        )
        db.add(single_payment)
        db.flush()
        db.add(
            PaymentLine(
                payment_id=single_payment_id,
                case_id=case_a_id,
                raw_amount=Decimal("80.00"),
                allocated_amt=Decimal("0.00"),
                balance_amt=Decimal("80.00"),
            )
        )
        db.commit()

    return {
        "client_id": client_id,
        "party_name": client_name,
        "case_a_id": case_a_id,
        "case_b_id": case_b_id,
        "multi_payment_id": multi_payment_id,
        "single_payment_id": single_payment_id,
    }


def test_fee_unified_query_merges_payment_and_receipt_rows(
    client,
    auth_headers,
    session_factory,
) -> None:
    seeded = _seed_fee_unified_query_rows(session_factory)

    resp = client.get("/api/v1/fee-unified-query", headers=auth_headers)
    assert resp.status_code == 200, resp.text

    data = resp.json()
    assert data["page"] == 1
    assert data["page_size"] == 20
    assert data["total"] == 2
    assert len(data["items"]) == 2

    first, second = data["items"]
    assert first["record_type"] == "RECEIPT"
    assert first["record_id"] == seeded["receipt_id"]
    assert first["case_id"] == seeded["case_id"]
    assert first["biz_no"] == "INV-001"
    assert first["party_name"] == "统一测试客户"
    assert Decimal(str(first["amount"])) == Decimal("80.00")
    assert first["currency"] == "CNY"
    assert first["status"] == "ARREARS"
    assert first["biz_date"] == "2026-03-02"
    assert first["remark"] == "收款备注"

    assert second["record_type"] == "PAYMENT"
    assert second["record_id"] == seeded["payment_id"]
    assert second["case_id"] == seeded["case_id"]
    assert second["biz_no"] == "PAY-001"
    assert second["party_name"] == "统一测试客户"
    assert Decimal(str(second["amount"])) == Decimal("100.00")
    assert second["currency"] == "CNY"
    assert second["status"] == "UNALLOCATED"
    assert second["biz_date"] == "2026-03-01"
    assert second["remark"] == "付款备注"


def test_fee_unified_query_filters_and_paginates(
    client,
    auth_headers,
    session_factory,
) -> None:
    seeded = _seed_fee_unified_query_rows(session_factory)

    with session_factory() as db:
        extra_payment = Payment(
            pay_no="PAY-002",
            client_id=seeded["client_id"],
            pay_date=date(2026, 3, 3),
            currency="CNY",
            amount=Decimal("150.00"),
            remark="第二笔付款",
        )
        db.add(extra_payment)
        db.flush()
        db.add(
            PaymentLine(
                payment_id=extra_payment.id,
                case_id=seeded["case_id"],
                raw_amount=Decimal("150.00"),
                allocated_amt=Decimal("150.00"),
                balance_amt=Decimal("0.00"),
            )
        )
        db.commit()

    paged_resp = client.get(
        "/api/v1/fee-unified-query",
        params={
            "record_type": "PAYMENT",
            "case_id": seeded["case_id"],
            "page": 1,
            "page_size": 1,
        },
        headers=auth_headers,
    )
    assert paged_resp.status_code == 200, paged_resp.text
    paged_data = paged_resp.json()
    assert paged_data["total"] == 2
    assert len(paged_data["items"]) == 1
    assert paged_data["items"][0]["biz_no"] == "PAY-002"

    amount_resp = client.get(
        "/api/v1/fee-unified-query",
        params={"amount_from": "120.00", "amount_to": "160.00"},
        headers=auth_headers,
    )
    assert amount_resp.status_code == 200, amount_resp.text
    amount_data = amount_resp.json()
    assert amount_data["total"] == 1
    assert amount_data["items"][0]["biz_no"] == "PAY-002"


def test_fee_unified_query_uses_date_from_date_to_contract(
    client,
    auth_headers,
    session_factory,
) -> None:
    seeded = _seed_fee_unified_query_status_rows(session_factory)

    resp = client.get(
        "/api/v1/fee-unified-query",
        params={
            "party_name": seeded["party_name"],
            "date_from": "2030-01-15",
            "date_to": "2030-01-15",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 200, resp.text

    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["record_id"] == seeded["settled_receipt_id"]
    assert data["items"][0]["biz_date"] == "2030-01-15"


def test_fee_unified_query_derives_receipt_status_from_amount_facts(
    client,
    auth_headers,
    session_factory,
) -> None:
    seeded = _seed_fee_unified_query_status_rows(session_factory)

    resp = client.get(
        "/api/v1/fee-unified-query",
        params={
            "record_type": "RECEIPT",
            "party_name": seeded["party_name"],
        },
        headers=auth_headers,
    )
    assert resp.status_code == 200, resp.text

    data = resp.json()
    assert data["total"] == 2
    items_by_biz_no = {item["biz_no"]: item for item in data["items"]}
    assert items_by_biz_no["INV-SETTLED"]["status"] == "SETTLED"
    assert items_by_biz_no["INV-PREPAY"]["status"] == "PREPAYMENT"


def test_fee_unified_query_filters_payment_case_id_by_any_linked_line(
    client,
    auth_headers,
    session_factory,
) -> None:
    seeded = _seed_fee_unified_query_payment_case_rows(session_factory)

    resp = client.get(
        "/api/v1/fee-unified-query",
        params={
            "record_type": "PAYMENT",
            "party_name": seeded["party_name"],
        },
        headers=auth_headers,
    )
    assert resp.status_code == 200, resp.text

    data = resp.json()
    assert data["total"] == 2
    items_by_biz_no = {item["biz_no"]: item for item in data["items"]}
    assert items_by_biz_no["PAY-MULTI-001"]["case_id"] is None
    assert items_by_biz_no["PAY-SINGLE-001"]["case_id"] == seeded["case_a_id"]

    filtered_resp = client.get(
        "/api/v1/fee-unified-query",
        params={
            "record_type": "PAYMENT",
            "party_name": seeded["party_name"],
            "case_id": seeded["case_b_id"],
        },
        headers=auth_headers,
    )
    assert filtered_resp.status_code == 200, filtered_resp.text
    filtered_data = filtered_resp.json()
    assert filtered_data["total"] == 1
    assert filtered_data["items"][0]["biz_no"] == "PAY-MULTI-001"


def test_fee_unified_query_rejects_inverted_date_range(
    client,
    auth_headers,
    session_factory,
) -> None:
    seeded = _seed_fee_unified_query_status_rows(session_factory)

    resp = client.get(
        "/api/v1/fee-unified-query",
        params={
            "party_name": seeded["party_name"],
            "date_from": "2030-01-16",
            "date_to": "2030-01-15",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 400, resp.text


def test_fee_unified_query_rejects_inverted_amount_range(
    client,
    auth_headers,
    session_factory,
) -> None:
    _seed_fee_unified_query_rows(session_factory)

    resp = client.get(
        "/api/v1/fee-unified-query",
        params={
            "amount_from": "160.00",
            "amount_to": "120.00",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 400, resp.text


def test_fee_unified_query_requires_both_permissions(
    client,
    auth_headers,
    session_factory,
) -> None:
    with session_factory() as db:
        admin_role = db.query(T_Role).filter(T_Role.code == "Admin").first()
        assert admin_role is not None
        missing_perm = (
            db.query(T_RolePerm)
            .filter(
                T_RolePerm.role_id == admin_role.id,
                T_RolePerm.perm_code == "CaseReceipt.Read",
            )
            .first()
        )
        assert missing_perm is not None
        db.delete(missing_perm)
        db.commit()

    try:
        resp = client.get("/api/v1/fee-unified-query", headers=auth_headers)
        assert resp.status_code == 403, resp.text
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
