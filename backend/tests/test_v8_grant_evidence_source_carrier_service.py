from __future__ import annotations

import hashlib
import inspect
import json
from dataclasses import FrozenInstanceError, fields, is_dataclass, replace
from datetime import datetime, timedelta
from enum import Enum
from typing import get_type_hints
from uuid import uuid4

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.errors import BusinessError
from app.modules.auth.models import T_User
from app.modules.system import grant_evidence_source_service as service
from app.modules.system.models import (
    CustomerDecisionGate,
    GrantEvidenceSourceConfig,
    GrantEvidenceSourceRecord,
)

AS_OF = datetime(2026, 8, 10, 12, 0, 0, 123456)
DECISION_SOURCE = "docs/product/v8/customer-decisions/2026-08-10-v8-full-batch-scheme-a.txt"
DECISION_VERSION = "customer-decision:2026-08-10:v8-full-batch-scheme-a:v1"


def _add_user(transaction: Session, username: str) -> str:
    user_id = str(uuid4())
    transaction.add(
        T_User(
            id=user_id,
            username=username,
            display_name=username,
            password_hash="test-only",
            is_active=True,
        )
    )
    return user_id


def _actors(transaction: Session) -> tuple[str, str, str]:
    actor_ids = tuple(_add_user(transaction, f"grant-source-{uuid4()}") for _ in range(3))
    transaction.commit()
    return actor_ids


def _install_gate(transaction: Session, actor_id: str) -> None:
    transaction.add(
        CustomerDecisionGate(
            id=str(uuid4()),
            gate_code="DG-GRANT-EVIDENCE-SOURCE",
            scope_key="GLOBAL",
            decision_value="APPROVED_POLICY",
            decision_status="CONFIRMED",
            source_reference=DECISION_SOURCE,
            source_version=DECISION_VERSION,
            confirmed_by=actor_id,
            effective_at=AS_OF - timedelta(days=1),
            supersedes_gate_id=None,
            decision_snapshot="test-only-gate-snapshot",
            idempotency_key=f"gate-{uuid4()}",
            current_identity_key="DG-GRANT-EVIDENCE-SOURCE|GLOBAL",
        )
    )
    transaction.commit()


def _register_command(
    actor_id: str,
    *,
    source_code: str = "CNIPA-GRANT-ANNOUNCEMENT",
    source_version: str = "2026-08-v1",
    evidence_scope: service.GrantEvidenceScope = service.GrantEvidenceScope.GRANT_ANNOUNCEMENT,
    supersedes_source_id: str | None = None,
    idempotency_key: str | None = None,
) -> service.RegisterGrantEvidenceSourceCommand:
    return service.RegisterGrantEvidenceSourceCommand(
        source_code=source_code,
        source_version=source_version,
        evidence_scope=evidence_scope,
        source_reference_kind=service.GrantEvidenceSourceReferenceKind.QUERY_CHANNEL,
        source_reference_value="https://www.cnipa.gov.cn/test-only",
        acquisition_method="SYNTHETIC_TEST_ONLY",
        effective_from=AS_OF - timedelta(days=10),
        effective_to=None,
        supersedes_source_id=supersedes_source_id,
        actor_id=actor_id,
        idempotency_key=idempotency_key or f"register-{uuid4()}",
    )


def _review(
    transaction: Session,
    source_record_id: str,
    reviewer_id: str,
    *,
    decision: service.GrantEvidenceSourceReviewDecision = (
        service.GrantEvidenceSourceReviewDecision.APPROVED
    ),
) -> service.GrantEvidenceSourceRecordResult:
    return service.review_grant_evidence_source(
        service.ReviewGrantEvidenceSourceCommand(
            source_record_id=source_record_id,
            decision=decision,
            reviewer_id=reviewer_id,
            reviewed_at=AS_OF - timedelta(days=2),
            reason="synthetic independent review",
        ),
        transaction,
    )


def _activate(
    transaction: Session,
    source_record_id: str,
    actor_id: str,
    expected_current_source_id: str | None,
) -> service.GrantEvidenceSourceRecordResult:
    return service.activate_grant_evidence_source(
        service.ActivateGrantEvidenceSourceCommand(
            source_record_id=source_record_id,
            actor_id=actor_id,
            activated_at=AS_OF - timedelta(days=1),
            expected_current_source_id=expected_current_source_id,
        ),
        transaction,
    )


def _publish(
    transaction: Session,
    source_record_id: str,
    selected_by: str,
    *,
    evidence_scope: service.GrantEvidenceScope = service.GrantEvidenceScope.GRANT_ANNOUNCEMENT,
    config_version: str = "config-v1",
    expected_current_config_id: str | None = None,
    idempotency_key: str | None = None,
) -> service.GrantEvidenceSourceConfigResult:
    return service.publish_grant_evidence_source_config(
        service.PublishGrantEvidenceSourceConfigCommand(
            evidence_scope=evidence_scope,
            source_record_id=source_record_id,
            config_version=config_version,
            effective_from=AS_OF - timedelta(hours=1),
            effective_to=None,
            selected_by=selected_by,
            published_at=AS_OF - timedelta(hours=2),
            selection_reason="synthetic test publication",
            expected_current_config_id=expected_current_config_id,
            idempotency_key=idempotency_key or f"publish-{uuid4()}",
        ),
        transaction,
    )


def _assert_error(call, code: str, status_code: int, details: dict | None = None) -> BusinessError:
    with pytest.raises(BusinessError) as caught:
        call()
    assert caught.value.code == code
    assert caught.value.status_code == status_code
    if details is not None:
        assert caught.value.details == details
    return caught.value


def test_public_contract_is_exact_frozen_keyword_only_and_synchronous() -> None:
    enum_values = {
        service.GrantEvidenceScope: ("GRANT_ANNOUNCEMENT", "PATENT_REGISTER"),
        service.GrantEvidenceSourceReferenceKind: ("DATA", "QUERY_CHANNEL", "FILE"),
        service.GrantEvidenceSourceReviewDecision: ("APPROVED", "REJECTED"),
        service.GrantEvidenceSourceDisposition: ("CREATED", "CHANGED", "REUSED"),
    }
    for enum_type, expected in enum_values.items():
        assert issubclass(enum_type, str)
        assert tuple(item.value for item in enum_type) == expected

    dto_fields = {
        service.RegisterGrantEvidenceSourceCommand: (
            "source_code",
            "source_version",
            "evidence_scope",
            "source_reference_kind",
            "source_reference_value",
            "acquisition_method",
            "effective_from",
            "effective_to",
            "supersedes_source_id",
            "actor_id",
            "idempotency_key",
        ),
        service.ReviewGrantEvidenceSourceCommand: (
            "source_record_id",
            "decision",
            "reviewer_id",
            "reviewed_at",
            "reason",
        ),
        service.ActivateGrantEvidenceSourceCommand: (
            "source_record_id",
            "actor_id",
            "activated_at",
            "expected_current_source_id",
        ),
        service.RetireGrantEvidenceSourceCommand: (
            "source_record_id",
            "actor_id",
            "retired_at",
            "expected_current_source_id",
        ),
        service.PublishGrantEvidenceSourceConfigCommand: (
            "evidence_scope",
            "source_record_id",
            "config_version",
            "effective_from",
            "effective_to",
            "selected_by",
            "published_at",
            "selection_reason",
            "expected_current_config_id",
            "idempotency_key",
        ),
        service.RevokeGrantEvidenceSourceConfigCommand: (
            "evidence_scope",
            "config_version",
            "effective_from",
            "selected_by",
            "published_at",
            "selection_reason",
            "expected_current_config_id",
            "idempotency_key",
        ),
        service.ResolveGrantEvidenceSourceCommand: ("evidence_scope", "as_of"),
        service.GrantEvidenceSourceRecordResult: (
            "source_record_id",
            "review_status",
            "activation_status",
            "source_snapshot_hash",
            "current_identity_key",
            "disposition",
        ),
        service.GrantEvidenceSourceConfigResult: (
            "config_id",
            "config_status",
            "config_snapshot_hash",
            "current_identity_key",
            "disposition",
        ),
        service.GrantEvidenceSourceResolution: (
            "gate_id",
            "config_id",
            "config_snapshot_hash",
            "source_record_id",
            "evidence_scope",
            "source_code",
            "source_version",
            "source_snapshot_hash",
            "source_reference_kind",
            "source_reference_value",
            "acquisition_method",
            "effective_from",
            "effective_to",
        ),
    }
    for dto_type, expected in dto_fields.items():
        assert is_dataclass(dto_type)
        assert dto_type.__dataclass_params__.frozen is True
        assert tuple(field.name for field in fields(dto_type)) == expected
        assert dto_type.__slots__ == expected
        assert all(
            parameter.kind is inspect.Parameter.KEYWORD_ONLY
            for parameter in inspect.signature(dto_type).parameters.values()
        )

    functions = (
        service.register_grant_evidence_source,
        service.review_grant_evidence_source,
        service.activate_grant_evidence_source,
        service.retire_grant_evidence_source,
        service.publish_grant_evidence_source_config,
        service.revoke_grant_evidence_source_config,
        service.resolve_grant_evidence_source,
    )
    for function in functions:
        assert tuple(inspect.signature(function).parameters) == ("command", "transaction")
        assert get_type_hints(function)["transaction"] is Session
        assert inspect.iscoroutinefunction(function) is False

    command = _register_command(str(uuid4()))
    with pytest.raises(FrozenInstanceError):
        command.source_code = "changed"


def test_registration_builds_canonical_snapshot_replays_and_never_activates(
    session_factory,
) -> None:
    with session_factory() as transaction:
        actor_id, reviewer_id, _ = _actors(transaction)
        key = f"register-{uuid4()}"
        command = _register_command(actor_id, idempotency_key=key)
        created = service.register_grant_evidence_source(command, transaction)
        assert created.disposition is service.GrantEvidenceSourceDisposition.CREATED
        assert created.review_status == "PENDING"
        assert created.activation_status == "INACTIVE"
        assert created.current_identity_key is None
        row = transaction.get(GrantEvidenceSourceRecord, created.source_record_id)
        assert row is not None
        expected_snapshot = json.dumps(
            {
                "acquisition_method": command.acquisition_method,
                "effective_from": command.effective_from.isoformat(timespec="microseconds"),
                "effective_to": None,
                "evidence_scope": command.evidence_scope.value,
                "schema_version": "CNIPA_GRANT_EVIDENCE_SOURCE_V1",
                "source_authority": "CNIPA",
                "source_code": command.source_code,
                "source_reference_kind": command.source_reference_kind.value,
                "source_reference_value": command.source_reference_value,
                "source_version": command.source_version,
            },
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        assert row.source_snapshot == expected_snapshot
        assert row.source_snapshot_hash == hashlib.sha256(expected_snapshot.encode()).hexdigest()
        assert row.created_by == row.updated_by == actor_id
        assert row.reviewed_by is row.activated_by is None
        assert service.register_grant_evidence_source(command, transaction).disposition is (
            service.GrantEvidenceSourceDisposition.REUSED
        )
        _review(transaction, row.id, reviewer_id)
        replay = service.register_grant_evidence_source(command, transaction)
        assert replay.review_status == "APPROVED"
        assert replay.disposition is service.GrantEvidenceSourceDisposition.REUSED
        changed = replace(command, source_version="changed")
        _assert_error(
            lambda: service.register_grant_evidence_source(changed, transaction),
            "GRANT_EVIDENCE_SOURCE_CONFLICT",
            409,
        )


def test_review_activation_replacement_replay_and_explicit_retirement_are_exact(
    session_factory,
) -> None:
    with session_factory() as transaction:
        creator, reviewer, activator = _actors(transaction)
        first = service.register_grant_evidence_source(_register_command(creator), transaction)
        reviewed = _review(transaction, first.source_record_id, reviewer)
        assert reviewed.disposition is service.GrantEvidenceSourceDisposition.CHANGED
        assert _review(transaction, first.source_record_id, reviewer).disposition is (
            service.GrantEvidenceSourceDisposition.REUSED
        )
        activated = _activate(transaction, first.source_record_id, activator, None)
        assert activated.activation_status == "ACTIVE"
        assert activated.current_identity_key == (
            "CNIPA|GRANT_ANNOUNCEMENT|CNIPA-GRANT-ANNOUNCEMENT"
        )
        assert _activate(transaction, first.source_record_id, activator, None).disposition is (
            service.GrantEvidenceSourceDisposition.REUSED
        )

        second = service.register_grant_evidence_source(
            _register_command(
                creator,
                source_version="2026-08-v2",
                supersedes_source_id=first.source_record_id,
            ),
            transaction,
        )
        _review(transaction, second.source_record_id, reviewer)
        _activate(transaction, second.source_record_id, activator, first.source_record_id)
        first_row = transaction.get(GrantEvidenceSourceRecord, first.source_record_id)
        second_row = transaction.get(GrantEvidenceSourceRecord, second.source_record_id)
        assert first_row.activation_status == "RETIRED"
        assert first_row.current_identity_key is None
        assert second_row.activation_status == "ACTIVE"

        retired = service.retire_grant_evidence_source(
            service.RetireGrantEvidenceSourceCommand(
                source_record_id=second.source_record_id,
                actor_id=activator,
                retired_at=AS_OF,
                expected_current_source_id=second.source_record_id,
            ),
            transaction,
        )
        assert retired.disposition is service.GrantEvidenceSourceDisposition.CHANGED
        _assert_error(
            lambda: service.retire_grant_evidence_source(
                service.RetireGrantEvidenceSourceCommand(
                    source_record_id=second.source_record_id,
                    actor_id=activator,
                    retired_at=AS_OF,
                    expected_current_source_id=second.source_record_id,
                ),
                transaction,
            ),
            "GRANT_EVIDENCE_SOURCE_CONFLICT",
            409,
        )


def test_publish_resolve_revoke_and_replay_are_fail_closed(session_factory) -> None:
    with session_factory() as transaction:
        creator, reviewer, selector = _actors(transaction)
        _install_gate(transaction, selector)
        registered = service.register_grant_evidence_source(_register_command(creator), transaction)
        _review(transaction, registered.source_record_id, reviewer)
        _activate(transaction, registered.source_record_id, selector, None)
        key = f"publish-{uuid4()}"
        published = _publish(
            transaction,
            registered.source_record_id,
            selector,
            idempotency_key=key,
        )
        assert published.config_status == "ACTIVE"
        assert published.disposition is service.GrantEvidenceSourceDisposition.CREATED
        replay = _publish(
            transaction,
            registered.source_record_id,
            selector,
            idempotency_key=key,
        )
        assert replay == service.GrantEvidenceSourceConfigResult(
            config_id=published.config_id,
            config_status="ACTIVE",
            config_snapshot_hash=published.config_snapshot_hash,
            current_identity_key=published.current_identity_key,
            disposition=service.GrantEvidenceSourceDisposition.REUSED,
        )

        before = tuple(
            transaction.scalar(select(func.count()).select_from(model))
            for model in (GrantEvidenceSourceRecord, GrantEvidenceSourceConfig)
        )
        resolved = service.resolve_grant_evidence_source(
            service.ResolveGrantEvidenceSourceCommand(
                evidence_scope=service.GrantEvidenceScope.GRANT_ANNOUNCEMENT,
                as_of=AS_OF,
            ),
            transaction,
        )
        after = tuple(
            transaction.scalar(select(func.count()).select_from(model))
            for model in (GrantEvidenceSourceRecord, GrantEvidenceSourceConfig)
        )
        assert after == before
        assert resolved.config_id == published.config_id
        assert resolved.source_record_id == registered.source_record_id
        assert resolved.source_snapshot_hash == registered.source_snapshot_hash
        assert resolved.config_snapshot_hash == published.config_snapshot_hash

        successor = service.register_grant_evidence_source(
            _register_command(
                creator,
                source_version="2026-08-v2",
                supersedes_source_id=registered.source_record_id,
            ),
            transaction,
        )
        _review(transaction, successor.source_record_id, reviewer)
        _activate(transaction, successor.source_record_id, selector, registered.source_record_id)
        historical_replay = _publish(
            transaction,
            registered.source_record_id,
            selector,
            idempotency_key=key,
        )
        assert historical_replay.config_id == published.config_id
        assert historical_replay.disposition is service.GrantEvidenceSourceDisposition.REUSED

        revoked = service.revoke_grant_evidence_source_config(
            service.RevokeGrantEvidenceSourceConfigCommand(
                evidence_scope=service.GrantEvidenceScope.GRANT_ANNOUNCEMENT,
                config_version="config-v2-revoked",
                effective_from=AS_OF,
                selected_by=selector,
                published_at=AS_OF,
                selection_reason="synthetic test revocation",
                expected_current_config_id=published.config_id,
                idempotency_key=f"revoke-{uuid4()}",
            ),
            transaction,
        )
        assert revoked.config_status == "REVOKED"
        _assert_error(
            lambda: service.resolve_grant_evidence_source(
                service.ResolveGrantEvidenceSourceCommand(
                    evidence_scope=service.GrantEvidenceScope.GRANT_ANNOUNCEMENT,
                    as_of=AS_OF,
                ),
                transaction,
            ),
            "GRANT_EVIDENCE_SOURCE_CONFLICT",
            409,
        )


class _ScopeLookalike(str, Enum):
    GRANT_ANNOUNCEMENT = "GRANT_ANNOUNCEMENT"


@pytest.mark.parametrize(
    ("change", "field"),
    [
        ({"evidence_scope": "GRANT_ANNOUNCEMENT"}, "evidence_scope"),
        ({"evidence_scope": _ScopeLookalike.GRANT_ANNOUNCEMENT}, "evidence_scope"),
        ({"source_code": " source"}, "source_code"),
        ({"source_code": ""}, "source_code"),
        ({"actor_id": "not-a-uuid"}, "actor_id"),
        (
            {"effective_from": AS_OF.replace(tzinfo=datetime.now().astimezone().tzinfo)},
            "effective_from",
        ),
        ({"effective_to": AS_OF - timedelta(days=20)}, "effective_to"),
    ],
)
def test_invalid_registration_fails_400_before_query(
    session_factory, change: dict[str, object], field: str
) -> None:
    with session_factory() as transaction:
        command = _register_command(str(uuid4()))
        values = {field.name: getattr(command, field.name) for field in fields(command)}
        values.update(change)
        invalid = service.RegisterGrantEvidenceSourceCommand(**values)
        _assert_error(
            lambda: service.register_grant_evidence_source(invalid, transaction),
            "GRANT_EVIDENCE_SOURCE_INPUT_INVALID",
            400,
            {"field": field},
        )
        assert transaction.get_transaction() is None


def test_dirty_session_fails_before_gate_query_or_flush(session_factory) -> None:
    with session_factory() as transaction:
        actor_id = _add_user(transaction, f"dirty-{uuid4()}")
        _assert_error(
            lambda: service.register_grant_evidence_source(
                _register_command(actor_id), transaction
            ),
            "GRANT_EVIDENCE_SOURCE_TRANSACTION_DIRTY",
            409,
        )
        assert transaction.new


def test_caller_rollback_removes_complete_write(session_factory) -> None:
    actor_id: str
    with session_factory() as transaction:
        actor_id, _, _ = _actors(transaction)
        created = service.register_grant_evidence_source(_register_command(actor_id), transaction)
        source_id = created.source_record_id
        transaction.rollback()
    with session_factory() as transaction:
        assert transaction.get(GrantEvidenceSourceRecord, source_id) is None
