from __future__ import annotations

import json
from datetime import date
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

import app.api.deps as deps
import app.modules.grant_fees.service as grant_fee_service
from app.modules.documents.models import DocAttachment, DocTemplate, Document
from app.modules.fees.models import T_GrantFeeTask
from app.modules.templates.models import Template

NOTICE_BASE = "/api/v1/grant-fee-tasks/generate-notices"


def _uid(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:8].upper()}"


def _create_client(client: TestClient, auth_headers: dict[str, str]) -> dict:
    resp = client.post(
        "/api/v1/clients",
        json={
            "client_code": _uid("GFN-CLI"),
            "name_cn": _uid("GFN-CLIENT"),
            "default_currency": "CNY",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def _create_case(
    client: TestClient,
    auth_headers: dict[str, str],
    *,
    client_id: str | None = None,
) -> dict:
    payload = {
        "case_no": _uid("GFN-CASE"),
        "case_type": "NORMAL",
        "patent_category": "INV",
        "flow_dir": "CN_DOMESTIC",
        "title_cn": "Grant Fee Notice Test Case",
    }
    if client_id:
        payload["client_id"] = client_id

    resp = client.post("/api/v1/cases", json=payload, headers=auth_headers)
    assert resp.status_code == 201, resp.text
    return resp.json()


def _insert_task(
    session_factory: sessionmaker,
    *,
    case_id: str,
    **overrides,
) -> str:
    with session_factory() as db:
        task = T_GrantFeeTask(
            case_id=case_id,
            due_date=overrides.pop("due_date", date(2026, 5, 20)),
            gov_fee_amt=overrides.pop("gov_fee_amt", Decimal("120.00")),
            service_fee_amt=overrides.pop("service_fee_amt", Decimal("80.00")),
            currency=overrides.pop("currency", "CNY"),
            client_instruction=overrides.pop("client_instruction", "NONE"),
            notify_count=overrides.pop("notify_count", 0),
            draft_generated=overrides.pop("draft_generated", False),
            notice_sent=overrides.pop("notice_sent", False),
            is_overdue=overrides.pop("is_overdue", False),
            remark=overrides.pop("remark", None),
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        return task.id


def _create_notice_template_bundle(session_factory: sessionmaker, *, template_path: Path) -> None:
    with session_factory() as db:
        existing_doc_template = db.execute(
            select(DocTemplate).where(DocTemplate.code == "GRANT_FEE_NOTICE")
        ).scalar_one_or_none()
        if existing_doc_template is None:
            existing_doc_template = DocTemplate(
                id=str(uuid4()),
                code="GRANT_FEE_NOTICE",
                name="授权费通知函",
                direction="OUT",
                enabled=True,
            )
            db.add(existing_doc_template)
        else:
            existing_doc_template.name = "授权费通知函"
            existing_doc_template.direction = "OUT"
            existing_doc_template.enabled = True

        existing_templates = (
            db.execute(
                select(Template).where(
                    Template.name == "GRANT_FEE_NOTICE",
                    Template.group == "DOC_TEMPLATE",
                )
            )
            .scalars()
            .all()
        )
        primary_template = existing_templates[0] if existing_templates else None
        for duplicate_template in existing_templates[1:]:
            db.delete(duplicate_template)

        if primary_template is None:
            primary_template = Template(
                id=str(uuid4()),
                name="GRANT_FEE_NOTICE",
                group="DOC_TEMPLATE",
                language="zh-CN",
                file_path=str(template_path),
                enabled=True,
            )
            db.add(primary_template)
        else:
            primary_template.language = "zh-CN"
            primary_template.file_path = str(template_path)
            primary_template.enabled = True
        db.commit()


def _set_missing_notice_template_code(monkeypatch) -> None:
    monkeypatch.setattr(
        grant_fee_service,
        "GRANT_FEE_NOTICE_TEMPLATE_CODE",
        f"MISSING_{uuid4().hex[:8].upper()}",
    )


def test_grant_fee_notice_generation_creates_document_and_attachment(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
    tmp_path: Path,
    monkeypatch,
) -> None:
    client_row = _create_client(client, auth_headers)
    case = _create_case(client, auth_headers, client_id=client_row["id"])
    task_id = _insert_task(session_factory, case_id=case["id"])

    template_path = tmp_path / "grant_fee_notice.docx"
    template_path.write_bytes(b"template")
    _create_notice_template_bundle(session_factory, template_path=template_path)

    storage_dir = tmp_path / "storage"
    storage_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(grant_fee_service, "_backend_storage_dir", lambda: storage_dir)

    captured: dict[str, object] = {}

    def _fake_render(self, *, template_path: str, context: dict) -> bytes:
        captured["template_path"] = template_path
        captured["context"] = context
        return b"generated-docx"

    monkeypatch.setattr(
        "app.modules.templates.render.TemplateRenderer.render_template_docx_bytes",
        _fake_render,
    )

    resp = client.post(NOTICE_BASE, json={"task_ids": [task_id]}, headers=auth_headers)
    assert resp.status_code == 200, resp.text
    payload = resp.json()

    assert payload["success_count"] == 1
    assert payload["failure_count"] == 0
    assert payload["generated_document_ids"]
    assert len(payload["items"]) == 1
    assert payload["items"][0]["task_id"] == task_id
    assert payload["items"][0]["case_id"] == case["id"]
    assert payload["items"][0]["notify_count"] == 1
    assert payload["items"][0]["file_name"].endswith(".docx")

    assert captured["template_path"] == str(template_path)
    context = captured["context"]
    assert isinstance(context, dict)
    assert context["grant_fee_task"]["id"] == task_id
    assert context["grant_fee_task"]["notify_count"] == 1
    assert context["document_direction"] == "OUT"

    with session_factory() as db:
        task = db.execute(select(T_GrantFeeTask).where(T_GrantFeeTask.id == task_id)).scalar_one()
        document = db.execute(select(Document).where(Document.case_id == case["id"])).scalar_one()
        attachment = db.execute(
            select(DocAttachment).where(DocAttachment.document_id == document.id)
        ).scalar_one()

    assert task.notice_sent is True
    assert task.notify_count == 1
    assert document.doc_template_id is not None
    assert document.direction == "OUT"
    assert json.loads(document.extra_data or "{}") == {"grant_fee_task_id": task_id}
    assert attachment.file_name.endswith(".docx")
    assert attachment.mime_type == grant_fee_service.DOCX_MIME_TYPE
    assert (storage_dir / attachment.file_path).read_bytes() == b"generated-docx"


def test_grant_fee_notice_generation_rejects_task_with_client_instruction(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
    tmp_path: Path,
) -> None:
    case = _create_case(client, auth_headers)
    task_id = _insert_task(session_factory, case_id=case["id"], client_instruction="PAY")
    template_path = tmp_path / "grant_fee_notice.docx"
    template_path.write_bytes(b"template")
    _create_notice_template_bundle(session_factory, template_path=template_path)

    resp = client.post(NOTICE_BASE, json={"task_ids": [task_id]}, headers=auth_headers)
    assert resp.status_code == 400, resp.text
    body = resp.json()
    assert body["error"]["code"] == "GRANT_FEE_NOTICE_STATE_INVALID"


def test_grant_fee_notice_generation_requires_template_configuration(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
    monkeypatch,
) -> None:
    case = _create_case(client, auth_headers)
    task_id = _insert_task(session_factory, case_id=case["id"])
    _set_missing_notice_template_code(monkeypatch)

    resp = client.post(NOTICE_BASE, json={"task_ids": [task_id]}, headers=auth_headers)
    assert resp.status_code == 409, resp.text
    body = resp.json()
    assert body["error"]["code"] == "GRANT_FEE_NOTICE_TEMPLATE_NOT_FOUND"


def test_grant_fee_notice_generation_requires_write_permission(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
    tmp_path: Path,
    monkeypatch,
) -> None:
    case = _create_case(client, auth_headers)
    task_id = _insert_task(session_factory, case_id=case["id"])
    template_path = tmp_path / "grant_fee_notice.docx"
    template_path.write_bytes(b"template")
    _create_notice_template_bundle(session_factory, template_path=template_path)

    def _no_perms(_db, _user_id) -> set[str]:
        return set()

    monkeypatch.setattr(deps, "get_user_permissions", _no_perms)

    resp = client.post(NOTICE_BASE, json={"task_ids": [task_id]}, headers=auth_headers)
    assert resp.status_code == 403, resp.text
    assert resp.json()["error"]["details"]["required_perm"] == "GrantFeeTask.Write"
