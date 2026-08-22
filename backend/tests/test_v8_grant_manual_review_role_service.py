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
from app.modules.system import grant_manual_review_role_service as service
from app.modules.system.models import CustomerDecisionGate, GrantManualReviewRoleConfig

AS_OF = datetime(2026, 8, 10, 12, 0, 0, 123456)
DECISION_SOURCE = "docs/product/v8/customer-decisions/2026-08-10-v8-full-batch-scheme-a.txt"
DECISION_VERSION = "customer-decision:2026-08-10:v8-full-batch-scheme-a:v1"


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


def _install_gate(
    transaction: Session,
    confirmer_id: str,
    *,
    effective_at: datetime = AS_OF - timedelta(days=1),
    decision_value: str = "APPROVED_POLICY",
    source_reference: str = DECISION_SOURCE,
    source_version: str = DECISION_VERSION,
) -> str:
    gate_id = str(uuid4())
    transaction.add(
        CustomerDecisionGate(
            id=gate_id,
            gate_code="DG-GRANT-MANUAL-REVIEW",
            scope_key="GLOBAL",
            decision_value=decision_value,
            decision_status="CONFIRMED",
            source_reference=source_reference,
            source_version=source_version,
            confirmed_by=confirmer_id,
            effective_at=effective_at,
            supersedes_gate_id=None,
            decision_snapshot="synthetic-test-only",
            idempotency_key=f"gate-{uuid4()}",
            current_identity_key="DG-GRANT-MANUAL-REVIEW|GLOBAL",
        )
    )
    return gate_id


def _ready_fixture(
    transaction: Session,
    *,
    same_verifier_role: bool = False,
    second_verifier_active: bool = True,
) -> tuple[str, tuple[str, str, str, str, str]]:
    confirmer_id = _user(transaction, "confirmer")
    first_role = _role(transaction, "first-verifier")
    second_role = first_role if same_verifier_role else _role(transaction, "second-verifier")
    role_ids = (
        _role(transaction, "official-copy-acquirer"),
        first_role,
        second_role,
        _role(transaction, "manual-review-proposer"),
        _role(transaction, "manual-review-second-reviewer"),
    )
    for index, role_id in enumerate(dict.fromkeys(role_ids)):
        member_id = _user(
            transaction,
            f"member-{index}",
            active=second_verifier_active or role_id != second_role,
        )
        _bind(transaction, member_id, role_id)
    if same_verifier_role:
        extra_id = _user(transaction, "second-distinct-verifier")
        _bind(transaction, extra_id, first_role)
    _install_gate(transaction, confirmer_id)
    transaction.commit()
    return confirmer_id, role_ids


def _publish_command(
    confirmer_id: str,
    role_ids: tuple[str, str, str, str, str],
    **changes: object,
) -> service.PublishGrantManualReviewRoleConfigCommand:
    values: dict[str, object] = {
        "official_copy_acquirer_role_id": role_ids[0],
        "first_verifier_role_id": role_ids[1],
        "second_verifier_role_id": role_ids[2],
        "manual_review_proposer_role_id": role_ids[3],
        "manual_review_second_reviewer_role_id": role_ids[4],
        "config_version": f"config-{uuid4()}",
        "effective_from": AS_OF - timedelta(hours=1),
        "effective_to": None,
        "confirmed_by": confirmer_id,
        "published_at": AS_OF - timedelta(hours=2),
        "expected_current_config_id": None,
        "idempotency_key": f"publish-{uuid4()}",
    }
    values.update(changes)
    return service.PublishGrantManualReviewRoleConfigCommand(**values)


def _assert_error(call, *, code: str = "GRANT_MANUAL_REVIEW_ROLE_CONFLICT", status: int = 409):
    with pytest.raises(BusinessError) as caught:
        call()
    assert caught.value.code == code
    assert caught.value.status_code == status
    return caught.value


def _snapshot(
    command: service.PublishGrantManualReviewRoleConfigCommand,
    *,
    status: str = "ACTIVE",
) -> str:
    return json.dumps(
        {
            "config_status": status,
            "config_version": command.config_version,
            "confirmed_by": command.confirmed_by,
            "effective_from": command.effective_from.isoformat(timespec="microseconds"),
            "effective_to": (
                command.effective_to.isoformat(timespec="microseconds")
                if command.effective_to is not None
                else None
            ),
            "expected_current_config_id": command.expected_current_config_id,
            "first_verifier_role_id": command.first_verifier_role_id,
            "gate_code": "DG-GRANT-MANUAL-REVIEW",
            "manual_review_proposer_role_id": command.manual_review_proposer_role_id,
            "manual_review_second_reviewer_role_id": (
                command.manual_review_second_reviewer_role_id
            ),
            "official_copy_acquirer_role_id": command.official_copy_acquirer_role_id,
            "published_at": command.published_at.isoformat(timespec="microseconds"),
            "schema": "FPMS_GRANT_MANUAL_REVIEW_ROLE_CONFIG_V1",
            "scope_key": "GLOBAL",
            "second_verifier_role_id": command.second_verifier_role_id,
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def test_public_contract_is_exact_frozen_keyword_only_and_synchronous() -> None:
    assert tuple(item.value for item in service.GrantManualReviewRoleDisposition) == (
        "CREATED",
        "REUSED",
    )
    dto_fields = {
        service.PublishGrantManualReviewRoleConfigCommand: (
            "official_copy_acquirer_role_id",
            "first_verifier_role_id",
            "second_verifier_role_id",
            "manual_review_proposer_role_id",
            "manual_review_second_reviewer_role_id",
            "config_version",
            "effective_from",
            "effective_to",
            "confirmed_by",
            "published_at",
            "expected_current_config_id",
            "idempotency_key",
        ),
        service.RevokeGrantManualReviewRoleConfigCommand: (
            "config_version",
            "effective_from",
            "confirmed_by",
            "published_at",
            "expected_current_config_id",
            "idempotency_key",
        ),
        service.ResolveGrantManualReviewRoleConfigCommand: ("as_of",),
        service.GrantManualReviewRoleConfigResult: (
            "config_id",
            "config_status",
            "config_snapshot_hash",
            "current_identity_key",
            "disposition",
        ),
        service.GrantManualReviewRoleResolution: (
            "gate_id",
            "config_id",
            "config_snapshot_hash",
            "official_copy_acquirer_role_id",
            "first_verifier_role_id",
            "second_verifier_role_id",
            "manual_review_proposer_role_id",
            "manual_review_second_reviewer_role_id",
            "effective_from",
            "effective_to",
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
    for function in (
        service.publish_grant_manual_review_role_config,
        service.revoke_grant_manual_review_role_config,
        service.resolve_grant_manual_review_role_config,
    ):
        assert tuple(inspect.signature(function).parameters) == ("command", "transaction")
        assert get_type_hints(function)["transaction"] is Session
        assert inspect.iscoroutinefunction(function) is False
    command = service.ResolveGrantManualReviewRoleConfigCommand(as_of=AS_OF)
    with pytest.raises(FrozenInstanceError):
        command.as_of = AS_OF + timedelta(days=1)


def test_publish_replay_resolve_revoke_and_shadow_are_canonical(session_factory) -> None:
    with session_factory() as transaction:
        confirmer_id, role_ids = _ready_fixture(transaction)
        command = _publish_command(confirmer_id, role_ids)
        created = service.publish_grant_manual_review_role_config(command, transaction)
        assert created.disposition is service.GrantManualReviewRoleDisposition.CREATED
        assert created.config_status == "ACTIVE"
        assert created.current_identity_key == "DG-GRANT-MANUAL-REVIEW|GLOBAL"
        row = transaction.get(GrantManualReviewRoleConfig, created.config_id)
        expected = _snapshot(command)
        assert row.config_snapshot == expected
        assert row.config_snapshot_hash == hashlib.sha256(expected.encode()).hexdigest()
        assert service.publish_grant_manual_review_role_config(command, transaction) == replace(
            created, disposition=service.GrantManualReviewRoleDisposition.REUSED
        )

        resolved = service.resolve_grant_manual_review_role_config(
            service.ResolveGrantManualReviewRoleConfigCommand(as_of=AS_OF), transaction
        )
        assert resolved.gate_id
        assert resolved.config_id == created.config_id
        assert (
            resolved.official_copy_acquirer_role_id,
            resolved.first_verifier_role_id,
            resolved.second_verifier_role_id,
            resolved.manual_review_proposer_role_id,
            resolved.manual_review_second_reviewer_role_id,
        ) == role_ids

        revoke = service.RevokeGrantManualReviewRoleConfigCommand(
            config_version=f"revoke-{uuid4()}",
            effective_from=AS_OF,
            confirmed_by=confirmer_id,
            published_at=AS_OF,
            expected_current_config_id=created.config_id,
            idempotency_key=f"revoke-{uuid4()}",
        )
        revoked = service.revoke_grant_manual_review_role_config(revoke, transaction)
        assert revoked.config_status == "REVOKED"
        assert service.revoke_grant_manual_review_role_config(revoke, transaction) == replace(
            revoked, disposition=service.GrantManualReviewRoleDisposition.REUSED
        )
        revoked_row = transaction.get(GrantManualReviewRoleConfig, revoked.config_id)
        active_row = transaction.get(GrantManualReviewRoleConfig, created.config_id)
        assert revoked_row.supersedes_config_id == created.config_id
        assert active_row.current_identity_key is None
        assert tuple(
            getattr(revoked_row, field)
            for field in (
                "official_copy_acquirer_role_id",
                "first_verifier_role_id",
                "second_verifier_role_id",
                "manual_review_proposer_role_id",
                "manual_review_second_reviewer_role_id",
            )
        ) == role_ids
        _assert_error(
            lambda: service.resolve_grant_manual_review_role_config(
                service.ResolveGrantManualReviewRoleConfigCommand(as_of=AS_OF), transaction
            )
        )


def test_same_role_is_ready_when_it_has_two_active_actual_users(session_factory) -> None:
    with session_factory() as transaction:
        confirmer_id, role_ids = _ready_fixture(transaction, same_verifier_role=True)
        assert service.publish_grant_manual_review_role_config(
            _publish_command(confirmer_id, role_ids), transaction
        ).config_status == "ACTIVE"


def test_every_configured_role_needs_an_active_member(session_factory) -> None:
    with session_factory() as transaction:
        confirmer_id, role_ids = _ready_fixture(transaction)
        second_user_id = transaction.scalar(
            select(T_UserRole.user_id).where(T_UserRole.role_id == role_ids[2])
        )
        transaction.get(T_User, second_user_id).is_active = False
        transaction.commit()
        before = transaction.scalar(select(func.count()).select_from(GrantManualReviewRoleConfig))
        _assert_error(
            lambda: service.publish_grant_manual_review_role_config(
                _publish_command(confirmer_id, role_ids), transaction
            )
        )
        assert transaction.scalar(
            select(func.count()).select_from(GrantManualReviewRoleConfig)
        ) == before


def test_same_paired_role_with_one_active_user_fails_separation(session_factory) -> None:
    with session_factory() as transaction:
        confirmer_id, role_ids = _ready_fixture(transaction, same_verifier_role=True)
        members = list(
            transaction.scalars(
                select(T_User).join(T_UserRole).where(T_UserRole.role_id == role_ids[1])
            )
        )
        members[1].is_active = False
        transaction.commit()
        _assert_error(
            lambda: service.publish_grant_manual_review_role_config(
                _publish_command(confirmer_id, role_ids), transaction
            )
        )


def test_gate_uses_published_at_for_write_and_as_of_for_resolution(session_factory) -> None:
    with session_factory() as transaction:
        confirmer_id = _user(transaction, "confirmer")
        role_ids = tuple(_role(transaction, f"role-{index}") for index in range(5))
        for index, role_id in enumerate(role_ids):
            member_id = _user(transaction, f"member-{index}")
            _bind(transaction, member_id, role_id)
        _install_gate(transaction, confirmer_id, effective_at=AS_OF)
        transaction.commit()
        command = _publish_command(
            confirmer_id,
            role_ids,
            published_at=AS_OF - timedelta(hours=1),
            effective_from=AS_OF + timedelta(hours=1),
        )
        _assert_error(
            lambda: service.publish_grant_manual_review_role_config(command, transaction)
        )
        assert transaction.scalar(
            select(func.count()).select_from(GrantManualReviewRoleConfig)
        ) == 0
        created = service.publish_grant_manual_review_role_config(
            replace(command, published_at=AS_OF), transaction
        )
        _assert_error(
            lambda: service.resolve_grant_manual_review_role_config(
                service.ResolveGrantManualReviewRoleConfigCommand(as_of=AS_OF), transaction
            )
        )
        assert service.resolve_grant_manual_review_role_config(
            service.ResolveGrantManualReviewRoleConfigCommand(
                as_of=AS_OF + timedelta(hours=1)
            ),
            transaction,
        ).config_id == created.config_id


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("decision_status", "REVOKED"),
        ("decision_value", "WRONG"),
        ("source_reference", "wrong-source"),
        ("source_version", "wrong-version"),
        ("scope_key", "case:wrong"),
    ],
)
def test_wrong_or_revoked_gate_authority_fails_closed(
    session_factory, field: str, value: str
) -> None:
    with session_factory() as transaction:
        confirmer_id, role_ids = _ready_fixture(transaction)
        gate = transaction.scalar(
            select(CustomerDecisionGate).where(
                CustomerDecisionGate.current_identity_key
                == "DG-GRANT-MANUAL-REVIEW|GLOBAL"
            )
        )
        setattr(gate, field, value)
        if field == "scope_key":
            gate.current_identity_key = "DG-GRANT-MANUAL-REVIEW|case:wrong"
        transaction.commit()
        _assert_error(
            lambda: service.publish_grant_manual_review_role_config(
                _publish_command(confirmer_id, role_ids), transaction
            )
        )
        assert transaction.scalar(
            select(func.count()).select_from(GrantManualReviewRoleConfig)
        ) == 0


@pytest.mark.parametrize(
    ("change", "field"),
    [
        ({"config_version": " bad"}, "config_version"),
        ({"official_copy_acquirer_role_id": "not-a-uuid"}, "official_copy_acquirer_role_id"),
        ({"effective_to": AS_OF - timedelta(days=2)}, "effective_to"),
        ({"published_at": datetime.now(timezone.utc)}, "published_at"),
        ({"idempotency_key": "bad\x00key"}, "idempotency_key"),
    ],
)
def test_invalid_input_fails_400_without_write(session_factory, change, field: str) -> None:
    with session_factory() as transaction:
        confirmer_id, role_ids = _ready_fixture(transaction)
        command = _publish_command(confirmer_id, role_ids, **change)
        error = _assert_error(
            lambda: service.publish_grant_manual_review_role_config(command, transaction),
            code="GRANT_MANUAL_REVIEW_ROLE_INPUT_INVALID",
            status=400,
        )
        assert error.details == {"field": field}
        assert transaction.scalar(
            select(func.count()).select_from(GrantManualReviewRoleConfig)
        ) == 0


def test_changed_replay_cas_and_corruption_fail_closed(session_factory) -> None:
    with session_factory() as transaction:
        confirmer_id, role_ids = _ready_fixture(transaction)
        command = _publish_command(confirmer_id, role_ids)
        created = service.publish_grant_manual_review_role_config(command, transaction)
        _assert_error(
            lambda: service.publish_grant_manual_review_role_config(
                replace(command, config_version=f"changed-{uuid4()}"), transaction
            )
        )
        _assert_error(
            lambda: service.publish_grant_manual_review_role_config(
                _publish_command(
                    confirmer_id,
                    role_ids,
                    expected_current_config_id=str(uuid4()),
                ),
                transaction,
            )
        )
        row = transaction.get(GrantManualReviewRoleConfig, created.config_id)
        row.config_snapshot_hash = "0" * 64
        transaction.commit()
        _assert_error(
            lambda: service.resolve_grant_manual_review_role_config(
                service.ResolveGrantManualReviewRoleConfigCommand(as_of=AS_OF), transaction
            )
        )


def test_membership_drift_disables_resolution(session_factory) -> None:
    with session_factory() as transaction:
        confirmer_id, role_ids = _ready_fixture(transaction)
        command = _publish_command(confirmer_id, role_ids)
        service.publish_grant_manual_review_role_config(command, transaction)
        member_id = transaction.scalar(
            select(T_UserRole.user_id).where(T_UserRole.role_id == role_ids[4])
        )
        transaction.get(T_User, member_id).is_active = False
        transaction.commit()
        _assert_error(
            lambda: service.resolve_grant_manual_review_role_config(
                service.ResolveGrantManualReviewRoleConfigCommand(as_of=AS_OF), transaction
            )
        )
        _assert_error(
            lambda: service.publish_grant_manual_review_role_config(command, transaction)
        )


def test_publish_replay_revalidates_its_predecessor_chain(session_factory) -> None:
    with session_factory() as transaction:
        confirmer_id, role_ids = _ready_fixture(transaction)
        first = service.publish_grant_manual_review_role_config(
            _publish_command(confirmer_id, role_ids), transaction
        )
        successor_command = _publish_command(
            confirmer_id,
            role_ids,
            expected_current_config_id=first.config_id,
        )
        successor = service.publish_grant_manual_review_role_config(
            successor_command, transaction
        )
        transaction.commit()
        predecessor = transaction.get(GrantManualReviewRoleConfig, first.config_id)
        predecessor.config_snapshot_hash = "0" * 64
        transaction.commit()
        _assert_error(
            lambda: service.publish_grant_manual_review_role_config(
                successor_command, transaction
            )
        )
        transaction.delete(
            transaction.get(GrantManualReviewRoleConfig, successor.config_id)
        )
        transaction.flush()
        transaction.delete(predecessor)
        transaction.commit()


def test_revocation_remains_available_after_memberships_become_unusable(session_factory) -> None:
    with session_factory() as transaction:
        confirmer_id, role_ids = _ready_fixture(transaction)
        created = service.publish_grant_manual_review_role_config(
            _publish_command(confirmer_id, role_ids), transaction
        )
        transaction.commit()
        members = list(
            transaction.scalars(
                select(T_User).join(T_UserRole).where(T_UserRole.role_id.in_(role_ids))
            )
        )
        for member in members:
            member.is_active = False
        transaction.commit()
        revoked = service.revoke_grant_manual_review_role_config(
            service.RevokeGrantManualReviewRoleConfigCommand(
                config_version=f"revoke-{uuid4()}",
                effective_from=AS_OF,
                confirmed_by=confirmer_id,
                published_at=AS_OF,
                expected_current_config_id=created.config_id,
                idempotency_key=f"revoke-{uuid4()}",
            ),
            transaction,
        )
        assert revoked.config_status == "REVOKED"


def test_revoked_replay_rejects_a_canonically_rehashed_role_copy_mismatch(
    session_factory,
) -> None:
    with session_factory() as transaction:
        confirmer_id, role_ids = _ready_fixture(transaction)
        created = service.publish_grant_manual_review_role_config(
            _publish_command(confirmer_id, role_ids), transaction
        )
        revoke = service.RevokeGrantManualReviewRoleConfigCommand(
            config_version=f"revoke-{uuid4()}",
            effective_from=AS_OF,
            confirmed_by=confirmer_id,
            published_at=AS_OF,
            expected_current_config_id=created.config_id,
            idempotency_key=f"revoke-{uuid4()}",
        )
        revoked = service.revoke_grant_manual_review_role_config(revoke, transaction)
        row = transaction.get(GrantManualReviewRoleConfig, revoked.config_id)
        row.official_copy_acquirer_role_id = role_ids[1]
        snapshot = json.loads(row.config_snapshot)
        snapshot["official_copy_acquirer_role_id"] = role_ids[1]
        row.config_snapshot = json.dumps(
            snapshot,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        row.config_snapshot_hash = hashlib.sha256(row.config_snapshot.encode()).hexdigest()
        transaction.commit()
        _assert_error(
            lambda: service.revoke_grant_manual_review_role_config(revoke, transaction)
        )
        transaction.delete(row)
        transaction.flush()
        transaction.delete(
            transaction.get(GrantManualReviewRoleConfig, created.config_id)
        )
        transaction.commit()


def test_dirty_session_and_raw_lookalikes_fail_before_write(session_factory) -> None:
    _assert_error(
        lambda: service.publish_grant_manual_review_role_config(object(), object()),
        code="GRANT_MANUAL_REVIEW_ROLE_INPUT_INVALID",
        status=400,
    )
    with session_factory() as transaction:
        confirmer_id, role_ids = _ready_fixture(transaction)
        transaction.add(
            T_User(
                id=str(uuid4()),
                username=f"dirty-{uuid4()}",
                password_hash="test-only",
                is_active=True,
            )
        )
        _assert_error(
            lambda: service.publish_grant_manual_review_role_config(
                _publish_command(confirmer_id, role_ids), transaction
            )
        )
        assert transaction.scalar(
            select(func.count()).select_from(GrantManualReviewRoleConfig)
        ) == 0


def test_service_never_owns_caller_transaction_and_caller_rollback_removes_write(
    session_factory, monkeypatch
) -> None:
    with session_factory() as transaction:
        confirmer_id, role_ids = _ready_fixture(transaction)
        command = _publish_command(confirmer_id, role_ids)
        prohibited: list[str] = []

        def reject(name: str):
            def call(*_args, **_kwargs):
                prohibited.append(name)
                raise AssertionError(name)

            return call

        with monkeypatch.context() as patch:
            patch.setattr(transaction, "commit", reject("commit"))
            patch.setattr(transaction, "rollback", reject("rollback"))
            patch.setattr(transaction, "close", reject("close"))
            service.publish_grant_manual_review_role_config(command, transaction)
        assert prohibited == []
        assert transaction.scalar(
            select(func.count()).select_from(GrantManualReviewRoleConfig)
        ) == 1
        transaction.rollback()

    with session_factory() as transaction:
        assert transaction.scalar(
            select(func.count()).select_from(GrantManualReviewRoleConfig)
        ) == 0


def test_forced_successor_flush_fault_restores_predecessor_current_pointer(
    session_factory, monkeypatch
) -> None:
    with session_factory() as transaction:
        confirmer_id, role_ids = _ready_fixture(transaction)
        created = service.publish_grant_manual_review_role_config(
            _publish_command(confirmer_id, role_ids), transaction
        )
        transaction.commit()
        successor = _publish_command(
            confirmer_id,
            role_ids,
            expected_current_config_id=created.config_id,
        )
        original_flush = transaction.flush

        def forced_flush(objects=None, *args, **kwargs):
            if objects and any(
                isinstance(item, GrantManualReviewRoleConfig)
                and item.config_version == successor.config_version
                for item in objects
            ):
                raise RuntimeError("forced successor flush fault")
            return original_flush(objects, *args, **kwargs)

        with monkeypatch.context() as patch:
            patch.setattr(transaction, "flush", forced_flush)
            with pytest.raises(RuntimeError, match="forced successor flush fault"):
                service.publish_grant_manual_review_role_config(successor, transaction)
        transaction.expire_all()
        rows = list(transaction.scalars(select(GrantManualReviewRoleConfig)))
        assert len(rows) == 1
        assert rows[0].id == created.config_id
        assert rows[0].current_identity_key == "DG-GRANT-MANUAL-REVIEW|GLOBAL"
