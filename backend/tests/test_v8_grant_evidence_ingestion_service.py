from __future__ import annotations

import hashlib
import inspect
import json
from dataclasses import FrozenInstanceError, fields, is_dataclass, replace
from datetime import datetime, timedelta, timezone
from typing import get_type_hints
from uuid import uuid4

import pytest
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.core.errors import BusinessError
from app.modules.auth.models import T_Role, T_User, T_UserRole
from app.modules.cases.models import Case
from app.modules.documents import grant_evidence_ingestion_service as service
from app.modules.documents.models import (
    DocAttachment,
    Document,
    DocumentEvidenceVersion,
    GrantEvidenceCandidate,
    GrantOfficialCopyVerificationEvent,
)
from app.modules.system.grant_evidence_source_service import GrantEvidenceScope
from app.modules.system.grant_manual_review_role_service import GrantManualReviewRoleResolution
from app.modules.system.models import (
    GrantEvidenceSourceConfig,
    GrantEvidenceSourceRecord,
    GrantManualReviewRoleConfig,
)


@pytest.fixture(autouse=True)
def _remove_committed_verification_chain(session_factory):
    """Unlink the self-referencing fixture chain before the shared table reset."""
    yield
    with session_factory() as transaction:
        transaction.execute(delete(GrantEvidenceCandidate))
        for event_type in ("SECOND_VERIFIED", "FIRST_VERIFIED", "ACQUIRED"):
            transaction.execute(
                delete(GrantOfficialCopyVerificationEvent).where(
                    GrantOfficialCopyVerificationEvent.event_type == event_type
                )
            )
        transaction.commit()

ACQUIRED_AT = datetime(2026, 8, 10, 9, 0, 0, 123456)
PROPOSED_AT = datetime(2026, 8, 10, 12, 0, 0, 123456)
CONTENT_HASH = "raw-official-evidence-sha256"
REFERENCE = "CNIPA-TEST-REFERENCE-NOT-A-LEGAL-CLAIM"
METHOD = "CONTROLLED_DOWNLOAD"
EMPTY_HASH = hashlib.sha256(b"{}").hexdigest()


def _canonical(value: object) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def _event_snapshot(**values: object) -> str:
    return _canonical({"schema": "CNIPA_GRANT_OFFICIAL_COPY_VERIFICATION_EVENT_V1"} | values)


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


def _role(transaction: Session, label: str) -> str:
    role_id = str(uuid4())
    transaction.add(T_Role(id=role_id, code=f"{label}-{uuid4()}", name=label))
    return role_id


def _ready(transaction: Session, monkeypatch: pytest.MonkeyPatch) -> dict[str, object]:
    admin_id = _user(transaction, "admin")
    source_reviewer_id = _user(transaction, "source-reviewer")
    creator_id = _user(transaction, "evidence-creator")
    acquirer_id = _user(transaction, "acquirer")
    first_id = _user(transaction, "first")
    second_id = _user(transaction, "second")
    proposer_id = _user(transaction, "proposer")
    manual_second_id = _user(transaction, "manual-second")
    role_ids = tuple(_role(transaction, f"role-{index}") for index in range(5))
    for user_id, role_id in zip(
        (acquirer_id, first_id, second_id, proposer_id, manual_second_id),
        role_ids,
        strict=True,
    ):
        transaction.add(T_UserRole(user_id=user_id, role_id=role_id))
    transaction.flush()

    case_id = str(uuid4())
    document_id = str(uuid4())
    attachment_id = str(uuid4())
    evidence_id = str(uuid4())
    source_record_id = str(uuid4())
    source_config_id = str(uuid4())
    role_config_id = str(uuid4())
    transaction.add(Case(id=case_id, case_no=f"TEST-{uuid4()}"))
    transaction.flush()
    transaction.add(Document(id=document_id, case_id=case_id))
    transaction.flush()
    transaction.add(
        DocAttachment(
            id=attachment_id,
            document_id=document_id,
            file_name="official.pdf",
            file_path="/test/official.pdf",
            content_hash=CONTENT_HASH,
        )
    )
    transaction.flush()
    transaction.add(
        DocumentEvidenceVersion(
            id=evidence_id,
            case_id=case_id,
            document_id=document_id,
            attachment_id=attachment_id,
            lineage_key="official-copy",
            role="RAW_ATTACHMENT",
            version_number=1,
            state="FINAL",
            creator_id=creator_id,
            review_state="PENDING",
            reviewer_id=None,
            reviewed_at=None,
            final_submitted_at=None,
            content_hash=CONTENT_HASH,
            current_identity_key=f"{case_id}|official-copy",
        )
    )
    transaction.flush()
    transaction.add(
        GrantEvidenceSourceRecord(
            id=source_record_id,
            source_authority="CNIPA",
            source_code="TEST-SOURCE",
            source_version="v1",
            evidence_scope="GRANT_ANNOUNCEMENT",
            source_reference_kind="DATA",
            source_reference_value="TEST SOURCE",
            acquisition_method=METHOD,
            effective_from=ACQUIRED_AT - timedelta(days=1),
            effective_to=None,
            source_snapshot="{}",
            source_snapshot_hash=EMPTY_HASH,
            review_status="APPROVED",
            reviewed_by=source_reviewer_id,
            reviewed_at=ACQUIRED_AT - timedelta(days=1),
            review_reason="TEST ONLY",
            activation_status="ACTIVE",
            activated_by=admin_id,
            activated_at=ACQUIRED_AT - timedelta(hours=1),
            supersedes_source_id=None,
            current_identity_key="CNIPA|GRANT_ANNOUNCEMENT|TEST-SOURCE",
            idempotency_key=f"source-{uuid4()}",
            created_by=admin_id,
            updated_by=admin_id,
        )
    )
    transaction.flush()
    transaction.add(
        GrantEvidenceSourceConfig(
            id=source_config_id,
            gate_code="DG-GRANT-EVIDENCE-SOURCE",
            scope_key="GLOBAL",
            evidence_scope="GRANT_ANNOUNCEMENT",
            source_record_id=source_record_id,
            config_version="v1",
            config_status="ACTIVE",
            effective_from=ACQUIRED_AT - timedelta(days=1),
            effective_to=None,
            selected_by=admin_id,
            published_at=ACQUIRED_AT - timedelta(hours=1),
            selection_reason="TEST ONLY",
            supersedes_config_id=None,
            config_snapshot="{}",
            config_snapshot_hash=EMPTY_HASH,
            idempotency_key=f"source-config-{uuid4()}",
            current_identity_key=(
                "DG-GRANT-EVIDENCE-SOURCE|GLOBAL|GRANT_ANNOUNCEMENT"
            ),
        )
    )
    transaction.flush()
    transaction.add(
        GrantManualReviewRoleConfig(
            id=role_config_id,
            gate_code="DG-GRANT-MANUAL-REVIEW",
            scope_key="GLOBAL",
            official_copy_acquirer_role_id=role_ids[0],
            first_verifier_role_id=role_ids[1],
            second_verifier_role_id=role_ids[2],
            manual_review_proposer_role_id=role_ids[3],
            manual_review_second_reviewer_role_id=role_ids[4],
            config_version="v1",
            config_status="ACTIVE",
            effective_from=ACQUIRED_AT - timedelta(days=1),
            effective_to=None,
            confirmed_by=admin_id,
            published_at=ACQUIRED_AT - timedelta(hours=1),
            supersedes_config_id=None,
            config_snapshot="{}",
            config_snapshot_hash=EMPTY_HASH,
            idempotency_key=f"role-config-{uuid4()}",
            current_identity_key="DG-GRANT-MANUAL-REVIEW|GLOBAL",
        )
    )
    transaction.flush()

    event_ids = [str(uuid4()) for _ in range(3)]
    actors = (acquirer_id, first_id, second_id)
    stages = ("ACQUIRED", "FIRST_VERIFIED", "SECOND_VERIFIED")
    reasons = ("TEST ACQUIRE", "TEST FIRST", "TEST SECOND")
    for index, (event_id, actor_id, stage, reason) in enumerate(
        zip(event_ids, actors, stages, reasons, strict=True)
    ):
        action_at = ACQUIRED_AT + timedelta(minutes=index)
        predecessor_id = event_ids[index - 1] if index else None
        snapshot = _event_snapshot(
            acquisition_method_snapshot=METHOD,
            action_at=action_at.isoformat(timespec="microseconds"),
            actor_id=actor_id,
            event_type=stage,
            evidence_content_hash=CONTENT_HASH,
            evidence_scope="GRANT_ANNOUNCEMENT",
            evidence_version_id=evidence_id,
            original_reference=REFERENCE,
            predecessor_event_id=predecessor_id,
            reason=reason,
            role_config_id=role_config_id,
            role_config_snapshot_hash=EMPTY_HASH,
            source_config_id=source_config_id,
            source_config_snapshot_hash=EMPTY_HASH,
            source_record_id=source_record_id,
            source_snapshot_hash=EMPTY_HASH,
        )
        transaction.add(
            GrantOfficialCopyVerificationEvent(
                id=event_id,
                evidence_version_id=evidence_id,
                source_config_id=source_config_id,
                source_record_id=source_record_id,
                role_config_id=role_config_id,
                evidence_scope="GRANT_ANNOUNCEMENT",
                event_type=stage,
                actor_id=actor_id,
                action_at=action_at,
                reason=reason,
                original_reference=REFERENCE,
                acquisition_method_snapshot=METHOD,
                evidence_content_hash=CONTENT_HASH,
                source_config_snapshot_hash=EMPTY_HASH,
                source_snapshot_hash=EMPTY_HASH,
                role_config_snapshot_hash=EMPTY_HASH,
                predecessor_event_id=predecessor_id,
                event_snapshot=snapshot,
                event_snapshot_hash=hashlib.sha256(snapshot.encode()).hexdigest(),
                idempotency_key=f"event-{index}-{uuid4()}",
                current_identity_key=(
                    f"GRANT_OFFICIAL_COPY|{evidence_id}" if index == 2 else None
                ),
            )
        )
        transaction.flush()
    transaction.commit()

    role_resolution = GrantManualReviewRoleResolution(
        gate_id=str(uuid4()),
        config_id=role_config_id,
        config_snapshot_hash=EMPTY_HASH,
        official_copy_acquirer_role_id=role_ids[0],
        first_verifier_role_id=role_ids[1],
        second_verifier_role_id=role_ids[2],
        manual_review_proposer_role_id=role_ids[3],
        manual_review_second_reviewer_role_id=role_ids[4],
        effective_from=ACQUIRED_AT - timedelta(days=1),
        effective_to=None,
    )
    monkeypatch.setattr(
        service,
        "resolve_grant_manual_review_role_config",
        lambda _command, _transaction: role_resolution,
    )
    return {
        "case_id": case_id,
        "document_id": document_id,
        "attachment_id": attachment_id,
        "evidence_id": evidence_id,
        "event_ids": tuple(event_ids),
        "source_record_id": source_record_id,
        "source_config_id": source_config_id,
        "role_config_id": role_config_id,
        "proposer_id": proposer_id,
        "first_id": first_id,
        "second_id": second_id,
        "roles": role_resolution,
    }


def _command(ready: dict[str, object], **changes: object):
    values: dict[str, object] = {
        "case_id": ready["case_id"],
        "document_id": ready["document_id"],
        "evidence_version_id": ready["evidence_id"],
        "evidence_scope": GrantEvidenceScope.GRANT_ANNOUNCEMENT,
        "expected_terminal_event_id": ready["event_ids"][2],
        "proposed_by": ready["proposer_id"],
        "proposed_at": PROPOSED_AT,
        "facts": (
            service.GrantEvidenceFact(name="grant_number", raw_value="CN-TEST-001"),
            service.GrantEvidenceFact(name="status", raw_value="GRANTED"),
        ),
        "conflicts": (),
    }
    values.update(changes)
    return service.IngestGrantEvidenceCandidateCommand(**values)


def _assert_error(call, *, code: str, status: int) -> BusinessError:
    with pytest.raises(BusinessError) as caught:
        call()
    assert caught.value.code == code
    assert caught.value.status_code == status
    return caught.value


def test_public_contract_is_exact_frozen_keyword_only_and_synchronous() -> None:
    dto_fields = {
        service.GrantEvidenceFact: ("name", "raw_value"),
        service.GrantEvidenceConflict: ("name", "raw_values"),
        service.IngestGrantEvidenceCandidateCommand: (
            "case_id",
            "document_id",
            "evidence_version_id",
            "evidence_scope",
            "expected_terminal_event_id",
            "proposed_by",
            "proposed_at",
            "facts",
            "conflicts",
        ),
        service.IngestGrantEvidenceCandidateResult: (
            "candidate_id",
            "evidence_version_id",
            "terminal_event_id",
            "source_config_id",
            "source_record_id",
            "proposal_role_config_id",
            "evidence_scope",
            "acquisition_snapshot_hash",
            "candidate_snapshot_hash",
            "review_status",
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
    function = service.ingest_grant_evidence_candidate
    assert tuple(inspect.signature(function).parameters) == ("command", "transaction")
    assert get_type_hints(function)["transaction"] is Session
    assert inspect.iscoroutinefunction(function) is False
    fact = service.GrantEvidenceFact(name="a", raw_value="b")
    with pytest.raises(FrozenInstanceError):
        fact.name = "changed"


def test_valid_terminal_chain_creates_canonical_pending_candidate_without_side_effects(
    session_factory, monkeypatch
) -> None:
    with session_factory() as transaction:
        ready = _ready(transaction, monkeypatch)
        case = transaction.get(Case, ready["case_id"])
        before = (case.status, case.legal_status, case.lifecycle_revision)
        result = service.ingest_grant_evidence_candidate(_command(ready), transaction)
        assert result.disposition == "CREATED"
        assert result.terminal_event_id == ready["event_ids"][2]
        assert result.proposal_role_config_id == ready["role_config_id"]
        row = transaction.get(GrantEvidenceCandidate, result.candidate_id)
        acquisition = json.loads(row.acquisition_snapshot)
        assert acquisition["schema_version"] == "CNIPA_GRANT_EVIDENCE_ACQUISITION_V2"
        assert acquisition["acquired_by"] != acquisition["proposed_by"]
        assert acquisition["first_verified_by"] != acquisition["second_verified_by"]
        assert acquisition["terminal_verification_event_id"] == ready["event_ids"][2]
        assert row.acquisition_snapshot_hash == hashlib.sha256(
            row.acquisition_snapshot.encode()
        ).hexdigest()
        assert row.candidate_snapshot_hash == hashlib.sha256(
            row.candidate_snapshot.encode()
        ).hexdigest()
        assert row.review_status == "PENDING"
        assert (row.reviewer_id, row.reviewed_at, row.review_reason) == (None, None, None)
        transaction.expire_all()
        case = transaction.get(Case, ready["case_id"])
        assert (case.status, case.legal_status, case.lifecycle_revision) == before


def test_exact_replay_reuses_and_changed_candidate_conflicts(session_factory, monkeypatch) -> None:
    with session_factory() as transaction:
        ready = _ready(transaction, monkeypatch)
        command = _command(ready)
        created = service.ingest_grant_evidence_candidate(command, transaction)
        assert service.ingest_grant_evidence_candidate(command, transaction) == replace(
            created, disposition="REUSED"
        )
        changed = replace(
            command,
            facts=(service.GrantEvidenceFact(name="status", raw_value="DIFFERENT"),),
        )
        _assert_error(
            lambda: service.ingest_grant_evidence_candidate(changed, transaction),
            code="GRANT_EVIDENCE_CANDIDATE_CONFLICT",
            status=409,
        )
        assert transaction.scalar(select(func.count()).select_from(GrantEvidenceCandidate)) == 1


@pytest.mark.parametrize(
    "changes",
    (
        {"evidence_scope": "GRANT_ANNOUNCEMENT"},
        {"proposed_at": PROPOSED_AT.replace(tzinfo=timezone.utc)},
        {"case_id": "not-a-uuid"},
        {"facts": ()},
        {
            "facts": (
                service.GrantEvidenceFact(name="z", raw_value="1"),
                service.GrantEvidenceFact(name="a", raw_value="2"),
            )
        },
        {
            "facts": (service.GrantEvidenceFact(name="status", raw_value="GRANTED"),),
            "conflicts": (
                service.GrantEvidenceConflict(name="status", raw_values=("same", "same")),
            ),
        },
    ),
)
def test_malformed_input_is_400_without_candidate(session_factory, monkeypatch, changes) -> None:
    with session_factory() as transaction:
        ready = _ready(transaction, monkeypatch)
        _assert_error(
            lambda: service.ingest_grant_evidence_candidate(
                _command(ready, **changes), transaction
            ),
            code="GRANT_EVIDENCE_CANDIDATE_INPUT_INVALID",
            status=400,
        )
        assert transaction.scalar(select(func.count()).select_from(GrantEvidenceCandidate)) == 0


def test_nonterminal_wrong_current_corrupt_and_same_verifier_fail_closed(
    session_factory, monkeypatch
) -> None:
    with session_factory() as transaction:
        ready = _ready(transaction, monkeypatch)
        for expected in (ready["event_ids"][1], str(uuid4())):
            _assert_error(
                lambda expected=expected: service.ingest_grant_evidence_candidate(
                    _command(ready, expected_terminal_event_id=expected), transaction
                ),
                code="GRANT_EVIDENCE_CANDIDATE_CONFLICT",
                status=409,
            )
        terminal = transaction.get(
            GrantOfficialCopyVerificationEvent, ready["event_ids"][2]
        )
        terminal.event_snapshot_hash = "d" * 64
        transaction.commit()
        _assert_error(
            lambda: service.ingest_grant_evidence_candidate(_command(ready), transaction),
            code="GRANT_EVIDENCE_CANDIDATE_CONFLICT",
            status=409,
        )
        terminal.event_snapshot_hash = hashlib.sha256(terminal.event_snapshot.encode()).hexdigest()
        terminal.actor_id = ready["first_id"]
        snapshot = json.loads(terminal.event_snapshot)
        snapshot["actor_id"] = ready["first_id"]
        terminal.event_snapshot = _canonical(snapshot)
        terminal.event_snapshot_hash = hashlib.sha256(terminal.event_snapshot.encode()).hexdigest()
        transaction.commit()
        _assert_error(
            lambda: service.ingest_grant_evidence_candidate(_command(ready), transaction),
            code="GRANT_EVIDENCE_CANDIDATE_CONFLICT",
            status=409,
        )


def test_unbound_inactive_proposer_and_role_resolver_failure_are_no_write(
    session_factory, monkeypatch
) -> None:
    with session_factory() as transaction:
        ready = _ready(transaction, monkeypatch)
        outsider_id = _user(transaction, "outsider")
        transaction.commit()
        _assert_error(
            lambda: service.ingest_grant_evidence_candidate(
                _command(ready, proposed_by=outsider_id), transaction
            ),
            code="GRANT_EVIDENCE_CANDIDATE_CONFLICT",
            status=409,
        )
        proposer = transaction.get(T_User, ready["proposer_id"])
        proposer.is_active = False
        transaction.commit()
        _assert_error(
            lambda: service.ingest_grant_evidence_candidate(_command(ready), transaction),
            code="GRANT_EVIDENCE_CANDIDATE_CONFLICT",
            status=409,
        )
        monkeypatch.setattr(
            service,
            "resolve_grant_manual_review_role_config",
            lambda _c, _t: (_ for _ in ()).throw(
                BusinessError("ROLE", "missing", status_code=409)
            ),
        )
        _assert_error(
            lambda: service.ingest_grant_evidence_candidate(_command(ready), transaction),
            code="GRANT_EVIDENCE_CANDIDATE_CONFLICT",
            status=409,
        )
        assert transaction.scalar(select(func.count()).select_from(GrantEvidenceCandidate)) == 0


@pytest.mark.parametrize(
    ("target", "field", "value"),
    (
        ("evidence", "state", "DRAFT"),
        ("evidence", "current_identity_key", None),
        ("source", "source_snapshot_hash", "d" * 64),
        ("source", "effective_from", ACQUIRED_AT + timedelta(days=1)),
        ("source_config", "config_status", "REVOKED"),
        ("role_config", "config_snapshot_hash", "d" * 64),
    ),
)
def test_invalid_evidence_or_historical_authority_fails_closed(
    session_factory, monkeypatch, target, field, value
) -> None:
    with session_factory() as transaction:
        ready = _ready(transaction, monkeypatch)
        rows = {
            "evidence": transaction.get(DocumentEvidenceVersion, ready["evidence_id"]),
            "source": transaction.get(GrantEvidenceSourceRecord, ready["source_record_id"]),
            "source_config": transaction.get(
                GrantEvidenceSourceConfig, ready["source_config_id"]
            ),
            "role_config": transaction.get(
                GrantManualReviewRoleConfig, ready["role_config_id"]
            ),
        }
        setattr(rows[target], field, value)
        transaction.commit()
        _assert_error(
            lambda: service.ingest_grant_evidence_candidate(_command(ready), transaction),
            code="GRANT_EVIDENCE_CANDIDATE_CONFLICT",
            status=409,
        )
        assert transaction.scalar(select(func.count()).select_from(GrantEvidenceCandidate)) == 0


def test_caller_rollback_and_flush_failure_leave_no_candidate(
    session_factory, monkeypatch
) -> None:
    with session_factory() as transaction:
        ready = _ready(transaction, monkeypatch)
        command = _command(ready)
        created = service.ingest_grant_evidence_candidate(command, transaction)
        transaction.rollback()
        assert transaction.get(GrantEvidenceCandidate, created.candidate_id) is None

        original_flush = transaction.flush

        def fail_flush(*_args, **_kwargs):
            raise RuntimeError("injected flush failure")

        monkeypatch.setattr(transaction, "flush", fail_flush)
        with pytest.raises(RuntimeError, match="injected flush failure"):
            service.ingest_grant_evidence_candidate(command, transaction)
        monkeypatch.setattr(transaction, "flush", original_flush)
        assert transaction.scalar(select(func.count()).select_from(GrantEvidenceCandidate)) == 0
