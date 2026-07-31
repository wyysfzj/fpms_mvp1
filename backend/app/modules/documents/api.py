from __future__ import annotations

import logging
from datetime import date

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    Response,
    UploadFile,
    status,
)
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import current_user_dep, require_perm
from app.core.config import get_settings
from app.core.errors import BusinessError
from app.db.session import get_db
from app.modules.auth.models import T_User
from app.modules.cases.models import Case
from app.modules.documents.enums import DocumentDirection, DocumentDocType
from app.modules.documents.evidence_review_schemas import EvidenceVersionReviewIn
from app.modules.documents.evidence_service import (
    ReviewEvidenceVersionCommand,
    ReviewEvidenceVersionResult,
    review_evidence_version,
)
from app.modules.documents.export_excel import (
    DOCUMENT_LIST_EXPORT_MIME_TYPE,
    build_document_list_export_xlsx,
)
from app.modules.documents.extra_data import parse_document_extra_data
from app.modules.documents.fee_linking_service import maybe_create_fee_draft
from app.modules.documents.lifecycle_evidence_adapters import (
    ApplicationAbandonmentIn,
    ApplicationRejectionIn,
    ApplicationRestorationIn,
    ApplicationWithdrawalEvidenceResult,
    ApplicationWithdrawalIn,
    PassPreliminaryExaminationCommand,
    PassPreliminaryExaminationResult,
    PreliminaryExaminationPassIn,
    PreliminaryExaminationStartIn,
    PublicationNoticeIn,
    RecordApplicationAbandonmentCommand,
    RecordApplicationRejectionCommand,
    RecordApplicationRestorationCommand,
    RecordApplicationWithdrawalCommand,
    RecordPublicationNoticeCommand,
    RecordPublicationNoticeResult,
    RecordRectificationNoticeCommand,
    RecordRectificationNoticeResult,
    RectificationNoticeIn,
    ReexaminationStartIn,
    StartPreliminaryExaminationCommand,
    StartPreliminaryExaminationResult,
    StartReexaminationCommand,
    StartReexaminationResult,
    StartSubstantiveExaminationCommand,
    StartSubstantiveExaminationResult,
    SubstantiveExaminationStartIn,
    TerminalLifecycleEvidenceResult,
    pass_preliminary_examination_from_evidence,
    record_application_abandonment_from_evidence,
    record_application_rejection_from_evidence,
    record_application_restoration_from_evidence,
    record_application_withdrawal_from_evidence,
    record_publication_notice_from_evidence,
    record_rectification_notice_from_evidence,
    start_preliminary_examination_from_evidence,
    start_reexamination_from_evidence,
    start_substantive_examination_from_evidence,
)
from app.modules.documents.models import DocTemplate
from app.modules.documents.schemas import (
    DocAttachmentOut,
    DocTemplateCreateIn,
    DocTemplateListOut,
    DocTemplateOut,
    DocTemplateUpdateIn,
    DocumentCreateIn,
    DocumentDispatchCreateIn,
    DocumentDispatchLineOut,
    DocumentDispatchOut,
    DocumentEnvelopePreviewOut,
    DocumentImpactPreviewIn,
    DocumentImpactPreviewOut,
    DocumentListOut,
    DocumentMailingBatchIn,
    DocumentMailingBatchItemOut,
    DocumentMailingBatchOut,
    DocumentOut,
    DocumentUpdateIn,
    DocumentWizardAttachmentPreviewIn,
    DocumentWizardAttachmentPreviewOut,
    DocumentWizardBatchCreateIn,
    DocumentWizardBatchCreateOut,
    DocumentWizardFeePreviewIn,
    DocumentWizardFeePreviewOut,
    DocumentWizardTaskPreviewOut,
)
from app.modules.documents.service import (
    _remove_managed_attachment_file,
    batch_register_document_mailing,
    create_doc_template,
    create_document_dispatch,
    create_document_wizard_batch,
    get_attachment_download,
    get_current_attachment_evidence_versions,
    get_doc_template,
    get_document_dispatch,
    get_document_envelope_preview,
    list_doc_templates,
    list_documents,
    preview_document_impact,
    preview_document_wizard_attachment_candidates,
    preview_document_wizard_fee_candidates,
    preview_document_wizard_tasks,
    update_doc_template,
)
from app.modules.documents.service import (
    add_attachment as add_attachment_service,
)
from app.modules.documents.service import (
    create_document as create_document_service,
)
from app.modules.documents.service import (
    get_document as get_document_service,
)
from app.modules.documents.service import (
    update_document as update_document_service,
)
from app.modules.grant_fees.service import ensure_grant_fee_task_for_notice_document
from app.modules.masterdata.clients.models import Client
from app.modules.tasks.task_generation_service import TaskGenerationService

router = APIRouter()


@router.post(
    "/documents/evidence-versions/{evidence_version_id}/review",
    status_code=status.HTTP_200_OK,
    response_model=ReviewEvidenceVersionResult,
)
def review_document_evidence_version(
    evidence_version_id: str,
    payload: EvidenceVersionReviewIn,
    _perm: None = Depends(require_perm("Doc.Edit")),
    current_user: T_User = current_user_dep,
    db: Session = Depends(get_db),
) -> ReviewEvidenceVersionResult:
    try:
        result = review_evidence_version(
            ReviewEvidenceVersionCommand(
                case_id=payload.case_id,
                evidence_version_id=evidence_version_id,
                reviewer_id=current_user.id,
                decision=payload.decision,
                reviewed_at=payload.reviewed_at,
                idempotency_key=payload.idempotency_key,
            ),
            db,
        )
        db.commit()
    except Exception:
        db.rollback()
        raise
    return result


def _build_document_out(
    document,
    *,
    case_no: str | None = None,
    template_code: str | None = None,
    attachments: list | None = None,
) -> DocumentOut:
    extra_data = parse_document_extra_data(document.extra_data)
    return DocumentOut(
        id=document.id,
        case_id=document.case_id,
        case_no=case_no,
        doc_template_id=document.doc_template_id,
        template_code=template_code,
        doc_type=document.doc_type,
        direction=document.direction,
        doc_date=document.doc_date,
        title=document.title,
        ref_no=document.ref_no,
        extra_data=document.extra_data,
        official_due_date=extra_data.official_due_date,
        official_due_date_source=extra_data.official_due_date_source,
        official_due_date_status=extra_data.official_due_date_status,
        description=extra_data.description,
        reply_to_id=document.reply_to_id,
        need_reply=document.need_reply,
        reply_date=document.reply_date,
        created_at=document.created_at,
        updated_at=document.updated_at,
        attachments=attachments or [],
    )


def _build_document_mailing_batch_item_out(
    document,
    *,
    case_no: str | None = None,
) -> DocumentMailingBatchItemOut:
    return DocumentMailingBatchItemOut(
        document_id=document.id,
        case_id=document.case_id,
        case_no=case_no,
        outgoing_reg_no=document.outgoing_reg_no,
        forward_date=document.forward_date,
    )


def _build_document_dispatch_out(
    dispatch, *, client_name: str | None = None
) -> DocumentDispatchOut:
    return DocumentDispatchOut(
        id=dispatch.id,
        client_id=dispatch.client_id,
        client_name=client_name,
        dispatch_date=dispatch.dispatch_date,
        remark=dispatch.remark,
        created_at=dispatch.created_at,
        updated_at=dispatch.updated_at,
        lines=[
            DocumentDispatchLineOut(
                id=line.id,
                dispatch_id=line.dispatch_id,
                document_id=line.document_id,
                case_id=line.case_id,
                case_no=line.document.case.case_no
                if line.document and line.document.case
                else None,
                doc_name=line.doc_name,
                outgoing_reg_no=line.outgoing_reg_no,
            )
            for line in dispatch.lines
        ],
    )


# ---------------------------------------------------------------------------
# B1: DocTemplate CRUD endpoints (registered BEFORE /documents/{id} routes)
# ---------------------------------------------------------------------------


@router.get("/doc-templates", response_model=DocTemplateListOut, summary="List doc templates")
def list_doc_templates_endpoint(
    q: str | None = Query(default=None),
    direction: DocumentDirection | None = Query(default=None),
    enabled: bool | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    _perm: None = Depends(require_perm("DocTemplate.Read")),
    db: Session = Depends(get_db),
) -> DocTemplateListOut:
    items, total = list_doc_templates(
        db, direction=direction, enabled=enabled, q=q, page=page, page_size=page_size
    )
    return DocTemplateListOut(
        items=[DocTemplateOut.model_validate(t) for t in items],
        page=page,
        page_size=page_size,
        total=total,
    )


@router.post(
    "/doc-templates",
    status_code=status.HTTP_201_CREATED,
    response_model=DocTemplateOut,
    summary="Create a doc template",
)
def create_doc_template_endpoint(
    payload: DocTemplateCreateIn,
    _perm: None = Depends(require_perm("DocTemplate.Create")),
    db: Session = Depends(get_db),
) -> DocTemplateOut:
    template = create_doc_template(db, payload)
    return DocTemplateOut.model_validate(template)


@router.get(
    "/doc-templates/{template_id}",
    response_model=DocTemplateOut,
    summary="Get a doc template",
)
def get_doc_template_endpoint(
    template_id: str,
    _perm: None = Depends(require_perm("DocTemplate.Read")),
    db: Session = Depends(get_db),
) -> DocTemplateOut:
    template = get_doc_template(db, template_id)
    return DocTemplateOut.model_validate(template)


@router.put(
    "/doc-templates/{template_id}",
    response_model=DocTemplateOut,
    summary="Update a doc template",
)
def update_doc_template_endpoint(
    template_id: str,
    payload: DocTemplateUpdateIn,
    _perm: None = Depends(require_perm("DocTemplate.Edit")),
    db: Session = Depends(get_db),
) -> DocTemplateOut:
    template = update_doc_template(db, template_id, payload)
    return DocTemplateOut.model_validate(template)


# ---------------------------------------------------------------------------
# Document endpoints
# ---------------------------------------------------------------------------


@router.post(
    "/documents/{document_id}/lifecycle/preliminary-start",
    status_code=status.HTTP_200_OK,
    response_model=StartPreliminaryExaminationResult,
)
def start_document_preliminary_examination(
    document_id: str,
    payload: PreliminaryExaminationStartIn,
    _perm: None = Depends(require_perm("Doc.Edit")),
    current_user: T_User = current_user_dep,
    db: Session = Depends(get_db),
) -> StartPreliminaryExaminationResult:
    try:
        result = start_preliminary_examination_from_evidence(
            StartPreliminaryExaminationCommand(
                document_id=document_id,
                evidence_version_id=payload.evidence_version_id,
                actor_id=current_user.id,
                effective_at=payload.effective_at,
                occurred_at=payload.occurred_at,
                idempotency_key=payload.idempotency_key,
            ),
            db,
        )
        db.commit()
    except Exception:
        db.rollback()
        raise
    return result


@router.post(
    "/documents/{document_id}/lifecycle/preliminary-pass",
    status_code=status.HTTP_200_OK,
    response_model=PassPreliminaryExaminationResult,
)
def pass_document_preliminary_examination(
    document_id: str,
    payload: PreliminaryExaminationPassIn,
    _perm: None = Depends(require_perm("Doc.Edit")),
    current_user: T_User = current_user_dep,
    db: Session = Depends(get_db),
) -> PassPreliminaryExaminationResult:
    try:
        result = pass_preliminary_examination_from_evidence(
            PassPreliminaryExaminationCommand(
                document_id=document_id,
                evidence_version_id=payload.evidence_version_id,
                actor_id=current_user.id,
                effective_at=payload.effective_at,
                occurred_at=payload.occurred_at,
                idempotency_key=payload.idempotency_key,
            ),
            db,
        )
        db.commit()
    except Exception:
        db.rollback()
        raise
    return result


@router.post(
    "/documents/{document_id}/lifecycle/rectification-notice",
    status_code=status.HTTP_200_OK,
    response_model=RecordRectificationNoticeResult,
)
def record_document_rectification_notice(
    document_id: str,
    payload: RectificationNoticeIn,
    _perm: None = Depends(require_perm("Doc.Edit")),
    current_user: T_User = current_user_dep,
    db: Session = Depends(get_db),
) -> RecordRectificationNoticeResult:
    try:
        result = record_rectification_notice_from_evidence(
            RecordRectificationNoticeCommand(
                document_id=document_id,
                evidence_version_id=payload.evidence_version_id,
                actor_id=current_user.id,
                effective_at=payload.effective_at,
                occurred_at=payload.occurred_at,
                idempotency_key=payload.idempotency_key,
            ),
            db,
        )
        db.commit()
    except Exception:
        db.rollback()
        raise
    return result


@router.post(
    "/documents/{document_id}/lifecycle/publication-notice",
    status_code=status.HTTP_200_OK,
    response_model=RecordPublicationNoticeResult,
)
def record_document_publication_notice(
    document_id: str,
    payload: PublicationNoticeIn,
    _perm: None = Depends(require_perm("Doc.Edit")),
    current_user: T_User = current_user_dep,
    db: Session = Depends(get_db),
) -> RecordPublicationNoticeResult:
    try:
        result = record_publication_notice_from_evidence(
            RecordPublicationNoticeCommand(
                document_id=document_id,
                evidence_version_id=payload.evidence_version_id,
                actor_id=current_user.id,
                effective_at=payload.effective_at,
                occurred_at=payload.occurred_at,
                idempotency_key=payload.idempotency_key,
            ),
            db,
        )
        db.commit()
    except Exception:
        db.rollback()
        raise
    return result


@router.post(
    "/documents/{document_id}/lifecycle/substantive-start",
    status_code=status.HTTP_200_OK,
    response_model=StartSubstantiveExaminationResult,
)
def start_document_substantive_examination(
    document_id: str,
    payload: SubstantiveExaminationStartIn,
    _perm: None = Depends(require_perm("Doc.Edit")),
    current_user: T_User = current_user_dep,
    db: Session = Depends(get_db),
) -> StartSubstantiveExaminationResult:
    try:
        result = start_substantive_examination_from_evidence(
            StartSubstantiveExaminationCommand(
                document_id=document_id,
                evidence_version_id=payload.evidence_version_id,
                actor_id=current_user.id,
                effective_at=payload.effective_at,
                occurred_at=payload.occurred_at,
                idempotency_key=payload.idempotency_key,
            ),
            db,
        )
        db.commit()
    except Exception:
        db.rollback()
        raise
    return result


@router.post(
    "/documents/{document_id}/lifecycle/reexamination-start",
    status_code=status.HTTP_200_OK,
    response_model=StartReexaminationResult,
)
def start_document_reexamination(
    document_id: str,
    payload: ReexaminationStartIn,
    _perm: None = Depends(require_perm("Doc.Edit")),
    current_user: T_User = current_user_dep,
    db: Session = Depends(get_db),
) -> StartReexaminationResult:
    try:
        result = start_reexamination_from_evidence(
            StartReexaminationCommand(
                document_id=document_id,
                evidence_version_id=payload.evidence_version_id,
                actor_id=current_user.id,
                effective_at=payload.effective_at,
                occurred_at=payload.occurred_at,
                idempotency_key=payload.idempotency_key,
            ),
            db,
        )
        db.commit()
    except Exception:
        db.rollback()
        raise
    return result


@router.post(
    "/documents/{document_id}/lifecycle/application-rejection",
    status_code=status.HTTP_200_OK,
    response_model=TerminalLifecycleEvidenceResult,
)
def record_document_application_rejection(
    document_id: str,
    payload: ApplicationRejectionIn,
    _perm: None = Depends(require_perm("Doc.Edit")),
    current_user: T_User = current_user_dep,
    db: Session = Depends(get_db),
) -> TerminalLifecycleEvidenceResult:
    try:
        result = record_application_rejection_from_evidence(
            RecordApplicationRejectionCommand(
                document_id=document_id,
                evidence_version_id=payload.evidence_version_id,
                evidence_kind=payload.evidence_kind,
                actor_id=current_user.id,
                effective_at=payload.effective_at,
                occurred_at=payload.occurred_at,
                idempotency_key=payload.idempotency_key,
            ),
            db,
        )
        db.commit()
    except Exception:
        db.rollback()
        raise
    return result


@router.post(
    "/documents/{document_id}/lifecycle/application-withdrawal",
    status_code=status.HTTP_200_OK,
    response_model=ApplicationWithdrawalEvidenceResult,
)
def record_document_application_withdrawal(
    document_id: str,
    payload: ApplicationWithdrawalIn,
    _perm: None = Depends(require_perm("Doc.Edit")),
    current_user: T_User = current_user_dep,
    db: Session = Depends(get_db),
) -> ApplicationWithdrawalEvidenceResult:
    try:
        result = record_application_withdrawal_from_evidence(
            RecordApplicationWithdrawalCommand(
                document_id=document_id,
                evidence_version_id=payload.evidence_version_id,
                confirmation_evidence_version_id=(
                    payload.confirmation_evidence_version_id
                ),
                actor_id=current_user.id,
                effective_at=payload.effective_at,
                occurred_at=payload.occurred_at,
                idempotency_key=payload.idempotency_key,
            ),
            db,
        )
        db.commit()
    except Exception:
        db.rollback()
        raise
    return result


@router.post(
    "/documents/{document_id}/lifecycle/application-abandonment",
    status_code=status.HTTP_200_OK,
    response_model=TerminalLifecycleEvidenceResult,
)
def record_document_application_abandonment(
    document_id: str,
    payload: ApplicationAbandonmentIn,
    _perm: None = Depends(require_perm("Doc.Edit")),
    current_user: T_User = current_user_dep,
    db: Session = Depends(get_db),
) -> TerminalLifecycleEvidenceResult:
    try:
        result = record_application_abandonment_from_evidence(
            RecordApplicationAbandonmentCommand(
                document_id=document_id,
                evidence_version_id=payload.evidence_version_id,
                evidence_kind=payload.evidence_kind,
                actor_id=current_user.id,
                effective_at=payload.effective_at,
                occurred_at=payload.occurred_at,
                idempotency_key=payload.idempotency_key,
            ),
            db,
        )
        db.commit()
    except Exception:
        db.rollback()
        raise
    return result


@router.post(
    "/documents/{document_id}/lifecycle/application-restoration",
    status_code=status.HTTP_200_OK,
    response_model=TerminalLifecycleEvidenceResult,
)
def record_document_application_restoration(
    document_id: str,
    payload: ApplicationRestorationIn,
    _perm: None = Depends(require_perm("Doc.Edit")),
    current_user: T_User = current_user_dep,
    db: Session = Depends(get_db),
) -> TerminalLifecycleEvidenceResult:
    try:
        result = record_application_restoration_from_evidence(
            RecordApplicationRestorationCommand(
                document_id=document_id,
                evidence_version_id=payload.evidence_version_id,
                restored_official_procedure_stage=(
                    payload.restored_official_procedure_stage
                ),
                actor_id=current_user.id,
                effective_at=payload.effective_at,
                occurred_at=payload.occurred_at,
                idempotency_key=payload.idempotency_key,
            ),
            db,
        )
        db.commit()
    except Exception:
        db.rollback()
        raise
    return result


@router.get("/documents", response_model=DocumentListOut, summary="List documents")
def get_documents(
    q: str | None = Query(default=None),
    doc_name: str | None = Query(default=None),
    doc_type: list[DocumentDocType] | None = Query(default=None),
    direction: DocumentDirection | None = Query(default=None),
    template_code: str | None = Query(default=None),
    doc_template_id: str | None = Query(default=None),
    case_no: str | None = Query(default=None),
    case_id: str | None = Query(default=None),
    client_id: str | None = Query(default=None),
    need_reply: bool | None = Query(default=None),
    replied: bool | None = Query(default=None),
    has_attachment: bool | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    _perm: None = Depends(require_perm("Doc.Read")),
    db: Session = Depends(get_db),
) -> DocumentListOut:
    """
    List documents with filters and pagination.

    **Auth**: Bearer JWT
    **Permission**: Doc.Read
    **Request example**:
    `GET /api/v1/documents?page=1&page_size=20&direction=IN&case_id=CASE_ID`
    **Curl example**:
    ```bash
    curl -s -X GET "http://localhost:8000/api/v1/documents?page=1&page_size=20" \\
      -H "Authorization: Bearer $FPMS_TOKEN"
    ```
    **Responses**:
    - 200: List of documents
    - 401: AUTH_REQUIRED
    - 403: FORBIDDEN
    - 422: VALIDATION_ERROR
    """
    documents, total = list_documents(
        db,
        q=q,
        doc_name=doc_name,
        doc_types=doc_type,
        direction=direction,
        template_code=template_code,
        doc_template_id=doc_template_id,
        case_no=case_no,
        case_id=case_id,
        client_id=client_id,
        need_reply=need_reply,
        replied=replied,
        has_attachment=has_attachment,
        date_from=date_from,
        date_to=date_to,
        page=page,
        page_size=page_size,
    )
    # Batch-resolve case_no for all documents in this page
    case_ids = {doc.case_id for doc in documents if doc.case_id}
    case_no_map: dict[str, str] = {}
    if case_ids:
        cases = db.query(Case.id, Case.case_no).filter(Case.id.in_(case_ids)).all()
        case_no_map = {c.id: c.case_no for c in cases}
    template_ids = {doc.doc_template_id for doc in documents if doc.doc_template_id}
    template_code_map: dict[str, str] = {}
    if template_ids:
        templates = (
            db.query(DocTemplate.id, DocTemplate.code)
            .filter(DocTemplate.id.in_(template_ids))
            .all()
        )
        template_code_map = {t.id: t.code for t in templates}

    items = [
        _build_document_out(
            document,
            case_no=case_no_map.get(document.case_id) if document.case_id else None,
            template_code=template_code_map.get(document.doc_template_id)
            if document.doc_template_id
            else None,
        )
        for document in documents
    ]
    return DocumentListOut(items=items, page=page, page_size=page_size, total=total)


@router.get(
    "/documents/export",
    summary="Export document list to Excel",
    response_class=Response,
    responses={
        200: {
            "content": {DOCUMENT_LIST_EXPORT_MIME_TYPE: {}},
            "description": "Document list Excel export generated",
        }
    },
)
def export_documents(
    q: str | None = Query(default=None),
    doc_name: str | None = Query(default=None),
    doc_type: list[DocumentDocType] | None = Query(default=None),
    direction: DocumentDirection | None = Query(default=None),
    template_code: str | None = Query(default=None),
    doc_template_id: str | None = Query(default=None),
    case_no: str | None = Query(default=None),
    case_id: str | None = Query(default=None),
    client_id: str | None = Query(default=None),
    need_reply: bool | None = Query(default=None),
    replied: bool | None = Query(default=None),
    has_attachment: bool | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    _perm: None = Depends(require_perm("Doc.Read")),
    db: Session = Depends(get_db),
) -> Response:
    """Export the filtered document list as an Excel file (US-WD-06)."""
    documents, _total = list_documents(
        db,
        q=q,
        doc_name=doc_name,
        doc_types=doc_type,
        direction=direction,
        template_code=template_code,
        doc_template_id=doc_template_id,
        case_no=case_no,
        case_id=case_id,
        client_id=client_id,
        need_reply=need_reply,
        replied=replied,
        has_attachment=has_attachment,
        date_from=date_from,
        date_to=date_to,
        page=1,
        page_size=1000,
    )
    case_ids = {doc.case_id for doc in documents if doc.case_id}
    case_no_map: dict[str, str] = {}
    if case_ids:
        cases = db.query(Case.id, Case.case_no).filter(Case.id.in_(case_ids)).all()
        case_no_map = {c.id: c.case_no for c in cases}
    template_ids = {doc.doc_template_id for doc in documents if doc.doc_template_id}
    template_name_map: dict[str, str] = {}
    if template_ids:
        templates = (
            db.query(DocTemplate.id, DocTemplate.name)
            .filter(DocTemplate.id.in_(template_ids))
            .all()
        )
        template_name_map = {t.id: t.name for t in templates}

    direction_labels = {"IN": "收文", "OUT": "发文"}
    rows: list[list[object]] = [
        ["文书清单导出"],
        [],
        ["文书标题", "案号", "方向", "文书类型", "文书日期", "文号", "需答复", "答复日期"],
    ]
    for document in documents:
        direction_value = (
            document.direction.value
            if hasattr(document.direction, "value")
            else document.direction
        )
        rows.append(
            [
                document.title or "",
                case_no_map.get(document.case_id) if document.case_id else "",
                direction_labels.get(str(direction_value or ""), direction_value or ""),
                template_name_map.get(document.doc_template_id)
                if document.doc_template_id
                else "",
                document.doc_date,
                document.ref_no or "",
                "是" if document.need_reply else "否",
                document.reply_date,
            ]
        )
    content = build_document_list_export_xlsx(rows=rows)
    return Response(
        content=content,
        media_type=DOCUMENT_LIST_EXPORT_MIME_TYPE,
        headers={
            "Content-Disposition": 'attachment; filename="document-list.xlsx"',
        },
    )


@router.post(
    "/documents",
    status_code=status.HTTP_201_CREATED,
    response_model=DocumentOut,
    summary="Create a document",
)
def create_document(
    payload: DocumentCreateIn,
    response: Response,
    _perm: None = Depends(require_perm("Doc.Create")),
    db: Session = Depends(get_db),
) -> DocumentOut:
    """
    Create a document.

    **Auth**: Bearer JWT
    **Permission**: Doc.Create
    **Request example**:
    ```json
    {
      "case_id": "CASE_ID",
      "doc_template_id": null,
      "direction": "IN",
      "doc_date": "2024-01-15",
      "title": "CURL Doc Title",
      "ref_no": "DOC-REF-001",
      "extra_data": null
    }
    ```
    **Curl example**:
    ```bash
    curl -s -X POST http://localhost:8000/api/v1/documents \\
      -H "Authorization: Bearer $FPMS_TOKEN" \\
      -H "Content-Type: application/json" \\
      -d '{"case_id":"CASE_ID","doc_template_id":null,"direction":"IN","doc_date":"2024-01-15","title":"CURL Doc Title","ref_no":"DOC-REF-001","extra_data":null}'
    ```
    **Responses**:
    - 201: Document created
    - 401: AUTH_REQUIRED
    - 403: FORBIDDEN
    - 404: Case or template not found
    - 409: Task generation failed
    - 422: VALIDATION_ERROR
    """
    document = create_document_service(db, payload)

    # B3: Auto-create fee draft if template has fee_draft_type
    auto_fee_draft_id = None
    template = None
    if document.doc_template_id:
        template = db.execute(
            select(DocTemplate).where(DocTemplate.id == document.doc_template_id)
        ).scalar_one_or_none()
        if template:
            try:
                draft = maybe_create_fee_draft(db, document, template)
                if draft:
                    auto_fee_draft_id = draft.id
            except Exception:
                logging.getLogger(__name__).warning(
                    "B3: fee draft creation failed for doc %s", document.id, exc_info=True
                )
            ensure_grant_fee_task_for_notice_document(db, document=document, template=template)

    try:
        created_tasks = TaskGenerationService().generate_from_document(db, document)
    except RuntimeError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    db.commit()
    db.refresh(document)
    response.headers["X-Auto-Tasks-Created"] = str(len(created_tasks))
    if auto_fee_draft_id:
        response.headers["X-Auto-Fee-Draft-Created"] = auto_fee_draft_id
    case = db.execute(select(Case).where(Case.id == document.case_id)).scalar_one_or_none()
    return _build_document_out(document, case_no=case.case_no if case else None)


@router.post(
    "/documents/impact-preview",
    response_model=DocumentImpactPreviewOut,
    summary="Preview document create impacts",
)
def preview_document_impact_endpoint(
    payload: DocumentImpactPreviewIn,
    _perm: None = Depends(require_perm("Doc.Create")),
    db: Session = Depends(get_db),
) -> DocumentImpactPreviewOut:
    return preview_document_impact(db, payload)


@router.post(
    "/documents/wizard/task-preview",
    response_model=DocumentWizardTaskPreviewOut,
    summary="Preview task candidates from wizard batch",
)
def preview_document_wizard_tasks_endpoint(
    payload: DocumentWizardBatchCreateIn,
    _perm: None = Depends(require_perm("Doc.Create")),
    db: Session = Depends(get_db),
) -> DocumentWizardTaskPreviewOut:
    try:
        items = preview_document_wizard_tasks(db, payload)
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    return DocumentWizardTaskPreviewOut(total_candidates=len(items), items=items)


@router.post(
    "/documents/wizard/fee-preview",
    response_model=DocumentWizardFeePreviewOut,
    summary="Preview fee candidates from wizard batch",
)
def preview_document_wizard_fee_candidates_endpoint(
    payload: DocumentWizardFeePreviewIn,
    _perm: None = Depends(require_perm("Doc.Create")),
    db: Session = Depends(get_db),
) -> DocumentWizardFeePreviewOut:
    try:
        items = preview_document_wizard_fee_candidates(db, payload)
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    return DocumentWizardFeePreviewOut(total_candidates=len(items), items=items)


@router.post(
    "/documents/wizard/attachment-preview",
    response_model=DocumentWizardAttachmentPreviewOut,
    summary="Preview attachment candidates from wizard batch",
)
def preview_document_wizard_attachment_candidates_endpoint(
    payload: DocumentWizardAttachmentPreviewIn,
    _perm: None = Depends(require_perm("Doc.Create")),
    db: Session = Depends(get_db),
) -> DocumentWizardAttachmentPreviewOut:
    try:
        items = preview_document_wizard_attachment_candidates(db, payload)
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    return DocumentWizardAttachmentPreviewOut(total_candidates=len(items), items=items)


@router.post(
    "/documents/wizard/batch-create",
    status_code=status.HTTP_201_CREATED,
    response_model=DocumentWizardBatchCreateOut,
    summary="Create documents from wizard batch with Step 3 task rows and Step 4 fee rows",
)
def create_document_wizard_batch_endpoint(
    payload: DocumentWizardBatchCreateIn,
    _perm: None = Depends(require_perm("Doc.Create")),
    current_user: T_User = current_user_dep,
    db: Session = Depends(get_db),
) -> DocumentWizardBatchCreateOut:
    created_rows = create_document_wizard_batch(db, payload, actor_id=current_user.id)
    case_ids = {document.case_id for _, document in created_rows}
    case_no_map: dict[str, str] = {}
    if case_ids:
        cases = db.query(Case.id, Case.case_no).filter(Case.id.in_(case_ids)).all()
        case_no_map = {c.id: c.case_no for c in cases}

    items = [
        {
            "row_index": row_index,
            "document": _build_document_out(
                document,
                case_no=case_no_map.get(document.case_id),
            ),
        }
        for row_index, document in created_rows
    ]
    return DocumentWizardBatchCreateOut(created=len(items), total=len(created_rows), items=items)


@router.post(
    "/documents/dispatch/mailing/batch-register",
    response_model=DocumentMailingBatchOut,
    summary="Batch register outgoing mailing info",
)
def batch_register_document_mailing_endpoint(
    payload: DocumentMailingBatchIn,
    _perm: None = Depends(require_perm("Doc.Edit")),
    db: Session = Depends(get_db),
) -> DocumentMailingBatchOut:
    documents = batch_register_document_mailing(db, payload, user_id="system")
    case_ids = {document.case_id for document in documents if document.case_id}
    case_no_map: dict[str, str] = {}
    if case_ids:
        cases = db.query(Case.id, Case.case_no).filter(Case.id.in_(case_ids)).all()
        case_no_map = {c.id: c.case_no for c in cases}

    items = [
        _build_document_mailing_batch_item_out(
            document,
            case_no=case_no_map.get(document.case_id) if document.case_id else None,
        )
        for document in documents
    ]
    return DocumentMailingBatchOut(
        success_count=len(items),
        failure_count=0,
        items=items,
    )


@router.post(
    "/documents/dispatches",
    response_model=DocumentDispatchOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a document dispatch sheet",
)
def create_document_dispatch_endpoint(
    payload: DocumentDispatchCreateIn,
    _perm: None = Depends(require_perm("Doc.Edit")),
    db: Session = Depends(get_db),
) -> DocumentDispatchOut:
    dispatch = create_document_dispatch(db, payload, user_id="system")
    client = db.execute(select(Client).where(Client.id == dispatch.client_id)).scalar_one_or_none()
    return _build_document_dispatch_out(dispatch, client_name=client.name_cn if client else None)


@router.get(
    "/documents/dispatches/{dispatch_id}",
    response_model=DocumentDispatchOut,
    summary="Get a document dispatch sheet",
)
def get_document_dispatch_endpoint(
    dispatch_id: str,
    _perm: None = Depends(require_perm("Doc.Read")),
    db: Session = Depends(get_db),
) -> DocumentDispatchOut:
    dispatch = get_document_dispatch(db, dispatch_id)
    client = db.execute(select(Client).where(Client.id == dispatch.client_id)).scalar_one_or_none()
    return _build_document_dispatch_out(dispatch, client_name=client.name_cn if client else None)


@router.get(
    "/documents/{document_id}/envelope-preview",
    response_model=DocumentEnvelopePreviewOut,
    summary="Preview envelope data for a document",
)
def get_document_envelope_preview_endpoint(
    document_id: str,
    _perm: None = Depends(require_perm("Doc.Read")),
    db: Session = Depends(get_db),
) -> DocumentEnvelopePreviewOut:
    return get_document_envelope_preview(db, document_id=document_id)


@router.get(
    "/documents/{document_id}/attachments/{attachment_id}/download",
    summary="Download a document attachment",
)
def download_attachment(
    document_id: str,
    attachment_id: str,
    _perm: None = Depends(require_perm("Doc.Attach")),
    db: Session = Depends(get_db),
) -> FileResponse:
    """
    Download a document attachment file.

    **Auth**: Bearer JWT
    **Permission**: Doc.Attach
    **Request example**:
    `GET /api/v1/documents/DOCUMENT_ID/attachments/ATTACHMENT_ID/download`
    **Curl example**:
    ```bash
    curl -s -X GET \\
      "http://localhost:8000/api/v1/documents/DOCUMENT_ID/attachments/ATTACHMENT_ID/download" \\
      -H "Authorization: Bearer $FPMS_TOKEN" \\
      -o attachment.bin
    ```
    **Responses**:
    - 200: File download
    - 401: AUTH_REQUIRED
    - 403: FORBIDDEN
    - 404: Document or attachment not found
    - 422: VALIDATION_ERROR
    """
    settings = get_settings()
    abs_path, filename, mime_type = get_attachment_download(
        db,
        document_id=document_id,
        attachment_id=attachment_id,
        storage_dir=settings.storage_dir,
    )
    return FileResponse(path=abs_path, filename=filename, media_type=mime_type)


@router.get(
    "/documents/{document_id}",
    response_model=DocumentOut,
    summary="Get a document",
)
def get_document(
    document_id: str,
    _perm: None = Depends(require_perm("Doc.Read")),
    db: Session = Depends(get_db),
) -> DocumentOut:
    """
    Get a document by ID (includes attachments).

    **Auth**: Bearer JWT
    **Permission**: Doc.Read
    **Request example**:
    `GET /api/v1/documents/DOCUMENT_ID`
    **Curl example**:
    ```bash
    curl -s -X GET http://localhost:8000/api/v1/documents/DOCUMENT_ID \\
      -H "Authorization: Bearer $FPMS_TOKEN"
    ```
    **Responses**:
    - 200: Document details
    - 401: AUTH_REQUIRED
    - 403: FORBIDDEN
    - 404: Document not found
    - 422: VALIDATION_ERROR
    """
    document = get_document_service(db, document_id)
    case = db.execute(select(Case).where(Case.id == document.case_id)).scalar_one_or_none()
    evidence_versions = get_current_attachment_evidence_versions(
        db,
        document=document,
    )
    attachments = []
    for attachment in document.attachments:
        evidence_version = evidence_versions.get(attachment.id)
        attachments.append(
            {
                "id": attachment.id,
                "document_id": attachment.document_id,
                "file_name": attachment.file_name,
                "mime_type": attachment.mime_type or "",
                "file_size": attachment.file_size or 0,
                "uploaded_at": attachment.created_at,
                "official_file_role": attachment.official_file_role,
                "source_role_alias": attachment.source_role_alias,
                "external_upload_position": attachment.external_upload_position,
                "content_hash": attachment.content_hash,
                "package_usage_hint": attachment.package_usage_hint,
                "is_archive_evidence": bool(attachment.is_archive_evidence),
                "is_receipt_evidence": bool(attachment.is_receipt_evidence),
                "evidence_version_id": (
                    evidence_version.evidence_version_id
                    if evidence_version is not None
                    else None
                ),
                "role": (
                    evidence_version.role.value if evidence_version is not None else None
                ),
                "creator_id": (
                    evidence_version.creator_id if evidence_version is not None else None
                ),
                "reviewer_id": (
                    evidence_version.reviewer_id if evidence_version is not None else None
                ),
                "review_state": (
                    evidence_version.review_state.value
                    if evidence_version is not None
                    else None
                ),
                "is_current": bool(
                    evidence_version is not None and evidence_version.is_current
                ),
                "is_final": bool(evidence_version is not None and evidence_version.is_final),
            }
        )
    return _build_document_out(
        document,
        case_no=case.case_no if case else None,
        attachments=attachments,
    )


@router.put(
    "/documents/{document_id}",
    response_model=DocumentOut,
    summary="Update a document",
)
def update_document(
    document_id: str,
    payload: DocumentUpdateIn,
    _perm: None = Depends(require_perm("Doc.Edit")),
    db: Session = Depends(get_db),
) -> DocumentOut:
    """
    Update a document by ID.

    **Auth**: Bearer JWT
    **Permission**: Doc.Edit
    **Request example**:
    ```json
    {"title": "Updated Document Title", "ref_no": "DOC-REF-002"}
    ```
    **Curl example**:
    ```bash
    curl -s -X PUT http://localhost:8000/api/v1/documents/DOCUMENT_ID \\
      -H "Authorization: Bearer $FPMS_TOKEN" \\
      -H "Content-Type: application/json" \\
      -d '{"title":"Updated Document Title","ref_no":"DOC-REF-002"}'
    ```
    **Responses**:
    - 200: Document updated
    - 401: AUTH_REQUIRED
    - 403: FORBIDDEN
    - 404: Document, case, or template not found
    - 422: VALIDATION_ERROR
    """
    document = update_document_service(db, document_id, payload)
    case = db.execute(select(Case).where(Case.id == document.case_id)).scalar_one_or_none()
    return _build_document_out(document, case_no=case.case_no if case else None)


@router.post(
    "/documents/{document_id}/attachments",
    status_code=status.HTTP_201_CREATED,
    response_model=DocAttachmentOut,
    response_model_exclude={
        "evidence_version_id",
        "role",
        "creator_id",
        "reviewer_id",
        "review_state",
        "is_current",
        "is_final",
    },
    summary="Upload a document attachment",
)
def add_attachment(
    document_id: str,
    file: UploadFile = File(...),
    official_file_role: str | None = Form(default=None),
    source_role_alias: str | None = Form(default=None),
    _perm: None = Depends(require_perm("Doc.Attach")),
    current_user: T_User = current_user_dep,
    db: Session = Depends(get_db),
) -> DocAttachmentOut:
    """
    Upload a document attachment.

    **Auth**: Bearer JWT
    **Permission**: Doc.Attach
    **Request example**:
    `POST /api/v1/documents/DOCUMENT_ID/attachments (multipart form file)`
    **Curl example**:
    ```bash
    curl -s -X POST http://localhost:8000/api/v1/documents/DOCUMENT_ID/attachments \\
      -H "Authorization: Bearer $FPMS_TOKEN" \\
      -F "file=@/path/to/file.pdf" \\
      -F "official_file_role=OA_STATEMENT_PDF" \\
      -F "source_role_alias=OA意见陈述 PDF"
    ```
    **Responses**:
    - 201: Attachment uploaded
    - 400: Attachment validation failed
    - 401: AUTH_REQUIRED
    - 403: FORBIDDEN
    - 404: Document not found
    - 422: VALIDATION_ERROR
    """
    settings = get_settings()
    try:
        pending = add_attachment_service(
            db,
            document_id,
            upload_file=file,
            storage_dir=settings.storage_dir,
            actor_id=current_user.id,
            official_file_role=official_file_role,
            source_role_alias=source_role_alias,
        )
    except Exception:
        db.rollback()
        raise

    try:
        db.commit()
    except Exception as exc:
        db.rollback()
        _remove_managed_attachment_file(pending.managed_file_path, original_error=exc)
        raise BusinessError(
            "ATTACHMENT_PERSIST_FAILED",
            "Attachment persistence failed",
            status_code=500,
        ) from exc

    attachment = pending.attachment
    return DocAttachmentOut(
        id=attachment.id,
        document_id=attachment.document_id,
        file_name=attachment.file_name,
        mime_type=attachment.mime_type or "",
        file_size=attachment.file_size or 0,
        uploaded_at=attachment.created_at,
        official_file_role=attachment.official_file_role,
        source_role_alias=attachment.source_role_alias,
        external_upload_position=attachment.external_upload_position,
        content_hash=attachment.content_hash,
        package_usage_hint=attachment.package_usage_hint,
        is_archive_evidence=bool(attachment.is_archive_evidence),
        is_receipt_evidence=bool(attachment.is_receipt_evidence),
    )
