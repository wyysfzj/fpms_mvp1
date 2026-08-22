from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from app.modules.cases.models import Case, CaseActivityEvent


def _case_payload(*, case_no: str, **overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "case_no": case_no,
        "case_type": "NORMAL",
        "patent_category": "INV",
        "flow_dir": "CN_DOMESTIC",
        "title_cn": "生命周期新建案件",
        "fee_reduction": "0",
    }
    payload.update(overrides)
    return payload


def test_case_post_rejects_caller_supplied_legacy_status(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    case_no = f"V8-CREATE-STATUS-{uuid4().hex[:8]}"

    response = client.post(
        "/api/v1/cases",
        headers=auth_headers,
        json=_case_payload(case_no=case_no, status="GRANTED"),
    )

    assert response.status_code == 422, response.text
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"
    with session_factory() as transaction:
        assert transaction.scalar(select(Case).where(Case.case_no == case_no)) is None


def test_case_post_initializes_lifecycle_through_case_opened(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    case_no = f"V8-CASE-OPENED-{uuid4().hex[:8]}"

    response = client.post(
        "/api/v1/cases",
        headers=auth_headers,
        json=_case_payload(case_no=case_no),
    )

    assert response.status_code == 201, response.text
    case_id = response.json()["id"]
    with session_factory() as transaction:
        case = transaction.get(Case, case_id)
        assert case is not None
        assert case.status == "NOT_FILED"
        assert case.business_stage == "NEW_CASE"
        assert case.official_procedure_stage == "NOT_SUBMITTED"
        assert case.legal_status == "NOT_ESTABLISHED"
        assert case.lifecycle_verification_status == "CONFIRMED"
        assert case.lifecycle_revision == 1

        activities = transaction.scalars(
            select(CaseActivityEvent).where(CaseActivityEvent.case_id == case_id)
        ).all()
        assert len(activities) == 1
        activity = activities[0]
        assert activity.sequence == 1
        assert activity.lane == "LIFECYCLE"
        assert activity.activity_type == "CASE_OPENED"
        assert activity.confirmation_status == "CONFIRMED"
        assert activity.idempotency_key == f"case-opened:{case_id}"
