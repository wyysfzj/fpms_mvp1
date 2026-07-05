from __future__ import annotations

from datetime import date
from typing import Any

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import current_user_dep, require_perm
from app.core.errors import raise_business_error
from app.db.session import get_db
from app.modules.auth.models import T_User
from app.modules.cases.models import Case
from app.modules.fees.models import FeeDraft, FeeItem
from app.modules.fees.schemas import (
    ApplyFeeDraftGenerateIn,
    FeeDraftCreateIn,
    FeeDraftListItemOut,
    FeeDraftOut,
    FeeDraftReportListResponse,
    FeeDraftReportSummaryResponse,
    FeeItemCreateIn,
    FeeItemOut,
    FeeItemUpdateIn,
    FeeRateCreateIn,
    FeeRateOut,
    FeeRateUpdateIn,
    OfficialFeePreviewIn,
    OfficialFeePreviewOut,
    OkOut,
)
from app.modules.fees.service import add_fee_item, list_fee_drafts, list_fee_items, list_fee_rates
from app.modules.fees.service import create_fee_draft as create_fee_draft_service
from app.modules.fees.service import create_fee_rate as create_fee_rate_service
from app.modules.fees.service import generate_apply_fee_draft as generate_apply_fee_draft_service
from app.modules.fees.service import lock_fee_draft as lock_fee_draft_service
from app.modules.fees.service import preview_official_fee_candidates as preview_official_fee_service
from app.modules.fees.service import unlock_fee_draft as unlock_fee_draft_service
from app.modules.fees.service import update_fee_item as update_fee_item_service
from app.modules.fees.service import update_fee_rate as update_fee_rate_service
from app.modules.masterdata.clients.models import Client

router = APIRouter()


def _get_client_display_name(client: Client) -> str | None:
    return client.name_cn or client.name_en


def _build_case_no_map(db: Session, case_ids: set[str]) -> dict[str, str]:
    if not case_ids:
        return {}
    cases = db.execute(select(Case.id, Case.case_no).where(Case.id.in_(case_ids))).all()
    return {case_id: case_no for case_id, case_no in cases if case_no}


def _build_client_name_map(db: Session, client_ids: set[str]) -> dict[str, str]:
    if not client_ids:
        return {}
    clients = db.execute(select(Client).where(Client.id.in_(client_ids))).scalars().all()
    return {
        client.id: _get_client_display_name(client)
        for client in clients
        if _get_client_display_name(client)
    }


@router.get("/fees/drafts", summary="List fee drafts")
def get_fee_drafts(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    case_id: str | None = Query(default=None),
    case_no: str | None = Query(default=None),
    client_id: str | None = Query(default=None),
    fee_type: str | None = Query(default=None),
    currency: str | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    draft_status: str | None = Query(default=None),
    bill_status: str | None = Query(default=None),
    status_filter: str | None = Query(default=None, alias="status"),
    _perm: None = Depends(require_perm("Fee.Read")),
    db: Session = Depends(get_db),
) -> FeeDraftReportListResponse:
    """
    List fee drafts with filters and pagination.

    **Auth**: Bearer JWT
    **Permission**: Fee.Read
    **Request example**:
    `GET /api/v1/fees/drafts?page=1&page_size=20&status=OPEN&case_id=CASE_ID`
    **Curl example**:
    ```bash
    curl -s -X GET "http://localhost:8000/api/v1/fees/drafts?page=1&page_size=20" \\
      -H "Authorization: Bearer $FPMS_TOKEN"
    ```
    **Responses**:
    - 200: List of fee drafts
    - 401: AUTH_REQUIRED
    - 403: FORBIDDEN
    - 422: VALIDATION_ERROR
    """
    filters = {
        "case_id": case_id,
        "case_no": case_no,
        "client_id": client_id,
        "fee_type": fee_type,
        "currency": currency,
        "date_from": date_from,
        "date_to": date_to,
        "draft_status": draft_status,
        "bill_status": bill_status,
        "status": status_filter,
    }
    drafts, total, summary = list_fee_drafts(db, filters=filters, page=page, page_size=page_size)
    case_no_map = _build_case_no_map(db, {draft.case_id for draft in drafts if draft.case_id})
    client_name_map = _build_client_name_map(
        db, {draft.client_id for draft in drafts if draft.client_id}
    )
    items = [
        FeeDraftListItemOut(
            id=draft.id,
            case_id=draft.case_id,
            case_no=case_no_map.get(draft.case_id),
            client_id=draft.client_id,
            client_name=client_name_map.get(draft.client_id) if draft.client_id else None,
            currency=draft.currency,
            status=draft.status,
            amount=draft.amount,
        )
        for draft in drafts
    ]
    return FeeDraftReportListResponse(
        items=items,
        page=page,
        page_size=page_size,
        total=total,
        summary=FeeDraftReportSummaryResponse.model_validate(summary),
    )


@router.post(
    "/fees/drafts",
    status_code=status.HTTP_201_CREATED,
    response_model=FeeDraftOut,
    summary="Create a fee draft",
)
def create_fee_draft(
    payload: FeeDraftCreateIn,
    _perm: None = Depends(require_perm("Fee.Create")),
    current_user: T_User = current_user_dep,
    db: Session = Depends(get_db),
) -> FeeDraftOut:
    """
    Create a fee draft.

    **Auth**: Bearer JWT
    **Permission**: Fee.Create
    **Request example**:
    ```json
    {"case_id": "CASE_ID", "client_id": "CLIENT_ID", "currency": "CNY"}
    ```
    **Curl example**:
    ```bash
    curl -s -X POST http://localhost:8000/api/v1/fees/drafts \\
      -H "Authorization: Bearer $FPMS_TOKEN" \\
      -H "Content-Type: application/json" \\
      -d '{"case_id":"CASE_ID","client_id":"CLIENT_ID","currency":"CNY"}'
    ```
    **Responses**:
    - 201: Fee draft created
    - 401: AUTH_REQUIRED
    - 403: FORBIDDEN
    - 404: Case or client not found
    - 422: VALIDATION_ERROR
    """
    draft = create_fee_draft_service(db, data=payload, actor_id=current_user.id)
    return FeeDraftOut.model_validate(draft)


@router.post(
    "/fees/drafts/apply-fee/generate",
    status_code=status.HTTP_201_CREATED,
    response_model=FeeDraftOut,
    summary="Generate application fee draft",
)
def generate_apply_fee_draft(
    payload: ApplyFeeDraftGenerateIn,
    response: Response,
    _perm: None = Depends(require_perm("Fee.Create")),
    current_user: T_User = current_user_dep,
    db: Session = Depends(get_db),
) -> FeeDraftOut:
    draft, created = generate_apply_fee_draft_service(
        db,
        data=payload,
        actor_id=current_user.id,
    )
    if not created:
        response.status_code = status.HTTP_200_OK
    return FeeDraftOut.model_validate(draft)


@router.post(
    "/fees/official-fee-preview",
    response_model=OfficialFeePreviewOut,
    summary="Preview official fee candidates",
)
def preview_official_fee_candidates(
    payload: OfficialFeePreviewIn,
    _perm: None = Depends(require_perm("Fee.Read")),
    db: Session = Depends(get_db),
) -> OfficialFeePreviewOut:
    preview = preview_official_fee_service(db, data=payload)
    return OfficialFeePreviewOut.model_validate(preview)


@router.post("/fees/drafts/{draft_id}/lock", response_model=OkOut, summary="Lock a fee draft")
def lock_fee_draft(
    draft_id: str,
    _perm: None = Depends(require_perm("Fee.Lock")),
    current_user: T_User = current_user_dep,
    db: Session = Depends(get_db),
) -> OkOut:
    """
    Lock a fee draft to prevent edits.

    **Auth**: Bearer JWT
    **Permission**: Fee.Lock
    **Request example**:
    `POST /api/v1/fees/drafts/DRAFT_ID/lock`
    **Curl example**:
    ```bash
    curl -s -X POST http://localhost:8000/api/v1/fees/drafts/DRAFT_ID/lock \\
      -H "Authorization: Bearer $FPMS_TOKEN"
    ```
    **Responses**:
    - 200: Fee draft locked
    - 401: AUTH_REQUIRED
    - 403: FORBIDDEN
    - 404: Fee draft not found
    - 409: Fee draft already locked
    - 422: VALIDATION_ERROR
    """
    lock_fee_draft_service(db, draft_id=draft_id, actor_id=current_user.id)
    return OkOut()


@router.post(
    "/fees/drafts/{draft_id}/unlock",
    response_model=OkOut,
    summary="Unlock a fee draft",
)
def unlock_fee_draft(
    draft_id: str,
    _perm: None = Depends(require_perm("Fee.Lock")),
    current_user: T_User = current_user_dep,
    db: Session = Depends(get_db),
) -> OkOut:
    """
    Unlock a fee draft to allow edits.

    **Auth**: Bearer JWT
    **Permission**: Fee.Lock
    **Request example**:
    `POST /api/v1/fees/drafts/DRAFT_ID/unlock`
    **Curl example**:
    ```bash
    curl -s -X POST http://localhost:8000/api/v1/fees/drafts/DRAFT_ID/unlock \\
      -H "Authorization: Bearer $FPMS_TOKEN"
    ```
    **Responses**:
    - 200: Fee draft unlocked
    - 401: AUTH_REQUIRED
    - 403: FORBIDDEN
    - 404: Fee draft not found
    - 409: Fee draft not locked
    - 422: VALIDATION_ERROR
    """
    unlock_fee_draft_service(db, draft_id=draft_id, actor_id=current_user.id)
    return OkOut()


@router.post(
    "/fees/drafts/{draft_id}/items",
    status_code=status.HTTP_201_CREATED,
    response_model=FeeItemOut,
    summary="Add a fee item to a draft",
)
def create_fee_item(
    draft_id: str,
    payload: FeeItemCreateIn,
    _perm: None = Depends(require_perm("Fee.Edit")),
    current_user: T_User = current_user_dep,
    db: Session = Depends(get_db),
) -> FeeItemOut:
    """
    Add a fee item to a draft.

    **Auth**: Bearer JWT
    **Permission**: Fee.Edit
    **Request example**:
    ```json
    {"rate_id": "RATE_ID", "quantity": 1, "unit_price": "100.00"}
    ```
    **Curl example**:
    ```bash
    curl -s -X POST http://localhost:8000/api/v1/fees/drafts/DRAFT_ID/items \\
      -H "Authorization: Bearer $FPMS_TOKEN" \\
      -H "Content-Type: application/json" \\
      -d '{"rate_id":"RATE_ID","quantity":1,"unit_price":"100.00"}'
    ```
    **Responses**:
    - 201: Fee item created
    - 400: Rate disabled or currency mismatch
    - 401: AUTH_REQUIRED
    - 403: FORBIDDEN
    - 404: Draft or rate not found
    - 409: Draft is locked
    - 422: VALIDATION_ERROR
    """
    item = add_fee_item(db, draft_id=draft_id, data=payload, actor_id=current_user.id)
    return FeeItemOut.model_validate(item)


@router.get(
    "/fees/drafts/{draft_id}/items",
    response_model=list[FeeItemOut],
    summary="List fee items for a draft",
)
def get_fee_items(
    draft_id: str,
    _perm: None = Depends(require_perm("Fee.Read")),
    db: Session = Depends(get_db),
) -> list[FeeItemOut]:
    """
    List fee items for a draft.

    **Auth**: Bearer JWT
    **Permission**: Fee.Read
    **Request example**:
    `GET /api/v1/fees/drafts/DRAFT_ID/items`
    **Curl example**:
    ```bash
    curl -s -X GET http://localhost:8000/api/v1/fees/drafts/DRAFT_ID/items \\
      -H "Authorization: Bearer $FPMS_TOKEN"
    ```
    **Responses**:
    - 200: Fee item list
    - 401: AUTH_REQUIRED
    - 403: FORBIDDEN
    - 404: Fee draft not found
    - 422: VALIDATION_ERROR
    """
    items = list_fee_items(db, draft_id=draft_id)
    return [FeeItemOut.model_validate(item) for item in items]


@router.put(
    "/fees/drafts/{draft_id}/items/{item_id}",
    response_model=FeeItemOut,
    summary="Update a fee item",
)
def update_fee_item(
    draft_id: str,
    item_id: str,
    payload: FeeItemUpdateIn,
    _perm: None = Depends(require_perm("Fee.Edit")),
    current_user: T_User = current_user_dep,
    db: Session = Depends(get_db),
) -> FeeItemOut:
    """
    Update a fee item in a draft.

    **Auth**: Bearer JWT
    **Permission**: Fee.Edit
    **Request example**:
    ```json
    {"quantity": 2, "unit_price": "120.00"}
    ```
    **Curl example**:
    ```bash
    curl -s -X PUT http://localhost:8000/api/v1/fees/drafts/DRAFT_ID/items/ITEM_ID \\
      -H "Authorization: Bearer $FPMS_TOKEN" \\
      -H "Content-Type: application/json" \\
      -d '{"quantity":2,"unit_price":"120.00"}'
    ```
    **Responses**:
    - 200: Fee item updated
    - 401: AUTH_REQUIRED
    - 403: FORBIDDEN
    - 404: Draft or item not found
    - 409: Draft is locked
    - 422: VALIDATION_ERROR
    """
    item = update_fee_item_service(
        db,
        draft_id=draft_id,
        item_id=item_id,
        data=payload,
        actor_id=current_user.id,
    )
    return FeeItemOut.model_validate(item)


@router.delete(
    "/fees/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a fee item",
)
def delete_fee_item(
    item_id: str,
    _perm: None = Depends(require_perm("Fee.Item.Delete")),
    db: Session = Depends(get_db),
) -> Response:
    """
    Delete a fee item.

    **Auth**: Bearer JWT
    **Permission**: Fee.Item.Delete
    **Request example**:
    `DELETE /api/v1/fees/items/ITEM_ID`
    **Curl example**:
    ```bash
    curl -s -X DELETE http://localhost:8000/api/v1/fees/items/ITEM_ID \\
      -H "Authorization: Bearer $FPMS_TOKEN"
    ```
    **Responses**:
    - 204: Fee item deleted
    - 401: AUTH_REQUIRED
    - 403: FORBIDDEN
    - 404: Fee item not found
    - 422: VALIDATION_ERROR
    """
    item = db.query(FeeItem).filter(FeeItem.id == item_id).first()
    if not item:
        raise_business_error(
            "FEE_ITEM_NOT_FOUND",
            "Fee item not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    remaining_count = db.query(FeeItem).filter(FeeItem.draft_id == item.draft_id).count()
    if remaining_count <= 1:
        raise_business_error(
            "FEE_DRAFT_ITEM_REQUIRED",
            "Fee draft must keep at least one fee item",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"draft_id": item.draft_id},
        )

    db.delete(item)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/fees/drafts/{draft_id}", response_model=FeeDraftOut, summary="Get a fee draft")
def get_fee_draft(
    draft_id: str,
    _perm: None = Depends(require_perm("Fee.Draft.Read")),
    db: Session = Depends(get_db),
) -> FeeDraftOut:
    """
    Get a fee draft by ID.

    **Auth**: Bearer JWT
    **Permission**: Fee.Draft.Read
    **Request example**:
    `GET /api/v1/fees/drafts/DRAFT_ID`
    **Curl example**:
    ```bash
    curl -s -X GET http://localhost:8000/api/v1/fees/drafts/DRAFT_ID \\
      -H "Authorization: Bearer $FPMS_TOKEN"
    ```
    **Responses**:
    - 200: Fee draft details
    - 401: AUTH_REQUIRED
    - 403: FORBIDDEN
    - 404: Fee draft not found
    - 422: VALIDATION_ERROR
    """
    draft = db.query(FeeDraft).filter(FeeDraft.id == draft_id).first()
    if not draft:
        raise_business_error(
            "FEE_DRAFT_NOT_FOUND",
            "Fee draft not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    case_no = db.execute(select(Case.case_no).where(Case.id == draft.case_id)).scalar_one_or_none()
    client_name = None
    if draft.client_id:
        client = db.execute(select(Client).where(Client.id == draft.client_id)).scalar_one_or_none()
        if client:
            client_name = _get_client_display_name(client)

    return FeeDraftOut(
        id=draft.id,
        case_id=draft.case_id,
        case_no=case_no,
        client_id=draft.client_id,
        client_name=client_name,
        draft_type=draft.draft_type,
        currency=draft.currency,
        status=draft.status,
        total_gov=draft.total_gov,
        total_service=draft.total_service,
        total_misc=draft.total_misc,
        amount=draft.amount,
        created_at=draft.created_at,
        updated_at=draft.updated_at,
    )


@router.put("/fees/drafts/{draft_id}", summary="Update a fee draft")
def update_fee_draft(
    draft_id: str,
    payload: dict[str, Any],
    _perm: None = Depends(require_perm("Fee.Draft.Edit")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """
    Update a fee draft fields.

    **Auth**: Bearer JWT
    **Permission**: Fee.Draft.Edit
    **Request example**:
    ```json
    {"draft_type": "GENERIC", "currency": "CNY"}
    ```
    **Curl example**:
    ```bash
    curl -s -X PUT http://localhost:8000/api/v1/fees/drafts/DRAFT_ID \\
      -H "Authorization: Bearer $FPMS_TOKEN" \\
      -H "Content-Type: application/json" \\
      -d '{"draft_type":"GENERIC","currency":"CNY"}'
    ```
    **Responses**:
    - 200: Fee draft updated
    - 401: AUTH_REQUIRED
    - 403: FORBIDDEN
    - 404: Fee draft not found
    - 422: VALIDATION_ERROR
    """
    draft = db.query(FeeDraft).filter(FeeDraft.id == draft_id).first()
    if not draft:
        raise_business_error(
            "FEE_DRAFT_NOT_FOUND",
            "Fee draft not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    if "case_id" in payload:
        draft.case_id = payload.get("case_id")
    if "client_id" in payload:
        draft.client_id = payload.get("client_id")
    if "draft_type" in payload:
        draft.draft_type = payload.get("draft_type") or draft.draft_type
    if "currency" in payload:
        if not str(payload.get("currency") or "").strip():
            raise_business_error(
                "FEE_DRAFT_CURRENCY_REQUIRED",
                "Fee draft currency is required",
                status_code=status.HTTP_400_BAD_REQUEST,
                details={"currency": payload.get("currency")},
            )
        draft.currency = payload.get("currency") or draft.currency
    if "status" in payload:
        draft.status = payload.get("status") or draft.status

    db.commit()
    db.refresh(draft)

    return {
        "id": draft.id,
        "case_id": draft.case_id,
        "client_id": draft.client_id,
        "draft_type": draft.draft_type,
        "currency": draft.currency,
        "status": draft.status,
    }


@router.get("/fees/rates", summary="List fee rates")
def get_fee_rates(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    fee_code: str | None = Query(default=None),
    fee_type: str | None = Query(default=None),
    currency: str | None = Query(default=None),
    enabled: bool | None = Query(default=None),
    rate_group: str | None = Query(default=None),
    country_code: str | None = Query(default=None),
    case_type: str | None = Query(default=None),
    patent_category: str | None = Query(default=None),
    fee_domain: str | None = Query(default=None),
    fee_section: str | None = Query(default=None),
    fee_category: str | None = Query(default=None),
    fee_subtype: str | None = Query(default=None),
    calc_mode: str | None = Query(default=None),
    _perm: None = Depends(require_perm("FeeRate.Read")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """
    List fee rates with filters and pagination.

    **Auth**: Bearer JWT
    **Permission**: FeeRate.Read
    **Request example**:
    `GET /api/v1/fees/rates?page=1&page_size=20&currency=CNY&enabled=true`
    **Curl example**:
    ```bash
    curl -s -X GET "http://localhost:8000/api/v1/fees/rates?page=1&page_size=20" \\
      -H "Authorization: Bearer $FPMS_TOKEN"
    ```
    **Responses**:
    - 200: List of fee rates
    - 401: AUTH_REQUIRED
    - 403: FORBIDDEN
    - 422: VALIDATION_ERROR
    """
    filters = {
        "fee_code": fee_code,
        "fee_type": fee_type,
        "currency": currency,
        "enabled": enabled,
        "rate_group": rate_group,
        "country_code": country_code,
        "case_type": case_type,
        "patent_category": patent_category,
        "fee_domain": fee_domain,
        "fee_section": fee_section,
        "fee_category": fee_category,
        "fee_subtype": fee_subtype,
        "calc_mode": calc_mode,
    }
    rates, total = list_fee_rates(db, filters=filters, page=page, page_size=page_size)
    items = [FeeRateOut.model_validate(rate) for rate in rates]
    return {"items": items, "page": page, "page_size": page_size, "total": total}


@router.post(
    "/fees/rates",
    status_code=status.HTTP_201_CREATED,
    response_model=FeeRateOut,
    summary="Create a fee rate",
)
def create_fee_rate(
    payload: FeeRateCreateIn,
    _perm: None = Depends(require_perm("FeeRate.Create")),
    current_user: T_User = current_user_dep,
    db: Session = Depends(get_db),
) -> FeeRateOut:
    """
    Create a fee rate.

    **Auth**: Bearer JWT
    **Permission**: FeeRate.Create
    **Request example**:
    ```json
    {
      "fee_code": "FEE_CODE_001",
      "fee_name": "Filing Fee",
      "fee_type": "GOV",
      "currency": "CNY",
      "default_amount": "100.00",
      "enabled": true
    }
    ```
    **Curl example**:
    ```bash
    curl -s -X POST http://localhost:8000/api/v1/fees/rates \\
      -H "Authorization: Bearer $FPMS_TOKEN" \\
      -H "Content-Type: application/json" \\
      -d '{"fee_code":"FEE_CODE_001","fee_name":"Filing Fee","fee_type":"GOV","currency":"CNY","default_amount":"100.00","enabled":true}'
    ```
    **Responses**:
    - 201: Fee rate created
    - 401: AUTH_REQUIRED
    - 403: FORBIDDEN
    - 422: VALIDATION_ERROR
    """
    rate = create_fee_rate_service(db, data=payload, actor_id=current_user.id)
    return FeeRateOut.model_validate(rate)


@router.put("/fees/rates/{rate_id}", response_model=FeeRateOut, summary="Update a fee rate")
def update_fee_rate(
    rate_id: str,
    payload: FeeRateUpdateIn,
    _perm: None = Depends(require_perm("FeeRate.Edit")),
    current_user: T_User = current_user_dep,
    db: Session = Depends(get_db),
) -> FeeRateOut:
    """
    Update a fee rate by ID.

    **Auth**: Bearer JWT
    **Permission**: FeeRate.Edit
    **Request example**:
    ```json
    {"fee_name": "Updated Filing Fee", "enabled": false}
    ```
    **Curl example**:
    ```bash
    curl -s -X PUT http://localhost:8000/api/v1/fees/rates/RATE_ID \\
      -H "Authorization: Bearer $FPMS_TOKEN" \\
      -H "Content-Type: application/json" \\
      -d '{"fee_name":"Updated Filing Fee","enabled":false}'
    ```
    **Responses**:
    - 200: Fee rate updated
    - 401: AUTH_REQUIRED
    - 403: FORBIDDEN
    - 404: Fee rate not found
    - 422: VALIDATION_ERROR
    """
    rate = update_fee_rate_service(db, rate_id=rate_id, data=payload, actor_id=current_user.id)
    return FeeRateOut.model_validate(rate)
