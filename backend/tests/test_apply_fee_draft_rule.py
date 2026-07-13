from __future__ import annotations

from decimal import Decimal
from uuid import uuid4

from fastapi.testclient import TestClient

from app.modules.fees.models import FeeDraft, FeeRate
from app.modules.masterdata.applicants.models import Applicant


def _create_client(client: TestClient, auth_headers: dict[str, str]) -> str:
    response = client.post(
        "/api/v1/clients",
        json={
            "client_code": f"AFD-CL-{uuid4().hex[:8]}",
            "name_cn": "申请费草单客户",
            "client_type": "CLIENT",
            "default_currency": "CNY",
            "is_active": True,
        },
        headers=auth_headers,
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def _seed_applicant(session_factory) -> str:
    applicant_id = str(uuid4())
    with session_factory() as db:
        db.add(
            Applicant(
                id=applicant_id,
                code=f"AFD-AP-{uuid4().hex[:8]}",
                name_cn=f"申请费草单申请人-{uuid4().hex[:8]}",
                applicant_type="ENTITY",
                is_active=True,
            )
        )
        db.commit()
    return applicant_id


def _seed_apply_fee_rates(session_factory, *, include_exam: bool = True) -> None:
    rows = [
        ("CN_INV_APPLICATION_FEE", "发明申请费", "GOV", Decimal("900.00"), "FIXED", True),
        ("CN_UM_APPLICATION_FEE", "实用新型申请费", "GOV", Decimal("500.00"), "FIXED", True),
        ("CN_DES_APPLICATION_FEE", "外观设计申请费", "GOV", Decimal("500.00"), "FIXED", True),
        ("CN_EXCESS_CLAIM_FEE", "权利要求附加费", "GOV", Decimal("150.00"), "PER_CLAIM", False),
        ("CN_PUBLICATION_PRINT_FEE", "公布印刷费", "GOV", Decimal("50.00"), "FIXED", False),
    ]
    if include_exam:
        rows.append(
            ("CN_SUBSTANTIVE_EXAM_FEE", "发明实审费", "GOV", Decimal("2500.00"), "FIXED", True)
        )

    with session_factory() as db:
        for fee_code, fee_name, fee_type, amount, calc_mode, allow_reduction in rows:
            existing = db.query(FeeRate).filter(FeeRate.fee_code == fee_code).one_or_none()
            if existing is None:
                existing = FeeRate(id=str(uuid4()), fee_code=fee_code)
                db.add(existing)
            existing.fee_name = fee_name
            existing.fee_type = fee_type
            existing.currency = "CNY"
            existing.default_amount = amount
            existing.enabled = True
            existing.calc_mode = calc_mode
            existing.allow_reduction = allow_reduction
        if not include_exam:
            exam_rate = (
                db.query(FeeRate)
                .filter(FeeRate.fee_code == "CN_SUBSTANTIVE_EXAM_FEE")
                .one_or_none()
            )
            if exam_rate is not None:
                exam_rate.enabled = False
        db.commit()


def _create_case(
    client: TestClient,
    auth_headers: dict[str, str],
    *,
    client_id: str,
    applicant_id: str,
    patent_category: str = "INV",
    claim_count: int = 12,
    has_exam_request: bool = True,
) -> dict:
    response = client.post(
        "/api/v1/cases",
        json={
            "case_no": f"AFD-{uuid4().hex[:8]}",
            "case_type": "NORMAL",
            "patent_category": patent_category,
            "flow_dir": "CN_DOMESTIC",
            "client_id": client_id,
            "title_cn": "申请费草单测试案",
            "status": "NOT_FILED",
            "recv_date": "2026-03-01",
            "claim_count": claim_count,
            "has_exam_request": has_exam_request,
            "fee_reduction": "0.85",
            "applicants": [
                {
                    "seq": 1,
                    "is_first": True,
                    "applicant_id": applicant_id,
                    "name_cn": "申请费草单申请人",
                }
            ],
        },
        headers=auth_headers,
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_generate_apply_fee_draft_calculates_items_and_is_idempotent(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory,
) -> None:
    _seed_apply_fee_rates(session_factory)
    client_id = _create_client(client, auth_headers)
    applicant_id = _seed_applicant(session_factory)
    case_data = _create_case(
        client,
        auth_headers,
        client_id=client_id,
        applicant_id=applicant_id,
    )

    response = client.post(
        "/api/v1/fees/drafts/apply-fee/generate",
        json={"case_id": case_data["id"], "currency": "CNY", "discount_rate": "0.10"},
        headers=auth_headers,
    )

    assert response.status_code == 201, response.text
    draft = response.json()
    assert draft["case_id"] == case_data["id"]
    assert draft["client_id"] == client_id
    assert draft["draft_type"] == "APPLY_FEE"
    assert draft["status"] == "OPEN"
    assert Decimal(draft["total_gov"]) == Decimal("860.00")
    assert Decimal(draft["total_service"]) == Decimal("0.00")
    assert Decimal(draft["total_misc"]) == Decimal("0.00")
    assert Decimal(draft["amount"]) == Decimal("860.00")

    items_response = client.get(
        f"/api/v1/fees/drafts/{draft['id']}/items",
        headers=auth_headers,
    )
    assert items_response.status_code == 200, items_response.text
    items = {item["fee_code"]: item for item in items_response.json()}
    assert set(items) == {
        "CN_INV_APPLICATION_FEE",
        "CN_EXCESS_CLAIM_FEE",
        "CN_PUBLICATION_PRINT_FEE",
        "CN_SUBSTANTIVE_EXAM_FEE",
    }
    assert {item["fee_type"] for item in items.values()} == {"GOV"}
    assert Decimal(items["CN_INV_APPLICATION_FEE"]["amount"]) == Decimal("135.00")
    assert Decimal(items["CN_EXCESS_CLAIM_FEE"]["quantity"]) == Decimal("2.0000")
    assert Decimal(items["CN_EXCESS_CLAIM_FEE"]["amount"]) == Decimal("300.00")
    assert Decimal(items["CN_PUBLICATION_PRINT_FEE"]["amount"]) == Decimal("50.00")
    assert Decimal(items["CN_SUBSTANTIVE_EXAM_FEE"]["amount"]) == Decimal("375.00")

    rerun = client.post(
        "/api/v1/fees/drafts/apply-fee/generate",
        json={"case_id": case_data["id"], "currency": "CNY", "discount_rate": "0.10"},
        headers=auth_headers,
    )

    assert rerun.status_code == 200, rerun.text
    assert rerun.json()["id"] == draft["id"]
    with session_factory() as db:
        draft_count = (
            db.query(FeeDraft)
            .filter(
                FeeDraft.case_id == case_data["id"],
                FeeDraft.draft_type == "APPLY_FEE",
                FeeDraft.status == "OPEN",
            )
            .count()
        )
        assert draft_count == 1


def test_generate_apply_fee_draft_reports_missing_rate(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory,
) -> None:
    _seed_apply_fee_rates(session_factory, include_exam=False)
    client_id = _create_client(client, auth_headers)
    applicant_id = _seed_applicant(session_factory)
    case_data = _create_case(
        client,
        auth_headers,
        client_id=client_id,
        applicant_id=applicant_id,
    )

    response = client.post(
        "/api/v1/fees/drafts/apply-fee/generate",
        json={"case_id": case_data["id"], "currency": "CNY"},
        headers=auth_headers,
    )

    assert response.status_code == 409, response.text
    body = response.json()
    assert body["error"]["code"] == "APPLY_FEE_RATE_MISSING"
    assert body["error"]["details"]["missing_fee_codes"] == ["CN_SUBSTANTIVE_EXAM_FEE"]


def test_generate_apply_fee_draft_supports_um_case(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory,
) -> None:
    """实用新型申请费草单：不含公布印刷费/实审费，费减 0.85 应缴 15%。"""
    _seed_apply_fee_rates(session_factory)
    client_id = _create_client(client, auth_headers)
    applicant_id = _seed_applicant(session_factory)
    case_data = _create_case(
        client,
        auth_headers,
        client_id=client_id,
        applicant_id=applicant_id,
        patent_category="UM",
        claim_count=8,
        has_exam_request=False,
    )

    response = client.post(
        "/api/v1/fees/drafts/apply-fee/generate",
        json={"case_id": case_data["id"], "currency": "CNY"},
        headers=auth_headers,
    )

    assert response.status_code == 201, response.text
    draft = response.json()
    assert draft["draft_type"] == "APPLY_FEE"
    # 500 * 0.15 = 75
    assert Decimal(draft["total_gov"]) == Decimal("75.00")

    items_response = client.get(
        f"/api/v1/fees/drafts/{draft['id']}/items",
        headers=auth_headers,
    )
    assert items_response.status_code == 200, items_response.text
    items = {item["fee_code"]: item for item in items_response.json()}
    assert set(items) == {"CN_UM_APPLICATION_FEE"}
    assert Decimal(items["CN_UM_APPLICATION_FEE"]["amount"]) == Decimal("75.00")


def test_generate_apply_fee_draft_supports_des_case_with_excess_claims(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory,
) -> None:
    """外观设计申请费草单：含权利要求附加费（不可费减，全额）。"""
    _seed_apply_fee_rates(session_factory)
    client_id = _create_client(client, auth_headers)
    applicant_id = _seed_applicant(session_factory)
    case_data = _create_case(
        client,
        auth_headers,
        client_id=client_id,
        applicant_id=applicant_id,
        patent_category="DES",
        claim_count=12,
        has_exam_request=False,
    )

    response = client.post(
        "/api/v1/fees/drafts/apply-fee/generate",
        json={"case_id": case_data["id"], "currency": "CNY"},
        headers=auth_headers,
    )

    assert response.status_code == 201, response.text
    draft = response.json()
    # 500 * 0.15 + 150 * 2 (不可费减) = 75 + 300 = 375
    assert Decimal(draft["total_gov"]) == Decimal("375.00")

    items_response = client.get(
        f"/api/v1/fees/drafts/{draft['id']}/items",
        headers=auth_headers,
    )
    assert items_response.status_code == 200, items_response.text
    items = {item["fee_code"]: item for item in items_response.json()}
    assert set(items) == {"CN_DES_APPLICATION_FEE", "CN_EXCESS_CLAIM_FEE"}
    assert Decimal(items["CN_DES_APPLICATION_FEE"]["amount"]) == Decimal("75.00")
    assert Decimal(items["CN_EXCESS_CLAIM_FEE"]["quantity"]) == Decimal("2.0000")
    assert Decimal(items["CN_EXCESS_CLAIM_FEE"]["amount"]) == Decimal("300.00")
