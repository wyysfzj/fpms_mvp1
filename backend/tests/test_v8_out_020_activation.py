from __future__ import annotations

import json

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.modules.documents.models import DocTemplate
from app.modules.documents.official_notice_catalog import (
    seed_official_letter_out_form_020_catalog as seed_doc_templates,
)
from app.modules.documents.semantics import resolve_document_semantics

DECISION_SOURCE = "docs/product/v8/customer-decisions/2026-08-10-v8-full-batch-scheme-a.txt"
DECISION_VERSION = "customer-decision:2026-08-10:v8-full-batch-scheme-a:v1"
DECISION_SHA256 = "e6cfd648f1d366e27bde3f74310f00033a6db60ce55d850d2e668764745faace"
CATALOG_SOURCE = "相关流程操作-20260526.docx [P0102] TABLE 002"


def _rows(transaction: Session) -> list[DocTemplate]:
    return (
        transaction.execute(
            select(DocTemplate)
            .where(DocTemplate.code.like("OFFICIAL_LETTER_OUT_%"))
            .order_by(DocTemplate.code.asc())
        )
        .scalars()
        .all()
    )


def test_seed_classifies_only_form_020_as_internal_reference_material(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        seed_doc_templates(transaction)
        transaction.flush()
        rows = _rows(transaction)
        assert len(rows) == 22

        for index, item in enumerate(rows[:20], start=1):
            payload = json.loads(item.input_fields or "{}")
            assert payload["legacy_form_scope"] == f"form-{index:03d}"
            assert payload["legacy_form_classification"] == "INTERNAL_ONLY"
            assert payload["catalog_status"] == "REFERENCE_ONLY"

        row = rows[19]
        assert (row.code, row.name) == ("OFFICIAL_LETTER_OUT_020", "三通意见陈述")
        assert json.loads(row.input_fields or "{}") == {
            "catalog_kind": "OFFICIAL_LETTER_OUT",
            "catalog_status": "REFERENCE_ONLY",
            "decision_source": DECISION_SOURCE,
            "decision_source_sha256": DECISION_SHA256,
            "decision_version": DECISION_VERSION,
            "legacy_form_classification": "INTERNAL_ONLY",
            "legacy_form_scope": "form-020",
            "official_letter_name": "三通意见陈述",
            "source": CATALOG_SOURCE,
        }
        assert (row.status_effect, row.status_restore, row.deadline_template_code) == (
            None,
            None,
            None,
        )
        assert row.fee_draft_type is None and row.need_reply is False
        assert resolve_document_semantics(row).catalog_status == "REFERENCE_ONLY"

        for later in rows[20:]:
            assert json.loads(later.input_fields or "{}") == {
                "catalog_kind": "OFFICIAL_LETTER_OUT",
                "official_letter_name": later.name,
                "source": CATALOG_SOURCE,
            }

        before = tuple(item.input_fields for item in rows)
        seed_doc_templates(transaction)
        transaction.flush()
        assert tuple(item.input_fields for item in _rows(transaction)) == before
