from __future__ import annotations

from typing import Any


class BillContextBuilder:
    def build(self, bill: Any, bill_items: list[Any], client: Any, letter_head: Any) -> dict:
        return {
            "bill": {
                "id": getattr(bill, "id", None),
                "bill_no": getattr(bill, "bill_no", None),
                "bill_date": getattr(bill, "bill_date", None),
                "due_date": getattr(bill, "due_date", None),
                "status": getattr(bill, "status", None),
                "currency": getattr(bill, "currency", None),
                "direction": getattr(bill, "direction", None),
                "total_gov": getattr(bill, "total_gov", None),
                "total_service": getattr(bill, "total_service", None),
                "total_misc": getattr(bill, "total_misc", None),
                "amount": getattr(bill, "amount", None),
                "balance": getattr(bill, "balance", None),
            },
            "client": {
                "id": getattr(client, "id", None),
                "client_code": getattr(client, "client_code", None),
                "name_cn": getattr(client, "name_cn", None),
                "name_en": getattr(client, "name_en", None),
                "client_type": getattr(client, "client_type", None),
            },
            "items": [
                {
                    "id": getattr(item, "id", None),
                    "case_id": getattr(item, "case_id", None),
                    "fee_code": getattr(item, "fee_code", None),
                    "fee_name": getattr(item, "fee_name", None),
                    "fee_type": getattr(item, "fee_type", None),
                    "year_no": getattr(item, "year_no", None),
                    "amount": getattr(item, "amount", None),
                }
                for item in bill_items
            ],
            "letter_head": None
            if letter_head is None
            else {
                "id": getattr(letter_head, "id", None),
                "name": getattr(letter_head, "name", None),
                "locale": getattr(letter_head, "locale", None),
                "logo_file_path": getattr(letter_head, "logo_file_path", None),
                "header_text": getattr(letter_head, "header_text", None),
                "footer_text": getattr(letter_head, "footer_text", None),
                "address_block": getattr(letter_head, "address_block", None),
                "phone": getattr(letter_head, "phone", None),
                "email": getattr(letter_head, "email", None),
                "website": getattr(letter_head, "website", None),
            },
        }
