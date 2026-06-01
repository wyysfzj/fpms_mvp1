from __future__ import annotations

import json
from datetime import datetime
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from app.modules.annuity.models import PayList  # noqa: F401
from app.modules.cases.models import Case
from app.modules.documents.enums import DocumentDirection
from app.modules.documents.models import DocAttachment, DocTemplate, Document, LetterHandoff
from app.modules.masterdata.clients.models import Client, ClientContact
from app.modules.templates.models import FormatLetterMapping, Template

BASE = "/api/v1/official-documents"


def _create_letter_handoff_fixture(session_factory: sessionmaker) -> dict[str, str]:
    with session_factory() as db:
        client = Client(
            id=str(uuid4()),
            client_code=f"C-{uuid4().hex[:6].upper()}",
            name_cn="测试客户有限公司",
            email="client@example.com",
        )
        db.add(client)
        db.flush()
        contact = ClientContact(
            id=str(uuid4()),
            client_id=client.id,
            contact_name="张三",
            title="老师",
            email="zhangsan@example.com",
            is_primary=True,
        )
        db.add(contact)
        oa_in_template = db.execute(
            select(DocTemplate).where(DocTemplate.code == "OA_IN")
        ).scalar_one()
        case = Case(
            id=str(uuid4()),
            case_no=f"LH-{uuid4().hex[:8].upper()}",
            case_type="NORMAL",
            patent_category="INV",
            flow_dir="CN_DOMESTIC",
            client_id=client.id,
            title_cn="格式函交接测试案件",
            app_no="CN202610000002.0",
        )
        db.add(case)
        db.flush()
        official_doc = Document(
            id=str(uuid4()),
            case_id=case.id,
            doc_template_id=oa_in_template.id,
            direction=DocumentDirection.IN,
            title="第一次审查意见通知书",
            ref_no="OA1",
        )
        db.add(official_doc)
        db.flush()
        official_attachment = DocAttachment(
            id=str(uuid4()),
            document_id=official_doc.id,
            file_name="第一次审查意见通知书.pdf",
            file_path=f"attachments/{official_doc.id}/oa.pdf",
            mime_type="application/pdf",
            file_size=128,
            official_file_role="OFFICIAL_NOTICE_PDF",
        )
        template = Template(
            id=str(uuid4()),
            name="一通格式函模板",
            group="FORMAT_LETTER",
            language="zh-CN",
            file_path="templates/format-letter-oa1.docx",
            enabled=True,
        )
        db.add(template)
        db.flush()
        mapping = FormatLetterMapping(
            id=str(uuid4()),
            official_doc_template_id=oa_in_template.id,
            official_doc_template_code="OA_IN",
            official_doc_name_pattern="第一次审查意见",
            format_letter_template_id=template.id,
            format_letter_template_code="FORMAT_LETTER_OA1",
            output_name_rule="{case_no}-一通格式函.docx",
            salutation_rule_code="PRIMARY_CONTACT_TITLE",
            contact_rule_code="CLIENT_PRIMARY_CONTACT",
            enabled=True,
        )
        db.add_all([official_attachment, mapping])
        db.commit()
        return {
            "case_id": case.id,
            "case_no": case.case_no,
            "client_id": client.id,
            "contact_id": contact.id,
            "document_id": official_doc.id,
            "attachment_id": official_attachment.id,
            "mapping_id": mapping.id,
            "template_id": template.id,
        }


def test_letter_handoff_api_previews_creates_and_records_status(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    ids = _create_letter_handoff_fixture(session_factory)

    preview_resp = client.get(
        f"{BASE}/{ids['document_id']}/letter-handoff/preview",
        headers=auth_headers,
    )
    assert preview_resp.status_code == 200, preview_resp.text
    preview = preview_resp.json()
    assert preview["source_document_id"] == ids["document_id"]
    assert preview["mapping"]["id"] == ids["mapping_id"]
    assert preview["template_status"] == "READY"
    assert preview["client_contact_id"] == ids["contact_id"]
    assert preview["contact_selection_source"] == "CLIENT_PRIMARY_CONTACT"
    assert preview["salutation_text"] == "张三老师：您好"
    assert preview["generated_word_path"].endswith(f"{ids['case_no']}-一通格式函.docx")
    assert preview["mail_subject"] == f"{ids['case_no']} 第一次审查意见通知书"
    assert "格式函交接测试案件" in preview["mail_body_draft"]
    assert {item["attachment_role"] for item in preview["attachments"]} == {
        "FORMAT_LETTER_WORD",
        "SOURCE_OFFICIAL_DOCUMENT",
    }

    create_resp = client.post(
        f"{BASE}/{ids['document_id']}/letter-handoff",
        headers=auth_headers,
        json={"remark": "交给龙虾系统待发送"},
    )
    assert create_resp.status_code == 201, create_resp.text
    created = create_resp.json()
    assert created["handoff"]["source_document_id"] == ids["document_id"]
    assert created["handoff"]["format_letter_mapping_id"] == ids["mapping_id"]
    assert created["handoff"]["format_letter_template_id"] == ids["template_id"]
    assert created["handoff"]["client_contact_id"] == ids["contact_id"]
    assert created["handoff"]["salutation_text"] == "张三老师：您好"
    assert created["handoff"]["longxia_handoff_status"] == "READY"
    assert (
        json.loads(created["handoff"]["longxia_handoff_payload"])["source_document_id"]
        == ids["document_id"]
    )
    assert len(created["handoff"]["attachments"]) == 2

    handoff_id = created["handoff"]["id"]
    status_resp = client.patch(
        f"{BASE}/{ids['document_id']}/letter-handoff/{handoff_id}/status",
        headers=auth_headers,
        json={
            "longxia_handoff_status": "HANDED_OFF",
            "longxia_handoff_payload": '{"batch":"LX-20260531"}',
            "handoff_at": "2026-05-31T15:30:00",
        },
    )
    assert status_resp.status_code == 200, status_resp.text
    updated = status_resp.json()
    assert updated["handoff"]["longxia_handoff_status"] == "HANDED_OFF"
    assert updated["handoff"]["handoff_at"] == "2026-05-31T15:30:00"

    with session_factory() as db:
        stored = db.get(LetterHandoff, handoff_id)
        assert stored is not None
        assert stored.longxia_handoff_status == "HANDED_OFF"
        assert stored.contact_selection_source == "CLIENT_PRIMARY_CONTACT"
        assert stored.salutation_source == "PRIMARY_CONTACT_TITLE"
        assert stored.handoff_at == datetime(2026, 5, 31, 15, 30, 0)


def test_letter_handoff_preview_uses_default_salutation_without_confirmed_contact_rule(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    ids = _create_letter_handoff_fixture(session_factory)
    with session_factory() as db:
        mapping = db.get(FormatLetterMapping, ids["mapping_id"])
        assert mapping is not None
        mapping.contact_rule_code = None
        mapping.salutation_rule_code = None
        db.commit()

    resp = client.get(
        f"{BASE}/{ids['document_id']}/letter-handoff/preview",
        headers=auth_headers,
    )

    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["client_contact_id"] is None
    assert body["contact_selection_source"] == "UNCONFIRMED"
    assert body["salutation_text"] == "尊敬的：您好"
