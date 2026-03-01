"""B3: Auto-create FeeDraft when document registered with fee-enabled template."""

from __future__ import annotations

import json
import logging
from decimal import Decimal
from uuid import uuid4

from sqlalchemy.orm import Session

from app.modules.cases.models import Case
from app.modules.documents.models import DocTemplate, Document
from app.modules.fees.models import FeeDraft, FeeItem

logger = logging.getLogger(__name__)


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

    # Parse fee_item_list if present
    fee_item_list_raw = getattr(template, "fee_item_list", None)
    if fee_item_list_raw:
        _parse_and_create_fee_items(db, draft, document, fee_item_list_raw, template.code)

    return draft


def _parse_and_create_fee_items(
    db: Session,
    draft: FeeDraft,
    document: Document,
    raw_json: str,
    template_code: str,
) -> None:
    """Parse fee_item_list JSON and create FeeItem rows. Logs warning on malformed data."""
    try:
        items = json.loads(raw_json)
    except (json.JSONDecodeError, TypeError) as exc:
        logger.warning("B3: Malformed fee_item_list JSON in template %s: %s", template_code, exc)
        return

    if not isinstance(items, list):
        logger.warning("B3: fee_item_list in template %s is not a list", template_code)
        return

    for item_data in items:
        if not isinstance(item_data, dict):
            continue
        fee_item = FeeItem(
            id=str(uuid4()),
            draft_id=draft.id,
            case_id=document.case_id,
            fee_code=item_data.get("code") or item_data.get("fee_code"),
            fee_name=item_data.get("name") or item_data.get("fee_name"),
            fee_type=item_data.get("fee_type", "SERVICE"),
            quantity=Decimal(str(item_data["quantity"]))
            if item_data.get("quantity") is not None
            else None,
            unit_price=Decimal(str(item_data["unit_price"]))
            if item_data.get("unit_price") is not None
            else None,
            amount=Decimal(str(item_data.get("amount", 0))),
        )
        db.add(fee_item)
