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
from sqlalchemy.orm import Session

from app.core.errors import BusinessError
from app.modules.auth.models import T_Role, T_User, T_UserRole
from app.modules.cases.models import Case
from app.modules.documents import grant_official_copy_verification_service as service
from app.modules.documents.models import (
    DocAttachment,
    Document,
    DocumentEvidenceVersion,
    GrantEvidenceCandidate,
    GrantOfficialCopyVerificationEvent,
)
from app.modules.system.grant_evidence_source_service import (
    GrantEvidenceScope,
    GrantEvidenceSourceReferenceKind,
    GrantEvidenceSourceResolution,
)
from app.modules.system.grant_manual_review_role_service import (
    GrantManualReviewRoleResolution,
)
from app.modules.system.models import (
    GrantEvidenceSourceConfig,
    GrantEvidenceSourceRecord,
    GrantManualReviewRoleConfig,
)

ACTION_AT = datetime(2026, 8, 10, 16, 0, 0, 123456)
SOURCE_CONFIG_HASH = "a" * 64
SOURCE_HASH = "b" * 64
ROLE_CONFIG_HASH = "c" * 64
CONTENT_HASH = "raw-official-evidence-sha256"
REFERENCE = "CNIPA-TEST-REFERENCE-NOT-A-LEGAL-CLAIM"


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


def _bind(transaction: Session, user_id: str, role_id: str) -> None:
    transaction.add(T_UserRole(user_id=user_id, role_id=role_id))


def _ready(transaction: Session, monkeypatch: pytest.MonkeyPatch) -> dict[str, object]:
    admin_id = _user(transaction, "admin")
    reviewer_id = _user(transaction, "source-reviewer")
    acquirer_id = _user(transaction, "acquirer")
    first_id = _user(transaction, "first")
    second_id = _user(transaction, "second")
    proposer_id = _user(transaction, "proposer")
    manual_second_id = _user(transaction, "manual-second")
    creator_id = _user(transaction, "evidence-creator")
    role_ids = tuple(_role(transaction, f"duty-{index}") for index in range(5))
    for user_id, role_id in zip(
        (acquirer_id, first_id, second_id, proposer_id, manual_second_id),
        role_ids,
        strict=True,
    ):
        _bind(transaction, user_id, role_id)
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
            source_reference_value="TEST SOURCE DIRECTORY ENTRY",
            acquisition_method="CONTROLLED_DOWNLOAD",
            effective_from=ACTION_AT - timedelta(days=1),
            effective_to=None,
            source_snapshot="{}",
            source_snapshot_hash=SOURCE_HASH,
            review_status="APPROVED",
            reviewed_by=reviewer_id,
            reviewed_at=ACTION_AT - timedelta(days=1),
            review_reason="TEST ONLY",
            activation_status="ACTIVE",
            activated_by=admin_id,
            activated_at=ACTION_AT - timedelta(days=1),
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
            effective_from=ACTION_AT - timedelta(days=1),
            effective_to=None,
            selected_by=admin_id,
            published_at=ACTION_AT - timedelta(days=1),
            selection_reason="TEST ONLY",
            supersedes_config_id=None,
            config_snapshot="{}",
            config_snapshot_hash=SOURCE_CONFIG_HASH,
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
            effective_from=ACTION_AT - timedelta(days=1),
            effective_to=None,
            confirmed_by=admin_id,
            published_at=ACTION_AT - timedelta(days=1),
            supersedes_config_id=None,
            config_snapshot="{}",
            config_snapshot_hash=ROLE_CONFIG_HASH,
            idempotency_key=f"role-config-{uuid4()}",
            current_identity_key="DG-GRANT-MANUAL-REVIEW|GLOBAL",
        )
    )
    transaction.commit()

    source_resolution = GrantEvidenceSourceResolution(
        gate_id=str(uuid4()),
        config_id=source_config_id,
        config_snapshot_hash=SOURCE_CONFIG_HASH,
        source_record_id=source_record_id,
        evidence_scope=GrantEvidenceScope.GRANT_ANNOUNCEMENT,
        source_code="TEST-SOURCE",
        source_version="v1",
        source_snapshot_hash=SOURCE_HASH,
        source_reference_kind=GrantEvidenceSourceReferenceKind.DATA,
        source_reference_value="TEST SOURCE DIRECTORY ENTRY",
        acquisition_method="CONTROLLED_DOWNLOAD",
        effective_from=ACTION_AT - timedelta(days=1),
        effective_to=None,
    )
    role_resolution = GrantManualReviewRoleResolution(
        gate_id=str(uuid4()),
        config_id=role_config_id,
        config_snapshot_hash=ROLE_CONFIG_HASH,
        official_copy_acquirer_role_id=role_ids[0],
        first_verifier_role_id=role_ids[1],
        second_verifier_role_id=role_ids[2],
        manual_review_proposer_role_id=role_ids[3],
        manual_review_second_reviewer_role_id=role_ids[4],
        effective_from=ACTION_AT - timedelta(days=1),
        effective_to=None,
    )
    monkeypatch.setattr(service, "resolve_grant_evidence_source", lambda _c, _t: source_resolution)
    monkeypatch.setattr(
        service,
        "resolve_grant_manual_review_role_config",
        lambda _c, _t: role_resolution,
    )
    return {
        "case_id": case_id,
        "document_id": document_id,
        "attachment_id": attachment_id,
        "evidence_id": evidence_id,
        "source": source_resolution,
        "roles": role_resolution,
        "acquirer_id": acquirer_id,
        "first_id": first_id,
        "second_id": second_id,
    }


def _command(
    ready: dict[str, object],
    stage: service.GrantOfficialCopyEventType,
    **changes: object,
) -> service.RecordGrantOfficialCopyEventCommand:
    actors = {
        service.GrantOfficialCopyEventType.ACQUIRED: ready["acquirer_id"],
        service.GrantOfficialCopyEventType.FIRST_VERIFIED: ready["first_id"],
        service.GrantOfficialCopyEventType.SECOND_VERIFIED: ready["second_id"],
    }
    values: dict[str, object] = {
        "evidence_version_id": ready["evidence_id"],
        "evidence_scope": GrantEvidenceScope.GRANT_ANNOUNCEMENT,
        "event_type": stage,
        "actor_id": actors[stage],
        "action_at": ACTION_AT + timedelta(minutes=list(actors).index(stage)),
        "reason": f"TEST {stage.value}",
        "original_reference": REFERENCE if stage is service.GrantOfficialCopyEventType.ACQUIRED else None,
        "expected_current_event_id": None,
        "idempotency_key": f"{stage.value}-{uuid4()}",
    }
    values.update(changes)
    return service.RecordGrantOfficialCopyEventCommand(**values)


def _assert_error(call, *, code: str, status: int) -> BusinessError:
    with pytest.raises(BusinessError) as caught:
        call()
    assert caught.value.code == code
    assert caught.value.status_code == status
    return caught.value


def _record_chain(
    transaction: Session,
    ready: dict[str, object],
) -> tuple[service.GrantOfficialCopyEventResult, ...]:
    acquired_command = _command(ready, service.GrantOfficialCopyEventType.ACQUIRED)
    acquired = service.record_grant_official_copy_event(acquired_command, transaction)
    first = service.record_grant_official_copy_event(
        _command(
            ready,
            service.GrantOfficialCopyEventType.FIRST_VERIFIED,
            expected_current_event_id=acquired.event_id,
        ),
        transaction,
    )
    second = service.record_grant_official_copy_event(
        _command(
            ready,
            service.GrantOfficialCopyEventType.SECOND_VERIFIED,
            expected_current_event_id=first.event_id,
        ),
        transaction,
    )
    return acquired, first, second


def test_public_contract_is_exact_frozen_keyword_only_and_synchronous() -> None:
    assert tuple(item.value for item in service.GrantOfficialCopyEventType) == (
        "ACQUIRED",
        "FIRST_VERIFIED",
        "SECOND_VERIFIED",
    )
    assert tuple(item.value for item in service.GrantOfficialCopyDisposition) == (
        "CREATED",
        "REUSED",
    )
    dto_fields = {
        service.RecordGrantOfficialCopyEventCommand: (
            "evidence_version_id",
            "evidence_scope",
            "event_type",
            "actor_id",
            "action_at",
            "reason",
            "original_reference",
            "expected_current_event_id",
            "idempotency_key",
        ),
        service.GrantOfficialCopyEventResult: (
            "event_id",
            "evidence_version_id",
            "evidence_scope",
            "event_type",
            "source_config_id",
            "source_record_id",
            "role_config_id",
            "event_snapshot_hash",
            "current_identity_key",
            "disposition",
        ),
    }
    for dto, expected in dto_fields.items():
        assert is_dataclass(dto)
        assert dto.__dataclass_params__.frozen is True
        assert dto.__slots__ == expected
        assert tuple(field.name for field in fields(dto)) == expected
        assert all(
            value.kind is inspect.Parameter.KEYWORD_ONLY
            for value in inspect.signature(dto).parameters.values()
        )
    function = service.record_grant_official_copy_event
    assert tuple(inspect.signature(function).parameters) == ("command", "transaction")
    assert get_type_hints(function)["transaction"] is Session
    assert inspect.iscoroutinefunction(function) is False
    placeholder = service.RecordGrantOfficialCopyEventCommand(
        evidence_version_id=str(uuid4()),
        evidence_scope=GrantEvidenceScope.GRANT_ANNOUNCEMENT,
        event_type=service.GrantOfficialCopyEventType.ACQUIRED,
        actor_id=str(uuid4()),
        action_at=ACTION_AT,
        reason="TEST",
        original_reference=REFERENCE,
        expected_current_event_id=None,
        idempotency_key="test",
    )
    with pytest.raises(FrozenInstanceError):
        placeholder.reason = "changed"


def test_valid_chain_is_canonical_current_and_has_no_product_side_effects(
    session_factory, monkeypatch
) -> None:
    with session_factory() as transaction:
        ready = _ready(transaction, monkeypatch)
        before_case = transaction.get(Case, ready["case_id"])
        before_status = (before_case.status, before_case.legal_status, before_case.lifecycle_revision)
        acquired, first, second = _record_chain(transaction, ready)
        assert tuple(result.disposition for result in (acquired, first, second)) == (
            service.GrantOfficialCopyDisposition.CREATED,
        ) * 3
        rows = list(
            transaction.scalars(
                select(GrantOfficialCopyVerificationEvent).order_by(
                    GrantOfficialCopyVerificationEvent.action_at
                )
            )
        )
        assert [row.event_type for row in rows] == [
            "ACQUIRED",
            "FIRST_VERIFIED",
            "SECOND_VERIFIED",
        ]
        assert [row.actor_id for row in rows] == [
            ready["acquirer_id"],
            ready["first_id"],
            ready["second_id"],
        ]
        assert [row.predecessor_event_id for row in rows] == [None, rows[0].id, rows[1].id]
        assert [row.current_identity_key is not None for row in rows] == [False, False, True]
        for row in rows:
            snapshot = json.loads(row.event_snapshot)
            assert tuple(sorted(snapshot)) == tuple(
                sorted(
                    (
                        "schema",
                        "evidence_version_id",
                        "source_config_id",
                        "source_record_id",
                        "role_config_id",
                        "evidence_scope",
                        "event_type",
                        "actor_id",
                        "action_at",
                        "reason",
                        "original_reference",
                        "acquisition_method_snapshot",
                        "evidence_content_hash",
                        "source_config_snapshot_hash",
                        "source_snapshot_hash",
                        "role_config_snapshot_hash",
                        "predecessor_event_id",
                    )
                )
            )
            assert snapshot["schema"] == "CNIPA_GRANT_OFFICIAL_COPY_VERIFICATION_EVENT_V1"
            assert row.event_snapshot_hash == hashlib.sha256(row.event_snapshot.encode()).hexdigest()
            assert row.evidence_content_hash == CONTENT_HASH
            assert row.original_reference == REFERENCE
        after_case = transaction.get(Case, ready["case_id"])
        assert (after_case.status, after_case.legal_status, after_case.lifecycle_revision) == before_status
        assert transaction.scalar(select(func.count()).select_from(GrantEvidenceCandidate)) == 0


def test_exact_replay_reuses_and_changed_replay_conflicts(session_factory, monkeypatch) -> None:
    with session_factory() as transaction:
        ready = _ready(transaction, monkeypatch)
        command = _command(ready, service.GrantOfficialCopyEventType.ACQUIRED)
        created = service.record_grant_official_copy_event(command, transaction)
        assert service.record_grant_official_copy_event(command, transaction) == replace(
            created,
            disposition=service.GrantOfficialCopyDisposition.REUSED,
        )
        changed = replace(command, reason="CHANGED")
        _assert_error(
            lambda: service.record_grant_official_copy_event(changed, transaction),
            code="GRANT_OFFICIAL_COPY_EVENT_CONFLICT",
            status=409,
        )
        assert transaction.scalar(
            select(func.count()).select_from(GrantOfficialCopyVerificationEvent)
        ) == 1


@pytest.mark.parametrize(
    "changes",
    (
        {"evidence_scope": "GRANT_ANNOUNCEMENT"},
        {"event_type": "ACQUIRED"},
        {"action_at": ACTION_AT.replace(tzinfo=timezone.utc)},
        {"reason": " bad"},
        {"original_reference": None},
        {"expected_current_event_id": str(uuid4())},
        {"idempotency_key": ""},
    ),
)
def test_malformed_acquisition_input_is_400_no_write(
    session_factory, monkeypatch, changes
) -> None:
    with session_factory() as transaction:
        ready = _ready(transaction, monkeypatch)
        command = _command(ready, service.GrantOfficialCopyEventType.ACQUIRED, **changes)
        _assert_error(
            lambda: service.record_grant_official_copy_event(command, transaction),
            code="GRANT_OFFICIAL_COPY_EVENT_INPUT_INVALID",
            status=400,
        )
        assert transaction.scalar(
            select(func.count()).select_from(GrantOfficialCopyVerificationEvent)
        ) == 0


def test_wrong_stage_current_and_same_actual_verifier_fail_closed(
    session_factory, monkeypatch
) -> None:
    with session_factory() as transaction:
        ready = _ready(transaction, monkeypatch)
        acquired = service.record_grant_official_copy_event(
            _command(ready, service.GrantOfficialCopyEventType.ACQUIRED), transaction
        )
        wrong_expected = _command(
            ready,
            service.GrantOfficialCopyEventType.FIRST_VERIFIED,
            expected_current_event_id=str(uuid4()),
        )
        _assert_error(
            lambda: service.record_grant_official_copy_event(wrong_expected, transaction),
            code="GRANT_OFFICIAL_COPY_EVENT_CONFLICT",
            status=409,
        )
        first = service.record_grant_official_copy_event(
            replace(wrong_expected, expected_current_event_id=acquired.event_id), transaction
        )
        _bind(transaction, ready["first_id"], ready["roles"].second_verifier_role_id)
        transaction.flush()
        same_user = _command(
            ready,
            service.GrantOfficialCopyEventType.SECOND_VERIFIED,
            actor_id=ready["first_id"],
            expected_current_event_id=first.event_id,
        )
        _assert_error(
            lambda: service.record_grant_official_copy_event(same_user, transaction),
            code="GRANT_OFFICIAL_COPY_EVENT_CONFLICT",
            status=409,
        )
        transaction.expire_all()
        assert transaction.get(GrantOfficialCopyVerificationEvent, first.event_id).current_identity_key


def test_unbound_or_inactive_actor_and_resolver_failure_are_no_write(
    session_factory, monkeypatch
) -> None:
    with session_factory() as transaction:
        ready = _ready(transaction, monkeypatch)
        outsider_id = _user(transaction, "outsider")
        transaction.commit()
        unbound = _command(
            ready,
            service.GrantOfficialCopyEventType.ACQUIRED,
            actor_id=outsider_id,
        )
        _assert_error(
            lambda: service.record_grant_official_copy_event(unbound, transaction),
            code="GRANT_OFFICIAL_COPY_EVENT_CONFLICT",
            status=409,
        )
        actor = transaction.get(T_User, ready["acquirer_id"])
        actor.is_active = False
        transaction.commit()
        _assert_error(
            lambda: service.record_grant_official_copy_event(
                _command(ready, service.GrantOfficialCopyEventType.ACQUIRED), transaction
            ),
            code="GRANT_OFFICIAL_COPY_EVENT_CONFLICT",
            status=409,
        )
        monkeypatch.setattr(
            service,
            "resolve_grant_evidence_source",
            lambda _c, _t: (_ for _ in ()).throw(BusinessError("SOURCE", "missing", status_code=409)),
        )
        _assert_error(
            lambda: service.record_grant_official_copy_event(
                _command(ready, service.GrantOfficialCopyEventType.ACQUIRED), transaction
            ),
            code="GRANT_OFFICIAL_COPY_EVENT_CONFLICT",
            status=409,
        )
        assert transaction.scalar(
            select(func.count()).select_from(GrantOfficialCopyVerificationEvent)
        ) == 0


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("state", "DRAFT"),
        ("role", "GENERATED_ATTACHMENT"),
        ("review_state", "APPROVED"),
        ("current_identity_key", None),
        ("content_hash", " bad"),
    ),
)
def test_invalid_evidence_version_fails_before_event(
    session_factory, monkeypatch, field, value
) -> None:
    with session_factory() as transaction:
        ready = _ready(transaction, monkeypatch)
        evidence = transaction.get(DocumentEvidenceVersion, ready["evidence_id"])
        setattr(evidence, field, value)
        transaction.commit()
        _assert_error(
            lambda: service.record_grant_official_copy_event(
                _command(ready, service.GrantOfficialCopyEventType.ACQUIRED), transaction
            ),
            code="GRANT_OFFICIAL_COPY_EVENT_CONFLICT",
            status=409,
        )
        assert transaction.scalar(
            select(func.count()).select_from(GrantOfficialCopyVerificationEvent)
        ) == 0


def test_changed_source_between_stages_fails_without_pointer_move(
    session_factory, monkeypatch
) -> None:
    with session_factory() as transaction:
        ready = _ready(transaction, monkeypatch)
        acquired = service.record_grant_official_copy_event(
            _command(ready, service.GrantOfficialCopyEventType.ACQUIRED), transaction
        )
        changed_source = replace(ready["source"], config_snapshot_hash="d" * 64)
        monkeypatch.setattr(
            service,
            "resolve_grant_evidence_source",
            lambda _c, _t: changed_source,
        )
        _assert_error(
            lambda: service.record_grant_official_copy_event(
                _command(
                    ready,
                    service.GrantOfficialCopyEventType.FIRST_VERIFIED,
                    expected_current_event_id=acquired.event_id,
                ),
                transaction,
            ),
            code="GRANT_OFFICIAL_COPY_EVENT_CONFLICT",
            status=409,
        )
        transaction.expire_all()
        assert transaction.get(
            GrantOfficialCopyVerificationEvent, acquired.event_id
        ).current_identity_key
        assert transaction.scalar(
            select(func.count()).select_from(GrantOfficialCopyVerificationEvent)
        ) == 1


def test_corrupt_predecessor_canonical_lineage_fails_closed(
    session_factory, monkeypatch
) -> None:
    with session_factory() as transaction:
        ready = _ready(transaction, monkeypatch)
        acquired = service.record_grant_official_copy_event(
            _command(ready, service.GrantOfficialCopyEventType.ACQUIRED), transaction
        )
        transaction.commit()
        row = transaction.get(GrantOfficialCopyVerificationEvent, acquired.event_id)
        row.event_snapshot_hash = "d" * 64
        transaction.commit()
        _assert_error(
            lambda: service.record_grant_official_copy_event(
                _command(
                    ready,
                    service.GrantOfficialCopyEventType.FIRST_VERIFIED,
                    expected_current_event_id=acquired.event_id,
                ),
                transaction,
            ),
            code="GRANT_OFFICIAL_COPY_EVENT_CONFLICT",
            status=409,
        )
        assert transaction.scalar(
            select(func.count()).select_from(GrantOfficialCopyVerificationEvent)
        ) == 1


def test_caller_rollback_and_flush_failure_leave_no_residue(
    session_factory, monkeypatch
) -> None:
    with session_factory() as transaction:
        ready = _ready(transaction, monkeypatch)
        acquired_command = _command(ready, service.GrantOfficialCopyEventType.ACQUIRED)
        acquired = service.record_grant_official_copy_event(acquired_command, transaction)
        transaction.rollback()
        assert transaction.get(GrantOfficialCopyVerificationEvent, acquired.event_id) is None

        acquired = service.record_grant_official_copy_event(acquired_command, transaction)
        transaction.commit()
        original_flush = transaction.flush

        def fail_flush(*_args, **_kwargs):
            raise RuntimeError("injected flush failure")

        monkeypatch.setattr(transaction, "flush", fail_flush)
        with pytest.raises(RuntimeError, match="injected flush failure"):
            service.record_grant_official_copy_event(
                _command(
                    ready,
                    service.GrantOfficialCopyEventType.FIRST_VERIFIED,
                    expected_current_event_id=acquired.event_id,
                ),
                transaction,
            )
        monkeypatch.setattr(transaction, "flush", original_flush)
        transaction.expire_all()
        assert transaction.get(
            GrantOfficialCopyVerificationEvent, acquired.event_id
        ).current_identity_key
        assert transaction.scalar(
            select(func.count()).select_from(GrantOfficialCopyVerificationEvent)
        ) == 1
