from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
from uuid import uuid4

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.core.errors import raise_business_error
from app.core.storage import ensure_dir, safe_join
from app.modules.cases.models import Case
from app.modules.cases.service import validate_case_status_transition
from app.modules.documents.enums import DocumentDirection
from app.modules.documents.fee_linking_service import maybe_create_fee_draft
from app.modules.documents.models import DocAttachment, DocTemplate, Document
from app.modules.documents.schemas import (
    DocTemplateCreateIn,
    DocTemplateUpdateIn,
    DocumentCreateIn,
    DocumentUpdateIn,
    DocumentWizardBatchCreateIn,
    DocumentWizardBatchRowIn,
)
from app.modules.tasks.enums import TaskAction, TaskStatus
from app.modules.tasks.models import Task
from app.modules.tasks.service import _create_task_log
from app.modules.tasks.task_generation_service import TaskGenerationService


def _apply_template_defaults(
    *,
    case: Case,
    document: Document,
    template: DocTemplate | None,
    need_reply_overridden: bool = False,
) -> None:
    if not template:
        return

    if not need_reply_overridden and getattr(template, "need_reply", None) is not None:
        document.need_reply = template.need_reply

    if getattr(template, "status_effect", None) and document.direction == DocumentDirection.IN:
        validate_case_status_transition(case.status, template.status_effect)
        case.status = template.status_effect

    if (
        getattr(template, "status_restore", None)
        and document.direction == DocumentDirection.OUT
        and document.reply_to_id
    ):
        validate_case_status_transition(case.status, template.status_restore)
        case.status = template.status_restore


def _apply_reply_chain(db: Session, *, document: Document, doc_date: date | None) -> None:
    if not document.reply_to_id or document.direction != DocumentDirection.OUT:
        return

    original_doc = db.execute(
        select(Document).where(Document.id == document.reply_to_id)
    ).scalar_one_or_none()
    if not original_doc:
        raise_business_error(
            "REPLY_TO_DOC_NOT_FOUND", "Reply-to document not found", status_code=404
        )

    open_tasks = (
        db.execute(
            select(Task).where(
                Task.document_id == document.reply_to_id,
                Task.status == TaskStatus.OPEN.value,
            )
        )
        .scalars()
        .all()
    )

    for task in open_tasks:
        task.status = TaskStatus.DONE.value
        task.done_at = datetime.utcnow()
        _create_task_log(
            db,
            task_id=task.id,
            action=TaskAction.AUTO_WRITEOFF,
            from_status=TaskStatus.OPEN.value,
            to_status=TaskStatus.DONE.value,
            remark=f"Auto write-off: reply document {document.id}",
        )

    original_doc.reply_date = doc_date


def _normalize_text(value: str | None) -> str | None:
    if value is None:
        return None
    text = value.strip()
    return text or None


def _create_document_record(
    db: Session,
    data: DocumentCreateIn,
    *,
    commit: bool,
) -> Document:
    case = db.execute(select(Case).where(Case.id == data.case_id)).scalar_one_or_none()
    if not case:
        raise_business_error("CASE_NOT_FOUND", "Case not found", status_code=404)

    template = None
    if data.doc_template_id:
        template = db.execute(
            select(DocTemplate).where(DocTemplate.id == data.doc_template_id)
        ).scalar_one_or_none()
        if not template:
            raise_business_error(
                "DOC_TEMPLATE_NOT_FOUND", "Doc template not found", status_code=404
            )

    document = Document(
        id=str(uuid4()),
        case_id=data.case_id,
        doc_template_id=data.doc_template_id,
        direction=data.direction,
        doc_date=data.doc_date,
        title=data.title,
        ref_no=data.ref_no,
        extra_data=data.extra_data,
        reply_to_id=data.reply_to_id,
    )
    db.add(document)
    db.flush()

    _apply_template_defaults(case=case, document=document, template=template)
    _apply_reply_chain(db, document=document, doc_date=data.doc_date)

    if commit:
        db.commit()
        db.refresh(document)
    return document


def list_documents(
    db: Session,
    *,
    q: str | None = None,
    direction: DocumentDirection | None = None,
    doc_template_id: str | None = None,
    case_id: str | None = None,
    client_id: str | None = None,
    need_reply: bool | None = None,
    replied: bool | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[Document], int]:
    """List documents with filters and pagination."""
    stmt = select(Document)

    if q:
        q_like = f"%{q.lower()}%"
        stmt = stmt.where(
            or_(
                func.lower(Document.title).like(q_like),
                func.lower(Document.ref_no).like(q_like),
            )
        )

    if direction:
        stmt = stmt.where(Document.direction == direction)
    if doc_template_id:
        stmt = stmt.where(Document.doc_template_id == doc_template_id)
    if case_id:
        stmt = stmt.where(Document.case_id == case_id)
    if client_id:
        stmt = stmt.join(Case, Document.case_id == Case.id).where(Case.client_id == client_id)
    if need_reply is not None:
        stmt = stmt.where(Document.need_reply.is_(need_reply))
    if replied is True:
        stmt = stmt.where(Document.reply_date.is_not(None))
    elif replied is False:
        stmt = stmt.where(Document.reply_date.is_(None))
    if date_from:
        stmt = stmt.where(Document.doc_date >= date_from)
    if date_to:
        stmt = stmt.where(Document.doc_date <= date_to)

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = db.execute(count_stmt).scalar_one()

    offset = (page - 1) * page_size
    stmt = (
        stmt.order_by(
            Document.doc_date.desc(),
            Document.created_at.desc(),
            Document.id.desc(),
        )
        .offset(offset)
        .limit(page_size)
    )

    items = db.execute(stmt).scalars().all()
    return items, total


def create_document(db: Session, data: DocumentCreateIn) -> Document:
    return _create_document_record(db, data, commit=True)


def create_document_wizard_batch(
    db: Session, data: DocumentWizardBatchCreateIn
) -> list[tuple[int, Document]]:
    template = db.execute(
        select(DocTemplate).where(DocTemplate.id == data.defaults.doc_template_id)
    ).scalar_one_or_none()
    if not template:
        raise_business_error("DOC_TEMPLATE_NOT_FOUND", "Doc template not found", status_code=404)

    rows = data.rows
    row_errors: list[dict[str, object]] = []
    seen_case_ids: set[str] = set()
    case_ids: list[str] = []

    for idx, row in enumerate(rows, start=1):
        case_id = _normalize_text(row.case_id)
        if not case_id:
            row_errors.append(
                {
                    "row_index": idx,
                    "field": "case_id",
                    "code": "CASE_ID_REQUIRED",
                    "message": "Case ID is required",
                }
            )
            continue
        if case_id in seen_case_ids:
            row_errors.append(
                {
                    "row_index": idx,
                    "field": "case_id",
                    "code": "CASE_ID_DUPLICATE",
                    "message": "Case ID must be unique within the batch",
                }
            )
            continue
        seen_case_ids.add(case_id)
        case_ids.append(case_id)

    existing_case_ids = set(
        db.execute(select(Case.id).where(Case.id.in_(case_ids))).scalars().all()
    )
    for idx, row in enumerate(rows, start=1):
        case_id = _normalize_text(row.case_id)
        if case_id and case_id not in existing_case_ids:
            row_errors.append(
                {
                    "row_index": idx,
                    "field": "case_id",
                    "code": "CASE_NOT_FOUND",
                    "message": "Case not found",
                    "case_id": case_id,
                }
            )

    if row_errors:
        raise_business_error(
            "DOCUMENT_WIZARD_BATCH_INVALID",
            "Document wizard batch contains invalid rows",
            details={"row_errors": row_errors},
            status_code=400,
        )

    created_rows: list[tuple[int, Document]] = []
    try:
        for idx, row in enumerate(rows, start=1):
            payload = _build_document_wizard_payload(data.defaults, row, template)
            document = _create_document_record(db, payload, commit=False)
            maybe_create_fee_draft(db, document, template)
            TaskGenerationService().generate_from_document(db, document)
            created_rows.append((idx, document))

        db.commit()
        for _, document in created_rows:
            db.refresh(document)
        return created_rows
    except Exception:
        db.rollback()
        raise


def _build_document_wizard_payload(
    defaults,
    row: DocumentWizardBatchRowIn,
    template: DocTemplate,
) -> DocumentCreateIn:
    data = defaults.model_dump()
    row_data = row.model_dump(exclude_unset=True)
    data.update(row_data)
    data["case_id"] = _normalize_text(row.case_id)
    data["doc_template_id"] = defaults.doc_template_id
    data["direction"] = defaults.direction

    if data.get("doc_date") is None:
        data["doc_date"] = defaults.doc_date

    data["title"] = _normalize_text(data.get("title")) or template.name
    data["ref_no"] = _normalize_text(data.get("ref_no"))
    data["extra_data"] = _normalize_text(data.get("extra_data"))
    data["reply_to_id"] = _normalize_text(data.get("reply_to_id"))

    return DocumentCreateIn(**data)


def get_document(db: Session, document_id: str) -> Document:
    stmt = (
        select(Document)
        .where(Document.id == document_id)
        .options(selectinload(Document.attachments))
    )
    document = db.execute(stmt).scalar_one_or_none()
    if not document:
        raise_business_error("DOCUMENT_NOT_FOUND", "Document not found", status_code=404)
    return document


def update_document(db: Session, document_id: str, data: DocumentUpdateIn) -> Document:
    document = db.execute(select(Document).where(Document.id == document_id)).scalar_one_or_none()
    if not document:
        raise_business_error("DOCUMENT_NOT_FOUND", "Document not found", status_code=404)

    updates = data.model_dump(exclude_unset=True)
    case = db.execute(select(Case).where(Case.id == document.case_id)).scalar_one_or_none()
    if not case:
        raise_business_error("CASE_NOT_FOUND", "Case not found", status_code=404)

    template = None

    if "case_id" in updates:
        case = db.execute(select(Case).where(Case.id == updates["case_id"])).scalar_one_or_none()
        if not case:
            raise_business_error("CASE_NOT_FOUND", "Case not found", status_code=404)

    if "doc_template_id" in updates and updates["doc_template_id"] is not None:
        template = db.execute(
            select(DocTemplate).where(DocTemplate.id == updates["doc_template_id"])
        ).scalar_one_or_none()
        if not template:
            raise_business_error(
                "DOC_TEMPLATE_NOT_FOUND", "Doc template not found", status_code=404
            )
    elif document.doc_template_id:
        template = db.execute(
            select(DocTemplate).where(DocTemplate.id == document.doc_template_id)
        ).scalar_one_or_none()

    for field, value in updates.items():
        setattr(document, field, value)

    _apply_template_defaults(
        case=case,
        document=document,
        template=template,
        need_reply_overridden="need_reply" in updates,
    )
    if "reply_to_id" in updates or (
        "doc_template_id" in updates and getattr(template, "status_restore", None)
    ):
        _apply_reply_chain(db, document=document, doc_date=document.doc_date)

    db.commit()
    db.refresh(document)
    return document


def add_attachment(
    db: Session,
    document_id: str,
    upload_file,
    storage_dir: str,
    actor_id: str | None = None,
) -> DocAttachment:
    document = db.execute(select(Document).where(Document.id == document_id)).scalar_one_or_none()
    if not document:
        raise_business_error("DOCUMENT_NOT_FOUND", "Document not found", status_code=404)

    original_name = (upload_file.filename or "").strip()
    if not original_name:
        raise_business_error(
            "ATTACHMENT_FILENAME_REQUIRED",
            "Attachment filename is required",
            status_code=400,
        )

    allowed_mime_types: set[str] | None = None
    allowed_exts: set[str] | None = None

    content_type = upload_file.content_type or "application/octet-stream"
    ext = Path(original_name).suffix.lower()
    if allowed_mime_types and content_type not in allowed_mime_types:
        raise_business_error(
            "ATTACHMENT_MIME_NOT_ALLOWED",
            "Attachment mime type not allowed",
            status_code=400,
        )
    if allowed_exts and ext not in allowed_exts:
        raise_business_error(
            "ATTACHMENT_EXTENSION_NOT_ALLOWED",
            "Attachment extension not allowed",
            status_code=400,
        )

    max_size_bytes = 25 * 1024 * 1024
    stored_name = f"{uuid4().hex}_{Path(original_name).name}"
    relative_path = f"attachments/{document_id}/{stored_name}"
    dest_path = safe_join(storage_dir, relative_path)
    ensure_dir(str(Path(dest_path).parent))

    size_bytes = 0
    try:
        with open(dest_path, "wb") as f:
            while True:
                chunk = upload_file.file.read(1024 * 1024)
                if not chunk:
                    break
                size_bytes += len(chunk)
                if size_bytes > max_size_bytes:
                    raise_business_error(
                        "ATTACHMENT_TOO_LARGE",
                        "Attachment exceeds size limit",
                        status_code=400,
                    )
                f.write(chunk)
    except Exception:
        try:
            Path(dest_path).unlink()
        except FileNotFoundError:
            pass
        raise

    attachment = DocAttachment(
        id=str(uuid4()),
        document_id=document_id,
        file_name=original_name,
        file_path=relative_path,
        mime_type=content_type,
        file_size=size_bytes,
    )
    db.add(attachment)
    db.commit()
    db.refresh(attachment)
    return attachment


def get_attachment_download(
    db: Session,
    document_id: str,
    attachment_id: str,
    storage_dir: str,
) -> tuple[str, str, str]:
    document = db.execute(select(Document).where(Document.id == document_id)).scalar_one_or_none()
    if not document:
        raise_business_error("DOCUMENT_NOT_FOUND", "Document not found", status_code=404)

    attachment = db.execute(
        select(DocAttachment).where(
            DocAttachment.id == attachment_id,
            DocAttachment.document_id == document_id,
        )
    ).scalar_one_or_none()
    if not attachment:
        raise_business_error("ATTACHMENT_NOT_FOUND", "Attachment not found", status_code=404)

    abs_path = safe_join(storage_dir, attachment.file_path)
    if not Path(abs_path).exists():
        raise_business_error("ATTACHMENT_NOT_FOUND", "Attachment not found", status_code=404)

    mime_type = attachment.mime_type or "application/octet-stream"
    return (abs_path, attachment.file_name, mime_type)


# ---------------------------------------------------------------------------
# B1: DocTemplate CRUD
# ---------------------------------------------------------------------------


def list_doc_templates(
    db: Session,
    *,
    direction: DocumentDirection | None = None,
    enabled: bool | None = None,
    q: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[DocTemplate], int]:
    """List doc templates with optional filters and pagination."""
    stmt = select(DocTemplate)

    if direction:
        stmt = stmt.where(DocTemplate.direction == direction)
    if enabled is not None:
        stmt = stmt.where(DocTemplate.enabled == enabled)
    if q:
        q_like = f"%{q.lower()}%"
        stmt = stmt.where(
            or_(
                func.lower(DocTemplate.code).like(q_like),
                func.lower(DocTemplate.name).like(q_like),
            )
        )

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = db.execute(count_stmt).scalar_one()

    offset = (page - 1) * page_size
    stmt = stmt.order_by(DocTemplate.code.asc()).offset(offset).limit(page_size)
    items = db.execute(stmt).scalars().all()
    return items, total


def get_doc_template(db: Session, template_id: str) -> DocTemplate:
    """Get a single doc template by ID. Raises 404 if not found."""
    template = db.execute(
        select(DocTemplate).where(DocTemplate.id == template_id)
    ).scalar_one_or_none()
    if not template:
        raise_business_error("DOC_TEMPLATE_NOT_FOUND", "Doc template not found", status_code=404)
    return template


def create_doc_template(db: Session, data: DocTemplateCreateIn) -> DocTemplate:
    """Create a new doc template. Raises 409 if code already exists."""
    existing = db.execute(
        select(DocTemplate).where(DocTemplate.code == data.code)
    ).scalar_one_or_none()
    if existing:
        raise_business_error(
            "DOC_TEMPLATE_CODE_EXISTS",
            f"Doc template code '{data.code}' already exists",
            status_code=409,
        )

    template = DocTemplate(
        id=str(uuid4()),
        code=data.code,
        name=data.name,
        direction=data.direction,
        enabled=data.enabled,
        status_effect=data.status_effect,
        status_restore=data.status_restore,
        deadline_template_code=data.deadline_template_code,
        fee_draft_type=data.fee_draft_type,
        fee_item_list=data.fee_item_list,
        need_reply=data.need_reply,
        reply_to_template_code=data.reply_to_template_code,
        input_fields=data.input_fields,
    )
    db.add(template)
    db.commit()
    db.refresh(template)
    return template


def update_doc_template(db: Session, template_id: str, data: DocTemplateUpdateIn) -> DocTemplate:
    """Update an existing doc template. Raises 404 if not found."""
    template = db.execute(
        select(DocTemplate).where(DocTemplate.id == template_id)
    ).scalar_one_or_none()
    if not template:
        raise_business_error("DOC_TEMPLATE_NOT_FOUND", "Doc template not found", status_code=404)

    updates = data.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(template, field, value)

    db.commit()
    db.refresh(template)
    return template
