from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any


class BillContextBuilder:
    def build(self, bill, bill_items, client, letter_head) -> dict:
        return {
            "bill": self._build_bill(bill),
            "client": self._build_client(client),
            "items": [self._build_item(item) for item in bill_items],
            "letter_head": self._build_letter_head(letter_head) if letter_head else None,
        }

    def _build_bill(self, bill) -> dict:
        return {
            "id": bill.id,
            "bill_no": bill.bill_no,
            "bill_date": self._serialize_value(bill.bill_date),
            "due_date": self._serialize_value(bill.due_date),
            "status": bill.status,
            "currency": bill.currency,
            "direction": bill.direction,
            "total_gov": self._serialize_value(bill.total_gov),
            "total_service": self._serialize_value(bill.total_service),
            "total_misc": self._serialize_value(bill.total_misc),
            "amount": self._serialize_value(bill.amount),
            "balance": self._serialize_value(bill.balance),
        }

    def _build_client(self, client) -> dict:
        return {
            "id": client.id,
            "client_code": client.client_code,
            "name_cn": client.name_cn,
            "name_en": client.name_en,
            "client_type": client.client_type,
            "default_currency": client.default_currency,
        }

    def _build_item(self, item) -> dict:
        return {
            "id": item.id,
            "description": item.fee_name or item.fee_code,
            "qty": self._serialize_value(getattr(item, "quantity", None)),
            "unit_price": self._serialize_value(getattr(item, "unit_price", None)),
            "amount": self._serialize_value(item.amount),
            "fee_code": item.fee_code,
            "fee_name": item.fee_name,
            "fee_type": item.fee_type,
            "year_no": item.year_no,
            "case_id": item.case_id,
        }

    def _build_letter_head(self, letter_head) -> dict:
        return {
            "id": letter_head.id,
            "name": letter_head.name,
            "locale": letter_head.locale,
            "logo_file_path": letter_head.logo_file_path,
            "header_text": letter_head.header_text,
            "footer_text": letter_head.footer_text,
            "address_block": letter_head.address_block,
            "phone": letter_head.phone,
            "email": letter_head.email,
            "website": letter_head.website,
            "is_default": letter_head.is_default,
            "created_at": self._serialize_value(letter_head.created_at),
            "updated_at": self._serialize_value(letter_head.updated_at),
        }

    def _serialize_value(self, value: Any) -> Any:
        if isinstance(value, (datetime, date)):
            return value.isoformat()
        if isinstance(value, Decimal):
            return float(value)
        return value
