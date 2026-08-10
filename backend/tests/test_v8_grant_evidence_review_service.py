from __future__ import annotations

import hashlib
import inspect
import json
from dataclasses import FrozenInstanceError, fields, is_dataclass, replace
from datetime import datetime, timedelta, timezone
from typing import get_type_hints
from uuid import uuid4

import pytest
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import BusinessError
from app.modules.auth.models import T_Role, T_User, T_UserRole
from app.modules.cases.models import Case, CaseActivityEvent
from app.modules.documents import grant_evidence_review_service as service
from app.modules.documents.models import (
    DocAttachment,
    Document,
    DocumentEvidenceVersion,
    GrantEvidenceCandidate,
)
from app.modules.system.grant_manual_review_role_service import GrantManualReviewRoleResolution
from app.modules.system.models import GrantEvidenceSourceConfig, GrantEvidenceSourceRecord

ACQUIRED_AT = datetime(2026, 8, 10, 9, 0, 0, 123456)
PROPOSED_AT = datetime(2026, 8, 10, 12, 0, 0, 123456)
REVIEWED_AT = datetime(2026, 8, 10, 13, 0, 0, 123456)


def _canonical(value: object) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def _hash(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def _user(transaction: Session, label: str, *, active: bool = True) -> str:
    user_id = str(uuid4())
    transaction.add(
        T_User(
            id=user_id,
            username=f"{label}-{uuid4()}",
            display_name=label,
            password_hash="test-only",
            is_active=active,
        )
    )
    return user_id


def _ready(transaction: Session, monkeypatch: pytest.MonkeyPatch) -> dict[str, object]:
    admin_id = _user(transaction, "admin")
    proposer_id = _user(transaction, "proposer")
    reviewer_id = _user(transaction, "reviewer")
    reviewer_role_id = str(uuid4())
    transaction.add(
        T_Role(id=reviewer_role_id, code=f"grant-reviewer-{uuid4()}", name="grant reviewer")
    )
    transaction.add(T_UserRole(user_id=reviewer_id, role_id=reviewer_role_id))
    transaction.flush()

    case_id = str(uuid4())
    document_id = str(uuid4())
    attachment_id = str(uuid4())
    evidence_id = str(uuid4())
    source_record_id = str(uuid4())
    source_config_id = str(uuid4())
    candidate_id = str(uuid4())
    transaction.add(Case(id=case_id, case_no=f"REVIEW-{uuid4()}"))
    transaction.flush()
    transaction.add(Document(id=document_id, case_id=case_id))
    transaction.flush()
    transaction.add(
        DocAttachment(
            id=attachment_id,
            document_id=document_id,
            file_name="grant.pdf",
            file_path="/test/grant.pdf",
            content_hash="official-copy-hash",
        )
    )
    transaction.flush()
    transaction.add(
        DocumentEvidenceVersion(
            id=evidence_id,
            case_id=case_id,
            document_id=document_id,
            attachment_id=attachment_id,
            lineage_key="grant-official-copy",
            role="RAW_ATTACHMENT",
            version_number=1,
            state="FINAL",
            creator_id=admin_id,
            review_state="PENDING",
            reviewer_id=None,
            reviewed_at=None,
            final_submitted_at=None,
            content_hash="official-copy-hash",
            current_identity_key=f"{case_id}|grant-official-copy",
        )
    )
    transaction.flush()

    source_snapshot = _canonical({"source": "test"})
    transaction.add(
        GrantEvidenceSourceRecord(
            id=source_record_id,
            source_authority="CNIPA",
            source_code=f"REVIEW-{uuid4()}",
            source_version="v1",
            evidence_scope="GRANT_ANNOUNCEMENT",
            source_reference_kind="DATA",
            source_reference_value="TEST",
            acquisition_method="CONTROLLED_DOWNLOAD",
            effective_from=ACQUIRED_AT - timedelta(days=1),
            effective_to=None,
            source_snapshot=source_snapshot,
            source_snapshot_hash=_hash(source_snapshot),
            review_status="PENDING",
            reviewed_by=None,
            reviewed_at=None,
            review_reason=None,
            activation_status="INACTIVE",
            activated_by=None,
            activated_at=None,
            supersedes_source_id=None,
            current_identity_key=None,
            idempotency_key=f"source-{uuid4()}",
            created_by=admin_id,
            updated_by=admin_id,
        )
    )
    transaction.flush()
    config_snapshot = _canonical({"config": "test"})
    transaction.add(
        GrantEvidenceSourceConfig(
            id=source_config_id,
            gate_code="DG-GRANT-EVIDENCE-SOURCE",
            scope_key="GLOBAL",
            evidence_scope="GRANT_ANNOUNCEMENT",
            source_record_id=source_record_id,
            config_version=f"v1-{uuid4()}",
            config_status="ACTIVE",
            effective_from=ACQUIRED_AT - timedelta(days=1),
            effective_to=None,
            selected_by=admin_id,
            published_at=ACQUIRED_AT - timedelta(hours=1),
            selection_reason="TEST",
            supersedes_config_id=None,
            config_snapshot=config_snapshot,
            config_snapshot_hash=_hash(config_snapshot),
            idempotency_key=f"config-{uuid4()}",
            current_identity_key=None,
        )
    )
    transaction.flush()

    candidate_snapshot = _canonical(
        {
            "conflicts": [{"name": "status", "raw_values": ["公告：授权", "登记簿：待确认"]}],
            "evidence_scope": "GRANT_ANNOUNCEMENT",
            "facts": [
                {"name": "grant_number", "raw_value": "CN-TEST-001"},
                {"name": "status", "raw_value": "公告：授权"},
            ],
            "schema_version": "CNIPA_GRANT_EVIDENCE_CANDIDATE_V1",
        }
    )
    conflict_snapshot = _canonical(json.loads(candidate_snapshot)["conflicts"])
    acquisition_snapshot = _canonical(
        {
            "acquired_at": ACQUIRED_AT.isoformat(timespec="microseconds"),
            "acquired_by": admin_id,
            "acquisition_event_id": str(uuid4()),
            "acquisition_event_snapshot_hash": "1" * 64,
            "acquisition_method": "CONTROLLED_DOWNLOAD",
            "acquisition_reason": "TEST ACQUIRE",
            "attachment_id": attachment_id,
            "case_id": case_id,
            "document_id": document_id,
            "evidence_content_hash": "official-copy-hash",
            "evidence_scope": "GRANT_ANNOUNCEMENT",
            "evidence_version_id": evidence_id,
            "first_verification_event_id": str(uuid4()),
            "first_verification_event_snapshot_hash": "2" * 64,
            "first_verification_reason": "TEST FIRST",
            "first_verified_at": (ACQUIRED_AT + timedelta(minutes=1)).isoformat(
                timespec="microseconds"
            ),
            "first_verified_by": str(uuid4()),
            "original_reference": "CNIPA-TEST-REFERENCE",
            "proposal_role_config_id": str(uuid4()),
            "proposal_role_config_snapshot_hash": "3" * 64,
            "proposed_at": PROPOSED_AT.isoformat(timespec="microseconds"),
            "proposed_by": proposer_id,
            "schema_version": "CNIPA_GRANT_EVIDENCE_ACQUISITION_V2",
            "second_verification_reason": "TEST SECOND",
            "second_verified_at": (ACQUIRED_AT + timedelta(minutes=2)).isoformat(
                timespec="microseconds"
            ),
            "second_verified_by": str(uuid4()),
            "source_config_id": source_config_id,
            "source_config_snapshot_hash": "4" * 64,
            "source_record_id": source_record_id,
            "source_snapshot_hash": "5" * 64,
            "source_version": "v1",
            "terminal_verification_event_id": str(uuid4()),
            "terminal_verification_event_snapshot_hash": "6" * 64,
        }
    )
    transaction.add(
        GrantEvidenceCandidate(
            id=candidate_id,
            case_id=case_id,
            document_id=document_id,
            evidence_version_id=evidence_id,
            source_config_id=source_config_id,
            source_record_id=source_record_id,
            evidence_scope="GRANT_ANNOUNCEMENT",
            source_version_snapshot="v1",
            original_reference="CNIPA-TEST-REFERENCE",
            acquisition_method_snapshot="CONTROLLED_DOWNLOAD",
            acquired_at=ACQUIRED_AT,
            acquisition_snapshot=acquisition_snapshot,
            acquisition_snapshot_hash=_hash(acquisition_snapshot),
            candidate_snapshot=candidate_snapshot,
            candidate_snapshot_hash=_hash(candidate_snapshot),
            proposed_by=proposer_id,
            proposed_at=PROPOSED_AT,
            review_status="PENDING",
            reviewer_id=None,
            reviewed_at=None,
            review_reason=None,
            conflict_snapshot=conflict_snapshot,
        )
    )
    transaction.commit()

    role_resolution = GrantManualReviewRoleResolution(
        gate_id=str(uuid4()),
        config_id=str(uuid4()),
        config_snapshot_hash="a" * 64,
        official_copy_acquirer_role_id=str(uuid4()),
        first_verifier_role_id=str(uuid4()),
        second_verifier_role_id=str(uuid4()),
        manual_review_proposer_role_id=str(uuid4()),
        manual_review_second_reviewer_role_id=reviewer_role_id,
        effective_from=ACQUIRED_AT - timedelta(days=1),
        effective_to=None,
    )
    monkeypatch.setattr(
        service,
        "resolve_grant_manual_review_role_config",
        lambda command, _transaction: (
            role_resolution if command.as_of == REVIEWED_AT else pytest.fail("wrong as_of")
        ),
    )
    return {
        "candidate_id": candidate_id,
        "case_id": case_id,
        "reviewer_id": reviewer_id,
        "reviewer_role_id": reviewer_role_id,
        "proposer_id": proposer_id,
        "candidate_snapshot": candidate_snapshot,
        "conflict_snapshot": conflict_snapshot,
        "acquisition_snapshot": acquisition_snapshot,
        "roles": role_resolution,
    }


def _command(ready: dict[str, object], **changes: object):
    values: dict[str, object] = {
        "candidate_id": ready["candidate_id"],
        "decision": service.GrantEvidenceReviewDecision.APPROVED,
        "reviewer_id": ready["reviewer_id"],
        "reviewed_at": REVIEWED_AT,
        "reason": "双人复核完成，保留原始冲突。",
    }
    values.update(changes)
    return service.ReviewGrantEvidenceCandidateCommand(**values)


def _assert_error(call, *, code: str, status: int) -> BusinessError:
    with pytest.raises(BusinessError) as caught:
        call()
    assert caught.value.code == code
    assert caught.value.status_code == status
    return caught.value


def test_public_contract_is_exact_frozen_keyword_only_and_synchronous() -> None:
    dto_fields = {
        service.ReviewGrantEvidenceCandidateCommand: (
            "candidate_id",
            "decision",
            "reviewer_id",
            "reviewed_at",
            "reason",
        ),
        service.ReviewGrantEvidenceCandidateResult: (
            "candidate_id",
            "evidence_version_id",
            "review_status",
            "reviewer_id",
            "reviewed_at",
            "candidate_snapshot_hash",
            "review_role_config_id",
            "review_role_config_snapshot_hash",
            "disposition",
        ),
    }
    for dto, expected in dto_fields.items():
        assert is_dataclass(dto)
        assert dto.__dataclass_params__.frozen is True
        assert dto.__slots__ == expected
        assert tuple(field.name for field in fields(dto)) == expected
        assert all(
            parameter.kind is inspect.Parameter.KEYWORD_ONLY
            for parameter in inspect.signature(dto).parameters.values()
        )
    function = service.review_grant_evidence_candidate
    assert tuple(inspect.signature(function).parameters) == ("command", "transaction")
    assert get_type_hints(function)["transaction"] is Session
    assert inspect.iscoroutinefunction(function) is False
    command = service.ReviewGrantEvidenceCandidateCommand(
        candidate_id=str(uuid4()),
        decision=service.GrantEvidenceReviewDecision.REJECTED,
        reviewer_id=str(uuid4()),
        reviewed_at=REVIEWED_AT,
        reason="TEST",
    )
    with pytest.raises(FrozenInstanceError):
        command.reason = "changed"


@pytest.mark.parametrize(
    "decision",
    (service.GrantEvidenceReviewDecision.APPROVED, service.GrantEvidenceReviewDecision.REJECTED),
)
def test_decision_preserves_raw_evidence_and_has_no_adjacent_side_effects(
    session_factory, monkeypatch, decision
) -> None:
    with session_factory() as transaction:
        ready = _ready(transaction, monkeypatch)
        row = transaction.get(GrantEvidenceCandidate, ready["candidate_id"])
        case = transaction.get(Case, ready["case_id"])
        before_case = (case.status, case.legal_status, case.lifecycle_revision)
        before_immutable = (
            row.acquisition_snapshot,
            row.acquisition_snapshot_hash,
            row.candidate_snapshot,
            row.candidate_snapshot_hash,
            row.conflict_snapshot,
            row.proposed_by,
            row.proposed_at,
        )
        result = service.review_grant_evidence_candidate(
            _command(ready, decision=decision), transaction
        )
        assert result.review_status == decision.value
        assert result.disposition is service.GrantEvidenceReviewDisposition.CHANGED
        assert result.review_role_config_id == ready["roles"].config_id
        transaction.expire_all()
        row = transaction.get(GrantEvidenceCandidate, ready["candidate_id"])
        assert (row.review_status, row.reviewer_id, row.reviewed_at, row.review_reason) == (
            decision.value,
            ready["reviewer_id"],
            REVIEWED_AT,
            "双人复核完成，保留原始冲突。",
        )
        assert (
            row.acquisition_snapshot,
            row.acquisition_snapshot_hash,
            row.candidate_snapshot,
            row.candidate_snapshot_hash,
            row.conflict_snapshot,
            row.proposed_by,
            row.proposed_at,
        ) == before_immutable
        assert json.loads(row.conflict_snapshot) == [
            {"name": "status", "raw_values": ["公告：授权", "登记簿：待确认"]}
        ]
        case = transaction.get(Case, ready["case_id"])
        assert (case.status, case.legal_status, case.lifecycle_revision) == before_case
        assert transaction.scalar(select(func.count()).select_from(CaseActivityEvent)) == 0
        transaction.rollback()
    with session_factory() as transaction:
        row = transaction.get(GrantEvidenceCandidate, ready["candidate_id"])
        assert (row.review_status, row.reviewer_id, row.reviewed_at, row.review_reason) == (
            "PENDING",
            None,
            None,
            None,
        )


def test_exact_terminal_replay_reuses_but_changed_repeat_conflicts(
    session_factory, monkeypatch
) -> None:
    with session_factory() as transaction:
        ready = _ready(transaction, monkeypatch)
        command = _command(ready)
        changed = service.review_grant_evidence_candidate(command, transaction)
        transaction.commit()
        reused = service.review_grant_evidence_candidate(command, transaction)
        assert reused == replace(
            changed,
            disposition=service.GrantEvidenceReviewDisposition.REUSED,
        )
        _assert_error(
            lambda: service.review_grant_evidence_candidate(
                replace(command, reason="changed"), transaction
            ),
            code="GRANT_EVIDENCE_REVIEW_CONFLICT",
            status=409,
        )


def test_self_unbound_and_inactive_reviewers_fail_without_write(
    session_factory, monkeypatch
) -> None:
    with session_factory() as transaction:
        ready = _ready(transaction, monkeypatch)
        outsider_id = _user(transaction, "outsider")
        transaction.commit()
        for reviewer_id in (ready["proposer_id"], outsider_id):
            _assert_error(
                lambda reviewer_id=reviewer_id: service.review_grant_evidence_candidate(
                    _command(ready, reviewer_id=reviewer_id), transaction
                ),
                code="GRANT_EVIDENCE_REVIEW_CONFLICT",
                status=409,
            )
        reviewer = transaction.get(T_User, ready["reviewer_id"])
        reviewer.is_active = False
        transaction.commit()
        _assert_error(
            lambda: service.review_grant_evidence_candidate(_command(ready), transaction),
            code="GRANT_EVIDENCE_REVIEW_CONFLICT",
            status=409,
        )
        row = transaction.get(GrantEvidenceCandidate, ready["candidate_id"])
        assert (row.review_status, row.reviewer_id) == ("PENDING", None)


def test_missing_current_role_authority_and_dirty_session_fail_without_write(
    session_factory, monkeypatch
) -> None:
    with session_factory() as transaction:
        ready = _ready(transaction, monkeypatch)

        def unavailable(*_args: object) -> None:
            raise BusinessError("UPSTREAM_CONFLICT", "unavailable", status_code=409)

        monkeypatch.setattr(service, "resolve_grant_manual_review_role_config", unavailable)
        _assert_error(
            lambda: service.review_grant_evidence_candidate(_command(ready), transaction),
            code="GRANT_EVIDENCE_REVIEW_CONFLICT",
            status=409,
        )
        assert transaction.get(GrantEvidenceCandidate, ready["candidate_id"]).review_status == (
            "PENDING"
        )

        transaction.add(
            T_User(
                id=str(uuid4()),
                username=f"pending-{uuid4()}",
                display_name="pending",
                password_hash="test-only",
                is_active=True,
            )
        )
        _assert_error(
            lambda: service.review_grant_evidence_candidate(_command(ready), transaction),
            code="GRANT_EVIDENCE_REVIEW_CONFLICT",
            status=409,
        )
        assert transaction.get(GrantEvidenceCandidate, ready["candidate_id"]).review_status == (
            "PENDING"
        )


@pytest.mark.parametrize(
    "changes",
    (
        {"candidate_id": "not-a-uuid"},
        {"decision": "APPROVED"},
        {"reviewed_at": REVIEWED_AT.replace(tzinfo=timezone.utc)},
        {"reviewed_at": PROPOSED_AT - timedelta(microseconds=1)},
        {"reason": " surrounding whitespace "},
    ),
)
def test_malformed_input_is_400_or_chronology_conflict_without_write(
    session_factory, monkeypatch, changes
) -> None:
    with session_factory() as transaction:
        ready = _ready(transaction, monkeypatch)
        expected_code = (
            "GRANT_EVIDENCE_REVIEW_CONFLICT"
            if changes.get("reviewed_at") == PROPOSED_AT - timedelta(microseconds=1)
            else "GRANT_EVIDENCE_REVIEW_INPUT_INVALID"
        )
        _assert_error(
            lambda: service.review_grant_evidence_candidate(
                _command(ready, **changes), transaction
            ),
            code=expected_code,
            status=409 if expected_code.endswith("CONFLICT") else 400,
        )
        row = transaction.get(GrantEvidenceCandidate, ready["candidate_id"])
        assert row.review_status == "PENDING"


@pytest.mark.parametrize("corruption", ("candidate_hash", "conflicts", "acquisition_binding"))
def test_corrupt_or_cross_bound_candidate_fails_closed(
    session_factory, monkeypatch, corruption
) -> None:
    with session_factory() as transaction:
        ready = _ready(transaction, monkeypatch)
        row = transaction.get(GrantEvidenceCandidate, ready["candidate_id"])
        if corruption == "candidate_hash":
            row.candidate_snapshot_hash = "f" * 64
        elif corruption == "conflicts":
            row.conflict_snapshot = _canonical([])
        else:
            snapshot = json.loads(row.acquisition_snapshot)
            snapshot["case_id"] = str(uuid4())
            row.acquisition_snapshot = _canonical(snapshot)
            row.acquisition_snapshot_hash = _hash(row.acquisition_snapshot)
        transaction.commit()
        _assert_error(
            lambda: service.review_grant_evidence_candidate(_command(ready), transaction),
            code="GRANT_EVIDENCE_REVIEW_CONFLICT",
            status=409,
        )
        transaction.expire_all()
        assert transaction.get(GrantEvidenceCandidate, ready["candidate_id"]).review_status == (
            "PENDING"
        )


def test_lost_compare_and_swap_and_integrity_failure_leave_no_residue(
    session_factory, monkeypatch
) -> None:
    class LostUpdate:
        rowcount = 0

    with session_factory() as transaction:
        ready = _ready(transaction, monkeypatch)
        original_execute = transaction.execute

        def lose_update(statement: object, *args: object, **kwargs: object) -> object:
            if getattr(statement, "is_update", False):
                return LostUpdate()
            return original_execute(statement, *args, **kwargs)

        monkeypatch.setattr(transaction, "execute", lose_update)
        _assert_error(
            lambda: service.review_grant_evidence_candidate(_command(ready), transaction),
            code="GRANT_EVIDENCE_REVIEW_CONFLICT",
            status=409,
        )
        transaction.expire_all()
        assert transaction.get(GrantEvidenceCandidate, ready["candidate_id"]).review_status == (
            "PENDING"
        )

    with session_factory() as transaction:
        ready = _ready(transaction, monkeypatch)
        original_execute = transaction.execute

        def fail_update(statement: object, *args: object, **kwargs: object) -> object:
            if getattr(statement, "is_update", False):
                raise IntegrityError("UPDATE", {}, RuntimeError("injected"))
            return original_execute(statement, *args, **kwargs)

        monkeypatch.setattr(transaction, "execute", fail_update)
        _assert_error(
            lambda: service.review_grant_evidence_candidate(_command(ready), transaction),
            code="GRANT_EVIDENCE_REVIEW_CONFLICT",
            status=409,
        )
        transaction.expire_all()
        assert transaction.get(GrantEvidenceCandidate, ready["candidate_id"]).review_status == (
            "PENDING"
        )
