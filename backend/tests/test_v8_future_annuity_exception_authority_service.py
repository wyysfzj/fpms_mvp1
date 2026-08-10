from __future__ import annotations

import hashlib
import json
from dataclasses import fields, is_dataclass, replace
from datetime import datetime, timedelta, timezone
from threading import Event, Thread
from time import sleep
from uuid import uuid4

import pytest
from sqlalchemy import func, select, update
from sqlalchemy.orm import Session, sessionmaker

from app.core.errors import BusinessError
from app.modules.auth.models import T_Role, T_RolePerm, T_User, T_UserRole
from app.modules.cases.models import Case
from app.modules.masterdata.clients.models import Client
from app.modules.system import future_annuity_exception_authority_service as service
from app.modules.system.models import CustomerDecisionGate, FutureAnnuityDraftExceptionRecord

AS_OF = datetime(2026, 8, 10, 12, 0, 0, 123456)
DECISION_SOURCE = "docs/product/v8/customer-decisions/2026-08-10-v8-full-batch-scheme-a.txt"
DECISION_VERSION = "customer-decision:2026-08-10:v8-full-batch-scheme-a:v1"


def _seed(
    transaction: Session,
    *,
    permission: bool = True,
    active: bool = True,
    source_reference: str = DECISION_SOURCE,
) -> tuple[str, str, str]:
    actor_id = str(uuid4())
    role_id = str(uuid4())
    client_id = str(uuid4())
    case_id = str(uuid4())
    transaction.add_all(
        [
            T_User(
                id=actor_id,
                username=f"annuity-exception-{uuid4()}",
                password_hash="test-only",
                is_active=active,
            ),
            T_Role(id=role_id, code=f"exception-admin-{uuid4()}", name="测试管理员"),
            Client(id=client_id, client_code=f"EX-{uuid4()}", name_cn="测试客户"),
        ]
    )
    transaction.flush()
    transaction.add_all(
        [
            T_UserRole(user_id=actor_id, role_id=role_id),
            Case(
                id=case_id,
                case_no=f"EX-{uuid4()}",
                case_type="NORMAL",
                patent_category="INV",
                flow_dir="CN_DOMESTIC",
                client_id=client_id,
                status="NOT_FILED",
            ),
            CustomerDecisionGate(
                id=str(uuid4()),
                gate_code="DG-FEE-FUTURE-ANNUITY",
                scope_key="GLOBAL",
                decision_value="APPROVED_POLICY",
                decision_status="CONFIRMED",
                source_reference=source_reference,
                source_version=DECISION_VERSION,
                confirmed_by=actor_id,
                effective_at=AS_OF - timedelta(days=1),
                supersedes_gate_id=None,
                decision_snapshot="synthetic-test-only",
                idempotency_key=f"gate-{uuid4()}",
                current_identity_key="DG-FEE-FUTURE-ANNUITY|GLOBAL",
            ),
        ]
    )
    if permission:
        transaction.add(
            T_RolePerm(
                id=str(uuid4()), role_id=role_id, perm_code="SystemParam.Edit"
            )
        )
    transaction.commit()
    return actor_id, client_id, case_id


def _publish(
    actor_id: str,
    scope_id: str,
    **changes: object,
) -> service.PublishFutureAnnuityExceptionCommand:
    values: dict[str, object] = {
        "scope_type": service.FutureAnnuityExceptionScope.CLIENT,
        "scope_id": scope_id,
        "effective_from": AS_OF - timedelta(hours=1),
        "effective_to": AS_OF + timedelta(days=30),
        "record_version": f"exception-{uuid4()}",
        "source_reference": "客户年费例外授权单",
        "source_version": "2026-08-10-v1",
        "reason": "客户在限定期间授权生成内部草单",
        "confirmed_by": actor_id,
        "published_at": AS_OF - timedelta(minutes=30),
        "effective_at": AS_OF - timedelta(minutes=15),
        "idempotency_key": f"publish-{uuid4()}",
    }
    values.update(changes)
    return service.PublishFutureAnnuityExceptionCommand(**values)


def _assert_error(call, code: str, status: int) -> BusinessError:
    with pytest.raises(BusinessError) as caught:
        call()
    assert caught.value.code == code
    assert caught.value.status_code == status
    return caught.value


def test_public_contract_is_frozen_slotted_and_keyword_only() -> None:
    assert tuple(item.value for item in service.FutureAnnuityExceptionScope) == (
        "CLIENT",
        "CASE",
    )
    assert tuple(item.value for item in service.FutureAnnuityExceptionRecordType) == (
        "PUBLISHED",
        "REVOKED",
    )
    assert tuple(item.value for item in service.FutureAnnuityExceptionDisposition) == (
        "CREATED",
        "REUSED",
    )
    for dto in (
        service.PublishFutureAnnuityExceptionCommand,
        service.RevokeFutureAnnuityExceptionCommand,
        service.ResolveFutureAnnuityExceptionCommand,
        service.FutureAnnuityExceptionRecordResult,
        service.FutureAnnuityExceptionUseAttestation,
    ):
        assert is_dataclass(dto)
        assert dto.__dataclass_params__.frozen is True
        assert dto.__slots__ == tuple(field.name for field in fields(dto))


def test_publish_replay_resolve_and_caller_rollback(session_factory: sessionmaker) -> None:
    with session_factory() as transaction:
        actor_id, client_id, case_id = _seed(transaction)
        command = _publish(actor_id, client_id)
        created = service.publish_future_annuity_exception(command, transaction)
        replay = service.publish_future_annuity_exception(command, transaction)
        attestation = service.resolve_future_annuity_exception(
            service.ResolveFutureAnnuityExceptionCommand(
                client_id=client_id,
                case_id=case_id,
                as_of=AS_OF,
            ),
            transaction,
        )

        assert created.disposition is service.FutureAnnuityExceptionDisposition.CREATED
        assert replay == replace(
            created, disposition=service.FutureAnnuityExceptionDisposition.REUSED
        )
        assert attestation.publication_id == created.record_id
        assert attestation.scope_type is service.FutureAnnuityExceptionScope.CLIENT
        assert attestation.scope_id == client_id
        row = transaction.get(FutureAnnuityDraftExceptionRecord, created.record_id)
        assert row is not None
        payload = json.loads(row.record_snapshot)
        assert set(payload) == {
            "schema",
            "record_type",
            "scope_type",
            "scope_id",
            "effective_from",
            "effective_to",
            "effective_at",
            "record_version",
            "source_reference",
            "source_version",
            "reason",
            "confirmed_by",
            "published_at",
        }
        assert row.record_snapshot == json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        assert row.record_snapshot_hash == hashlib.sha256(
            row.record_snapshot.encode("utf-8")
        ).hexdigest()

        transaction.rollback()
        assert (
            transaction.scalar(
                select(func.count()).select_from(FutureAnnuityDraftExceptionRecord)
            )
            == 0
        )


def test_client_case_overlap_fails_but_distinct_cases_and_boundary_are_allowed(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        actor_id, client_id, case_id = _seed(transaction)
        other_case_id = str(uuid4())
        transaction.add(
            Case(
                id=other_case_id,
                case_no=f"EX-{uuid4()}",
                case_type="NORMAL",
                patent_category="INV",
                flow_dir="CN_DOMESTIC",
                client_id=client_id,
                status="NOT_FILED",
            )
        )
        transaction.commit()

        case_command = _publish(
            actor_id,
            case_id,
            scope_type=service.FutureAnnuityExceptionScope.CASE,
        )
        service.publish_future_annuity_exception(case_command, transaction)
        service.publish_future_annuity_exception(
            _publish(
                actor_id,
                other_case_id,
                scope_type=service.FutureAnnuityExceptionScope.CASE,
            ),
            transaction,
        )
        _assert_error(
            lambda: service.publish_future_annuity_exception(
                _publish(actor_id, client_id), transaction
            ),
            "FUTURE_ANNUITY_EXCEPTION_CONFLICT",
            409,
        )
        boundary = _publish(
            actor_id,
            case_id,
            scope_type=service.FutureAnnuityExceptionScope.CASE,
            effective_from=case_command.effective_to,
            effective_to=case_command.effective_to + timedelta(days=10),
            published_at=case_command.effective_to,
            effective_at=case_command.effective_to,
        )
        assert (
            service.publish_future_annuity_exception(boundary, transaction).disposition
            is service.FutureAnnuityExceptionDisposition.CREATED
        )


def test_revocation_is_append_only_and_suppresses_only_after_both_times(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        actor_id, client_id, case_id = _seed(transaction)
        publication = service.publish_future_annuity_exception(
            _publish(actor_id, client_id), transaction
        )
        revoke = service.RevokeFutureAnnuityExceptionCommand(
            target_publication_id=publication.record_id,
            record_version=f"revoke-{uuid4()}",
            reason="终止限定授权",
            confirmed_by=actor_id,
            published_at=AS_OF + timedelta(days=1),
            effective_at=AS_OF + timedelta(days=2),
            idempotency_key=f"revoke-{uuid4()}",
        )
        revoked = service.revoke_future_annuity_exception(revoke, transaction)
        replay = service.revoke_future_annuity_exception(revoke, transaction)
        assert revoked.record_type is service.FutureAnnuityExceptionRecordType.REVOKED
        assert replay.disposition is service.FutureAnnuityExceptionDisposition.REUSED
        assert service.resolve_future_annuity_exception(
            service.ResolveFutureAnnuityExceptionCommand(
                client_id=client_id,
                case_id=case_id,
                as_of=AS_OF + timedelta(days=1, hours=12),
            ),
            transaction,
        ).publication_id == publication.record_id
        _assert_error(
            lambda: service.resolve_future_annuity_exception(
                service.ResolveFutureAnnuityExceptionCommand(
                    client_id=client_id,
                    case_id=case_id,
                    as_of=AS_OF + timedelta(days=2),
                ),
                transaction,
            ),
            "FUTURE_ANNUITY_EXCEPTION_NOT_FOUND",
            404,
        )
        _assert_error(
            lambda: service.revoke_future_annuity_exception(
                replace(
                    revoke,
                    record_version=f"revoke-{uuid4()}",
                    idempotency_key=f"revoke-{uuid4()}",
                ),
                transaction,
            ),
            "FUTURE_ANNUITY_EXCEPTION_CONFLICT",
            409,
        )


@pytest.mark.parametrize("permission,active", [(False, True), (True, False)])
def test_mutation_requires_active_system_parameter_editor(
    session_factory: sessionmaker,
    permission: bool,
    active: bool,
) -> None:
    with session_factory() as transaction:
        actor_id, client_id, _ = _seed(
            transaction, permission=permission, active=active
        )
        _assert_error(
            lambda: service.publish_future_annuity_exception(
                _publish(actor_id, client_id), transaction
            ),
            "FUTURE_ANNUITY_EXCEPTION_CONFLICT",
            409,
        )
        assert (
            transaction.scalar(
                select(func.count()).select_from(FutureAnnuityDraftExceptionRecord)
            )
            == 0
        )


def test_wrong_scheme_a_source_and_changed_replay_fail_closed(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        actor_id, client_id, _ = _seed(transaction, source_reference="unreviewed-source")
        command = _publish(actor_id, client_id)
        _assert_error(
            lambda: service.publish_future_annuity_exception(command, transaction),
            "FUTURE_ANNUITY_EXCEPTION_CONFLICT",
            409,
        )
        transaction.execute(
            update(CustomerDecisionGate)
            .where(CustomerDecisionGate.gate_code == "DG-FEE-FUTURE-ANNUITY")
            .values(source_reference=DECISION_SOURCE)
        )
        transaction.commit()
        command = _publish(actor_id, client_id)
        service.publish_future_annuity_exception(command, transaction)
        _assert_error(
            lambda: service.publish_future_annuity_exception(
                replace(command, reason="changed"), transaction
            ),
            "FUTURE_ANNUITY_EXCEPTION_CONFLICT",
            409,
        )


def test_corrupt_snapshot_and_client_case_mismatch_fail_closed(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        actor_id, client_id, case_id = _seed(transaction)
        publication = service.publish_future_annuity_exception(
            _publish(actor_id, client_id), transaction
        )
        other_client_id = str(uuid4())
        transaction.add(
            Client(id=other_client_id, client_code=f"EX-{uuid4()}", name_cn="其他客户")
        )
        transaction.flush()
        _assert_error(
            lambda: service.resolve_future_annuity_exception(
                service.ResolveFutureAnnuityExceptionCommand(
                    client_id=other_client_id,
                    case_id=case_id,
                    as_of=AS_OF,
                ),
                transaction,
            ),
            "FUTURE_ANNUITY_EXCEPTION_CONFLICT",
            409,
        )
        transaction.execute(
            update(FutureAnnuityDraftExceptionRecord)
            .where(FutureAnnuityDraftExceptionRecord.id == publication.record_id)
            .values(record_snapshot="{}")
        )
        transaction.commit()
        _assert_error(
            lambda: service.resolve_future_annuity_exception(
                service.ResolveFutureAnnuityExceptionCommand(
                    client_id=client_id,
                    case_id=case_id,
                    as_of=AS_OF,
                ),
                transaction,
            ),
            "FUTURE_ANNUITY_EXCEPTION_CONFLICT",
            409,
        )


def test_input_and_dirty_transaction_are_rejected_without_write(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        actor_id, client_id, _ = _seed(transaction)
        _assert_error(
            lambda: service.publish_future_annuity_exception(
                _publish(
                    actor_id,
                    client_id,
                    effective_from=AS_OF.replace(tzinfo=timezone.utc),
                ),
                transaction,
            ),
            "FUTURE_ANNUITY_EXCEPTION_INPUT_INVALID",
            400,
        )
        transaction.add(
            Client(id=str(uuid4()), client_code=f"DIRTY-{uuid4()}", name_cn="未提交")
        )
        _assert_error(
            lambda: service.publish_future_annuity_exception(
                _publish(actor_id, client_id), transaction
            ),
            "FUTURE_ANNUITY_EXCEPTION_TRANSACTION_DIRTY",
            409,
        )


def test_concurrent_overlapping_publications_serialize_and_fail_closed(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as first:
        actor_id, client_id, _ = _seed(first)
        service.publish_future_annuity_exception(
            _publish(actor_id, client_id), first
        )
        started = Event()
        outcome: list[object] = []

        def publish_overlap() -> None:
            with session_factory() as second:
                started.set()
                try:
                    outcome.append(
                        service.publish_future_annuity_exception(
                            _publish(actor_id, client_id), second
                        )
                    )
                except Exception as error:  # captured for exact cross-thread assertion
                    outcome.append(error)

        contender = Thread(target=publish_overlap)
        contender.start()
        assert started.wait(timeout=2)
        sleep(0.1)
        assert contender.is_alive()
        first.commit()
        contender.join(timeout=5)
        assert not contender.is_alive()

    assert len(outcome) == 1
    assert isinstance(outcome[0], BusinessError)
    assert outcome[0].code == "FUTURE_ANNUITY_EXCEPTION_CONFLICT"
    assert outcome[0].status_code == 409
    with session_factory() as transaction:
        assert (
            transaction.scalar(
                select(func.count()).select_from(FutureAnnuityDraftExceptionRecord)
            )
            == 1
        )
