from __future__ import annotations

import json
from datetime import date
from decimal import Decimal
import os
from pathlib import Path
import sys

from sqlalchemy import select

REPO_ROOT = Path(__file__).resolve().parents[4]
BACKEND_ROOT = REPO_ROOT / "backend"
os.chdir(BACKEND_ROOT)
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.core.config import get_settings  # noqa: E402
from app.modules.annuity.models import AnnuityTask, GovPayment, PayList  # noqa: E402
from app.modules.auth.models import T_User  # noqa: E402,F401
from app.modules.cases.models import Case, T_CaseApplicant, T_CaseInventor  # noqa: E402
from app.modules.documents.models import (  # noqa: E402
    DocAttachment,
    DocTemplate,
    Document,
    LetterHandoff,
    LetterHandoffAttachment,
)
from app.modules.fees.models import FeeDraft, FeeItem, OfficialFeeChecklist  # noqa: E402
from app.modules.fees.models import T_GrantFeeTask  # noqa: E402
from app.modules.masterdata.applicants.models import Applicant  # noqa: E402
from app.modules.masterdata.clients.models import Client, ClientContact  # noqa: E402
from app.modules.official_workflows.models import (  # noqa: E402
    OfficialWorkPackage,
    OfficialWorkPackageChecklist,
    OfficialWorkPackageManifest,
    OfficialWorkPackageOverride,
    OfficialWorkPackageReceipt,
)
from app.modules.tasks.models import Task  # noqa: E402
from app.modules.templates.models import FormatLetterMapping, Template  # noqa: E402

CASE_ID = "CASE-PD-P1-LIVE"
CASE_NO = "P1E2E-LIVE"
CLIENT_ID = "CLIENT-PD-P1-LIVE"
CONTACT_ID = "CONTACT-PD-P1-LIVE"
APPLICANT_MASTER_ID = "APP-PD-P1-LIVE-1"

FILING_DOCUMENT_ID = "DOC-FILING-PD-P1-LIVE"
SOURCE_OA_DOCUMENT_ID = "DOC-OA-IN-PD-P1-LIVE"
REPLY_DOCUMENT_ID = "DOC-OA-OUT-PD-P1-LIVE"
LETTER_DOCUMENT_ID = "DOC-LETTER-PD-P1-LIVE"
GRANT_DOCUMENT_ID = "DOC-GRANT-PD-P1-LIVE"

FILING_PACKAGE_ID = "FILING-PD-P1-LIVE"
OA_PACKAGE_ID = "OA-PD-P1-LIVE"

FEE_DRAFT_ID = "FD-PD-P1-LIVE"
FEE_ITEM_ID = "FI-PD-P1-LIVE-GOV"
PAY_LIST_ID = 860612

FORMAT_DOC_TEMPLATE_CODE = "FORMAT_LETTER_OA1"
FORMAT_TEMPLATE_ID = "TPL-PD-P1-LIVE-FMT"
FORMAT_MAPPING_ID = "MAP-PD-P1-LIVE-FMT"

ATTACHMENTS = {
    "technical_disclosure": "ATT-PD-P1-LIVE-TECH",
    "filing_zip": "ATT-PD-P1-LIVE-ZIP",
    "oa_statement_word": "ATT-PD-P1-LIVE-STMT-WORD",
    "oa_statement_pdf": "ATT-PD-P1-LIVE-STMT-PDF",
    "oa_modified_claims": "ATT-PD-P1-LIVE-CLAIMS",
    "oa_comparison": "ATT-PD-P1-LIVE-COMPARE",
    "oa_experiment": "ATT-PD-P1-LIVE-EXPER",
    "oa_receipt": "ATT-PD-P1-LIVE-RECEIPT",
    "letter_pdf": "ATT-PD-P1-LIVE-LETTER-PDF",
}

SAFE_FPMS_ENVS = {"dev", "development", "local", "test", "demo"}


def main() -> None:
    assert_safe_demo_environment()
    from app.db.session import SessionLocal  # noqa: PLC0415

    db = SessionLocal()
    try:
        clear_fixture(db)
        seed_fixture(db)
        db.commit()
        print(
            json.dumps(
                {
                    "caseId": CASE_ID,
                    "caseNo": CASE_NO,
                    "clientId": CLIENT_ID,
                    "filingPackageId": FILING_PACKAGE_ID,
                    "feeDraftId": FEE_DRAFT_ID,
                    "payListId": PAY_LIST_ID,
                    "oaPackageId": OA_PACKAGE_ID,
                    "sourceOaDocumentId": SOURCE_OA_DOCUMENT_ID,
                    "replyDocumentId": REPLY_DOCUMENT_ID,
                    "receiptAttachmentId": ATTACHMENTS["oa_receipt"],
                    "letterDocumentId": LETTER_DOCUMENT_ID,
                    "grantDocumentId": GRANT_DOCUMENT_ID,
                },
                ensure_ascii=False,
                sort_keys=True,
            )
        )
    finally:
        db.close()


def assert_safe_demo_environment() -> None:
    settings = get_settings()
    env = (settings.fpms_env or "").strip().lower()
    database_url = (settings.database_url or "").strip().lower()
    if env not in SAFE_FPMS_ENVS:
        raise RuntimeError(
            f"P1 demo seed is blocked for FPMS_ENV={settings.fpms_env!r}; "
            f"allowed values are {sorted(SAFE_FPMS_ENVS)}."
        )
    if not database_url.startswith("sqlite"):
        raise RuntimeError("P1 demo seed is blocked for non-SQLite DATABASE_URL.")


def clear_fixture(db) -> None:
    document_ids = [
        FILING_DOCUMENT_ID,
        SOURCE_OA_DOCUMENT_ID,
        REPLY_DOCUMENT_ID,
        LETTER_DOCUMENT_ID,
        GRANT_DOCUMENT_ID,
    ]
    package_ids = [FILING_PACKAGE_ID, OA_PACKAGE_ID]

    handoff_ids = list(
        db.execute(
            select(LetterHandoff.id).where(LetterHandoff.source_document_id.in_(document_ids))
        ).scalars()
    )
    if handoff_ids:
        db.query(LetterHandoffAttachment).filter(
            LetterHandoffAttachment.handoff_id.in_(handoff_ids)
        ).delete(synchronize_session=False)
        db.query(LetterHandoff).filter(LetterHandoff.id.in_(handoff_ids)).delete(
            synchronize_session=False
        )

    db.query(OfficialWorkPackageReceipt).filter(
        OfficialWorkPackageReceipt.package_id.in_(package_ids)
    ).delete(synchronize_session=False)
    db.query(OfficialWorkPackageOverride).filter(
        OfficialWorkPackageOverride.package_id.in_(package_ids)
    ).delete(synchronize_session=False)
    db.query(OfficialWorkPackageChecklist).filter(
        OfficialWorkPackageChecklist.package_id.in_(package_ids)
    ).delete(synchronize_session=False)
    db.query(OfficialWorkPackageManifest).filter(
        OfficialWorkPackageManifest.package_id.in_(package_ids)
    ).delete(synchronize_session=False)
    db.query(OfficialWorkPackage).filter(OfficialWorkPackage.id.in_(package_ids)).delete(
        synchronize_session=False
    )

    demo_fee_draft_ids = list(
        db.execute(select(FeeDraft.id).where(FeeDraft.case_id == CASE_ID)).scalars()
    )
    if FEE_DRAFT_ID not in demo_fee_draft_ids:
        demo_fee_draft_ids.append(FEE_DRAFT_ID)

    demo_fee_item_ids = (
        list(
            db.execute(
                select(FeeItem.id).where(FeeItem.draft_id.in_(demo_fee_draft_ids))
            ).scalars()
        )
        if demo_fee_draft_ids
        else []
    )

    demo_pay_list_ids = {PAY_LIST_ID}
    demo_pay_list_ids.update(
        db.execute(select(GovPayment.pay_list_id).where(GovPayment.case_id == CASE_ID)).scalars()
    )
    if demo_fee_item_ids:
        demo_pay_list_ids.update(
            db.execute(
                select(GovPayment.pay_list_id).where(GovPayment.fee_item_id.in_(demo_fee_item_ids))
            ).scalars()
        )
    demo_pay_list_id_list = sorted(demo_pay_list_ids)
    assert_demo_pay_lists_are_exclusive(db, demo_pay_list_id_list, demo_fee_item_ids)

    if demo_fee_draft_ids:
        db.query(OfficialFeeChecklist).filter(
            OfficialFeeChecklist.fee_draft_id.in_(demo_fee_draft_ids)
        ).delete(synchronize_session=False)
    db.query(OfficialFeeChecklist).filter(
        OfficialFeeChecklist.pay_list_id.in_(demo_pay_list_id_list)
    ).delete(synchronize_session=False)
    db.query(GovPayment).filter(GovPayment.pay_list_id.in_(demo_pay_list_id_list)).delete(
        synchronize_session=False
    )
    db.query(GovPayment).filter(GovPayment.case_id == CASE_ID).delete(synchronize_session=False)
    if demo_fee_item_ids:
        db.query(GovPayment).filter(GovPayment.fee_item_id.in_(demo_fee_item_ids)).delete(
            synchronize_session=False
        )
    db.query(PayList).filter(PayList.id.in_(demo_pay_list_id_list)).delete(
        synchronize_session=False
    )
    if demo_fee_draft_ids:
        db.query(FeeItem).filter(FeeItem.draft_id.in_(demo_fee_draft_ids)).delete(
            synchronize_session=False
        )
        db.query(FeeDraft).filter(FeeDraft.id.in_(demo_fee_draft_ids)).delete(
            synchronize_session=False
        )
    db.query(AnnuityTask).filter(AnnuityTask.case_id == CASE_ID).delete(
        synchronize_session=False
    )
    db.query(T_GrantFeeTask).filter(T_GrantFeeTask.case_id == CASE_ID).delete(
        synchronize_session=False
    )

    db.query(Task).filter(Task.document_id.in_(document_ids)).delete(synchronize_session=False)
    db.query(DocAttachment).filter(DocAttachment.document_id.in_(document_ids)).delete(
        synchronize_session=False
    )
    db.query(Document).filter(Document.id.in_(document_ids)).delete(synchronize_session=False)
    db.query(T_CaseApplicant).filter(T_CaseApplicant.case_id == CASE_ID).delete(
        synchronize_session=False
    )
    db.query(T_CaseInventor).filter(T_CaseInventor.case_id == CASE_ID).delete(
        synchronize_session=False
    )
    db.query(Case).filter(Case.id == CASE_ID).delete(synchronize_session=False)
    db.query(Applicant).filter(Applicant.id == APPLICANT_MASTER_ID).delete(
        synchronize_session=False
    )
    db.query(FormatLetterMapping).filter(FormatLetterMapping.id == FORMAT_MAPPING_ID).delete(
        synchronize_session=False
    )
    db.query(Template).filter(Template.id == FORMAT_TEMPLATE_ID).delete(synchronize_session=False)
    db.query(ClientContact).filter(ClientContact.id == CONTACT_ID).delete(
        synchronize_session=False
    )
    db.query(Client).filter(Client.id == CLIENT_ID).delete(synchronize_session=False)
    db.commit()


def assert_demo_pay_lists_are_exclusive(
    db,
    pay_list_ids: list[int],
    demo_fee_item_ids: list[str],
) -> None:
    if not pay_list_ids:
        return

    demo_fee_item_id_set = set(demo_fee_item_ids)
    mixed_rows = db.execute(
        select(GovPayment.pay_list_id, GovPayment.case_id, GovPayment.fee_item_id).where(
            GovPayment.pay_list_id.in_(pay_list_ids)
        )
    ).all()
    unsafe_rows = [
        row
        for row in mixed_rows
        if row.case_id != CASE_ID and row.fee_item_id not in demo_fee_item_id_set
    ]
    if unsafe_rows:
        details = ", ".join(
            f"pay_list_id={row.pay_list_id}, case_id={row.case_id}, fee_item_id={row.fee_item_id}"
            for row in unsafe_rows[:5]
        )
        raise RuntimeError(
            "P1 demo seed refused to delete a pay-list containing non-demo payment rows: "
            f"{details}"
        )


def seed_fixture(db) -> None:
    client = Client(
        id=CLIENT_ID,
        client_code="PD-P1-LIVE",
        name_cn="P1全流程客户有限公司",
        name_en=None,
        email="p1-live@example.com",
        client_type="CORP",
        default_currency="CNY",
        is_active=True,
    )
    db.add(client)
    db.flush()
    db.add(
        ClientContact(
            id=CONTACT_ID,
            client_id=CLIENT_ID,
            contact_name="张三",
            title="老师",
            phone=None,
            mobile="13800000000",
            email="zhangsan@example.com",
            is_primary=True,
        )
    )

    db.add(
        Applicant(
            id=APPLICANT_MASTER_ID,
            code="AA-PD-P1-LIVE-1",
            name_cn="P1测试申请人有限公司",
            name_en=None,
            total_power_of_attorney_no="总委备-P1-LIVE-001",
            applicant_type="ENTITY",
            is_active=True,
        )
    )
    db.add(
        Case(
            id=CASE_ID,
            case_no=CASE_NO,
            case_type="NORMAL",
            patent_category="INV",
            flow_dir="CN_DOMESTIC",
            client_id=CLIENT_ID,
            title_cn="P1全流程测试方法及系统",
            app_no="CN202610000001.0",
            status="NOT_FILED",
            recv_date=date(2026, 6, 2),
            filing_date=date(2026, 6, 2),
            spec_pages=18,
            draw_pages=3,
            claim_count=10,
            claim_pages=4,
            has_exam_request=True,
            fee_reduction="0.85",
            discount_rate=Decimal("0.8500"),
            applicant_kind="企业",
            primary_agent_id="AGENT-PD-P1",
            draftor_id="DRAFTOR-PD-P1",
        )
    )
    db.flush()
    db.add(
        T_CaseApplicant(
            id="APPL-PD-P1-LIVE-1",
            case_id=CASE_ID,
            applicant_id=APPLICANT_MASTER_ID,
            seq=1,
            is_first=True,
            name_cn="P1测试申请人有限公司",
            address_cn="北京市海淀区测试路1号",
            nationality="CN",
            certificate_type="统一社会信用代码",
            certificate_no="91110000P1E2E0000X",
            official_postcode=None,
            official_applicant_kind="企业",
        )
    )
    db.add(
        T_CaseInventor(
            id="INV-PD-P1-LIVE-1",
            case_id=CASE_ID,
            seq=1,
            name_cn="李四",
            nationality="CN",
            china_id_no="110101199001011234",
        )
    )

    client_in_template = ensure_doc_template(db, "CLIENT_IN", "客户来函", "IN")
    oa_in_template = ensure_doc_template(db, "OA_IN", "审查意见通知书（收文）", "IN")
    oa_out_template = ensure_doc_template(db, "OA_OUT", "审查意见答复书（发文）", "OUT")
    grant_notice_template = ensure_doc_template(db, "GRANT_NOTICE", "授权通知书", "IN")
    grant_notice_template.status_effect = "GRANT_PENDING"
    grant_notice_template.fee_draft_type = "GRANT_FEE"
    letter_doc_template = ensure_doc_template(
        db,
        FORMAT_DOC_TEMPLATE_CODE,
        "第一次审查意见通知书格式函",
        "OUT",
    )

    db.add(
        Template(
            id=FORMAT_TEMPLATE_ID,
            name="FORMAT_LETTER_OA1",
            group="LETTER",
            language="zh-CN",
            file_path="templates/format-letter-oa1.docx",
            enabled=True,
        )
    )
    db.flush()
    db.add(
        FormatLetterMapping(
            id=FORMAT_MAPPING_ID,
            official_doc_template_id=letter_doc_template.id,
            official_doc_template_code=FORMAT_DOC_TEMPLATE_CODE,
            official_doc_name_pattern="第一次审查意见通知书",
            format_letter_template_id=FORMAT_TEMPLATE_ID,
            format_letter_template_code="FORMAT_LETTER_OA1",
            output_name_rule="{case_no}-一通格式函.docx",
            salutation_rule_code="PRIMARY_CONTACT_TITLE",
            contact_rule_code="CLIENT_PRIMARY_CONTACT",
            enabled=True,
            remark="P1 live E2E format-letter mapping",
        )
    )

    db.add(
        Document(
            id=FILING_DOCUMENT_ID,
            case_id=CASE_ID,
            doc_template_id=client_in_template.id,
            doc_type="CLIENT_IN",
            direction="IN",
            doc_date=date(2026, 6, 2),
            title="客户新申请材料",
            ref_no="FILING-P1-LIVE",
            extra_data=json.dumps({"source": "post-demo P1 live E2E"}, ensure_ascii=False),
        )
    )
    db.add(
        Document(
            id=SOURCE_OA_DOCUMENT_ID,
            case_id=CASE_ID,
            doc_template_id=oa_in_template.id,
            doc_type="OFFICIAL_IN",
            direction="IN",
            doc_date=date(2026, 5, 20),
            title="第一次审查意见通知书",
            ref_no="OA-1",
            extra_data=json.dumps(
                {
                    "official_notice_code": "OA-1",
                    "official_notice_name": "第一次审查意见通知书",
                    "issue_sequence": "一通",
                    "issue_date": "2026-05-20",
                    "official_due_date": "2026-08-20",
                },
                ensure_ascii=False,
            ),
            need_reply=True,
        )
    )
    db.add(
        Document(
            id=REPLY_DOCUMENT_ID,
            case_id=CASE_ID,
            doc_template_id=oa_out_template.id,
            doc_type="OFFICIAL_OUT",
            direction="OUT",
            doc_date=date(2026, 6, 2),
            title="第一次审查意见答复",
            ref_no="OA-OUT-1",
            extra_data=json.dumps(
                {
                    "reply_statement_text": "详见随附 PDF 意见陈述书。",
                    "experiment_data_submitted": True,
                },
                ensure_ascii=False,
            ),
            reply_to_id=SOURCE_OA_DOCUMENT_ID,
            need_reply=False,
            reply_date=date(2026, 6, 2),
        )
    )
    db.add(
        Document(
            id=LETTER_DOCUMENT_ID,
            case_id=CASE_ID,
            doc_template_id=letter_doc_template.id,
            doc_type="CLIENT_OUT",
            direction="OUT",
            doc_date=date(2026, 6, 2),
            title="第一次审查意见通知书",
            ref_no="LETTER-OA1",
            extra_data="格式函交接预览，供龙虾邮件流程使用。",
            reply_to_id=SOURCE_OA_DOCUMENT_ID,
            need_reply=False,
            reply_date=date(2026, 6, 2),
        )
    )
    db.add(
        Document(
            id=GRANT_DOCUMENT_ID,
            case_id=CASE_ID,
            doc_template_id=grant_notice_template.id,
            doc_type="OFFICIAL_IN",
            direction="IN",
            doc_date=date(2027, 3, 15),
            title="授权通知书-电子",
            ref_no="GRANT-PD-P1-LIVE",
            extra_data=json.dumps(
                {
                    "official_notice_code": "GRANT_NOTICE",
                    "official_notice_name": "授权通知书",
                    "issue_date": "2027-03-15",
                },
                ensure_ascii=False,
            ),
            need_reply=False,
        )
    )
    db.flush()

    add_attachment(
        db,
        ATTACHMENTS["technical_disclosure"],
        FILING_DOCUMENT_ID,
        "技术交底书.docx",
        "TECHNICAL_DISCLOSURE",
        "新建案件 gate：技术交底书必传",
    )
    add_attachment(
        db,
        ATTACHMENTS["filing_zip"],
        FILING_DOCUMENT_ID,
        "请求类表格.zip",
        "FILING_XML_ZIP",
        "专利业务办理系统导入准备文件",
        mime_type="application/zip",
    )
    add_attachment(
        db,
        ATTACHMENTS["oa_statement_word"],
        REPLY_DOCUMENT_ID,
        "意见陈述书.docx",
        "OA_STATEMENT_WORD",
        "陈述的意见",
    )
    add_attachment(
        db,
        ATTACHMENTS["oa_statement_pdf"],
        REPLY_DOCUMENT_ID,
        "意见陈述书.pdf",
        "OA_STATEMENT_PDF",
        "附加文件：意见陈述书PDF",
        mime_type="application/pdf",
    )
    add_attachment(
        db,
        ATTACHMENTS["oa_modified_claims"],
        REPLY_DOCUMENT_ID,
        "修改后的权利要求书.docx",
        "OA_MODIFIED_CLAIMS",
        "权利要求书",
    )
    add_attachment(
        db,
        ATTACHMENTS["oa_comparison"],
        REPLY_DOCUMENT_ID,
        "修改对照页.pdf",
        "OA_AMENDMENT_COMPARISON",
        "附加文件：修改对照页",
        mime_type="application/pdf",
    )
    add_attachment(
        db,
        ATTACHMENTS["oa_experiment"],
        REPLY_DOCUMENT_ID,
        "实验数据.pdf",
        "OA_OTHER_PROOF",
        "附加文件：其他证明文件",
        mime_type="application/pdf",
    )
    add_attachment(
        db,
        ATTACHMENTS["oa_receipt"],
        REPLY_DOCUMENT_ID,
        "电子申请回执.pdf",
        "ELECTRONIC_RECEIPT",
        "回执归档",
        mime_type="application/pdf",
        package_usage_hint="RECEIPT_ARCHIVE",
    )
    add_attachment(
        db,
        ATTACHMENTS["letter_pdf"],
        LETTER_DOCUMENT_ID,
        "第一次审查意见通知书.pdf",
        "SOURCE_DOCUMENT",
        "信函交接附件清单",
        mime_type="application/pdf",
    )

    seed_filing_work_package(db)
    seed_oa_work_package(db)
    seed_fees(db)
    seed_task(db)


def ensure_doc_template(db, code: str, name: str, direction: str) -> DocTemplate:
    template = db.execute(select(DocTemplate).where(DocTemplate.code == code)).scalar_one_or_none()
    if template:
        return template
    template = DocTemplate(
        id=f"DTPL-{code}"[:36],
        code=code,
        name=name,
        direction=direction,
        enabled=True,
        need_reply=code == "OA_IN",
        reply_to_template_code="OA_IN" if code == "OA_OUT" else None,
    )
    db.add(template)
    db.flush()
    return template


def add_attachment(
    db,
    attachment_id: str,
    document_id: str,
    file_name: str,
    role: str,
    external_position: str,
    *,
    mime_type: str = "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    package_usage_hint: str | None = None,
) -> None:
    db.add(
        DocAttachment(
            id=attachment_id,
            document_id=document_id,
            file_name=file_name,
            file_path=f"test-fixtures/pd-p1-live/{file_name}",
            mime_type=mime_type,
            file_size=1024,
            official_file_role=role,
            source_role_alias=file_name,
            external_upload_position=external_position,
            content_hash=f"sha256-{attachment_id.lower()}",
            package_usage_hint=package_usage_hint,
            is_archive_evidence=False,
            is_receipt_evidence=False,
        )
    )


def seed_filing_work_package(db) -> None:
    db.add(
        OfficialWorkPackage(
            id=FILING_PACKAGE_ID,
            case_id=CASE_ID,
            package_kind="FILING_PREP",
            status="NEEDS_MAINTENANCE",
            external_system="CNIPA_WEB",
            remark="P1 live E2E filing workflow fixture",
        )
    )
    manifests = [
        (
            "MAN-PD-P1-LIVE-TECH",
            ATTACHMENTS["technical_disclosure"],
            "TECHNICAL_DISCLOSURE",
            "技术交底书",
            "新建案件 gate：技术交底书必传",
            True,
            True,
            10,
        ),
        (
            "MAN-PD-P1-LIVE-COMM",
            None,
            "COMMISSION_INSTRUCTION",
            "委托指示（如有）",
            "客户反馈为如有，不作为固定必传",
            False,
            False,
            20,
        ),
        (
            "MAN-PD-P1-LIVE-ZIP",
            ATTACHMENTS["filing_zip"],
            "FILING_XML_ZIP",
            "XML zip",
            "为专利业务办理系统导入做准备",
            True,
            True,
            30,
        ),
        (
            "MAN-PD-P1-LIVE-PDF",
            None,
            "FILING_MERGED_PDF",
            "合并 PDF",
            "官方提交后人工下载并归档",
            False,
            False,
            40,
        ),
    ]
    for (
        manifest_id,
        attachment_id,
        role,
        alias,
        note,
        required,
        present,
        sort_order,
    ) in manifests:
        db.add(
            OfficialWorkPackageManifest(
                id=manifest_id,
                package_id=FILING_PACKAGE_ID,
                attachment_id=attachment_id,
                official_file_role=role,
                source_role_alias=alias,
                external_upload_position="官方页面对应位置" if present else None,
                content_hash=f"sha256-{role.lower()}" if present else None,
                required=required,
                present=present,
                sort_order=sort_order,
                note=note,
            )
        )

    for checklist_id, code, label, status, order in [
        ("CHK-PD-P1-LIVE-FORM", "CNIPA_FORM_IMPORTED", "接收类表格导入", "PENDING", 10),
        ("CHK-PD-P1-LIVE-PREV", "PREVIEW_CONFIRMED", "官方页面预览", "PENDING", 20),
        ("CHK-PD-P1-LIVE-SIGN", "SIGNATURE_CONFIRMED", "签名和递交责任", "PENDING", 30),
    ]:
        db.add(
            OfficialWorkPackageChecklist(
                id=checklist_id,
                package_id=FILING_PACKAGE_ID,
                section_code="FILING_PAGE",
                item_code=code,
                item_label=label,
                status=status,
                required=True,
                sort_order=order,
            )
        )


def seed_oa_work_package(db) -> None:
    db.add(
        OfficialWorkPackage(
            id=OA_PACKAGE_ID,
            case_id=CASE_ID,
            package_kind="OA_REPLY",
            status="WAITING_RECEIPT",
            source_document_id=SOURCE_OA_DOCUMENT_ID,
            reply_document_id=REPLY_DOCUMENT_ID,
            external_system="CNIPA_WEB",
            remark="P1 live E2E OA reply fixture",
        )
    )

    manifests = [
        (
            "MAN-PD-P1-LIVE-STMT-W",
            ATTACHMENTS["oa_statement_word"],
            "OA_STATEMENT_WORD",
            "意见陈述书.docx",
            "意见陈述正文来源",
            True,
            True,
            10,
        ),
        (
            "MAN-PD-P1-LIVE-STMT-P",
            ATTACHMENTS["oa_statement_pdf"],
            "OA_STATEMENT_PDF",
            "意见陈述书.pdf",
            "公式/表格/图片保真附件",
            True,
            True,
            20,
        ),
        (
            "MAN-PD-P1-LIVE-CLAIM",
            ATTACHMENTS["oa_modified_claims"],
            "OA_MODIFIED_CLAIMS",
            "修改后的权利要求书.docx",
            "主要修改文件",
            True,
            True,
            30,
        ),
        (
            "MAN-PD-P1-LIVE-COMP",
            ATTACHMENTS["oa_comparison"],
            "OA_AMENDMENT_COMPARISON",
            "修改对照页.pdf",
            "官方附加文件",
            False,
            True,
            40,
        ),
        (
            "MAN-PD-P1-LIVE-PROOF",
            ATTACHMENTS["oa_experiment"],
            "OA_OTHER_PROOF",
            "实验数据.pdf",
            "按需补交实验数据",
            False,
            True,
            50,
        ),
    ]
    for (
        manifest_id,
        attachment_id,
        role,
        alias,
        note,
        required,
        present,
        sort_order,
    ) in manifests:
        db.add(
            OfficialWorkPackageManifest(
                id=manifest_id,
                package_id=OA_PACKAGE_ID,
                attachment_id=attachment_id,
                official_file_role=role,
                source_role_alias=alias,
                external_upload_position="官方页面对应位置",
                content_hash=f"sha256-{role.lower()}",
                required=required,
                present=present,
                sort_order=sort_order,
                note=note,
            )
        )

    checklist_rows = [
        ("CHK-PD-P1-LIVE-CLOUD", "OA_PAGE", "CLOUD_SECOND_DOWNLOAD_CONFIRMED", "云端二次下载", "PENDING", 10, None),
        ("CHK-PD-P1-LIVE-QUERY", "OA_PAGE", "QUERY_RESULT_CONFIRMED", "查询结果", "DONE", 20, "已核对申请号、官文代码和期限"),
        ("CHK-PD-P1-LIVE-HANDLE", "OA_PAGE", "BUSINESS_HANDLING_CONFIRMED", "业务办理", "DONE", 30, "已进入OA答复办理页面"),
        ("CHK-PD-P1-LIVE-STMT", "OA_REPLY", "STATEMENT_TEXT_CONFIRMED", "陈述意见文本已确认", "DONE", 35, "意见陈述文本已核对"),
        ("CHK-PD-P1-LIVE-PDF", "OA_REPLY", "PDF_FIDELITY_CONFIRMED", "PDF 保真附件已确认", "DONE", 36, "PDF 附件用于公式/表格/图片保真"),
        ("CHK-PD-P1-LIVE-MOD", "OA_REPLY", "MODIFIED_CLAIMS_CONFIRMED", "修改文件已确认", "DONE", 37, "权利要求书修改文件已核对"),
        ("CHK-PD-P1-LIVE-EXP", "OA_REPLY", "EXPERIMENT_DATA_FLAG_CONFIRMED", "补交实验数据勾选已确认", "DONE", 38, "补交实验数据：是"),
        ("CHK-PD-P1-LIVE-OA-PREV", "OA_PAGE", "PREVIEW_TABS_CONFIRMED", "预览标签页", "PENDING", 40, None),
        ("CHK-PD-P1-LIVE-OA-SIGN", "OA_PAGE", "SIGNATURE_CONFIRMED", "签名确认", "DONE", 50, "签名/提交由人工完成"),
        ("CHK-PD-P1-LIVE-SUB", "OA_PAGE", "SUBMISSION_CONFIRMED", "提交确认", "PENDING", 60, None),
        ("CHK-PD-P1-LIVE-REC", "OA_PAGE", "RECEIPT_CONFIRMED", "回执归档", "PENDING", 70, None),
    ]
    for checklist_id, section, code, label, status, order, note in checklist_rows:
        db.add(
            OfficialWorkPackageChecklist(
                id=checklist_id,
                package_id=OA_PACKAGE_ID,
                section_code=section,
                item_code=code,
                item_label=label,
                status=status,
                required=True,
                sort_order=order,
                evidence_note=note,
            )
        )


def seed_fees(db) -> None:
    db.add(
        FeeDraft(
            id=FEE_DRAFT_ID,
            case_id=CASE_ID,
            client_id=CLIENT_ID,
            draft_type="APPLY_FEE",
            currency="CNY",
            status="OPEN",
            total_gov=Decimal("950.00"),
            total_service=Decimal("3000.00"),
            total_misc=Decimal("0.00"),
            amount=Decimal("3950.00"),
            official_fee_reduction_note="客户已确认旧系统数值为减免比例，系统转换为官方应缴比例。",
            official_template_status="UNCONFIRMED",
            official_template_note="补充缴费信息模板字段待确认",
        )
    )
    db.add(
        FeeItem(
            id=FEE_ITEM_ID,
            draft_id=FEE_DRAFT_ID,
            case_id=CASE_ID,
            fee_code="APPLY_FEE",
            fee_name="申请费",
            fee_type="GOV",
            quantity=Decimal("1"),
            unit_price=Decimal("950.00"),
            amount=Decimal("950.00"),
            remark="申请费",
        )
    )
    db.add(
        PayList(
            id=PAY_LIST_ID,
            client_id=CLIENT_ID,
            pay_list_no="PL-PD-P1-LIVE",
            status="EXPORTED",
            currency="CNY",
            planned_pay_date=date(2026, 6, 5),
            total_amount=Decimal("950.00"),
            remark="补充缴费信息模板字段待确认；内部清单不等同官方 Excel。",
            official_upload_template_status="UNCONFIRMED",
            official_upload_template_name="补充缴费信息模板",
            official_upload_batch_limit=500,
            official_pay_list_boundary_note="内部 pay-list 不是官方上传 Excel；需客户提供官方模板样例后再生成。",
        )
    )
    db.flush()
    db.add(
        GovPayment(
            pay_list_id=PAY_LIST_ID,
            case_id=CASE_ID,
            fee_item_id=FEE_ITEM_ID,
            status="PENDING",
            currency="CNY",
            paid_amount=Decimal("950.00"),
            remark="人工官方缴费后登记",
        )
    )
    db.add(
        OfficialFeeChecklist(
            id="OFCHK-PD-P1-LIVE-RATE",
            fee_draft_id=FEE_DRAFT_ID,
            checklist_code="FEE_RATE_SOURCE_READABLE",
            checklist_label="官方费率来源",
            status="NEEDS_CONFIRMATION",
            required=True,
            blocker_reason="官方费率 / 费减清单来源待确认",
            sort_order=10,
        )
    )
    db.add(
        OfficialFeeChecklist(
            id="OFCHK-PD-P1-LIVE-TPL",
            pay_list_id=PAY_LIST_ID,
            checklist_code="OFFICIAL_EXCEL_TEMPLATE",
            checklist_label="补充缴费信息模板",
            status="NEEDS_CONFIRMATION",
            required=True,
            blocker_reason="补充缴费信息模板字段待确认",
            sort_order=20,
        )
    )


def seed_task(db) -> None:
    db.add(
        Task(
            id="TASK-PD-P1-LIVE-OA",
            case_id=CASE_ID,
            document_id=SOURCE_OA_DOCUMENT_ID,
            title="第一次审查意见答复期限",
            base_date=date(2026, 5, 20),
            due_date=date(2026, 8, 20),
            internal_due_date=date(2026, 8, 13),
            status="OPEN",
        )
    )


if __name__ == "__main__":
    main()
