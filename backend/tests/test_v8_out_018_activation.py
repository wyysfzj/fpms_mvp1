from __future__ import annotations

import json

from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from app.modules.documents.models import DocTemplate
from app.modules.documents.official_notice_catalog import (
    seed_official_letter_out_form_018_catalog as seed_doc_templates,
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


def test_seed_accumulates_form_018_internal_only_as_its_own_scope(
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
        classified = rows[:18]
        names = [
            "补正答复", "一通意见陈述", "提前公开请求", "实审请求", "主动撤回", "主动放弃",
            "著录项目变更", "复审请求", "主动补正", "恢复权利请求", "复审、无效程序中的意见陈述",
            "复审中的补正", "纸件申请转电子申请请求书", "费用减缓请求书", "改正译文错误请求书",
            "PPH请求", "发明主动修改", "延长期限请求",
        ]
        assert [(row.code, row.name) for row in classified] == [
            (f"OFFICIAL_LETTER_OUT_{index:03d}", name)
            for index, name in enumerate(names, start=1)
        ]
        for index, row in enumerate(classified, start=1):
            assert json.loads(row.input_fields or "{}") == _classified_payload(
                row.name, f"form-{index:03d}"
            )
            assert (row.status_effect, row.status_restore, row.deadline_template_code) == (
                None, None, None
            )
            assert row.fee_draft_type is None and row.need_reply is False
            assert resolve_document_semantics(row).catalog_status == "REFERENCE_ONLY"
        for row in rows[18:]:
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
                        tuple(f"OFFICIAL_LETTER_OUT_{index:03d}" for index in range(1, 19))
                    )
                )
                .order_by(DocTemplate.code.asc())
            )
            .scalars()
            .all()
        )
        assert tuple(row.input_fields for row in rerun) == first_payloads
