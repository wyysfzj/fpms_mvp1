from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import current_user_dep, require_perm
from app.db.session import get_db
from app.modules.auth.models import T_User
from app.modules.templates.schemas import (
    LetterHeadCreateIn,
    LetterHeadOut,
    LetterHeadUpdateIn,
    TemplateCreateIn,
    TemplateListItemOut,
    TemplateOut,
    TemplateUpdateIn,
)
from app.modules.templates.service import create_letterhead as create_letterhead_service
from app.modules.templates.service import create_template as create_template_service
from app.modules.templates.service import list_letterheads as list_letterheads_service
from app.modules.templates.service import list_templates as list_templates_service
from app.modules.templates.service import update_letterhead as update_letterhead_service
from app.modules.templates.service import update_template as update_template_service

router = APIRouter()


@router.post(
    "/templates",
    status_code=status.HTTP_201_CREATED,
    response_model=TemplateOut,
    summary="Create a template",
)
def create_template(
    payload: TemplateCreateIn,
    _perm: None = Depends(require_perm("Template.Create")),
    current_user: T_User = current_user_dep,
    db: Session = Depends(get_db),
) -> TemplateOut:
    """
    Create a template.

    **Auth**: Bearer JWT
    **Permission**: Template.Create
    **Request example**:
    ```json
    {"name": "CURL Template", "group": "DOC", "language": "EN", "file_path": "templates/doc.docx"}
    ```
    **Curl example**:
    ```bash
    curl -s -X POST http://localhost:8000/api/v1/templates \\
      -H "Authorization: Bearer $FPMS_TOKEN" \\
      -H "Content-Type: application/json" \\
      -d '{"name":"CURL Template","group":"DOC","language":"EN","file_path":"templates/doc.docx"}'
    ```
    **Responses**:
    - 201: Template created
    - 401: AUTH_REQUIRED
    - 403: FORBIDDEN
    - 422: VALIDATION_ERROR
    """
    template = create_template_service(db, data=payload, actor_id=current_user.id)
    return TemplateOut.model_validate(template)


@router.get("/templates", summary="List templates")
def list_templates(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    group: str | None = Query(default=None),
    language: str | None = Query(default=None),
    enabled: bool | None = Query(default=None),
    _perm: None = Depends(require_perm("Template.Read")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """
    List templates with filters and pagination.

    **Auth**: Bearer JWT
    **Permission**: Template.Read
    **Request example**:
    `GET /api/v1/templates?page=1&page_size=20&group=DOC&enabled=true`
    **Curl example**:
    ```bash
    curl -s -X GET "http://localhost:8000/api/v1/templates?page=1&page_size=20" \\
      -H "Authorization: Bearer $FPMS_TOKEN"
    ```
    **Responses**:
    - 200: List of templates
    - 401: AUTH_REQUIRED
    - 403: FORBIDDEN
    - 422: VALIDATION_ERROR
    """
    filters = {"group": group, "language": language, "enabled": enabled}
    templates, total = list_templates_service(db, filters=filters, page=page, page_size=page_size)
    items = [TemplateListItemOut.model_validate(template) for template in templates]
    return {"items": items, "page": page, "page_size": page_size, "total": total}


@router.put("/templates/{template_id}", response_model=TemplateOut, summary="Update a template")
def update_template(
    template_id: str,
    payload: TemplateUpdateIn,
    _perm: None = Depends(require_perm("Template.Edit")),
    current_user: T_User = current_user_dep,
    db: Session = Depends(get_db),
) -> TemplateOut:
    """
    Update a template.

    **Auth**: Bearer JWT
    **Permission**: Template.Edit
    **Request example**:
    ```json
    {"name": "Updated Template", "enabled": false}
    ```
    **Curl example**:
    ```bash
    curl -s -X PUT http://localhost:8000/api/v1/templates/TEMPLATE_ID \\
      -H "Authorization: Bearer $FPMS_TOKEN" \\
      -H "Content-Type: application/json" \\
      -d '{"name":"Updated Template","enabled":false}'
    ```
    **Responses**:
    - 200: Template updated
    - 401: AUTH_REQUIRED
    - 403: FORBIDDEN
    - 404: Template not found
    - 422: VALIDATION_ERROR
    """
    template = update_template_service(
        db,
        template_id=template_id,
        data=payload,
        actor_id=current_user.id,
    )
    return TemplateOut.model_validate(template)


@router.post(
    "/letterheads",
    status_code=status.HTTP_201_CREATED,
    response_model=LetterHeadOut,
    summary="Create a letterhead",
)
def create_letterhead(
    payload: LetterHeadCreateIn,
    _perm: None = Depends(require_perm("LetterHead.Create")),
    current_user: T_User = current_user_dep,
    db: Session = Depends(get_db),
) -> LetterHeadOut:
    """
    Create a letterhead.

    **Auth**: Bearer JWT
    **Permission**: LetterHead.Create
    **Request example**:
    ```json
    {"name": "Default Letterhead", "locale": "en", "is_default": true}
    ```
    **Curl example**:
    ```bash
    curl -s -X POST http://localhost:8000/api/v1/letterheads \\
      -H "Authorization: Bearer $FPMS_TOKEN" \\
      -H "Content-Type: application/json" \\
      -d '{"name":"Default Letterhead","locale":"en","is_default":true}'
    ```
    **Responses**:
    - 201: Letterhead created
    - 401: AUTH_REQUIRED
    - 403: FORBIDDEN
    - 422: VALIDATION_ERROR
    """
    letterhead = create_letterhead_service(db, data=payload, actor_id=current_user.id)
    return LetterHeadOut.model_validate(letterhead)


@router.get("/letterheads", response_model=list[LetterHeadOut], summary="List letterheads")
def list_letterheads(
    locale: str | None = Query(default=None),
    _perm: None = Depends(require_perm("LetterHead.Read")),
    db: Session = Depends(get_db),
) -> list[LetterHeadOut]:
    """
    List letterheads (optional locale filter).

    **Auth**: Bearer JWT
    **Permission**: LetterHead.Read
    **Request example**:
    `GET /api/v1/letterheads?locale=en`
    **Curl example**:
    ```bash
    curl -s -X GET "http://localhost:8000/api/v1/letterheads?locale=en" \\
      -H "Authorization: Bearer $FPMS_TOKEN"
    ```
    **Responses**:
    - 200: List of letterheads
    - 401: AUTH_REQUIRED
    - 403: FORBIDDEN
    - 422: VALIDATION_ERROR
    """
    letterheads = list_letterheads_service(db, locale=locale)
    return [LetterHeadOut.model_validate(letterhead) for letterhead in letterheads]


@router.put(
    "/letterheads/{letterhead_id}",
    response_model=LetterHeadOut,
    summary="Update a letterhead",
)
def update_letterhead(
    letterhead_id: str,
    payload: LetterHeadUpdateIn,
    _perm: None = Depends(require_perm("LetterHead.Edit")),
    current_user: T_User = current_user_dep,
    db: Session = Depends(get_db),
) -> LetterHeadOut:
    """
    Update a letterhead.

    **Auth**: Bearer JWT
    **Permission**: LetterHead.Edit
    **Request example**:
    ```json
    {"name": "Updated Letterhead", "is_default": false}
    ```
    **Curl example**:
    ```bash
    curl -s -X PUT http://localhost:8000/api/v1/letterheads/LETTERHEAD_ID \\
      -H "Authorization: Bearer $FPMS_TOKEN" \\
      -H "Content-Type: application/json" \\
      -d '{"name":"Updated Letterhead","is_default":false}'
    ```
    **Responses**:
    - 200: Letterhead updated
    - 401: AUTH_REQUIRED
    - 403: FORBIDDEN
    - 404: Letterhead not found
    - 422: VALIDATION_ERROR
    """
    letterhead = update_letterhead_service(
        db,
        letterhead_id=letterhead_id,
        data=payload,
        actor_id=current_user.id,
    )
    return LetterHeadOut.model_validate(letterhead)
