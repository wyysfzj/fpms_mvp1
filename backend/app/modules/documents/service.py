from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
from uuid import uuid4

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.core.errors import raise_business_error
from app.core.storage import ensure_dir, safe_join
from app.modules.cases.models import Case
from app.modules.documents.enums import DocumentDirection
from app.modules.documents.models import DocAttachment, DocTemplate, Document
from app.modules.documents.schemas import (
    DocTemplateCreateIn,
    DocTemplateUpdateIn,
    DocumentCreateIn,
    DocumentUpdateIn,
)
from app.modules.tasks.enums import TaskAction, TaskStatus
from app.modules.tasks.models import Task
from app.modules.tasks.service import _create_task_log


def list_documents(
    db: Session,
    *,
    q: str | None = None,
    direction: DocumentDirection | None = None,
    doc_template_id: str | None = None,
    case_id: str | None = None,
    client_id: str | None = None,
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

    # B2: DocTemplate cascade
    if data.doc_template_id and template:
        # Propagate need_reply from template to document
        if getattr(template, "need_reply", None):
            document.need_reply = True

        # Apply status_effect to case
        if getattr(template, "status_effect", None):
            case.status = template.status_effect

    # B2: Reply chain — auto write-off
    if data.reply_to_id and data.direction == DocumentDirection.OUT:
        original_doc = db.execute(
            select(Document).where(Document.id == data.reply_to_id)
        ).scalar_one_or_none()
        if not original_doc:
            raise_business_error(
                "REPLY_TO_DOC_NOT_FOUND", "Reply-to document not found", status_code=404
            )

        # Find OPEN tasks linked to the original document
        open_tasks = (
            db.execute(
                select(Task).where(
                    Task.document_id == data.reply_to_id,
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

        # Update original document's reply_date
        original_doc.reply_date = data.doc_date

    db.commit()
    db.refresh(document)
    return document


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

    for field, value in updates.items():
        setattr(document, field, value)

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
