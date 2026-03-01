from __future__ import annotations

from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.errors import raise_business_error
from app.models.letter_head import LetterHead
from app.modules.templates.models import Template
from app.modules.templates.schemas import (
    LetterHeadCreateIn,
    LetterHeadUpdateIn,
    TemplateCreateIn,
    TemplateUpdateIn,
)


def list_templates(
    db: Session,
    *,
    filters: dict,
    page: int,
    page_size: int,
) -> tuple[list[Template], int]:
    stmt = select(Template)

    group = filters.get("group")
    language = filters.get("language")
    enabled = filters.get("enabled")

    if group:
        stmt = stmt.where(Template.group == group)
    if language:
        stmt = stmt.where(Template.language == language)
    if enabled is not None:
        stmt = stmt.where(Template.enabled == enabled)

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = db.execute(count_stmt).scalar_one()

    offset = (page - 1) * page_size
    stmt = stmt.order_by(Template.created_at.desc()).offset(offset).limit(page_size)
    items = db.execute(stmt).scalars().all()
    return items, total


def get_template(db: Session, *, template_id: str) -> Template:
    template = db.execute(select(Template).where(Template.id == template_id)).scalar_one_or_none()
    if not template:
        raise_business_error("TEMPLATE_NOT_FOUND", "Template not found", status_code=404)
    return template


def create_template(db: Session, *, data: TemplateCreateIn, actor_id: str | None) -> Template:
    template = Template(
        id=str(uuid4()),
        name=data.name,
        group=data.group,
        language=data.language,
        file_path=data.file_path,
        enabled=data.enabled,
    )
    db.add(template)
    db.commit()
    db.refresh(template)
    return template


def update_template(
    db: Session,
    *,
    template_id: str,
    data: TemplateUpdateIn,
    actor_id: str | None,
) -> Template:
    template = get_template(db, template_id=template_id)
    updates = data.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(template, field, value)
    db.commit()
    db.refresh(template)
    return template


def list_letterheads(db: Session, *, locale: str | None = None) -> list[LetterHead]:
    stmt = select(LetterHead)
    if locale is not None:
        stmt = stmt.where(LetterHead.locale == locale)
    return db.execute(stmt.order_by(LetterHead.created_at.desc())).scalars().all()


def get_letterhead(db: Session, *, letterhead_id: str) -> LetterHead:
    letterhead = db.execute(
        select(LetterHead).where(LetterHead.id == letterhead_id)
    ).scalar_one_or_none()
    if not letterhead:
        raise_business_error("LETTERHEAD_NOT_FOUND", "Letterhead not found", status_code=404)
    return letterhead


def _clear_default_letterheads(db: Session, *, locale: str | None) -> None:
    stmt = select(LetterHead).where(LetterHead.is_default.is_(True))
    if locale is None:
        stmt = stmt.where(LetterHead.locale.is_(None))
    else:
        stmt = stmt.where(LetterHead.locale == locale)
    existing = db.execute(stmt).scalars().all()
    for item in existing:
        item.is_default = False


def create_letterhead(
    db: Session,
    *,
    data: LetterHeadCreateIn,
    actor_id: str | None,
) -> LetterHead:
    if data.is_default:
        _clear_default_letterheads(db, locale=data.locale)

    letterhead = LetterHead(
        name=data.name,
        locale=data.locale,
        logo_file_path=data.logo_file_path,
        header_text=data.header_text,
        footer_text=data.footer_text,
        address_block=data.address_block,
        phone=data.phone,
        email=data.email,
        website=data.website,
        is_default=bool(data.is_default) if data.is_default is not None else False,
        created_by_user_id=data.created_by_user_id,
    )
    db.add(letterhead)
    db.commit()
    db.refresh(letterhead)
    return letterhead


def update_letterhead(
    db: Session,
    *,
    letterhead_id: str,
    data: LetterHeadUpdateIn,
    actor_id: str | None,
) -> LetterHead:
    letterhead = get_letterhead(db, letterhead_id=letterhead_id)
    updates = data.model_dump(exclude_unset=True)

    if updates.get("is_default") is True:
        target_locale = updates.get("locale", letterhead.locale)
        _clear_default_letterheads(db, locale=target_locale)

    for field, value in updates.items():
        setattr(letterhead, field, value)

    db.commit()
    db.refresh(letterhead)
    return letterhead
