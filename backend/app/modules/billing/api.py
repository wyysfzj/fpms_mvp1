from __future__ import annotations

from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.api.deps import require_perm
from app.common.doc_render.renderer import DocxRenderer
from app.core.errors import raise_business_error
from app.db.session import get_db
from app.models.letter_head import LetterHead
from app.models.system_param import SystemParam
from app.modules.billing.doc_render_bill_context import BillContextBuilder
from app.modules.billing.models import Bill, BillItem, CaseReceipt, Payment, PaymentLine
from app.modules.billing.schemas import (
    BillFromDraftsRequest,
    BillResponse,
    OffsetCreateSchema,
    OffsetResponse,
    PaymentResponse,
    PaymentSchema,
)
from app.modules.billing.service import (
    create_offset as create_offset_service,
)
from app.modules.billing.service import (
    generate_bill_from_drafts,
    process_payment,
)
from app.modules.billing.service import (
    reverse_offset as reverse_offset_service,
)
from app.modules.masterdata.clients.models import Client

router = APIRouter()


@router.get("/bills", summary="List bills")
def get_bills(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    _perm: None = Depends(require_perm("Bill.Read")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
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
    query = db.query(Bill)
    total = query.count()
    bills = (
        query.order_by(Bill.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    )

    # Batch-resolve client names for all bills in this page
    client_ids = {bill.client_id for bill in bills if bill.client_id}
    client_name_map: dict[str, str] = {}
    if client_ids:
        clients = db.query(Client.id, Client.name_cn).filter(Client.id.in_(client_ids)).all()
        client_name_map = {c.id: c.name_cn for c in clients}

    items = [
        {
            "id": bill.id,
            "bill_no": bill.bill_no,
            "client_id": bill.client_id,
            "client_name": client_name_map.get(bill.client_id),
            "currency": bill.currency,
            "status": bill.status,
            "amount": bill.amount,
            "balance": bill.balance,
            "bill_date": bill.bill_date,
            "due_date": bill.due_date,
        }
        for bill in bills
    ]
    return {"items": items, "page": page, "page_size": page_size, "total": total}


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


@router.get("/payments", summary="List payments")
def get_payments(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    _perm: None = Depends(require_perm("Payment.Read")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
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
    query = db.query(Payment)
    total = query.count()
    payments = (
        query.order_by(Payment.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    items = [
        {
            "id": payment.id,
            "pay_no": payment.pay_no,
            "client_id": payment.client_id,
            "pay_date": payment.pay_date,
            "currency": payment.currency,
            "amount": payment.amount,
        }
        for payment in payments
    ]
    return {"items": items, "page": page, "page_size": page_size, "total": total}


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
    payload: dict[str, Any],
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
    client_id = payload.get("client_id")
    if not client_id:
        raise_business_error(
            "BILL_INVALID",
            "client_id is required",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    bill = Bill(
        id=str(uuid4()),
        bill_no=payload.get("bill_no"),
        client_id=client_id,
        currency=payload.get("currency") or "CNY",
        direction=payload.get("direction") or "AR",
        status=payload.get("status") or "UNSETTLED",
    )
    db.add(bill)
    db.commit()
    db.refresh(bill)

    return {
        "id": bill.id,
        "bill_no": bill.bill_no,
        "client_id": bill.client_id,
        "currency": bill.currency,
        "direction": bill.direction,
        "status": bill.status,
    }


@router.get("/bills/{bill_id}", summary="Get a bill")
def get_bill(
    bill_id: str,
    _perm: None = Depends(require_perm("Bill.Read")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
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
    bill = db.query(Bill).filter(Bill.id == bill_id).first()
    if not bill:
        raise_business_error(
            "BILL_NOT_FOUND",
            "Bill not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    return {
        "id": bill.id,
        "bill_no": bill.bill_no,
        "client_id": bill.client_id,
        "currency": bill.currency,
        "direction": bill.direction,
        "status": bill.status,
    }


@router.get("/cases/{case_id}/receipts", summary="Get case receipt")
def get_case_receipt(
    case_id: str,
    _perm: None = Depends(require_perm("CaseReceipt.Read")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
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
    receipt = db.query(CaseReceipt).filter(CaseReceipt.case_id == case_id).first()
    if not receipt:
        raise_business_error(
            "CASE_RECEIPT_NOT_FOUND",
            "Case receipt not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    return {
        "id": receipt.id,
        "case_id": receipt.case_id,
        "fee_type": receipt.fee_type,
        "currency": receipt.currency,
        "receivable_amt": receipt.receivable_amt,
        "received_amt": receipt.received_amt,
        "last_receipt_date": receipt.last_receipt_date,
        "fee_code": receipt.fee_code,
        "year_no": receipt.year_no,
        "is_arrears": receipt.is_arrears,
        "invoice_no": receipt.invoice_no,
        "is_commissionable": receipt.is_commissionable,
    }
