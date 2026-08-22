from __future__ import annotations

import hashlib
import json
from datetime import date, datetime
from decimal import Decimal
from uuid import uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.core.errors import BusinessError
from app.modules.auth.models import T_User
from app.modules.cases.models import Case
from app.modules.documents.models import DocAttachment, Document, DocumentEvidenceVersion
from app.modules.fees.fee_reduction import FeeReductionApprovalScopeType
from app.modules.fees.fee_reduction_approval_service import (
    RecordFeeReductionApprovalCommand,
    record_fee_reduction_approval,
)
from app.modules.fees.models import FeeReductionApproval, LegacyFeeReductionProvenance
from scripts.backfill_v8_fee_reduction import (
    LegacyFeeReductionApprovalMatch,
    LegacyFeeReductionMigrationManifest,
    LegacyFeeReductionMigrationRow,
    import_legacy_fee_reductions,
)

_COUNT_KEYS = {
    "scanned",
    "explicit-zero",
    "reused-70",
    "reused-85",
    "unchanged",
    "invalid",
    "missing-approval",
    "ambiguous-approval",
    "planned-writes",
}


def _row(case_id: str, legacy_value: object) -> LegacyFeeReductionMigrationRow:
    return LegacyFeeReductionMigrationRow(
        case_id=case_id,
        legacy_value=legacy_value,
        source_reference=f"legacy://fee-reduction/{case_id}",
        source_version="customer-export-v1",
        source_snapshot_hash="b" * 64,
        approval_id=None,
    )


def _manifest(
    actor_id: str,
    *rows: LegacyFeeReductionMigrationRow,
) -> LegacyFeeReductionMigrationManifest:
    return LegacyFeeReductionMigrationManifest(
        version="customer-approved-v1",
        manifest_hash="a" * 64,
        approval_status="APPROVED",
        confirmed_by=actor_id,
        confirmed_at=datetime(2026, 7, 15, 9, 30),
        rows=tuple(rows),
    )


def _seed_cases(transaction: Session, *case_ids: str) -> None:
    transaction.add_all(
        Case(id=case_id, case_no=f"NO-{case_id}", fee_reduction=None) for case_id in case_ids
    )
    transaction.commit()


def _admin_id(transaction: Session) -> str:
    return transaction.scalar(select(T_User.id).where(T_User.username == "admin"))


def _approval_row(
    *,
    case_id: str,
    legacy_value: str,
    approval_id: str,
    match: LegacyFeeReductionApprovalMatch,
) -> LegacyFeeReductionMigrationRow:
    return LegacyFeeReductionMigrationRow(
        case_id=case_id,
        legacy_value=legacy_value,
        source_reference=f"legacy://fee-reduction/{case_id}",
        source_version="customer-export-v1",
        source_snapshot_hash="b" * 64,
        approval_id=approval_id,
        approval_match=match,
    )


def _seed_confirmed_approval(
    transaction: Session,
    *,
    case_id: str,
    legacy_value: str,
    actor_id: str,
) -> tuple[FeeReductionApproval, LegacyFeeReductionApprovalMatch]:
    document_id = str(uuid4())
    attachment_id = str(uuid4())
    evidence_id = str(uuid4())
    lineage_key = f"fee-reduction-{case_id}"
    content_hash = f"sha256:{'d' * 64}"
    transaction.add(Document(id=document_id, case_id=case_id, title="synthetic approval source"))
    transaction.flush()
    transaction.add(
        DocAttachment(
            id=attachment_id,
            document_id=document_id,
            file_name="synthetic.txt",
            file_path=f"/synthetic/{case_id}.txt",
            content_hash=content_hash,
        )
    )
    transaction.flush()
    transaction.add(
        DocumentEvidenceVersion(
            id=evidence_id,
            case_id=case_id,
            document_id=document_id,
            attachment_id=attachment_id,
            lineage_key=lineage_key,
            role="FEE_REDUCTION_APPROVAL",
            version_number=1,
            state="FINAL",
            creator_id="synthetic-creator",
            review_state="APPROVED",
            reviewer_id="synthetic-reviewer",
            reviewed_at=datetime(2026, 7, 14, 10, 0),
            final_submitted_at=datetime(2026, 7, 14, 9, 0),
            content_hash=content_hash,
            current_identity_key=f"{case_id}|{lineage_key}",
        )
    )
    transaction.flush()
    applicant_ids = ("applicant-1", "applicant-2") if legacy_value == "0.7" else ("applicant-1",)
    attributes_json = json.dumps(
        {applicant_id: {"eligible": True} for applicant_id in applicant_ids},
        sort_keys=True,
        separators=(",", ":"),
    )
    result = record_fee_reduction_approval(
        transaction=transaction,
        command=RecordFeeReductionApprovalCommand(
            case_id=case_id,
            scope_type=FeeReductionApprovalScopeType.CASE,
            applicant_ids=applicant_ids,
            eligibility_attributes_version="synthetic-v1",
            eligibility_attributes_json=attributes_json,
            reduction_ratio=Decimal(legacy_value),
            fee_codes=("FILING_FEE",),
            fee_year_from=2026,
            fee_year_to=2026,
            effective_from=date(2026, 1, 1),
            effective_to=date(2026, 12, 31),
            source_evidence_version_id=evidence_id,
            expected_source_content_hash=content_hash,
            confirmed_at=datetime(2026, 7, 15, 8, 0),
            confirmed_by=actor_id,
        ),
    )
    transaction.flush()
    approval = transaction.get(FeeReductionApproval, result.approval_id)
    return approval, LegacyFeeReductionApprovalMatch(
        scope_type=FeeReductionApprovalScopeType.CASE,
        case_id=case_id,
        applicant_set_key=None,
        fee_codes=("FILING_FEE",),
        fee_year_from=2026,
        fee_year_to=2026,
        effective_from=date(2026, 1, 1),
        effective_to=date(2026, 12, 31),
        source_evidence_version_id=evidence_id,
        source_evidence_content_hash=content_hash,
    )


def test_dry_run_is_deterministic_case_ordered_and_write_free(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        _seed_cases(transaction, "case-002", "case-001")
        manifest = _manifest(
            _admin_id(transaction),
            _row("case-002", "0"),
            _row("case-001", "0"),
        )

        first = import_legacy_fee_reductions(
            transaction=transaction,
            manifest=manifest,
            dry_run=True,
        )
        second = import_legacy_fee_reductions(
            transaction=transaction,
            manifest=manifest,
            dry_run=True,
        )

        assert first == second
        assert tuple(row.case_id for row in first.rows) == ("case-001", "case-002")
        assert tuple(row.classification for row in first.rows) == (
            "explicit-zero",
            "explicit-zero",
        )
        assert set(first.counts) == _COUNT_KEYS
        assert first.counts == {
            "scanned": 2,
            "explicit-zero": 2,
            "reused-70": 0,
            "reused-85": 0,
            "unchanged": 0,
            "invalid": 0,
            "missing-approval": 0,
            "ambiguous-approval": 0,
            "planned-writes": 2,
        }
        assert len(first.input_sha256) == 64
        assert len(first.plan_sha256) == 64
        assert len(first.output_sha256) == 64
        assert transaction.scalar(select(LegacyFeeReductionProvenance.id)) is None
        assert transaction.get(Case, "case-001").fee_reduction is None


def test_apply_requires_exact_plan_and_remains_caller_owned(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        _seed_cases(transaction, "case-plan")
        manifest = _manifest(_admin_id(transaction), _row("case-plan", "0"))
        planned = import_legacy_fee_reductions(
            transaction=transaction,
            manifest=manifest,
            dry_run=True,
        )

        for expected_hash in (None, "f" * 64):
            with pytest.raises(BusinessError) as error:
                import_legacy_fee_reductions(
                    transaction=transaction,
                    manifest=manifest,
                    dry_run=False,
                    expected_plan_sha256=expected_hash,
                )
            assert error.value.status_code == 409
        assert transaction.get(Case, "case-plan").fee_reduction is None
        assert transaction.scalar(select(LegacyFeeReductionProvenance.id)) is None

        applied = import_legacy_fee_reductions(
            transaction=transaction,
            manifest=manifest,
            dry_run=False,
            expected_plan_sha256=planned.plan_sha256,
        )
        assert applied.output_sha256 == planned.output_sha256
        assert transaction.get(Case, "case-plan").fee_reduction == "0"
        assert transaction.scalar(select(LegacyFeeReductionProvenance.id)) is not None
        transaction.rollback()

    with session_factory() as observer:
        assert observer.get(Case, "case-plan").fee_reduction is None
        assert observer.scalar(select(LegacyFeeReductionProvenance.id)) is None


@pytest.mark.parametrize("invalid_value", [None, 0, 0.0, "", " 0", "0 ", "00", "0.70"])
def test_invalid_grammar_fails_the_whole_apply_before_any_write(
    session_factory: sessionmaker,
    invalid_value: object,
) -> None:
    with session_factory() as transaction:
        _seed_cases(transaction, "case-valid", "case-invalid")
        manifest = _manifest(
            _admin_id(transaction),
            _row("case-valid", "0"),
            _row("case-invalid", invalid_value),
        )
        planned = import_legacy_fee_reductions(
            transaction=transaction,
            manifest=manifest,
            dry_run=True,
        )

        assert planned.counts["invalid"] == 1
        with pytest.raises(BusinessError) as error:
            import_legacy_fee_reductions(
                transaction=transaction,
                manifest=manifest,
                dry_run=False,
                expected_plan_sha256=planned.plan_sha256,
            )
        assert error.value.status_code == 409
        assert transaction.get(Case, "case-valid").fee_reduction is None
        assert transaction.scalar(select(LegacyFeeReductionProvenance.id)) is None


@pytest.mark.parametrize(
    ("case_id", "legacy_value", "classification"),
    [
        ("case-reduction-70", "0.7", "reused-70"),
        ("case-reduction-85", "0.85", "reused-85"),
    ],
)
def test_nonzero_import_reuses_one_exact_confirmed_approval(
    session_factory: sessionmaker,
    case_id: str,
    legacy_value: str,
    classification: str,
) -> None:
    with session_factory() as transaction:
        _seed_cases(transaction, case_id)
        actor_id = _admin_id(transaction)
        approval, match = _seed_confirmed_approval(
            transaction,
            case_id=case_id,
            legacy_value=legacy_value,
            actor_id=actor_id,
        )
        transaction.commit()
        manifest = _manifest(
            actor_id,
            _approval_row(
                case_id=case_id,
                legacy_value=legacy_value,
                approval_id=approval.id,
                match=match,
            ),
        )
        approval_count = transaction.scalar(
            select(FeeReductionApproval.id).where(FeeReductionApproval.id == approval.id)
        )

        planned = import_legacy_fee_reductions(
            transaction=transaction,
            manifest=manifest,
            dry_run=True,
        )
        assert planned.rows[0].classification == classification
        assert planned.counts[classification] == 1
        assert planned.counts["planned-writes"] == 1
        assert transaction.get(Case, case_id).fee_reduction is None

        import_legacy_fee_reductions(
            transaction=transaction,
            manifest=manifest,
            dry_run=False,
            expected_plan_sha256=planned.plan_sha256,
        )
        transaction.commit()
        provenance = transaction.scalar(
            select(LegacyFeeReductionProvenance).where(
                LegacyFeeReductionProvenance.case_id == case_id
            )
        )
        assert transaction.get(Case, case_id).fee_reduction == legacy_value
        assert provenance.legacy_value == legacy_value
        assert provenance.approval_id == approval.id
        assert (
            transaction.scalar(
                select(FeeReductionApproval.id).where(FeeReductionApproval.id == approval.id)
            )
            == approval_count
        )

        replay_plan = import_legacy_fee_reductions(
            transaction=transaction,
            manifest=manifest,
            dry_run=True,
        )
        assert replay_plan.rows[0].classification == "unchanged"
        assert replay_plan.counts["planned-writes"] == 0
        import_legacy_fee_reductions(
            transaction=transaction,
            manifest=manifest,
            dry_run=False,
            expected_plan_sha256=replay_plan.plan_sha256,
        )
        assert transaction.scalars(
            select(LegacyFeeReductionProvenance).where(
                LegacyFeeReductionProvenance.case_id == case_id
            )
        ).all() == [provenance]


def test_missing_or_multiple_exact_approvals_fail_before_any_write(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        _seed_cases(transaction, "case-missing", "case-ambiguous")
        actor_id = _admin_id(transaction)
        missing_approval, missing_match = _seed_confirmed_approval(
            transaction,
            case_id="case-missing",
            legacy_value="0.7",
            actor_id=actor_id,
        )
        approval, ambiguous_match = _seed_confirmed_approval(
            transaction,
            case_id="case-ambiguous",
            legacy_value="0.85",
            actor_id=actor_id,
        )
        transaction.flush()
        duplicate = FeeReductionApproval(
            id=str(uuid4()),
            scope_type=approval.scope_type,
            case_id=approval.case_id,
            applicant_set_key=approval.applicant_set_key,
            reduction_ratio=approval.reduction_ratio,
            fee_scope_snapshot=approval.fee_scope_snapshot,
            fee_scope_hash=approval.fee_scope_hash,
            fee_year_from=approval.fee_year_from,
            fee_year_to=approval.fee_year_to,
            effective_from=approval.effective_from,
            effective_to=approval.effective_to,
            source_evidence_version_id=approval.source_evidence_version_id,
            confirmation_status=approval.confirmation_status,
            confirmed_at=approval.confirmed_at,
            confirmed_by=approval.confirmed_by,
            eligibility_snapshot=approval.eligibility_snapshot,
            eligibility_snapshot_hash=approval.eligibility_snapshot_hash,
            approval_identity_key=hashlib.sha256(b"synthetic-duplicate").hexdigest(),
        )
        transaction.add(duplicate)
        transaction.commit()
        manifest = _manifest(
            actor_id,
            _approval_row(
                case_id="case-missing",
                legacy_value="0.7",
                approval_id=str(uuid4()),
                match=missing_match,
            ),
            _approval_row(
                case_id="case-ambiguous",
                legacy_value="0.85",
                approval_id=approval.id,
                match=ambiguous_match,
            ),
        )

        planned = import_legacy_fee_reductions(
            transaction=transaction,
            manifest=manifest,
            dry_run=True,
        )
        assert planned.counts["missing-approval"] == 1
        assert planned.counts["ambiguous-approval"] == 1
        with pytest.raises(BusinessError) as error:
            import_legacy_fee_reductions(
                transaction=transaction,
                manifest=manifest,
                dry_run=False,
                expected_plan_sha256=planned.plan_sha256,
            )
        assert error.value.status_code == 409
        assert transaction.get(Case, "case-missing").fee_reduction is None
        assert transaction.get(Case, "case-ambiguous").fee_reduction is None
        assert transaction.scalar(select(LegacyFeeReductionProvenance.id)) is None
        assert transaction.get(FeeReductionApproval, missing_approval.id) is not None


def test_changed_replay_under_the_same_identity_fails_409(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        _seed_cases(transaction, "case-replay")
        actor_id = _admin_id(transaction)
        original = _manifest(actor_id, _row("case-replay", "0"))
        planned = import_legacy_fee_reductions(
            transaction=transaction,
            manifest=original,
            dry_run=True,
        )
        import_legacy_fee_reductions(
            transaction=transaction,
            manifest=original,
            dry_run=False,
            expected_plan_sha256=planned.plan_sha256,
        )
        transaction.commit()
        provenance_id = transaction.scalar(select(LegacyFeeReductionProvenance.id))
        changed_row = _row("case-replay", "0")
        changed_row = LegacyFeeReductionMigrationRow(
            case_id=changed_row.case_id,
            legacy_value=changed_row.legacy_value,
            source_reference=changed_row.source_reference,
            source_version="changed-source-version",
            source_snapshot_hash=changed_row.source_snapshot_hash,
            approval_id=None,
        )
        changed = _manifest(actor_id, changed_row)

        changed_plan = import_legacy_fee_reductions(
            transaction=transaction,
            manifest=changed,
            dry_run=True,
        )
        assert changed_plan.rows[0].classification == "invalid"
        with pytest.raises(BusinessError) as error:
            import_legacy_fee_reductions(
                transaction=transaction,
                manifest=changed,
                dry_run=False,
                expected_plan_sha256=changed_plan.plan_sha256,
            )
        assert error.value.status_code == 409
        assert transaction.scalar(select(LegacyFeeReductionProvenance.id)) == provenance_id
