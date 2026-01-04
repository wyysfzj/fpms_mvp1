from __future__ import annotations

from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.api.deps import require_perm
from app.common.doc_render.renderer import DocxRenderer
from app.db.session import get_db
from app.models.letter_head import LetterHead
from app.models.system_param import SystemParam
from app.modules.billing.doc_render_bill_context import BillContextBuilder
from app.modules.billing.models import Bill, BillItem, CaseReceipt, Offset, Payment
from app.modules.masterdata.clients.models import Client

router = APIRouter()


@router.get("/bills")
def get_bills(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1),
    _perm: None = Depends(require_perm("Bill.Read")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    query = db.query(Bill)
    total = query.count()
    bills = (
        query.order_by(Bill.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    )
    items = [
        {
            "id": bill.id,
            "bill_no": bill.bill_no,
            "client_id": bill.client_id,
            "currency": bill.currency,
        }
        for bill in bills
    ]
    return {"items": items, "page": page, "page_size": page_size, "total": total}


@router.post("/bills/from-drafts", status_code=status.HTTP_201_CREATED)
def create_bill_from_drafts(
    payload: dict[str, Any],
    _perm: None = Depends(require_perm("Bill.Create")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    client_id = payload.get("client_id")
    if not client_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="client_id is required")

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


@router.get("/bills/{bill_id}/print")
def print_bill(
    bill_id: str,
    _perm: None = Depends(require_perm("Bill.Print")),
    db: Session = Depends(get_db),
) -> Response:
    bill = db.query(Bill).filter(Bill.id == bill_id).first()
    if not bill:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bill not found")

    bill_items = db.query(BillItem).filter(BillItem.bill_id == bill.id).all()
    client = db.query(Client).filter(Client.id == bill.client_id).first()
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")

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
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Bill template not configured"
        )

    context = BillContextBuilder().build(bill, bill_items, client, letter_head)
    renderer = DocxRenderer()
    try:
        docx_bytes = renderer.render_docx_bytes(template_path, context)
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Template file missing",
        ) from exc

    headers = {
        "Content-Disposition": f'attachment; filename="bill_{bill.id}.docx"',
    }
    return Response(
        content=docx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers=headers,
    )


@router.get("/payments")
def get_payments(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1),
    _perm: None = Depends(require_perm("Payment.Read")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
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
        }
        for payment in payments
    ]
    return {"items": items, "page": page, "page_size": page_size, "total": total}


@router.post("/payments", status_code=status.HTTP_201_CREATED)
def create_payment(
    payload: dict[str, Any],
    _perm: None = Depends(require_perm("Payment.Create")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    client_id = payload.get("client_id")
    if not client_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="client_id is required")

    payment = Payment(
        id=str(uuid4()),
        pay_no=payload.get("pay_no"),
        client_id=client_id,
        pay_date=payload.get("pay_date"),
        currency=payload.get("currency") or "CNY",
        amount=payload.get("amount") or 0,
        remark=payload.get("remark"),
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)

    return {
        "id": payment.id,
        "pay_no": payment.pay_no,
        "client_id": payment.client_id,
        "pay_date": payment.pay_date,
        "currency": payment.currency,
        "amount": payment.amount,
    }


@router.get("/payments/{payment_id}")
def get_payment(
    payment_id: str,
    _perm: None = Depends(require_perm("Payment.Read")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")

    return {
        "id": payment.id,
        "pay_no": payment.pay_no,
        "client_id": payment.client_id,
        "pay_date": payment.pay_date,
        "currency": payment.currency,
        "amount": payment.amount,
    }


@router.post("/offsets", status_code=status.HTTP_201_CREATED)
def create_offset(
    payload: dict[str, Any],
    _perm: None = Depends(require_perm("Payment.Create")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    payment_line_id = payload.get("payment_line_id")
    bill_id = payload.get("bill_id")
    if not payment_line_id or not bill_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="payment_line_id and bill_id are required",
        )

    offset = Offset(
        id=str(uuid4()),
        payment_line_id=payment_line_id,
        bill_id=bill_id,
        offset_amt=payload.get("offset_amt") or 0,
        offset_date=payload.get("offset_date"),
        is_reversed=payload.get("is_reversed") or False,
    )
    db.add(offset)
    db.commit()
    db.refresh(offset)

    return {
        "id": offset.id,
        "payment_line_id": offset.payment_line_id,
        "bill_id": offset.bill_id,
        "offset_amt": offset.offset_amt,
        "offset_date": offset.offset_date,
        "is_reversed": offset.is_reversed,
    }


@router.post("/offsets/{offset_id}/reverse", status_code=status.HTTP_201_CREATED)
def reverse_offset(
    offset_id: str,
    _perm: None = Depends(require_perm("Payment.Create")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    offset = db.query(Offset).filter(Offset.id == offset_id).first()
    if not offset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Offset not found")

    offset.is_reversed = True
    db.commit()
    db.refresh(offset)

    return {
        "id": offset.id,
        "payment_line_id": offset.payment_line_id,
        "bill_id": offset.bill_id,
        "offset_amt": offset.offset_amt,
        "offset_date": offset.offset_date,
        "is_reversed": offset.is_reversed,
    }


@router.post("/bills/manual", status_code=status.HTTP_201_CREATED)
def create_manual_bill(
    payload: dict[str, Any],
    _perm: None = Depends(require_perm("Bill.Create")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    client_id = payload.get("client_id")
    if not client_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="client_id is required")

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


@router.get("/bills/{bill_id}")
def get_bill(
    bill_id: str,
    _perm: None = Depends(require_perm("Bill.Read")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    bill = db.query(Bill).filter(Bill.id == bill_id).first()
    if not bill:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bill not found")

    return {
        "id": bill.id,
        "bill_no": bill.bill_no,
        "client_id": bill.client_id,
        "currency": bill.currency,
        "direction": bill.direction,
        "status": bill.status,
    }


@router.get("/cases/{case_id}/receipts")
def get_case_receipt(
    case_id: str,
    _perm: None = Depends(require_perm("CaseReceipt.Read")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    receipt = db.query(CaseReceipt).filter(CaseReceipt.case_id == case_id).first()
    if not receipt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case receipt not found")

    return {
        "id": receipt.id,
        "case_id": receipt.case_id,
        "fee_type": receipt.fee_type,
        "currency": receipt.currency,
        "receivable_amt": receipt.receivable_amt,
        "received_amt": receipt.received_amt,
    }
