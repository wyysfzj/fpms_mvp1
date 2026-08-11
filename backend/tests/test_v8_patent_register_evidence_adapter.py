from __future__ import annotations

import hashlib
import json
from dataclasses import replace
from datetime import datetime

import pytest

from app.core.errors import BusinessError
from app.modules.cases.lifecycle_contracts import ActivityLane, ConfirmationStatus
from app.modules.documents import evidence_policy as adapter
from app.modules.documents.models import GrantEvidenceCandidate
from app.modules.system.grant_evidence_source_service import (
    GrantEvidenceScope,
    GrantEvidenceSourceReferenceKind,
    GrantEvidenceSourceResolution,
)
from app.modules.system.grant_manual_review_role_service import GrantManualReviewRoleResolution

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
    "proposal_role": "00000000-0000-0000-0000-000000000011",
    "review_role": "00000000-0000-0000-0000-000000000012",
}
ACQUIRED_AT = datetime(2026, 8, 10, 8)
PROPOSED_AT = datetime(2026, 8, 10, 9)
REVIEWED_AT = datetime(2026, 8, 10, 10)
OBSERVED_AT = datetime(2026, 8, 10, 7, 30)
EVIDENCE_HASH = f"sha256:{'b' * 64}"
HASHES = {number: hashlib.sha256(str(number).encode()).hexdigest() for number in range(1, 9)}


def _canonical(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _candidate(*, register_status: str = "PATENT_IN_FORCE") -> GrantEvidenceCandidate:
    candidate_snapshot = _canonical(
        {
            "schema_version": "CNIPA_GRANT_EVIDENCE_CANDIDATE_V1",
            "evidence_scope": "PATENT_REGISTER",
            "facts": [
                {
                    "name": "observed_at",
                    "raw_value": OBSERVED_AT.isoformat(timespec="microseconds"),
                },
                {"name": "register_status", "raw_value": register_status},
            ],
            "conflicts": [],
        }
    )
    acquisition_snapshot = _canonical(
        {
            "schema_version": "CNIPA_GRANT_EVIDENCE_ACQUISITION_V2",
            "case_id": IDS["case"],
            "document_id": IDS["document"],
            "evidence_version_id": IDS["evidence"],
            "attachment_id": "00000000-0000-0000-0000-000000000013",
            "evidence_scope": "PATENT_REGISTER",
            "evidence_content_hash": EVIDENCE_HASH,
            "source_config_id": IDS["source_config"],
            "source_config_snapshot_hash": HASHES[1],
            "source_record_id": IDS["source_record"],
            "source_version": "v1",
            "source_snapshot_hash": HASHES[2],
            "original_reference": "CNIPA controlled register source",
            "acquisition_method": "CONTROLLED_DOWNLOAD",
            "acquired_at": ACQUIRED_AT.isoformat(timespec="microseconds"),
            "acquired_by": "00000000-0000-0000-0000-000000000014",
            "acquisition_reason": "official copy",
            "acquisition_event_id": "00000000-0000-0000-0000-000000000015",
            "acquisition_event_snapshot_hash": HASHES[3],
            "first_verification_event_id": "00000000-0000-0000-0000-000000000016",
            "first_verification_event_snapshot_hash": HASHES[4],
            "first_verified_by": "00000000-0000-0000-0000-000000000017",
            "first_verified_at": datetime(2026, 8, 10, 8, 20).isoformat(timespec="microseconds"),
            "first_verification_reason": "first check",
            "terminal_verification_event_id": "00000000-0000-0000-0000-000000000018",
            "terminal_verification_event_snapshot_hash": HASHES[5],
            "second_verified_by": "00000000-0000-0000-0000-000000000019",
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
        evidence_scope="PATENT_REGISTER",
        source_version_snapshot="v1",
        original_reference="CNIPA controlled register source",
        acquisition_method_snapshot="CONTROLLED_DOWNLOAD",
        acquired_at=ACQUIRED_AT,
        acquisition_snapshot=acquisition_snapshot,
        acquisition_snapshot_hash=hashlib.sha256(acquisition_snapshot.encode()).hexdigest(),
        candidate_snapshot=candidate_snapshot,
        candidate_snapshot_hash=hashlib.sha256(candidate_snapshot.encode()).hexdigest(),
        proposed_by=IDS["proposer"],
        proposed_at=PROPOSED_AT,
        review_status="APPROVED",
        reviewer_id=IDS["reviewer"],
        reviewed_at=REVIEWED_AT,
        review_reason="second-person approval",
        conflict_snapshot=None,
        created_at=PROPOSED_AT,
        updated_at=REVIEWED_AT,
    )


def _source_resolution() -> GrantEvidenceSourceResolution:
    return GrantEvidenceSourceResolution(
        gate_id="00000000-0000-0000-0000-000000000020",
        config_id=IDS["source_config"],
        config_snapshot_hash=HASHES[1],
        source_record_id=IDS["source_record"],
        evidence_scope=GrantEvidenceScope.PATENT_REGISTER,
        source_code="CNIPA-REGISTER",
        source_version="v1",
        source_snapshot_hash=HASHES[2],
        source_reference_kind=GrantEvidenceSourceReferenceKind.DATA,
        source_reference_value="CNIPA controlled register source",
        acquisition_method="CONTROLLED_DOWNLOAD",
        effective_from=ACQUIRED_AT,
        effective_to=None,
    )


def _role_resolution(*, review: bool) -> GrantManualReviewRoleResolution:
    return GrantManualReviewRoleResolution(
        gate_id="00000000-0000-0000-0000-000000000021",
        config_id=IDS["review_role_config"] if review else IDS["proposal_role_config"],
        config_snapshot_hash=HASHES[7] if review else HASHES[6],
        official_copy_acquirer_role_id="00000000-0000-0000-0000-000000000022",
        first_verifier_role_id="00000000-0000-0000-0000-000000000023",
        second_verifier_role_id="00000000-0000-0000-0000-000000000024",
        manual_review_proposer_role_id=IDS["proposal_role"],
        manual_review_second_reviewer_role_id=IDS["review_role"],
        effective_from=ACQUIRED_AT,
        effective_to=None,
    )


def _arrange(monkeypatch, captured: list[object]) -> None:
    monkeypatch.setattr(
        adapter, "resolve_grant_evidence_source", lambda *_args: _source_resolution()
    )
    monkeypatch.setattr(
        adapter,
        "resolve_grant_manual_review_role_config",
        lambda command, _transaction: _role_resolution(review=command.as_of == REVIEWED_AT),
    )
    monkeypatch.setattr(adapter, "_active_role_member", lambda *_args: True)

    def apply(command, _transaction):
        captured.append(command)
        return "transition"

    monkeypatch.setattr(adapter, "apply_lifecycle_event", apply)


def _assert_conflict(call) -> None:
    with pytest.raises(BusinessError) as caught:
        call()
    assert (caught.value.code, caught.value.status_code) == (
        "PATENT_REGISTER_EVIDENCE_CONFLICT",
        409,
    )


def test_in_force_register_candidate_maps_once_to_generic_register_event(
    session_factory, monkeypatch
) -> None:
    captured: list[object] = []
    _arrange(monkeypatch, captured)
    row = _candidate()
    review_state = (row.review_status, row.reviewer_id, row.reviewed_at)
    with session_factory() as transaction:
        result = adapter.apply_patent_register_evidence(
            row,
            review_role_config_id=IDS["review_role_config"],
            review_role_config_snapshot_hash=HASHES[7],
            transaction=transaction,
        )
    assert result == "transition"
    assert len(captured) == 1
    command = captured[0]
    assert command.event_type == "PATENT_REGISTER_STATUS_CONFIRMED"
    assert command.lane is ActivityLane.LIFECYCLE
    assert command.confirmation_status is ConfirmationStatus.CONFIRMED
    assert command.effective_at == OBSERVED_AT
    assert command.occurred_at == REVIEWED_AT
    assert command.actor_id == IDS["proposer"]
    assert command.reviewer_id == IDS["reviewer"]
    assert command.idempotency_key == f"patent-register-status:{IDS['candidate']}"
    assert command.supersedes_event_id is None
    assert command.evidence_refs[0].object_id == IDS["evidence"]
    assert command.evidence_refs[0].content_hash == EVIDENCE_HASH
    assert command.evidence_refs[0].evidence_kind == "DOCUMENT_EVIDENCE_VERSION"
    assert command.payload["register_status"] == "PATENT_IN_FORCE"
    assert command.payload["source_provenance_id"] == IDS["candidate"]
    assert command.payload["predecessor_status_snapshot_hash"] is None
    assert command.payload["supersedes_activity_id"] is None
    assert (
        command.payload["status_snapshot_hash"]
        == hashlib.sha256(command.payload["status_snapshot"].encode()).hexdigest()
    )
    assert (row.review_status, row.reviewer_id, row.reviewed_at) == review_state


@pytest.mark.parametrize(
    ("register_status", "event_type", "idempotency_prefix"),
    (
        ("PATENT_TERMINATED", "PATENT_TERMINATION_CONFIRMED", "patent-termination:"),
        ("PATENT_EXPIRED", "PATENT_EXPIRY_CONFIRMED", "patent-expiry:"),
    ),
)
def test_terminal_register_candidate_maps_once_to_specific_status_change_event(
    session_factory,
    monkeypatch,
    register_status,
    event_type,
    idempotency_prefix,
) -> None:
    captured: list[object] = []
    _arrange(monkeypatch, captured)
    with session_factory() as transaction:
        result = adapter.apply_patent_register_evidence(
            _candidate(register_status=register_status),
            review_role_config_id=IDS["review_role_config"],
            review_role_config_snapshot_hash=HASHES[7],
            transaction=transaction,
        )
    assert result == "transition"
    assert len(captured) == 1
    command = captured[0]
    assert command.event_type == event_type
    assert command.lane is ActivityLane.LIFECYCLE
    assert command.confirmation_status is ConfirmationStatus.CONFIRMED
    assert command.effective_at == OBSERVED_AT
    assert command.occurred_at == REVIEWED_AT
    assert command.actor_id == IDS["proposer"]
    assert command.reviewer_id == IDS["reviewer"]
    assert command.idempotency_key == f"{idempotency_prefix}{IDS['candidate']}"
    assert command.payload == {}
    assert command.supersedes_event_id is None
    assert len(command.evidence_refs) == 1
    assert command.evidence_refs[0].evidence_kind == "PATENT_REGISTER_STATUS_EVIDENCE"
    assert command.evidence_refs[0].object_id == IDS["evidence"]
    assert command.evidence_refs[0].content_hash == EVIDENCE_HASH


def test_invalidated_register_candidate_without_effective_decision_fails_before_dispatch(
    session_factory, monkeypatch
) -> None:
    captured: list[object] = []
    _arrange(monkeypatch, captured)
    with session_factory() as transaction:
        _assert_conflict(
            lambda: adapter.apply_patent_register_evidence(
                _candidate(register_status="PATENT_INVALIDATED"),
                review_role_config_id=IDS["review_role_config"],
                review_role_config_snapshot_hash=HASHES[7],
                transaction=transaction,
            )
        )
    assert captured == []


@pytest.mark.parametrize(
    "mutate",
    (
        lambda row: setattr(row, "review_status", "REJECTED"),
        lambda row: setattr(row, "evidence_scope", "GRANT_ANNOUNCEMENT"),
        lambda row: setattr(row, "reviewer_id", row.proposed_by),
        lambda row: setattr(row, "candidate_snapshot_hash", "0" * 64),
    ),
)
def test_invalid_or_unaccepted_candidate_fails_before_dispatch(
    session_factory, monkeypatch, mutate
) -> None:
    captured: list[object] = []
    _arrange(monkeypatch, captured)
    row = _candidate()
    mutate(row)
    with session_factory() as transaction:
        _assert_conflict(
            lambda: adapter.apply_patent_register_evidence(
                row,
                review_role_config_id=IDS["review_role_config"],
                review_role_config_snapshot_hash=HASHES[7],
                transaction=transaction,
            )
        )
    assert captured == []


@pytest.mark.parametrize(
    "failure",
    (
        "source_absent",
        "source_revoked",
        "source_future",
        "source_scope_mismatch",
        "role_absent",
        "role_revoked",
        "role_future",
    ),
)
def test_unavailable_or_mismatched_authority_fails_before_dispatch(
    session_factory, monkeypatch, failure
) -> None:
    captured: list[object] = []
    _arrange(monkeypatch, captured)

    def unavailable(*_args):
        raise BusinessError(failure.upper(), "authority unavailable", status_code=409)

    if failure == "source_scope_mismatch":
        monkeypatch.setattr(
            adapter,
            "resolve_grant_evidence_source",
            lambda *_args: replace(
                _source_resolution(),
                evidence_scope=GrantEvidenceScope.GRANT_ANNOUNCEMENT,
            ),
        )
    elif failure.startswith("source_"):
        monkeypatch.setattr(adapter, "resolve_grant_evidence_source", unavailable)
    else:
        monkeypatch.setattr(adapter, "resolve_grant_manual_review_role_config", unavailable)
    with session_factory() as transaction:
        _assert_conflict(
            lambda: adapter.apply_patent_register_evidence(
                _candidate(),
                review_role_config_id=IDS["review_role_config"],
                review_role_config_snapshot_hash=HASHES[7],
                transaction=transaction,
            )
        )
    assert captured == []


def test_authority_identity_mismatch_fails_before_dispatch(session_factory, monkeypatch) -> None:
    captured: list[object] = []
    _arrange(monkeypatch, captured)
    with session_factory() as transaction:
        _assert_conflict(
            lambda: adapter.apply_patent_register_evidence(
                _candidate(),
                review_role_config_id=IDS["proposal_role_config"],
                review_role_config_snapshot_hash=HASHES[7],
                transaction=transaction,
            )
        )
    assert captured == []
