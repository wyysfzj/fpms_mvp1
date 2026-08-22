from __future__ import annotations

from datetime import datetime
from types import SimpleNamespace

import pytest

from app.core.errors import BusinessError
from app.modules.annuity import api
from app.modules.annuity.models import PayList
from app.modules.annuity.service import ExportInternalPayListResult


class _Session:
    def __init__(
        self,
        *,
        pay_list: PayList | None = None,
        commit_error: Exception | None = None,
    ) -> None:
        self.pay_list = pay_list
        self.commit_error = commit_error
        self.commits = 0
        self.rollbacks = 0

    def get(self, model: object, identity: object) -> object | None:
        assert model is PayList
        if self.pay_list is not None:
            assert identity == self.pay_list.id
        return self.pay_list

    def commit(self) -> None:
        self.commits += 1
        if self.commit_error is not None:
            raise self.commit_error

    def rollback(self) -> None:
        self.rollbacks += 1


def _user() -> SimpleNamespace:
    return SimpleNamespace(id="actor-pay-list-route")


def _pay_list(*, status: str = "DRAFT") -> PayList:
    return PayList(
        id=7,
        client_id="client-pay-list-route",
        pay_list_no="PL-000007",
        status=status,
        currency="CNY",
    )


def _export_result(*, reused: bool = False) -> ExportInternalPayListResult:
    return ExportInternalPayListResult(
        artifact_id="artifact-pay-list-route",
        pay_list_id=7,
        filename="PL-000007-export.xlsx",
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        content=b"internal-xlsx",
        content_sha256="a" * 64,
        managed_storage_path="pay-list-exports/7/artifact-pay-list-route.xlsx",
        activity_ids=("activity-pay-list-route",),
        generated_at=datetime(2026, 8, 9, 12, 0),
        idempotency_key="pay-list-internal-export:http-v1:7",
        reused=reused,
    )


def test_create_route_supplies_actor_and_commits_before_return(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[dict[str, object]] = []
    expected = {"pay_list": {"id": 7, "status": "DRAFT"}}

    def create(_db: object, **kwargs: object) -> dict[str, object]:
        calls.append(kwargs)
        return expected

    monkeypatch.setattr(api, "create_pay_list_from_fee_items", create)
    transaction = _Session()
    result = api.post_pay_list_from_fee_items(
        api.PayListFromFeeItemsIn(
            fee_item_ids=["fee-item-1"],
            planned_pay_date=None,
            remark="boundary",
        ),
        current_user=_user(),
        db=transaction,
    )

    assert result == expected
    assert calls == [
        {
            "fee_item_ids": ["fee-item-1"],
            "planned_pay_date": None,
            "remark": "boundary",
            "actor_id": "actor-pay-list-route",
        }
    ]
    assert (transaction.commits, transaction.rollbacks) == (1, 0)


@pytest.mark.parametrize("failure_at", ("service", "commit"))
def test_create_route_rolls_back_every_failure(
    monkeypatch: pytest.MonkeyPatch,
    failure_at: str,
) -> None:
    failure = RuntimeError(failure_at)

    def create(_db: object, **_kwargs: object) -> dict[str, object]:
        if failure_at == "service":
            raise failure
        return {"pay_list": {"id": 7}}

    monkeypatch.setattr(api, "create_pay_list_from_fee_items", create)
    transaction = _Session(commit_error=failure if failure_at == "commit" else None)

    with pytest.raises(RuntimeError, match=failure_at):
        api.post_pay_list_from_fee_items(
            api.PayListFromFeeItemsIn(fee_item_ids=["fee-item-1"]),
            current_user=_user(),
            db=transaction,
        )

    assert transaction.rollbacks == 1


def test_export_route_uses_exact_replay_key_and_preserves_binary_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    commands: list[object] = []
    expected = _export_result()

    def export(command: object, transaction: object) -> ExportInternalPayListResult:
        commands.append(command)
        assert transaction is db
        return expected

    monkeypatch.setattr(api, "export_internal_pay_list", export, raising=False)
    assert not hasattr(api, "export_pay_list")
    db = _Session(pay_list=_pay_list())

    response = api.post_pay_list_export(7, current_user=_user(), db=db)

    assert response.body == expected.content
    assert response.media_type == expected.content_type
    assert response.headers["content-disposition"] == (
        'attachment; filename="PL-000007-export.xlsx"'
    )
    assert len(commands) == 1
    command = commands[0]
    assert (
        command.pay_list_id,
        command.actor_id,
        command.idempotency_key,
    ) == (7, "actor-pay-list-route", "pay-list-internal-export:http-v1:7")
    assert db.pay_list is not None and db.pay_list.status == "DRAFT"
    assert (db.commits, db.rollbacks) == (1, 0)


@pytest.mark.parametrize(
    ("pay_list", "code", "status_code"),
    (
        (None, "PAY_LIST_NOT_FOUND", 404),
        (_pay_list(status="EXPORTED"), "PAY_LIST_STATE_CONFLICT", 409),
        (_pay_list(status="PAID"), "PAY_LIST_STATE_CONFLICT", 409),
    ),
)
def test_export_route_preserves_missing_and_non_draft_fail_closed_statuses(
    monkeypatch: pytest.MonkeyPatch,
    pay_list: PayList | None,
    code: str,
    status_code: int,
) -> None:
    monkeypatch.setattr(
        api,
        "export_internal_pay_list",
        lambda *_args, **_kwargs: pytest.fail("blocked export must not call the service"),
        raising=False,
    )
    db = _Session(pay_list=pay_list)

    with pytest.raises(BusinessError) as captured:
        api.post_pay_list_export(7, current_user=_user(), db=db)

    assert (captured.value.code, captured.value.status_code) == (code, status_code)
    assert (db.commits, db.rollbacks) == (0, 0)


@pytest.mark.parametrize("reused", (False, True))
def test_export_commit_failure_compensates_only_fresh_managed_file(
    monkeypatch: pytest.MonkeyPatch,
    reused: bool,
) -> None:
    expected = _export_result(reused=reused)
    compensated: list[str] = []
    monkeypatch.setattr(api, "export_internal_pay_list", lambda *_args: expected, raising=False)
    monkeypatch.setattr(
        api,
        "compensate_internal_pay_list_export",
        compensated.append,
        raising=False,
    )
    db = _Session(pay_list=_pay_list(), commit_error=RuntimeError("commit failed"))

    with pytest.raises(RuntimeError, match="commit failed"):
        api.post_pay_list_export(7, current_user=_user(), db=db)

    assert (db.commits, db.rollbacks) == (1, 1)
    assert compensated == ([] if reused else [expected.managed_storage_path])


def test_export_service_failure_rolls_back_without_file_compensation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    compensated: list[str] = []

    def fail(*_args: object) -> ExportInternalPayListResult:
        raise RuntimeError("service failed")

    monkeypatch.setattr(api, "export_internal_pay_list", fail, raising=False)
    monkeypatch.setattr(
        api,
        "compensate_internal_pay_list_export",
        compensated.append,
        raising=False,
    )
    db = _Session(pay_list=_pay_list())

    with pytest.raises(RuntimeError, match="service failed"):
        api.post_pay_list_export(7, current_user=_user(), db=db)

    assert (db.commits, db.rollbacks) == (0, 1)
    assert compensated == []
