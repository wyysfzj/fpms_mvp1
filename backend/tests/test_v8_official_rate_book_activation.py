from __future__ import annotations

import hashlib
import json
from datetime import date, datetime, timezone
from uuid import uuid4

import pytest
from sqlalchemy import event, select, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.errors import BusinessError
from app.modules.auth.models import T_User
from app.modules.fees.models import FeeRate, OfficialRateBook
from app.modules.fees.official_rate_book import (
    ActivateOfficialRateBookCommand,
    OfficialRateBookActivationDisposition,
    activate_official_rate_book,
)
from scripts.seed_dev import seed_official_fee_rate_catalog

REFERENCE = "https://www.cnipa.gov.cn/art/2026/7/13/rate-book.html"
PUBLISHED_ON = date(2026, 7, 13)
APPROVED_AT = datetime(2026, 7, 13, 9, 0, 0)
ACTIVATED_AT = datetime(2026, 7, 13, 10, 0, 0)


def _snapshot(
    *,
    url: str = REFERENCE,
    published_on: str = "2026-07-13",
    retrieved_at: str = "2026-07-13T08:00:00Z",
    content_sha256: str = "b" * 64,
    document_no: str | None = None,
    title: str = "Synthetic CNIPA activation fixture",
) -> tuple[str, str]:
    snapshot = json.dumps(
        {
            "schema_version": "CNIPA_RATE_SOURCE_V1",
            "sources": [
                {
                    "content_sha256": content_sha256,
                    "document_no": document_no,
                    "published_on": published_on,
                    "retrieved_at": retrieved_at,
                    "title": title,
                    "url": url,
                }
            ],
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    return snapshot, hashlib.sha256(snapshot.encode("utf-8")).hexdigest()


def _actor(db: Session, *, active: bool = True) -> T_User:
    actor = T_User(
        id=str(uuid4()),
        username=f"rate-book-{uuid4()}",
        password_hash="not-used",
        is_active=active,
    )
    db.add(actor)
    db.flush()
    return actor


def _book(
    db: Session,
    *,
    book_code: str = "CNIPA-PATENT-FEES",
    version_code: str | None = None,
    effective_from: date = date(2026, 7, 1),
    effective_to: date | None = date(2026, 12, 31),
    approval_status: str = "PENDING",
    approved_by: str | None = None,
    approved_at: datetime | None = None,
    activation_status: str = "INACTIVE",
    activated_by: str | None = None,
    activated_at: datetime | None = None,
    current_identity_key: str | None = None,
    source_reference: str = REFERENCE,
    source_published_on: date = PUBLISHED_ON,
    source_snapshot: str | None = None,
    source_snapshot_hash: str | None = None,
) -> OfficialRateBook:
    if source_snapshot is None:
        source_snapshot, calculated_hash = _snapshot(url=source_reference)
    else:
        calculated_hash = hashlib.sha256(source_snapshot.encode("utf-8")).hexdigest()
    row = OfficialRateBook(
        id=str(uuid4()),
        book_code=book_code,
        version_code=version_code or f"SYNTHETIC-{uuid4()}",
        source_authority="CNIPA",
        source_reference=source_reference,
        source_version="SYNTHETIC-ACTIVATION-FIXTURE",
        source_published_on=source_published_on,
        source_snapshot=source_snapshot,
        source_snapshot_hash=source_snapshot_hash or calculated_hash,
        approval_status=approval_status,
        approved_by=approved_by,
        approved_at=approved_at,
        effective_from=effective_from,
        effective_to=effective_to,
        activation_status=activation_status,
        activated_by=activated_by,
        activated_at=activated_at,
        current_identity_key=current_identity_key,
    )
    db.add(row)
    db.flush()
    return row


def _command(
    row: OfficialRateBook,
    actor: T_User,
    *,
    expected_current_rate_book_id: str | None = None,
    approved_at: datetime = APPROVED_AT,
    activated_at: datetime = ACTIVATED_AT,
) -> ActivateOfficialRateBookCommand:
    return ActivateOfficialRateBookCommand(
        rate_book_id=row.id,
        approved_by=actor.id,
        approved_at=approved_at,
        activated_by=actor.id,
        activated_at=activated_at,
        expected_current_rate_book_id=expected_current_rate_book_id,
    )


def _assert_error(
    code: str,
    status_code: int,
    callable_,
) -> BusinessError:
    with pytest.raises(BusinessError) as caught:
        callable_()
    assert caught.value.code == code
    assert caught.value.status_code == status_code
    return caught.value


def _unsafe_update(db: Session, row_id: str, assignment: str, values: dict[str, object]) -> None:
    db.execute(text("PRAGMA ignore_check_constraints=ON"))
    try:
        db.execute(
            text(f"UPDATE t_fee_rate_book SET {assignment} WHERE id = :row_id"),
            {"row_id": row_id, **values},
        )
    finally:
        db.execute(text("PRAGMA ignore_check_constraints=OFF"))
    db.expire_all()


def _install_unique_current_race_trigger(
    db: Session,
    *,
    trigger_name: str,
    candidate: OfficialRateBook,
    predecessor: OfficialRateBook,
    synthetic_winner_id: str,
    observation_function: str,
) -> None:
    db.execute(
        text(
            f"""
            CREATE TEMP TRIGGER {trigger_name}
            BEFORE UPDATE OF current_identity_key ON t_fee_rate_book
            WHEN OLD.id = '{candidate.id}'
                 AND NEW.current_identity_key = 'CNIPA|{candidate.book_code}'
            BEGIN
                SELECT {observation_function}(
                    (SELECT activation_status
                     FROM t_fee_rate_book WHERE id = '{predecessor.id}'),
                    (SELECT current_identity_key
                     FROM t_fee_rate_book WHERE id = '{predecessor.id}')
                );
                INSERT INTO t_fee_rate_book (
                    id, book_code, version_code, source_authority,
                    source_reference, source_version, source_published_on,
                    source_snapshot, source_snapshot_hash, approval_status,
                    approved_by, approved_at, effective_from, effective_to,
                    activation_status, activated_by, activated_at,
                    current_identity_key, updated_by, updated_at
                ) VALUES (
                    '{synthetic_winner_id}', NEW.book_code, 'SYNTHETIC-RACE-WINNER',
                    NEW.source_authority, NEW.source_reference, NEW.source_version,
                    NEW.source_published_on, NEW.source_snapshot,
                    NEW.source_snapshot_hash, 'APPROVED', NEW.approved_by,
                    NEW.approved_at, NEW.effective_from, NEW.effective_to,
                    'ACTIVE', NEW.activated_by, NEW.activated_at,
                    NEW.current_identity_key, NEW.activated_by, NEW.activated_at
                );
            END
            """
        )
    )


def test_pending_and_preapproved_candidates_activate_without_committing(
    session_factory: sessionmaker,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with session_factory() as db:
        actor = _actor(db)
        pending = _book(db)
        monkeypatch.setattr(
            db,
            "commit",
            lambda: pytest.fail("activation service must not commit caller transaction"),
        )

        result = activate_official_rate_book(_command(pending, actor), db)

        assert result.rate_book_id == pending.id
        assert result.book_code == pending.book_code
        assert result.version_code == pending.version_code
        assert result.effective_from == pending.effective_from
        assert result.effective_to == pending.effective_to
        assert result.approval_status == "APPROVED"
        assert result.activation_status == "ACTIVE"
        assert result.disposition is OfficialRateBookActivationDisposition.ACTIVATED
        assert pending.approved_by == actor.id
        assert pending.approved_at == APPROVED_AT
        assert pending.activated_by == actor.id
        assert pending.activated_at == ACTIVATED_AT
        assert pending.current_identity_key == f"CNIPA|{pending.book_code}"
        db.rollback()

    with session_factory() as db:
        actor = _actor(db)
        preapproved = _book(
            db,
            approval_status="APPROVED",
            approved_by=actor.id,
            approved_at=APPROVED_AT,
        )
        result = activate_official_rate_book(_command(preapproved, actor), db)
        assert result.disposition is OfficialRateBookActivationDisposition.ACTIVATED
        assert preapproved.approved_by == actor.id
        assert preapproved.approved_at == APPROVED_AT
        assert preapproved.activated_by == actor.id


def test_exact_replay_reuses_and_differing_payload_conflicts(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as db:
        actor = _actor(db)
        candidate = _book(db)
        command = _command(candidate, actor)
        activate_official_rate_book(command, db)

        replay = ActivateOfficialRateBookCommand(
            **{
                **command.__dict__,
                "expected_current_rate_book_id": str(uuid4()),
            }
        )
        reused = activate_official_rate_book(replay, db)
        assert reused.disposition is OfficialRateBookActivationDisposition.REUSED

        conflicting = ActivateOfficialRateBookCommand(
            **{
                **command.__dict__,
                "activated_at": datetime(2026, 7, 13, 10, 0, 1),
            }
        )
        _assert_error(
            "OFFICIAL_RATE_BOOK_ACTIVATION_PAYLOAD_CONFLICT",
            409,
            lambda: activate_official_rate_book(conflicting, db),
        )


@pytest.mark.parametrize(
    ("field", "mutator"),
    (
        (
            "source_snapshot",
            lambda row, db: _unsafe_update(db, row.id, "source_snapshot = :value", {"value": "{"}),
        ),
        (
            "source_snapshot",
            lambda row, db: _unsafe_update(
                db,
                row.id,
                "source_snapshot = :value, source_snapshot_hash = :hash",
                {
                    "value": json.dumps(json.loads(row.source_snapshot), ensure_ascii=False),
                    "hash": hashlib.sha256(
                        json.dumps(json.loads(row.source_snapshot), ensure_ascii=False).encode()
                    ).hexdigest(),
                },
            ),
        ),
        (
            "source_snapshot",
            lambda row, db: _replace_snapshot(db, row, {"unexpected": True}),
        ),
        (
            "source_snapshot",
            lambda row, db: _replace_snapshot(
                db, row, {"sources": None}, remove=("schema_version",)
            ),
        ),
        ("sources", lambda row, db: _replace_snapshot(db, row, {"sources": []})),
        (
            "content_sha256",
            lambda row, db: _replace_first_source(db, row, {"content_sha256": "A" * 64}),
        ),
        (
            "source_snapshot_hash",
            lambda row, db: _unsafe_update(
                db, row.id, "source_snapshot_hash = :value", {"value": "0" * 64}
            ),
        ),
        (
            "published_on",
            lambda row, db: _replace_first_source(db, row, {"published_on": "2026-02-30"}),
        ),
        (
            "retrieved_at",
            lambda row, db: _replace_first_source(
                db, row, {"retrieved_at": "2026-07-13T08:00:00+00:00"}
            ),
        ),
        (
            "source_reference",
            lambda row, db: _unsafe_update(
                db,
                row.id,
                "source_reference = :value",
                {"value": "https://www.cnipa.gov.cn/other.html"},
            ),
        ),
        (
            "source_published_on",
            lambda row, db: _unsafe_update(
                db,
                row.id,
                "source_published_on = :value",
                {"value": "2026-07-12"},
            ),
        ),
        ("sources", lambda row, db: _replace_first_source(db, row, {"extra": "x"})),
        ("document_no", lambda row, db: _replace_first_source(db, row, {"document_no": ""})),
        ("title", lambda row, db: _replace_first_source(db, row, {"title": " fixture"})),
        (
            "effective_to",
            lambda row, db: _unsafe_update(
                db,
                row.id,
                "effective_to = :value",
                {"value": "2026-06-30"},
            ),
        ),
        (
            "book_code",
            lambda row, db: _unsafe_update(
                db, row.id, "book_code = :value", {"value": " CNIPA-PATENT-FEES"}
            ),
        ),
    ),
)
def test_canonical_snapshot_hash_and_cross_field_validation_fail_closed(
    session_factory: sessionmaker,
    field: str,
    mutator,
) -> None:
    with session_factory() as db:
        actor = _actor(db)
        candidate = _book(db)
        mutator(candidate, db)
        candidate = db.get(OfficialRateBook, candidate.id)

        error = _assert_error(
            "OFFICIAL_RATE_BOOK_SOURCE_INVALID",
            409,
            lambda: activate_official_rate_book(_command(candidate, actor), db),
        )
        assert error.details["field"] == field
        db.refresh(candidate)
        assert candidate.activation_status == "INACTIVE"


def _replace_snapshot(
    db: Session,
    row: OfficialRateBook,
    updates: dict[str, object],
    *,
    remove: tuple[str, ...] = (),
) -> None:
    value = json.loads(row.source_snapshot)
    for key in remove:
        value.pop(key, None)
    value.update(updates)
    snapshot = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    _unsafe_update(
        db,
        row.id,
        "source_snapshot = :value, source_snapshot_hash = :hash",
        {"value": snapshot, "hash": hashlib.sha256(snapshot.encode()).hexdigest()},
    )


def _replace_first_source(
    db: Session,
    row: OfficialRateBook,
    updates: dict[str, object],
) -> None:
    value = json.loads(row.source_snapshot)
    value["sources"][0].update(updates)
    snapshot = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    _unsafe_update(
        db,
        row.id,
        "source_snapshot = :value, source_snapshot_hash = :hash",
        {"value": snapshot, "hash": hashlib.sha256(snapshot.encode()).hexdigest()},
    )


@pytest.mark.parametrize(
    ("authority", "url"),
    (
        ("WIPO", REFERENCE),
        ("CNIPA", "docs/postdemo/标准费率.XLS"),
        ("CNIPA", "http://www.tianyueip.com/product/612"),
        ("CNIPA", "https://example.com/rates"),
        ("CNIPA", "http://www.cnipa.gov.cn/rates"),
        ("CNIPA", f"{REFERENCE}?download=1"),
        ("CNIPA", f"{REFERENCE}#rates"),
        ("CNIPA", "https://user@www.cnipa.gov.cn/rates"),
        ("CNIPA", "https://www.cnipa.gov.cn:443/rates"),
    ),
)
def test_only_exact_cnipa_https_sources_are_trusted(
    session_factory: sessionmaker,
    authority: str,
    url: str,
) -> None:
    with session_factory() as db:
        actor = _actor(db)
        snapshot, snapshot_hash = _snapshot(url=url)
        candidate = _book(
            db,
            source_reference=url,
            source_snapshot=snapshot,
            source_snapshot_hash=snapshot_hash,
        )
        if authority != "CNIPA":
            _unsafe_update(
                db,
                candidate.id,
                "source_authority = :authority",
                {"authority": authority},
            )
            candidate = db.get(OfficialRateBook, candidate.id)

        _assert_error(
            "OFFICIAL_RATE_BOOK_SOURCE_UNTRUSTED",
            409,
            lambda: activate_official_rate_book(_command(candidate, actor), db),
        )
        db.refresh(candidate)
        assert candidate.activation_status == "INACTIVE"


def test_invalid_commands_missing_or_inactive_actors_and_bad_states_fail_closed(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as db:
        actor = _actor(db)
        candidate = _book(db)
        _assert_error(
            "OFFICIAL_RATE_BOOK_INVALID_INPUT",
            400,
            lambda: activate_official_rate_book(object(), db),
        )
        _assert_error(
            "OFFICIAL_RATE_BOOK_INVALID_INPUT",
            400,
            lambda: activate_official_rate_book(
                ActivateOfficialRateBookCommand(
                    rate_book_id="NOT-A-UUID",
                    approved_by=actor.id,
                    approved_at=APPROVED_AT,
                    activated_by=actor.id,
                    activated_at=ACTIVATED_AT,
                    expected_current_rate_book_id=None,
                ),
                db,
            ),
        )
        _assert_error(
            "OFFICIAL_RATE_BOOK_INVALID_INPUT",
            400,
            lambda: activate_official_rate_book(
                _command(
                    candidate,
                    actor,
                    approved_at=datetime(2026, 7, 13, 9, tzinfo=timezone.utc),
                ),
                db,
            ),
        )
        missing_candidate = _command(candidate, actor)
        missing_candidate = ActivateOfficialRateBookCommand(
            **{**missing_candidate.__dict__, "rate_book_id": str(uuid4())}
        )
        _assert_error(
            "OFFICIAL_RATE_BOOK_NOT_FOUND",
            404,
            lambda: activate_official_rate_book(missing_candidate, db),
        )

        missing_actor = _command(candidate, actor)
        missing_actor = ActivateOfficialRateBookCommand(
            **{**missing_actor.__dict__, "approved_by": str(uuid4())}
        )
        _assert_error(
            "OFFICIAL_RATE_BOOK_ACTOR_NOT_FOUND",
            404,
            lambda: activate_official_rate_book(missing_actor, db),
        )

        inactive = _actor(db, active=False)
        _assert_error(
            "OFFICIAL_RATE_BOOK_ACTOR_INACTIVE",
            409,
            lambda: activate_official_rate_book(_command(candidate, inactive), db),
        )

    with session_factory() as db:
        actor = _actor(db)
        rejected = _book(
            db,
            approval_status="REJECTED",
            approved_by=actor.id,
            approved_at=APPROVED_AT,
        )
        _assert_error(
            "OFFICIAL_RATE_BOOK_STATE_CONFLICT",
            409,
            lambda: activate_official_rate_book(_command(rejected, actor), db),
        )

        retired = _book(
            db,
            book_code="CNIPA-RETIRED-CANDIDATE",
            approval_status="APPROVED",
            approved_by=actor.id,
            approved_at=APPROVED_AT,
            activation_status="RETIRED",
            activated_by=actor.id,
            activated_at=ACTIVATED_AT,
        )
        _assert_error(
            "OFFICIAL_RATE_BOOK_STATE_CONFLICT",
            409,
            lambda: activate_official_rate_book(_command(retired, actor), db),
        )

        inconsistent = _book(db, book_code="CNIPA-INCONSISTENT")
        _unsafe_update(
            db,
            inconsistent.id,
            "approved_by = :actor_id",
            {"actor_id": actor.id},
        )
        inconsistent = db.get(OfficialRateBook, inconsistent.id)
        _assert_error(
            "OFFICIAL_RATE_BOOK_STATE_CONFLICT",
            409,
            lambda: activate_official_rate_book(_command(inconsistent, actor), db),
        )


def test_inclusive_overlap_retired_history_and_next_day_successor_rules(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as db:
        actor = _actor(db)
        predecessor = _book(
            db,
            effective_from=date(2026, 1, 1),
            effective_to=date(2026, 6, 30),
            approval_status="APPROVED",
            approved_by=actor.id,
            approved_at=APPROVED_AT,
            activation_status="ACTIVE",
            activated_by=actor.id,
            activated_at=ACTIVATED_AT,
            current_identity_key="CNIPA|CNIPA-PATENT-FEES",
        )
        same_day = _book(
            db,
            effective_from=date(2026, 6, 30),
            effective_to=date(2026, 12, 31),
        )
        _assert_error(
            "OFFICIAL_RATE_BOOK_INTERVAL_OVERLAP",
            409,
            lambda: activate_official_rate_book(
                _command(
                    same_day,
                    actor,
                    expected_current_rate_book_id=predecessor.id,
                ),
                db,
            ),
        )
        assert predecessor.activation_status == "ACTIVE"
        assert same_day.activation_status == "INACTIVE"
        db.rollback()

    with session_factory() as db:
        actor = _actor(db)
        retired = _book(
            db,
            effective_from=date(2026, 1, 1),
            effective_to=date(2026, 6, 30),
            approval_status="APPROVED",
            approved_by=actor.id,
            approved_at=APPROVED_AT,
            activation_status="RETIRED",
            activated_by=actor.id,
            activated_at=ACTIVATED_AT,
        )
        overlap = _book(
            db,
            effective_from=date(2026, 6, 1),
            effective_to=date(2026, 12, 31),
        )
        _assert_error(
            "OFFICIAL_RATE_BOOK_INTERVAL_OVERLAP",
            409,
            lambda: activate_official_rate_book(_command(overlap, actor), db),
        )
        assert retired.activation_status == "RETIRED"
        db.rollback()

    with session_factory() as db:
        actor = _actor(db)
        first_approved_at = datetime(2026, 1, 1, 9)
        first_activated_at = datetime(2026, 1, 1, 10)
        predecessor = _book(
            db,
            effective_from=date(2026, 1, 1),
            effective_to=date(2026, 6, 30),
            approval_status="APPROVED",
            approved_by=actor.id,
            approved_at=first_approved_at,
            activation_status="ACTIVE",
            activated_by=actor.id,
            activated_at=first_activated_at,
            current_identity_key="CNIPA|CNIPA-PATENT-FEES",
        )
        predecessor_source = (
            predecessor.source_snapshot,
            predecessor.source_snapshot_hash,
            predecessor.source_reference,
            predecessor.approved_by,
            predecessor.approved_at,
            predecessor.activated_by,
            predecessor.activated_at,
        )
        successor = _book(
            db,
            effective_from=date(2026, 7, 1),
            effective_to=date(2026, 12, 31),
        )

        activate_official_rate_book(
            _command(successor, actor, expected_current_rate_book_id=predecessor.id),
            db,
        )

        assert predecessor.activation_status == "RETIRED"
        assert predecessor.current_identity_key is None
        assert predecessor.updated_by == actor.id
        assert predecessor.updated_at == ACTIVATED_AT
        assert (
            predecessor.source_snapshot,
            predecessor.source_snapshot_hash,
            predecessor.source_reference,
            predecessor.approved_by,
            predecessor.approved_at,
            predecessor.activated_by,
            predecessor.activated_at,
        ) == predecessor_source
        assert successor.activation_status == "ACTIVE"


def test_expected_current_cas_leaves_one_winner_and_no_partial_write(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as db:
        actor = _actor(db)
        candidate = _book(db)
        _assert_error(
            "OFFICIAL_RATE_BOOK_CURRENT_IDENTITY_CONFLICT",
            409,
            lambda: activate_official_rate_book(
                _command(
                    candidate,
                    actor,
                    expected_current_rate_book_id=str(uuid4()),
                ),
                db,
            ),
        )
        assert candidate.approval_status == "PENDING"
        assert candidate.activation_status == "INACTIVE"

        winner = _book(db, version_code="SYNTHETIC-WINNER")
        activate_official_rate_book(_command(winner, actor), db)
        loser = _book(db, version_code="SYNTHETIC-LOSER")
        _assert_error(
            "OFFICIAL_RATE_BOOK_CURRENT_IDENTITY_CONFLICT",
            409,
            lambda: activate_official_rate_book(_command(loser, actor), db),
        )

        assert winner.activation_status == "ACTIVE"
        assert winner.current_identity_key == "CNIPA|CNIPA-PATENT-FEES"
        assert loser.approval_status == "PENDING"
        assert loser.activation_status == "INACTIVE"
        assert (
            db.scalar(
                select(OfficialRateBook).where(
                    OfficialRateBook.current_identity_key == "CNIPA|CNIPA-PATENT-FEES"
                )
            ).id
            == winner.id
        )

        unrelated = _actor(db)
        db.flush()
        assert db.get(T_User, unrelated.id) is unrelated


def test_unique_current_integrity_race_rolls_back_only_nested_activation(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as db:
        actor = _actor(db)
        predecessor = _book(
            db,
            effective_from=date(2026, 1, 1),
            effective_to=date(2026, 6, 30),
            approval_status="APPROVED",
            approved_by=actor.id,
            approved_at=datetime(2026, 1, 1, 9),
            activation_status="ACTIVE",
            activated_by=actor.id,
            activated_at=datetime(2026, 1, 1, 10),
            current_identity_key="CNIPA|CNIPA-PATENT-FEES",
        )
        candidate = _book(
            db,
            effective_from=date(2026, 7, 1),
            effective_to=date(2026, 12, 31),
        )
        trigger_name = "fpms_rate_book_unique_race_conflict"
        observation_function = "fpms_observe_rate_book_unique_race_conflict"
        synthetic_winner_id = str(uuid4())
        observations: list[tuple[str, str | None]] = []
        connection = db.connection()
        raw_connection = connection.connection
        raw_connection.create_function(
            observation_function,
            2,
            lambda status, current_key: observations.append((status, current_key)) or 1,
        )
        _install_unique_current_race_trigger(
            db,
            trigger_name=trigger_name,
            candidate=candidate,
            predecessor=predecessor,
            synthetic_winner_id=synthetic_winner_id,
            observation_function=observation_function,
        )
        try:
            error = _assert_error(
                "OFFICIAL_RATE_BOOK_CURRENT_IDENTITY_CONFLICT",
                409,
                lambda: activate_official_rate_book(
                    _command(
                        candidate,
                        actor,
                        expected_current_rate_book_id=predecessor.id,
                    ),
                    db,
                ),
            )

            assert observations == [("RETIRED", None)]
            assert error.details == {
                "rate_book_id": candidate.id,
                "expected_current_rate_book_id": predecessor.id,
                "actual_current_rate_book_id": predecessor.id,
            }
            db.refresh(predecessor)
            db.refresh(candidate)
            assert predecessor.activation_status == "ACTIVE"
            assert predecessor.current_identity_key == "CNIPA|CNIPA-PATENT-FEES"
            assert candidate.approval_status == "PENDING"
            assert candidate.activation_status == "INACTIVE"
            assert db.get(OfficialRateBook, synthetic_winner_id) is None
            active_ids = tuple(
                db.scalars(
                    select(OfficialRateBook.id).where(
                        OfficialRateBook.activation_status == "ACTIVE"
                    )
                ).all()
            )
            assert active_ids == (predecessor.id,)

            unrelated = _actor(db)
            db.flush()
            assert db.get(T_User, unrelated.id) is unrelated
        finally:
            db.execute(text(f"DROP TRIGGER IF EXISTS {trigger_name}"))
            raw_connection.create_function(observation_function, 2, None)


def test_unique_current_integrity_race_reuses_exact_same_candidate_winner(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as db:
        actor = _actor(db)
        predecessor = _book(
            db,
            effective_from=date(2026, 1, 1),
            effective_to=date(2026, 6, 30),
            approval_status="APPROVED",
            approved_by=actor.id,
            approved_at=datetime(2026, 1, 1, 9),
            activation_status="ACTIVE",
            activated_by=actor.id,
            activated_at=datetime(2026, 1, 1, 10),
            current_identity_key="CNIPA|CNIPA-PATENT-FEES",
        )
        candidate = _book(
            db,
            effective_from=date(2026, 7, 1),
            effective_to=date(2026, 12, 31),
        )
        command = _command(
            candidate,
            actor,
            expected_current_rate_book_id=predecessor.id,
        )
        predecessor_id = predecessor.id
        candidate_id = candidate.id
        actor_id = actor.id
        trigger_name = "fpms_rate_book_unique_race_reuse"
        observation_function = "fpms_observe_rate_book_unique_race_reuse"
        synthetic_winner_id = str(uuid4())
        trigger_observations: list[tuple[str, str | None]] = []
        restored_observations: list[tuple[str, str | None, str, str | None]] = []
        connection = db.connection()
        raw_connection = connection.connection
        raw_connection.create_function(
            observation_function,
            2,
            lambda status, current_key: trigger_observations.append((status, current_key)) or 1,
        )
        _install_unique_current_race_trigger(
            db,
            trigger_name=trigger_name,
            candidate=candidate,
            predecessor=predecessor,
            synthetic_winner_id=synthetic_winner_id,
            observation_function=observation_function,
        )
        installed = False

        def install_exact_winner_before_service_reread(
            sqlalchemy_connection,
            _cursor,
            statement,
            _parameters,
            _context,
            _executemany,
        ) -> None:
            nonlocal installed
            if (
                installed
                or not trigger_observations
                or not statement.lstrip().upper().startswith("SELECT")
            ):
                return
            driver_connection = sqlalchemy_connection.connection.driver_connection
            race_cursor = driver_connection.cursor()
            try:
                predecessor_state = race_cursor.execute(
                    "SELECT activation_status, current_identity_key "
                    "FROM t_fee_rate_book WHERE id = ?",
                    (predecessor_id,),
                ).fetchone()
                candidate_state = race_cursor.execute(
                    "SELECT activation_status, current_identity_key "
                    "FROM t_fee_rate_book WHERE id = ?",
                    (candidate_id,),
                ).fetchone()
                restored_observations.append((*predecessor_state, *candidate_state))
                race_cursor.execute(f"DROP TRIGGER IF EXISTS {trigger_name}")
                activated_at = command.activated_at.strftime("%Y-%m-%d %H:%M:%S.%f")
                approved_at = command.approved_at.strftime("%Y-%m-%d %H:%M:%S.%f")
                race_cursor.execute(
                    "UPDATE t_fee_rate_book "
                    "SET activation_status = 'RETIRED', current_identity_key = NULL, "
                    "updated_by = ?, updated_at = ? WHERE id = ?",
                    (actor_id, activated_at, predecessor_id),
                )
                race_cursor.execute(
                    "UPDATE t_fee_rate_book "
                    "SET approval_status = 'APPROVED', approved_by = ?, approved_at = ?, "
                    "activation_status = 'ACTIVE', activated_by = ?, activated_at = ?, "
                    "current_identity_key = ?, updated_by = ?, updated_at = ? "
                    "WHERE id = ?",
                    (
                        command.approved_by,
                        approved_at,
                        command.activated_by,
                        activated_at,
                        "CNIPA|CNIPA-PATENT-FEES",
                        command.activated_by,
                        activated_at,
                        candidate_id,
                    ),
                )
                installed = True
            finally:
                race_cursor.close()

        event.listen(
            connection,
            "before_cursor_execute",
            install_exact_winner_before_service_reread,
        )
        try:
            result = activate_official_rate_book(command, db)

            assert trigger_observations == [("RETIRED", None)]
            assert restored_observations == [
                (
                    "ACTIVE",
                    "CNIPA|CNIPA-PATENT-FEES",
                    "INACTIVE",
                    None,
                )
            ]
            assert result.disposition is OfficialRateBookActivationDisposition.REUSED
            assert result.rate_book_id == candidate.id
            db.refresh(predecessor)
            db.refresh(candidate)
            assert predecessor.activation_status == "RETIRED"
            assert predecessor.current_identity_key is None
            assert candidate.activation_status == "ACTIVE"
            assert candidate.current_identity_key == "CNIPA|CNIPA-PATENT-FEES"
            assert db.get(OfficialRateBook, synthetic_winner_id) is None
            active_ids = tuple(
                db.scalars(
                    select(OfficialRateBook.id).where(
                        OfficialRateBook.activation_status == "ACTIVE"
                    )
                ).all()
            )
            assert active_ids == (candidate.id,)

            unrelated = _actor(db)
            db.flush()
            assert db.get(T_User, unrelated.id) is unrelated
        finally:
            event.remove(
                connection,
                "before_cursor_execute",
                install_exact_winner_before_service_reread,
            )
            db.execute(text(f"DROP TRIGGER IF EXISTS {trigger_name}"))
            raw_connection.create_function(observation_function, 2, None)


def test_customer_fee_seed_is_idempotent_and_never_creates_or_links_rate_book(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as db:
        seed_official_fee_rate_catalog(db)
        first_ids = tuple(db.scalars(select(FeeRate.id).order_by(FeeRate.id)).all())
        seed_official_fee_rate_catalog(db)
        second_ids = tuple(db.scalars(select(FeeRate.id).order_by(FeeRate.id)).all())

        assert first_ids == second_ids
        assert db.scalar(select(OfficialRateBook.id).limit(1)) is None
        assert (
            db.scalar(select(FeeRate.id).where(FeeRate.official_rate_book_id.is_not(None)).limit(1))
            is None
        )
