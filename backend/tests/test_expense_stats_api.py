from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.modules.billing.models import CaseReceipt
from app.modules.cases.models import Case
from app.modules.expenses.models import Expense
from app.modules.masterdata.clients.models import Client


def test_expense_stats_include_case_and_client_groupings(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    suffix = uuid4().hex[:8].upper()
    case_a_id = str(uuid4())
    case_b_id = str(uuid4())
    client_a_id = str(uuid4())
    client_b_id = str(uuid4())

    with session_factory() as db:
        db.add_all(
            [
                Client(
                    id=client_a_id,
                    client_code=f"CLIENT-A-{suffix}",
                    name_cn="甲方客户",
                    client_type="CLIENT",
                    default_currency="CNY",
                    is_active=True,
                ),
                Client(
                    id=client_b_id,
                    client_code=f"CLIENT-B-{suffix}",
                    name_cn="乙方客户",
                    client_type="CLIENT",
                    default_currency="CNY",
                    is_active=True,
                ),
            ]
        )
        db.commit()

        db.add_all(
            [
                Case(
                    id=case_a_id,
                    case_no=f"CASE-A-{suffix}",
                    client_id=client_a_id,
                    title_cn="案件A",
                ),
                Case(
                    id=case_b_id,
                    case_no=f"CASE-B-{suffix}",
                    client_id=client_b_id,
                    title_cn="案件B",
                ),
            ]
        )
        db.commit()

        db.add_all(
            [
                Expense(
                    case_id=case_a_id,
                    client_id=None,
                    expense_no=f"EXP-A1-{suffix}",
                    category="TRANSLATION",
                    expense_date=date(2026, 4, 1),
                    currency="CNY",
                    amount=Decimal("100.00"),
                    status="DRAFT",
                ),
                Expense(
                    case_id=case_a_id,
                    client_id=client_a_id,
                    expense_no=f"EXP-A2-{suffix}",
                    category="TRANSPORT",
                    expense_date=date(2026, 4, 2),
                    currency="CNY",
                    amount=Decimal("50.00"),
                    status="DRAFT",
                ),
                Expense(
                    case_id=case_b_id,
                    client_id=client_b_id,
                    expense_no=f"EXP-B1-{suffix}",
                    category="SEARCH_DB",
                    expense_date=date(2026, 4, 3),
                    currency="CNY",
                    amount=Decimal("80.00"),
                    status="DRAFT",
                ),
            ]
        )
        db.commit()

    response = client.get(
        "/api/v1/expenses",
        headers=auth_headers,
        params={"include_stats": True},
    )

    assert response.status_code == 200, response.text
    stats = response.json()["stats"]

    assert stats["count_total"] >= 3
    case_amounts = {item["label"]: item for item in stats["case_amounts"]}
    client_amounts = {item["label"]: item for item in stats["client_amounts"]}

    assert case_amounts[f"CASE-A-{suffix}"]["expense_count"] == 2
    assert Decimal(case_amounts[f"CASE-A-{suffix}"]["total_amount"]) == Decimal("150.00")
    assert case_amounts[f"CASE-B-{suffix}"]["expense_count"] == 1
    assert Decimal(case_amounts[f"CASE-B-{suffix}"]["total_amount"]) == Decimal("80.00")

    assert client_amounts["甲方客户"]["expense_count"] == 2
    assert Decimal(client_amounts["甲方客户"]["total_amount"]) == Decimal("150.00")
    assert client_amounts["乙方客户"]["expense_count"] == 1
    assert Decimal(client_amounts["乙方客户"]["total_amount"]) == Decimal("80.00")


def test_expense_stats_require_expense_read_permission(
    client: TestClient,
    auth_headers: dict[str, str],
    monkeypatch,
) -> None:
    import app.api.deps as deps

    def _no_perms(_db, _user_id) -> set[str]:
        return set()

    monkeypatch.setattr(deps, "get_user_permissions", _no_perms)

    response = client.get("/api/v1/expenses", headers=auth_headers, params={"include_stats": True})

    assert response.status_code == 403, response.text
    assert response.json()["error"]["details"]["required_perm"] == "Expense.Read"


def test_expense_stats_include_case_level_gross_profit_by_currency(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    suffix = uuid4().hex[:8].upper()
    case_a_id = str(uuid4())
    case_b_id = str(uuid4())
    client_a_id = str(uuid4())

    with session_factory() as db:
        db.add(
            Client(
                id=client_a_id,
                client_code=f"CLIENT-GP-{suffix}",
                name_cn="毛利客户",
                client_type="CLIENT",
                default_currency="CNY",
                is_active=True,
            )
        )
        db.commit()

        db.add_all(
            [
                Case(
                    id=case_a_id,
                    case_no=f"CASE-GP-A-{suffix}",
                    client_id=client_a_id,
                    title_cn="毛利案件A",
                ),
                Case(
                    id=case_b_id,
                    case_no=f"CASE-GP-B-{suffix}",
                    client_id=client_a_id,
                    title_cn="毛利案件B",
                ),
            ]
        )
        db.commit()

        db.add_all(
            [
                Expense(
                    case_id=case_a_id,
                    client_id=client_a_id,
                    expense_no=f"EXP-GP-A1-{suffix}",
                    category="TRANSLATION",
                    expense_date=date(2026, 4, 4),
                    currency="CNY",
                    amount=Decimal("120.00"),
                    status="DRAFT",
                ),
                Expense(
                    case_id=case_b_id,
                    client_id=client_a_id,
                    expense_no=f"EXP-GP-B1-{suffix}",
                    category="SEARCH_DB",
                    expense_date=date(2026, 4, 5),
                    currency="USD",
                    amount=Decimal("40.00"),
                    status="DRAFT",
                ),
            ]
        )
        db.add_all(
            [
                CaseReceipt(
                    id=str(uuid4()),
                    case_id=case_a_id,
                    fee_type="SERVICE",
                    currency="CNY",
                    receivable_amt=Decimal("300.00"),
                    received_amt=Decimal("260.00"),
                    last_receipt_date=date(2026, 4, 5),
                ),
                CaseReceipt(
                    id=str(uuid4()),
                    case_id=case_b_id,
                    fee_type="SERVICE",
                    currency="USD",
                    receivable_amt=Decimal("80.00"),
                    received_amt=Decimal("90.00"),
                    last_receipt_date=date(2026, 4, 6),
                ),
                CaseReceipt(
                    id=str(uuid4()),
                    case_id=case_a_id,
                    fee_type="SERVICE",
                    currency="USD",
                    receivable_amt=Decimal("999.00"),
                    received_amt=Decimal("999.00"),
                    last_receipt_date=date(2026, 4, 6),
                ),
            ]
        )
        db.commit()

    response = client.get(
        "/api/v1/expenses",
        headers=auth_headers,
        params={"include_stats": True},
    )

    assert response.status_code == 200, response.text
    stats = response.json()["stats"]

    gross_profit_rows = {
        (item["key"], item["currency"]): item for item in stats["gross_profit_amounts"]
    }

    case_a = gross_profit_rows[(case_a_id, "CNY")]
    assert case_a["label"] == f"CASE-GP-A-{suffix}"
    assert Decimal(case_a["expense_total"]) == Decimal("120.00")
    assert Decimal(case_a["received_total"]) == Decimal("260.00")
    assert Decimal(case_a["gross_profit_total"]) == Decimal("140.00")

    case_b = gross_profit_rows[(case_b_id, "USD")]
    assert case_b["label"] == f"CASE-GP-B-{suffix}"
    assert Decimal(case_b["expense_total"]) == Decimal("40.00")
    assert Decimal(case_b["received_total"]) == Decimal("90.00")
    assert Decimal(case_b["gross_profit_total"]) == Decimal("50.00")

    assert (case_a_id, "USD") not in gross_profit_rows
