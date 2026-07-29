from __future__ import annotations

import json
from datetime import date
from hashlib import sha256
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Path, Query, Response, status
from sqlalchemy import literal, select
from sqlalchemy.orm import Session

from app.api.deps import current_user_dep, require_perm
from app.core.errors import BusinessError, raise_business_error
from app.db.session import get_db
from app.modules.auth.models import T_User
from app.modules.cases.models import Case
from app.modules.documents.models import DocumentEvidenceVersion
from app.modules.fees.fee_reduction import FeeReductionValidationError
from app.modules.fees.fee_reduction_approval_schemas import (
    FeeReductionApprovalCreateIn,
    FeeReductionApprovalCreateOut,
    FeeReductionApprovalListItemOut,
)
from app.modules.fees.fee_reduction_approval_service import (
    FeeReductionApprovalRecordDisposition,
    RecordFeeReductionApprovalCommand,
    record_fee_reduction_approval,
)
from app.modules.fees.models import FeeDraft, FeeItem, FeeReductionApproval
from app.modules.fees.obligation_contracts import (
    FeeEstimateContext,
    PreviewFeeEstimateCommand,
    RecordFeeObligationInstructionCommand,
)
from app.modules.fees.obligation_schemas import (
    FeeObligationInstructionIn,
    FeeObligationInstructionOut,
)
from app.modules.fees.obligation_service import (
    FeeEstimatePreviewError,
    FeeEstimatePreviewErrorCode,
    preview_estimate,
    record_client_instruction,
)
from app.modules.fees.official_rate_book import SqlAlchemyOfficialFeeEstimateRateProvider
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


def _raise_corrupt_approval_scope() -> None:
    raise_business_error(
        "FEE_REDUCTION_APPROVAL_SCOPE_CORRUPT",
        "费用减免审批费用范围数据损坏",
        status_code=status.HTTP_409_CONFLICT,
    )


def _fee_codes_from_approval_scope(
    value: object,
    expected_hash: object,
) -> tuple[str, ...]:
    def reject_constant(_value: str) -> None:
        raise ValueError

    def unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, item in pairs:
            if key in result:
                raise ValueError
            result[key] = item
        return result

    try:
        if type(value) is not str:
            raise ValueError
        snapshot = json.loads(
            value,
            object_pairs_hook=unique_object,
            parse_constant=reject_constant,
        )
        canonical_snapshot = json.dumps(
            snapshot,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        snapshot_bytes = value.encode("utf-8")
    except (TypeError, ValueError, json.JSONDecodeError, UnicodeEncodeError):
        _raise_corrupt_approval_scope()

    fee_codes = snapshot.get("fee_codes") if type(snapshot) is dict else None
    if (
        type(snapshot) is not dict
        or set(snapshot) != {"fee_codes", "schema"}
        or snapshot.get("schema") != "FPMS_FEE_REDUCTION_FEE_SCOPE_V1"
        or type(fee_codes) is not list
        or not fee_codes
        or any(
            type(code) is not str
            or not code
            or code != code.strip()
            or "\x00" in code
            or len(code) > 64
            for code in fee_codes
        )
        or len(set(fee_codes)) != len(fee_codes)
        or fee_codes != sorted(fee_codes)
        or canonical_snapshot != value
        or type(expected_hash) is not str
        or len(expected_hash) != 64
        or any(character not in "0123456789abcdef" for character in expected_hash)
        or sha256(snapshot_bytes).hexdigest() != expected_hash
    ):
        _raise_corrupt_approval_scope()
    return tuple(fee_codes)


def _validate_approval_source_identity(row: Any, case_id: str) -> None:
    evidence_case_id = row["evidence_case_id"]
    lineage_key = row["evidence_lineage_key"]
    current_identity_key = row["evidence_current_identity_key"]
    try:
        lineage_is_utf8 = type(lineage_key) is str and bool(lineage_key.encode("utf-8"))
    except UnicodeEncodeError:
        lineage_is_utf8 = False
    if (
        evidence_case_id != case_id
        or type(lineage_key) is not str
        or not lineage_key
        or lineage_key != lineage_key.strip()
        or "\x00" in lineage_key
        or len(lineage_key) > 128
        or not lineage_is_utf8
        or current_identity_key != f"{case_id}|{lineage_key}"
        or row["is_current"] is not True
    ):
        raise_business_error(
            "FEE_REDUCTION_APPROVAL_SOURCE_IDENTITY_CORRUPT",
            "费用减免审批来源当前标识数据损坏",
            status_code=status.HTTP_409_CONFLICT,
        )


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
    status_code=status.HTTP_200_OK,
    response_model=OfficialFeePreviewOut,
    summary="Preview official fee candidates",
)
def preview_official_fee_candidates(
    payload: OfficialFeePreviewIn,
    _perm: None = Depends(require_perm("Fee.Read")),
    db: Session = Depends(get_db),
) -> OfficialFeePreviewOut:
    with db.no_autoflush:
        case = db.execute(select(Case).where(Case.id == payload.case_id)).scalar_one_or_none()
    if case is None:
        raise_business_error("CASE_NOT_FOUND", "Case not found", status_code=404)

    command = PreviewFeeEstimateCommand(
        case_id=payload.case_id,
        trigger_context=FeeEstimateContext(
            trigger=payload.trigger_context.trigger,
            source_document_id=payload.trigger_context.source_document_id,
        ),
        currency=payload.currency,
    )
    try:
        estimate = preview_estimate(
            command=command,
            rate_effective_on=payload.rate_effective_on,
            rate_provider=SqlAlchemyOfficialFeeEstimateRateProvider(db),
        )
    except FeeEstimatePreviewError as exc:
        status_code = (
            400
            if exc.code
            in {
                FeeEstimatePreviewErrorCode.INVALID_COMMAND,
                FeeEstimatePreviewErrorCode.TRIGGER_UNSUPPORTED,
            }
            else 409
        )
        raise_business_error(
            exc.code.value,
            exc.code.value,
            details=exc.details,
            status_code=status_code,
        )
    except FeeReductionValidationError as exc:
        raise_business_error(
            exc.code.value,
            exc.code.value,
            details=exc.details,
            status_code=409,
        )

    return OfficialFeePreviewOut.model_validate(estimate)


@router.get(
    "/fees/cases/{case_id}/reduction-approvals",
    response_model=list[FeeReductionApprovalListItemOut],
    summary="List current fee reduction approvals for a case",
)
def list_fee_reduction_approvals(
    case_id: Annotated[str, Path(min_length=1, max_length=36)],
    _perm: None = Depends(require_perm("Fee.Read")),
    db: Session = Depends(get_db),
) -> list[FeeReductionApprovalListItemOut]:
    with db.no_autoflush:
        if db.get(Case, case_id) is None:
            raise_business_error("CASE_NOT_FOUND", "Case not found", status_code=404)
        rows = (
            db.execute(
                select(
                    FeeReductionApproval.id.label("approval_id"),
                    FeeReductionApproval.scope_type,
                    FeeReductionApproval.case_id,
                    FeeReductionApproval.applicant_set_key,
                    FeeReductionApproval.reduction_ratio,
                    FeeReductionApproval.fee_scope_snapshot,
                    FeeReductionApproval.fee_scope_hash,
                    FeeReductionApproval.fee_year_from,
                    FeeReductionApproval.fee_year_to,
                    FeeReductionApproval.effective_from,
                    FeeReductionApproval.effective_to,
                    FeeReductionApproval.source_evidence_version_id,
                    FeeReductionApproval.confirmation_status,
                    FeeReductionApproval.confirmed_at,
                    FeeReductionApproval.confirmed_by,
                    DocumentEvidenceVersion.case_id.label("evidence_case_id"),
                    DocumentEvidenceVersion.lineage_key.label("evidence_lineage_key"),
                    DocumentEvidenceVersion.current_identity_key.label(
                        "evidence_current_identity_key"
                    ),
                    (
                        DocumentEvidenceVersion.current_identity_key
                        == DocumentEvidenceVersion.case_id
                        + literal("|")
                        + DocumentEvidenceVersion.lineage_key
                    ).label("is_current"),
                )
                .join(
                    DocumentEvidenceVersion,
                    DocumentEvidenceVersion.id == FeeReductionApproval.source_evidence_version_id,
                )
                .where(
                    DocumentEvidenceVersion.case_id == case_id,
                    FeeReductionApproval.confirmation_status == "CONFIRMED",
                )
                .order_by(
                    FeeReductionApproval.confirmed_at.asc(),
                    FeeReductionApproval.id.asc(),
                )
            )
            .mappings()
            .all()
        )
    result: list[FeeReductionApprovalListItemOut] = []
    for row in rows:
        _validate_approval_source_identity(row, case_id)
        result.append(
            FeeReductionApprovalListItemOut.model_validate(
                {
                    **row,
                    "fee_codes": _fee_codes_from_approval_scope(
                        row["fee_scope_snapshot"],
                        row["fee_scope_hash"],
                    ),
                }
            )
        )
    return result


@router.post(
    "/fees/cases/{case_id}/reduction-approvals",
    status_code=status.HTTP_201_CREATED,
    response_model=FeeReductionApprovalCreateOut,
    summary="Create a fee reduction approval",
)
def create_fee_reduction_approval(
    case_id: str,
    payload: FeeReductionApprovalCreateIn,
    response: Response,
    _perm: None = Depends(require_perm("Fee.Edit")),
    current_user: T_User = current_user_dep,
    db: Session = Depends(get_db),
) -> FeeReductionApprovalCreateOut:
    if payload.case_id != case_id:
        raise_business_error(
            "FEE_REDUCTION_APPROVAL_CASE_MISMATCH",
            "费用减免审批案件标识不匹配",
            details={
                "path_case_id": case_id,
                "body_case_id": payload.case_id,
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    command = RecordFeeReductionApprovalCommand(
        case_id=payload.case_id,
        scope_type=payload.scope_type,
        applicant_ids=payload.applicant_ids,
        eligibility_attributes_version=payload.eligibility_attributes_version,
        eligibility_attributes_json=payload.eligibility_attributes_json,
        reduction_ratio=payload.reduction_ratio,
        fee_codes=payload.fee_codes,
        fee_year_from=payload.fee_year_from,
        fee_year_to=payload.fee_year_to,
        effective_from=payload.effective_from,
        effective_to=payload.effective_to,
        source_evidence_version_id=payload.source_evidence_version_id,
        expected_source_content_hash=payload.expected_source_content_hash,
        confirmed_at=payload.confirmed_at,
        confirmed_by=current_user.id,
    )
    try:
        result = record_fee_reduction_approval(command, db)
        db.commit()
    except Exception:
        db.rollback()
        raise

    if result.disposition is FeeReductionApprovalRecordDisposition.REUSED:
        response.status_code = status.HTTP_200_OK
    return FeeReductionApprovalCreateOut(approval_id=result.approval_id)


@router.post(
    "/fees/obligations/{obligation_id}/instruction",
    status_code=status.HTTP_200_OK,
    response_model=FeeObligationInstructionOut,
    summary="Record a fee obligation client instruction",
)
def record_fee_obligation_instruction(
    obligation_id: str,
    payload: FeeObligationInstructionIn,
    _perm: None = Depends(require_perm("Fee.Edit")),
    current_user: T_User = current_user_dep,
    db: Session = Depends(get_db),
) -> FeeObligationInstructionOut:
    command = RecordFeeObligationInstructionCommand(
        obligation_id=obligation_id,
        instruction=payload.instruction,
        actor_id=current_user.id,
        idempotency_key=payload.idempotency_key,
    )
    try:
        result = record_client_instruction(command, db)
    except BusinessError:
        db.rollback()
        raise

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    return FeeObligationInstructionOut(
        obligation_id=result.obligation.id,
        client_instruction_status=result.obligation.statuses.client_instruction_status,
        activity_id=result.activity_id,
        idempotency_key=result.idempotency_key,
        reused=result.reused,
    )


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
