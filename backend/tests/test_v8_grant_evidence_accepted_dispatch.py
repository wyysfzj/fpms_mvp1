from __future__ import annotations

import hashlib
import json
from datetime import datetime

import pytest
from sqlalchemy import func, select

from app.core.errors import BusinessError
from app.modules.auth.models import T_User
from app.modules.cases.models import Case, CaseActivityEvent
from app.modules.documents import evidence_policy
from app.modules.documents import grant_evidence_review_service as service
from app.modules.documents.models import (
    DocAttachment,
    Document,
    DocumentEvidenceVersion,
    GrantEvidenceCandidate,
)
from app.modules.system.grant_manual_review_role_service import GrantManualReviewRoleResolution
from app.modules.system.models import GrantEvidenceSourceConfig, GrantEvidenceSourceRecord

IDS = {
    "candidate": "00000000-0000-0000-0000-000000000001",
    "case": "00000000-0000-0000-0000-000000000002",
    "document": "00000000-0000-0000-0000-000000000003",
    "evidence": "00000000-0000-0000-0000-000000000004",
    "source_config": "00000000-0000-0000-0000-000000000005",
    "source_record": "00000000-0000-0000-0000-000000000006",
    "proposer": "00000000-0000-0000-0000-000000000007",
    "reviewer": "00000000-0000-0000-0000-000000000008",
    "proposal_role_config": "00000000-0000-0000-0000-000000000009",
    "review_role_config": "00000000-0000-0000-0000-000000000010",
}
ACQUIRED_AT = datetime(2026, 8, 10, 8)
PROPOSED_AT = datetime(2026, 8, 10, 9)
REVIEWED_AT = datetime(2026, 8, 10, 10)
HASHES = {number: hashlib.sha256(str(number).encode()).hexdigest() for number in range(1, 9)}
ROLES = GrantManualReviewRoleResolution(
    gate_id="00000000-0000-0000-0000-000000000011",
    config_id=IDS["review_role_config"],
    config_snapshot_hash=HASHES[7],
    official_copy_acquirer_role_id="00000000-0000-0000-0000-000000000012",
    first_verifier_role_id="00000000-0000-0000-0000-000000000013",
    second_verifier_role_id="00000000-0000-0000-0000-000000000014",
    manual_review_proposer_role_id="00000000-0000-0000-0000-000000000015",
    manual_review_second_reviewer_role_id="00000000-0000-0000-0000-000000000016",
    effective_from=ACQUIRED_AT,
    effective_to=None,
)


def _canonical(value: object) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def _candidate(evidence_scope: str) -> GrantEvidenceCandidate:
    candidate_snapshot = _canonical(
        {
            "schema_version": "CNIPA_GRANT_EVIDENCE_CANDIDATE_V1",
            "evidence_scope": evidence_scope,
            "facts": [{"name": "status", "raw_value": "CONFIRMED"}],
            "conflicts": [],
        }
    )
    acquisition_snapshot = _canonical(
        {
            "schema_version": "CNIPA_GRANT_EVIDENCE_ACQUISITION_V2",
            "case_id": IDS["case"],
            "document_id": IDS["document"],
            "evidence_version_id": IDS["evidence"],
            "attachment_id": "00000000-0000-0000-0000-000000000017",
            "evidence_scope": evidence_scope,
            "evidence_content_hash": "official-copy-hash",
            "source_config_id": IDS["source_config"],
            "source_config_snapshot_hash": HASHES[1],
            "source_record_id": IDS["source_record"],
            "source_version": "v1",
            "source_snapshot_hash": HASHES[2],
            "original_reference": "CNIPA controlled source",
            "acquisition_method": "CONTROLLED_DOWNLOAD",
            "acquired_at": ACQUIRED_AT.isoformat(timespec="microseconds"),
            "acquired_by": "00000000-0000-0000-0000-000000000018",
            "acquisition_reason": "official copy",
            "acquisition_event_id": "00000000-0000-0000-0000-000000000019",
            "acquisition_event_snapshot_hash": HASHES[3],
            "first_verification_event_id": "00000000-0000-0000-0000-000000000020",
            "first_verification_event_snapshot_hash": HASHES[4],
            "first_verified_by": "00000000-0000-0000-0000-000000000021",
            "first_verified_at": datetime(2026, 8, 10, 8, 20).isoformat(timespec="microseconds"),
            "first_verification_reason": "first check",
            "terminal_verification_event_id": "00000000-0000-0000-0000-000000000022",
            "terminal_verification_event_snapshot_hash": HASHES[5],
            "second_verified_by": "00000000-0000-0000-0000-000000000023",
            "second_verified_at": datetime(2026, 8, 10, 8, 40).isoformat(timespec="microseconds"),
            "second_verification_reason": "second check",
            "proposal_role_config_id": IDS["proposal_role_config"],
            "proposal_role_config_snapshot_hash": HASHES[6],
            "proposed_by": IDS["proposer"],
            "proposed_at": PROPOSED_AT.isoformat(timespec="microseconds"),
        }
    )
    return GrantEvidenceCandidate(
        id=IDS["candidate"],
        case_id=IDS["case"],
        document_id=IDS["document"],
        evidence_version_id=IDS["evidence"],
        source_config_id=IDS["source_config"],
        source_record_id=IDS["source_record"],
        evidence_scope=evidence_scope,
        source_version_snapshot="v1",
        original_reference="CNIPA controlled source",
        acquisition_method_snapshot="CONTROLLED_DOWNLOAD",
        acquired_at=ACQUIRED_AT,
        acquisition_snapshot=acquisition_snapshot,
        acquisition_snapshot_hash=hashlib.sha256(acquisition_snapshot.encode()).hexdigest(),
        candidate_snapshot=candidate_snapshot,
        candidate_snapshot_hash=hashlib.sha256(candidate_snapshot.encode()).hexdigest(),
        proposed_by=IDS["proposer"],
        proposed_at=PROPOSED_AT,
        review_status="PENDING",
        reviewer_id=None,
        reviewed_at=None,
        review_reason=None,
        conflict_snapshot=None,
        created_at=PROPOSED_AT,
        updated_at=PROPOSED_AT,
    )


def _command(
    *, decision: service.GrantEvidenceReviewDecision
) -> service.ReviewGrantEvidenceCandidateCommand:
    return service.ReviewGrantEvidenceCandidateCommand(
        candidate_id=IDS["candidate"],
        decision=decision,
        reviewer_id=IDS["reviewer"],
        reviewed_at=REVIEWED_AT,
        reason="second-person review",
    )


def _arrange_review(transaction, monkeypatch, row, command, updates) -> None:
    class Changed:
        rowcount = 1

    monkeypatch.setattr(transaction, "get", lambda *_args: row)
    monkeypatch.setattr(service, "_review_authority", lambda *_args: ROLES)
    monkeypatch.setattr(service, "_ensure_sqlite_outer_transaction", lambda *_args: None)

    def execute(statement):
        assert statement.is_update
        updates.append(statement)
        row.review_status = command.decision.value
        row.reviewer_id = command.reviewer_id
        row.reviewed_at = command.reviewed_at
        row.review_reason = command.reason
        row.updated_at = command.reviewed_at
        return Changed()

    monkeypatch.setattr(transaction, "execute", execute)


def _persist_candidate(transaction, row: GrantEvidenceCandidate) -> None:
    transaction.add_all(
        (
            T_User(
                id=IDS["proposer"],
                username="dispatch-proposer",
                display_name="dispatch proposer",
                password_hash="test-only",
                is_active=True,
            ),
            T_User(
                id=IDS["reviewer"],
                username="dispatch-reviewer",
                display_name="dispatch reviewer",
                password_hash="test-only",
                is_active=True,
            ),
        )
    )
    transaction.flush()
    transaction.add(Case(id=IDS["case"], case_no="DISPATCH-ATOMICITY"))
    transaction.flush()
    transaction.add(Document(id=IDS["document"], case_id=IDS["case"]))
    transaction.flush()
    transaction.add(
        DocAttachment(
            id="00000000-0000-0000-0000-000000000017",
            document_id=IDS["document"],
            file_name="official.pdf",
            file_path="/test/official.pdf",
            content_hash="official-copy-hash",
        )
    )
    transaction.flush()
    transaction.add(
        DocumentEvidenceVersion(
            id=IDS["evidence"],
            case_id=IDS["case"],
            document_id=IDS["document"],
            attachment_id="00000000-0000-0000-0000-000000000017",
            lineage_key="grant-official-copy",
            role="RAW_ATTACHMENT",
            version_number=1,
            state="FINAL",
            creator_id=IDS["proposer"],
            review_state="PENDING",
            reviewer_id=None,
            reviewed_at=None,
            final_submitted_at=None,
            content_hash="official-copy-hash",
            current_identity_key=f"{IDS['case']}|grant-official-copy",
        )
    )
    transaction.flush()
    source_snapshot = _canonical({"source": "controlled"})
    transaction.add(
        GrantEvidenceSourceRecord(
            id=IDS["source_record"],
            source_authority="CNIPA",
            source_code="DISPATCH-ATOMICITY",
            source_version="v1",
            evidence_scope=row.evidence_scope,
            source_reference_kind="DATA",
            source_reference_value="CNIPA controlled source",
            acquisition_method="CONTROLLED_DOWNLOAD",
            effective_from=ACQUIRED_AT,
            effective_to=None,
            source_snapshot=source_snapshot,
            source_snapshot_hash=hashlib.sha256(source_snapshot.encode()).hexdigest(),
            review_status="PENDING",
            reviewed_by=None,
            reviewed_at=None,
            review_reason=None,
            activation_status="INACTIVE",
            activated_by=None,
            activated_at=None,
            supersedes_source_id=None,
            current_identity_key=None,
            idempotency_key="dispatch-source",
            created_by=IDS["proposer"],
            updated_by=IDS["proposer"],
        )
    )
    transaction.flush()
    config_snapshot = _canonical({"config": "controlled"})
    transaction.add(
        GrantEvidenceSourceConfig(
            id=IDS["source_config"],
            gate_code="DG-GRANT-EVIDENCE-SOURCE",
            scope_key="GLOBAL",
            evidence_scope=row.evidence_scope,
            source_record_id=IDS["source_record"],
            config_version="v1",
            config_status="ACTIVE",
            effective_from=ACQUIRED_AT,
            effective_to=None,
            selected_by=IDS["proposer"],
            published_at=ACQUIRED_AT,
            selection_reason="controlled test source",
            supersedes_config_id=None,
            config_snapshot=config_snapshot,
            config_snapshot_hash=hashlib.sha256(config_snapshot.encode()).hexdigest(),
            idempotency_key="dispatch-config",
            current_identity_key=None,
        )
    )
    transaction.flush()
    transaction.add(row)
    transaction.commit()


@pytest.mark.parametrize(
    ("evidence_scope", "expected_adapter"),
    (
        ("GRANT_ANNOUNCEMENT", "announcement"),
        ("PATENT_REGISTER", "register"),
    ),
)
def test_changed_approval_dispatches_exact_adapter_once_and_replay_does_not_redispatch(
    session_factory, monkeypatch, evidence_scope, expected_adapter
) -> None:
    row = _candidate(evidence_scope)
    command = _command(decision=service.GrantEvidenceReviewDecision.APPROVED)
    updates: list[object] = []
    calls: list[tuple[str, object, str, str, object]] = []

    def capture(name):
        def apply(
            candidate, *, review_role_config_id, review_role_config_snapshot_hash, transaction
        ):
            calls.append(
                (
                    name,
                    candidate,
                    review_role_config_id,
                    review_role_config_snapshot_hash,
                    transaction,
                )
            )
            return "transition"

        return apply

    monkeypatch.setattr(
        evidence_policy, "apply_grant_announcement_evidence", capture("announcement")
    )
    monkeypatch.setattr(evidence_policy, "apply_patent_register_evidence", capture("register"))
    with session_factory() as transaction:
        _arrange_review(transaction, monkeypatch, row, command, updates)
        changed = service.review_grant_evidence_candidate(command, transaction)
        reused = service.review_grant_evidence_candidate(command, transaction)
    assert changed.disposition is service.GrantEvidenceReviewDisposition.CHANGED
    assert reused.disposition is service.GrantEvidenceReviewDisposition.REUSED
    assert len(updates) == 1
    assert calls == [
        (
            expected_adapter,
            row,
            IDS["review_role_config"],
            HASHES[7],
            transaction,
        )
    ]


def test_rejection_updates_review_without_dispatch(session_factory, monkeypatch) -> None:
    row = _candidate("GRANT_ANNOUNCEMENT")
    command = _command(decision=service.GrantEvidenceReviewDecision.REJECTED)
    updates: list[object] = []
    calls: list[str] = []
    monkeypatch.setattr(
        evidence_policy,
        "apply_grant_announcement_evidence",
        lambda *_args, **_kwargs: calls.append("announcement"),
    )
    monkeypatch.setattr(
        evidence_policy,
        "apply_patent_register_evidence",
        lambda *_args, **_kwargs: calls.append("register"),
    )
    with session_factory() as transaction:
        _arrange_review(transaction, monkeypatch, row, command, updates)
        result = service.review_grant_evidence_candidate(command, transaction)
    assert result.review_status == "REJECTED"
    assert len(updates) == 1
    assert calls == []


def test_approved_conflicting_candidate_preserves_review_without_dispatch(
    session_factory, monkeypatch
) -> None:
    row = _candidate("GRANT_ANNOUNCEMENT")
    payload = json.loads(row.candidate_snapshot)
    payload["conflicts"] = [{"name": "status", "raw_values": ["CONFIRMED", "CONFLICT"]}]
    row.candidate_snapshot = _canonical(payload)
    row.candidate_snapshot_hash = hashlib.sha256(row.candidate_snapshot.encode()).hexdigest()
    row.conflict_snapshot = _canonical(payload["conflicts"])
    command = _command(decision=service.GrantEvidenceReviewDecision.APPROVED)
    updates: list[object] = []
    calls: list[str] = []
    monkeypatch.setattr(
        evidence_policy,
        "apply_grant_announcement_evidence",
        lambda *_args, **_kwargs: calls.append("announcement"),
    )
    monkeypatch.setattr(
        evidence_policy,
        "apply_patent_register_evidence",
        lambda *_args, **_kwargs: calls.append("register"),
    )
    with session_factory() as transaction:
        _arrange_review(transaction, monkeypatch, row, command, updates)
        result = service.review_grant_evidence_candidate(command, transaction)
    assert result.review_status == "APPROVED"
    assert len(updates) == 1
    assert calls == []


def test_review_conflict_fails_before_update_or_dispatch(session_factory, monkeypatch) -> None:
    row = _candidate("PATENT_REGISTER")
    command = service.ReviewGrantEvidenceCandidateCommand(
        candidate_id=IDS["candidate"],
        decision=service.GrantEvidenceReviewDecision.APPROVED,
        reviewer_id=IDS["proposer"],
        reviewed_at=REVIEWED_AT,
        reason="self review",
    )
    updates: list[object] = []
    calls: list[str] = []
    monkeypatch.setattr(
        evidence_policy,
        "apply_grant_announcement_evidence",
        lambda *_args, **_kwargs: calls.append("announcement"),
    )
    monkeypatch.setattr(
        evidence_policy,
        "apply_patent_register_evidence",
        lambda *_args, **_kwargs: calls.append("register"),
    )
    with session_factory() as transaction:
        _arrange_review(transaction, monkeypatch, row, command, updates)
        with pytest.raises(BusinessError) as caught:
            service.review_grant_evidence_candidate(command, transaction)
    assert (caught.value.code, caught.value.status_code) == (
        "GRANT_EVIDENCE_REVIEW_CONFLICT",
        409,
    )
    assert updates == []
    assert calls == []


def test_adapter_conflict_rolls_back_review_savepoint_but_not_outer_transaction(
    session_factory, monkeypatch
) -> None:
    row = _candidate("GRANT_ANNOUNCEMENT")
    controlled_error = BusinessError(
        "GRANT_ANNOUNCEMENT_EVIDENCE_CONFLICT",
        "source unavailable",
        status_code=409,
    )
    adapter_transactions: list[object] = []
    outer_calls: list[str] = []
    marker_id = "00000000-0000-0000-0000-000000000024"

    def fail_adapter(_candidate, *, transaction, **_kwargs):
        adapter_transactions.append(transaction)
        raise controlled_error

    monkeypatch.setattr(evidence_policy, "apply_grant_announcement_evidence", fail_adapter)
    monkeypatch.setattr(service, "_review_authority", lambda *_args: ROLES)
    with session_factory() as transaction:
        _persist_candidate(transaction, row)
        transaction.add(
            T_User(
                id=marker_id,
                username="outer-marker",
                display_name="outer marker",
                password_hash="test-only",
                is_active=True,
            )
        )
        transaction.flush()
        original_commit = transaction.commit
        original_rollback = transaction.rollback

        def commit() -> None:
            outer_calls.append("commit")
            original_commit()

        def rollback() -> None:
            outer_calls.append("rollback")
            original_rollback()

        monkeypatch.setattr(transaction, "commit", commit)
        monkeypatch.setattr(transaction, "rollback", rollback)
        with pytest.raises(BusinessError) as caught:
            service.review_grant_evidence_candidate(
                _command(decision=service.GrantEvidenceReviewDecision.APPROVED),
                transaction,
            )
        assert caught.value is controlled_error
        assert adapter_transactions == [transaction]
        assert outer_calls == []
        transaction.commit()
        assert outer_calls == ["commit"]

    with session_factory() as transaction:
        persisted = transaction.get(GrantEvidenceCandidate, IDS["candidate"])
        assert (
            persisted.review_status,
            persisted.reviewer_id,
            persisted.reviewed_at,
            persisted.review_reason,
        ) == ("PENDING", None, None, None)
        assert transaction.get(T_User, marker_id) is not None
        assert transaction.scalar(select(func.count()).select_from(CaseActivityEvent)) == 0
