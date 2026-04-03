from __future__ import annotations

import logging
from datetime import date

from fastapi import APIRouter, Depends, File, HTTPException, Query, Response, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_perm
from app.core.config import get_settings
from app.db.session import get_db
from app.modules.cases.models import Case
from app.modules.documents.enums import DocumentDirection
from app.modules.documents.fee_linking_service import maybe_create_fee_draft
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
    DocumentListOut,
    DocumentMailingBatchIn,
    DocumentMailingBatchItemOut,
    DocumentMailingBatchOut,
    DocumentOut,
    DocumentUpdateIn,
    DocumentWizardBatchCreateIn,
    DocumentWizardBatchCreateOut,
    DocumentWizardTaskPreviewOut,
)
from app.modules.documents.service import (
    add_attachment as add_attachment_service,
)
from app.modules.documents.service import (
    batch_register_document_mailing,
    create_doc_template,
    create_document_dispatch,
    create_document_wizard_batch,
    get_attachment_download,
    get_doc_template,
    get_document_dispatch,
    get_document_envelope_preview,
    list_doc_templates,
    list_documents,
    preview_document_wizard_tasks,
    update_doc_template,
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
from app.modules.masterdata.clients.models import Client
from app.modules.tasks.task_generation_service import TaskGenerationService

router = APIRouter()


def _build_document_out(
    document, *, case_no: str | None = None, attachments: list | None = None
) -> DocumentOut:
    return DocumentOut(
        id=document.id,
        case_id=document.case_id,
        case_no=case_no,
        doc_template_id=document.doc_template_id,
        direction=document.direction,
        doc_date=document.doc_date,
        title=document.title,
        ref_no=document.ref_no,
        extra_data=document.extra_data,
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


@router.get("/documents", response_model=DocumentListOut, summary="List documents")
def get_documents(
    q: str | None = Query(default=None),
    doc_name: str | None = Query(default=None),
    direction: DocumentDirection | None = Query(default=None),
    template_code: str | None = Query(default=None),
    doc_template_id: str | None = Query(default=None),
    case_no: str | None = Query(default=None),
    case_id: str | None = Query(default=None),
    client_id: str | None = Query(default=None),
    need_reply: bool | None = Query(default=None),
    replied: bool | None = Query(default=None),
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
        direction=direction,
        template_code=template_code,
        doc_template_id=doc_template_id,
        case_no=case_no,
        case_id=case_id,
        client_id=client_id,
        need_reply=need_reply,
        replied=replied,
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
        DocumentOut(
            id=document.id,
            case_id=document.case_id,
            case_no=case_no_map.get(document.case_id) if document.case_id else None,
            doc_template_id=document.doc_template_id,
            template_code=template_code_map.get(document.doc_template_id)
            if document.doc_template_id
            else None,
            direction=document.direction,
            doc_date=document.doc_date,
            title=document.title,
            ref_no=document.ref_no,
            extra_data=document.extra_data,
            reply_to_id=document.reply_to_id,
            need_reply=document.need_reply,
            reply_date=document.reply_date,
            created_at=document.created_at,
            updated_at=document.updated_at,
        )
        for document in documents
    ]
    return DocumentListOut(items=items, page=page, page_size=page_size, total=total)


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
    "/documents/wizard/batch-create",
    status_code=status.HTTP_201_CREATED,
    response_model=DocumentWizardBatchCreateOut,
    summary="Create documents from wizard batch",
)
def create_document_wizard_batch_endpoint(
    payload: DocumentWizardBatchCreateIn,
    _perm: None = Depends(require_perm("Doc.Create")),
    db: Session = Depends(get_db),
) -> DocumentWizardBatchCreateOut:
    created_rows = create_document_wizard_batch(db, payload)
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
    return _build_document_out(
        document,
        case_no=case.case_no if case else None,
        attachments=[
            {
                "id": attachment.id,
                "document_id": attachment.document_id,
                "file_name": attachment.file_name,
                "mime_type": attachment.mime_type or "",
                "file_size": attachment.file_size or 0,
                "uploaded_at": attachment.created_at,
            }
            for attachment in document.attachments
        ],
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
    summary="Upload a document attachment",
)
def add_attachment(
    document_id: str,
    file: UploadFile = File(...),
    _perm: None = Depends(require_perm("Doc.Attach")),
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
      -F "file=@/path/to/file.pdf"
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
    attachment = add_attachment_service(
        db,
        document_id,
        upload_file=file,
        storage_dir=settings.storage_dir,
        actor_id=None,
    )
    return DocAttachmentOut(
        id=attachment.id,
        document_id=attachment.document_id,
        file_name=attachment.file_name,
        mime_type=attachment.mime_type or "",
        file_size=attachment.file_size or 0,
        uploaded_at=attachment.created_at,
    )
