from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from io import BytesIO
from uuid import uuid4
from zipfile import ZipFile

from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from app.modules.auth.models import T_Role
from app.modules.cases.models import Case
from app.modules.commission.models import Commission, CommissionSettleLine, CommissionSettlement
from app.modules.rbac.models import T_RolePerm


def _uid(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:8].upper()}"


def _create_case(session_factory: sessionmaker, *, case_no: str | None = None) -> str:
    with session_factory() as db:
        case = Case(
            id=str(uuid4()),
            case_no=case_no or _uid("CASE"),
            case_type="NORMAL",
            patent_category="INV",
            flow_dir="CN_DOMESTIC",
            title_cn="提成报表测试案件",
        )
        db.add(case)
        db.commit()
        return case.id


def _create_report_row(
    session_factory: sessionmaker,
    *,
    settlement_no: str,
    settlement_agent_id: str,
    settlement_status: str,
    commission_case_id: str,
    commission_agent_id: str | None,
    line_amount: str,
    line_status: str,
    created_at: datetime,
) -> None:
    with session_factory() as db:
        settlement = CommissionSettlement(
            settlement_no=settlement_no,
            agent_id=settlement_agent_id,
            status=settlement_status,
            currency="CNY",
            period_from=date(2026, 3, 1),
            period_to=date(2026, 3, 31),
            line_count=1,
            total_amount=Decimal(line_amount),
            created_at=created_at,
            updated_at=created_at,
        )
        db.add(settlement)
        db.flush()

        commission = Commission(
            case_id=commission_case_id,
            agent_id=commission_agent_id,
            base_fee=Decimal("0"),
            s1_rate=Decimal("0"),
            s1_amount=Decimal("0"),
            s1_done=False,
            s2_rate=Decimal("0"),
            s2_amount=Decimal("0"),
            s2_done=False,
            wait_pay=False,
            force_settle=False,
            status="SETTLED",
            is_settleable=True,
            settleable_date=date(2026, 3, 20),
            created_at=created_at,
            updated_at=created_at,
        )
        db.add(commission)
        db.flush()

        line = CommissionSettleLine(
            settlement_id=settlement.id,
            commission_id=commission.id,
            line_no=1,
            amount=Decimal(line_amount),
            status=line_status,
            created_at=created_at,
            updated_at=created_at,
        )
        db.add(line)
        db.commit()


def test_settlement_report_returns_summary_and_grouped_totals(
    client,
    auth_headers,
    session_factory: sessionmaker,
) -> None:
    case_a = _create_case(session_factory, case_no="CASE-REPORT-A")
    case_b = _create_case(session_factory, case_no="CASE-REPORT-B")

    _create_report_row(
        session_factory,
        settlement_no="SETTLE-001",
        settlement_agent_id="AGENT-A",
        settlement_status="SETTLED",
        commission_case_id=case_a,
        commission_agent_id="AGENT-A",
        line_amount="100.00",
        line_status="SETTLED",
        created_at=datetime(2026, 3, 10, 9, 0, 0),
    )
    _create_report_row(
        session_factory,
        settlement_no="SETTLE-002",
        settlement_agent_id="AGENT-A",
        settlement_status="SETTLED",
        commission_case_id=case_b,
        commission_agent_id="AGENT-B",
        line_amount="25.50",
        line_status="SETTLED",
        created_at=datetime(2026, 3, 11, 9, 0, 0),
    )
    _create_report_row(
        session_factory,
        settlement_no="SETTLE-003",
        settlement_agent_id="AGENT-B",
        settlement_status="DRAFT",
        commission_case_id=case_a,
        commission_agent_id=None,
        line_amount="74.50",
        line_status="DRAFT",
        created_at=datetime(2026, 3, 12, 9, 0, 0),
    )

    resp = client.get(
        "/api/v1/commission/reports/settlement",
        headers=auth_headers,
        params={
            "currency": "cny",
            "settlement_status": "settled",
            "line_status": "settled",
            "date_from": "2026-03-01",
            "date_to": "2026-03-31",
            "time_field": "line_created_at",
        },
    )
    assert resp.status_code == 200, resp.text
    payload = resp.json()

    assert {"filters", "summary", "totals", "by_agent", "by_case", "details"}.issubset(payload)
    assert payload["filters"] == {
        "agent_id": None,
        "case_id": None,
        "currency": "CNY",
        "settlement_status": "SETTLED",
        "line_status": "SETTLED",
        "date_from": "2026-03-01",
        "date_to": "2026-03-31",
        "time_field": "line_created_at",
    }

    assert payload["summary"] == {
        "line_count": 2,
        "settlement_count": 2,
        "case_count": 2,
        "agent_count": 2,
        "total_amount": "125.50",
    }
    assert payload["totals"] == {
        "line_count": 2,
        "total_amount": "125.50",
    }

    assert payload["by_agent"] == [
        {"agent_id": "AGENT-A", "line_count": 1, "total_amount": "100.00"},
        {"agent_id": "AGENT-B", "line_count": 1, "total_amount": "25.50"},
    ]
    by_case = {row["case_id"]: row for row in payload["by_case"]}
    assert by_case[case_a] == {"case_id": case_a, "line_count": 1, "total_amount": "100.00"}
    assert by_case[case_b] == {"case_id": case_b, "line_count": 1, "total_amount": "25.50"}
    assert len(payload["details"]) == 2
    assert {detail["line_status"] for detail in payload["details"]} == {"SETTLED"}
    assert {detail["settlement_status"] for detail in payload["details"]} == {"SETTLED"}

    with session_factory() as db:
        rows = db.execute(select(CommissionSettlement.id)).scalars().all()
        assert len(rows) == 3


def test_settlement_report_export_returns_excel_payload(
    client,
    auth_headers,
    session_factory: sessionmaker,
) -> None:
    case_a = _create_case(session_factory, case_no="CASE-EXPORT-A")
    case_b = _create_case(session_factory, case_no="CASE-EXPORT-B")

    _create_report_row(
        session_factory,
        settlement_no="SETTLE-EXP-001",
        settlement_agent_id="AGENT-EXP-A",
        settlement_status="SETTLED",
        commission_case_id=case_a,
        commission_agent_id="AGENT-EXP-A",
        line_amount="88.00",
        line_status="SETTLED",
        created_at=datetime(2026, 3, 9, 9, 0, 0),
    )
    _create_report_row(
        session_factory,
        settlement_no="SETTLE-EXP-002",
        settlement_agent_id="AGENT-EXP-B",
        settlement_status="SETTLED",
        commission_case_id=case_b,
        commission_agent_id="AGENT-EXP-B",
        line_amount="18.50",
        line_status="SETTLED",
        created_at=datetime(2026, 3, 10, 9, 0, 0),
    )

    response = client.get(
        "/api/v1/commission/reports/settlement/export",
        headers=auth_headers,
        params={
            "settlement_status": "SETTLED",
            "line_status": "SETTLED",
            "date_from": "2026-03-01",
            "date_to": "2026-03-31",
        },
    )

    assert response.status_code == 200, response.text
    assert (
        response.headers["content-type"]
        == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    assert 'attachment; filename="commission-settlement-report.xlsx"' in response.headers.get(
        "content-disposition", ""
    )

    archive = ZipFile(BytesIO(response.content))
    sheet_xml = archive.read("xl/worksheets/sheet1.xml").decode("utf-8")
    assert "提成结算报表" in sheet_xml
    assert "AGENT-EXP-A" in sheet_xml
    assert "SETTLE-EXP-001" in sheet_xml
    assert case_a in sheet_xml


def test_settlement_report_export_requires_report_permission(
    client,
    auth_headers,
    session_factory: sessionmaker,
) -> None:
    case_a = _create_case(session_factory, case_no="CASE-EXPORT-PERM")
    _create_report_row(
        session_factory,
        settlement_no="SETTLE-EXP-PERM",
        settlement_agent_id="AGENT-PERM",
        settlement_status="SETTLED",
        commission_case_id=case_a,
        commission_agent_id="AGENT-PERM",
        line_amount="10.00",
        line_status="SETTLED",
        created_at=datetime(2026, 3, 9, 9, 0, 0),
    )

    with session_factory() as db:
        admin_role = db.query(T_Role).filter(T_Role.code == "Admin").first()
        assert admin_role is not None
        binding = (
            db.query(T_RolePerm)
            .filter(
                T_RolePerm.role_id == admin_role.id,
                T_RolePerm.perm_code == "CommissionReport.Read",
            )
            .first()
        )
        assert binding is not None
        db.delete(binding)
        db.commit()

    try:
        response = client.get(
            "/api/v1/commission/reports/settlement/export",
            headers=auth_headers,
        )
        assert response.status_code == 403, response.text
    finally:
        with session_factory() as db:
            admin_role = db.query(T_Role).filter(T_Role.code == "Admin").first()
            assert admin_role is not None
            restored = (
                db.query(T_RolePerm)
                .filter(
                    T_RolePerm.role_id == admin_role.id,
                    T_RolePerm.perm_code == "CommissionReport.Read",
                )
                .first()
            )
            if not restored:
                db.add(
                    T_RolePerm(
                        id=str(uuid4()),
                        role_id=admin_role.id,
                        perm_code="CommissionReport.Read",
                    )
                )
                db.commit()
