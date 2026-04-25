from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

import app.modules.documents.service as document_service
from app.modules.documents.models import DocAttachment
from app.modules.fees.models import FeeDraft, FeeItem
from app.modules.tasks.models import Task
from app.modules.templates.models import Template
from app.modules.templates.render import TemplateRenderer

BASE = "/api/v1/documents/wizard/batch-create"
CASE_BASE = "/api/v1/cases"
DOC_BASE = "/api/v1/documents"
DOC_TMPL_BASE = "/api/v1/doc-templates"


def _unique_case_no() -> str:
    return f"WZ-{uuid4().hex[:8].upper()}"


def _create_applicant(client: TestClient, auth_headers: dict[str, str]) -> dict:
    suffix = uuid4().hex[:8].upper()
    resp = client.post(
        "/api/v1/applicants",
        headers=auth_headers,
        json={
            "code": f"WZ-AP-{suffix}",
            "name_cn": f"Wizard测试申请人-{suffix}",
            "applicant_type": "ENTITY",
            "is_active": True,
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def _create_case(client: TestClient, auth_headers: dict[str, str]) -> dict:
    applicant = _create_applicant(client, auth_headers)
    resp = client.post(
        CASE_BASE,
        headers=auth_headers,
        json={
            "case_no": _unique_case_no(),
            "case_type": "NORMAL",
            "patent_category": "INV",
            "flow_dir": "CN_DOMESTIC",
            "title_cn": "Wizard Test Case",
            "applicants": [
                {
                    "seq": 1,
                    "is_first": True,
                    "applicant_id": applicant["id"],
                    "name_cn": applicant["name_cn"],
                }
            ],
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def _get_template(client: TestClient, auth_headers: dict, code: str) -> dict:
    resp = client.get(DOC_TMPL_BASE, headers=auth_headers, params={"q": code, "page_size": 100})
    assert resp.status_code == 200, resp.text
    items = resp.json()["items"]
    match = [item for item in items if item["code"] == code]
    assert match, f"template {code} not found"
    return match[0]


def _create_fee_template(client: TestClient, auth_headers: dict) -> dict:
    code = f"STEP4_FEE_{uuid4().hex[:8].upper()}"
    resp = client.post(
        DOC_TMPL_BASE,
        headers=auth_headers,
        json={
            "code": code,
            "name": f"Step 4 Fee Template {code}",
            "direction": "IN",
            "enabled": True,
            "fee_draft_type": "CUSTOM_FEE",
            "fee_item_list": json.dumps(
                [
                    {
                        "fee_code": "REG_FEE",
                        "fee_name": "登记费",
                        "fee_type": "GOV",
                        "amount": 200,
                    }
                ]
            ),
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def _preview_task_candidates(
    client: TestClient,
    auth_headers: dict[str, str],
    *,
    template_id: str,
    case_id: str,
    title: str,
) -> dict:
    resp = client.post(
        "/api/v1/documents/wizard/task-preview",
        headers=auth_headers,
        json={
            "defaults": {
                "doc_template_id": template_id,
                "direction": "IN",
                "doc_date": "2026-01-15",
            },
            "rows": [{"case_id": case_id, "title": title}],
        },
    )
    assert resp.status_code == 200, resp.text
    return resp.json()


def _preview_fee_candidates(
    client: TestClient,
    auth_headers: dict[str, str],
    *,
    template_id: str,
    case_id: str,
    title: str,
) -> dict:
    resp = client.post(
        "/api/v1/documents/wizard/fee-preview",
        headers=auth_headers,
        json={
            "defaults": {
                "doc_template_id": template_id,
                "direction": "IN",
                "doc_date": "2026-01-15",
            },
            "rows": [{"case_id": case_id, "title": title}],
        },
    )
    assert resp.status_code == 200, resp.text
    return resp.json()


def _preview_attachment_candidates(
    client: TestClient,
    auth_headers: dict[str, str],
    *,
    template_id: str,
    case_id: str,
    title: str,
) -> dict:
    resp = client.post(
        "/api/v1/documents/wizard/attachment-preview",
        headers=auth_headers,
        json={
            "defaults": {
                "doc_template_id": template_id,
                "direction": "IN",
                "doc_date": "2026-01-15",
            },
            "rows": [{"case_id": case_id, "title": title}],
        },
    )
    assert resp.status_code == 200, resp.text
    return resp.json()


def test_batch_create_documents_success(client: TestClient, auth_headers: dict) -> None:
    case_one = _create_case(client, auth_headers)
    case_two = _create_case(client, auth_headers)
    template = _get_template(client, auth_headers, "CLIENT_IN")

    resp = client.post(
        BASE,
        headers=auth_headers,
        json={
            "defaults": {
                "doc_template_id": template["id"],
                "direction": "IN",
                "doc_date": "2026-01-15",
            },
            "rows": [
                {"case_id": case_one["id"], "title": "第一份批量文件"},
                {"case_id": case_two["id"], "title": "第二份批量文件"},
            ],
        },
    )

    assert resp.status_code == 201, resp.text
    payload = resp.json()
    assert payload["created"] == 2
    assert len(payload["items"]) == 2

    documents = [row["document"] for row in payload["items"]]
    assert {doc["case_id"] for doc in documents} == {case_one["id"], case_two["id"]}
    assert all(doc["doc_template_id"] == template["id"] for doc in documents)

    single_resp = client.post(
        DOC_BASE,
        headers=auth_headers,
        json={
            "case_id": case_one["id"],
            "doc_template_id": template["id"],
            "direction": "IN",
            "doc_date": "2026-01-15",
            "title": "单条文件",
        },
    )
    assert single_resp.status_code == 201, single_resp.text


def test_batch_create_documents_uses_step3_task_rows(
    client: TestClient, auth_headers: dict, session_factory: sessionmaker
) -> None:
    case_one = _create_case(client, auth_headers)
    template = _get_template(client, auth_headers, "OA_IN")

    preview = _preview_task_candidates(
        client,
        auth_headers,
        template_id=template["id"],
        case_id=case_one["id"],
        title="OA 收文任务",
    )
    assert preview["total_candidates"] == 1
    preview_item = preview["items"][0]
    expected_due_date = preview_item["due_date"][:10]
    expected_internal_due_date = "2026-05-01"

    resp = client.post(
        BASE,
        headers=auth_headers,
        json={
            "defaults": {
                "doc_template_id": template["id"],
                "direction": "IN",
                "doc_date": "2026-01-15",
            },
            "rows": [{"case_id": case_one["id"], "title": "OA 收文文书"}],
            "task_rows": [
                {
                    "row_index": preview_item["row_index"],
                    "case_id": case_one["id"],
                    "task_template_code": preview_item["task_template_code"],
                    "title": "手动任务标题",
                    "internal_due_date": expected_internal_due_date,
                    "remind1": "2026-04-30",
                    "remind2": "2026-04-28",
                    "remind3": "2026-04-26",
                }
            ],
        },
    )

    assert resp.status_code == 201, resp.text
    payload = resp.json()
    assert payload["created"] == 1

    tasks_resp = client.get(
        "/api/v1/tasks",
        headers=auth_headers,
        params={"case_id": case_one["id"], "page_size": 100},
    )
    assert tasks_resp.status_code == 200, tasks_resp.text
    tasks_payload = tasks_resp.json()
    assert tasks_payload["total"] == 1
    task = tasks_payload["items"][0]
    assert task["title"] == "手动任务标题"
    assert task["due_date"] == expected_due_date
    assert task["internal_due_date"] == expected_internal_due_date
    assert task["case_id"] == case_one["id"]

    with session_factory() as db:
        created_task = db.query(Task).filter(Task.id == task["id"]).one()
        assert created_task.remind1.isoformat() == "2026-04-30"
        assert created_task.remind2.isoformat() == "2026-04-28"
        assert created_task.remind3.isoformat() == "2026-04-26"
        assert created_task.daily_remind is False


def test_batch_create_documents_uses_step4_fee_rows(
    client: TestClient, auth_headers: dict, session_factory: sessionmaker
) -> None:
    case_one = _create_case(client, auth_headers)
    template = _create_fee_template(client, auth_headers)

    preview = _preview_fee_candidates(
        client,
        auth_headers,
        template_id=template["id"],
        case_id=case_one["id"],
        title="费用预览文书",
    )
    assert preview["total_candidates"] == 1
    preview_item = preview["items"][0]
    preview_fee_item = preview_item["fee_items"][0]

    resp = client.post(
        BASE,
        headers=auth_headers,
        json={
            "defaults": {
                "doc_template_id": template["id"],
                "direction": "IN",
                "doc_date": "2026-01-15",
            },
            "rows": [{"case_id": case_one["id"], "title": "费用最终提交文书"}],
            "fee_rows": [
                {
                    "row_index": preview_item["row_index"],
                    "case_id": case_one["id"],
                    "fee_draft_type": preview_item["fee_draft_type"],
                    "skip_this_candidate": False,
                    "fee_items": [
                        {
                            "fee_code": preview_fee_item["fee_code"],
                            "fee_name": "登记费（调整）",
                            "fee_type": preview_fee_item["fee_type"],
                            "quantity": 1,
                            "unit_price": 180,
                            "amount": 180,
                            "remark": "手动调整",
                        }
                    ],
                }
            ],
        },
    )

    assert resp.status_code == 201, resp.text
    payload = resp.json()
    assert payload["created"] == 1

    with session_factory() as db:
        drafts = (
            db.execute(select(FeeDraft).where(FeeDraft.case_id == case_one["id"])).scalars().all()
        )
        assert len(drafts) == 1
        draft = drafts[0]
        assert draft.draft_type == preview_item["fee_draft_type"]
        assert float(draft.amount) == 180.0
        assert float(draft.total_gov) == 180.0
        assert float(draft.total_service) == 0.0
        assert float(draft.total_misc) == 0.0

        items = db.execute(select(FeeItem).where(FeeItem.draft_id == draft.id)).scalars().all()
        assert len(items) == 1
        item = items[0]
        assert item.fee_code == preview_fee_item["fee_code"]
        assert item.fee_name == "登记费（调整）"
        assert item.fee_type == preview_fee_item["fee_type"]
        assert float(item.quantity) == 1.0
        assert float(item.unit_price) == 180.0
        assert float(item.amount) == 180.0
        assert item.remark == "手动调整"


def test_batch_create_documents_uses_step5_attachment_rows(
    client: TestClient,
    auth_headers: dict,
    session_factory: sessionmaker,
    tmp_path: Path,
    monkeypatch,
) -> None:
    case_one = _create_case(client, auth_headers)
    template = _get_template(client, auth_headers, "CLIENT_IN")

    template_source_file = tmp_path / "wizard-step5-template.docx"
    template_source_file.write_bytes(b"fake-template-source")

    with session_factory() as db:
        db.add(
            Template(
                id=str(uuid4()),
                name=template["code"],
                group="DOC_TEMPLATE",
                language="zh-CN",
                file_path=str(template_source_file),
                enabled=True,
            )
        )
        db.commit()

    monkeypatch.setattr(document_service, "_backend_storage_dir", lambda: tmp_path)
    monkeypatch.setattr(
        TemplateRenderer,
        "render_template_docx_bytes",
        lambda self, *, template_path, context: (
            b"rendered-step5-docx"
            if template_path == str(template_source_file)
            and context["document"]["title"] == "附件最终提交文书"
            else b"unexpected-render"
        ),
    )

    preview = _preview_attachment_candidates(
        client,
        auth_headers,
        template_id=template["id"],
        case_id=case_one["id"],
        title="附件预览文书",
    )
    assert preview["total_candidates"] == 1
    preview_item = preview["items"][0]

    resp = client.post(
        BASE,
        headers=auth_headers,
        json={
            "defaults": {
                "doc_template_id": template["id"],
                "direction": "IN",
                "doc_date": "2026-01-15",
            },
            "rows": [{"case_id": case_one["id"], "title": "附件最终提交文书"}],
            "attachment_rows": [
                {
                    "row_index": preview_item["row_index"],
                    "case_id": case_one["id"],
                    "template_code": preview_item["template_code"],
                    "output_name": "授权通知书终稿",
                    "output_file_name": "授权通知书终稿.docx",
                    "output_format": preview_item["output_format"],
                    "candidate_source_kind": preview_item["candidate_source_kind"],
                    "remark": "最终附件",
                }
            ],
        },
    )

    assert resp.status_code == 201, resp.text
    payload = resp.json()
    assert payload["created"] == 1
    document_id = payload["items"][0]["document"]["id"]

    with session_factory() as db:
        attachments = (
            db.execute(select(DocAttachment).where(DocAttachment.document_id == document_id))
            .scalars()
            .all()
        )
        assert len(attachments) == 1
        attachment = attachments[0]
        assert attachment.file_name == "授权通知书终稿.docx"
        assert (
            attachment.mime_type
            == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        assert attachment.file_path.startswith(f"attachments/{document_id}/")
        stored_path = tmp_path / attachment.file_path
        assert stored_path.exists()
        assert stored_path.read_bytes() == b"rendered-step5-docx"


def test_batch_create_documents_rejects_invalid_row(client: TestClient, auth_headers: dict) -> None:
    case_one = _create_case(client, auth_headers)
    template = _get_template(client, auth_headers, "CLIENT_IN")

    resp = client.post(
        BASE,
        headers=auth_headers,
        json={
            "defaults": {
                "doc_template_id": template["id"],
                "direction": "IN",
                "doc_date": "2026-01-15",
            },
            "rows": [
                {"case_id": case_one["id"], "title": "有效行"},
                {"case_id": str(uuid4()), "title": "无效行"},
            ],
        },
    )

    assert resp.status_code == 400, resp.text
    payload = resp.json()
    assert payload["error"]["code"] == "DOCUMENT_WIZARD_BATCH_INVALID"
    assert payload["error"]["details"]["row_errors"]


def test_batch_create_documents_rejects_invalid_step3_task_row(
    client: TestClient, auth_headers: dict
) -> None:
    case_one = _create_case(client, auth_headers)
    template = _get_template(client, auth_headers, "OA_IN")

    resp = client.post(
        BASE,
        headers=auth_headers,
        json={
            "defaults": {
                "doc_template_id": template["id"],
                "direction": "IN",
                "doc_date": "2026-01-15",
            },
            "rows": [{"case_id": case_one["id"], "title": "OA 收文文书"}],
            "task_rows": [
                {
                    "row_index": 2,
                    "case_id": case_one["id"],
                    "task_template_code": "OA_REPLY",
                    "title": "无效任务行",
                }
            ],
        },
    )

    assert resp.status_code == 400, resp.text
    payload = resp.json()
    assert payload["error"]["code"] == "DOCUMENT_WIZARD_BATCH_INVALID"
    assert payload["error"]["details"]["row_errors"]


def test_batch_create_documents_rejects_invalid_step4_fee_row(
    client: TestClient, auth_headers: dict
) -> None:
    case_one = _create_case(client, auth_headers)
    template = _create_fee_template(client, auth_headers)

    resp = client.post(
        BASE,
        headers=auth_headers,
        json={
            "defaults": {
                "doc_template_id": template["id"],
                "direction": "IN",
                "doc_date": "2026-01-15",
            },
            "rows": [{"case_id": case_one["id"], "title": "费用最终提交文书"}],
            "fee_rows": [
                {
                    "row_index": 2,
                    "case_id": case_one["id"],
                    "fee_draft_type": "CUSTOM_FEE",
                    "skip_this_candidate": False,
                    "fee_items": [
                        {
                            "fee_code": "REG_FEE",
                            "fee_name": "登记费（调整）",
                            "fee_type": "GOV",
                            "quantity": 1,
                            "unit_price": 180,
                            "amount": 180,
                            "remark": "手动调整",
                        }
                    ],
                }
            ],
        },
    )

    assert resp.status_code == 400, resp.text
    payload = resp.json()
    assert payload["error"]["code"] == "DOCUMENT_WIZARD_BATCH_INVALID"
    assert payload["error"]["details"]["row_errors"]


def test_batch_create_documents_rejects_invalid_step5_attachment_row(
    client: TestClient, auth_headers: dict
) -> None:
    case_one = _create_case(client, auth_headers)
    template = _get_template(client, auth_headers, "CLIENT_IN")

    resp = client.post(
        BASE,
        headers=auth_headers,
        json={
            "defaults": {
                "doc_template_id": template["id"],
                "direction": "IN",
                "doc_date": "2026-01-15",
            },
            "rows": [{"case_id": case_one["id"], "title": "附件最终提交文书"}],
            "attachment_rows": [
                {
                    "row_index": 2,
                    "case_id": case_one["id"],
                    "template_code": template["code"],
                    "output_name": "无效附件",
                    "output_file_name": "无效附件.docx",
                    "output_format": "DOCX",
                    "candidate_source_kind": "DOC_TEMPLATE",
                }
            ],
        },
    )

    assert resp.status_code == 400, resp.text
    payload = resp.json()
    assert payload["error"]["code"] == "DOCUMENT_WIZARD_BATCH_INVALID"
    assert payload["error"]["details"]["row_errors"]
