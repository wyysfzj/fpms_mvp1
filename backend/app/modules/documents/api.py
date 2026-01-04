from __future__ import annotations

from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.api.deps import require_perm
from app.db.session import get_db
from app.modules.documents.models import DocAttachment, Document
from app.modules.tasks.task_generation_service import TaskGenerationService

router = APIRouter()


@router.get("/documents")
def get_documents(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1),
    _perm: None = Depends(require_perm("Doc.Read")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    query = db.query(Document)
    total = query.count()
    documents = (
        query.order_by(Document.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    items = [
        {
            "id": document.id,
            "case_id": document.case_id,
            "doc_template_id": document.doc_template_id,
            "direction": document.direction,
        }
        for document in documents
    ]
    return {"items": items, "page": page, "page_size": page_size, "total": total}


@router.post("/documents", status_code=status.HTTP_201_CREATED)
def create_document(
    payload: dict[str, Any],
    response: Response,
    _perm: None = Depends(require_perm("Doc.Create")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    case_id = payload.get("case_id")
    if not case_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="case_id is required")

    document = Document(
        id=str(uuid4()),
        case_id=case_id,
        doc_template_id=payload.get("doc_template_id"),
        direction=payload.get("direction") or "IN",
        doc_date=payload.get("doc_date"),
        title=payload.get("title"),
    )
    db.add(document)
    try:
        created_tasks = TaskGenerationService().generate_from_document(db, document)
    except RuntimeError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    db.commit()
    db.refresh(document)
    response.headers["X-Auto-Tasks-Created"] = str(len(created_tasks))
    return {
        "id": document.id,
        "case_id": document.case_id,
        "doc_template_id": document.doc_template_id,
        "direction": document.direction,
        "doc_date": str(document.doc_date) if document.doc_date else None,
        "title": document.title,
    }


@router.get("/documents/{document_id}/attachments/{attachment_id}/download")
def download_attachment(
    document_id: str,
    attachment_id: str,
    _perm: None = Depends(require_perm("Doc.Attach")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    attachment = (
        db.query(DocAttachment)
        .filter(DocAttachment.id == attachment_id, DocAttachment.document_id == document_id)
        .first()
    )
    if not attachment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attachment not found")

    return {
        "id": document.id,
        "case_id": document.case_id,
        "doc_template_id": document.doc_template_id,
        "direction": document.direction,
        "doc_date": str(document.doc_date) if document.doc_date else None,
        "title": document.title,
    }


@router.get("/documents/{document_id}")
def get_document(
    document_id: str,
    _perm: None = Depends(require_perm("Doc.Read")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    return {
        "id": document.id,
        "case_id": document.case_id,
        "doc_template_id": document.doc_template_id,
        "direction": document.direction,
        "doc_date": str(document.doc_date) if document.doc_date else None,
        "title": document.title,
    }


@router.put("/documents/{document_id}")
def update_document(
    document_id: str,
    payload: dict[str, Any],
    _perm: None = Depends(require_perm("Doc.Edit")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    if "case_id" in payload:
        document.case_id = payload.get("case_id")
    if "doc_template_id" in payload:
        document.doc_template_id = payload.get("doc_template_id")
    if "direction" in payload:
        document.direction = payload.get("direction") or document.direction
    if "doc_date" in payload:
        document.doc_date = payload.get("doc_date")
    if "title" in payload:
        document.title = payload.get("title")

    db.commit()
    db.refresh(document)

    return {
        "id": document.id,
        "case_id": document.case_id,
        "doc_template_id": document.doc_template_id,
        "direction": document.direction,
        "doc_date": str(document.doc_date) if document.doc_date else None,
        "title": document.title,
    }


@router.post("/documents/{document_id}/attachments", status_code=status.HTTP_201_CREATED)
def add_attachment(
    document_id: str,
    payload: dict[str, Any],
    _perm: None = Depends(require_perm("Doc.Attach")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    attachment = DocAttachment(
        id=str(uuid4()),
        document_id=document.id,
        file_name=payload.get("file_name") or "",
        file_path=payload.get("file_path") or "",
        mime_type=payload.get("mime_type"),
        file_size=payload.get("file_size"),
    )
    db.add(attachment)
    db.commit()

    return {
        "id": document.id,
        "case_id": document.case_id,
        "doc_template_id": document.doc_template_id,
        "direction": document.direction,
        "doc_date": str(document.doc_date) if document.doc_date else None,
        "title": document.title,
    }
