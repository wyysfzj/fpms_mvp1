from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal
from io import BytesIO
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from app.modules.cases.models import Case
from app.modules.documents.models import Document
from app.modules.fees.models import FeeRate, T_GrantFeeTask

DOC_BASE = "/api/v1/documents"
DOC_TEMPLATE_BASE = "/api/v1/doc-templates"
CASE_BASE = "/api/v1/cases"
GRANT_FEE_TASK_BASE = "/api/v1/grant-fee-tasks/list"


def _uid(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:8].upper()}"


def _create_case(client: TestClient, auth_headers: dict[str, str]) -> dict:
    resp = client.post(
        CASE_BASE,
        json={
            "case_no": _uid("GFNT-CASE"),
            "case_type": "NORMAL",
            "patent_category": "INV",
            "flow_dir": "CN_DOMESTIC",
            "title_cn": "Grant fee notice task case",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def _get_template(client: TestClient, auth_headers: dict[str, str], code: str) -> dict:
    resp = client.get(
        DOC_TEMPLATE_BASE,
        params={"q": code, "page_size": 100},
        headers=auth_headers,
    )
    assert resp.status_code == 200, resp.text
    matches = [item for item in resp.json()["items"] if item["code"] == code]
    assert len(matches) == 1
    return matches[0]


def _create_grant_notice(
    client: TestClient,
    auth_headers: dict[str, str],
    *,
    case_id: str,
    template_id: str,
    title: str,
) -> dict:
    resp = client.post(
        DOC_BASE,
        json={
            "case_id": case_id,
            "doc_template_id": template_id,
            "direction": "IN",
            "doc_date": "2026-04-10",
            "title": title,
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def _set_case_ready_for_granted(session_factory: sessionmaker, *, case_id: str) -> None:
    with session_factory() as db:
        case = db.execute(select(Case).where(Case.id == case_id)).scalar_one()
        case.app_no = "CN202610000009"
        case.filing_date = date(2026, 3, 20)
        case.issue_date = date(2026, 7, 20)
        case.pub_no = "CN202610000009A"
        case.pub_date = date(2026, 4, 1)
        case.grant_no = "CN202610000009B"
        case.grant_date = date(2026, 8, 1)
        case.first_annuity_year = 3
        case.valid_until = date(2046, 3, 20)
        db.commit()


def _set_case_missing_publication_fields_for_granted(
    session_factory: sessionmaker, *, case_id: str
) -> None:
    with session_factory() as db:
        case = db.execute(select(Case).where(Case.id == case_id)).scalar_one()
        case.app_no = "CN202610000010"
        case.filing_date = date(2026, 3, 20)
        case.issue_date = date(2026, 7, 20)
        case.pub_no = None
        case.pub_date = None
        case.grant_no = "CN202610000010B"
        case.grant_date = date(2026, 8, 1)
        case.first_annuity_year = 3
        case.valid_until = date(2046, 3, 20)
        db.commit()


def _seed_inv_annuity_gov_rate(session_factory: sessionmaker) -> None:
    with session_factory() as db:
        db.add(
            FeeRate(
                id=str(uuid4()),
                fee_code=_uid("GFNT-INV-ANNUITY"),
                fee_name="发明授权当年年费",
                fee_type="GOV",
                currency="CNY",
                default_amount=Decimal("0.00"),
                enabled=True,
                rate_group="ANNUITY",
                patent_category="INV",
                calc_mode="TIER",
                calc_params=(
                    '{"tiers":['
                    '{"from":1,"to":3,"amount":"900.00"},'
                    '{"from":4,"to":6,"amount":"1200.00"}'
                    "]}"
                ),
            )
        )
        db.add(
            FeeRate(
                id=str(uuid4()),
                fee_code=_uid("GFNT-SERVICE"),
                fee_name="旧授权服务费",
                fee_type="SERVICE",
                currency="CNY",
                default_amount=Decimal("50.00"),
                enabled=True,
                rate_group="GRANT",
            )
        )
        db.commit()


def _seed_inv_annuity_gov_rate_with_effective_windows(session_factory: sessionmaker) -> None:
    today = date.today()
    rows = [
        (
            "过期发明授权当年年费",
            today - timedelta(days=730),
            today - timedelta(days=1),
            '{"tiers":[{"from":1,"to":3,"amount":"700.00"},{"from":4,"to":6,"amount":"1000.00"}]}',
        ),
        (
            "发明授权当年年费",
            today - timedelta(days=1),
            today + timedelta(days=1),
            '{"tiers":[{"from":1,"to":3,"amount":"900.00"},{"from":4,"to":6,"amount":"1200.00"}]}',
        ),
        (
            "未来发明授权当年年费",
            today + timedelta(days=1),
            None,
            '{"tiers":[{"from":1,"to":3,"amount":"1900.00"},{"from":4,"to":6,"amount":"2200.00"}]}',
        ),
    ]
    with session_factory() as db:
        for fee_name, effective_from, effective_to, calc_params in rows:
            db.add(
                FeeRate(
                    id=str(uuid4()),
                    fee_code=_uid("GFNT-INV-ANNUITY"),
                    fee_name=fee_name,
                    fee_type="GOV",
                    currency="CNY",
                    default_amount=Decimal("0.00"),
                    enabled=True,
                    rate_group="ANNUITY",
                    patent_category="INV",
                    calc_mode="TIER",
                    calc_params=calc_params,
                    effective_from=effective_from,
                    effective_to=effective_to,
                )
            )
        db.commit()


def _seed_imported_grant_notice_document(
    session_factory: sessionmaker,
    *,
    case_id: str,
    template_id: str,
) -> str:
    document_id = str(uuid4())
    with session_factory() as db:
        db.add(
            Document(
                id=document_id,
                case_id=case_id,
                doc_template_id=template_id,
                doc_type="OFFICIAL_IN",
                direction="IN",
                doc_date=date(2026, 4, 10),
                title="授权通知书",
            )
        )
        db.commit()
    return document_id


def test_grant_notice_document_creation_creates_one_reusable_grant_fee_task(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    case = _create_case(client, auth_headers)
    template = _get_template(client, auth_headers, "GRANT_NOTICE")

    _create_grant_notice(
        client,
        auth_headers,
        case_id=case["id"],
        template_id=template["id"],
        title="授权通知书",
    )
    _create_grant_notice(
        client,
        auth_headers,
        case_id=case["id"],
        template_id=template["id"],
        title="授权通知书-重复登记",
    )

    resp = client.get(
        GRANT_FEE_TASK_BASE,
        params={"case_id": case["id"], "page_size": 100},
        headers=auth_headers,
    )
    assert resp.status_code == 200, resp.text
    payload = resp.json()
    assert payload["total"] == 1
    assert len(payload["items"]) == 1
    item = payload["items"][0]
    assert item["case_id"] == case["id"]
    assert item["status"] == "OPEN"
    assert item["due_date"] == "2026-06-09"
    assert item["currency"] == "CNY"
    assert item["trigger_rule"] == "收到办理登记手续通知书/授权通知书"
    assert (
        item["deadline_rule"]
        == "以办理登记手续通知书/授权通知书载明期限为准；当前按授权费任务到期日展示"
    )
    assert (
        item["fee_basis"] == "授权阶段官费按授权费任务金额展示；如无授权费率则回退授权当年年费规则"
    )
    assert (
        item["fee_node_explanation"]
        == "授权费用节点：客户确认缴费后生成官费草单，缴费登记后进入授权后年费监视。"
    )

    with session_factory() as db:
        tasks = (
            db.execute(select(T_GrantFeeTask).where(T_GrantFeeTask.case_id == case["id"]))
            .scalars()
            .all()
        )
        assert len(tasks) == 1
        assert tasks[0].due_date == date(2026, 6, 9)

    case_resp = client.get(f"{CASE_BASE}/{case['id']}", headers=auth_headers)
    assert case_resp.status_code == 200, case_resp.text
    assert case_resp.json()["status"] == "GRANT_PENDING"


def test_grant_notice_document_creation_prefills_official_gov_fee_from_annuity_rate(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    case = _create_case(client, auth_headers)
    _set_case_ready_for_granted(session_factory, case_id=case["id"])
    _seed_inv_annuity_gov_rate(session_factory)
    template = _get_template(client, auth_headers, "GRANT_NOTICE")

    _create_grant_notice(
        client,
        auth_headers,
        case_id=case["id"],
        template_id=template["id"],
        title="授权通知书-官费预填",
    )

    with session_factory() as db:
        task = db.execute(
            select(T_GrantFeeTask).where(T_GrantFeeTask.case_id == case["id"])
        ).scalar_one()
        assert task.gov_fee_amt == Decimal("900.00")
        assert task.service_fee_amt == Decimal("0.00")


def test_grant_notice_document_creation_prefills_current_effective_gov_fee(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    case = _create_case(client, auth_headers)
    _set_case_ready_for_granted(session_factory, case_id=case["id"])
    _seed_inv_annuity_gov_rate_with_effective_windows(session_factory)
    template = _get_template(client, auth_headers, "GRANT_NOTICE")

    _create_grant_notice(
        client,
        auth_headers,
        case_id=case["id"],
        template_id=template["id"],
        title="授权通知书-当前费率预填",
    )

    with session_factory() as db:
        task = db.execute(
            select(T_GrantFeeTask).where(T_GrantFeeTask.case_id == case["id"])
        ).scalar_one()
        assert task.gov_fee_amt == Decimal("900.00")
        assert task.service_fee_amt == Decimal("0.00")


def test_grant_notice_attachment_upload_advances_ready_case_to_granted(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    case = _create_case(client, auth_headers)
    _set_case_ready_for_granted(session_factory, case_id=case["id"])
    template = _get_template(client, auth_headers, "GRANT_NOTICE")

    document = _create_grant_notice(
        client,
        auth_headers,
        case_id=case["id"],
        template_id=template["id"],
        title="授权通知书",
    )

    pending_resp = client.get(f"{CASE_BASE}/{case['id']}", headers=auth_headers)
    assert pending_resp.status_code == 200, pending_resp.text
    assert pending_resp.json()["status"] == "GRANT_PENDING"

    upload_resp = client.post(
        f"{DOC_BASE}/{document['id']}/attachments",
        headers=auth_headers,
        files={
            "file": (
                "授权通知书.pdf",
                BytesIO(b"%PDF-1.4 demo grant notice attachment"),
                "application/pdf",
            )
        },
    )
    assert upload_resp.status_code == 201, upload_resp.text

    case_resp = client.get(f"{CASE_BASE}/{case['id']}", headers=auth_headers)
    assert case_resp.status_code == 200, case_resp.text
    assert case_resp.json()["status"] == "GRANTED"


def test_grant_notice_attachment_upload_does_not_advance_without_publication_fields(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    case = _create_case(client, auth_headers)
    _set_case_missing_publication_fields_for_granted(session_factory, case_id=case["id"])
    template = _get_template(client, auth_headers, "GRANT_NOTICE")

    document = _create_grant_notice(
        client,
        auth_headers,
        case_id=case["id"],
        template_id=template["id"],
        title="授权通知书",
    )

    pending_resp = client.get(f"{CASE_BASE}/{case['id']}", headers=auth_headers)
    assert pending_resp.status_code == 200, pending_resp.text
    assert pending_resp.json()["status"] == "GRANT_PENDING"

    upload_resp = client.post(
        f"{DOC_BASE}/{document['id']}/attachments",
        headers=auth_headers,
        files={
            "file": (
                "授权通知书.pdf",
                BytesIO(b"%PDF-1.4 demo grant notice attachment"),
                "application/pdf",
            )
        },
    )
    assert upload_resp.status_code == 201, upload_resp.text

    case_resp = client.get(f"{CASE_BASE}/{case['id']}", headers=auth_headers)
    assert case_resp.status_code == 200, case_resp.text
    assert case_resp.json()["status"] == "GRANT_PENDING"


def test_imported_grant_notice_attachment_upload_advances_case_and_creates_fee_task(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    case = _create_case(client, auth_headers)
    _set_case_ready_for_granted(session_factory, case_id=case["id"])
    with session_factory() as db:
        target_case = db.execute(select(Case).where(Case.id == case["id"])).scalar_one()
        target_case.status = "SUB_EXAM"
        db.commit()
    template = _get_template(client, auth_headers, "GRANT_NOTICE")
    document_id = _seed_imported_grant_notice_document(
        session_factory,
        case_id=case["id"],
        template_id=template["id"],
    )

    upload_resp = client.post(
        f"{DOC_BASE}/{document_id}/attachments",
        headers=auth_headers,
        files={
            "file": (
                "授权通知书.pdf",
                BytesIO(b"%PDF-1.4 imported grant notice attachment"),
                "application/pdf",
            )
        },
    )

    assert upload_resp.status_code == 201, upload_resp.text
    case_resp = client.get(f"{CASE_BASE}/{case['id']}", headers=auth_headers)
    assert case_resp.status_code == 200, case_resp.text
    assert case_resp.json()["status"] == "GRANTED"

    task_resp = client.get(
        GRANT_FEE_TASK_BASE,
        params={"case_id": case["id"], "page_size": 100},
        headers=auth_headers,
    )
    assert task_resp.status_code == 200, task_resp.text
    payload = task_resp.json()
    assert payload["total"] == 1
    assert payload["items"][0]["due_date"] == "2026-06-09"
