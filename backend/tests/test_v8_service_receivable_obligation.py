from __future__ import annotations

import json
from contextlib import nullcontext
from datetime import datetime, timedelta
from decimal import Decimal
from types import SimpleNamespace

import pytest

from app.core.errors import BusinessError
from app.modules.fees import obligation_service as service
from app.modules.fees.obligation_contracts import (
    FeeDifferenceReviewState,
    FeeDomain,
    FeeOfficialEvidenceStatus,
    FeeSourceStatus,
)

NOW = datetime(2026, 8, 13, 16, 0)


class Transaction:
    def __init__(self, book: object) -> None:
        self.new: set[object] = set()
        self.dirty: set[object] = set()
        self.deleted: set[object] = set()
        self.no_autoflush = nullcontext()
        self.values = [SimpleNamespace(id="case-1", status="OPEN"), book, None]

    def scalar(self, _statement: object) -> object | None:
        return self.values.pop(0)


def _book(**changes: object) -> object:
    snapshot = json.dumps(
        {"items": [{"item_code": "SERVICE-FILING", "unit_price": "3000.00"}]},
        separators=(",", ":"),
    )
    values = {
        "id": "11111111-1111-4111-8111-111111111228",
        "source_classification": "PRODUCTION",
        "status": "ACTIVE",
        "scope_key": "GLOBAL",
        "current_identity_key": "GLOBAL",
        "effective_from": NOW - timedelta(days=1),
        "effective_to": NOW + timedelta(days=365),
        "source_reference": "managed://service-price-books/2026-08.json",
        "book_version": "2026.08",
        "item_snapshot": snapshot,
        "item_snapshot_hash": "a" * 64,
        "source_content_hash": "b" * 64,
        "currency": "CNY",
        "tax_policy": "EXCLUSIVE",
        "discount_policy": "NONE",
    }
    values.update(changes)
    return SimpleNamespace(**values)


def _command(**changes: object) -> service.CreateServiceReceivableObligationCommand:
    values = {
        "price_book_version_id": "11111111-1111-4111-8111-111111111228",
        "item_code": "SERVICE-FILING",
        "case_id": "case-1",
        "actor_id": "00000000-0000-4000-8000-000000000228",
        "idempotency_key": "service-receivable-1",
        "recognized_at": NOW,
    }
    values.update(changes)
    return service.CreateServiceReceivableObligationCommand(**values)


def _install(monkeypatch: pytest.MonkeyPatch, *, reused: bool = False) -> tuple[list, list]:
    sources: list[object] = []
    recognitions: list[object] = []
    monkeypatch.setattr(service, "_activation_snapshot", lambda _book: "gate-snapshot")
    monkeypatch.setattr(
        service,
        "resolve_decision_gate",
        lambda *_args: SimpleNamespace(
            resolved_scope_key="GLOBAL",
            source_reference="managed://service-price-books/2026-08.json",
            source_version="2026.08",
            decision_value="gate-snapshot",
        ),
    )
    monkeypatch.setattr(service, "_case_projection", lambda _case: SimpleNamespace())

    def append(command: object, *_args: object, **_kwargs: object) -> object:
        sources.append(command)
        return SimpleNamespace(activity_id="source-activity-1", reused=reused)

    def recognize(command: object, _transaction: object) -> object:
        recognitions.append(command)
        statuses = SimpleNamespace(
            official_evidence_status=FeeOfficialEvidenceStatus.NOT_APPLICABLE,
        )
        obligation = SimpleNamespace(fee_domain=FeeDomain.SERVICE, statuses=statuses)
        return SimpleNamespace(obligation=obligation, reused=reused)

    monkeypatch.setattr(service, "append_case_activity", append)
    monkeypatch.setattr(service, "recognize_obligation", recognize)
    return sources, recognitions


def test_approved_item_creates_service_only_obligation(monkeypatch: pytest.MonkeyPatch) -> None:
    sources, recognitions = _install(monkeypatch)
    result = service.create_service_receivable_obligation(_command(), Transaction(_book()))

    assert result.unit_price == Decimal("3000.00")
    assert result.reused is False
    source = sources[0]
    assert source.event_type == "SERVICE_PRICE_ITEM_SELECTED"
    assert source.lane.value == "FEE"
    assert source.payload["price_book_version_id"] == result.price_book_version_id
    assert source.payload["item_snapshot_hash"] == "a" * 64
    command = recognitions[0]
    assert command.fee_domain is FeeDomain.SERVICE
    assert command.source_status is FeeSourceStatus.VERIFIED
    assert command.source_document_id is None
    assert command.lines[0].official_full_amount is None
    assert command.lines[0].payable_amount == Decimal("3000.00")
    assert command.lines[0].difference_review_state is FeeDifferenceReviewState.MATCHED
    assert (
        result.recognition.obligation.statuses.official_evidence_status
        is FeeOfficialEvidenceStatus.NOT_APPLICABLE
    )


@pytest.mark.parametrize(
    "book",
    [
        _book(status="DRAFT", current_identity_key=None),
        _book(source_classification="TEST_ONLY"),
        _book(effective_from=NOW + timedelta(seconds=1)),
    ],
)
def test_inactive_or_ineligible_book_is_409_without_write(
    monkeypatch: pytest.MonkeyPatch,
    book: object,
) -> None:
    sources, recognitions = _install(monkeypatch)
    with pytest.raises(BusinessError) as caught:
        service.create_service_receivable_obligation(_command(), Transaction(book))
    assert caught.value.code == "SERVICE_RECEIVABLE_CONFLICT"
    assert caught.value.status_code == 409
    assert sources == recognitions == []


def test_gate_or_item_mismatch_is_409_without_write(monkeypatch: pytest.MonkeyPatch) -> None:
    sources, recognitions = _install(monkeypatch)
    monkeypatch.setattr(
        service,
        "resolve_decision_gate",
        lambda *_args: SimpleNamespace(
            resolved_scope_key="GLOBAL",
            source_reference="wrong",
            source_version="2026.08",
            decision_value="gate-snapshot",
        ),
    )
    with pytest.raises(BusinessError) as caught:
        service.create_service_receivable_obligation(_command(), Transaction(_book()))
    assert caught.value.code == "SERVICE_RECEIVABLE_CONFLICT"
    assert sources == recognitions == []

    monkeypatch.setattr(
        service,
        "resolve_decision_gate",
        lambda *_args: SimpleNamespace(
            resolved_scope_key="GLOBAL",
            source_reference="managed://service-price-books/2026-08.json",
            source_version="2026.08",
            decision_value="gate-snapshot",
        ),
    )
    with pytest.raises(BusinessError) as caught:
        service.create_service_receivable_obligation(
            _command(item_code="UNKNOWN"),
            Transaction(_book()),
        )
    assert caught.value.code == "SERVICE_RECEIVABLE_CONFLICT"
    assert sources == recognitions == []


def test_replay_uses_original_source_time_and_reuses_both_seams(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sources, recognitions = _install(monkeypatch, reused=True)
    transaction = Transaction(_book())
    transaction.values[-1] = SimpleNamespace(effective_at=NOW)
    result = service.create_service_receivable_obligation(
        _command(recognized_at=NOW + timedelta(seconds=5)),
        transaction,
    )
    assert result.reused is True
    assert sources[0].effective_at == NOW
    assert recognitions[0].lines[0].source_date == NOW.date()
