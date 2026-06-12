from __future__ import annotations

from decimal import Decimal
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.modules.annuity.models import PayList  # noqa: F401
from app.modules.cases.models import Case, T_CaseApplicant, T_CaseInventor
from app.modules.masterdata.applicants.models import Applicant
from app.modules.official_workflows.models import OfficialWorkPackage

BASE = "/api/v1/official-work-packages"


def _create_filing_package_with_applicant(
    session_factory: sessionmaker,
    *,
    applicant_id: str | None,
    applicant_total_poa: str | None,
) -> str:
    with session_factory() as db:
        linked_applicant_id = applicant_id
        if applicant_id:
            db.add(
                Applicant(
                    id=applicant_id,
                    code=f"APP-{uuid4().hex[:8].upper()}",
                    name_cn="总委号主数据申请人",
                    total_power_of_attorney_no=applicant_total_poa,
                    is_active=True,
                )
            )
            db.flush()

        case = Case(
            id=str(uuid4()),
            case_no=f"POA-{uuid4().hex[:8].upper()}",
            case_type="NORMAL",
            patent_category="INV",
            flow_dir="CN_DOMESTIC",
            title_cn="总委号递交准备测试案件",
            primary_agent_id="agent-user-1",
            spec_pages=10,
            claim_count=8,
            fee_reduction="0.85",
            discount_rate=Decimal("0.8500"),
        )
        db.add(case)
        db.flush()

        db.add_all(
            [
                T_CaseApplicant(
                    id=str(uuid4()),
                    case_id=case.id,
                    applicant_id=linked_applicant_id,
                    seq=1,
                    is_first=True,
                    name_cn="总委号案件申请人",
                    nationality="CN",
                    certificate_type="USCI",
                    certificate_no="91110000123456789X",
                    official_postcode="100000",
                    official_applicant_kind="ENTERPRISE",
                ),
                T_CaseInventor(
                    id=str(uuid4()),
                    case_id=case.id,
                    seq=1,
                    name_cn="测试发明人",
                    nationality="CN",
                    china_id_no="110101199001011234",
                ),
            ]
        )
        package = OfficialWorkPackage(
            id=str(uuid4()),
            case_id=case.id,
            package_kind="FILING_PREP",
            status="PREPARING",
            external_system="CNIPA_WEB",
        )
        db.add(package)
        db.commit()
        return package.id


@pytest.mark.parametrize(
    ("applicant_id", "total_poa", "expected_status", "message_fragment"),
    [
        (str(uuid4()), "POA-2026-001", "READY", None),
        (None, None, "NEEDS_CONFIRMATION", "申请人主数据映射待确认"),
        (str(uuid4()), None, "MISSING", "总委托书备案编号缺失"),
    ],
)
def test_filing_preparation_reports_total_poa_readiness(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
    applicant_id: str | None,
    total_poa: str | None,
    expected_status: str,
    message_fragment: str | None,
) -> None:
    package_id = _create_filing_package_with_applicant(
        session_factory,
        applicant_id=applicant_id,
        applicant_total_poa=total_poa,
    )

    response = client.post(
        f"{BASE}/{package_id}/filing-preparation/refresh",
        headers=auth_headers,
        json={},
    )

    assert response.status_code == 200, response.text
    items = {item["code"]: item for item in response.json()["official_field_summary"]["items"]}
    total_poa_item = items["APPLICANT_1_TOTAL_POWER_OF_ATTORNEY_NO"]
    assert total_poa_item["label"] == "总委托书备案编号"
    assert total_poa_item["status"] == expected_status
    if message_fragment:
        assert message_fragment in total_poa_item["message"]
    else:
        assert total_poa_item["message"] is None
