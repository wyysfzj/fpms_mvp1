from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal
from uuid import uuid4

from fastapi.testclient import TestClient

from app.modules.fees.models import FeeDraft, FeeItem, FeeRate
from app.modules.masterdata.applicants.models import Applicant


def _create_client(client: TestClient, auth_headers: dict[str, str]) -> str:
    response = client.post(
        "/api/v1/clients",
        json={
            "client_code": f"OFP-CL-{uuid4().hex[:8]}",
            "name_cn": "官费预览客户",
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
                code=f"OFP-AP-{uuid4().hex[:8]}",
                name_cn=f"官费预览申请人-{uuid4().hex[:8]}",
                applicant_type="ENTITY",
                is_active=True,
            )
        )
        db.commit()
    return applicant_id


def _seed_apply_fee_rates(session_factory) -> None:
    rows = [
        (
            "CN_INV_APPLICATION_FEE",
            "发明申请费",
            Decimal("900.00"),
            "FIXED",
            True,
            "申请费",
            "发明专利",
            "申请费（不包括公布印刷费、申请附加费）",
        ),
        (
            "CN_EXCESS_CLAIM_FEE",
            "权利要求附加费",
            Decimal("150.00"),
            "PER_CLAIM",
            False,
            "申请附加费",
            "权利要求第11项起每项",
            "不可费减",
        ),
        (
            "CN_PUBLICATION_PRINT_FEE",
            "公布印刷费",
            Decimal("50.00"),
            "FIXED",
            False,
            "公布印刷费",
            "发明专利",
            "不可费减",
        ),
        (
            "CN_SUBSTANTIVE_EXAM_FEE",
            "发明实审费",
            Decimal("2500.00"),
            "FIXED",
            True,
            "发明实质审查费",
            "发明专利",
            "发明专利申请实质审查费",
        ),
    ]
    with session_factory() as db:
        for (
            fee_code,
            fee_name,
            amount,
            calc_mode,
            allow_reduction,
            fee_category,
            fee_subtype,
            reduction_scope,
        ) in rows:
            db.add(
                FeeRate(
                    id=str(uuid4()),
                    fee_code=fee_code,
                    fee_name=fee_name,
                    fee_type="GOV",
                    currency="CNY",
                    default_amount=amount,
                    enabled=True,
                    rate_group="DOMESTIC",
                    fee_domain="PATENT",
                    fee_section="专利收费-国内部分",
                    fee_category=fee_category,
                    fee_subtype=fee_subtype,
                    reduction_scope=reduction_scope,
                    calc_mode=calc_mode,
                    allow_reduction=allow_reduction,
                    source_doc="专利收费场景-20260626.docx",
                    source_status="CONFIRMED",
                )
            )
        db.commit()


def _seed_apply_fee_rates_with_effective_windows(session_factory) -> None:
    today = date.today()
    rows = [
        (
            "CN_INV_APPLICATION_FEE",
            "过期发明申请费",
            Decimal("800.00"),
            "FIXED",
            True,
            "申请费",
            "发明专利",
            "申请费（不包括公布印刷费、申请附加费）",
            today - timedelta(days=730),
            today - timedelta(days=1),
        ),
        (
            "CN_INV_APPLICATION_FEE",
            "发明申请费",
            Decimal("900.00"),
            "FIXED",
            True,
            "申请费",
            "发明专利",
            "申请费（不包括公布印刷费、申请附加费）",
            today - timedelta(days=1),
            today + timedelta(days=1),
        ),
        (
            "CN_INV_APPLICATION_FEE",
            "未来发明申请费",
            Decimal("1900.00"),
            "FIXED",
            True,
            "申请费",
            "发明专利",
            "申请费（不包括公布印刷费、申请附加费）",
            today + timedelta(days=1),
            None,
        ),
        (
            "CN_EXCESS_CLAIM_FEE",
            "权利要求附加费",
            Decimal("150.00"),
            "PER_CLAIM",
            False,
            "申请附加费",
            "权利要求第11项起每项",
            "不可费减",
            today - timedelta(days=1),
            None,
        ),
        (
            "CN_PUBLICATION_PRINT_FEE",
            "公布印刷费",
            Decimal("50.00"),
            "FIXED",
            False,
            "公布印刷费",
            "发明专利",
            "不可费减",
            today - timedelta(days=1),
            None,
        ),
        (
            "CN_SUBSTANTIVE_EXAM_FEE",
            "发明实审费",
            Decimal("2500.00"),
            "FIXED",
            True,
            "发明实质审查费",
            "发明专利",
            "发明专利申请实质审查费",
            today - timedelta(days=1),
            None,
        ),
    ]
    with session_factory() as db:
        for (
            fee_code,
            fee_name,
            amount,
            calc_mode,
            allow_reduction,
            fee_category,
            fee_subtype,
            reduction_scope,
            effective_from,
            effective_to,
        ) in rows:
            db.add(
                FeeRate(
                    id=str(uuid4()),
                    fee_code=fee_code,
                    fee_name=fee_name,
                    fee_type="GOV",
                    currency="CNY",
                    default_amount=amount,
                    enabled=True,
                    rate_group="DOMESTIC",
                    fee_domain="PATENT",
                    fee_section="专利收费-国内部分",
                    fee_category=fee_category,
                    fee_subtype=fee_subtype,
                    reduction_scope=reduction_scope,
                    calc_mode=calc_mode,
                    allow_reduction=allow_reduction,
                    effective_from=effective_from,
                    effective_to=effective_to,
                    source_doc="专利收费场景-20260626.docx",
                    source_status="CONFIRMED",
                )
            )
        db.commit()


def _seed_reexam_fee_rates(session_factory) -> None:
    rows = [
        ("CN_REEXAM_FEE_INV", "发明专利复审费", Decimal("1000.00"), "发明专利"),
        ("CN_REEXAM_FEE_UM", "实用新型专利复审费", Decimal("300.00"), "实用新型专利"),
        ("CN_REEXAM_FEE_DES", "外观设计专利复审费", Decimal("300.00"), "外观设计专利"),
    ]
    with session_factory() as db:
        for fee_code, fee_name, amount, fee_subtype in rows:
            db.add(
                FeeRate(
                    id=str(uuid4()),
                    fee_code=fee_code,
                    fee_name=fee_name,
                    fee_type="GOV",
                    currency="CNY",
                    default_amount=amount,
                    enabled=True,
                    rate_group="DOMESTIC",
                    fee_domain="PATENT",
                    fee_section="专利收费-国内部分",
                    fee_category="复审费",
                    fee_subtype=fee_subtype,
                    reduction_scope="复审费",
                    calc_mode="FIXED",
                    allow_reduction=True,
                    source_doc="专利收费场景-20260626.docx",
                    source_status="CONFIRMED",
                )
            )
        db.commit()


def _create_case(
    client: TestClient,
    auth_headers: dict[str, str],
    *,
    client_id: str,
    applicant_id: str,
    patent_category: str = "INV",
) -> dict:
    response = client.post(
        "/api/v1/cases",
        json={
            "case_no": f"OFP-{uuid4().hex[:8]}",
            "case_type": "NORMAL",
            "patent_category": patent_category,
            "flow_dir": "CN_DOMESTIC",
            "client_id": client_id,
            "title_cn": "官费预览测试案",
            "status": "NOT_FILED",
            "recv_date": "2026-03-01",
            "claim_count": 12,
            "has_exam_request": True,
            "fee_reduction": "0.85",
            "applicants": [
                {
                    "seq": 1,
                    "is_first": True,
                    "applicant_id": applicant_id,
                    "name_cn": "官费预览申请人",
                }
            ],
        },
        headers=auth_headers,
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_official_fee_preview_returns_candidates_without_creating_draft(
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
        "/api/v1/fees/official-fee-preview",
        json={
            "case_id": case_data["id"],
            "currency": "CNY",
            "trigger_event": "FILING_ACCEPTED",
            "source_document_id": "DOC-OFP-1",
        },
        headers=auth_headers,
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["case_id"] == case_data["id"]
    assert body["trigger_event"] == "FILING_ACCEPTED"
    assert body["source_document_id"] == "DOC-OFP-1"
    assert body["idempotency_key"] == f"{case_data['id']}:FILING_ACCEPTED:DOC-OFP-1"
    assert body["preview_only"] is True
    assert body["draft_type"] == "APPLY_FEE"
    assert Decimal(body["total_gov"]) == Decimal("860.00")

    candidates = {item["fee_code"]: item for item in body["candidates"]}
    assert set(candidates) == {
        "CN_INV_APPLICATION_FEE",
        "CN_EXCESS_CLAIM_FEE",
        "CN_PUBLICATION_PRINT_FEE",
        "CN_SUBSTANTIVE_EXAM_FEE",
    }
    assert {item["fee_type"] for item in candidates.values()} == {"GOV"}
    assert Decimal(candidates["CN_INV_APPLICATION_FEE"]["amount"]) == Decimal("135.00")
    assert candidates["CN_INV_APPLICATION_FEE"]["fee_category"] == "申请费"
    assert candidates["CN_INV_APPLICATION_FEE"]["fee_subtype"] == "发明专利"
    assert candidates["CN_INV_APPLICATION_FEE"]["trigger_rule"] == "提交申请/收到受理通知"
    assert candidates["CN_INV_APPLICATION_FEE"]["deadline_rule"] == "申请日/受理通知起 2 个月"
    assert (
        candidates["CN_INV_APPLICATION_FEE"]["reduction_scope"]
        == "申请费（不包括公布印刷费、申请附加费）"
    )
    assert Decimal(candidates["CN_EXCESS_CLAIM_FEE"]["quantity"]) == Decimal("2.0000")
    assert Decimal(candidates["CN_EXCESS_CLAIM_FEE"]["amount"]) == Decimal("300.00")
    assert candidates["CN_EXCESS_CLAIM_FEE"]["fee_category"] == "申请附加费"
    assert candidates["CN_EXCESS_CLAIM_FEE"]["fee_subtype"] == "权利要求第11项起每项"
    assert Decimal(candidates["CN_PUBLICATION_PRINT_FEE"]["amount"]) == Decimal("50.00")
    assert Decimal(candidates["CN_SUBSTANTIVE_EXAM_FEE"]["amount"]) == Decimal("375.00")

    with session_factory() as db:
        assert db.query(FeeDraft).count() == 0
        assert db.query(FeeItem).count() == 0


def test_official_fee_preview_selects_current_effective_rate(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory,
) -> None:
    _seed_apply_fee_rates_with_effective_windows(session_factory)
    client_id = _create_client(client, auth_headers)
    applicant_id = _seed_applicant(session_factory)
    case_data = _create_case(
        client,
        auth_headers,
        client_id=client_id,
        applicant_id=applicant_id,
    )

    response = client.post(
        "/api/v1/fees/official-fee-preview",
        json={
            "case_id": case_data["id"],
            "currency": "CNY",
            "trigger_event": "FILING_ACCEPTED",
        },
        headers=auth_headers,
    )

    assert response.status_code == 200, response.text
    body = response.json()
    candidates = {item["fee_code"]: item for item in body["candidates"]}
    assert Decimal(body["total_gov"]) == Decimal("860.00")
    assert Decimal(candidates["CN_INV_APPLICATION_FEE"]["unit_price"]) == Decimal("900.00")
    assert Decimal(candidates["CN_INV_APPLICATION_FEE"]["amount"]) == Decimal("135.00")


def test_official_fee_preview_returns_reexam_candidate_without_creating_draft(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory,
) -> None:
    _seed_reexam_fee_rates(session_factory)
    client_id = _create_client(client, auth_headers)
    applicant_id = _seed_applicant(session_factory)
    case_data = _create_case(
        client,
        auth_headers,
        client_id=client_id,
        applicant_id=applicant_id,
    )

    response = client.post(
        "/api/v1/fees/official-fee-preview",
        json={
            "case_id": case_data["id"],
            "currency": "CNY",
            "trigger_event": "REEXAM_REQUESTED",
            "source_document_id": "DOC-REJECTION-1",
        },
        headers=auth_headers,
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["case_id"] == case_data["id"]
    assert body["trigger_event"] == "REEXAM_REQUESTED"
    assert body["source_document_id"] == "DOC-REJECTION-1"
    assert body["idempotency_key"] == f"{case_data['id']}:REEXAM_REQUESTED:DOC-REJECTION-1"
    assert body["preview_only"] is True
    assert body["draft_type"] == "REEXAM_FEE"
    assert Decimal(body["total_gov"]) == Decimal("150.00")

    assert len(body["candidates"]) == 1
    candidate = body["candidates"][0]
    assert candidate["fee_code"] == "CN_REEXAM_FEE_INV"
    assert candidate["fee_name"] == "发明专利复审费"
    assert candidate["fee_type"] == "GOV"
    assert candidate["fee_category"] == "复审费"
    assert candidate["fee_subtype"] == "发明专利"
    assert candidate["trigger_rule"] == "收到驳回决定且决定复审"
    assert candidate["deadline_rule"] == "驳回决定起 3 个月"
    assert candidate["reduction_scope"] == "复审费"
    assert candidate["source_document_id"] == "DOC-REJECTION-1"
    assert Decimal(candidate["amount_before_reduction"]) == Decimal("1000.00")
    assert Decimal(candidate["reduction_ratio"]) == Decimal("0.85")
    assert Decimal(candidate["payable_ratio"]) == Decimal("0.15")
    assert Decimal(candidate["amount"]) == Decimal("150.00")

    with session_factory() as db:
        assert db.query(FeeDraft).count() == 0
        assert db.query(FeeItem).count() == 0


def test_official_fee_preview_rejects_unsupported_trigger(
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
        "/api/v1/fees/official-fee-preview",
        json={
            "case_id": case_data["id"],
            "trigger_event": "RESTORE_RIGHT_REQUESTED",
        },
        headers=auth_headers,
    )

    assert response.status_code == 400, response.text
    assert response.json()["error"]["code"] == "OFFICIAL_FEE_PREVIEW_TRIGGER_UNSUPPORTED"
