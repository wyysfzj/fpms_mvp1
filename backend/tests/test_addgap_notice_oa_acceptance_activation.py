from __future__ import annotations

import json

from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

import scripts.seed_dev as seed_dev
from app.modules.documents import official_notice_catalog as notice_catalog
from app.modules.documents.models import DocTemplate

APPROVED_ACTIVATIONS = {
    "OFFICIAL_NOTICE_001": ("ACCEPTANCE_NOTICE", "ACCEPTANCE_NOTICE", "ACCEPTED", None, False),
    "OFFICIAL_NOTICE_003": ("OA_REPLY", "OA_IN", "OA1", "OA_REPLY", True),
    "OFFICIAL_NOTICE_005": ("OA_REPLY", "OA_IN", "OA2", "OA_REPLY_SUBSEQUENT", True),
    "OFFICIAL_NOTICE_021": ("OA_REPLY", "OA_IN", "OA2", "OA_REPLY_SUBSEQUENT", True),
    "OFFICIAL_NOTICE_024": ("OA_REPLY", "OA_IN", "OA2", "OA_REPLY_SUBSEQUENT", True),
    "OFFICIAL_NOTICE_029": ("OA_REPLY", "OA_IN", "OA2", "OA_REPLY_SUBSEQUENT", True),
}
SEED_DEV_ACTIVATIONS = {
    **APPROVED_ACTIVATIONS,
    "OFFICIAL_NOTICE_009": (
        "GRANT_NOTICE",
        "GRANT_NOTICE",
        "GRANT_PENDING",
        None,
        False,
    ),
    "OFFICIAL_NOTICE_031": (
        "FEE_REDUCTION_APPROVAL_NOTICE",
        "FEE_REDUCTION_APPROVAL_NOTICE",
        None,
        None,
        False,
    ),
    "OFFICIAL_NOTICE_034": (
        "APPLICATION_FEE_NOTICE",
        "APPLICATION_FEE_NOTICE",
        None,
        None,
        False,
    ),
}


def _catalog_rows(db) -> list[DocTemplate]:
    return list(
        db.execute(
            select(DocTemplate)
            .where(DocTemplate.code.like("OFFICIAL_NOTICE_%"))
            .order_by(DocTemplate.code.asc())
        )
        .scalars()
        .all()
    )


def _seed_activated_catalog(db) -> int:
    seed = getattr(notice_catalog, "seed_oa_acceptance_official_notice_catalog", None)
    assert callable(seed), "activated official-notice catalog seeder is missing"
    return seed(db)


def _assert_activated_catalog(
    rows: list[DocTemplate],
    activations=APPROVED_ACTIVATIONS,
) -> None:
    assert len(rows) == len(notice_catalog.OFFICIAL_NOTICE_CATALOG) == 60
    for row in rows:
        metadata = json.loads(row.input_fields or "{}")
        activation = activations.get(row.code)
        if activation is None:
            assert metadata["catalog_status"] == "REFERENCE_ONLY"
            assert metadata["execution_behavior"] is None
            assert metadata["canonical_template_code"] is None
            assert metadata["completion_event"] is None
            assert metadata["archive_status_restore"] is None
            assert metadata["deadline_source_policy"] is None
            assert row.status_effect is None
            assert row.deadline_template_code is None
            assert row.fee_draft_type is None
            assert row.need_reply is False
            continue

        behavior, canonical_code, status_effect, task_code, need_reply = activation
        assert metadata["catalog_status"] == "EXECUTABLE"
        assert metadata["execution_behavior"] == behavior
        assert metadata["canonical_template_code"] == canonical_code
        assert row.status_effect == status_effect
        assert row.deadline_template_code == task_code
        assert row.need_reply is need_reply
        if behavior == "OA_REPLY":
            assert row.fee_draft_type is None
            assert metadata["completion_event"] == "OFFICIAL_RECEIPT_ARCHIVED"
            assert metadata["archive_status_restore"] == "SUB_EXAM"
            assert metadata["deadline_source_policy"] == "EXPLICIT_OFFICIAL_DUE_REQUIRED"
        elif behavior == "GRANT_NOTICE":
            assert row.code == "OFFICIAL_NOTICE_009"
            assert row.name == "授权通知书-电子"
            assert row.fee_draft_type == "GRANT_FEE"
            assert metadata["completion_event"] is None
            assert metadata["archive_status_restore"] is None
            assert metadata["deadline_source_policy"] == "EXPLICIT_OFFICIAL_DUE_REQUIRED"
        elif behavior == "APPLICATION_FEE_NOTICE":
            assert row.code == "OFFICIAL_NOTICE_034"
            assert row.name == "缴纳申请费通知书"
            assert metadata["official_doc_codes"] == ["200103"]
            assert row.fee_draft_type == "APPLICATION_FEE"
            assert metadata["completion_event"] is None
            assert metadata["archive_status_restore"] is None
            assert metadata["deadline_source_policy"] == "EXPLICIT_OFFICIAL_DUE_REQUIRED"
        elif behavior == "FEE_REDUCTION_APPROVAL_NOTICE":
            assert row.code == "OFFICIAL_NOTICE_031"
            assert row.name == "费用减缓审批通知书"
            assert metadata["official_doc_codes"] == ["200021"]
            assert row.fee_draft_type is None
            assert row.reply_to_template_code is None
            assert metadata["completion_event"] is None
            assert metadata["archive_status_restore"] is None
            assert metadata["deadline_source_policy"] is None
        else:
            assert row.fee_draft_type is None
            assert metadata["completion_event"] is None
            assert metadata["archive_status_restore"] is None
            assert metadata["deadline_source_policy"] is None


def test_base_catalog_seed_remains_sixty_reference_only_rows(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as db:
        assert notice_catalog.seed_official_notice_catalog(db) == 60
        db.commit()

        rows = _catalog_rows(db)
        assert len(rows) == len(notice_catalog.OFFICIAL_NOTICE_CATALOG) == 60
        assert all(
            json.loads(row.input_fields or "{}")["catalog_status"] == "REFERENCE_ONLY"
            for row in rows
        )
        assert notice_catalog.seed_official_notice_catalog(db) == 0


def test_overlay_activates_only_approved_acceptance_and_oa_rows_idempotently(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as db:
        assert _seed_activated_catalog(db) == 60
        db.commit()

        rows = _catalog_rows(db)
        _assert_activated_catalog(rows)
        assert {
            row.code
            for row in rows
            if json.loads(row.input_fields)["catalog_status"] == "EXECUTABLE"
        } == set(APPROVED_ACTIVATIONS)
        assert _seed_activated_catalog(db) == 0


def test_seed_dev_applies_activation_overlay_idempotently(
    monkeypatch,
    session_factory: sessionmaker,
) -> None:
    monkeypatch.setattr(seed_dev, "seed_official_letter_out_catalog", lambda _db: 0)
    monkeypatch.setattr(seed_dev, "seed_grant_fee_notice_template_source", lambda _db: False)
    monkeypatch.setattr(seed_dev, "seed_format_letter_mappings", lambda _db: 0)

    with session_factory() as db:
        seed_dev.seed_doc_templates(db)
        rows = _catalog_rows(db)
        _assert_activated_catalog(rows, activations=SEED_DEV_ACTIVATIONS)
        first_snapshot = [(row.id, row.code, row.input_fields) for row in rows]

        seed_dev.seed_doc_templates(db)
        second_rows = _catalog_rows(db)
        _assert_activated_catalog(second_rows, activations=SEED_DEV_ACTIVATIONS)
        assert [(row.id, row.code, row.input_fields) for row in second_rows] == first_snapshot
