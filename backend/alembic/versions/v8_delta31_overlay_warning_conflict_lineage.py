"""add durable lifecycle overlay conflict lineage

Revision ID: v8_d31_overlay_conflict_01
Revises: v8_d27_annuity_reduction_01
"""

from __future__ import annotations

from hashlib import sha256
import json

import sqlalchemy as sa
from alembic import op


revision = "v8_d31_overlay_conflict_01"
down_revision = "v8_d27_annuity_reduction_01"
branch_labels = None
depends_on = None

_VERSION = "V1"
_LEGACY_CODES = ("LEGACY_STATUS_UNVERIFIED", "NO_REVERSE_MAPPING_AUTHORITY")
_KNOWN_STATUSES = frozenset(
    {
        "NOT_FILED", "PENDING", "GRANTED", "REJECTED", "WITHDRAWN", "ABANDONED",
        "EXPIRED", "WAITING_RECEIPT", "PRELIM_EXAM", "PRELIM_PASS", "AMENDMENT",
        "PUBLISHED", "SUB_EXAM", "OA1", "OA2", "REEXAM", "ACCEPTED",
        "GRANT_PENDING", "TERMINATED", "INVALIDATED",
    }
)


def _digest(codes: tuple[str, ...]) -> str:
    canonical = json.dumps(codes, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    return sha256(canonical.encode("utf-8")).hexdigest()


def _canonical_payload(case_id: str, status: str) -> str:
    return json.dumps(
        {
            "case_id": case_id,
            "legacy_status": status,
            "reverse_mapping": "NONE",
            "schema": "FPMS_V8_LEGACY_LIFECYCLE_IMPORT_V1",
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def _valid_ledger(connection, case_row, events) -> bool:
    revision_value = case_row["lifecycle_revision"]
    if type(revision_value) is not int or revision_value < 1 or len(events) != revision_value:
        return False
    if [row["sequence"] for row in events] != list(range(1, revision_value + 1)):
        return False
    axes = (None, None, None)
    for row in events:
        old_axes = (
            row["old_business_stage"],
            row["old_official_procedure_stage"],
            row["old_legal_status"],
        )
        if old_axes != axes:
            return False
        axes = (
            row["new_business_stage"],
            row["new_official_procedure_stage"],
            row["new_legal_status"],
        )
    return axes == (
        case_row["business_stage"],
        case_row["official_procedure_stage"],
        case_row["legal_status"],
    )


def _exact_legacy_import(connection, case_row, activity, events) -> bool:
    lifecycle_events = [row for row in events if row["lane"] == "LIFECYCLE"]
    evidence = connection.execute(
        sa.text(
            "SELECT 1 FROM t_case_activity_event_evidence "
            "WHERE activity_id = :activity_id LIMIT 1"
        ),
        {"activity_id": activity["id"]},
    ).first()
    payload_status = None
    try:
        payload = json.loads(activity["payload_json"])
        if type(payload) is dict:
            payload_status = payload.get("legacy_status")
    except (TypeError, ValueError):
        pass
    return bool(
        case_row["status"] in _KNOWN_STATUSES
        and payload_status in _KNOWN_STATUSES
        and activity["lane"] == "LIFECYCLE"
        and activity["activity_type"] == "LEGACY_IMPORT"
        and activity["confirmation_status"] == "LEGACY_UNVERIFIED"
        and activity["idempotency_key"]
        == f"v8-legacy-lifecycle-import:{activity['case_id']}"
        and activity["source_activity_id"] is None
        and activity["supersedes_event_id"] is None
        and activity["reviewer_id"] is None
        and activity["old_business_stage"] is None
        and activity["new_business_stage"] is None
        and activity["old_official_procedure_stage"] is None
        and activity["new_official_procedure_stage"] is None
        and activity["old_legal_status"] is None
        and activity["new_legal_status"] == "UNKNOWN"
        and activity["occurred_at"] == activity["effective_at"]
        and activity["payload_json"]
        == _canonical_payload(activity["case_id"], payload_status)
        and evidence is None
        and lifecycle_events
        and lifecycle_events[0]["id"] == activity["id"]
        and _valid_ledger(connection, case_row, events)
    )


def upgrade() -> None:
    with op.batch_alter_table("t_case_activity_event", recreate="always") as batch_op:
        batch_op.add_column(sa.Column("conflict_lineage_version", sa.String(32), nullable=True))
        batch_op.add_column(sa.Column("conflict_code_count", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("conflict_codes_sha256", sa.String(64), nullable=True))
        batch_op.create_check_constraint(
            "ck_t_case_activity_event_conflict_lineage_shape",
            "(conflict_lineage_version IS NULL AND conflict_code_count IS NULL "
            "AND conflict_codes_sha256 IS NULL) OR "
            "(conflict_lineage_version = 'V1' AND conflict_code_count IS NOT NULL "
            "AND conflict_code_count >= 0 AND conflict_codes_sha256 IS NOT NULL "
            "AND length(conflict_codes_sha256) = 64 "
            "AND conflict_codes_sha256 = lower(conflict_codes_sha256))",
        )
    op.create_table(
        "t_case_activity_event_conflict",
        sa.Column("case_id", sa.String(36), nullable=False),
        sa.Column("activity_id", sa.String(36), nullable=False),
        sa.Column("code", sa.String(128), nullable=False),
        sa.PrimaryKeyConstraint("activity_id", "code", name="pk_t_case_activity_event_conflict"),
        sa.ForeignKeyConstraint(
            ["case_id", "activity_id"],
            ["t_case_activity_event.case_id", "t_case_activity_event.id"],
            name="fk_t_case_activity_event_conflict_activity_same_case",
            ondelete="CASCADE",
        ),
        sa.CheckConstraint(
            "length(code) BETWEEN 1 AND 128",
            name="ck_t_case_activity_event_conflict_code",
        ),
    )
    connection = op.get_bind()
    connection.execute(
        sa.text(
            "UPDATE t_case_activity_event SET conflict_lineage_version = :version, "
            "conflict_code_count = 0, conflict_codes_sha256 = :digest "
            "WHERE activity_type NOT IN ('LEGACY_IMPORT', 'PATENT_REGISTER_STATUS_CONFIRMED')"
        ),
        {"version": _VERSION, "digest": _digest(())},
    )
    cases = connection.execute(
        sa.text(
            "SELECT id, status, lifecycle_revision, business_stage, "
            "official_procedure_stage, legal_status FROM t_case ORDER BY id"
        )
    ).mappings()
    for case_row in cases:
        events = list(
            connection.execute(
                sa.text(
                    "SELECT * FROM t_case_activity_event WHERE case_id = :case_id "
                    "ORDER BY sequence, id"
                ),
                {"case_id": case_row["id"]},
            ).mappings()
        )
        for activity in events:
            if activity["activity_type"] != "LEGACY_IMPORT" or not _exact_legacy_import(
                connection, case_row, activity, events
            ):
                continue
            connection.execute(
                sa.text(
                    "INSERT INTO t_case_activity_event_conflict (case_id, activity_id, code) "
                    "VALUES (:case_id, :activity_id, :code)"
                ),
                [
                    {"case_id": activity["case_id"], "activity_id": activity["id"], "code": code}
                    for code in _LEGACY_CODES
                ],
            )
            connection.execute(
                sa.text(
                    "UPDATE t_case_activity_event SET conflict_lineage_version = :version, "
                    "conflict_code_count = :count, conflict_codes_sha256 = :digest "
                    "WHERE id = :activity_id"
                ),
                {
                    "version": _VERSION,
                    "count": len(_LEGACY_CODES),
                    "digest": _digest(_LEGACY_CODES),
                    "activity_id": activity["id"],
                },
            )


def downgrade() -> None:
    raise NotImplementedError("This is a forward-only migration")
