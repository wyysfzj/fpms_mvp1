from __future__ import annotations

import json

from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from app.modules.documents.models import DocTemplate
from app.modules.documents.official_notice_catalog import (
    seed_official_letter_out_form_007_catalog as seed_doc_templates,
)
from app.modules.documents.semantics import resolve_document_semantics

DECISION_SOURCE = "docs/product/v8/customer-decisions/2026-08-10-v8-full-batch-scheme-a.txt"
DECISION_VERSION = "customer-decision:2026-08-10:v8-full-batch-scheme-a:v1"
DECISION_SHA256 = "e6cfd648f1d366e27bde3f74310f00033a6db60ce55d850d2e668764745faace"
CATALOG_SOURCE = "相关流程操作-20260526.docx [P0102] TABLE 002"


def _classified_payload(name: str, scope: str) -> dict[str, object]:
    return {
        "catalog_kind": "OFFICIAL_LETTER_OUT",
        "catalog_status": "REFERENCE_ONLY",
        "decision_source": DECISION_SOURCE,
        "decision_source_sha256": DECISION_SHA256,
        "decision_version": DECISION_VERSION,
        "legacy_form_classification": "INTERNAL_ONLY",
        "legacy_form_scope": scope,
        "official_letter_name": name,
        "source": CATALOG_SOURCE,
    }


def test_seed_accumulates_form_007_internal_only_after_forms_001_through_006(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        seed_doc_templates(transaction)
        transaction.flush()

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
        classified = rows[:7]
        assert [(row.code, row.name) for row in classified] == [
            ("OFFICIAL_LETTER_OUT_001", "补正答复"),
            ("OFFICIAL_LETTER_OUT_002", "一通意见陈述"),
            ("OFFICIAL_LETTER_OUT_003", "提前公开请求"),
            ("OFFICIAL_LETTER_OUT_004", "实审请求"),
            ("OFFICIAL_LETTER_OUT_005", "主动撤回"),
            ("OFFICIAL_LETTER_OUT_006", "主动放弃"),
            ("OFFICIAL_LETTER_OUT_007", "著录项目变更"),
        ]
        for row, scope in zip(
            classified,
            (
                "form-001",
                "form-002",
                "form-003",
                "form-004",
                "form-005",
                "form-006",
                "form-007",
            ),
            strict=True,
        ):
            assert json.loads(row.input_fields or "{}") == _classified_payload(
                row.name,
                scope,
            )
            assert row.status_effect is None
            assert row.status_restore is None
            assert row.deadline_template_code is None
            assert row.fee_draft_type is None
            assert row.need_reply is False
            assert resolve_document_semantics(row).catalog_status == "REFERENCE_ONLY"

        for row in rows[7:]:
            assert json.loads(row.input_fields or "{}") == {
                "catalog_kind": "OFFICIAL_LETTER_OUT",
                "official_letter_name": row.name,
                "source": CATALOG_SOURCE,
            }

        first_payloads = tuple(row.input_fields for row in classified)
        seed_doc_templates(transaction)
        transaction.flush()
        rerun = (
            transaction.execute(
                select(DocTemplate)
                .where(
                    DocTemplate.code.in_(
                        (
                            "OFFICIAL_LETTER_OUT_001",
                            "OFFICIAL_LETTER_OUT_002",
                            "OFFICIAL_LETTER_OUT_003",
                            "OFFICIAL_LETTER_OUT_004",
                            "OFFICIAL_LETTER_OUT_005",
                            "OFFICIAL_LETTER_OUT_006",
                            "OFFICIAL_LETTER_OUT_007",
                        )
                    )
                )
                .order_by(DocTemplate.code.asc())
            )
            .scalars()
            .all()
        )
        assert tuple(row.input_fields for row in rerun) == first_payloads
