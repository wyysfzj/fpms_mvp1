from __future__ import annotations

from datetime import date
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from app.modules.documents.models import Document
from app.modules.tasks.models import Task

WIZARD_URL = "/api/v1/documents/wizard/batch-create"
TASK_PREVIEW_URL = "/api/v1/documents/wizard/task-preview"


def _create_case(client: TestClient, auth_headers: dict[str, str]) -> dict:
    response = client.post(
        "/api/v1/cases",
        headers=auth_headers,
        json={
            "case_no": f"ADDGAP-WIZ-DUE-{uuid4().hex[:8].upper()}",
            "case_type": "NORMAL",
            "patent_category": "INV",
            "flow_dir": "CN_DOMESTIC",
            "title_cn": "向导逐行期限测试案件",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def _get_oa_template(client: TestClient, auth_headers: dict[str, str]) -> dict:
    response = client.get(
        "/api/v1/doc-templates",
        headers=auth_headers,
        params={"q": "OA_IN", "page_size": 100},
    )
    assert response.status_code == 200, response.text
    matches = [item for item in response.json()["items"] if item["code"] == "OA_IN"]
    assert len(matches) == 1
    return matches[0]


def test_wizard_persists_default_and_per_row_confirmed_deadline_lineage(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    first_case = _create_case(client, auth_headers)
    second_case = _create_case(client, auth_headers)
    template = _get_oa_template(client, auth_headers)

    response = client.post(
        WIZARD_URL,
        headers=auth_headers,
        json={
            "defaults": {
                "doc_template_id": template["id"],
                "direction": "IN",
                "doc_date": "2026-07-11",
                "official_due_date": "2026-10-11",
                "official_due_date_source": "MANUAL_OFFICIAL_NOTICE",
                "official_due_date_status": "CONFIRMED",
            },
            "rows": [
                {"case_id": first_case["id"], "title": "第一件 OA"},
                {
                    "case_id": second_case["id"],
                    "title": "第二件 OA",
                    "official_due_date": "2026-11-20",
                    "official_due_date_source": "IMPORTED_OFFICIAL_NOTICE",
                    "official_due_date_status": "CONFIRMED",
                },
            ],
        },
    )

    assert response.status_code == 201, response.text
    documents = [item["document"] for item in response.json()["items"]]
    assert [document["official_due_date"] for document in documents] == [
        "2026-10-11",
        "2026-11-20",
    ]
    assert [document["official_due_date_source"] for document in documents] == [
        "MANUAL_OFFICIAL_NOTICE",
        "IMPORTED_OFFICIAL_NOTICE",
    ]
    assert all(document["official_due_date_status"] == "CONFIRMED" for document in documents)

    with session_factory() as db:
        stored_documents = (
            db.execute(select(Document).where(Document.id.in_([item["id"] for item in documents])))
            .scalars()
            .all()
        )
        assert len(stored_documents) == 2
        tasks = (
            db.execute(
                select(Task)
                .where(Task.document_id.in_([item["id"] for item in documents]))
                .order_by(Task.due_date)
            )
            .scalars()
            .all()
        )
        assert [task.due_date for task in tasks] == [date(2026, 10, 11), date(2026, 11, 20)]


def test_wizard_task_preview_uses_structured_row_deadline(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    case = _create_case(client, auth_headers)
    template = _get_oa_template(client, auth_headers)

    response = client.post(
        TASK_PREVIEW_URL,
        headers=auth_headers,
        json={
            "defaults": {
                "doc_template_id": template["id"],
                "direction": "IN",
                "doc_date": "2026-07-11",
            },
            "rows": [
                {
                    "case_id": case["id"],
                    "title": "OA 任务预览",
                    "official_due_date": "2026-12-05",
                    "official_due_date_source": "MANUAL_OFFICIAL_NOTICE",
                    "official_due_date_status": "CONFIRMED",
                }
            ],
        },
    )

    assert response.status_code == 200, response.text
    assert response.json()["total_candidates"] == 1
    assert response.json()["items"][0]["due_date"] == "2026-12-05"


def test_wizard_rejects_partial_row_deadline_and_rolls_back_prior_rows(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    first_case = _create_case(client, auth_headers)
    second_case = _create_case(client, auth_headers)
    template = _get_oa_template(client, auth_headers)
    titles = [f"完整期限-{uuid4().hex}", f"不完整期限-{uuid4().hex}"]

    response = client.post(
        WIZARD_URL,
        headers=auth_headers,
        json={
            "defaults": {
                "doc_template_id": template["id"],
                "direction": "IN",
                "doc_date": "2026-07-11",
            },
            "rows": [
                {
                    "case_id": first_case["id"],
                    "title": titles[0],
                    "official_due_date": "2026-10-11",
                    "official_due_date_source": "MANUAL_OFFICIAL_NOTICE",
                    "official_due_date_status": "CONFIRMED",
                },
                {
                    "case_id": second_case["id"],
                    "title": titles[1],
                    "official_due_date": "2026-11-20",
                },
            ],
        },
    )

    assert response.status_code == 400, response.text
    assert response.json()["error"]["code"] == "DOCUMENT_DEADLINE_INVALID"
    with session_factory() as db:
        assert db.execute(select(Document).where(Document.title.in_(titles))).scalars().all() == []
        assert (
            db.execute(select(Task).where(Task.case_id.in_([first_case["id"], second_case["id"]])))
            .scalars()
            .all()
            == []
        )


def test_wizard_unconfirmed_executable_deadline_returns_409_without_writes(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    case = _create_case(client, auth_headers)
    template = _get_oa_template(client, auth_headers)
    title = f"待确认期限-{uuid4().hex}"

    response = client.post(
        WIZARD_URL,
        headers=auth_headers,
        json={
            "defaults": {
                "doc_template_id": template["id"],
                "direction": "IN",
                "doc_date": "2026-07-11",
            },
            "rows": [
                {
                    "case_id": case["id"],
                    "title": title,
                    "official_due_date": "2026-12-05",
                    "official_due_date_source": "IMPORTED_OFFICIAL_NOTICE",
                    "official_due_date_status": "NEEDS_CONFIRMATION",
                }
            ],
        },
    )

    assert response.status_code == 409, response.text
    assert response.json()["error"]["code"] == "OA_OFFICIAL_DUE_DATE_REQUIRED"
    with session_factory() as db:
        assert (
            db.execute(select(Document).where(Document.title == title)).scalar_one_or_none() is None
        )
        assert db.execute(select(Task).where(Task.case_id == case["id"])).scalars().all() == []


def test_wizard_rejects_legacy_unverified_write_status_as_shape_error(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    case = _create_case(client, auth_headers)
    template = _get_oa_template(client, auth_headers)

    response = client.post(
        WIZARD_URL,
        headers=auth_headers,
        json={
            "defaults": {
                "doc_template_id": template["id"],
                "direction": "IN",
                "doc_date": "2026-07-11",
            },
            "rows": [
                {
                    "case_id": case["id"],
                    "title": "禁止 legacy write status",
                    "official_due_date": "2026-12-05",
                    "official_due_date_source": "MANUAL_OFFICIAL_NOTICE",
                    "official_due_date_status": "LEGACY_UNVERIFIED",
                }
            ],
        },
    )

    assert response.status_code == 422, response.text
