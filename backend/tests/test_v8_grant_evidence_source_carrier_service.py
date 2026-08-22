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
from app.modules.documents.models import GrantEvidenceCandidate
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


def _active_source_and_gate(
    transaction: Session,
    *,
    evidence_scope: service.GrantEvidenceScope = service.GrantEvidenceScope.GRANT_ANNOUNCEMENT,
) -> tuple[str, str, str, service.GrantEvidenceSourceRecordResult]:
    creator, reviewer, selector = _actors(transaction)
    _install_gate(transaction, selector)
    registered = service.register_grant_evidence_source(
        _register_command(
            creator,
            source_code=f"CNIPA-{evidence_scope.value}",
            evidence_scope=evidence_scope,
        ),
        transaction,
    )
    _review(transaction, registered.source_record_id, reviewer)
    _activate(transaction, registered.source_record_id, selector, None)
    return creator, reviewer, selector, registered


def _expected_config_snapshot(
    command: service.PublishGrantEvidenceSourceConfigCommand,
    source: GrantEvidenceSourceRecord,
    *,
    config_status: str = "ACTIVE",
) -> str:
    return json.dumps(
        {
            "config_status": config_status,
            "config_version": command.config_version,
            "effective_from": command.effective_from.isoformat(timespec="microseconds"),
            "effective_to": (
                command.effective_to.isoformat(timespec="microseconds")
                if command.effective_to is not None
                else None
            ),
            "evidence_scope": command.evidence_scope.value,
            "expected_current_config_id": command.expected_current_config_id,
            "gate_code": "DG-GRANT-EVIDENCE-SOURCE",
            "published_at": command.published_at.isoformat(timespec="microseconds"),
            "schema_version": "CNIPA_GRANT_EVIDENCE_CONFIG_V1",
            "scope_key": "GLOBAL",
            "selected_by": command.selected_by,
            "selection_reason": command.selection_reason,
            "source_record_id": source.id,
            "source_snapshot_hash": source.source_snapshot_hash,
            "source_version": source.source_version,
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
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

    assert get_type_hints(service.RegisterGrantEvidenceSourceCommand) == {
        "source_code": str,
        "source_version": str,
        "evidence_scope": service.GrantEvidenceScope,
        "source_reference_kind": service.GrantEvidenceSourceReferenceKind,
        "source_reference_value": str,
        "acquisition_method": str,
        "effective_from": datetime,
        "effective_to": datetime | None,
        "supersedes_source_id": str | None,
        "actor_id": str,
        "idempotency_key": str,
    }
    assert get_type_hints(service.ReviewGrantEvidenceSourceCommand) == {
        "source_record_id": str,
        "decision": service.GrantEvidenceSourceReviewDecision,
        "reviewer_id": str,
        "reviewed_at": datetime,
        "reason": str,
    }
    assert get_type_hints(service.ActivateGrantEvidenceSourceCommand) == {
        "source_record_id": str,
        "actor_id": str,
        "activated_at": datetime,
        "expected_current_source_id": str | None,
    }
    assert get_type_hints(service.RetireGrantEvidenceSourceCommand) == {
        "source_record_id": str,
        "actor_id": str,
        "retired_at": datetime,
        "expected_current_source_id": str,
    }
    assert get_type_hints(service.PublishGrantEvidenceSourceConfigCommand) == {
        "evidence_scope": service.GrantEvidenceScope,
        "source_record_id": str,
        "config_version": str,
        "effective_from": datetime,
        "effective_to": datetime | None,
        "selected_by": str,
        "published_at": datetime,
        "selection_reason": str,
        "expected_current_config_id": str | None,
        "idempotency_key": str,
    }
    assert get_type_hints(service.RevokeGrantEvidenceSourceConfigCommand) == {
        "evidence_scope": service.GrantEvidenceScope,
        "config_version": str,
        "effective_from": datetime,
        "selected_by": str,
        "published_at": datetime,
        "selection_reason": str,
        "expected_current_config_id": str,
        "idempotency_key": str,
    }
    assert get_type_hints(service.ResolveGrantEvidenceSourceCommand) == {
        "evidence_scope": service.GrantEvidenceScope,
        "as_of": datetime,
    }
    assert get_type_hints(service.GrantEvidenceSourceRecordResult) == {
        "source_record_id": str,
        "review_status": str,
        "activation_status": str,
        "source_snapshot_hash": str,
        "current_identity_key": str | None,
        "disposition": service.GrantEvidenceSourceDisposition,
    }
    assert get_type_hints(service.GrantEvidenceSourceConfigResult) == {
        "config_id": str,
        "config_status": str,
        "config_snapshot_hash": str,
        "current_identity_key": str | None,
        "disposition": service.GrantEvidenceSourceDisposition,
    }
    assert get_type_hints(service.GrantEvidenceSourceResolution) == {
        "gate_id": str,
        "config_id": str,
        "config_snapshot_hash": str,
        "source_record_id": str,
        "evidence_scope": service.GrantEvidenceScope,
        "source_code": str,
        "source_version": str,
        "source_snapshot_hash": str,
        "source_reference_kind": service.GrantEvidenceSourceReferenceKind,
        "source_reference_value": str,
        "acquisition_method": str,
        "effective_from": datetime,
        "effective_to": datetime | None,
    }

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
        actor_id, reviewer_id, other_actor_id = _actors(transaction)
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
        for replay_actor_id in (other_actor_id, str(uuid4())):
            before = transaction.scalar(select(func.count()).select_from(GrantEvidenceSourceRecord))
            _assert_error(
                lambda replay_actor_id=replay_actor_id: service.register_grant_evidence_source(
                    replace(command, actor_id=replay_actor_id), transaction
                ),
                "GRANT_EVIDENCE_SOURCE_CONFLICT",
                409,
            )
            assert (
                transaction.scalar(select(func.count()).select_from(GrantEvidenceSourceRecord))
                == before
            )
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
        _assert_error(
            lambda: _review(transaction, first.source_record_id, creator),
            "GRANT_EVIDENCE_SOURCE_CONFLICT",
            409,
        )
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
        _assert_error(
            lambda: service.activate_grant_evidence_source(
                service.ActivateGrantEvidenceSourceCommand(
                    source_record_id=first.source_record_id,
                    actor_id=reviewer,
                    activated_at=AS_OF - timedelta(days=1),
                    expected_current_source_id=None,
                ),
                transaction,
            ),
            "GRANT_EVIDENCE_SOURCE_CONFLICT",
            409,
        )

        rejected = service.register_grant_evidence_source(
            _register_command(
                creator,
                source_code="CNIPA-REJECTED-TEST",
                source_version="rejected-v1",
            ),
            transaction,
        )
        rejected_result = _review(
            transaction,
            rejected.source_record_id,
            reviewer,
            decision=service.GrantEvidenceSourceReviewDecision.REJECTED,
        )
        assert rejected_result.review_status == "REJECTED"
        _assert_error(
            lambda: _activate(transaction, rejected.source_record_id, activator, None),
            "GRANT_EVIDENCE_SOURCE_CONFLICT",
            409,
        )
        _assert_error(
            lambda: service.review_grant_evidence_source(
                service.ReviewGrantEvidenceSourceCommand(
                    source_record_id=rejected.source_record_id,
                    decision=service.GrantEvidenceSourceReviewDecision.APPROVED,
                    reviewer_id=reviewer,
                    reviewed_at=AS_OF - timedelta(days=2),
                    reason="changed terminal review",
                ),
                transaction,
            ),
            "GRANT_EVIDENCE_SOURCE_CONFLICT",
            409,
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
        collision = service.register_grant_evidence_source(
            _register_command(
                creator,
                source_version="2026-08-v3",
                supersedes_source_id=first.source_record_id,
            ),
            transaction,
        )
        _review(transaction, collision.source_record_id, reviewer)
        _assert_error(
            lambda: _activate(transaction, second.source_record_id, activator, None),
            "GRANT_EVIDENCE_SOURCE_CONFLICT",
            409,
        )
        assert (
            transaction.get(GrantEvidenceSourceRecord, first.source_record_id).activation_status
            == "ACTIVE"
        )
        assert (
            transaction.get(GrantEvidenceSourceRecord, second.source_record_id).activation_status
            == "INACTIVE"
        )
        _activate(transaction, second.source_record_id, activator, first.source_record_id)
        first_row = transaction.get(GrantEvidenceSourceRecord, first.source_record_id)
        second_row = transaction.get(GrantEvidenceSourceRecord, second.source_record_id)
        assert first_row.activation_status == "RETIRED"
        assert first_row.current_identity_key is None
        assert second_row.activation_status == "ACTIVE"
        _assert_error(
            lambda: _activate(
                transaction,
                collision.source_record_id,
                activator,
                first.source_record_id,
            ),
            "GRANT_EVIDENCE_SOURCE_CONFLICT",
            409,
        )
        assert transaction.get(
            GrantEvidenceSourceRecord, second.source_record_id
        ).current_identity_key == ("CNIPA|GRANT_ANNOUNCEMENT|CNIPA-GRANT-ANNOUNCEMENT")
        assert (
            transaction.get(GrantEvidenceSourceRecord, collision.source_record_id).activation_status
            == "INACTIVE"
        )

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


@pytest.mark.parametrize("evidence_scope", tuple(service.GrantEvidenceScope))
def test_publish_resolve_revoke_and_replay_are_fail_closed(
    session_factory, evidence_scope: service.GrantEvidenceScope
) -> None:
    with session_factory() as transaction:
        creator, reviewer, selector = _actors(transaction)
        _install_gate(transaction, selector)
        source_code = f"CNIPA-{evidence_scope.value}"
        registered = service.register_grant_evidence_source(
            _register_command(
                creator,
                source_code=source_code,
                evidence_scope=evidence_scope,
            ),
            transaction,
        )
        _review(transaction, registered.source_record_id, reviewer)
        _activate(transaction, registered.source_record_id, selector, None)
        key = f"publish-{uuid4()}"
        publish_command = service.PublishGrantEvidenceSourceConfigCommand(
            evidence_scope=evidence_scope,
            source_record_id=registered.source_record_id,
            config_version="config-v1",
            effective_from=AS_OF - timedelta(hours=1),
            effective_to=None,
            selected_by=selector,
            published_at=AS_OF - timedelta(hours=2),
            selection_reason="synthetic test publication",
            expected_current_config_id=None,
            idempotency_key=key,
        )
        published = service.publish_grant_evidence_source_config(
            publish_command,
            transaction,
        )
        assert published.config_status == "ACTIVE"
        assert published.disposition is service.GrantEvidenceSourceDisposition.CREATED
        source_row = transaction.get(GrantEvidenceSourceRecord, registered.source_record_id)
        config_row = transaction.get(GrantEvidenceSourceConfig, published.config_id)
        expected_snapshot = _expected_config_snapshot(publish_command, source_row)
        assert config_row.config_snapshot == expected_snapshot
        assert (
            config_row.config_snapshot_hash
            == hashlib.sha256(expected_snapshot.encode()).hexdigest()
        )
        assert config_row.supersedes_config_id is None
        replay = service.publish_grant_evidence_source_config(
            publish_command,
            transaction,
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
                evidence_scope=evidence_scope,
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

        revoke_command = service.RevokeGrantEvidenceSourceConfigCommand(
            evidence_scope=evidence_scope,
            config_version="config-v2-revoked",
            effective_from=AS_OF,
            selected_by=selector,
            published_at=AS_OF,
            selection_reason="synthetic test revocation",
            expected_current_config_id=published.config_id,
            idempotency_key=f"revoke-{uuid4()}",
        )
        revoked = service.revoke_grant_evidence_source_config(revoke_command, transaction)
        assert revoked.config_status == "REVOKED"
        revoked_row = transaction.get(GrantEvidenceSourceConfig, revoked.config_id)
        revoke_snapshot_command = service.PublishGrantEvidenceSourceConfigCommand(
            evidence_scope=evidence_scope,
            source_record_id=registered.source_record_id,
            config_version=revoke_command.config_version,
            effective_from=revoke_command.effective_from,
            effective_to=None,
            selected_by=revoke_command.selected_by,
            published_at=revoke_command.published_at,
            selection_reason=revoke_command.selection_reason,
            expected_current_config_id=published.config_id,
            idempotency_key=revoke_command.idempotency_key,
        )
        expected_revoke_snapshot = _expected_config_snapshot(
            revoke_snapshot_command,
            source_row,
            config_status="REVOKED",
        )
        assert revoked_row.config_snapshot == expected_revoke_snapshot
        assert (
            revoked_row.config_snapshot_hash
            == hashlib.sha256(expected_revoke_snapshot.encode()).hexdigest()
        )
        assert revoked_row.supersedes_config_id == published.config_id
        assert (
            service.revoke_grant_evidence_source_config(revoke_command, transaction).disposition
            is service.GrantEvidenceSourceDisposition.REUSED
        )
        _assert_error(
            lambda: service.resolve_grant_evidence_source(
                service.ResolveGrantEvidenceSourceCommand(
                    evidence_scope=evidence_scope,
                    as_of=AS_OF,
                ),
                transaction,
            ),
            "GRANT_EVIDENCE_SOURCE_CONFLICT",
            409,
        )

        successor = service.register_grant_evidence_source(
            _register_command(
                creator,
                source_code=source_code,
                source_version="2026-08-v2",
                evidence_scope=evidence_scope,
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
            evidence_scope=evidence_scope,
            idempotency_key=key,
        )
        assert historical_replay.config_id == published.config_id
        assert historical_replay.disposition is service.GrantEvidenceSourceDisposition.REUSED


def test_revoke_requires_linked_source_to_remain_reviewed_active_current_and_effective(
    session_factory,
) -> None:
    with session_factory() as transaction:
        creator, reviewer, selector, registered = _active_source_and_gate(transaction)
        published = _publish(transaction, registered.source_record_id, selector)
        successor = service.register_grant_evidence_source(
            _register_command(
                creator,
                source_code="CNIPA-GRANT_ANNOUNCEMENT",
                source_version="2026-08-v2",
                supersedes_source_id=registered.source_record_id,
            ),
            transaction,
        )
        _review(transaction, successor.source_record_id, reviewer)
        _activate(transaction, successor.source_record_id, selector, registered.source_record_id)
        before = transaction.scalar(select(func.count()).select_from(GrantEvidenceSourceConfig))
        _assert_error(
            lambda: service.revoke_grant_evidence_source_config(
                service.RevokeGrantEvidenceSourceConfigCommand(
                    evidence_scope=service.GrantEvidenceScope.GRANT_ANNOUNCEMENT,
                    config_version="revoke-after-retirement",
                    effective_from=AS_OF,
                    selected_by=selector,
                    published_at=AS_OF,
                    selection_reason="must fail closed",
                    expected_current_config_id=published.config_id,
                    idempotency_key=f"revoke-{uuid4()}",
                ),
                transaction,
            ),
            "GRANT_EVIDENCE_SOURCE_CONFLICT",
            409,
        )
        assert (
            transaction.scalar(select(func.count()).select_from(GrantEvidenceSourceConfig))
            == before
        )
        current = transaction.get(GrantEvidenceSourceConfig, published.config_id)
        assert current.current_identity_key == (
            "DG-GRANT-EVIDENCE-SOURCE|GLOBAL|GRANT_ANNOUNCEMENT"
        )


@pytest.mark.parametrize(
    "corruption", ("source", "revoke_bound_lineage", "predecessor_bound_lineage")
)
def test_revoke_replay_validates_actual_immutable_source_lineage(
    session_factory, corruption: str
) -> None:
    with session_factory() as transaction:
        _, _, selector, registered = _active_source_and_gate(transaction)
        published = _publish(transaction, registered.source_record_id, selector)
        command = service.RevokeGrantEvidenceSourceConfigCommand(
            evidence_scope=service.GrantEvidenceScope.GRANT_ANNOUNCEMENT,
            config_version="config-revoked",
            effective_from=AS_OF,
            selected_by=selector,
            published_at=AS_OF,
            selection_reason="synthetic replay lineage",
            expected_current_config_id=published.config_id,
            idempotency_key=f"revoke-{uuid4()}",
        )
        revoked = service.revoke_grant_evidence_source_config(command, transaction)
        if corruption == "source":
            transaction.get(
                GrantEvidenceSourceRecord, registered.source_record_id
            ).source_snapshot_hash = "0" * 64
        else:
            config_id = (
                revoked.config_id if corruption == "revoke_bound_lineage" else published.config_id
            )
            config = transaction.get(GrantEvidenceSourceConfig, config_id)
            snapshot = json.loads(config.config_snapshot)
            snapshot["source_snapshot_hash"] = "1" * 64
            config.config_snapshot = json.dumps(
                snapshot,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
                allow_nan=False,
            )
            config.config_snapshot_hash = hashlib.sha256(
                config.config_snapshot.encode()
            ).hexdigest()
        transaction.flush()
        before = transaction.scalar(select(func.count()).select_from(GrantEvidenceSourceConfig))
        _assert_error(
            lambda: service.revoke_grant_evidence_source_config(command, transaction),
            "GRANT_EVIDENCE_SOURCE_CONFLICT",
            409,
        )
        assert (
            transaction.scalar(select(func.count()).select_from(GrantEvidenceSourceConfig))
            == before
        )


def test_publish_replay_binds_selected_actor_and_current_cas(session_factory) -> None:
    with session_factory() as transaction:
        _, _, selector, registered = _active_source_and_gate(transaction)
        other_selector = _add_user(transaction, f"other-selector-{uuid4()}")
        transaction.commit()
        key = f"publish-{uuid4()}"
        published = _publish(
            transaction,
            registered.source_record_id,
            selector,
            idempotency_key=key,
        )
        before = transaction.scalar(select(func.count()).select_from(GrantEvidenceSourceConfig))
        for replay_selector in (other_selector, str(uuid4())):
            _assert_error(
                lambda replay_selector=replay_selector: _publish(
                    transaction,
                    registered.source_record_id,
                    replay_selector,
                    idempotency_key=key,
                ),
                "GRANT_EVIDENCE_SOURCE_CONFLICT",
                409,
            )
        _assert_error(
            lambda: _publish(
                transaction,
                registered.source_record_id,
                selector,
                config_version="stale-cas",
                expected_current_config_id=str(uuid4()),
            ),
            "GRANT_EVIDENCE_SOURCE_CONFLICT",
            409,
        )
        assert (
            transaction.scalar(select(func.count()).select_from(GrantEvidenceSourceConfig))
            == before
        )
        assert transaction.get(
            GrantEvidenceSourceConfig, published.config_id
        ).current_identity_key == ("DG-GRANT-EVIDENCE-SOURCE|GLOBAL|GRANT_ANNOUNCEMENT")


@pytest.mark.parametrize(
    "corruption",
    (
        "gate_missing",
        "gate_revoked",
        "gate_future",
        "gate_source",
        "gate_version",
        "config_snapshot",
        "source_hash",
    ),
)
def test_gate_and_canonical_corruption_fail_409_without_write(
    session_factory, corruption: str
) -> None:
    with session_factory() as transaction:
        _, _, selector, registered = _active_source_and_gate(transaction)
        if corruption.startswith("gate_"):
            gate = transaction.scalar(select(CustomerDecisionGate))
            if corruption == "gate_missing":
                transaction.delete(gate)
            elif corruption == "gate_revoked":
                gate.decision_status = "REVOKED"
            elif corruption == "gate_future":
                gate.effective_at = AS_OF + timedelta(days=1)
            elif corruption == "gate_source":
                gate.source_reference = "corrupt-source"
            else:
                gate.source_version = "corrupt-version"
            transaction.flush()
            before = transaction.scalar(select(func.count()).select_from(GrantEvidenceSourceConfig))
            with pytest.raises(BusinessError) as caught:
                _publish(transaction, registered.source_record_id, selector)
            assert caught.value.status_code == 409
            assert caught.value.code in {
                "DECISION_GATE_NOT_FOUND",
                "DECISION_GATE_REVOKED",
                "DECISION_GATE_NOT_EFFECTIVE",
                "GRANT_EVIDENCE_SOURCE_CONFLICT",
            }
            assert (
                transaction.scalar(select(func.count()).select_from(GrantEvidenceSourceConfig))
                == before
            )
            return

        published = _publish(transaction, registered.source_record_id, selector)
        if corruption == "config_snapshot":
            transaction.get(GrantEvidenceSourceConfig, published.config_id).config_snapshot = "{}"
        else:
            transaction.get(
                GrantEvidenceSourceRecord, registered.source_record_id
            ).source_snapshot_hash = "0" * 64
        transaction.commit()
        before = tuple(
            transaction.scalar(select(func.count()).select_from(model))
            for model in (
                GrantEvidenceSourceRecord,
                GrantEvidenceSourceConfig,
                GrantEvidenceCandidate,
            )
        )
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
        after = tuple(
            transaction.scalar(select(func.count()).select_from(model))
            for model in (
                GrantEvidenceSourceRecord,
                GrantEvidenceSourceConfig,
                GrantEvidenceCandidate,
            )
        )
        assert after == before


@pytest.mark.parametrize(
    "corruption",
    (
        "source_state",
        "source_scope",
        "config_source_version",
        "source_snapshot",
        "link_lineage",
        "config_multiplicity",
    ),
)
def test_resolution_rejects_source_and_link_lineage_corruption(
    session_factory, monkeypatch, corruption: str
) -> None:
    with session_factory() as transaction:
        creator, reviewer, selector, registered = _active_source_and_gate(transaction)
        published = _publish(transaction, registered.source_record_id, selector)
        source = transaction.get(GrantEvidenceSourceRecord, registered.source_record_id)
        config = transaction.get(GrantEvidenceSourceConfig, published.config_id)
        if corruption == "source_state":
            source.activation_status = "RETIRED"
            source.current_identity_key = None
        elif corruption == "source_scope":
            source.evidence_scope = service.GrantEvidenceScope.PATENT_REGISTER.value
            source.current_identity_key = "CNIPA|PATENT_REGISTER|CNIPA-GRANT_ANNOUNCEMENT"
            snapshot = json.loads(source.source_snapshot)
            snapshot["evidence_scope"] = service.GrantEvidenceScope.PATENT_REGISTER.value
            source.source_snapshot = json.dumps(
                snapshot,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
                allow_nan=False,
            )
            source.source_snapshot_hash = hashlib.sha256(
                source.source_snapshot.encode()
            ).hexdigest()
        elif corruption == "config_source_version":
            snapshot = json.loads(config.config_snapshot)
            snapshot["source_version"] = "corrupt-version"
            config.config_snapshot = json.dumps(
                snapshot,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
                allow_nan=False,
            )
            config.config_snapshot_hash = hashlib.sha256(
                config.config_snapshot.encode()
            ).hexdigest()
        elif corruption == "source_snapshot":
            source.source_snapshot = "{}"
            source.source_snapshot_hash = hashlib.sha256(b"{}").hexdigest()
        elif corruption == "link_lineage":
            other = service.register_grant_evidence_source(
                _register_command(
                    creator,
                    source_code="CNIPA-OTHER-SERIES",
                    source_version="other-v1",
                ),
                transaction,
            )
            _review(transaction, other.source_record_id, reviewer)
            _activate(transaction, other.source_record_id, selector, None)
            snapshot = json.loads(config.config_snapshot)
            snapshot["source_record_id"] = other.source_record_id
            config.source_record_id = other.source_record_id
            config.config_snapshot = json.dumps(
                snapshot,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
                allow_nan=False,
            )
            config.config_snapshot_hash = hashlib.sha256(
                config.config_snapshot.encode()
            ).hexdigest()
        transaction.commit()

        original_scalars = transaction.scalars

        def scalars_with_config_multiplicity(statement, *args, **kwargs):
            rows = original_scalars(statement, *args, **kwargs)
            entity = statement.column_descriptions[0].get("entity")
            if corruption == "config_multiplicity" and entity is GrantEvidenceSourceConfig:
                values = list(rows)
                return values + values
            return rows

        before = tuple(
            transaction.scalar(select(func.count()).select_from(model))
            for model in (
                GrantEvidenceSourceRecord,
                GrantEvidenceSourceConfig,
                GrantEvidenceCandidate,
            )
        )
        with monkeypatch.context() as patch:
            patch.setattr(transaction, "scalars", scalars_with_config_multiplicity)
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
        after = tuple(
            transaction.scalar(select(func.count()).select_from(model))
            for model in (
                GrantEvidenceSourceRecord,
                GrantEvidenceSourceConfig,
                GrantEvidenceCandidate,
            )
        )
        assert after == before


@pytest.mark.parametrize("config_state", ("missing", "future", "expired"))
def test_resolution_requires_one_current_effective_config(
    session_factory, config_state: str
) -> None:
    with session_factory() as transaction:
        _, _, selector, registered = _active_source_and_gate(transaction)
        if config_state != "missing":
            if config_state == "future":
                effective_from = AS_OF + timedelta(seconds=1)
                effective_to = None
            else:
                effective_from = AS_OF - timedelta(hours=2)
                effective_to = AS_OF - timedelta(seconds=1)
            service.publish_grant_evidence_source_config(
                service.PublishGrantEvidenceSourceConfigCommand(
                    evidence_scope=service.GrantEvidenceScope.GRANT_ANNOUNCEMENT,
                    source_record_id=registered.source_record_id,
                    config_version=f"config-{config_state}",
                    effective_from=effective_from,
                    effective_to=effective_to,
                    selected_by=selector,
                    published_at=AS_OF - timedelta(hours=3),
                    selection_reason=f"synthetic {config_state} config",
                    expected_current_config_id=None,
                    idempotency_key=f"publish-{uuid4()}",
                ),
                transaction,
            )
        before = tuple(
            transaction.scalar(select(func.count()).select_from(model))
            for model in (
                GrantEvidenceSourceRecord,
                GrantEvidenceSourceConfig,
                GrantEvidenceCandidate,
            )
        )
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
        after = tuple(
            transaction.scalar(select(func.count()).select_from(model))
            for model in (
                GrantEvidenceSourceRecord,
                GrantEvidenceSourceConfig,
                GrantEvidenceCandidate,
            )
        )
        assert after == before


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


class _NoQueryTransaction:
    @property
    def new(self):
        raise AssertionError("transaction was touched before input rejection")


@pytest.mark.parametrize(
    ("call", "field"),
    (
        (
            lambda transaction: service.review_grant_evidence_source(
                service.ReviewGrantEvidenceSourceCommand(
                    source_record_id="not-a-uuid",
                    decision=service.GrantEvidenceSourceReviewDecision.APPROVED,
                    reviewer_id=str(uuid4()),
                    reviewed_at=AS_OF,
                    reason="review",
                ),
                transaction,
            ),
            "source_record_id",
        ),
        (
            lambda transaction: service.activate_grant_evidence_source(
                service.ActivateGrantEvidenceSourceCommand(
                    source_record_id=str(uuid4()),
                    actor_id="not-a-uuid",
                    activated_at=AS_OF,
                    expected_current_source_id=None,
                ),
                transaction,
            ),
            "actor_id",
        ),
        (
            lambda transaction: service.retire_grant_evidence_source(
                service.RetireGrantEvidenceSourceCommand(
                    source_record_id=str(uuid4()),
                    actor_id=str(uuid4()),
                    retired_at=AS_OF,
                    expected_current_source_id=None,
                ),
                transaction,
            ),
            "expected_current_source_id",
        ),
        (
            lambda transaction: service.publish_grant_evidence_source_config(
                service.PublishGrantEvidenceSourceConfigCommand(
                    evidence_scope="GRANT_ANNOUNCEMENT",
                    source_record_id=str(uuid4()),
                    config_version="v1",
                    effective_from=AS_OF,
                    effective_to=None,
                    selected_by=str(uuid4()),
                    published_at=AS_OF,
                    selection_reason="publish",
                    expected_current_config_id=None,
                    idempotency_key="publish-key",
                ),
                transaction,
            ),
            "evidence_scope",
        ),
        (
            lambda transaction: service.revoke_grant_evidence_source_config(
                service.RevokeGrantEvidenceSourceConfigCommand(
                    evidence_scope=service.GrantEvidenceScope.GRANT_ANNOUNCEMENT,
                    config_version="v2",
                    effective_from=AS_OF.replace(tzinfo=datetime.now().astimezone().tzinfo),
                    selected_by=str(uuid4()),
                    published_at=AS_OF,
                    selection_reason="revoke",
                    expected_current_config_id=str(uuid4()),
                    idempotency_key="revoke-key",
                ),
                transaction,
            ),
            "effective_from",
        ),
        (
            lambda transaction: service.resolve_grant_evidence_source(
                service.ResolveGrantEvidenceSourceCommand(
                    evidence_scope=service.GrantEvidenceScope.GRANT_ANNOUNCEMENT,
                    as_of="not-a-datetime",
                ),
                transaction,
            ),
            "as_of",
        ),
    ),
)
def test_invalid_non_registration_commands_fail_before_transaction_or_query(
    call, field: str
) -> None:
    _assert_error(
        lambda: call(_NoQueryTransaction()),
        "GRANT_EVIDENCE_SOURCE_INPUT_INVALID",
        400,
        {"field": field},
    )


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


@pytest.mark.parametrize("operation", ("activation", "publish", "revoke"))
def test_multi_row_savepoint_fault_leaves_no_partial_transition(
    session_factory, monkeypatch, operation: str
) -> None:
    with session_factory() as transaction:
        if operation == "activation":
            creator, reviewer, actor = _actors(transaction)
            first = service.register_grant_evidence_source(_register_command(creator), transaction)
            _review(transaction, first.source_record_id, reviewer)
            _activate(transaction, first.source_record_id, actor, None)
            target = service.register_grant_evidence_source(
                _register_command(
                    creator,
                    source_version="fault-target-v2",
                    supersedes_source_id=first.source_record_id,
                ),
                transaction,
            )
            _review(transaction, target.source_record_id, reviewer)
            transaction.flush()

            def invoke() -> None:
                _activate(
                    transaction,
                    target.source_record_id,
                    actor,
                    first.source_record_id,
                )

            expected_count = 2
            expected_current_id = first.source_record_id
            expected_inactive_id = target.source_record_id
        else:
            _, _, actor, source = _active_source_and_gate(transaction)
            first_config = _publish(transaction, source.source_record_id, actor)
            transaction.commit()
            if operation == "publish":

                def invoke() -> None:
                    _publish(
                        transaction,
                        source.source_record_id,
                        actor,
                        config_version="fault-config-v2",
                        expected_current_config_id=first_config.config_id,
                    )

            else:

                def invoke() -> None:
                    service.revoke_grant_evidence_source_config(
                        service.RevokeGrantEvidenceSourceConfigCommand(
                            evidence_scope=service.GrantEvidenceScope.GRANT_ANNOUNCEMENT,
                            config_version="fault-revoke-v2",
                            effective_from=AS_OF,
                            selected_by=actor,
                            published_at=AS_OF,
                            selection_reason="forced fault",
                            expected_current_config_id=first_config.config_id,
                            idempotency_key=f"fault-{uuid4()}",
                        ),
                        transaction,
                    )

            expected_count = 1
            expected_current_id = first_config.config_id
            expected_inactive_id = None

        original_flush = transaction.flush
        flush_calls = 0

        def fail_second_flush(objects=None) -> None:
            nonlocal flush_calls
            flush_calls += 1
            if flush_calls == 2:
                raise RuntimeError("forced multi-row flush fault")
            original_flush(objects)

        with monkeypatch.context() as patch:
            patch.setattr(transaction, "flush", fail_second_flush)
            with pytest.raises(RuntimeError, match="forced multi-row flush fault"):
                invoke()
        transaction.expire_all()
        assert not transaction.new
        assert not transaction.dirty
        if operation == "activation":
            assert (
                transaction.scalar(select(func.count()).select_from(GrantEvidenceSourceRecord))
                == expected_count
            )
            assert (
                transaction.get(GrantEvidenceSourceRecord, expected_current_id).activation_status
                == "ACTIVE"
            )
            assert (
                transaction.get(GrantEvidenceSourceRecord, expected_inactive_id).activation_status
                == "INACTIVE"
            )
        else:
            assert (
                transaction.scalar(select(func.count()).select_from(GrantEvidenceSourceConfig))
                == expected_count
            )
            assert transaction.get(
                GrantEvidenceSourceConfig, expected_current_id
            ).current_identity_key == ("DG-GRANT-EVIDENCE-SOURCE|GLOBAL|GRANT_ANNOUNCEMENT")


def test_public_entrypoints_never_commit_rollback_or_close(session_factory, monkeypatch) -> None:
    with session_factory() as transaction:
        creator, reviewer, actor = _actors(transaction)
        _install_gate(transaction, actor)
        prohibited_calls: list[str] = []

        def prohibited(name: str):
            def call(*_args, **_kwargs) -> None:
                prohibited_calls.append(name)
                raise AssertionError(f"service called Session.{name}")

            return call

        with monkeypatch.context() as patch:
            patch.setattr(transaction, "commit", prohibited("commit"))
            patch.setattr(transaction, "rollback", prohibited("rollback"))
            patch.setattr(transaction, "close", prohibited("close"))
            registered = service.register_grant_evidence_source(
                _register_command(creator), transaction
            )
            _review(transaction, registered.source_record_id, reviewer)
            _activate(transaction, registered.source_record_id, actor, None)
            published = _publish(transaction, registered.source_record_id, actor)
            resolution = service.resolve_grant_evidence_source(
                service.ResolveGrantEvidenceSourceCommand(
                    evidence_scope=service.GrantEvidenceScope.GRANT_ANNOUNCEMENT,
                    as_of=AS_OF,
                ),
                transaction,
            )
            assert resolution.config_id == published.config_id
            service.revoke_grant_evidence_source_config(
                service.RevokeGrantEvidenceSourceConfigCommand(
                    evidence_scope=service.GrantEvidenceScope.GRANT_ANNOUNCEMENT,
                    config_version="spy-revoke-v2",
                    effective_from=AS_OF,
                    selected_by=actor,
                    published_at=AS_OF,
                    selection_reason="transaction ownership spy",
                    expected_current_config_id=published.config_id,
                    idempotency_key=f"spy-revoke-{uuid4()}",
                ),
                transaction,
            )
            service.retire_grant_evidence_source(
                service.RetireGrantEvidenceSourceCommand(
                    source_record_id=registered.source_record_id,
                    actor_id=actor,
                    retired_at=AS_OF,
                    expected_current_source_id=registered.source_record_id,
                ),
                transaction,
            )
        assert prohibited_calls == []


def test_forced_flush_fault_and_caller_rollback_remove_complete_write(
    session_factory, monkeypatch
) -> None:
    actor_id: str
    with session_factory() as transaction:
        actor_id, _, _ = _actors(transaction)
        original_flush = transaction.flush
        flush_calls = 0

        def fail_second_flush(objects=None) -> None:
            nonlocal flush_calls
            flush_calls += 1
            if flush_calls == 2:
                raise RuntimeError("forced test-only flush fault")
            original_flush(objects)

        with monkeypatch.context() as patch:
            patch.setattr(transaction, "flush", fail_second_flush)
            with pytest.raises(RuntimeError, match="forced test-only flush fault"):
                service.register_grant_evidence_source(_register_command(actor_id), transaction)
        assert not transaction.new
        assert not transaction.dirty
        assert transaction.scalar(select(func.count()).select_from(GrantEvidenceSourceRecord)) == 0

        created = service.register_grant_evidence_source(_register_command(actor_id), transaction)
        source_id = created.source_record_id
        transaction.rollback()
    with session_factory() as transaction:
        assert transaction.get(GrantEvidenceSourceRecord, source_id) is None

    with session_factory() as transaction:
        _, _, selector, registered = _active_source_and_gate(transaction)
        transaction.commit()
        published = _publish(transaction, registered.source_record_id, selector)
        config_id = published.config_id
        transaction.rollback()
    with session_factory() as transaction:
        assert transaction.get(GrantEvidenceSourceConfig, config_id) is None
        assert transaction.scalar(select(func.count()).select_from(GrantEvidenceCandidate)) == 0
