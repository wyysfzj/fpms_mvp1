from __future__ import annotations

import json
from datetime import date
from decimal import Decimal
from typing import Any

from fastapi import APIRouter, Depends, Path, Query, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.api.deps import current_user_dep, require_perm
from app.common.doc_render.renderer import DocxRenderer
from app.core.errors import BusinessError, raise_business_error
from app.db.session import get_db
from app.models.letter_head import LetterHead
from app.models.system_param import SystemParam
from app.modules.annuity.models import GovPayment, PayList
from app.modules.auth.models import T_User
from app.modules.billing.doc_render_bill_context import BillContextBuilder
from app.modules.billing.models import (
    Bill,
    BillItem,
    CaseReceipt,
    DemoFinanceCommand,
    Offset,
    Payment,
    PaymentLine,
)
from app.modules.billing.schemas import (
    BillBadDebtActionSchema,
    BillBadDebtRecoveryActionSchema,
    BillBadDebtRecoveryResponse,
    BillBadDebtVoucherResponse,
    BillDetailResponse,
    BillFromDraftsRequest,
    BillItemDetailResponse,
    BillListItemResponse,
    BillListReportSummaryResponse,
    BillListResponse,
    BillManualCreateSchema,
    BillResponse,
    CaseReceiptCreate,
    CaseReceiptResponse,
    CaseReceiptUpdate,
    DemoBankReceiptRequest,
    DemoBankReceiptResponse,
    DemoBillFromDraftRequest,
    DemoBillFromDraftResponse,
    DemoCaseReceiptOut,
    DemoFullOffsetRequest,
    DemoFullOffsetResponse,
    DemoGovPaymentRequest,
    DemoGovPaymentResponse,
    DemoOffsetOut,
    DemoPaymentLineOut,
    DemoPaymentOut,
    FeeOverviewCaseReceiptListResponse,
    FeeOverviewGovPaymentListResponse,
    FeeUnifiedQueryListResponse,
    OffsetCreateSchema,
    OffsetListItemResponse,
    OffsetResponse,
    PaymentListResponse,
    PaymentResponse,
    PaymentSchema,
)
from app.modules.billing.service import (
    DemoBankReceiptResult,
    DemoBillFromDraftResult,
    DemoFullOffsetResult,
    DemoGovPaymentResult,
    abandon_demo_finance_command,
    apply_bill_bad_debt_action,
    apply_bill_bad_debt_recovery,
    build_bill_report_item,
    complete_demo_finance_command,
    create_case_receipt,
    create_demo_bank_receipt,
    create_demo_bill_from_draft,
    create_demo_full_offset,
    create_demo_gov_payment,
    create_manual_bill_record,
    generate_bill_from_drafts,
    get_demo_finance_command,
    list_bills,
    list_case_receipts,
    list_fee_overview_case_receipts,
    list_fee_overview_gov_payments,
    list_fee_unified_queries,
    list_payments,
    load_bill_bad_debt_chain,
    process_payment,
    reconcile_demo_bank_receipt,
    reconcile_demo_bill_from_draft,
    reconcile_demo_full_offset,
    reconcile_demo_gov_payment,
    reserve_demo_finance_command,
    update_case_receipt,
)
from app.modules.billing.service import (
    create_offset as create_offset_service,
)
from app.modules.billing.service import (
    list_offsets as list_offsets_service,
)
from app.modules.billing.service import (
    reverse_offset as reverse_offset_service,
)
from app.modules.cases.models import Case
from app.modules.fees.models import FeeDraft
from app.modules.masterdata.clients.models import Client

router = APIRouter()


def _demo_command_snapshot(response: Any) -> str:
    frozen = response.model_copy(update={"reused": False})
    return json.dumps(
        frozen.model_dump(mode="json"),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def _complete_demo_command(
    db: Session,
    *,
    command_id: str,
    actor_id: str,
    response: Any,
) -> None:
    complete_demo_finance_command(
        db,
        command_id=command_id,
        actor_id=actor_id,
        result_snapshot=_demo_command_snapshot(response),
    )


def _stored_demo_command_response(model: Any, snapshot: str) -> Any:
    return model.model_validate_json(snapshot).model_copy(update={"reused": True})


def _pending_demo_command(idempotency_key: str) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_202_ACCEPTED,
        content={"idempotency_key": idempotency_key, "status": "IN_PROGRESS"},
    )


def _get_client_display_name(client: Client | None) -> str | None:
    if not client:
        return None
    return client.name_cn or client.name_en


def _build_draft_display_label(draft: FeeDraft) -> str:
    return f"{draft.draft_type}-{draft.id[:8].upper()}"


def _build_bill_detail_response(db: Session, bill_id: str) -> BillDetailResponse:
    bill = db.query(Bill).filter(Bill.id == bill_id).first()
    if not bill:
        raise_business_error(
            "BILL_NOT_FOUND",
            "Bill not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    bill_items = (
        db.query(BillItem)
        .filter(BillItem.bill_id == bill_id)
        .order_by(BillItem.created_at.asc())
        .all()
    )
    client = db.query(Client).filter(Client.id == bill.client_id).first()

    case_ids = [item.case_id for item in bill_items if item.case_id]
    unique_case_ids = list(dict.fromkeys(case_ids))
    case_map: dict[str, Case] = {}
    if unique_case_ids:
        cases = db.query(Case).filter(Case.id.in_(unique_case_ids)).all()
        case_map = {case.id: case for case in cases}

    draft_ids = [item.draft_id for item in bill_items if item.draft_id]
    unique_draft_ids = list(dict.fromkeys(draft_ids))
    draft_map: dict[str, FeeDraft] = {}
    if unique_draft_ids:
        drafts = db.query(FeeDraft).filter(FeeDraft.id.in_(unique_draft_ids)).all()
        draft_map = {draft.id: draft for draft in drafts}

    primary_case_id = unique_case_ids[0] if len(unique_case_ids) == 1 else None
    primary_case = case_map.get(primary_case_id) if primary_case_id else None

    source_draft_labels = [
        _build_draft_display_label(draft_map[draft_id])
        for draft_id in unique_draft_ids
        if draft_id in draft_map
    ]
    primary_draft_id = unique_draft_ids[0] if unique_draft_ids else None
    primary_draft = draft_map.get(primary_draft_id) if primary_draft_id else None

    items = [
        BillItemDetailResponse(
            id=item.id,
            bill_id=item.bill_id,
            case_id=item.case_id,
            draft_id=item.draft_id,
            fee_code=item.fee_code,
            fee_name=item.fee_name,
            fee_type=item.fee_type,
            year_no=item.year_no,
            description=item.fee_name or item.fee_code or "账单明细",
            quantity=1,
            unit_price=item.amount,
            amount=item.amount,
        )
        for item in bill_items
    ]

    bad_debt_voucher, bad_debt_recoveries, bad_debt_total_recovered, bad_debt_remaining_amount = (
        load_bill_bad_debt_chain(db, bill.id)
    )

    return BillDetailResponse(
        id=bill.id,
        bill_no=bill.bill_no,
        client_id=bill.client_id,
        client_name=_get_client_display_name(client),
        case_id=primary_case.id if primary_case else None,
        case_no=primary_case.case_no if primary_case else None,
        currency=bill.currency,
        direction=bill.direction,
        status=bill.status,
        bad_debt_status=bill.bad_debt_status,
        bad_debt_substatus=bill.bad_debt_substatus,
        total_gov=bill.total_gov,
        total_service=bill.total_service,
        total_misc=bill.total_misc,
        amount=bill.amount,
        balance=bill.balance,
        bill_date=bill.bill_date,
        due_date=bill.due_date,
        items=items,
        source_draft_ids=unique_draft_ids,
        source_draft_labels=source_draft_labels,
        primary_draft_id=primary_draft.id if primary_draft else None,
        primary_draft_label=_build_draft_display_label(primary_draft) if primary_draft else None,
        bad_debt_voucher=(
            BillBadDebtVoucherResponse(
                id=bad_debt_voucher.id,
                bill_id=bad_debt_voucher.bill_id,
                status=bad_debt_voucher.status,
                bad_debt_amount=bad_debt_voucher.bad_debt_amount,
                recovered_amount=bad_debt_voucher.recovered_amount,
                bad_debt_date=bad_debt_voucher.bad_debt_date,
                remark=bad_debt_voucher.remark,
            )
            if bad_debt_voucher
            else None
        ),
        bad_debt_recoveries=[
            BillBadDebtRecoveryResponse(
                id=recovery.id,
                voucher_id=recovery.voucher_id,
                recovery_amount=recovery.recovery_amount,
                recovery_date=recovery.recovery_date,
                remark=recovery.remark,
            )
            for recovery in bad_debt_recoveries
        ],
        bad_debt_total_recovered=bad_debt_total_recovered,
        bad_debt_remaining_amount=bad_debt_remaining_amount,
    )


@router.get("/bills", summary="List bills", response_model=BillListResponse)
def get_bills(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    client_id: str | None = Query(default=None),
    status: str | None = Query(default=None),
    bill_status: str | None = Query(default=None),
    currency: str | None = Query(default=None),
    bill_date_from: date | None = Query(default=None),
    bill_date_to: date | None = Query(default=None),
    aging_bucket: str | None = Query(default=None),
    is_overdue: bool | None = Query(default=None),
    is_bad_debt: bool | None = Query(default=None),
    bad_debt_status: str | None = Query(default=None),
    _perm: None = Depends(require_perm("Bill.Read")),
    db: Session = Depends(get_db),
) -> BillListResponse:
    """
    List bills with pagination.

    **Auth**: Bearer JWT
    **Permission**: Bill.Read
    **Request example**:
    `GET /api/v1/bills?page=1&page_size=20`
    **Curl example**:
    ```bash
    curl -s -X GET "http://localhost:8000/api/v1/bills?page=1&page_size=20" \\
      -H "Authorization: Bearer $FPMS_TOKEN"
    ```
    **Responses**:
    - 200: List of bills
    - 401: AUTH_REQUIRED
    - 403: FORBIDDEN
    - 422: VALIDATION_ERROR
    """
    bills, total, bad_debt_summary = list_bills(
        db,
        page=page,
        page_size=page_size,
        client_id=client_id,
        status=status,
        bill_status=bill_status,
        currency=currency,
        bill_date_from=bill_date_from,
        bill_date_to=bill_date_to,
        aging_bucket=aging_bucket,
        is_overdue=is_overdue,
        is_bad_debt=is_bad_debt,
        bad_debt_status=bad_debt_status,
    )

    # Batch-resolve client names for all bills in this page
    client_ids = {bill.client_id for bill in bills if bill.client_id}
    client_name_map: dict[str, str] = {}
    if client_ids:
        clients = db.query(Client.id, Client.name_cn).filter(Client.id.in_(client_ids)).all()
        client_name_map = {c.id: c.name_cn for c in clients}

    items = [
        BillListItemResponse(
            **build_bill_report_item(bill),
            client_name=client_name_map.get(bill.client_id),
        )
        for bill in bills
    ]
    summary = BillListReportSummaryResponse.model_validate(bad_debt_summary)
    return BillListResponse(
        items=items,
        page=page,
        page_size=page_size,
        total=total,
        summary=summary,
        bad_debt_bill_count=summary.bad_debt_bill_count,
        bad_debt_amount=summary.bad_debt_amount,
        total_recovered_amount=summary.total_recovered_amount,
        remaining_bad_debt_balance=summary.remaining_bad_debt_balance,
    )


@router.post(
    "/bills/demo-from-draft",
    status_code=status.HTTP_201_CREATED,
    response_model=DemoBillFromDraftResponse,
    summary="Create or replay one local-demo AR bill",
)
def create_local_demo_bill_from_draft(
    payload: DemoBillFromDraftRequest,
    _perm: None = Depends(require_perm("Bill.Create")),
    current_user: T_User = current_user_dep,
    db: Session = Depends(get_db),
) -> DemoBillFromDraftResponse | Response:
    actor_id = str(current_user.id)
    reservation = reserve_demo_finance_command(
        db,
        operation="BILL",
        idempotency_key=payload.idempotency_key,
        actor_id=actor_id,
        payload=payload.model_dump(mode="json"),
    )
    if reservation.state == "COMPLETED" and reservation.result_snapshot is not None:
        return _stored_demo_command_response(
            DemoBillFromDraftResponse, reservation.result_snapshot
        )
    if not reservation.created:
        try:
            result = reconcile_demo_bill_from_draft(
                db, payload.idempotency_key, actor_id=actor_id
            )
        except BusinessError as exc:
            if exc.status_code == 404:
                return _pending_demo_command(payload.idempotency_key)
            raise
        response = _demo_bill_command_response(db, result)
        _complete_demo_command(
            db,
            command_id=reservation.command_id,
            actor_id=actor_id,
            response=response,
        )
        return response
    try:
        result = create_demo_bill_from_draft(db, payload, actor_id=actor_id)
    except BusinessError:
        abandon_demo_finance_command(
            db, command_id=reservation.command_id, actor_id=actor_id
        )
        raise
    response = _demo_bill_command_response(db, result)
    _complete_demo_command(
        db,
        command_id=reservation.command_id,
        actor_id=actor_id,
        response=response,
    )
    return response


def _demo_bill_command_response(
    db: Session, result: DemoBillFromDraftResult
) -> DemoBillFromDraftResponse:
    return DemoBillFromDraftResponse(
        bill=_build_bill_detail_response(db, result.bill_id),
        idempotency_key=result.idempotency_key,
        reused=result.reused,
    )


@router.get(
    "/bills/from-drafts/idempotency/{idempotency_key}",
    response_model=DemoBillFromDraftResponse,
    summary="Reconcile one local-demo AR bill command",
)
def reconcile_local_demo_bill_from_draft(
    idempotency_key: str,
    _perm: None = Depends(require_perm("Bill.Read")),
    current_user: T_User = current_user_dep,
    db: Session = Depends(get_db),
) -> DemoBillFromDraftResponse | Response:
    actor_id = str(current_user.id)
    command = get_demo_finance_command(
        db,
        operation="BILL",
        idempotency_key=idempotency_key,
        actor_id=actor_id,
    )
    if command is None:
        raise_business_error(
            "DEMO_BILL_COMMAND_NOT_FOUND",
            "未找到可对账的账单命令",
            status_code=404,
        )
    if command.state == "COMPLETED" and command.result_snapshot is not None:
        return _stored_demo_command_response(
            DemoBillFromDraftResponse, command.result_snapshot
        )
    try:
        result = reconcile_demo_bill_from_draft(db, idempotency_key, actor_id=actor_id)
    except BusinessError as exc:
        if exc.status_code == 404:
            return _pending_demo_command(idempotency_key)
        raise
    response = _demo_bill_command_response(db, result)
    _complete_demo_command(
        db, command_id=command.id, actor_id=actor_id, response=response
    )
    return response


def _demo_gov_payment_command_response(
    db: Session,
    result: DemoGovPaymentResult,
) -> DemoGovPaymentResponse:
    payment = db.get(GovPayment, result.gov_payment_id)
    pay_list = db.get(PayList, payment.pay_list_id) if payment is not None else None
    if payment is None or pay_list is None:
        raise_business_error(
            "DEMO_GOV_PAYMENT_STORED_STATE_INVALID",
            "官费登记存量状态无效",
            status_code=409,
        )
    return DemoGovPaymentResponse(
        gov_payment={
            "id": payment.id,
            "pay_list_id": payment.pay_list_id,
            "case_id": payment.case_id,
            "fee_item_id": payment.fee_item_id,
            "status": payment.status,
            "currency": payment.currency,
            "paid_date": payment.paid_date,
            "paid_amount": payment.paid_amount,
            "official_receipt_no": payment.official_receipt_no,
            "remark": payment.remark,
            "fee_code": payment.fee_code,
            "year_no": payment.year_no,
            "planned_amt": payment.planned_amt,
            "planned_currency": payment.planned_currency,
            "paid_currency": payment.paid_currency,
            "voucher_no": payment.voucher_no,
            "invoice_no": payment.invoice_no,
        },
        pay_list={
            "id": pay_list.id,
            "pay_list_no": pay_list.pay_list_no,
            "total_amount": pay_list.total_amount,
            "currency": pay_list.currency,
            "client_id": pay_list.client_id,
        },
        fact_status="REGISTERED_PENDING_OFFICIAL_EVIDENCE",
        idempotency_key=result.idempotency_key,
        reused=result.reused,
    )


def _reconciled_demo_gov_payment_response(
    db: Session,
    *,
    command: DemoFinanceCommand,
    actor_id: str,
) -> DemoGovPaymentResponse:
    if command.result_snapshot is None:
        raise_business_error(
            "DEMO_GOV_PAYMENT_STORED_STATE_INVALID",
            "官费登记存量状态无效",
            status_code=409,
        )
    result = reconcile_demo_gov_payment(
        db,
        command.idempotency_key,
        actor_id=actor_id,
    )
    current = _demo_gov_payment_command_response(db, result)
    try:
        stored = _stored_demo_command_response(
            DemoGovPaymentResponse,
            command.result_snapshot,
        )
    except ValidationError:
        raise_business_error(
            "DEMO_GOV_PAYMENT_STORED_STATE_INVALID",
            "官费登记存量状态无效",
            status_code=409,
        )
    if current != stored:
        raise_business_error(
            "DEMO_GOV_PAYMENT_STORED_STATE_INVALID",
            "官费登记存量状态与权威对象不一致",
            status_code=409,
        )
    return current


@router.post(
    "/gov-payments/demo-command",
    status_code=status.HTTP_201_CREATED,
    response_model=DemoGovPaymentResponse,
    summary="登记或恢复本地演示官费付款",
)
def create_local_demo_gov_payment(
    payload: DemoGovPaymentRequest,
    response: Response,
    _perm: None = Depends(require_perm("GovPayment.Create")),
    current_user: T_User = current_user_dep,
    db: Session = Depends(get_db),
) -> DemoGovPaymentResponse | Response:
    actor_id = str(current_user.id)
    reservation = reserve_demo_finance_command(
        db,
        operation="GOV_PAYMENT",
        idempotency_key=payload.idempotency_key,
        actor_id=actor_id,
        payload=payload.model_dump(mode="json"),
    )
    if reservation.state == "COMPLETED" and reservation.result_snapshot is not None:
        response.status_code = status.HTTP_200_OK
        command = get_demo_finance_command(
            db,
            operation="GOV_PAYMENT",
            idempotency_key=payload.idempotency_key,
            actor_id=actor_id,
        )
        if command is None:
            raise_business_error(
                "DEMO_GOV_PAYMENT_COMMAND_NOT_FOUND",
                "未找到可恢复的官费登记命令",
                status_code=404,
            )
        return _reconciled_demo_gov_payment_response(
            db,
            command=command,
            actor_id=actor_id,
        )
    if not reservation.created:
        try:
            result = reconcile_demo_gov_payment(
                db,
                payload.idempotency_key,
                actor_id=actor_id,
            )
        except BusinessError as exc:
            if exc.status_code == 404:
                return _pending_demo_command(payload.idempotency_key)
            raise
        command_response = _demo_gov_payment_command_response(db, result)
        _complete_demo_command(
            db,
            command_id=reservation.command_id,
            actor_id=actor_id,
            response=command_response,
        )
        response.status_code = status.HTTP_200_OK
        return command_response
    try:
        result = create_demo_gov_payment(db, payload, actor_id=actor_id)
    except BusinessError:
        abandon_demo_finance_command(
            db,
            command_id=reservation.command_id,
            actor_id=actor_id,
        )
        raise
    command_response = _demo_gov_payment_command_response(db, result)
    _complete_demo_command(
        db,
        command_id=reservation.command_id,
        actor_id=actor_id,
        response=command_response,
    )
    return command_response


@router.get(
    "/gov-payments/idempotency/{idempotency_key}",
    response_model=DemoGovPaymentResponse,
    summary="按幂等键恢复本地演示官费登记",
)
def reconcile_local_demo_gov_payment(
    idempotency_key: str = Path(..., min_length=1, max_length=96),
    _perm: None = Depends(require_perm("GovPayment.Create")),
    current_user: T_User = current_user_dep,
    db: Session = Depends(get_db),
) -> DemoGovPaymentResponse | Response:
    actor_id = str(current_user.id)
    command = get_demo_finance_command(
        db,
        operation="GOV_PAYMENT",
        idempotency_key=idempotency_key,
        actor_id=actor_id,
    )
    if command is None:
        raise_business_error(
            "DEMO_GOV_PAYMENT_COMMAND_NOT_FOUND",
            "未找到可恢复的官费登记命令",
            status_code=404,
        )
    if command.state == "COMPLETED" and command.result_snapshot is not None:
        return _reconciled_demo_gov_payment_response(
            db,
            command=command,
            actor_id=actor_id,
        )
    try:
        result = reconcile_demo_gov_payment(
            db,
            idempotency_key,
            actor_id=actor_id,
        )
    except BusinessError as exc:
        if exc.status_code == 404:
            return _pending_demo_command(idempotency_key)
        raise
    command_response = _demo_gov_payment_command_response(db, result)
    _complete_demo_command(
        db,
        command_id=command.id,
        actor_id=actor_id,
        response=command_response,
    )
    return command_response


def _demo_payment_out(payment: Payment) -> DemoPaymentOut:
    return DemoPaymentOut(
        id=payment.id,
        pay_no=payment.pay_no or "",
        client_id=payment.client_id,
        pay_date=payment.pay_date,
        currency=payment.currency,
        amount=payment.amount,
        pay_method=payment.pay_method or "",
        bank_ref_no=payment.bank_ref_no or "",
        remark=payment.remark,
    )


def _demo_line_out(line: PaymentLine) -> DemoPaymentLineOut:
    status_value = "FULLY_ALLOCATED" if line.balance_amt == 0 else "UNALLOCATED"
    return DemoPaymentLineOut(
        id=line.id,
        payment_id=line.payment_id,
        case_id=line.case_id or "",
        raw_amount=line.raw_amount,
        allocated_amt=line.allocated_amt,
        balance_amt=line.balance_amt,
        status=status_value,
    )


@router.post(
    "/payments/demo-bank-receipts",
    status_code=status.HTTP_201_CREATED,
    response_model=DemoBankReceiptResponse,
    summary="Record or replay one local-demo customer bank receipt",
)
def create_local_demo_bank_receipt(
    payload: DemoBankReceiptRequest,
    _perm: None = Depends(require_perm("Payment.Create")),
    current_user: T_User = current_user_dep,
    db: Session = Depends(get_db),
) -> DemoBankReceiptResponse | Response:
    actor_id = str(current_user.id)
    reservation = reserve_demo_finance_command(
        db,
        operation="PAYMENT",
        idempotency_key=payload.idempotency_key,
        actor_id=actor_id,
        payload=payload.model_dump(mode="json"),
    )
    if reservation.state == "COMPLETED" and reservation.result_snapshot is not None:
        return _stored_demo_command_response(
            DemoBankReceiptResponse, reservation.result_snapshot
        )
    if not reservation.created:
        try:
            result = reconcile_demo_bank_receipt(
                db, payload.idempotency_key, actor_id=actor_id
            )
        except BusinessError as exc:
            if exc.status_code != 404:
                raise
        else:
            response = _demo_bank_receipt_command_response(db, result)
            _complete_demo_command(
                db,
                command_id=reservation.command_id,
                actor_id=actor_id,
                response=response,
            )
            return response
    try:
        result = create_demo_bank_receipt(db, payload, actor_id=actor_id)
    except BusinessError as exc:
        if exc.code != "DEMO_FINANCE_WRITE_BUSY":
            abandon_demo_finance_command(
                db, command_id=reservation.command_id, actor_id=actor_id
            )
        raise
    response = _demo_bank_receipt_command_response(db, result)
    _complete_demo_command(
        db,
        command_id=reservation.command_id,
        actor_id=actor_id,
        response=response,
    )
    return response


def _demo_bank_receipt_command_response(
    db: Session, result: DemoBankReceiptResult
) -> DemoBankReceiptResponse:
    payment = db.get(Payment, result.payment_id)
    line = db.get(PaymentLine, result.line_id)
    if payment is None or line is None:
        raise_business_error(
            "DEMO_PAYMENT_STORED_STATE_INVALID",
            "回款存量状态无效",
            status_code=409,
        )
    return DemoBankReceiptResponse(
        payment=_demo_payment_out(payment),
        line=_demo_line_out(line),
        bill=_build_bill_detail_response(db, result.target_bill_id),
        target_bill_id=result.target_bill_id,
        idempotency_key=result.idempotency_key,
        reused=result.reused,
    )


@router.get(
    "/payments/idempotency/{idempotency_key}",
    response_model=DemoBankReceiptResponse,
    summary="Reconcile one local-demo bank receipt command",
)
def reconcile_local_demo_bank_receipt(
    idempotency_key: str,
    _perm: None = Depends(require_perm("Payment.Read")),
    current_user: T_User = current_user_dep,
    db: Session = Depends(get_db),
) -> DemoBankReceiptResponse | Response:
    actor_id = str(current_user.id)
    command = get_demo_finance_command(
        db,
        operation="PAYMENT",
        idempotency_key=idempotency_key,
        actor_id=actor_id,
    )
    if command is None:
        raise_business_error(
            "DEMO_PAYMENT_COMMAND_NOT_FOUND",
            "未找到可对账的回款命令",
            status_code=404,
        )
    if command.state == "COMPLETED" and command.result_snapshot is not None:
        return _stored_demo_command_response(DemoBankReceiptResponse, command.result_snapshot)
    try:
        result = reconcile_demo_bank_receipt(db, idempotency_key, actor_id=actor_id)
    except BusinessError as exc:
        if exc.status_code == 404:
            return _pending_demo_command(idempotency_key)
        raise
    response = _demo_bank_receipt_command_response(db, result)
    _complete_demo_command(
        db, command_id=command.id, actor_id=actor_id, response=response
    )
    return response


@router.post(
    "/offsets/demo-full",
    status_code=status.HTTP_201_CREATED,
    response_model=DemoFullOffsetResponse,
    summary="Create or replay one local-demo full offset",
)
def create_local_demo_full_offset(
    payload: DemoFullOffsetRequest,
    _perm: None = Depends(require_perm("Payment.Create")),
    current_user: T_User = current_user_dep,
    db: Session = Depends(get_db),
) -> DemoFullOffsetResponse | Response:
    actor_id = str(current_user.id)
    reservation = reserve_demo_finance_command(
        db,
        operation="OFFSET",
        idempotency_key=payload.idempotency_key,
        actor_id=actor_id,
        payload=payload.model_dump(mode="json"),
    )
    if reservation.state == "COMPLETED" and reservation.result_snapshot is not None:
        return _stored_demo_command_response(
            DemoFullOffsetResponse, reservation.result_snapshot
        )
    if not reservation.created:
        try:
            result = reconcile_demo_full_offset(
                db, payload.idempotency_key, actor_id=actor_id
            )
        except BusinessError as exc:
            if exc.status_code != 404:
                raise
        else:
            response = _demo_full_offset_command_response(db, result)
            _complete_demo_command(
                db,
                command_id=reservation.command_id,
                actor_id=actor_id,
                response=response,
            )
            return response
    try:
        result = create_demo_full_offset(db, payload, actor_id=actor_id)
    except BusinessError as exc:
        if exc.code != "DEMO_FINANCE_WRITE_BUSY":
            abandon_demo_finance_command(
                db, command_id=reservation.command_id, actor_id=actor_id
            )
        raise
    response = _demo_full_offset_command_response(db, result)
    _complete_demo_command(
        db,
        command_id=reservation.command_id,
        actor_id=actor_id,
        response=response,
    )
    return response


def _demo_full_offset_command_response(
    db: Session, result: DemoFullOffsetResult
) -> DemoFullOffsetResponse:
    offset = db.get(Offset, result.offset_id)
    line = db.get(PaymentLine, result.line_id)
    receipt = db.get(CaseReceipt, result.receipt_id)
    if offset is None or line is None or receipt is None:
        raise_business_error(
            "DEMO_OFFSET_STORED_STATE_INVALID",
            "核销存量状态无效",
            status_code=409,
        )
    return DemoFullOffsetResponse(
        offset=DemoOffsetOut(
            id=offset.id,
            payment_line_id=offset.payment_line_id,
            bill_id=offset.bill_id,
            offset_amt=offset.offset_amt,
            offset_date=offset.offset_date,
            is_reversed=offset.is_reversed,
        ),
        bill=_build_bill_detail_response(db, result.bill_id),
        line=_demo_line_out(line),
        case_receipt=DemoCaseReceiptOut(
            id=receipt.id,
            case_id=receipt.case_id,
            fee_type=receipt.fee_type or "",
            fee_code=receipt.fee_code or "",
            currency=receipt.currency,
            receivable_amt=receipt.receivable_amt,
            received_amt=receipt.received_amt,
            last_receipt_date=receipt.last_receipt_date,
        ),
        idempotency_key=result.idempotency_key,
        reused=result.reused,
    )


@router.get(
    "/offsets/idempotency/{idempotency_key}",
    response_model=DemoFullOffsetResponse,
    summary="Reconcile one local-demo full offset command",
)
def reconcile_local_demo_full_offset(
    idempotency_key: str,
    _perm: None = Depends(require_perm("Bill.Read")),
    current_user: T_User = current_user_dep,
    db: Session = Depends(get_db),
) -> DemoFullOffsetResponse | Response:
    actor_id = str(current_user.id)
    command = get_demo_finance_command(
        db,
        operation="OFFSET",
        idempotency_key=idempotency_key,
        actor_id=actor_id,
    )
    if command is None:
        raise_business_error(
            "DEMO_OFFSET_COMMAND_NOT_FOUND",
            "未找到可对账的核销命令",
            status_code=404,
        )
    if command.state == "COMPLETED" and command.result_snapshot is not None:
        return _stored_demo_command_response(DemoFullOffsetResponse, command.result_snapshot)
    try:
        result = reconcile_demo_full_offset(db, idempotency_key, actor_id=actor_id)
    except BusinessError as exc:
        if exc.status_code == 404:
            return _pending_demo_command(idempotency_key)
        raise
    response = _demo_full_offset_command_response(db, result)
    _complete_demo_command(
        db, command_id=command.id, actor_id=actor_id, response=response
    )
    return response


@router.post(
    "/bills/from-drafts",
    status_code=status.HTTP_201_CREATED,
    response_model=BillResponse,
    summary="Create a bill from fee drafts",
)
def create_bill_from_drafts(
    payload: BillFromDraftsRequest,
    _perm: None = Depends(require_perm("Bill.Create")),
    db: Session = Depends(get_db),
) -> BillResponse:
    """
    Create a bill from fee drafts.

    **Auth**: Bearer JWT
    **Permission**: Bill.Create
    **Request example**:
    ```json
    {"draft_ids": ["DRAFT_ID_1", "DRAFT_ID_2"], "bill_no": "BILL-001"}
    ```
    **Curl example**:
    ```bash
    curl -s -X POST http://localhost:8000/api/v1/bills/from-drafts \\
      -H "Authorization: Bearer $FPMS_TOKEN" \\
      -H "Content-Type: application/json" \\
      -d '{"draft_ids":["DRAFT_ID_1","DRAFT_ID_2"],"bill_no":"BILL-001"}'
    ```
    **Responses**:
    - 201: Bill created
    - 400: Invalid drafts or totals
    - 401: AUTH_REQUIRED
    - 403: FORBIDDEN
    - 404: Drafts not found
    - 422: VALIDATION_ERROR
    """
    bill = generate_bill_from_drafts(db, payload)
    return BillResponse(
        id=bill.id,
        bill_no=bill.bill_no,
        client_id=bill.client_id,
        currency=bill.currency,
        direction=bill.direction,
        status=bill.status,
    )


@router.get("/bills/{bill_id}/print", summary="Print a bill document")
def print_bill(
    bill_id: str,
    _perm: None = Depends(require_perm("Bill.Print")),
    db: Session = Depends(get_db),
) -> Response:
    """
    Generate and download a bill document.

    **Auth**: Bearer JWT
    **Permission**: Bill.Print
    **Request example**:
    `GET /api/v1/bills/BILL_ID/print`
    **Curl example**:
    ```bash
    curl -s -X GET http://localhost:8000/api/v1/bills/BILL_ID/print \\
      -H "Authorization: Bearer $FPMS_TOKEN" \\
      -o bill.docx
    ```
    **Responses**:
    - 200: Bill DOCX
    - 401: AUTH_REQUIRED
    - 403: FORBIDDEN
    - 404: Bill or client not found
    - 409: Bill template not configured
    - 422: VALIDATION_ERROR
    - 500: Template file missing
    """
    bill = db.query(Bill).filter(Bill.id == bill_id).first()
    if not bill:
        raise_business_error(
            "BILL_NOT_FOUND",
            "Bill not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    bill_items = db.query(BillItem).filter(BillItem.bill_id == bill.id).all()
    client = db.query(Client).filter(Client.id == bill.client_id).first()
    if not client:
        raise_business_error(
            "CLIENT_NOT_FOUND",
            "Client not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    letter_head = (
        db.query(LetterHead)
        .filter(LetterHead.is_default.is_(True))
        .order_by(LetterHead.created_at.desc())
        .first()
    )

    template_path = getattr(bill, "template_path", None) or getattr(
        bill, "template_file_path", None
    )
    if not template_path:
        param = db.query(SystemParam).filter(SystemParam.param_key == "bill_template_path").first()
        template_path = param.param_value if param else None

    if not template_path:
        raise_business_error(
            "BILL_TEMPLATE_NOT_CONFIGURED",
            "Bill template not configured",
            status_code=status.HTTP_409_CONFLICT,
        )

    context = BillContextBuilder().build(bill, bill_items, client, letter_head)
    renderer = DocxRenderer()
    try:
        docx_bytes = renderer.render_docx_bytes(template_path, context)
    except FileNotFoundError as exc:
        raise_business_error(
            "BILL_TEMPLATE_FILE_MISSING",
            "Template file missing",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"reason": str(exc)},
        )

    headers = {
        "Content-Disposition": f'attachment; filename="bill_{bill.id}.docx"',
    }
    return Response(
        content=docx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers=headers,
    )


@router.post(
    "/bills/{bill_id}/bad-debt",
    response_model=BillDetailResponse,
    summary="Mark bill as bad debt",
)
def mark_bill_bad_debt_action(
    bill_id: str,
    payload: BillBadDebtActionSchema | None = None,
    _perm: None = Depends(require_perm("Billing.BadDebtMark")),
    db: Session = Depends(get_db),
) -> BillDetailResponse:
    """
    Mark an AR bill as bad debt or transfer a partial-payment remainder into bad debt.

    **Auth**: Bearer JWT
    **Permission**: Billing.BadDebtMark
    **Request example**:
    ```json
    {"mode": "TRANSFER", "remark": "剩余部分转坏账"}
    ```
    **Responses**:
    - 200: Bill detail with bad-debt chain
    - 400: Bill not eligible for bad debt
    - 401: AUTH_REQUIRED
    - 403: FORBIDDEN
    - 404: Bill not found
    - 422: VALIDATION_ERROR
    """
    bill = apply_bill_bad_debt_action(db, bill_id=bill_id, data=payload)
    return _build_bill_detail_response(db, bill.id)


@router.post(
    "/bills/{bill_id}/bad-debt/recover",
    response_model=BillDetailResponse,
    summary="Recover bad debt",
)
def recover_bill_bad_debt_action(
    bill_id: str,
    payload: BillBadDebtRecoveryActionSchema,
    _perm: None = Depends(require_perm("Billing.BadDebtRecover")),
    db: Session = Depends(get_db),
) -> BillDetailResponse:
    """
    Record a bad-debt recovery against an effective bad-debt voucher.

    **Auth**: Bearer JWT
    **Permission**: Billing.BadDebtRecover
    **Request example**:
    ```json
    {"recovery_amount": "50.00", "remark": "回收坏账"}
    ```
    **Responses**:
    - 200: Bill detail with updated bad-debt chain
    - 400: Recovery is invalid or exceeds remaining bad debt
    - 401: AUTH_REQUIRED
    - 403: FORBIDDEN
    - 404: Bill not found
    - 422: VALIDATION_ERROR
    """
    bill = apply_bill_bad_debt_recovery(db, bill_id=bill_id, data=payload)
    return _build_bill_detail_response(db, bill.id)


@router.get("/payments", summary="List payments")
def get_payments(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    bill_id: str | None = Query(default=None),
    client_id: str | None = Query(default=None),
    prepayment_status: str | None = Query(default=None),
    pay_date_from: date | None = Query(default=None),
    pay_date_to: date | None = Query(default=None),
    has_unapplied_only: bool = Query(default=False),
    _perm: None = Depends(require_perm("Payment.Read")),
    db: Session = Depends(get_db),
) -> PaymentListResponse:
    """
    List payments with pagination.

    **Auth**: Bearer JWT
    **Permission**: Payment.Read
    **Request example**:
    `GET /api/v1/payments?page=1&page_size=20`
    **Curl example**:
    ```bash
    curl -s -X GET "http://localhost:8000/api/v1/payments?page=1&page_size=20" \\
      -H "Authorization: Bearer $FPMS_TOKEN"
    ```
    **Responses**:
    - 200: List of payments
    - 401: AUTH_REQUIRED
    - 403: FORBIDDEN
    - 422: VALIDATION_ERROR
    """
    return PaymentListResponse(
        **list_payments(
            db,
            bill_id=bill_id,
            client_id=client_id,
            prepayment_status=prepayment_status,
            pay_date_from=pay_date_from,
            pay_date_to=pay_date_to,
            has_unapplied_only=has_unapplied_only,
            page=page,
            page_size=page_size,
        )
    )


@router.get(
    "/fee-overview/case-receipts",
    response_model=FeeOverviewCaseReceiptListResponse,
    summary="费用情况查询一览-个案收款情况",
)
def get_fee_overview_case_receipts(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    case_no: str | None = Query(default=None),
    app_no: str | None = Query(default=None),
    patent_no: str | None = Query(default=None),
    client_id: str | None = Query(default=None),
    applicant_name: str | None = Query(default=None),
    fee_type: str | None = Query(default=None),
    receipt_date_from: date | None = Query(default=None),
    receipt_date_to: date | None = Query(default=None),
    _perm: None = Depends(require_perm("CaseReceipt.Read")),
    db: Session = Depends(get_db),
) -> FeeOverviewCaseReceiptListResponse:
    """
    Get the dedicated lower-pane CaseReceipt overview for SPEC 5.11.

    **Auth**: Bearer JWT
    **Permission**: CaseReceipt.Read
    """
    return FeeOverviewCaseReceiptListResponse(
        **list_fee_overview_case_receipts(
            db,
            case_no=case_no,
            app_no=app_no,
            patent_no=patent_no,
            client_id=client_id,
            applicant_name=applicant_name,
            fee_type=fee_type,
            receipt_date_from=receipt_date_from,
            receipt_date_to=receipt_date_to,
            page=page,
            page_size=page_size,
        )
    )


@router.get(
    "/fee-overview/gov-payments",
    response_model=FeeOverviewGovPaymentListResponse,
    summary="费用情况查询一览-官费缴费情况",
)
def get_fee_overview_gov_payments(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    case_no: str | None = Query(default=None),
    app_no: str | None = Query(default=None),
    patent_no: str | None = Query(default=None),
    client_id: str | None = Query(default=None),
    applicant_name: str | None = Query(default=None),
    fee_type: str | None = Query(default=None),
    paid_date_from: date | None = Query(default=None),
    paid_date_to: date | None = Query(default=None),
    _perm: None = Depends(require_perm("PayList.Read")),
    db: Session = Depends(get_db),
) -> FeeOverviewGovPaymentListResponse:
    """
    Get the dedicated upper-pane GovPayment overview for SPEC 5.11.

    **Auth**: Bearer JWT
    **Permission**: PayList.Read
    """
    return FeeOverviewGovPaymentListResponse(
        **list_fee_overview_gov_payments(
            db,
            case_no=case_no,
            app_no=app_no,
            patent_no=patent_no,
            client_id=client_id,
            applicant_name=applicant_name,
            fee_type=fee_type,
            paid_date_from=paid_date_from,
            paid_date_to=paid_date_to,
            page=page,
            page_size=page_size,
        )
    )


@router.get(
    "/fee-unified-query",
    response_model=FeeUnifiedQueryListResponse,
    summary="统一费用查询",
)
def get_fee_unified_query(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    record_type: str | None = Query(default=None),
    case_id: str | None = Query(default=None),
    biz_no: str | None = Query(default=None),
    party_name: str | None = Query(default=None),
    status: str | None = Query(default=None),
    currency: str | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    amount_from: Decimal | None = Query(default=None),
    amount_to: Decimal | None = Query(default=None),
    _payment_perm: None = Depends(require_perm("Payment.Read")),
    _receipt_perm: None = Depends(require_perm("CaseReceipt.Read")),
    db: Session = Depends(get_db),
) -> FeeUnifiedQueryListResponse:
    """
    Get the unified payment and receipt list.

    **Auth**: Bearer JWT
    **Permission**: Payment.Read + CaseReceipt.Read
    """
    return FeeUnifiedQueryListResponse(
        **list_fee_unified_queries(
            db,
            record_type=record_type,
            case_id=case_id,
            biz_no=biz_no,
            party_name=party_name,
            status=status,
            currency=currency,
            date_from=date_from,
            date_to=date_to,
            amount_from=amount_from,
            amount_to=amount_to,
            page=page,
            page_size=page_size,
        )
    )


@router.post(
    "/payments",
    status_code=status.HTTP_201_CREATED,
    response_model=PaymentResponse,
    summary="Create a payment",
)
def create_payment(
    payload: PaymentSchema,
    _perm: None = Depends(require_perm("Payment.Create")),
    db: Session = Depends(get_db),
) -> PaymentResponse:
    """
    Create a payment.

    **Auth**: Bearer JWT
    **Permission**: Payment.Create
    **Request example**:
    ```json
    {"client_id": "CLIENT_ID", "amount": "1000.00", "currency": "CNY"}
    ```
    **Curl example**:
    ```bash
    curl -s -X POST http://localhost:8000/api/v1/payments \\
      -H "Authorization: Bearer $FPMS_TOKEN" \\
      -H "Content-Type: application/json" \\
      -d '{"client_id":"CLIENT_ID","amount":"1000.00","currency":"CNY"}'
    ```
    **Responses**:
    - 201: Payment created
    - 400: Invalid payment amount
    - 401: AUTH_REQUIRED
    - 403: FORBIDDEN
    - 422: VALIDATION_ERROR
    """
    payment = process_payment(db, payload)
    return PaymentResponse(
        id=payment.id,
        pay_no=payment.pay_no,
        bill_id=payload.bill_id,
        client_id=payment.client_id,
        pay_date=payment.pay_date,
        currency=payment.currency,
        amount=payment.amount,
    )


@router.get("/payments/{payment_id}", summary="Get a payment")
def get_payment(
    payment_id: str,
    _perm: None = Depends(require_perm("Payment.Read")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """
    Get a payment by ID.

    **Auth**: Bearer JWT
    **Permission**: Payment.Read
    **Request example**:
    `GET /api/v1/payments/PAYMENT_ID`
    **Curl example**:
    ```bash
    curl -s -X GET http://localhost:8000/api/v1/payments/PAYMENT_ID \\
      -H "Authorization: Bearer $FPMS_TOKEN"
    ```
    **Responses**:
    - 200: Payment details
    - 401: AUTH_REQUIRED
    - 403: FORBIDDEN
    - 404: Payment not found
    - 422: VALIDATION_ERROR
    """
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise_business_error(
            "PAYMENT_NOT_FOUND",
            "Payment not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    payment_lines = (
        db.query(PaymentLine)
        .filter(PaymentLine.payment_id == payment.id)
        .order_by(PaymentLine.created_at.asc())
        .all()
    )

    return {
        "id": payment.id,
        "pay_no": payment.pay_no,
        "client_id": payment.client_id,
        "pay_date": payment.pay_date,
        "currency": payment.currency,
        "amount": payment.amount,
        "payment_lines": [
            {
                "id": line.id,
                "payment_id": line.payment_id,
                "case_id": line.case_id,
                "raw_amount": line.raw_amount,
                "allocated_amt": line.allocated_amt,
                "balance_amt": line.balance_amt,
            }
            for line in payment_lines
        ],
    }


@router.get(
    "/offsets",
    summary="List offsets with optional filters",
)
def list_offsets(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    bill_id: str | None = Query(None),
    is_reversed: bool | None = Query(None),
    _perm: None = Depends(require_perm("Bill.Read")),
    db: Session = Depends(get_db),
) -> dict:
    """
    List offsets with pagination and optional filters.

    **Auth**: Bearer JWT
    **Permission**: Bill.Read
    **Query params**: page, page_size, bill_id, is_reversed
    """
    items, total = list_offsets_service(
        db,
        page=page,
        page_size=page_size,
        bill_id=bill_id,
        is_reversed=is_reversed,
    )

    bill_ids = {o.bill_id for o in items}
    bill_no_map: dict[str, str | None] = {}
    if bill_ids:
        bills = db.query(Bill.id, Bill.bill_no).filter(Bill.id.in_(bill_ids)).all()
        bill_no_map = {b.id: b.bill_no for b in bills}

    return {
        "items": [
            OffsetListItemResponse(
                id=o.id,
                payment_line_id=o.payment_line_id,
                bill_id=o.bill_id,
                bill_no=bill_no_map.get(o.bill_id),
                offset_amt=o.offset_amt,
                offset_date=o.offset_date,
                is_reversed=o.is_reversed,
                reversed_at=o.reversed_at.isoformat() if o.reversed_at else None,
                created_at=o.created_at.isoformat() if o.created_at else None,
            ).model_dump()
            for o in items
        ],
        "page": page,
        "page_size": page_size,
        "total": total,
    }


@router.post(
    "/offsets",
    status_code=status.HTTP_201_CREATED,
    response_model=OffsetResponse,
    summary="Create a payment offset",
)
def create_offset(
    payload: OffsetCreateSchema,
    _perm: None = Depends(require_perm("Payment.Create")),
    db: Session = Depends(get_db),
) -> OffsetResponse:
    """
    Create an offset between a payment line and a bill.

    **Auth**: Bearer JWT
    **Permission**: Payment.Create
    **Request example**:
    ```json
    {"payment_line_id": "PAYMENT_LINE_ID", "bill_id": "BILL_ID", "offset_amt": "500.00"}
    ```
    **Curl example**:
    ```bash
    curl -s -X POST http://localhost:8000/api/v1/offsets \\
      -H "Authorization: Bearer $FPMS_TOKEN" \\
      -H "Content-Type: application/json" \\
      -d '{"payment_line_id":"PAYMENT_LINE_ID","bill_id":"BILL_ID","offset_amt":"500.00"}'
    ```
    **Responses**:
    - 201: Offset created
    - 400: Invalid or mismatched payment/bill data
    - 401: AUTH_REQUIRED
    - 403: FORBIDDEN
    - 404: Payment line, payment, or bill not found
    - 422: VALIDATION_ERROR
    """
    offset = create_offset_service(db, payload)
    return OffsetResponse(
        id=offset.id,
        payment_line_id=offset.payment_line_id,
        bill_id=offset.bill_id,
        offset_amt=offset.offset_amt,
        offset_date=offset.offset_date,
        is_reversed=offset.is_reversed,
    )


@router.post(
    "/offsets/{offset_id}/reverse",
    summary="Reverse an offset",
    response_model=OffsetResponse,
)
def reverse_offset(
    offset_id: str,
    _perm: None = Depends(require_perm("Billing.Edit")),
    db: Session = Depends(get_db),
) -> OffsetResponse:
    """
    Reverse an offset (mark as reversed, restore bill and payment balances).

    **Auth**: Bearer JWT
    **Permission**: Billing.Edit
    **Request example**:
    `POST /api/v1/offsets/OFFSET_ID/reverse`
    **Curl example**:
    ```bash
    curl -s -X POST http://localhost:8000/api/v1/offsets/OFFSET_ID/reverse \\
      -H "Authorization: Bearer $FPMS_TOKEN"
    ```
    **Responses**:
    - 200: Offset reversed
    - 400: Offset already reversed
    - 401: AUTH_REQUIRED
    - 403: FORBIDDEN
    - 404: Offset not found
    - 422: VALIDATION_ERROR
    """
    offset = reverse_offset_service(db, offset_id)
    return OffsetResponse(
        id=offset.id,
        payment_line_id=offset.payment_line_id,
        bill_id=offset.bill_id,
        offset_amt=offset.offset_amt,
        offset_date=offset.offset_date,
        is_reversed=offset.is_reversed,
    )


@router.post("/bills/manual", status_code=status.HTTP_201_CREATED, summary="Create a bill manually")
def create_manual_bill(
    payload: BillManualCreateSchema,
    _perm: None = Depends(require_perm("Bill.Create")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """
    Create a manual bill record.

    **Auth**: Bearer JWT
    **Permission**: Bill.Create
    **Request example**:
    ```json
    {"client_id": "CLIENT_ID", "bill_no": "BILL-001", "currency": "CNY"}
    ```
    **Curl example**:
    ```bash
    curl -s -X POST http://localhost:8000/api/v1/bills/manual \\
      -H "Authorization: Bearer $FPMS_TOKEN" \\
      -H "Content-Type: application/json" \\
      -d '{"client_id":"CLIENT_ID","bill_no":"BILL-001","currency":"CNY"}'
    ```
    **Responses**:
    - 201: Manual bill created
    - 400: client_id is required
    - 401: AUTH_REQUIRED
    - 403: FORBIDDEN
    - 422: VALIDATION_ERROR
    """
    client_id = payload.client_id
    if not client_id:
        raise_business_error(
            "BILL_INVALID",
            "client_id is required",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    bill = create_manual_bill_record(db, payload)
    bill_items = (
        db.query(BillItem)
        .filter(BillItem.bill_id == bill.id)
        .order_by(BillItem.created_at.asc())
        .all()
    )

    return {
        "id": bill.id,
        "bill_no": bill.bill_no,
        "client_id": bill.client_id,
        "currency": bill.currency,
        "direction": bill.direction,
        "status": bill.status,
        "amount": bill.amount,
        "balance": bill.balance,
        "items": [
            {
                "id": item.id,
                "bill_id": item.bill_id,
                "case_id": item.case_id,
                "draft_id": item.draft_id,
                "fee_code": item.fee_code,
                "fee_name": item.fee_name,
                "fee_type": item.fee_type,
                "year_no": item.year_no,
                "description": item.fee_name or item.fee_code or "账单明细",
                "quantity": 1,
                "unit_price": item.amount,
                "amount": item.amount,
            }
            for item in bill_items
        ],
    }


@router.get("/bills/{bill_id}", response_model=BillDetailResponse, summary="Get a bill")
def get_bill(
    bill_id: str,
    _perm: None = Depends(require_perm("Bill.Read")),
    db: Session = Depends(get_db),
) -> BillDetailResponse:
    """
    Get a bill by ID.

    **Auth**: Bearer JWT
    **Permission**: Bill.Read
    **Request example**:
    `GET /api/v1/bills/BILL_ID`
    **Curl example**:
    ```bash
    curl -s -X GET http://localhost:8000/api/v1/bills/BILL_ID \\
      -H "Authorization: Bearer $FPMS_TOKEN"
    ```
    **Responses**:
    - 200: Bill details
    - 401: AUTH_REQUIRED
    - 403: FORBIDDEN
    - 404: Bill not found
    - 422: VALIDATION_ERROR
    """
    return _build_bill_detail_response(db, bill_id)


@router.get(
    "/cases/{case_id}/receipts",
    response_model=CaseReceiptResponse,
    summary="Get case receipt",
)
def get_case_receipt(
    case_id: str,
    _perm: None = Depends(require_perm("CaseReceipt.Read")),
    db: Session = Depends(get_db),
) -> CaseReceiptResponse:
    """
    Get the case receipt summary.

    **Auth**: Bearer JWT
    **Permission**: CaseReceipt.Read
    **Request example**:
    `GET /api/v1/cases/CASE_ID/receipts`
    **Curl example**:
    ```bash
    curl -s -X GET http://localhost:8000/api/v1/cases/CASE_ID/receipts \\
      -H "Authorization: Bearer $FPMS_TOKEN"
    ```
    **Responses**:
    - 200: Case receipt details
    - 401: AUTH_REQUIRED
    - 403: FORBIDDEN
    - 404: Case receipt not found
    - 422: VALIDATION_ERROR
    """
    bill_rows = (
        db.query(
            Bill.id,
            Bill.bill_no,
            Bill.status,
            Bill.amount,
            Bill.balance,
            Bill.bill_date,
            Bill.currency,
            BillItem.amount.label("item_amount"),
            BillItem.fee_code,
            BillItem.fee_name,
            BillItem.fee_type,
            BillItem.year_no,
        )
        .join(BillItem, BillItem.bill_id == Bill.id)
        .filter(BillItem.case_id == case_id)
        .order_by(Bill.bill_date.desc(), Bill.created_at.desc(), Bill.id.desc())
        .all()
    )
    seen_bill_ids: set[str] = set()
    bill_overview_rows: list[dict[str, Any]] = []
    bill_receivable_amt = Decimal("0")
    bill_fee_types: set[str] = set()
    bill_currencies: set[str] = set()
    for row in bill_rows:
        bill_receivable_amt += Decimal(row.item_amount or 0)
        if row.fee_type:
            bill_fee_types.add(row.fee_type)
        if row.currency:
            bill_currencies.add(row.currency)
        if row.id in seen_bill_ids:
            continue
        seen_bill_ids.add(row.id)
        bill_overview_rows.append(
            {
                "id": row.id,
                "bill_no": row.bill_no,
                "status": row.status,
                "amount": row.amount,
                "balance": row.balance,
                "issue_date": row.bill_date,
            }
        )

    receipts = db.query(CaseReceipt).filter(CaseReceipt.case_id == case_id).all()
    if not receipts:
        if not bill_overview_rows:
            raise_business_error(
                "CASE_RECEIPT_NOT_FOUND",
                "Case receipt not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        bill_item = bill_rows[0] if len(bill_rows) == 1 else None
        return CaseReceiptResponse(
            id=case_id,
            case_id=case_id,
            fee_type=next(iter(bill_fee_types)) if len(bill_fee_types) == 1 else "MIXED",
            currency=next(iter(bill_currencies)) if len(bill_currencies) == 1 else "MIXED",
            receivable_amt=bill_receivable_amt,
            received_amt=Decimal("0.00"),
            fee_code=bill_item.fee_code if bill_item else None,
            fee_name=bill_item.fee_name if bill_item else None,
            year_no=bill_item.year_no if bill_item else None,
            is_arrears=bill_receivable_amt > Decimal("0"),
            is_prepayment=False,
            is_commissionable=False,
            bills=bill_overview_rows,
        )

    receipt = receipts[0]
    receivable_amt = sum((Decimal(row.receivable_amt or 0) for row in receipts), Decimal("0"))
    received_amt = sum((Decimal(row.received_amt or 0) for row in receipts), Decimal("0"))
    fee_types = {row.fee_type for row in receipts if row.fee_type}
    currencies = {row.currency for row in receipts if row.currency}
    last_receipt_date = max(
        (row.last_receipt_date for row in receipts if row.last_receipt_date),
        default=None,
    )

    return CaseReceiptResponse(
        id=receipt.id,
        case_id=receipt.case_id,
        fee_type=receipt.fee_type if len(fee_types) <= 1 else "MIXED",
        currency=receipt.currency if len(currencies) <= 1 else "MIXED",
        receivable_amt=receivable_amt,
        received_amt=received_amt,
        last_receipt_date=last_receipt_date,
        fee_code=receipt.fee_code if len(receipts) == 1 else None,
        year_no=receipt.year_no if len(receipts) == 1 else None,
        is_arrears=receivable_amt > received_amt,
        invoice_no=receipt.invoice_no if len(receipts) == 1 else None,
        is_commissionable=any(row.is_commissionable for row in receipts),
        bills=bill_overview_rows,
    )


@router.post(
    "/case-receipts",
    response_model=CaseReceiptResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create case receipt",
)
def create_case_receipt_endpoint(
    payload: CaseReceiptCreate,
    _perm: None = Depends(require_perm("CaseReceipt.Create")),
    db: Session = Depends(get_db),
) -> CaseReceiptResponse:
    """
    Create a manual case receipt.

    **Auth**: Bearer JWT
    **Permission**: CaseReceipt.Create
    """
    receipt = create_case_receipt(db, payload)
    db.commit()
    return CaseReceiptResponse(
        id=receipt.id,
        case_id=receipt.case_id,
        fee_type=receipt.fee_type,
        currency=receipt.currency,
        receivable_amt=receipt.receivable_amt,
        received_amt=receipt.received_amt,
        last_receipt_date=receipt.last_receipt_date,
        fee_code=receipt.fee_code,
        fee_name=receipt.fee_name,
        year_no=receipt.year_no,
        due_date=receipt.due_date,
        is_arrears=receipt.is_arrears,
        is_prepayment=receipt.is_prepayment,
        is_commissionable=receipt.is_commissionable,
        invoice_no=receipt.invoice_no,
        remark=receipt.remark,
        bills=[],
    )


@router.put(
    "/case-receipts/{receipt_id}",
    response_model=CaseReceiptResponse,
    summary="Update case receipt",
)
def update_case_receipt_endpoint(
    receipt_id: str,
    payload: CaseReceiptUpdate,
    _perm: None = Depends(require_perm("CaseReceipt.Update")),
    db: Session = Depends(get_db),
) -> CaseReceiptResponse:
    """
    Update a case receipt (partial).

    **Auth**: Bearer JWT
    **Permission**: CaseReceipt.Update
    """
    receipt = update_case_receipt(db, receipt_id, payload)
    db.commit()
    return CaseReceiptResponse(
        id=receipt.id,
        case_id=receipt.case_id,
        fee_type=receipt.fee_type,
        currency=receipt.currency,
        receivable_amt=receipt.receivable_amt,
        received_amt=receipt.received_amt,
        last_receipt_date=receipt.last_receipt_date,
        fee_code=receipt.fee_code,
        fee_name=receipt.fee_name,
        year_no=receipt.year_no,
        due_date=receipt.due_date,
        is_arrears=receipt.is_arrears,
        is_prepayment=receipt.is_prepayment,
        is_commissionable=receipt.is_commissionable,
        invoice_no=receipt.invoice_no,
        remark=receipt.remark,
        bills=[],
    )


@router.get(
    "/case-receipts",
    summary="List case receipts",
)
def list_case_receipts_endpoint(
    client_id: str | None = None,
    case_no: str | None = None,
    fee_type: str | None = None,
    is_arrears: bool | None = None,
    is_commissionable: bool | None = None,
    currency: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    page: int = 1,
    page_size: int = 20,
    _perm: None = Depends(require_perm("CaseReceipt.Read")),
    db: Session = Depends(get_db),
) -> dict:
    """
    List case receipts with cross-case filters.

    **Auth**: Bearer JWT
    **Permission**: CaseReceipt.Read
    """
    result = list_case_receipts(
        db,
        client_id=client_id,
        case_no=case_no,
        fee_type=fee_type,
        is_arrears=is_arrears,
        is_commissionable=is_commissionable,
        currency=currency,
        date_from=date_from,
        date_to=date_to,
        page=page,
        page_size=page_size,
    )
    return jsonable_encoder(result)
