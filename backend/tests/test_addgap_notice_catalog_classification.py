from __future__ import annotations

import json
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from app.modules.documents.models import DocTemplate
from app.modules.documents.official_notice_catalog import (
    OFFICIAL_NOTICE_CATALOG,
    OFFICIAL_NOTICE_CATALOG_SOURCE,
    seed_official_notice_catalog,
)


def test_all_official_notice_catalog_rows_are_reference_only_without_effects(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as db:
        assert seed_official_notice_catalog(db) == 60
        db.commit()

        rows = (
            db.execute(
                select(DocTemplate)
                .where(DocTemplate.code.like("OFFICIAL_NOTICE_%"))
                .order_by(DocTemplate.code.asc())
            )
            .scalars()
            .all()
        )

        assert len(rows) == len(OFFICIAL_NOTICE_CATALOG) == 60
        for index, (row, (name, code_text)) in enumerate(
            zip(rows, OFFICIAL_NOTICE_CATALOG, strict=True), start=1
        ):
            assert row.code == f"OFFICIAL_NOTICE_{index:03d}"
            assert row.name == name
            assert row.direction == "IN"
            assert row.enabled is True
            assert row.status_effect is None
            assert row.status_restore is None
            assert row.deadline_template_code is None
            assert row.fee_draft_type is None
            assert row.fee_item_list is None
            assert row.need_reply is False
            assert row.reply_to_template_code is None

            metadata = json.loads(row.input_fields or "{}")
            assert metadata == {
                "archive_status_restore": None,
                "canonical_template_code": None,
                "catalog_kind": "OFFICIAL_NOTICE",
                "catalog_status": "REFERENCE_ONLY",
                "completion_event": None,
                "deadline_source_policy": None,
                "execution_behavior": None,
                "official_doc_code_text": code_text,
                "official_doc_codes": [
                    code for code in code_text.replace(";", ",").split(",") if code
                ],
                "official_notice_name": name,
                "source": OFFICIAL_NOTICE_CATALOG_SOURCE,
            }

        assert seed_official_notice_catalog(db) == 0


def test_seed_repairs_every_reference_only_field_on_an_existing_catalog_row(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as db:
        existing = DocTemplate(
            id=str(uuid4()),
            code="OFFICIAL_NOTICE_001",
            name="旧名称",
            direction="OUT",
            enabled=False,
            status_effect="OA1",
            status_restore="SUB_EXAM",
            deadline_template_code="OA_REPLY",
            fee_draft_type="GRANT_FEE",
            fee_item_list='["申请费"]',
            need_reply=True,
            reply_to_template_code="OA_OUT",
            input_fields='{"catalog_kind":"OFFICIAL_NOTICE","catalog_status":"EXECUTABLE"}',
        )
        db.add(existing)
        db.commit()

        assert seed_official_notice_catalog(db) == 60
        db.commit()
        db.refresh(existing)

        assert existing.name == "受理通知-电子"
        assert existing.direction == "IN"
        assert existing.enabled is True
        assert existing.status_effect is None
        assert existing.status_restore is None
        assert existing.deadline_template_code is None
        assert existing.fee_draft_type is None
        assert existing.fee_item_list is None
        assert existing.need_reply is False
        assert existing.reply_to_template_code is None
        assert json.loads(existing.input_fields or "{}")["catalog_status"] == "REFERENCE_ONLY"
        assert seed_official_notice_catalog(db) == 0
