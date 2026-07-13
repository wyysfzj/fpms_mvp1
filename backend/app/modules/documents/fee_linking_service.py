"""B3: Auto-create FeeDraft when document registered with fee-enabled template."""

from __future__ import annotations

import json
import logging
from decimal import Decimal
from uuid import uuid4

from sqlalchemy.orm import Session

from app.core.errors import raise_business_error
from app.modules.cases.models import Case
from app.modules.documents.models import DocTemplate, Document
from app.modules.documents.schemas import DocumentWizardFeeFinalRowIn
from app.modules.documents.semantics import resolve_document_semantics
from app.modules.fees.models import FeeDraft, FeeItem

logger = logging.getLogger(__name__)


def _to_decimal(value) -> Decimal | None:
    if value is None:
        return None
    try:
        return Decimal(str(value))
    except (TypeError, ValueError, ArithmeticError):
        return None


def parse_fee_item_list_candidates(
    raw_json: str | None, template_code: str
) -> list[dict[str, object]]:
    """Parse fee_item_list JSON into preview-safe candidate dicts."""
    if not raw_json:
        return []

    try:
        items = json.loads(raw_json)
    except (json.JSONDecodeError, TypeError) as exc:
        logger.warning("B3: Malformed fee_item_list JSON in template %s: %s", template_code, exc)
        return []

    if not isinstance(items, list):
        logger.warning("B3: fee_item_list in template %s is not a list", template_code)
        return []

    candidates: list[dict[str, object]] = []
    for item_data in items:
        if not isinstance(item_data, dict):
            continue
        amount = _to_decimal(item_data.get("amount"))
        if amount is None:
            amount = Decimal("0")
        candidates.append(
            {
                "fee_code": item_data.get("code") or item_data.get("fee_code"),
                "fee_name": item_data.get("name") or item_data.get("fee_name"),
                "fee_type": item_data.get("fee_type", "SERVICE"),
                "quantity": _to_decimal(item_data.get("quantity")),
                "unit_price": _to_decimal(item_data.get("unit_price")),
                "amount": amount,
                "remark": item_data.get("remark")
                or item_data.get("description")
                or item_data.get("label"),
            }
        )
    return candidates


def maybe_create_fee_draft(
    db: Session,
    document: Document,
    template: DocTemplate,
) -> FeeDraft | None:
    """Auto-create a FeeDraft if template has fee_draft_type configured.

    Returns created FeeDraft, or None if no draft was needed.
    Does NOT commit — caller is responsible for db.commit().
    """
    fee_draft_type = getattr(template, "fee_draft_type", None)
    if not fee_draft_type:
        return None
    semantics = resolve_document_semantics(template)
    if str(getattr(template, "code", "")).strip().upper() == "GRANT_NOTICE" or (
        semantics.catalog_status == "EXECUTABLE"
        and semantics.execution_behavior == "GRANT_NOTICE"
        and semantics.fee_trigger == "GRANT_FEE"
    ):
        return None

    # Load case to get client_id
    case = db.get(Case, document.case_id)
    if not case:
        logger.warning(
            "B3: Case %s not found for document %s, skipping fee draft",
            document.case_id,
            document.id,
        )
        return None

    draft = FeeDraft(
        id=str(uuid4()),
        case_id=document.case_id,
        client_id=case.client_id,
        draft_type=fee_draft_type,
        currency="CNY",
        status="OPEN",
        total_gov=Decimal("0"),
        total_service=Decimal("0"),
        total_misc=Decimal("0"),
        amount=Decimal("0"),
    )
    db.add(draft)

    fee_item_list_raw = getattr(template, "fee_item_list", None)
    if fee_item_list_raw:
        _create_fee_items_from_candidates(
            db,
            draft,
            document,
            parse_fee_item_list_candidates(fee_item_list_raw, template.code),
        )

    return draft


def create_fee_draft_from_wizard_row(
    db: Session,
    document: Document,
    fee_row: DocumentWizardFeeFinalRowIn,
) -> FeeDraft | None:
    """Create a FeeDraft from explicit wizard fee row values."""
    if fee_row.skip_this_candidate:
        return None

    case = db.get(Case, document.case_id)
    if not case:
        logger.warning(
            "B3: Case %s not found for document %s, skipping explicit fee draft",
            document.case_id,
            document.id,
        )
        return None

    draft_type = str(fee_row.fee_draft_type).strip()
    if not draft_type:
        raise_business_error(
            "DOCUMENT_WIZARD_BATCH_INVALID",
            "Document wizard batch contains invalid fee rows",
            details={
                "row_errors": [
                    {
                        "row_index": fee_row.row_index,
                        "field": "fee_draft_type",
                        "code": "FEE_DRAFT_TYPE_REQUIRED",
                        "message": "fee_draft_type is required",
                    }
                ]
            },
            status_code=400,
        )

    draft = FeeDraft(
        id=str(uuid4()),
        case_id=document.case_id,
        client_id=case.client_id,
        draft_type=draft_type,
        currency="CNY",
        status="OPEN",
        total_gov=Decimal("0"),
        total_service=Decimal("0"),
        total_misc=Decimal("0"),
        amount=Decimal("0"),
    )
    db.add(draft)
    _create_fee_items_from_wizard_row(db, draft, document, fee_row)
    return draft


def _create_fee_items_from_candidates(
    db: Session,
    draft: FeeDraft,
    document: Document,
    candidates: list[dict[str, object]],
) -> None:
    """Create FeeItem rows from parsed candidates."""
    total_gov = Decimal("0")
    total_service = Decimal("0")
    total_misc = Decimal("0")
    total_amount = Decimal("0")

    for item_data in candidates:
        fee_type = str(item_data.get("fee_type") or "SERVICE").upper()
        amount = item_data.get("amount", Decimal("0"))
        if not isinstance(amount, Decimal):
            amount = _to_decimal(amount) or Decimal("0")
        total_amount += amount
        if fee_type == "GOV":
            total_gov += amount
        elif fee_type == "SERVICE":
            total_service += amount
        else:
            total_misc += amount

        fee_item = FeeItem(
            id=str(uuid4()),
            draft_id=draft.id,
            case_id=document.case_id,
            fee_code=item_data.get("fee_code"),
            fee_name=item_data.get("fee_name"),
            fee_type=fee_type,
            quantity=item_data.get("quantity"),
            unit_price=item_data.get("unit_price"),
            amount=amount,
        )
        db.add(fee_item)

    draft.total_gov = total_gov
    draft.total_service = total_service
    draft.total_misc = total_misc
    draft.amount = total_amount


def _create_fee_items_from_wizard_row(
    db: Session,
    draft: FeeDraft,
    document: Document,
    fee_row: DocumentWizardFeeFinalRowIn,
) -> None:
    total_gov = Decimal("0")
    total_service = Decimal("0")
    total_misc = Decimal("0")
    total_amount = Decimal("0")

    for item_data in fee_row.fee_items:
        fee_type = (item_data.fee_type or "SERVICE").upper()
        amount = item_data.amount or Decimal("0")
        total_amount += amount
        if fee_type == "GOV":
            total_gov += amount
        elif fee_type == "SERVICE":
            total_service += amount
        else:
            total_misc += amount

        fee_item = FeeItem(
            id=str(uuid4()),
            draft_id=draft.id,
            case_id=document.case_id,
            fee_code=item_data.fee_code,
            fee_name=item_data.fee_name,
            fee_type=item_data.fee_type or "SERVICE",
            quantity=item_data.quantity,
            unit_price=item_data.unit_price,
            amount=amount,
            remark=item_data.remark,
        )
        db.add(fee_item)

    draft.total_gov = total_gov
    draft.total_service = total_service
    draft.total_misc = total_misc
    draft.amount = total_amount
