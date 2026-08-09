from __future__ import annotations

import ast
import hashlib
import importlib
import inspect
import json
from dataclasses import FrozenInstanceError, asdict, fields, is_dataclass
from datetime import datetime
from types import ModuleType
from typing import Any

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.core.errors import BusinessError
from app.modules.auth.models import T_User
from app.modules.cases.lifecycle_contracts import (
    ActivityLane,
    BusinessStage,
    ConfirmationStatus,
    LegalStatus,
    OfficialProcedureStage,
)
from app.modules.cases.models import Case, CaseActivityEvent
from app.modules.documents.evidence_contracts import (
    EvidenceReviewState,
    EvidenceRole,
    EvidenceVersionState,
)
from app.modules.documents.models import (
    DocAttachment,
    Document,
    DocumentEvidenceVersion,
)


def _id(value: int) -> str:
    return f"00000000-0000-0000-0000-{value:012d}"


def _api() -> ModuleType:
    try:
        return importlib.import_module("scripts.audit_v8_legacy_state")
    except ModuleNotFoundError:
        pytest.fail("legacy-state preflight public seam is missing")


def _actor_id(transaction: Session) -> str:
    actor_id = transaction.scalar(select(T_User.id).where(T_User.username == "admin"))
    assert actor_id is not None
    return actor_id


def _add_case(
    transaction: Session,
    value: int,
    *,
    case_id: str | None = None,
    status: str = "NOT_FILED",
    business_stage: str | None = BusinessStage.NEW_CASE.value,
    official_stage: str | None = OfficialProcedureStage.NOT_SUBMITTED.value,
    legal_status: str | None = LegalStatus.NOT_ESTABLISHED.value,
    verification_status: str | None = ConfirmationStatus.CONFIRMED.value,
    lifecycle_revision: int | None = 0,
) -> Case:
    case = Case(
        id=case_id or _id(value),
        case_no=f"LEGACY-PREFLIGHT-{value}",
        status=status,
        business_stage=business_stage,
        official_procedure_stage=official_stage,
        legal_status=legal_status,
        lifecycle_verification_status=verification_status,
        lifecycle_revision=lifecycle_revision,
    )
    transaction.add(case)
    transaction.flush()
    return case


def _add_activity(
    transaction: Session,
    *,
    case: Case,
    actor_id: str,
    value: int,
    sequence: int,
    lane: str = ActivityLane.LIFECYCLE.value,
    activity_type: str = "CASE_OPENED",
    confirmation_status: str = ConfirmationStatus.CONFIRMED.value,
    payload: object = None,
) -> CaseActivityEvent:
    activity = CaseActivityEvent(
        id=_id(1000 + value),
        case_id=case.id,
        sequence=sequence,
        lane=lane,
        activity_type=activity_type,
        effective_at=datetime(2026, 8, 9, 10, sequence),
        confirmation_status=confirmation_status,
        actor_id=actor_id,
        idempotency_key=f"legacy-preflight-{value}-{sequence}-{lane}",
        payload_json=(
            payload
            if isinstance(payload, str)
            else json.dumps(payload or {}, separators=(",", ":"))
        ),
    )
    transaction.add(activity)
    transaction.flush()
    return activity


def _add_attachment(
    transaction: Session,
    value: int,
    *,
    content_hash: str | None,
) -> tuple[Case, Document, DocAttachment]:
    case = _add_case(transaction, 2000 + value)
    document = Document(
        id=_id(3000 + value),
        case_id=case.id,
        direction="IN",
        title=f"旧附件 {value}",
    )
    attachment = DocAttachment(
        id=_id(4000 + value),
        document_id=document.id,
        file_name=f"legacy-{value}.pdf",
        file_path=f"legacy/legacy-{value}.pdf",
        content_hash=content_hash,
    )
    transaction.add_all((document, attachment))
    transaction.flush()
    return case, document, attachment


def _add_version(
    transaction: Session,
    *,
    actor_id: str,
    case: Case,
    document: Document,
    attachment: DocAttachment,
    value: int,
    role: EvidenceRole,
    lineage_attachment_id: str | None = None,
) -> DocumentEvidenceVersion:
    lineage_key = f"attachment:{lineage_attachment_id or attachment.id}"
    version = DocumentEvidenceVersion(
        id=_id(5000 + value),
        case_id=case.id,
        document_id=document.id,
        attachment_id=attachment.id,
        lineage_key=lineage_key,
        role=role.value,
        version_number=1,
        state=EvidenceVersionState.DRAFT.value,
        creator_id=actor_id,
        review_state=EvidenceReviewState.PENDING.value,
        content_hash=attachment.content_hash or f"sha256:{value:064x}",
        current_identity_key=f"{case.id}|{lineage_key}",
    )
    transaction.add(version)
    transaction.flush()
    return version


def _case_snapshot(transaction: Session) -> tuple[tuple[Any, ...], ...]:
    return tuple(
        transaction.execute(
            select(
                Case.id,
                Case.status,
                Case.business_stage,
                Case.official_procedure_stage,
                Case.legal_status,
                Case.lifecycle_verification_status,
                Case.lifecycle_revision,
            ).order_by(Case.id)
        ).all()
    )


def _activity_snapshot(transaction: Session) -> tuple[tuple[Any, ...], ...]:
    return tuple(
        transaction.execute(
            select(
                CaseActivityEvent.id,
                CaseActivityEvent.case_id,
                CaseActivityEvent.sequence,
                CaseActivityEvent.lane,
                CaseActivityEvent.activity_type,
                CaseActivityEvent.confirmation_status,
                CaseActivityEvent.payload_json,
            ).order_by(CaseActivityEvent.case_id, CaseActivityEvent.sequence)
        ).all()
    )


def _version_snapshot(transaction: Session) -> tuple[tuple[Any, ...], ...]:
    return tuple(
        transaction.execute(
            select(
                DocumentEvidenceVersion.id,
                DocumentEvidenceVersion.attachment_id,
                DocumentEvidenceVersion.lineage_key,
                DocumentEvidenceVersion.role,
                DocumentEvidenceVersion.current_identity_key,
            ).order_by(DocumentEvidenceVersion.id)
        ).all()
    )


def _canonical_report_hash(report: object) -> str:
    payload = asdict(report)
    payload.pop("report_sha256")
    payload = {
        "schema": "FPMS_V8_LEGACY_STATE_PREFLIGHT_V1",
        **payload,
    }
    serialized = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def test_public_contract_is_exact_frozen_slotted_keyword_only_and_synchronous() -> None:
    api = _api()

    assert api.__all__ == (
        "LegacyStatePreflightCaseRow",
        "LegacyStatePreflightAttachmentRow",
        "LegacyStatePreflightReport",
        "audit_v8_legacy_state",
    )
    expected_fields = {
        api.LegacyStatePreflightCaseRow: (
            "case_id",
            "legacy_status",
            "classification",
            "derived_status",
            "conflict_codes",
            "legacy_granted_unresolved",
        ),
        api.LegacyStatePreflightAttachmentRow: ("attachment_id", "classification"),
        api.LegacyStatePreflightReport: (
            "case_scanned",
            "case_unchanged",
            "case_update_required",
            "case_conflicts",
            "case_invalid",
            "legacy_granted_unresolved",
            "attachment_scanned",
            "attachment_importable",
            "attachment_unchanged",
            "attachment_invalid",
            "attachment_role_conflicts",
            "attachment_current_conflicts",
            "report_sha256",
            "cases",
            "attachments",
        ),
    }
    for result_type, names in expected_fields.items():
        assert is_dataclass(result_type)
        assert tuple(field.name for field in fields(result_type)) == names
        assert all(field.kw_only for field in fields(result_type))
        assert result_type.__slots__ == names

    row = api.LegacyStatePreflightCaseRow(
        case_id=_id(1),
        legacy_status="NOT_FILED",
        classification="UNCHANGED",
        derived_status="NOT_FILED",
        conflict_codes=(),
        legacy_granted_unresolved=False,
    )
    assert not hasattr(row, "__dict__")
    with pytest.raises(FrozenInstanceError):
        row.classification = "UPDATE_REQUIRED"

    signature = inspect.signature(api.audit_v8_legacy_state)
    assert tuple(signature.parameters) == ("transaction", "actor_id")
    assert all(
        parameter.kind is inspect.Parameter.KEYWORD_ONLY
        for parameter in signature.parameters.values()
    )
    assert not inspect.iscoroutinefunction(api.audit_v8_legacy_state)


def test_case_projection_latest_activity_granted_boundary_counts_and_hash_are_exact(
    session_factory: sessionmaker[Session],
) -> None:
    api = _api()
    with session_factory() as transaction:
        actor_id = _actor_id(transaction)
        second_actor = T_User(
            id=_id(999),
            username="legacy-preflight-reviewer",
            display_name="Legacy Preflight Reviewer",
            password_hash="not-used",
            is_active=True,
        )
        transaction.add(second_actor)

        unchanged = _add_case(transaction, 1)
        update = _add_case(transaction, 2, status="PENDING")
        retained = _add_case(
            transaction,
            3,
            status="PENDING",
            business_stage=None,
            official_stage=None,
            legal_status=None,
            verification_status=None,
            lifecycle_revision=None,
        )
        old_granted = _add_case(
            transaction,
            4,
            status="GRANTED",
            business_stage=None,
            official_stage=None,
            legal_status=None,
            verification_status=None,
            lifecycle_revision=None,
        )
        managed_granted = _add_case(
            transaction,
            5,
            status="GRANTED",
            business_stage=BusinessStage.POST_GRANT_MAINTENANCE.value,
            official_stage=OfficialProcedureStage.GRANT_ANNOUNCED.value,
            legal_status=LegalStatus.PATENT_IN_FORCE.value,
            verification_status=ConfirmationStatus.CONFIRMED.value,
            lifecycle_revision=1,
        )
        _add_activity(
            transaction,
            case=managed_granted,
            actor_id=actor_id,
            value=5,
            sequence=1,
            activity_type="GRANT_ANNOUNCEMENT_CONFIRMED",
        )
        oa = _add_case(
            transaction,
            6,
            status="OA2",
            business_stage=BusinessStage.OA_REPLY_IN_PROGRESS.value,
            official_stage=OfficialProcedureStage.OFFICE_ACTION_RESPONSE.value,
            legal_status=LegalStatus.APPLICATION_PENDING.value,
            verification_status=ConfirmationStatus.CONFIRMED.value,
            lifecycle_revision=3,
        )
        _add_activity(
            transaction,
            case=oa,
            actor_id=actor_id,
            value=60,
            sequence=1,
            activity_type="OA_NOTICE_RECORDED",
            payload={"oa_sequence": 2},
        )
        _add_activity(
            transaction,
            case=oa,
            actor_id=actor_id,
            value=61,
            sequence=2,
            lane=ActivityLane.DOCUMENT.value,
            activity_type="IGNORED_DOCUMENT_ACTIVITY",
            payload={"oa_sequence": False},
        )
        _add_activity(
            transaction,
            case=oa,
            actor_id=actor_id,
            value=62,
            sequence=3,
            activity_type="IGNORED_UNCONFIRMED_LIFECYCLE",
            confirmation_status=ConfirmationStatus.NEEDS_REVIEW.value,
            payload={"oa_sequence": False},
        )
        transaction.commit()

        report = api.audit_v8_legacy_state(transaction=transaction, actor_id=actor_id)
        second_report = api.audit_v8_legacy_state(
            transaction=transaction,
            actor_id=second_actor.id,
        )

        assert report == second_report
        assert (
            report.case_scanned,
            report.case_unchanged,
            report.case_update_required,
            report.case_conflicts,
            report.case_invalid,
            report.legacy_granted_unresolved,
        ) == (6, 3, 1, 2, 0, 1)
        assert report.attachment_scanned == 0
        assert tuple(row.case_id for row in report.cases) == tuple(
            sorted(row.case_id for row in report.cases)
        )
        by_id = {row.case_id: row for row in report.cases}
        assert (
            by_id[unchanged.id].classification,
            by_id[unchanged.id].derived_status,
        ) == ("UNCHANGED", "NOT_FILED")
        assert (
            by_id[update.id].classification,
            by_id[update.id].derived_status,
        ) == ("UPDATE_REQUIRED", "NOT_FILED")
        assert by_id[retained.id].classification == "RETAINED_CONFLICT"
        assert by_id[retained.id].conflict_codes == (
            "LEGACY_PROJECTION_INCOMPLETE_AXES",
            "LEGACY_PROJECTION_UNVERIFIED",
        )
        assert by_id[old_granted.id].classification == "RETAINED_CONFLICT"
        assert by_id[old_granted.id].legacy_granted_unresolved is True
        assert by_id[old_granted.id].conflict_codes == (
            "LEGACY_GRANTED_UNRESOLVED",
            "LEGACY_PROJECTION_INCOMPLETE_AXES",
            "LEGACY_PROJECTION_UNVERIFIED",
        )
        assert by_id[managed_granted.id].classification == "UNCHANGED"
        assert by_id[managed_granted.id].legacy_granted_unresolved is False
        assert by_id[oa.id].classification == "UNCHANGED"
        assert by_id[oa.id].derived_status == "OA2"
        assert report.report_sha256 == _canonical_report_hash(report)


@pytest.mark.parametrize(
    ("field", "value", "expected_code"),
    (
        ("case_id", " invalid-case-id ", "LEGACY_STATE_CASE_ID_INVALID"),
        ("status", " ", "LEGACY_STATE_STATUS_INVALID"),
        ("business_stage", "INVALID", "LEGACY_STATE_BUSINESS_STAGE_INVALID"),
        (
            "official_procedure_stage",
            "INVALID",
            "LEGACY_STATE_OFFICIAL_STAGE_INVALID",
        ),
        ("legal_status", "INVALID", "LEGACY_STATE_LEGAL_STATUS_INVALID"),
        (
            "lifecycle_verification_status",
            "INVALID",
            "LEGACY_STATE_VERIFICATION_STATUS_INVALID",
        ),
        ("lifecycle_revision", -1, "LEGACY_STATE_REVISION_INVALID"),
    ),
)
def test_invalid_case_carriers_fail_closed_without_aborting_other_rows(
    session_factory: sessionmaker[Session],
    field: str,
    value: object,
    expected_code: str,
) -> None:
    api = _api()
    with session_factory() as transaction:
        kwargs: dict[str, object] = {}
        if field == "case_id":
            kwargs["case_id"] = value
        elif field == "status":
            kwargs["status"] = value
        elif field == "business_stage":
            kwargs["business_stage"] = value
        elif field == "official_procedure_stage":
            kwargs["official_stage"] = value
        elif field == "legal_status":
            kwargs["legal_status"] = value
        elif field == "lifecycle_verification_status":
            kwargs["verification_status"] = value
        else:
            kwargs["lifecycle_revision"] = value
        invalid = _add_case(transaction, 100, **kwargs)  # type: ignore[arg-type]
        valid = _add_case(transaction, 101)
        transaction.commit()

        report = api.audit_v8_legacy_state(
            transaction=transaction,
            actor_id=_actor_id(transaction),
        )

        rows = {row.case_id: row for row in report.cases}
        assert rows[invalid.id].classification == "INVALID_CARRIER"
        assert rows[invalid.id].derived_status is None
        assert rows[invalid.id].conflict_codes == (expected_code,)
        assert rows[valid.id].classification == "UNCHANGED"
        assert (report.case_invalid, report.case_unchanged) == (1, 1)


def test_boolean_revision_is_invalid_without_autoflush(
    session_factory: sessionmaker[Session],
) -> None:
    api = _api()
    with session_factory() as transaction:
        invalid = _add_case(transaction, 110)
        transaction.commit()
        invalid.lifecycle_revision = True

        report = api.audit_v8_legacy_state(
            transaction=transaction,
            actor_id=_actor_id(transaction),
        )

        assert report.cases[0].case_id == invalid.id
        assert report.cases[0].classification == "INVALID_CARRIER"
        assert report.cases[0].conflict_codes == ("LEGACY_STATE_REVISION_INVALID",)
        assert invalid.lifecycle_revision is True


@pytest.mark.parametrize(
    ("activity_type", "payload", "expected_code"),
    (
        (" ", {}, "LEGACY_STATE_ACTIVITY_TYPE_INVALID"),
        ("OA_NOTICE_RECORDED", "[]", "LEGACY_STATE_ACTIVITY_PAYLOAD_INVALID"),
        ("OA_NOTICE_RECORDED", {"oa_sequence": False}, "LEGACY_STATE_OA_SEQUENCE_INVALID"),
        ("OA_NOTICE_RECORDED", {"oa_sequence": 0}, "LEGACY_STATE_OA_SEQUENCE_INVALID"),
    ),
)
def test_invalid_latest_activity_carriers_fail_closed(
    session_factory: sessionmaker[Session],
    activity_type: str,
    payload: object,
    expected_code: str,
) -> None:
    api = _api()
    with session_factory() as transaction:
        case = _add_case(
            transaction,
            120,
            status="OA1",
            business_stage=BusinessStage.OA_REPLY_IN_PROGRESS.value,
            official_stage=OfficialProcedureStage.OFFICE_ACTION_RESPONSE.value,
            legal_status=LegalStatus.APPLICATION_PENDING.value,
        )
        _add_activity(
            transaction,
            case=case,
            actor_id=_actor_id(transaction),
            value=120,
            sequence=1,
            activity_type=activity_type,
            payload=payload,
        )
        transaction.commit()

        report = api.audit_v8_legacy_state(
            transaction=transaction,
            actor_id=_actor_id(transaction),
        )

        assert report.cases[0].classification == "INVALID_CARRIER"
        assert report.cases[0].conflict_codes == (expected_code,)


def test_attachment_classifications_are_exact_and_entire_audit_is_read_only(
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    api = _api()
    with session_factory() as transaction:
        actor_id = _actor_id(transaction)
        _add_attachment(transaction, 1, content_hash=f"sha256:{'1' * 64}")
        unchanged = _add_attachment(transaction, 2, content_hash=f"sha256:{'2' * 64}")
        role_conflict = _add_attachment(transaction, 3, content_hash=f"sha256:{'3' * 64}")
        current_conflict = _add_attachment(
            transaction,
            4,
            content_hash=f"sha256:{'4' * 64}",
        )
        _add_attachment(transaction, 5, content_hash=None)
        _add_version(
            transaction,
            actor_id=actor_id,
            case=unchanged[0],
            document=unchanged[1],
            attachment=unchanged[2],
            value=2,
            role=EvidenceRole.RAW_ATTACHMENT,
        )
        _add_version(
            transaction,
            actor_id=actor_id,
            case=role_conflict[0],
            document=role_conflict[1],
            attachment=role_conflict[2],
            value=3,
            role=EvidenceRole.FILING_FULL_WORD,
        )
        conflicting_attachment = DocAttachment(
            id=_id(4904),
            document_id=current_conflict[1].id,
            file_name="other.pdf",
            file_path="legacy/other.pdf",
            content_hash=None,
        )
        transaction.add(conflicting_attachment)
        transaction.flush()
        _add_version(
            transaction,
            actor_id=actor_id,
            case=current_conflict[0],
            document=current_conflict[1],
            attachment=conflicting_attachment,
            value=4,
            role=EvidenceRole.RAW_ATTACHMENT,
            lineage_attachment_id=current_conflict[2].id,
        )
        transaction.commit()

        before_cases = _case_snapshot(transaction)
        before_activities = _activity_snapshot(transaction)
        before_versions = _version_snapshot(transaction)
        before_state = (
            tuple(transaction.new),
            tuple(transaction.dirty),
            tuple(transaction.deleted),
        )

        def _write_called(*_args: object, **_kwargs: object) -> None:
            pytest.fail("legacy-state preflight attempted a write or transaction operation")

        with monkeypatch.context() as guarded:
            for method in ("add", "add_all", "delete", "flush", "commit", "rollback", "close"):
                guarded.setattr(transaction, method, _write_called)
            first = api.audit_v8_legacy_state(transaction=transaction, actor_id=actor_id)
            second = api.audit_v8_legacy_state(transaction=transaction, actor_id=actor_id)

        assert first == second
        assert (
            first.attachment_scanned,
            first.attachment_importable,
            first.attachment_unchanged,
            first.attachment_invalid,
            first.attachment_role_conflicts,
            first.attachment_current_conflicts,
        ) == (6, 1, 1, 2, 1, 1)
        assert tuple(row.classification for row in first.attachments) == (
            "IMPORT",
            "UNCHANGED",
            "ROLE_CONFLICT",
            "CURRENT_CONFLICT",
            "INVALID",
            "INVALID",
        )
        assert tuple(row.attachment_id for row in first.attachments) == tuple(
            sorted(row.attachment_id for row in first.attachments)
        )
        assert first.report_sha256 == _canonical_report_hash(first)
        assert _case_snapshot(transaction) == before_cases
        assert _activity_snapshot(transaction) == before_activities
        assert _version_snapshot(transaction) == before_versions
        assert (
            tuple(transaction.new),
            tuple(transaction.dirty),
            tuple(transaction.deleted),
        ) == before_state


@pytest.mark.parametrize(
    ("actor_id", "expected_code"),
    (
        ("", "LEGACY_DOCUMENT_EVIDENCE_ACTOR_INVALID"),
        (_id(999999), "LEGACY_DOCUMENT_EVIDENCE_ACTOR_MISSING"),
    ),
)
def test_actor_errors_propagate_unchanged(
    session_factory: sessionmaker[Session],
    actor_id: str,
    expected_code: str,
) -> None:
    api = _api()
    with session_factory() as transaction:
        with pytest.raises(BusinessError) as caught:
            api.audit_v8_legacy_state(transaction=transaction, actor_id=actor_id)

        assert caught.value.code == expected_code
        assert caught.value.status_code == 409


def test_source_has_no_cli_reverse_mapping_or_write_path() -> None:
    api = _api()
    source = inspect.getsource(api)
    tree = ast.parse(source)

    assert "__main__" not in source
    assert "create_engine" not in source
    assert "append_case_activity" not in source
    assert "apply_lifecycle_event" not in source
    assert "PATENT_IN_FORCE" not in source
    assert not any(
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "transaction"
        and node.func.attr in {"add", "add_all", "delete", "flush", "commit", "rollback", "close"}
        for node in ast.walk(tree)
    )
    assert not any(
        isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign))
        and any(
            isinstance(target, ast.Attribute) and target.attr == "status"
            for target in (node.targets if isinstance(node, ast.Assign) else (node.target,))
        )
        for node in ast.walk(tree)
    )
