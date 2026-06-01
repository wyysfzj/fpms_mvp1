from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from app.modules.annuity.models import PayList  # noqa: F401
from app.modules.cases.models import Case, T_CaseApplicant, T_CaseInventor
from app.modules.documents.enums import DocumentDirection
from app.modules.documents.models import DocAttachment, DocTemplate, Document
from app.modules.fees.models import FeeDraft
from app.modules.official_workflows.models import (
    OfficialWorkPackage,
    OfficialWorkPackageChecklist,
    OfficialWorkPackageManifest,
)

BASE = "/api/v1/official-work-packages"


def _create_filing_fixture(session_factory: sessionmaker) -> tuple[str, str]:
    with session_factory() as db:
        template = db.execute(
            select(DocTemplate).where(DocTemplate.code == "CLIENT_IN")
        ).scalar_one()
        case = Case(
            id=str(uuid4()),
            case_no=f"FIL-{uuid4().hex[:8].upper()}",
            case_type="NORMAL",
            patent_category="INV",
            flow_dir="CN_DOMESTIC",
            title_cn="新申请递交包 API 测试案件",
            primary_agent_id="agent-user-1",
            spec_pages=12,
            claim_count=8,
            draw_pages=2,
            has_exam_request=True,
            fee_reduction="0.85",
            discount_rate=Decimal("0.8500"),
        )
        db.add(case)
        db.flush()
        db.add_all(
            [
                T_CaseApplicant(
                    id=str(uuid4()),
                    case_id=case.id,
                    seq=1,
                    is_first=True,
                    name_cn="测试申请人",
                    address_cn="北京市海淀区",
                    nationality="CN",
                    certificate_type="USCI",
                    certificate_no="91110000123456789X",
                    official_postcode=None,
                    official_applicant_kind="ENTERPRISE",
                ),
                T_CaseInventor(
                    id=str(uuid4()),
                    case_id=case.id,
                    seq=1,
                    name_cn="测试发明人",
                    nationality="CN",
                    china_id_no="110101199001011234",
                ),
            ]
        )
        document = Document(
            id=str(uuid4()),
            case_id=case.id,
            doc_template_id=template.id,
            direction=DocumentDirection.IN,
            doc_date=date(2026, 5, 31),
            title="客户新申请来文",
        )
        db.add(document)
        db.flush()
        db.add_all(
            [
                DocAttachment(
                    id=str(uuid4()),
                    document_id=document.id,
                    file_name="技术交底书.docx",
                    file_path=f"attachments/{document.id}/td.docx",
                    mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    file_size=256,
                    official_file_role="TECHNICAL_DISCLOSURE",
                    content_hash="sha256:td",
                ),
                DocAttachment(
                    id=str(uuid4()),
                    document_id=document.id,
                    file_name="请求类表格.zip",
                    file_path=f"attachments/{document.id}/filing.zip",
                    mime_type="application/zip",
                    file_size=512,
                    official_file_role="FILING_XML_ZIP",
                    content_hash="sha256:zip",
                ),
            ]
        )
        package = OfficialWorkPackage(
            id=str(uuid4()),
            case_id=case.id,
            package_kind="FILING_PREP",
            status="PREPARING",
            external_system="CNIPA_WEB",
        )
        db.add(
            FeeDraft(
                id=str(uuid4()),
                case_id=case.id,
                draft_type="APPLY_FEE",
                currency="CNY",
                status="OPEN",
                total_gov=Decimal("950.00"),
                total_service=Decimal("300.00"),
                total_misc=Decimal("0.00"),
                amount=Decimal("1250.00"),
                official_fee_reduction_note="0.85 语义待确认",
                official_template_status="UNCONFIRMED",
            )
        )
        db.add(package)
        db.commit()
        return package.id, case.id


def test_filing_package_refresh_read_and_review_api(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    package_id, case_id = _create_filing_fixture(session_factory)

    refresh_resp = client.post(
        f"{BASE}/{package_id}/filing-preparation/refresh",
        headers=auth_headers,
        json={"require_commission_instruction": True},
    )
    assert refresh_resp.status_code == 200, refresh_resp.text
    body = refresh_resp.json()
    assert body["package"]["id"] == package_id
    assert body["package"]["case_id"] == case_id
    assert body["official_field_summary"]["status"] == "NEEDS_MAINTENANCE"
    assert "APPLICANT_1_OFFICIAL_POSTCODE" in body["official_field_summary"]["missing_codes"]
    assert body["technical_disclosure_gate"]["status"] == "READY"
    assert body["commission_instruction_gate"]["required"] is True
    assert body["commission_instruction_gate"]["status"] == "MISSING"
    assert body["xml_zip"]["status"] == "PRESENT"
    assert body["merged_pdf_archive_status"] == "MISSING"
    assert body["fee_summary"]["draft_count"] == 1
    assert body["fee_summary"]["official_template_ready"] is False

    manifest_by_role = {item["official_file_role"]: item for item in body["filing_file_roles"]}
    assert manifest_by_role["TECHNICAL_DISCLOSURE"]["present"] is True
    assert manifest_by_role["COMMISSION_INSTRUCTION"]["present"] is False
    assert manifest_by_role["FILING_XML_ZIP"]["present"] is True
    assert manifest_by_role["FILING_MERGED_PDF"]["present"] is False

    review_resp = client.patch(
        f"{BASE}/{package_id}/filing-preparation/checklist/PREVIEW_CONFIRMED",
        headers=auth_headers,
        json={"status": "DONE", "evidence_note": "官方页面预览已人工确认"},
    )
    assert review_resp.status_code == 200, review_resp.text
    assert review_resp.json()["checklist_item"]["status"] == "DONE"

    operation_resp = client.post(
        f"{BASE}/{package_id}/filing-preparation/external-operations",
        headers=auth_headers,
        json={
            "operation_code": "CNIPA_IMPORT_STARTED",
            "occurred_at": "2026-05-31T14:30:00",
            "note": "专利业务办理系统导入请求类表格",
        },
    )
    assert operation_resp.status_code == 200, operation_resp.text
    operation_item = operation_resp.json()["checklist_item"]
    assert operation_item["status"] == "DONE"
    assert "2026-05-31T14:30:00" in operation_item["evidence_note"]

    get_resp = client.get(f"{BASE}/{package_id}/filing-preparation", headers=auth_headers)
    assert get_resp.status_code == 200, get_resp.text
    get_body = get_resp.json()
    checklist = {item["item_code"]: item for item in get_body["official_page_checklist"]}
    assert checklist["PREVIEW_CONFIRMED"]["status"] == "DONE"
    assert checklist["CNIPA_IMPORT_STARTED"]["status"] == "DONE"

    with session_factory() as db:
        manifests = (
            db.execute(
                select(OfficialWorkPackageManifest).where(
                    OfficialWorkPackageManifest.package_id == package_id
                )
            )
            .scalars()
            .all()
        )
        assert {item.official_file_role for item in manifests} >= {
            "TECHNICAL_DISCLOSURE",
            "COMMISSION_INSTRUCTION",
            "FILING_XML_ZIP",
            "FILING_MERGED_PDF",
        }
        checklist_rows = (
            db.execute(
                select(OfficialWorkPackageChecklist).where(
                    OfficialWorkPackageChecklist.package_id == package_id
                )
            )
            .scalars()
            .all()
        )
        assert {item.item_code for item in checklist_rows} >= {
            "PREVIEW_CONFIRMED",
            "CNIPA_IMPORT_STARTED",
        }


def test_filing_package_read_rejects_non_filing_package(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    package_id, case_id = _create_filing_fixture(session_factory)
    with session_factory() as db:
        package = db.execute(
            select(OfficialWorkPackage).where(OfficialWorkPackage.id == package_id)
        ).scalar_one()
        package.package_kind = "OA_REPLY"
        db.commit()

    response = client.get(f"{BASE}/{package_id}/filing-preparation", headers=auth_headers)

    assert response.status_code == 400, response.text
    assert response.json()["error"]["code"] == "OFFICIAL_WORK_PACKAGE_KIND_INVALID"
    assert case_id
