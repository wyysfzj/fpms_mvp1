from __future__ import annotations

import hashlib
import inspect
import json
from dataclasses import fields, is_dataclass
from datetime import datetime
from types import SimpleNamespace
from typing import get_type_hints

import pytest
from sqlalchemy.orm import Session

from app.core.errors import BusinessError
from app.modules.documents import grant_evidence_ingestion_service as service
from app.modules.documents.models import Document

DOCUMENT_ID = "11111111-1111-4111-8111-111111111111"
CASE_ID = "21111111-1111-4111-8111-111111111111"
EVIDENCE_ID = "31111111-1111-4111-8111-111111111111"
CANDIDATE_ID = "41111111-1111-4111-8111-111111111111"
SOURCE_CONFIG_ID = "51111111-1111-4111-8111-111111111111"
SOURCE_RECORD_ID = "61111111-1111-4111-8111-111111111111"
TERMINAL_ID = "71111111-1111-4111-8111-111111111111"
ROLE_CONFIG_ID = "81111111-1111-4111-8111-111111111111"
PROPOSER_ID = "91111111-1111-4111-8111-111111111111"
NOW = datetime(2026, 8, 11, 10, 0, 0, 123456)


def _canonical(value: object) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def _row(**changes: object) -> SimpleNamespace:
    facts = [
        {"name": "grant_number", "raw_value": "CN-TEST-001"},
        {"name": "status", "raw_value": "GRANTED"},
    ]
    candidate_payload = {
        "schema_version": "CNIPA_GRANT_EVIDENCE_CANDIDATE_V1",
        "evidence_scope": "GRANT_ANNOUNCEMENT",
        "facts": facts,
        "conflicts": [],
    }
    acquisition = {
        "schema_version": "CNIPA_GRANT_EVIDENCE_ACQUISITION_V2",
        "case_id": CASE_ID,
        "document_id": DOCUMENT_ID,
        "attachment_id": "a1111111-1111-4111-8111-111111111111",
        "evidence_version_id": EVIDENCE_ID,
        "evidence_content_hash": "raw-hash",
        "evidence_scope": "GRANT_ANNOUNCEMENT",
        "acquisition_event_id": "a2111111-1111-4111-8111-111111111111",
        "acquisition_event_snapshot_hash": "a" * 64,
        "acquired_by": "a3111111-1111-4111-8111-111111111111",
        "acquired_at": NOW.isoformat(timespec="microseconds"),
        "acquisition_reason": "TEST",
        "first_verification_event_id": "a4111111-1111-4111-8111-111111111111",
        "first_verification_event_snapshot_hash": "b" * 64,
        "first_verified_by": "a5111111-1111-4111-8111-111111111111",
        "first_verified_at": NOW.isoformat(timespec="microseconds"),
        "first_verification_reason": "TEST",
        "terminal_verification_event_id": TERMINAL_ID,
        "terminal_verification_event_snapshot_hash": "c" * 64,
        "second_verified_by": "a6111111-1111-4111-8111-111111111111",
        "second_verified_at": NOW.isoformat(timespec="microseconds"),
        "second_verification_reason": "TEST",
        "source_config_id": SOURCE_CONFIG_ID,
        "source_config_snapshot_hash": "d" * 64,
        "source_record_id": SOURCE_RECORD_ID,
        "source_version": "v1",
        "source_snapshot_hash": "e" * 64,
        "original_reference": "CNIPA TEST",
        "acquisition_method": "CONTROLLED_DOWNLOAD",
        "proposal_role_config_id": ROLE_CONFIG_ID,
        "proposal_role_config_snapshot_hash": "f" * 64,
        "proposed_by": PROPOSER_ID,
        "proposed_at": NOW.isoformat(timespec="microseconds"),
    }
    candidate_snapshot = _canonical(candidate_payload)
    acquisition_snapshot = _canonical(acquisition)
    values = {
        "id": CANDIDATE_ID,
        "case_id": CASE_ID,
        "document_id": DOCUMENT_ID,
        "evidence_version_id": EVIDENCE_ID,
        "source_config_id": SOURCE_CONFIG_ID,
        "source_record_id": SOURCE_RECORD_ID,
        "source_version_snapshot": "v1",
        "original_reference": "CNIPA TEST",
        "acquisition_method_snapshot": "CONTROLLED_DOWNLOAD",
        "acquired_at": NOW,
        "evidence_scope": "GRANT_ANNOUNCEMENT",
        "proposed_by": PROPOSER_ID,
        "proposed_at": NOW,
        "review_status": "PENDING",
        "reviewer_id": None,
        "reviewed_at": None,
        "review_reason": None,
        "acquisition_snapshot": acquisition_snapshot,
        "acquisition_snapshot_hash": hashlib.sha256(acquisition_snapshot.encode()).hexdigest(),
        "candidate_snapshot": candidate_snapshot,
        "candidate_snapshot_hash": hashlib.sha256(candidate_snapshot.encode()).hexdigest(),
        "conflict_snapshot": None,
    }
    values.update(changes)
    return SimpleNamespace(**values)


def _wire(transaction: Session, monkeypatch, rows, *, document_exists: bool = True) -> list[datetime]:
    gate_calls: list[datetime] = []
    monkeypatch.setattr(
        service,
        "_require_source_decision_gate",
        lambda _transaction, read_at: gate_calls.append(read_at),
    )
    monkeypatch.setattr(
        transaction,
        "get",
        lambda model, _identity: SimpleNamespace(id=DOCUMENT_ID)
        if model is Document and document_exists
        else None,
    )
    monkeypatch.setattr(transaction, "scalars", lambda _statement: rows)
    return gate_calls


def _error(call, code: str, status: int) -> None:
    with pytest.raises(BusinessError) as caught:
        call()
    assert (caught.value.code, caught.value.status_code) == (code, status)


def test_public_contract_is_exact_frozen_and_read_only() -> None:
    assert is_dataclass(service.ListGrantEvidenceCandidatesCommand)
    assert is_dataclass(service.GrantEvidenceCandidateRead)
    assert tuple(field.name for field in fields(service.ListGrantEvidenceCandidatesCommand)) == (
        "document_id",
        "read_at",
    )
    assert tuple(field.name for field in fields(service.GrantEvidenceCandidateRead)) == (
        "candidate_id", "case_id", "document_id", "evidence_version_id", "terminal_event_id",
        "source_config_id", "source_record_id", "source_version", "original_reference",
        "acquisition_method", "acquired_at", "evidence_scope", "proposal_role_config_id",
        "proposed_by", "proposed_at", "review_status", "reviewer_id", "reviewed_at",
        "review_reason", "acquisition_snapshot_hash", "candidate_snapshot_hash", "facts",
        "conflicts",
    )
    function = service.list_grant_evidence_candidates
    assert tuple(inspect.signature(function).parameters) == ("command", "transaction")
    assert get_type_hints(function)["transaction"] is Session


def test_valid_and_empty_reads_are_deterministic_and_preserve_raw_truth(
    session_factory, monkeypatch
) -> None:
    with session_factory() as transaction:
        gate_calls = _wire(transaction, monkeypatch, [_row()])
        result = service.list_grant_evidence_candidates(
            service.ListGrantEvidenceCandidatesCommand(document_id=DOCUMENT_ID, read_at=NOW),
            transaction,
        )
        assert gate_calls == [NOW]
        assert len(result) == 1
        assert result[0].terminal_event_id == TERMINAL_ID
        assert result[0].proposal_role_config_id == ROLE_CONFIG_ID
        assert result[0].facts[0].name == "grant_number"
        assert result[0].conflicts == ()
        monkeypatch.setattr(transaction, "scalars", lambda _statement: [])
        assert service.list_grant_evidence_candidates(
            service.ListGrantEvidenceCandidatesCommand(document_id=DOCUMENT_ID, read_at=NOW),
            transaction,
        ) == ()


def test_input_gate_and_missing_document_fail_closed(session_factory, monkeypatch) -> None:
    with session_factory() as transaction:
        _wire(transaction, monkeypatch, [], document_exists=False)
        _error(
            lambda: service.list_grant_evidence_candidates(
                service.ListGrantEvidenceCandidatesCommand(document_id=DOCUMENT_ID, read_at=NOW),
                transaction,
            ),
            "GRANT_EVIDENCE_DOCUMENT_NOT_FOUND",
            404,
        )
        _error(
            lambda: service.list_grant_evidence_candidates(
                service.ListGrantEvidenceCandidatesCommand(document_id="bad", read_at=NOW),
                transaction,
            ),
            "GRANT_EVIDENCE_CANDIDATE_INPUT_INVALID",
            400,
        )
        monkeypatch.setattr(
            service,
            "_require_source_decision_gate",
            lambda *_args: (_ for _ in ()).throw(BusinessError("GATE", "missing", status_code=409)),
        )
        _error(
            lambda: service.list_grant_evidence_candidates(
                service.ListGrantEvidenceCandidatesCommand(document_id=DOCUMENT_ID, read_at=NOW),
                transaction,
            ),
            "GRANT_EVIDENCE_CANDIDATE_CONFLICT",
            409,
        )


@pytest.mark.parametrize(
    "row",
    (
        _row(candidate_snapshot_hash="0" * 64),
        _row(acquisition_snapshot="{}", acquisition_snapshot_hash=hashlib.sha256(b"{}").hexdigest()),
        _row(review_status="APPROVED"),
        _row(conflict_snapshot="[]"),
    ),
)
def test_corrupt_persisted_candidate_fails_entire_read(session_factory, monkeypatch, row) -> None:
    with session_factory() as transaction:
        _wire(transaction, monkeypatch, [row])
        _error(
            lambda: service.list_grant_evidence_candidates(
                service.ListGrantEvidenceCandidatesCommand(document_id=DOCUMENT_ID, read_at=NOW),
                transaction,
            ),
            "GRANT_EVIDENCE_CANDIDATE_CONFLICT",
            409,
        )
