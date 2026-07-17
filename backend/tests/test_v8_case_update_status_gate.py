from __future__ import annotations

from datetime import date
from typing import Any
from uuid import uuid4

import pytest
from sqlalchemy import event, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.errors import BusinessError
from app.modules.cases.enums import CaseStatus
from app.modules.cases.models import Case, T_CaseApplicant
from app.modules.cases.schemas import CaseApplicantIn, CaseUpdateFull
from app.modules.cases.service import update_case_full

CASE_ID = "case-update-status-gate"
ACTOR_ID = "actor-update-status-gate"


def _seed_case(
    transaction: Session,
    *,
    status: str = CaseStatus.NOT_FILED.value,
    carrier: tuple[str, object] | None = None,
    with_applicant: bool = False,
) -> None:
    values: dict[str, Any] = {
        "id": CASE_ID,
        "case_no": f"STATUS-GATE-{uuid4().hex[:8]}",
        "case_type": "NORMAL",
        "patent_category": "INV",
        "flow_dir": "CN_DOMESTIC",
        "status": status,
        "title_cn": "更新前标题",
        "created_by": ACTOR_ID,
        "updated_by": ACTOR_ID,
    }
    if carrier is not None:
        values[carrier[0]] = carrier[1]
    transaction.add(Case(**values))
    if with_applicant:
        transaction.add(
            T_CaseApplicant(
                id=str(uuid4()),
                case_id=CASE_ID,
                seq=1,
                is_first=True,
                name_cn="更新前申请人",
            )
        )
    transaction.commit()


def _expect_error(action) -> BusinessError:
    with pytest.raises(BusinessError) as captured:
        action()
    return captured.value


def _assert_lifecycle_conflict(
    error: BusinessError,
    *,
    current_status: str,
    lifecycle_revision: int | None,
) -> None:
    assert error.status_code == 409
    assert error.code == "CASE_STATUS_MANAGED_BY_LIFECYCLE"
    assert error.message == "案件状态已由生命周期管理，不能直接修改"
    assert error.details == {
        "case_id": CASE_ID,
        "current_status": current_status,
        "requested_status": CaseStatus.PENDING.value,
        "lifecycle_revision": lifecycle_revision,
    }


@pytest.mark.parametrize(
    "payload",
    (
        {"title_cn": "省略状态后更新"},
        {"status": None, "title_cn": "空状态后更新"},
        {"status": CaseStatus.NOT_FILED.value, "title_cn": "同状态后更新"},
    ),
)
def test_protected_case_status_noops_allow_other_full_update_fields(
    session_factory: sessionmaker,
    payload: dict[str, object],
) -> None:
    with session_factory() as transaction:
        _seed_case(transaction, carrier=("business_stage", "CORRUPT_STAGE"))

        result = update_case_full(
            transaction,
            CASE_ID,
            CaseUpdateFull.model_validate(payload),
            ACTOR_ID,
        )

        assert result.status == CaseStatus.NOT_FILED.value
        assert result.title_cn == payload["title_cn"]


@pytest.mark.parametrize(
    ("carrier", "value"),
    (
        ("business_stage", ""),
        ("official_procedure_stage", "CORRUPT_OFFICIAL_STAGE"),
        ("legal_status", ""),
        ("lifecycle_verification_status", "CORRUPT_VERIFICATION"),
        ("lifecycle_revision", 0),
        ("lifecycle_revision", -1),
    ),
)
def test_each_nonnull_lifecycle_carrier_blocks_direct_status_change(
    session_factory: sessionmaker,
    carrier: str,
    value: object,
) -> None:
    with session_factory() as transaction:
        _seed_case(transaction, carrier=(carrier, value))

        error = _expect_error(
            lambda: update_case_full(
                transaction,
                CASE_ID,
                CaseUpdateFull(
                    status=CaseStatus.PENDING,
                    app_no="202610000001.0",
                    filing_date=date(2026, 7, 14),
                ),
                ACTOR_ID,
            )
        )

    _assert_lifecycle_conflict(
        error,
        current_status=CaseStatus.NOT_FILED.value,
        lifecycle_revision=value if carrier == "lifecycle_revision" else None,
    )


def test_lifecycle_gate_precedes_later_validation_and_leaves_no_partial_update(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        _seed_case(
            transaction,
            carrier=("legal_status", "PARTIAL_LEGACY_VALUE"),
            with_applicant=True,
        )

        error = _expect_error(
            lambda: update_case_full(
                transaction,
                CASE_ID,
                CaseUpdateFull(
                    status=CaseStatus.PENDING,
                    title_cn="不应保存的标题",
                    applicants=[CaseApplicantIn(seq=1, is_first=True, name_cn="不应保存的申请人")],
                ),
                ACTOR_ID,
            )
        )
        transaction.rollback()

    _assert_lifecycle_conflict(
        error,
        current_status=CaseStatus.NOT_FILED.value,
        lifecycle_revision=None,
    )
    with session_factory() as fresh:
        persisted = fresh.get(Case, CASE_ID)
        assert persisted is not None
        assert persisted.status == CaseStatus.NOT_FILED.value
        assert persisted.title_cn == "更新前标题"
        applicants = (
            fresh.query(T_CaseApplicant)
            .filter(T_CaseApplicant.case_id == CASE_ID)
            .order_by(T_CaseApplicant.seq)
            .all()
        )
        assert [(item.seq, item.name_cn) for item in applicants] == [(1, "更新前申请人")]


def test_all_null_legacy_case_preserves_valid_status_transition(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        _seed_case(transaction)

        result = update_case_full(
            transaction,
            CASE_ID,
            CaseUpdateFull(
                status=CaseStatus.PENDING,
                app_no="202610000002.5",
                filing_date=date(2026, 7, 14),
                title_cn="旧案件有效流转",
            ),
            ACTOR_ID,
        )

        assert result.status == CaseStatus.PENDING.value
        assert result.app_no == "202610000002.5"
        assert result.filing_date == date(2026, 7, 14)
        assert result.title_cn == "旧案件有效流转"


def test_all_null_legacy_case_preserves_forbidden_transition_error(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        _seed_case(transaction, status=CaseStatus.GRANTED.value)

        error = _expect_error(
            lambda: update_case_full(
                transaction,
                CASE_ID,
                CaseUpdateFull(
                    status=CaseStatus.PENDING,
                    app_no="202610000003.X",
                    filing_date=date(2026, 7, 14),
                ),
                ACTOR_ID,
            )
        )

    assert error.status_code == 409
    assert error.code == "CASE_STATUS_TRANSITION_INVALID"


def test_all_null_legacy_case_preserves_required_field_error(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        _seed_case(transaction)

        error = _expect_error(
            lambda: update_case_full(
                transaction,
                CASE_ID,
                CaseUpdateFull(status=CaseStatus.PENDING),
                ACTOR_ID,
            )
        )

    assert error.status_code == 400
    assert error.code == "CASE_STATUS_REQUIRES_APPLICATION_FIELDS"


def test_legacy_status_cas_runs_only_after_all_existing_validations(
    session_factory: sessionmaker,
    engine: Engine,
) -> None:
    with session_factory() as transaction:
        _seed_case(transaction, with_applicant=True)
        cas_statements = 0

        def count_status_cas(
            _connection,
            _cursor,
            statement: str,
            _parameters,
            _context,
            _executemany,
        ) -> None:
            nonlocal cas_statements
            normalized = " ".join(statement.upper().split())
            if (
                normalized.startswith("UPDATE T_CASE SET STATUS=")
                and "LIFECYCLE_REVISION IS NULL" in normalized
            ):
                cas_statements += 1

        event.listen(engine, "before_cursor_execute", count_status_cas)
        try:
            error = _expect_error(
                lambda: update_case_full(
                    transaction,
                    CASE_ID,
                    CaseUpdateFull(
                        status=CaseStatus.PENDING,
                        app_no="202610000005.9",
                        filing_date=date(2026, 7, 14),
                        title_cn="不应暂存的标题",
                        applicants=[
                            CaseApplicantIn(seq=1, is_first=True, name_cn="第一申请人"),
                            CaseApplicantIn(seq=2, is_first=True, name_cn="第二申请人"),
                        ],
                    ),
                    ACTOR_ID,
                )
            )
        finally:
            event.remove(engine, "before_cursor_execute", count_status_cas)
        transaction.rollback()

    assert error.status_code == 400
    assert error.code == "CASE_DUPLICATE_FIRST_APPLICANT"
    assert cas_statements == 0
    with session_factory() as fresh:
        persisted = fresh.get(Case, CASE_ID)
        assert persisted is not None
        assert persisted.status == CaseStatus.NOT_FILED.value
        assert persisted.title_cn == "更新前标题"


@pytest.mark.parametrize(
    ("raced_column", "raced_value"),
    (
        ("business_stage", "RACED_BUSINESS_STAGE"),
        ("official_procedure_stage", "RACED_OFFICIAL_STAGE"),
        ("legal_status", "RACED_LEGAL_STATUS"),
        ("lifecycle_verification_status", "RACED_VERIFICATION"),
        ("lifecycle_revision", 0),
        ("status", CaseStatus.WAITING_RECEIPT.value),
    ),
)
def test_legacy_status_cas_rejects_each_lifecycle_or_status_race_without_partial_update(
    session_factory: sessionmaker,
    engine: Engine,
    raced_column: str,
    raced_value: object,
) -> None:
    with session_factory() as transaction:
        _seed_case(transaction, with_applicant=True)
        race_injected = False

        def inject_race(
            _connection,
            _cursor,
            statement: str,
            _parameters,
            _context,
            _executemany,
        ) -> None:
            nonlocal race_injected
            normalized = " ".join(statement.upper().split())
            if (
                race_injected
                or not normalized.startswith("UPDATE T_CASE SET STATUS=")
                or "LIFECYCLE_REVISION IS NULL" not in normalized
            ):
                return
            race_injected = True
            with engine.begin() as concurrent:
                concurrent.execute(
                    text(f"UPDATE t_case SET {raced_column} = :value WHERE id = :case_id"),
                    {"value": raced_value, "case_id": CASE_ID},
                )

        event.listen(engine, "before_cursor_execute", inject_race)
        try:
            error = _expect_error(
                lambda: update_case_full(
                    transaction,
                    CASE_ID,
                    CaseUpdateFull(
                        status=CaseStatus.PENDING,
                        app_no="202610000004.4",
                        filing_date=date(2026, 7, 14),
                        title_cn="不应保存的竞态标题",
                        applicants=[
                            CaseApplicantIn(
                                seq=1,
                                is_first=True,
                                name_cn="不应保存的竞态申请人",
                            )
                        ],
                    ),
                    ACTOR_ID,
                )
            )
        finally:
            event.remove(engine, "before_cursor_execute", inject_race)
        assert race_injected is True
        transaction.rollback()

    _assert_lifecycle_conflict(
        error,
        current_status=(
            CaseStatus.WAITING_RECEIPT.value
            if raced_column == "status"
            else CaseStatus.NOT_FILED.value
        ),
        lifecycle_revision=0 if raced_column == "lifecycle_revision" else None,
    )
    with session_factory() as fresh:
        persisted = fresh.get(Case, CASE_ID)
        assert persisted is not None
        assert persisted.status == (
            raced_value if raced_column == "status" else CaseStatus.NOT_FILED.value
        )
        assert persisted.title_cn == "更新前标题"
        assert getattr(persisted, raced_column) == raced_value
        applicants = (
            fresh.query(T_CaseApplicant)
            .filter(T_CaseApplicant.case_id == CASE_ID)
            .order_by(T_CaseApplicant.seq)
            .all()
        )
        assert [(item.seq, item.name_cn) for item in applicants] == [(1, "更新前申请人")]
