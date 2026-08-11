from __future__ import annotations

import json

from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from app.modules.documents.models import DocTemplate
from app.modules.documents.semantics import resolve_document_semantics
from scripts.seed_dev import seed_doc_templates

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


def test_seed_accumulates_form_013_internal_only_as_its_own_scope(
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
        classified = rows[:13]
        assert [(row.code, row.name) for row in classified] == [
            ("OFFICIAL_LETTER_OUT_001", "补正答复"),
            ("OFFICIAL_LETTER_OUT_002", "一通意见陈述"),
            ("OFFICIAL_LETTER_OUT_003", "提前公开请求"),
            ("OFFICIAL_LETTER_OUT_004", "实审请求"),
            ("OFFICIAL_LETTER_OUT_005", "主动撤回"),
            ("OFFICIAL_LETTER_OUT_006", "主动放弃"),
            ("OFFICIAL_LETTER_OUT_007", "著录项目变更"),
            ("OFFICIAL_LETTER_OUT_008", "复审请求"),
            ("OFFICIAL_LETTER_OUT_009", "主动补正"),
            ("OFFICIAL_LETTER_OUT_010", "恢复权利请求"),
            ("OFFICIAL_LETTER_OUT_011", "复审、无效程序中的意见陈述"),
            ("OFFICIAL_LETTER_OUT_012", "复审中的补正"),
            ("OFFICIAL_LETTER_OUT_013", "纸件申请转电子申请请求书"),
        ]
        for index, row in enumerate(classified, start=1):
            assert json.loads(row.input_fields or "{}") == _classified_payload(
                row.name,
                f"form-{index:03d}",
            )
            assert row.status_effect is None
            assert row.status_restore is None
            assert row.deadline_template_code is None
            assert row.fee_draft_type is None
            assert row.need_reply is False
            assert resolve_document_semantics(row).catalog_status == "REFERENCE_ONLY"

        for row in rows[13:]:
            assert json.loads(row.input_fields or "{}") == {
                "catalog_kind": "OFFICIAL_LETTER_OUT",
                "official_letter_name": row.name,
                "source": CATALOG_SOURCE,
            }

        first_payloads = tuple(row.input_fields for row in classified)
        seed_doc_templates(transaction)
        rerun = (
            transaction.execute(
                select(DocTemplate)
                .where(
                    DocTemplate.code.in_(
                        tuple(f"OFFICIAL_LETTER_OUT_{index:03d}" for index in range(1, 14))
                    )
                )
                .order_by(DocTemplate.code.asc())
            )
            .scalars()
            .all()
        )
        assert tuple(row.input_fields for row in rerun) == first_payloads
