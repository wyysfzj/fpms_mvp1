from __future__ import annotations

from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from app.modules.annuity.models import PayList  # noqa: F401
from app.modules.masterdata.applicants.models import Applicant


def _seed_applicant(
    session_factory: sessionmaker,
    *,
    code: str,
    name_cn: str,
    total_power_of_attorney_no: str | None = None,
) -> str:
    applicant_id = str(uuid4())
    with session_factory() as db:
        db.add(
            Applicant(
                id=applicant_id,
                code=code,
                name_cn=name_cn,
                total_power_of_attorney_no=total_power_of_attorney_no,
                is_active=True,
            )
        )
        db.commit()
    return applicant_id


def test_create_applicant_accepts_total_power_of_attorney_no(
    client,
    auth_headers,
) -> None:
    code = f"APP-POA-{uuid4().hex[:8].upper()}"

    response = client.post(
        "/api/v1/applicants",
        headers=auth_headers,
        json={
            "code": code,
            "name_cn": "总委号申请人",
            "total_power_of_attorney_no": "POA-2026-001",
        },
    )

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["code"] == code
    assert body["total_power_of_attorney_no"] == "POA-2026-001"


def test_list_applicants_returns_total_power_of_attorney_no(
    client,
    auth_headers,
    session_factory,
) -> None:
    code = f"APP-POA-{uuid4().hex[:8].upper()}"
    _seed_applicant(
        session_factory,
        code=code,
        name_cn="列表总委号申请人",
        total_power_of_attorney_no="POA-LIST-001",
    )

    response = client.get("/api/v1/applicants", params={"q": code}, headers=auth_headers)

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["items"][0]["code"] == code
    assert body["items"][0]["total_power_of_attorney_no"] == "POA-LIST-001"


def test_update_applicant_normalizes_blank_total_power_of_attorney_no(
    client,
    auth_headers,
    session_factory,
) -> None:
    applicant_id = _seed_applicant(
        session_factory,
        code=f"APP-POA-{uuid4().hex[:8].upper()}",
        name_cn="更新总委号申请人",
        total_power_of_attorney_no="POA-OLD-001",
    )

    update_response = client.put(
        f"/api/v1/applicants/{applicant_id}",
        headers=auth_headers,
        json={"total_power_of_attorney_no": "   "},
    )

    assert update_response.status_code == 200, update_response.text
    assert update_response.json()["total_power_of_attorney_no"] is None

    with session_factory() as db:
        applicant = db.execute(select(Applicant).where(Applicant.id == applicant_id)).scalar_one()
        assert applicant.total_power_of_attorney_no is None
