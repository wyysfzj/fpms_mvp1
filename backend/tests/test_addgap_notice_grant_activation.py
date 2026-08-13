from __future__ import annotations

import json
from datetime import date
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

import scripts.seed_dev as seed_dev
from app.modules.cases.models import Case
from app.modules.documents import official_notice_catalog as notice_catalog
from app.modules.documents.models import DocTemplate, Document
from app.modules.fees.models import FeeDraft, T_GrantFeeTask

PRIOR_EXECUTABLE_CODES = {
    "OFFICIAL_NOTICE_001",
    "OFFICIAL_NOTICE_003",
    "OFFICIAL_NOTICE_005",
    "OFFICIAL_NOTICE_021",
    "OFFICIAL_NOTICE_024",
    "OFFICIAL_NOTICE_029",
}
GRANT_CODE = "OFFICIAL_NOTICE_009"
EXPECTED_EXECUTABLE_CODES = PRIOR_EXECUTABLE_CODES | {GRANT_CODE}


def _seed_grant_catalog(db) -> int:
    seed = getattr(notice_catalog, "seed_grant_official_notice_catalog", None)
    assert callable(seed), "grant-activated official-notice catalog seeder is missing"
    return seed(db)


def _catalog_rows(db) -> list[DocTemplate]:
    return list(
        db.execute(
            select(DocTemplate)
            .where(DocTemplate.code.like("OFFICIAL_NOTICE_%"))
            .order_by(DocTemplate.code.asc())
        )
        .scalars()
        .all()
    )


def _assert_grant_target_state(rows: list[DocTemplate]) -> None:
    assert len(rows) == len(notice_catalog.OFFICIAL_NOTICE_CATALOG) == 60
    executable_codes = {
        row.code
        for row in rows
        if json.loads(row.input_fields or "{}")["catalog_status"] == "EXECUTABLE"
    }
    assert executable_codes == EXPECTED_EXECUTABLE_CODES

    grant = next(row for row in rows if row.code == GRANT_CODE)
    metadata = json.loads(grant.input_fields or "{}")
    assert grant.name == "授权通知书-电子"
    assert grant.status_effect == "GRANT_PENDING"
    assert grant.deadline_template_code is None
    assert grant.fee_draft_type == "GRANT_FEE"
    assert grant.need_reply is False
    assert metadata["execution_behavior"] == "GRANT_NOTICE"
    assert metadata["canonical_template_code"] == "GRANT_NOTICE"
    assert metadata["deadline_source_policy"] == "EXPLICIT_OFFICIAL_DUE_REQUIRED"
    assert metadata["completion_event"] is None
    assert metadata["archive_status_restore"] is None

    for row in rows:
        if row.code in EXPECTED_EXECUTABLE_CODES:
            continue
        metadata = json.loads(row.input_fields or "{}")
        assert metadata["catalog_status"] == "REFERENCE_ONLY"
        assert metadata["execution_behavior"] is None
        assert metadata["canonical_template_code"] is None
        assert metadata["deadline_source_policy"] is None
        assert row.status_effect is None
        assert row.deadline_template_code is None
        assert row.fee_draft_type is None
        assert row.need_reply is False


def _create_case(client: TestClient, auth_headers: dict[str, str], label: str) -> dict:
    response = client.post(
        "/api/v1/cases",
        headers=auth_headers,
        json={
            "case_no": f"ADDGAP-GRANT-ACT-{uuid4().hex[:8].upper()}",
            "case_type": "NORMAL",
            "patent_category": "INV",
            "flow_dir": "CN_DOMESTIC",
            "fee_reduction": "0",
            "title_cn": label,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def _grant_template_id(session_factory: sessionmaker) -> str:
    with session_factory() as db:
        _seed_grant_catalog(db)
        db.commit()
        return db.execute(select(DocTemplate.id).where(DocTemplate.code == GRANT_CODE)).scalar_one()


def _grant_document_payload(case_id: str, template_id: str) -> dict:
    return {
        "case_id": case_id,
        "doc_template_id": template_id,
        "direction": "IN",
        "doc_date": "2026-07-11",
        "title": "授权通知书-电子",
    }


def test_grant_target_state_adds_only_row_nine_and_is_idempotent(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as db:
        assert _seed_grant_catalog(db) == 60
        db.commit()
        rows = _catalog_rows(db)
        _assert_grant_target_state(rows)
        first_snapshot = [(row.id, row.code, row.input_fields) for row in rows]

        assert _seed_grant_catalog(db) == 0
        db.commit()
        second_rows = _catalog_rows(db)
        assert [(row.id, row.code, row.input_fields) for row in second_rows] == first_snapshot


def test_seed_dev_uses_grant_target_state_idempotently(
    monkeypatch,
    session_factory: sessionmaker,
) -> None:
    monkeypatch.setattr(seed_dev, "seed_official_letter_out_catalog", lambda _db: 0)
    monkeypatch.setattr(seed_dev, "seed_grant_fee_notice_template_source", lambda _db: False)
    monkeypatch.setattr(seed_dev, "seed_format_letter_mappings", lambda _db: 0)

    with session_factory() as db:
        seed_dev.seed_doc_templates(db)
        first_rows = _catalog_rows(db)
        _assert_grant_target_state(first_rows)
        first_snapshot = [(row.id, row.code, row.input_fields) for row in first_rows]

        seed_dev.seed_doc_templates(db)
        second_rows = _catalog_rows(db)
        _assert_grant_target_state(second_rows)
        assert [(row.id, row.code, row.input_fields) for row in second_rows] == first_snapshot


def test_activated_grant_without_confirmed_due_returns_409_without_writes(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    template_id = _grant_template_id(session_factory)
    case = _create_case(client, auth_headers, "授权目录缺失期限测试")

    response = client.post(
        "/api/v1/documents",
        headers=auth_headers,
        json=_grant_document_payload(case["id"], template_id),
    )

    assert response.status_code == 409, response.text
    assert response.json()["error"]["code"] == "GRANT_OFFICIAL_DUE_DATE_REQUIRED"
    with session_factory() as db:
        assert (
            db.execute(select(Document).where(Document.case_id == case["id"])).scalar_one_or_none()
            is None
        )
        assert (
            db.execute(
                select(T_GrantFeeTask).where(T_GrantFeeTask.case_id == case["id"])
            ).scalar_one_or_none()
            is None
        )
        assert (
            db.execute(select(FeeDraft).where(FeeDraft.case_id == case["id"])).scalar_one_or_none()
            is None
        )
        assert (
            db.execute(select(Case).where(Case.id == case["id"])).scalar_one().status == "NOT_FILED"
        )


def test_activated_grant_with_confirmed_due_creates_source_task_without_generic_draft(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    template_id = _grant_template_id(session_factory)
    case = _create_case(client, auth_headers, "授权目录明确期限测试")
    payload = {
        **_grant_document_payload(case["id"], template_id),
        "official_due_date": "2026-08-28",
        "official_due_date_source": "MANUAL_OFFICIAL_NOTICE",
        "official_due_date_status": "CONFIRMED",
    }

    response = client.post("/api/v1/documents", headers=auth_headers, json=payload)

    assert response.status_code == 201, response.text
    document_id = response.json()["id"]
    assert response.headers.get("X-Auto-Fee-Draft-Created") is None
    with session_factory() as db:
        task = db.execute(
            select(T_GrantFeeTask).where(T_GrantFeeTask.case_id == case["id"])
        ).scalar_one()
        assert task.source_document_id == document_id
        assert task.due_date == date(2026, 8, 28)
        assert task.deadline_source == "MANUAL_OFFICIAL_NOTICE"
        assert task.deadline_confirmed_at is not None
        assert task.draft_generated is False
        assert (
            db.execute(select(FeeDraft).where(FeeDraft.case_id == case["id"])).scalar_one_or_none()
            is None
        )
        assert (
            db.execute(select(Case).where(Case.id == case["id"])).scalar_one().status
            == "GRANT_PENDING"
        )
