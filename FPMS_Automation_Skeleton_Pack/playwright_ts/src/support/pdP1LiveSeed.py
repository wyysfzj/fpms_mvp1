from __future__ import annotations

import json
import os
import sys
from datetime import date
from decimal import Decimal
from pathlib import Path

from sqlalchemy import select, text

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
from app.modules.fees.models import (  # noqa: E402
    FeeDraft,
    FeeItem,
    FeeRate,
    OfficialFeeChecklist,
    T_GrantFeeTask,  # noqa: E402
)
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
FEE_ITEM_ID = "FI-PD-P1-LIVE-GOV-APP"
FEE_PUBLICATION_ITEM_ID = "FI-PD-P1-LIVE-GOV-PUB"
FEE_EXAM_ITEM_ID = "FI-PD-P1-LIVE-GOV-EXAM"
PAY_LIST_ID = 860612
GRANT_FEE_TASK_ID = "GFT-PD-P1-LIVE"
ANNUITY_TASK_ID_YEAR_2 = 870201
ANNUITY_TASK_ID_YEAR_3 = 870202

V5_CASE_ID = "CASE-PD-P1-V5-LIVE"
V5_CASE_NO = "P1E2E-V5-LIVE"
V5_CLIENT_ID = "CLIENT-PD-P1-V5-LIVE"
V5_CONTACT_ID = "CONTACT-PD-P1-V5-LIVE"
V5_APPLICANT_MASTER_ID = "APP-PD-P1-V5-LIVE-1"

V5_FILING_DOCUMENT_ID = "DOC-FILING-PD-P1-V5-LIVE"
V5_SOURCE_OA_DOCUMENT_ID = "DOC-OA-IN-PD-P1-V5-LIVE"
V5_REPLY_DOCUMENT_ID = "DOC-OA-OUT-PD-P1-V5-LIVE"
V5_LETTER_DOCUMENT_ID = "DOC-LETTER-PD-P1-V5-LIVE"
V5_GRANT_DOCUMENT_ID = "DOC-GRANT-PD-P1-V5-LIVE"

V5_FILING_PACKAGE_ID = "FILING-PD-P1-V5-LIVE"
V5_OA_PACKAGE_ID = "OA-PD-P1-V5-LIVE"

V5_FEE_DRAFT_ID = "FD-PD-P1-V5-LIVE"
V5_PAY_LIST_ID = 860622
V5_GRANT_FEE_TASK_ID = "GFT-PD-P1-V5-LIVE"
V5_ANNUITY_TASK_ID_YEAR_2 = 870501
V5_ANNUITY_TASK_ID_YEAR_3 = 870502

V6_CASE_NO = "P1E2E-V6-LIVE"
V6_CLIENT_CODE = "PD-P1-V6-LIVE"

V6_FILING_DOCUMENT_ID = "DOC-FILING-PD-P1-V6-LIVE"
V6_SOURCE_OA_DOCUMENT_ID = "DOC-OA-IN-PD-P1-V6-LIVE"
V6_REPLY_DOCUMENT_ID = "DOC-OA-OUT-PD-P1-V6-LIVE"
V6_LETTER_DOCUMENT_ID = "DOC-LETTER-PD-P1-V6-LIVE"
V6_GRANT_DOCUMENT_ID = "DOC-GRANT-PD-P1-V6-LIVE"

V6_FILING_PACKAGE_ID = "FILING-PD-P1-V6-LIVE"
V6_OA_PACKAGE_ID = "OA-PD-P1-V6-LIVE"

V6_FEE_DRAFT_ID = "FD-PD-P1-V6-LIVE"
V6_PAY_LIST_ID = 860632
V6_GRANT_FEE_TASK_ID = "GFT-PD-P1-V6-LIVE"
V6_ANNUITY_TASK_ID_YEAR_2 = 870601
V6_ANNUITY_TASK_ID_YEAR_3 = 870602

FEE_RATE_ROWS = [
    (
        "RATE-PD-P1-LIVE-INV-APP",
        "CN_INV_APPLICATION_FEE",
        "发明申请费",
        Decimal("900.00"),
        "FIXED",
        True,
    ),
    (
        "RATE-PD-P1-LIVE-PUB-PRINT",
        "CN_PUBLICATION_PRINT_FEE",
        "发明公布印刷费",
        Decimal("50.00"),
        "FIXED",
        False,
    ),
    (
        "RATE-PD-P1-LIVE-SUB-EXAM",
        "CN_SUBSTANTIVE_EXAM_FEE",
        "发明实质审查费",
        Decimal("2500.00"),
        "FIXED",
        True,
    ),
]

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
    "grant_notice": "ATT-PD-P1-LIVE-GRANT",
}

SAFE_FPMS_ENVS = {"dev", "development", "local", "test", "demo"}


def main() -> None:
    variant = resolve_variant()
    if variant == "v5":
        main_v5()
        return
    if variant in {"v6-cleanup", "v6-clean"}:
        main_v6_cleanup()
        return
    if variant in {"v6-enrich", "v6-enrichment"}:
        main_v6_enrich()
        return
    if variant != "v4":
        raise RuntimeError(f"Unknown P1 demo seed variant: {variant}")

    assert_safe_demo_environment()
    from app.db.session import SessionLocal  # noqa: PLC0415

    db = SessionLocal()
    try:
        ensure_live_fee_rate_schema(db)
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
                    "grantFeeTaskId": GRANT_FEE_TASK_ID,
                    "annuityTaskIds": [ANNUITY_TASK_ID_YEAR_2, ANNUITY_TASK_ID_YEAR_3],
                },
                ensure_ascii=False,
                sort_keys=True,
            )
        )
    finally:
        db.close()


def resolve_variant() -> str:
    args = sys.argv[1:]
    if "--variant" in args:
        index = args.index("--variant")
        if index + 1 >= len(args):
            raise RuntimeError("--variant requires a value")
        return args[index + 1].strip().lower()
    for arg in args:
        if arg.startswith("--variant="):
            return arg.split("=", 1)[1].strip().lower()
    return "v4"


def main_v5() -> None:
    assert_safe_demo_environment()
    from app.db.session import SessionLocal  # noqa: PLC0415

    db = SessionLocal()
    try:
        ensure_live_fee_rate_schema(db)
        ensure_live_comparison_fixture(db)
        clear_v5_fixture(db)
        seed_v5_fixture(db)
        db.commit()
        print(
            json.dumps(
                {
                    "preservedCaseNo": CASE_NO,
                    "preservedClientId": CLIENT_ID,
                    "caseId": V5_CASE_ID,
                    "caseNo": V5_CASE_NO,
                    "clientId": V5_CLIENT_ID,
                    "filingPackageId": V5_FILING_PACKAGE_ID,
                    "feeDraftId": V5_FEE_DRAFT_ID,
                    "payListId": V5_PAY_LIST_ID,
                    "oaPackageId": V5_OA_PACKAGE_ID,
                    "sourceOaDocumentId": V5_SOURCE_OA_DOCUMENT_ID,
                    "replyDocumentId": V5_REPLY_DOCUMENT_ID,
                    "receiptAttachmentId": v5_id(ATTACHMENTS["oa_receipt"]),
                    "letterDocumentId": V5_LETTER_DOCUMENT_ID,
                    "grantDocumentId": V5_GRANT_DOCUMENT_ID,
                    "grantFeeTaskId": V5_GRANT_FEE_TASK_ID,
                    "annuityTaskIds": [
                        V5_ANNUITY_TASK_ID_YEAR_2,
                        V5_ANNUITY_TASK_ID_YEAR_3,
                    ],
                },
                ensure_ascii=False,
                sort_keys=True,
            )
        )
    finally:
        db.close()


def main_v6_cleanup() -> None:
    assert_safe_demo_environment()
    from app.db.session import SessionLocal  # noqa: PLC0415

    db = SessionLocal()
    try:
        ensure_live_fee_rate_schema(db)
        case, client = get_v6_customer_case(db)
        clear_v6_fixture(
            db,
            case_id=case.id if case else None,
            client_id=client.id if client else None,
            delete_customer_case=True,
        )
        db.commit()
        print(
            json.dumps(
                {
                    "variant": "v6-cleanup",
                    "preservedCaseNo": CASE_NO,
                    "targetCaseNo": V6_CASE_NO,
                    "targetClientCode": V6_CLIENT_CODE,
                },
                ensure_ascii=False,
                sort_keys=True,
            )
        )
    finally:
        db.close()


def main_v6_enrich() -> None:
    assert_safe_demo_environment()
    from app.db.session import SessionLocal  # noqa: PLC0415

    db = SessionLocal()
    try:
        ensure_live_fee_rate_schema(db)
        case, client = get_v6_customer_case(db)
        if case is None or client is None:
            raise RuntimeError(
                "V6 enrichment requires UI-created V6 customer and case before running; "
                f"expected client_code={V6_CLIENT_CODE} and case_no={V6_CASE_NO}."
            )
        if case.client_id != client.id:
            raise RuntimeError(
                "V6 enrichment requires UI-created V6 customer and case to be linked; "
                f"case_no={V6_CASE_NO} is linked to client_id={case.client_id}, "
                f"expected client_id={client.id}."
            )

        clear_v6_fixture(db, case_id=case.id, client_id=client.id, delete_customer_case=False)
        seed_v6_downstream_fixture(db, case_id=case.id, client_id=client.id)
        db.commit()
        print(
            json.dumps(
                {
                    "preservedCaseNo": CASE_NO,
                    "preservedClientCode": V6_CLIENT_CODE,
                    "caseId": case.id,
                    "caseNo": V6_CASE_NO,
                    "clientId": client.id,
                    "filingPackageId": V6_FILING_PACKAGE_ID,
                    "feeDraftId": V6_FEE_DRAFT_ID,
                    "payListId": V6_PAY_LIST_ID,
                    "oaPackageId": V6_OA_PACKAGE_ID,
                    "sourceOaDocumentId": V6_SOURCE_OA_DOCUMENT_ID,
                    "replyDocumentId": V6_REPLY_DOCUMENT_ID,
                    "receiptAttachmentId": v6_id(ATTACHMENTS["oa_receipt"], case.id, client.id),
                    "letterDocumentId": V6_LETTER_DOCUMENT_ID,
                    "grantDocumentId": V6_GRANT_DOCUMENT_ID,
                    "grantFeeTaskId": V6_GRANT_FEE_TASK_ID,
                    "annuityTaskIds": [
                        V6_ANNUITY_TASK_ID_YEAR_2,
                        V6_ANNUITY_TASK_ID_YEAR_3,
                    ],
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


def ensure_live_fee_rate_schema(db) -> None:
    """Patch old local SQLite demo DBs that predate fee-rate source metadata."""

    existing_columns = {
        row[1] for row in db.execute(text("PRAGMA table_info(t_fee_rate)")).all()
    }
    needed_columns = {
        "source_doc": "VARCHAR(256)",
        "source_url": "VARCHAR(512)",
        "source_policy": "VARCHAR(256)",
        "source_version": "VARCHAR(64)",
        "source_status": "VARCHAR(32)",
    }
    for column_name, column_type in needed_columns.items():
        if column_name not in existing_columns:
            db.execute(
                text(f"ALTER TABLE t_fee_rate ADD COLUMN {column_name} {column_type}")
            )
    db.commit()


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


def ensure_live_comparison_fixture(db) -> None:
    old_client = db.get(Client, CLIENT_ID)
    old_case = db.get(Case, CASE_ID)
    if old_client is not None and old_case is not None:
        return
    clear_fixture(db)
    seed_fixture(db)
    db.commit()


def clear_v5_fixture(db) -> None:
    document_ids = [
        V5_FILING_DOCUMENT_ID,
        V5_SOURCE_OA_DOCUMENT_ID,
        V5_REPLY_DOCUMENT_ID,
        V5_LETTER_DOCUMENT_ID,
        V5_GRANT_DOCUMENT_ID,
    ]
    package_ids = [V5_FILING_PACKAGE_ID, V5_OA_PACKAGE_ID]

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
        db.execute(select(FeeDraft.id).where(FeeDraft.case_id == V5_CASE_ID)).scalars()
    )
    if V5_FEE_DRAFT_ID not in demo_fee_draft_ids:
        demo_fee_draft_ids.append(V5_FEE_DRAFT_ID)

    demo_fee_item_ids = (
        list(
            db.execute(
                select(FeeItem.id).where(FeeItem.draft_id.in_(demo_fee_draft_ids))
            ).scalars()
        )
        if demo_fee_draft_ids
        else []
    )

    demo_pay_list_ids = {V5_PAY_LIST_ID}
    demo_pay_list_ids.update(
        db.execute(select(GovPayment.pay_list_id).where(GovPayment.case_id == V5_CASE_ID)).scalars()
    )
    if demo_fee_item_ids:
        demo_pay_list_ids.update(
            db.execute(
                select(GovPayment.pay_list_id).where(GovPayment.fee_item_id.in_(demo_fee_item_ids))
            ).scalars()
        )
    demo_pay_list_id_list = sorted(demo_pay_list_ids)
    assert_v5_pay_lists_are_exclusive(db, demo_pay_list_id_list, demo_fee_item_ids)

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
    db.query(GovPayment).filter(GovPayment.case_id == V5_CASE_ID).delete(
        synchronize_session=False
    )
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
    db.query(AnnuityTask).filter(AnnuityTask.case_id == V5_CASE_ID).delete(
        synchronize_session=False
    )
    db.query(T_GrantFeeTask).filter(T_GrantFeeTask.case_id == V5_CASE_ID).delete(
        synchronize_session=False
    )

    db.query(Task).filter(Task.document_id.in_(document_ids)).delete(synchronize_session=False)
    db.query(DocAttachment).filter(DocAttachment.document_id.in_(document_ids)).delete(
        synchronize_session=False
    )
    db.query(Document).filter(Document.id.in_(document_ids)).delete(synchronize_session=False)
    db.query(T_CaseApplicant).filter(T_CaseApplicant.case_id == V5_CASE_ID).delete(
        synchronize_session=False
    )
    db.query(T_CaseInventor).filter(T_CaseInventor.case_id == V5_CASE_ID).delete(
        synchronize_session=False
    )
    db.query(Case).filter(Case.id == V5_CASE_ID).delete(synchronize_session=False)
    db.query(Applicant).filter(Applicant.id == V5_APPLICANT_MASTER_ID).delete(
        synchronize_session=False
    )
    db.query(ClientContact).filter(ClientContact.id == V5_CONTACT_ID).delete(
        synchronize_session=False
    )
    db.query(Client).filter(Client.id == V5_CLIENT_ID).delete(synchronize_session=False)
    db.commit()


def assert_v5_pay_lists_are_exclusive(
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
        if row.case_id != V5_CASE_ID and row.fee_item_id not in demo_fee_item_id_set
    ]
    if unsafe_rows:
        details = ", ".join(
            f"pay_list_id={row.pay_list_id}, case_id={row.case_id}, fee_item_id={row.fee_item_id}"
            for row in unsafe_rows[:5]
        )
        raise RuntimeError(
            "P1 V5 demo seed refused to delete a pay-list containing non-demo payment rows: "
            f"{details}"
        )


def seed_v5_fixture(db) -> None:
    db.add(
        clone_row(
            Client,
            require_row(db, Client, CLIENT_ID),
            id=V5_CLIENT_ID,
            client_code="PD-P1-V5-LIVE",
            name_cn="P1五版演示客户有限公司",
            email="p1-v5@example.com",
        )
    )
    db.flush()
    db.add(
        clone_row(
            ClientContact,
            require_row(db, ClientContact, CONTACT_ID),
            id=V5_CONTACT_ID,
            client_id=V5_CLIENT_ID,
            contact_name="王五",
            email="wangwu@example.com",
        )
    )
    db.add(
        clone_row(
            Applicant,
            require_row(db, Applicant, APPLICANT_MASTER_ID),
            id=V5_APPLICANT_MASTER_ID,
            code="AA-PD-P1-V5-LIVE-1",
            name_cn="P1五版测试申请人有限公司",
            total_power_of_attorney_no="总委备-P1-V5-LIVE-001",
        )
    )
    db.add(
        clone_row(
            Case,
            require_row(db, Case, CASE_ID),
            id=V5_CASE_ID,
            case_no=V5_CASE_NO,
            client_id=V5_CLIENT_ID,
            title_cn="P1五版全流程状态演示方法及系统",
            app_no="CN202610000005.0",
            status="NOT_FILED",
            grant_no="ZL202610000005.0",
            patent_no="ZL202610000005.0",
        )
    )
    db.flush()
    db.add(
        clone_row(
            T_CaseApplicant,
            require_row(db, T_CaseApplicant, "APPL-PD-P1-LIVE-1"),
            id="APPL-PD-P1-V5-LIVE-1",
            case_id=V5_CASE_ID,
            applicant_id=V5_APPLICANT_MASTER_ID,
            name_cn="P1五版测试申请人有限公司",
            certificate_no="91110000P1E2EV5000X",
        )
    )
    db.add(
        clone_row(
            T_CaseInventor,
            require_row(db, T_CaseInventor, "INV-PD-P1-LIVE-1"),
            id="INV-PD-P1-V5-LIVE-1",
            case_id=V5_CASE_ID,
        )
    )

    clone_documents(db)
    clone_attachments(db)
    clone_work_packages(db)
    clone_fees(db)
    clone_grant_and_annuity(db)
    clone_task(db)


def clone_documents(db) -> None:
    for old_id, new_id in [
        (FILING_DOCUMENT_ID, V5_FILING_DOCUMENT_ID),
        (SOURCE_OA_DOCUMENT_ID, V5_SOURCE_OA_DOCUMENT_ID),
        (REPLY_DOCUMENT_ID, V5_REPLY_DOCUMENT_ID),
        (LETTER_DOCUMENT_ID, V5_LETTER_DOCUMENT_ID),
        (GRANT_DOCUMENT_ID, V5_GRANT_DOCUMENT_ID),
    ]:
        db.add(
            clone_row(
                Document,
                require_row(db, Document, old_id),
                id=new_id,
                case_id=V5_CASE_ID,
            )
        )
    db.flush()


def clone_attachments(db) -> None:
    for old_id in ATTACHMENTS.values():
        source = require_row(db, DocAttachment, old_id)
        db.add(
            clone_row(
                DocAttachment,
                source,
                id=v5_id(old_id),
                document_id=v5_id(source.document_id),
            )
        )


def clone_work_packages(db) -> None:
    for old_id, new_id, status in [
        (FILING_PACKAGE_ID, V5_FILING_PACKAGE_ID, "NEEDS_MAINTENANCE"),
        (OA_PACKAGE_ID, V5_OA_PACKAGE_ID, "WAITING_RECEIPT"),
    ]:
        source = require_row(db, OfficialWorkPackage, old_id)
        db.add(
            clone_row(
                OfficialWorkPackage,
                source,
                id=new_id,
                case_id=V5_CASE_ID,
                source_document_id=v5_optional_id(source.source_document_id),
                reply_document_id=v5_optional_id(source.reply_document_id),
                status=status,
            )
        )

    for manifest in db.execute(
        select(OfficialWorkPackageManifest).where(
            OfficialWorkPackageManifest.package_id.in_([FILING_PACKAGE_ID, OA_PACKAGE_ID])
        )
    ).scalars():
        db.add(
            clone_row(
                OfficialWorkPackageManifest,
                manifest,
                id=v5_id(manifest.id),
                package_id=v5_id(manifest.package_id),
                attachment_id=v5_optional_id(manifest.attachment_id),
            )
        )

    for checklist in db.execute(
        select(OfficialWorkPackageChecklist).where(
            OfficialWorkPackageChecklist.package_id.in_([FILING_PACKAGE_ID, OA_PACKAGE_ID])
        )
    ).scalars():
        db.add(
            clone_row(
                OfficialWorkPackageChecklist,
                checklist,
                id=v5_id(checklist.id),
                package_id=v5_id(checklist.package_id),
                status=initial_v5_checklist_status(
                    checklist.package_id,
                    checklist.item_code,
                ),
                evidence_note=initial_v5_checklist_note(
                    checklist.package_id,
                    checklist.item_code,
                    checklist.evidence_note,
                ),
            )
        )


def clone_fees(db) -> None:
    db.add(
        clone_row(
            FeeDraft,
            require_row(db, FeeDraft, FEE_DRAFT_ID),
            id=V5_FEE_DRAFT_ID,
            case_id=V5_CASE_ID,
            client_id=V5_CLIENT_ID,
            status="OPEN",
        )
    )
    for old_id in [FEE_ITEM_ID, FEE_PUBLICATION_ITEM_ID, FEE_EXAM_ITEM_ID]:
        source = require_row(db, FeeItem, old_id)
        db.add(
            clone_row(
                FeeItem,
                source,
                id=v5_id(old_id),
                draft_id=V5_FEE_DRAFT_ID,
                case_id=V5_CASE_ID,
                rate_id=source.rate_id,
            )
        )
    db.add(
        clone_row(
            PayList,
            require_row(db, PayList, PAY_LIST_ID),
            id=V5_PAY_LIST_ID,
            client_id=V5_CLIENT_ID,
            pay_list_no="PL-PD-P1-V5-LIVE",
        )
    )
    db.flush()
    for payment in db.execute(
        select(GovPayment).where(GovPayment.pay_list_id == PAY_LIST_ID)
    ).scalars():
        db.add(
            clone_row(
                GovPayment,
                payment,
                id=None,
                pay_list_id=V5_PAY_LIST_ID,
                case_id=V5_CASE_ID,
                fee_item_id=v5_optional_id(payment.fee_item_id),
            )
        )

    for checklist in db.execute(
        select(OfficialFeeChecklist).where(
            (OfficialFeeChecklist.fee_draft_id == FEE_DRAFT_ID)
            | (OfficialFeeChecklist.pay_list_id == PAY_LIST_ID)
        )
    ).scalars():
        db.add(
            clone_row(
                OfficialFeeChecklist,
                checklist,
                id=v5_id(checklist.id),
                fee_draft_id=v5_optional_id(checklist.fee_draft_id),
                pay_list_id=V5_PAY_LIST_ID if checklist.pay_list_id == PAY_LIST_ID else None,
            )
        )


def clone_grant_and_annuity(db) -> None:
    db.add(
        clone_row(
            T_GrantFeeTask,
            require_row(db, T_GrantFeeTask, GRANT_FEE_TASK_ID),
            id=V5_GRANT_FEE_TASK_ID,
            case_id=V5_CASE_ID,
            draft_generated=False,
        )
    )
    for old_id, new_id in [
        (ANNUITY_TASK_ID_YEAR_2, V5_ANNUITY_TASK_ID_YEAR_2),
        (ANNUITY_TASK_ID_YEAR_3, V5_ANNUITY_TASK_ID_YEAR_3),
    ]:
        db.add(
            clone_row(
                AnnuityTask,
                require_row(db, AnnuityTask, old_id),
                id=new_id,
                case_id=V5_CASE_ID,
                client_id=V5_CLIENT_ID,
                draft_generated=False,
            )
        )


def clone_task(db) -> None:
    db.add(
        clone_row(
            Task,
            require_row(db, Task, "TASK-PD-P1-LIVE-OA"),
            id="TASK-PD-P1-V5-LIVE-OA",
            case_id=V5_CASE_ID,
            document_id=V5_SOURCE_OA_DOCUMENT_ID,
        )
    )


def get_v6_customer_case(db):
    client = (
        db.execute(select(Client).where(Client.client_code == V6_CLIENT_CODE))
        .scalars()
        .first()
    )
    case = db.execute(select(Case).where(Case.case_no == V6_CASE_NO)).scalars().first()
    return case, client


def clear_v6_fixture(
    db,
    *,
    case_id: str | None,
    client_id: str | None,
    delete_customer_case: bool,
) -> None:
    document_ids = [
        V6_FILING_DOCUMENT_ID,
        V6_SOURCE_OA_DOCUMENT_ID,
        V6_REPLY_DOCUMENT_ID,
        V6_LETTER_DOCUMENT_ID,
        V6_GRANT_DOCUMENT_ID,
    ]
    package_ids = [V6_FILING_PACKAGE_ID, V6_OA_PACKAGE_ID]

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

    demo_fee_draft_ids = [V6_FEE_DRAFT_ID]
    if case_id:
        demo_fee_draft_ids.extend(
            db.execute(select(FeeDraft.id).where(FeeDraft.case_id == case_id)).scalars()
        )
    demo_fee_draft_ids = sorted(set(demo_fee_draft_ids))

    demo_fee_item_ids = list(
        db.execute(select(FeeItem.id).where(FeeItem.draft_id.in_(demo_fee_draft_ids))).scalars()
    )

    demo_pay_list_ids = {V6_PAY_LIST_ID}
    if case_id:
        demo_pay_list_ids.update(
            db.execute(select(GovPayment.pay_list_id).where(GovPayment.case_id == case_id)).scalars()
        )
    if demo_fee_item_ids:
        demo_pay_list_ids.update(
            db.execute(
                select(GovPayment.pay_list_id).where(GovPayment.fee_item_id.in_(demo_fee_item_ids))
            ).scalars()
        )
    demo_pay_list_id_list = sorted(demo_pay_list_ids)
    assert_v6_pay_lists_are_exclusive(db, demo_pay_list_id_list, demo_fee_item_ids, case_id)

    db.query(OfficialFeeChecklist).filter(
        OfficialFeeChecklist.fee_draft_id.in_(demo_fee_draft_ids)
    ).delete(synchronize_session=False)
    db.query(OfficialFeeChecklist).filter(
        OfficialFeeChecklist.pay_list_id.in_(demo_pay_list_id_list)
    ).delete(synchronize_session=False)
    db.query(GovPayment).filter(GovPayment.pay_list_id.in_(demo_pay_list_id_list)).delete(
        synchronize_session=False
    )
    if case_id:
        db.query(GovPayment).filter(GovPayment.case_id == case_id).delete(
            synchronize_session=False
        )
    if demo_fee_item_ids:
        db.query(GovPayment).filter(GovPayment.fee_item_id.in_(demo_fee_item_ids)).delete(
            synchronize_session=False
        )
    db.query(PayList).filter(PayList.id.in_(demo_pay_list_id_list)).delete(
        synchronize_session=False
    )
    db.query(FeeItem).filter(FeeItem.draft_id.in_(demo_fee_draft_ids)).delete(
        synchronize_session=False
    )
    db.query(FeeDraft).filter(FeeDraft.id.in_(demo_fee_draft_ids)).delete(
        synchronize_session=False
    )

    if case_id:
        db.query(AnnuityTask).filter(AnnuityTask.case_id == case_id).delete(
            synchronize_session=False
        )
        db.query(T_GrantFeeTask).filter(T_GrantFeeTask.case_id == case_id).delete(
            synchronize_session=False
        )
    db.query(AnnuityTask).filter(
        AnnuityTask.id.in_([V6_ANNUITY_TASK_ID_YEAR_2, V6_ANNUITY_TASK_ID_YEAR_3])
    ).delete(synchronize_session=False)
    db.query(T_GrantFeeTask).filter(T_GrantFeeTask.id == V6_GRANT_FEE_TASK_ID).delete(
        synchronize_session=False
    )

    db.query(Task).filter(Task.document_id.in_(document_ids)).delete(synchronize_session=False)
    db.query(Task).filter(Task.id == "TASK-PD-P1-V6-LIVE-OA").delete(
        synchronize_session=False
    )
    db.query(DocAttachment).filter(DocAttachment.document_id.in_(document_ids)).delete(
        synchronize_session=False
    )
    db.query(Document).filter(Document.id.in_(document_ids)).delete(synchronize_session=False)

    if delete_customer_case and case_id:
        db.query(T_CaseApplicant).filter(T_CaseApplicant.case_id == case_id).delete(
            synchronize_session=False
        )
        db.query(T_CaseInventor).filter(T_CaseInventor.case_id == case_id).delete(
            synchronize_session=False
        )
        db.query(Case).filter(Case.id == case_id).delete(synchronize_session=False)
    if delete_customer_case and client_id:
        db.query(ClientContact).filter(ClientContact.client_id == client_id).delete(
            synchronize_session=False
        )
        db.query(Client).filter(Client.id == client_id).delete(synchronize_session=False)


def assert_v6_pay_lists_are_exclusive(
    db,
    pay_list_ids: list[int],
    demo_fee_item_ids: list[str],
    case_id: str | None,
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
        if row.case_id != case_id and row.fee_item_id not in demo_fee_item_id_set
    ]
    if unsafe_rows:
        details = ", ".join(
            f"pay_list_id={row.pay_list_id}, case_id={row.case_id}, fee_item_id={row.fee_item_id}"
            for row in unsafe_rows[:5]
        )
        raise RuntimeError(
            "P1 V6 demo helper refused to delete a pay-list containing non-demo payment rows: "
            f"{details}"
        )


def seed_v6_downstream_fixture(db, *, case_id: str, client_id: str) -> None:
    clone_v6_documents(db, case_id=case_id, client_id=client_id)
    clone_v6_attachments(db, case_id=case_id, client_id=client_id)
    clone_v6_work_packages(db, case_id=case_id, client_id=client_id)
    clone_v6_fees(db, case_id=case_id, client_id=client_id)
    clone_v6_grant_and_annuity(db, case_id=case_id, client_id=client_id)
    clone_v6_task(db, case_id=case_id, client_id=client_id)


def clone_v6_documents(db, *, case_id: str, client_id: str) -> None:
    for old_id, new_id in [
        (FILING_DOCUMENT_ID, V6_FILING_DOCUMENT_ID),
        (SOURCE_OA_DOCUMENT_ID, V6_SOURCE_OA_DOCUMENT_ID),
        (REPLY_DOCUMENT_ID, V6_REPLY_DOCUMENT_ID),
        (LETTER_DOCUMENT_ID, V6_LETTER_DOCUMENT_ID),
        (GRANT_DOCUMENT_ID, V6_GRANT_DOCUMENT_ID),
    ]:
        db.add(
            clone_v6_row(
                Document,
                require_row(db, Document, old_id),
                case_id,
                client_id,
                id=new_id,
                case_id=case_id,
            )
        )
    db.flush()


def clone_v6_attachments(db, *, case_id: str, client_id: str) -> None:
    for old_id in ATTACHMENTS.values():
        source = require_row(db, DocAttachment, old_id)
        db.add(
            clone_v6_row(
                DocAttachment,
                source,
                case_id,
                client_id,
                id=v6_id(old_id, case_id, client_id),
                document_id=v6_id(source.document_id, case_id, client_id),
            )
        )


def clone_v6_work_packages(db, *, case_id: str, client_id: str) -> None:
    for old_id, new_id, status in [
        (FILING_PACKAGE_ID, V6_FILING_PACKAGE_ID, "NEEDS_MAINTENANCE"),
        (OA_PACKAGE_ID, V6_OA_PACKAGE_ID, "WAITING_RECEIPT"),
    ]:
        source = require_row(db, OfficialWorkPackage, old_id)
        db.add(
            clone_v6_row(
                OfficialWorkPackage,
                source,
                case_id,
                client_id,
                id=new_id,
                case_id=case_id,
                source_document_id=v6_optional_id(source.source_document_id, case_id, client_id),
                reply_document_id=v6_optional_id(source.reply_document_id, case_id, client_id),
                status=status,
            )
        )

    for manifest in db.execute(
        select(OfficialWorkPackageManifest).where(
            OfficialWorkPackageManifest.package_id.in_([FILING_PACKAGE_ID, OA_PACKAGE_ID])
        )
    ).scalars():
        db.add(
            clone_v6_row(
                OfficialWorkPackageManifest,
                manifest,
                case_id,
                client_id,
                id=v6_id(manifest.id, case_id, client_id),
                package_id=v6_id(manifest.package_id, case_id, client_id),
                attachment_id=v6_optional_id(manifest.attachment_id, case_id, client_id),
            )
        )

    for checklist in db.execute(
        select(OfficialWorkPackageChecklist).where(
            OfficialWorkPackageChecklist.package_id.in_([FILING_PACKAGE_ID, OA_PACKAGE_ID])
        )
    ).scalars():
        db.add(
            clone_v6_row(
                OfficialWorkPackageChecklist,
                checklist,
                case_id,
                client_id,
                id=v6_id(checklist.id, case_id, client_id),
                package_id=v6_id(checklist.package_id, case_id, client_id),
                status=initial_v5_checklist_status(
                    checklist.package_id,
                    checklist.item_code,
                ),
                evidence_note=initial_v5_checklist_note(
                    checklist.package_id,
                    checklist.item_code,
                    checklist.evidence_note,
                ),
            )
        )


def clone_v6_fees(db, *, case_id: str, client_id: str) -> None:
    db.add(
        clone_v6_row(
            FeeDraft,
            require_row(db, FeeDraft, FEE_DRAFT_ID),
            case_id,
            client_id,
            id=V6_FEE_DRAFT_ID,
            case_id=case_id,
            client_id=client_id,
            status="OPEN",
        )
    )
    for old_id in [FEE_ITEM_ID, FEE_PUBLICATION_ITEM_ID, FEE_EXAM_ITEM_ID]:
        source = require_row(db, FeeItem, old_id)
        db.add(
            clone_v6_row(
                FeeItem,
                source,
                case_id,
                client_id,
                id=v6_id(old_id, case_id, client_id),
                draft_id=V6_FEE_DRAFT_ID,
                case_id=case_id,
                rate_id=source.rate_id,
            )
        )
    db.add(
        clone_v6_row(
            PayList,
            require_row(db, PayList, PAY_LIST_ID),
            case_id,
            client_id,
            id=V6_PAY_LIST_ID,
            client_id=client_id,
            pay_list_no="PL-PD-P1-V6-LIVE",
        )
    )
    db.flush()
    for payment in db.execute(
        select(GovPayment).where(GovPayment.pay_list_id == PAY_LIST_ID)
    ).scalars():
        db.add(
            clone_v6_row(
                GovPayment,
                payment,
                case_id,
                client_id,
                id=None,
                pay_list_id=V6_PAY_LIST_ID,
                case_id=case_id,
                fee_item_id=v6_optional_id(payment.fee_item_id, case_id, client_id),
            )
        )

    for checklist in db.execute(
        select(OfficialFeeChecklist).where(
            (OfficialFeeChecklist.fee_draft_id == FEE_DRAFT_ID)
            | (OfficialFeeChecklist.pay_list_id == PAY_LIST_ID)
        )
    ).scalars():
        db.add(
            clone_v6_row(
                OfficialFeeChecklist,
                checklist,
                case_id,
                client_id,
                id=v6_id(checklist.id, case_id, client_id),
                fee_draft_id=v6_optional_id(checklist.fee_draft_id, case_id, client_id),
                pay_list_id=V6_PAY_LIST_ID if checklist.pay_list_id == PAY_LIST_ID else None,
            )
        )


def clone_v6_grant_and_annuity(db, *, case_id: str, client_id: str) -> None:
    db.add(
        clone_v6_row(
            T_GrantFeeTask,
            require_row(db, T_GrantFeeTask, GRANT_FEE_TASK_ID),
            case_id,
            client_id,
            id=V6_GRANT_FEE_TASK_ID,
            case_id=case_id,
            draft_generated=False,
        )
    )
    for old_id, new_id in [
        (ANNUITY_TASK_ID_YEAR_2, V6_ANNUITY_TASK_ID_YEAR_2),
        (ANNUITY_TASK_ID_YEAR_3, V6_ANNUITY_TASK_ID_YEAR_3),
    ]:
        db.add(
            clone_v6_row(
                AnnuityTask,
                require_row(db, AnnuityTask, old_id),
                case_id,
                client_id,
                id=new_id,
                case_id=case_id,
                client_id=client_id,
                draft_generated=False,
            )
        )


def clone_v6_task(db, *, case_id: str, client_id: str) -> None:
    db.add(
        clone_v6_row(
            Task,
            require_row(db, Task, "TASK-PD-P1-LIVE-OA"),
            case_id,
            client_id,
            id="TASK-PD-P1-V6-LIVE-OA",
            case_id=case_id,
            document_id=V6_SOURCE_OA_DOCUMENT_ID,
        )
    )


def initial_v5_checklist_status(package_id: str, item_code: str) -> str:
    if package_id == OA_PACKAGE_ID and item_code == "SIGNATURE_CONFIRMED":
        return "DONE"
    pending_codes = {
        "CNIPA_FORM_IMPORTED",
        "PREVIEW_CONFIRMED",
        "SIGNATURE_CONFIRMED",
        "CLOUD_SECOND_DOWNLOAD_CONFIRMED",
        "PREVIEW_TABS_CONFIRMED",
        "SUBMISSION_CONFIRMED",
        "RECEIPT_CONFIRMED",
    }
    return "PENDING" if item_code in pending_codes else "DONE"


def initial_v5_checklist_note(
    package_id: str,
    item_code: str,
    current_note: str | None,
) -> str | None:
    if initial_v5_checklist_status(package_id, item_code) == "PENDING":
        return None
    return current_note


def require_row(db, model, row_id):
    row = db.get(model, row_id)
    if row is None:
        raise RuntimeError(f"Missing required seed source row {model.__name__}:{row_id}")
    return row


def clone_row(model, source, **overrides):
    data = {}
    for column in model.__table__.columns:
        name = column.name
        if name in overrides:
            continue
        data[name] = v5_value(getattr(source, name))
    data.update(overrides)
    return model(**data)


def clone_v6_row(model, source, context_case_id: str, context_client_id: str, **overrides):
    data = {}
    for column in model.__table__.columns:
        name = column.name
        if name in overrides:
            continue
        data[name] = v6_value(getattr(source, name), context_case_id, context_client_id)
    data.update(overrides)
    return model(**data)


def v5_optional_id(value):
    return None if value is None else v5_id(value)


def v5_id(value):
    if value == PAY_LIST_ID:
        return V5_PAY_LIST_ID
    if value == ANNUITY_TASK_ID_YEAR_2:
        return V5_ANNUITY_TASK_ID_YEAR_2
    if value == ANNUITY_TASK_ID_YEAR_3:
        return V5_ANNUITY_TASK_ID_YEAR_3
    if isinstance(value, str):
        return v5_text(value)
    return value


def v5_value(value):
    if isinstance(value, str):
        return v5_text(value)
    return v5_id(value)


def v5_text(value: str) -> str:
    replacements = [
        (CASE_ID, V5_CASE_ID),
        (CASE_NO, V5_CASE_NO),
        (CLIENT_ID, V5_CLIENT_ID),
        (CONTACT_ID, V5_CONTACT_ID),
        (APPLICANT_MASTER_ID, V5_APPLICANT_MASTER_ID),
        ("PD-P1-LIVE", "PD-P1-V5-LIVE"),
        ("P1全流程客户有限公司", "P1五版演示客户有限公司"),
        ("P1测试申请人有限公司", "P1五版测试申请人有限公司"),
        ("P1全流程测试方法及系统", "P1五版全流程状态演示方法及系统"),
        ("CN202610000001.0", "CN202610000005.0"),
        ("ZL202610000001.0", "ZL202610000005.0"),
        ("91110000P1E2E0000X", "91110000P1E2EV5000X"),
        ("总委备-P1-LIVE-001", "总委备-P1-V5-LIVE-001"),
        ("张三", "王五"),
        ("zhangsan@example.com", "wangwu@example.com"),
        ("p1-live@example.com", "p1-v5@example.com"),
        ("P1 V4 demo", "P1 V5 demo"),
        ("P1 live E2E", "P1 V5 live E2E"),
    ]
    result = value
    for old, new in replacements:
        result = result.replace(old, new)
    return result


def v6_optional_id(value, context_case_id: str, context_client_id: str):
    return None if value is None else v6_id(value, context_case_id, context_client_id)


def v6_id(value, context_case_id: str, context_client_id: str):
    if value == PAY_LIST_ID:
        return V6_PAY_LIST_ID
    if value == ANNUITY_TASK_ID_YEAR_2:
        return V6_ANNUITY_TASK_ID_YEAR_2
    if value == ANNUITY_TASK_ID_YEAR_3:
        return V6_ANNUITY_TASK_ID_YEAR_3
    if isinstance(value, str):
        return v6_text(value, context_case_id, context_client_id)
    return value


def v6_value(value, context_case_id: str, context_client_id: str):
    if isinstance(value, str):
        return v6_text(value, context_case_id, context_client_id)
    return v6_id(value, context_case_id, context_client_id)


def v6_text(value: str, context_case_id: str, context_client_id: str) -> str:
    replacements = [
        (CASE_ID, context_case_id),
        (CASE_NO, V6_CASE_NO),
        (CLIENT_ID, context_client_id),
        (CONTACT_ID, "CONTACT-PD-P1-V6-LIVE"),
        (APPLICANT_MASTER_ID, "APP-PD-P1-V6-LIVE-1"),
        ("PD-P1-LIVE", "PD-P1-V6-LIVE"),
        ("P1全流程客户有限公司", "P1六版演示客户有限公司"),
        ("P1测试申请人有限公司", "P1六版测试申请人有限公司"),
        ("P1全流程测试方法及系统", "P1六版现场创建全流程演示方法及系统"),
        ("CN202610000001.0", "CN202610000006.0"),
        ("ZL202610000001.0", "ZL202610000006.0"),
        ("91110000P1E2E0000X", "91110000P1E2EV6000X"),
        ("总委备-P1-LIVE-001", "总委备-P1-V6-LIVE-001"),
        ("张三", "赵六老师"),
        ("zhangsan@example.com", "zhaoliu@example.com"),
        ("p1-live@example.com", "p1-v6@example.com"),
        ("P1 V4 demo", "P1 V6 demo"),
        ("P1 live E2E", "P1 V6 live E2E"),
    ]
    result = value
    for old, new in replacements:
        result = result.replace(old, new)
    return result


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
            pub_date=date(2027, 4, 9),
            pub_no="CN112345678A",
            issue_date=date(2027, 3, 15),
            grant_date=date(2027, 4, 9),
            grant_no="ZL202610000001.0",
            patent_no="ZL202610000001.0",
            valid_until=date(2046, 6, 2),
            spec_pages=18,
            draw_pages=3,
            claim_count=10,
            claim_pages=4,
            has_exam_request=True,
            fee_reduction="0.85",
            discount_rate=Decimal("0.8500"),
            applicant_kind="企业",
            is_fee_monitor=True,
            first_annuity_year=2,
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
    add_attachment(
        db,
        ATTACHMENTS["grant_notice"],
        GRANT_DOCUMENT_ID,
        "授权通知书.pdf",
        "GRANT_NOTICE",
        "授权通知",
        mime_type="application/pdf",
        package_usage_hint="GRANT_STATUS_EVIDENCE",
    )

    seed_filing_work_package(db)
    seed_oa_work_package(db)
    seed_fees(db)
    seed_grant_and_annuity_tasks(db)
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
    rates_by_code = seed_fee_rates(db)
    db.add(
        FeeDraft(
            id=FEE_DRAFT_ID,
            case_id=CASE_ID,
            client_id=CLIENT_ID,
            draft_type="APPLY_FEE",
            currency="CNY",
            status="OPEN",
            total_gov=Decimal("560.00"),
            total_service=Decimal("0.00"),
            total_misc=Decimal("0.00"),
            amount=Decimal("560.00"),
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
            rate_id=rates_by_code["CN_INV_APPLICATION_FEE"].id,
            fee_code="CN_INV_APPLICATION_FEE",
            fee_name="发明申请费",
            fee_type="GOV",
            quantity=Decimal("1"),
            unit_price=Decimal("900.00"),
            amount=Decimal("135.00"),
            remark="申请费，按客户确认费减比例 0.85 计算",
        )
    )
    db.add(
        FeeItem(
            id=FEE_PUBLICATION_ITEM_ID,
            draft_id=FEE_DRAFT_ID,
            case_id=CASE_ID,
            rate_id=rates_by_code["CN_PUBLICATION_PRINT_FEE"].id,
            fee_code="CN_PUBLICATION_PRINT_FEE",
            fee_name="发明公布印刷费",
            fee_type="GOV",
            quantity=Decimal("1"),
            unit_price=Decimal("50.00"),
            amount=Decimal("50.00"),
            remark="公布印刷费不适用费减",
        )
    )
    db.add(
        FeeItem(
            id=FEE_EXAM_ITEM_ID,
            draft_id=FEE_DRAFT_ID,
            case_id=CASE_ID,
            rate_id=rates_by_code["CN_SUBSTANTIVE_EXAM_FEE"].id,
            fee_code="CN_SUBSTANTIVE_EXAM_FEE",
            fee_name="发明实质审查费",
            fee_type="GOV",
            quantity=Decimal("1"),
            unit_price=Decimal("2500.00"),
            amount=Decimal("375.00"),
            remark="实质审查费，按客户确认费减比例 0.85 计算",
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
            total_amount=Decimal("560.00"),
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
            paid_amount=Decimal("560.00"),
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


def seed_grant_and_annuity_tasks(db) -> None:
    db.add(
        T_GrantFeeTask(
            id=GRANT_FEE_TASK_ID,
            case_id=CASE_ID,
            due_date=date(2027, 5, 14),
            gov_fee_amt=Decimal("135.00"),
            service_fee_amt=Decimal("0.00"),
            currency="CNY",
            client_instruction="PAY",
            notify_count=2,
            draft_generated=False,
            notice_sent=True,
            is_overdue=False,
            remark="P1 V4 demo：授权通知后客户已指示缴纳授权阶段官费，可生成草单。",
        )
    )

    for task_id, year_no, due_date in [
        (ANNUITY_TASK_ID_YEAR_2, 2, date(2028, 6, 2)),
        (ANNUITY_TASK_ID_YEAR_3, 3, date(2029, 6, 2)),
    ]:
        db.add(
            AnnuityTask(
                id=task_id,
                case_id=CASE_ID,
                client_id=CLIENT_ID,
                year_no=year_no,
                due_date=due_date,
                client_instruction="PAY" if year_no == 2 else None,
                instruction_date=date(2027, 4, 15) if year_no == 2 else None,
                notice_status="SENT" if year_no == 2 else "PENDING",
                notice_sent_date=date(2027, 4, 15) if year_no == 2 else None,
                status="OPEN",
                gov_fee_amt=Decimal("135.00"),
                service_fee_amt=Decimal("0.00"),
                notify_count=1 if year_no == 2 else 0,
                pay_next_year=False,
                draft_generated=False,
                notice_sent=year_no == 2,
                remark=f"P1 V4 demo：发明第{year_no}年度年费，按 900 元全额和减缴 85% 预估应缴 135 元。",
            )
        )


def seed_fee_rates(db) -> dict[str, FeeRate]:
    rates_by_code: dict[str, FeeRate] = {}
    for (
        rate_id,
        fee_code,
        fee_name,
        amount,
        calc_mode,
        allow_reduction,
    ) in FEE_RATE_ROWS:
        rate = (
            db.execute(
                select(FeeRate).where(
                    FeeRate.fee_code == fee_code,
                    FeeRate.fee_type == "GOV",
                    FeeRate.currency == "CNY",
                )
            )
            .scalars()
            .first()
        )
        if rate is None:
            rate = FeeRate(id=rate_id, fee_code=fee_code)
            db.add(rate)
        rate.fee_name = fee_name
        rate.fee_type = "GOV"
        rate.currency = "CNY"
        rate.default_amount = amount
        rate.enabled = True
        rate.rate_group = "DOMESTIC"
        rate.country_code = "CN"
        rate.case_type = "NORMAL"
        rate.patent_category = "INV"
        rate.calc_mode = calc_mode
        rate.allow_reduction = allow_reduction
        rate.source_doc = "docs/postdemo/专利收费场景-20260626.docx"
        rate.source_url = "http://www.tianyueip.com/product/612"
        rate.source_policy = "客户补充收费场景与客户官网费用清单"
        rate.source_version = "2026-07-05-postdemo"
        rate.source_status = "CONFIRMED"
        rates_by_code[fee_code] = rate
    db.flush()
    return rates_by_code


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
