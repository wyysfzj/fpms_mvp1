from __future__ import annotations

import json

from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from app.modules.documents.models import DocTemplate
from app.modules.templates.models import FormatLetterMapping, Template
from scripts.seed_dev import seed_doc_templates


def test_seed_doc_templates_imports_official_letter_out_catalog(
    session_factory: sessionmaker,
) -> None:
    """客户"致函官方文件清单"22 行（相关流程操作 P0102 TABLE 002）作为 OUT 目录。"""
    with session_factory() as db:
        seed_doc_templates(db)

        rows = (
            db.execute(
                select(DocTemplate)
                .where(DocTemplate.code.like("OFFICIAL_LETTER_OUT_%"))
                .order_by(DocTemplate.code.asc())
            )
            .scalars()
            .all()
        )

        assert len(rows) == 22
        assert all(row.direction == "OUT" for row in rows)
        assert all(row.enabled for row in rows)

        names = {row.name for row in rows}
        assert "补正答复" in names
        assert "一通意见陈述" in names
        assert "复审请求" in names
        assert "费用减缓请求书" in names
        assert "办理文件副本请求书" in names

        first = next(row for row in rows if row.code == "OFFICIAL_LETTER_OUT_001")
        payload = json.loads(first.input_fields or "{}")
        assert payload["catalog_kind"] == "OFFICIAL_LETTER_OUT"
        assert payload["official_letter_name"] == "补正答复"

        # idempotent rerun
        seed_doc_templates(db)
        recount = (
            db.execute(
                select(DocTemplate).where(DocTemplate.code.like("OFFICIAL_LETTER_OUT_%"))
            )
            .scalars()
            .all()
        )
        assert len(recount) == 22


def test_seed_format_letter_mappings_installs_customer_table(
    session_factory: sessionmaker,
) -> None:
    """客户 8 行"官文→格式函"映射（信函生成操作 P0007 TABLE 001）落库并可重复执行。"""
    with session_factory() as db:
        seed_doc_templates(db)

        mappings = (
            db.execute(
                select(FormatLetterMapping).where(
                    FormatLetterMapping.format_letter_template_code.like("FORMAT_LETTER_%")
                )
            )
            .scalars()
            .all()
        )
        assert len(mappings) == 8
        by_pattern = {m.official_doc_name_pattern: m for m in mappings}
        assert set(by_pattern) == {
            "驳回决定",
            "初步审查合格",
            "公布通知书",
            "进入实审通知",
            "受理通知-电子",
            "授权通知书-电子",
            "第一次审查意见通知书",
            "专利证书",
        }
        # 客户命名规则：{案号}-给{申请人名称}的邮件.docx
        assert all(
            m.output_name_rule == "{case_no}-给{applicant_name}的邮件.docx" for m in mappings
        )
        assert all(m.enabled for m in mappings)

        # every mapping points at a real enabled Template row
        template_ids = {m.format_letter_template_id for m in mappings}
        templates = (
            db.execute(select(Template).where(Template.id.in_(template_ids))).scalars().all()
        )
        assert len(templates) == 8
        assert all(t.group == "FORMAT_LETTER" and t.enabled for t in templates)

        # idempotent rerun does not duplicate
        seed_doc_templates(db)
        recount = (
            db.execute(
                select(FormatLetterMapping).where(
                    FormatLetterMapping.format_letter_template_code.like("FORMAT_LETTER_%")
                )
            )
            .scalars()
            .all()
        )
        assert len(recount) == 8
