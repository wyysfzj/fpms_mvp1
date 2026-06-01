from __future__ import annotations

import json
from datetime import date
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from app.modules.annuity.models import PayList  # noqa: F401
from app.modules.cases.models import Case, T_CaseApplicant
from app.modules.documents.enums import DocumentDirection
from app.modules.documents.models import DocAttachment, DocTemplate, Document
from app.modules.official_workflows.models import (
    OfficialWorkPackage,
    OfficialWorkPackageChecklist,
    OfficialWorkPackageManifest,
)
from app.modules.tasks.models import Task

BASE = "/api/v1/official-work-packages"


def _create_oa_reply_fixture(session_factory: sessionmaker) -> dict[str, str]:
    with session_factory() as db:
        oa_in_template = db.execute(
            select(DocTemplate).where(DocTemplate.code == "OA_IN")
        ).scalar_one()
        oa_out_template = db.execute(
            select(DocTemplate).where(DocTemplate.code == "OA_OUT")
        ).scalar_one()
        case = Case(
            id=str(uuid4()),
            case_no=f"OA-{uuid4().hex[:8].upper()}",
            case_type="NORMAL",
            patent_category="INV",
            flow_dir="CN_DOMESTIC",
            title_cn="OA 答复工作包测试案件",
            app_no="CN202610000001.0",
        )
        db.add(case)
        db.flush()
        db.add(
            T_CaseApplicant(
                id=str(uuid4()),
                case_id=case.id,
                seq=1,
                is_first=True,
                name_cn="第一申请人A",
                nationality="CN",
                certificate_type="统一社会信用代码",
                certificate_no="91310000MA1A000000",
                official_postcode="200001",
            )
        )
        source_doc = Document(
            id=str(uuid4()),
            case_id=case.id,
            doc_template_id=oa_in_template.id,
            direction=DocumentDirection.IN,
            doc_date=date(2026, 5, 10),
            title="第一次审查意见通知书",
            ref_no="OA1",
            need_reply=True,
            extra_data=json.dumps(
                {
                    "official_notice_code": "200101",
                    "official_notice_name": "第一次审查意见通知书",
                    "issue_sequence": "1",
                    "official_due_date": "2026-08-10",
                },
                ensure_ascii=False,
            ),
        )
        reply_doc = Document(
            id=str(uuid4()),
            case_id=case.id,
            doc_template_id=oa_out_template.id,
            direction=DocumentDirection.OUT,
            doc_date=date(2026, 5, 31),
            title="第一次审查意见答复",
            extra_data=json.dumps(
                {
                    "reply_statement_text": "详见随附 PDF 意见陈述书。",
                    "experiment_data_submitted": True,
                },
                ensure_ascii=False,
            ),
        )
        db.add_all([source_doc, reply_doc])
        db.flush()

        attachments = [
            DocAttachment(
                id=str(uuid4()),
                document_id=reply_doc.id,
                file_name="意见陈述书.docx",
                file_path=f"attachments/{reply_doc.id}/statement.docx",
                mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                file_size=128,
                official_file_role="OA_STATEMENT_WORD",
                content_hash="sha256:statement-word",
            ),
            DocAttachment(
                id=str(uuid4()),
                document_id=reply_doc.id,
                file_name="意见陈述书.pdf",
                file_path=f"attachments/{reply_doc.id}/statement.pdf",
                mime_type="application/pdf",
                file_size=256,
                official_file_role="OA_STATEMENT_PDF",
                content_hash="sha256:statement-pdf",
            ),
            DocAttachment(
                id=str(uuid4()),
                document_id=reply_doc.id,
                file_name="修改后权利要求书.docx",
                file_path=f"attachments/{reply_doc.id}/claims.docx",
                mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                file_size=512,
                official_file_role="OA_MODIFIED_CLAIMS",
                content_hash="sha256:claims",
            ),
            DocAttachment(
                id=str(uuid4()),
                document_id=reply_doc.id,
                file_name="修改对照页.pdf",
                file_path=f"attachments/{reply_doc.id}/comparison.pdf",
                mime_type="application/pdf",
                file_size=512,
                official_file_role="OA_AMENDMENT_COMPARISON",
                content_hash="sha256:comparison",
            ),
            DocAttachment(
                id=str(uuid4()),
                document_id=reply_doc.id,
                file_name="实验数据.pdf",
                file_path=f"attachments/{reply_doc.id}/proof.pdf",
                mime_type="application/pdf",
                file_size=512,
                official_file_role="OA_OTHER_PROOF",
                content_hash="sha256:proof",
            ),
        ]
        db.add_all(attachments)
        db.add(
            Task(
                id=str(uuid4()),
                case_id=case.id,
                document_id=source_doc.id,
                title="OA 答复任务",
                base_date=date(2026, 5, 10),
                due_date=date(2026, 8, 10),
                internal_due_date=date(2026, 7, 31),
                status="OPEN",
            )
        )
        package = OfficialWorkPackage(
            id=str(uuid4()),
            case_id=case.id,
            package_kind="OA_REPLY",
            status="PREPARING",
            source_document_id=source_doc.id,
            external_system="CNIPA_WEB",
        )
        db.add(package)
        db.commit()
        return {
            "case_id": case.id,
            "source_document_id": source_doc.id,
            "reply_document_id": reply_doc.id,
            "package_id": package.id,
        }


def test_oa_reply_package_api_links_reply_document_refreshes_manifest_and_checklist(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    ids = _create_oa_reply_fixture(session_factory)

    link_resp = client.post(
        f"{BASE}/{ids['package_id']}/oa-reply/reply-document",
        headers=auth_headers,
        json={"reply_document_id": ids["reply_document_id"]},
    )
    assert link_resp.status_code == 200, link_resp.text
    linked = link_resp.json()
    assert linked["package"]["reply_document_id"] == ids["reply_document_id"]
    assert linked["reply_document"]["reply_to_id"] == ids["source_document_id"]
    assert linked["reply_status"] == "REPLY_DOCUMENT_LINKED"

    refresh_resp = client.post(
        f"{BASE}/{ids['package_id']}/oa-reply/refresh",
        headers=auth_headers,
        json={},
    )
    assert refresh_resp.status_code == 200, refresh_resp.text
    body = refresh_resp.json()
    assert body["application_no"] == "CN202610000001.0"
    assert body["applicant_display"] == "第一申请人A"
    assert body["notice_code"] == "200101"
    assert body["notice_name"] == "第一次审查意见通知书"
    assert body["issue_sequence"] == "1"
    assert body["issue_date"] == "2026-05-10"
    assert body["official_due_date"] == "2026-08-10"
    assert body["internal_due_date"] == "2026-07-31"
    assert body["statement_text"] == "详见随附 PDF 意见陈述书。"
    assert body["experiment_data_submitted"] is True
    assert body["statement_word"]["status"] == "PRESENT"
    assert body["statement_pdf"]["status"] == "PRESENT"
    assert body["comparison_page"]["status"] == "PRESENT"
    assert [item["role"] for item in body["modified_claim_files"]] == ["OA_MODIFIED_CLAIMS"]
    assert [item["role"] for item in body["proof_files"]] == ["OA_OTHER_PROOF"]
    assert "PDF_FIDELITY_CONFIRMED" in {
        item["item_code"] for item in body["official_page_checklist"]
    }

    checklist_resp = client.patch(
        f"{BASE}/{ids['package_id']}/oa-reply/checklist/PDF_FIDELITY_CONFIRMED",
        headers=auth_headers,
        json={"status": "DONE", "evidence_note": "PDF 附件已人工核对"},
    )
    assert checklist_resp.status_code == 200, checklist_resp.text
    assert checklist_resp.json()["checklist_item"]["status"] == "DONE"

    get_resp = client.get(
        f"{BASE}/{ids['package_id']}/oa-reply",
        headers=auth_headers,
    )
    assert get_resp.status_code == 200, get_resp.text
    checklist_by_code = {
        item["item_code"]: item for item in get_resp.json()["official_page_checklist"]
    }
    assert checklist_by_code["PDF_FIDELITY_CONFIRMED"]["status"] == "DONE"

    with session_factory() as db:
        source_doc = db.get(Document, ids["source_document_id"])
        reply_doc = db.get(Document, ids["reply_document_id"])
        manifests = (
            db.execute(
                select(OfficialWorkPackageManifest).where(
                    OfficialWorkPackageManifest.package_id == ids["package_id"]
                )
            )
            .scalars()
            .all()
        )
        checklists = (
            db.execute(
                select(OfficialWorkPackageChecklist).where(
                    OfficialWorkPackageChecklist.package_id == ids["package_id"]
                )
            )
            .scalars()
            .all()
        )
        assert source_doc is not None
        assert source_doc.need_reply is True
        assert source_doc.reply_date is None
        assert reply_doc is not None
        assert reply_doc.reply_to_id == ids["source_document_id"]
        assert {manifest.official_file_role for manifest in manifests} >= {
            "OA_STATEMENT_WORD",
            "OA_STATEMENT_PDF",
            "OA_MODIFIED_CLAIMS",
            "OA_AMENDMENT_COMPARISON",
            "OA_OTHER_PROOF",
        }
        assert {checklist.item_code for checklist in checklists} >= {
            "STATEMENT_TEXT_CONFIRMED",
            "PDF_FIDELITY_CONFIRMED",
            "MODIFIED_CLAIMS_CONFIRMED",
            "EXPERIMENT_DATA_FLAG_CONFIRMED",
            "PREVIEW_CONFIRMED",
            "SIGNATURE_CONFIRMED",
        }


def test_oa_reply_package_api_rejects_non_oa_package(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    ids = _create_oa_reply_fixture(session_factory)
    with session_factory() as db:
        package = db.get(OfficialWorkPackage, ids["package_id"])
        assert package is not None
        package.package_kind = "FILING_PREP"
        db.commit()

    resp = client.get(
        f"{BASE}/{ids['package_id']}/oa-reply",
        headers=auth_headers,
    )

    assert resp.status_code == 400, resp.text
    assert resp.json()["error"]["code"] == "OFFICIAL_WORK_PACKAGE_KIND_INVALID"
