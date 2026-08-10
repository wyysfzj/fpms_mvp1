from __future__ import annotations

import json

from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from app.modules.documents.models import DocTemplate
from app.modules.documents.semantics import resolve_document_semantics
from scripts.seed_dev import seed_doc_templates

FORM_001_DECISION_SOURCE = (
    "docs/product/v8/customer-decisions/2026-08-10-v8-full-batch-scheme-a.txt"
)
FORM_001_DECISION_VERSION = "customer-decision:2026-08-10:v8-full-batch-scheme-a:v1"
FORM_001_DECISION_SHA256 = "e6cfd648f1d366e27bde3f74310f00033a6db60ce55d850d2e668764745faace"


def test_seed_applies_only_form_001_internal_only_classification(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        seed_doc_templates(transaction)

        rows = (
            transaction.execute(
                select(DocTemplate)
                .where(DocTemplate.code.like("OFFICIAL_LETTER_OUT_%"))
                .order_by(DocTemplate.code.asc())
            )
            .scalars()
            .all()
        )

        assert len(rows) == 22
        form_001 = rows[0]
        assert form_001.code == "OFFICIAL_LETTER_OUT_001"
        assert form_001.name == "补正答复"
        assert json.loads(form_001.input_fields or "{}") == {
            "catalog_kind": "OFFICIAL_LETTER_OUT",
            "catalog_status": "REFERENCE_ONLY",
            "decision_source": FORM_001_DECISION_SOURCE,
            "decision_source_sha256": FORM_001_DECISION_SHA256,
            "decision_version": FORM_001_DECISION_VERSION,
            "legacy_form_classification": "INTERNAL_ONLY",
            "legacy_form_scope": "form-001",
            "official_letter_name": "补正答复",
            "source": "相关流程操作-20260526.docx [P0102] TABLE 002",
        }
        assert form_001.status_effect is None
        assert form_001.status_restore is None
        assert form_001.deadline_template_code is None
        assert form_001.fee_draft_type is None
        assert form_001.need_reply is False
        assert resolve_document_semantics(form_001).catalog_status == "REFERENCE_ONLY"

        for row in rows[1:]:
            assert json.loads(row.input_fields or "{}") == {
                "catalog_kind": "OFFICIAL_LETTER_OUT",
                "official_letter_name": row.name,
                "source": "相关流程操作-20260526.docx [P0102] TABLE 002",
            }

        first_payload = form_001.input_fields
        seed_doc_templates(transaction)
        rerun = transaction.execute(
            select(DocTemplate).where(DocTemplate.code == "OFFICIAL_LETTER_OUT_001")
        ).scalar_one()
        assert rerun.input_fields == first_payload
