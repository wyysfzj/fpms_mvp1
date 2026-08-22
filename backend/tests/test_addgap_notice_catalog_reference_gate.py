from __future__ import annotations

import json
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from app.modules.cases.models import Case
from app.modules.documents.models import Document
from app.modules.fees.models import FeeDraft, T_GrantFeeTask
from app.modules.tasks.models import Task

DOCUMENT_BASE = "/api/v1/documents"
WIZARD_BASE = "/api/v1/documents/wizard/batch-create"
TEMPLATE_BASE = "/api/v1/doc-templates"


def _create_case(client: TestClient, auth_headers: dict[str, str], label: str) -> dict:
    response = client.post(
        "/api/v1/cases",
        headers=auth_headers,
        json={
            "case_no": f"ADDGAP-REF-GATE-{uuid4().hex[:8].upper()}",
            "case_type": "NORMAL",
            "patent_category": "INV",
            "flow_dir": "CN_DOMESTIC",
            "fee_reduction": "0",
            "title_cn": label,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def _create_template(
    client: TestClient,
    auth_headers: dict[str, str],
    *,
    code_prefix: str,
    input_fields: str | None,
    status_effect: str | None = None,
) -> dict:
    code = f"{code_prefix}_{uuid4().hex[:8].upper()}"
    payload = {
        "code": code,
        "name": f"目录 gate 测试模板 {code}",
        "direction": "IN",
        "enabled": True,
        "status_effect": status_effect,
        "need_reply": False,
    }
    if input_fields is not None:
        payload["input_fields"] = input_fields
    response = client.post(TEMPLATE_BASE, headers=auth_headers, json=payload)
    assert response.status_code == 201, response.text
    return response.json()


def _reference_only_metadata() -> str:
    return json.dumps(
        {
            "archive_status_restore": None,
            "canonical_template_code": None,
            "catalog_kind": "OFFICIAL_NOTICE",
            "catalog_status": "REFERENCE_ONLY",
            "completion_event": None,
            "deadline_source_policy": None,
            "execution_behavior": None,
            "source": "Task21 reference-only fixture",
        }
    )


def _executable_acceptance_metadata() -> str:
    return json.dumps(
        {
            "archive_status_restore": None,
            "canonical_template_code": "ACCEPTANCE_NOTICE",
            "catalog_kind": "OFFICIAL_NOTICE",
            "catalog_status": "EXECUTABLE",
            "completion_event": None,
            "deadline_source_policy": None,
            "execution_behavior": "ACCEPTANCE_NOTICE",
            "source": "Task21 executable fixture",
        }
    )


def _submit(
    client: TestClient,
    auth_headers: dict[str, str],
    *,
    entry_point: str,
    case_id: str,
    template_id: str,
    title: str,
):
    if entry_point == "single":
        return client.post(
            DOCUMENT_BASE,
            headers=auth_headers,
            json={
                "case_id": case_id,
                "doc_template_id": template_id,
                "direction": "IN",
                "doc_date": "2026-07-11",
                "title": title,
                "ref_no": f"REF-{uuid4().hex[:8].upper()}",
            },
        )
    return client.post(
        WIZARD_BASE,
        headers=auth_headers,
        json={
            "defaults": {
                "doc_template_id": template_id,
                "direction": "IN",
                "doc_date": "2026-07-11",
            },
            "rows": [
                {
                    "case_id": case_id,
                    "title": title,
                    "ref_no": f"REF-{uuid4().hex[:8].upper()}",
                }
            ],
        },
    )


@pytest.mark.parametrize("entry_point", ["single", "wizard"])
@pytest.mark.parametrize(
    "reference_metadata",
    [
        _reference_only_metadata(),
        "{malformed",
        None,
        json.dumps(
            {
                "catalog_kind": "OFFICIAL_NOTICE",
                "catalog_status": "PENDING_CONFIRMATION",
            }
        ),
    ],
    ids=["declared", "malformed", "missing", "unknown-status"],
)
def test_reference_only_official_catalog_template_returns_409_without_writes(
    entry_point: str,
    reference_metadata: str | None,
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    case = _create_case(client, auth_headers, f"reference-only {entry_point}")
    template = _create_template(
        client,
        auth_headers,
        code_prefix="OFFICIAL_NOTICE_REFERENCE_GATE",
        input_fields=reference_metadata,
    )

    response = _submit(
        client,
        auth_headers,
        entry_point=entry_point,
        case_id=case["id"],
        template_id=template["id"],
        title=f"reference-only rejected through {entry_point}",
    )

    assert response.status_code == 409, response.text
    error = response.json()["error"]
    assert error["code"] == "DOCUMENT_TEMPLATE_REFERENCE_ONLY"
    assert error["details"] == {
        "template_id": template["id"],
        "template_code": template["code"],
        "catalog_status": "REFERENCE_ONLY",
    }

    with session_factory() as db:
        assert (
            db.execute(
                select(Document).where(Document.doc_template_id == template["id"])
            ).scalar_one_or_none()
            is None
        )
        assert (
            db.execute(select(Task).where(Task.case_id == case["id"])).scalar_one_or_none() is None
        )
        assert (
            db.execute(select(FeeDraft).where(FeeDraft.case_id == case["id"])).scalar_one_or_none()
            is None
        )
        assert (
            db.execute(
                select(T_GrantFeeTask).where(T_GrantFeeTask.case_id == case["id"])
            ).scalar_one_or_none()
            is None
        )
        stored_case = db.execute(select(Case).where(Case.id == case["id"])).scalar_one()
        assert stored_case.status == "NOT_FILED"


@pytest.mark.parametrize("entry_point", ["single", "wizard"])
def test_plain_non_catalog_template_keeps_existing_success_behavior(
    entry_point: str,
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    case = _create_case(client, auth_headers, f"plain {entry_point}")
    template = _create_template(
        client,
        auth_headers,
        code_prefix="PLAIN_REFERENCE_GATE",
        input_fields=json.dumps({"custom_field": "preserved"}),
    )

    response = _submit(
        client,
        auth_headers,
        entry_point=entry_point,
        case_id=case["id"],
        template_id=template["id"],
        title=f"plain template through {entry_point}",
    )

    assert response.status_code == 201, response.text


@pytest.mark.parametrize("entry_point", ["single", "wizard"])
def test_executable_official_catalog_template_keeps_existing_success_behavior(
    entry_point: str,
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    case = _create_case(client, auth_headers, f"executable {entry_point}")
    template = _create_template(
        client,
        auth_headers,
        code_prefix="OFFICIAL_NOTICE_EXECUTABLE_GATE",
        input_fields=_executable_acceptance_metadata(),
        status_effect="ACCEPTED",
    )

    response = _submit(
        client,
        auth_headers,
        entry_point=entry_point,
        case_id=case["id"],
        template_id=template["id"],
        title=f"executable template through {entry_point}",
    )

    assert response.status_code == 201, response.text
