from __future__ import annotations

from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import require_perm
from app.db.session import get_db
from app.models.letter_head import LetterHead
from app.modules.templates.models import Template

router = APIRouter()


@router.post("/templates", status_code=status.HTTP_201_CREATED)
def create_template(
    payload: dict[str, Any],
    _perm: None = Depends(require_perm("Template.Create")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    name = payload.get("name")
    file_path = payload.get("file_path")
    if not name or not file_path:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="name and file_path are required"
        )

    template_type = payload.get("template_type")
    language = payload.get("language")

    template = Template(
        id=str(uuid4()),
        name=name,
        group=template_type,
        language=language,
        file_path=file_path,
        enabled=True,
    )
    db.add(template)
    db.commit()
    db.refresh(template)

    return {
        "id": template.id,
        "name": template.name,
        "template_type": template.group,
        "file_path": template.file_path,
        "created_at": template.created_at,
    }


@router.get("/templates")
def list_templates(
    _perm: None = Depends(require_perm("Template.Read")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    query = db.query(Template)
    total = query.count()
    templates = query.order_by(Template.created_at.desc()).all()
    items = [
        {
            "id": template.id,
            "name": template.name,
            "template_type": template.group,
            "file_path": template.file_path,
        }
        for template in templates
    ]
    return {"items": items, "total": total}


@router.post("/letterheads")
def create_letterhead(
    payload: dict[str, Any],
    _perm: None = Depends(require_perm("LetterHead.Create")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    name = payload.get("name")
    if not name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="name is required")

    letterhead = LetterHead(
        name=name,
        locale=payload.get("locale"),
        logo_file_path=payload.get("logo_file_path"),
        header_text=payload.get("header_text"),
        footer_text=payload.get("footer_text"),
        address_block=payload.get("address_block"),
        phone=payload.get("phone"),
        email=payload.get("email"),
        website=payload.get("website"),
        is_default=bool(payload.get("is_default"))
        if payload.get("is_default") is not None
        else False,
        created_by_user_id=payload.get("created_by_user_id"),
    )
    db.add(letterhead)
    db.commit()
    db.refresh(letterhead)

    return {
        "id": letterhead.id,
        "name": letterhead.name,
        "locale": letterhead.locale,
        "is_default": letterhead.is_default,
    }


@router.get("/letterheads")
def list_letterheads(
    _perm: None = Depends(require_perm("LetterHead.Read")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    query = db.query(LetterHead)
    total = query.count()
    letterheads = query.order_by(LetterHead.created_at.desc()).all()
    items = [
        {
            "id": letterhead.id,
            "name": letterhead.name,
            "locale": letterhead.locale,
            "is_default": letterhead.is_default,
        }
        for letterhead in letterheads
    ]
    return {"items": items, "total": total}
