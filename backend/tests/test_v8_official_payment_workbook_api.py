from __future__ import annotations

import inspect
from datetime import datetime
from types import SimpleNamespace

import pytest
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient

from app.api.deps import get_current_user
from app.core.errors import BusinessError
from app.db.session import get_db
from app.main import create_app
from app.modules.annuity import api as annuity_api

NOW = datetime(2026, 8, 13, 15, 0)
ACTOR_ID = "00000000-0000-4000-8000-000000000216"


class RecordingSession:
    def __init__(self, commit_error: Exception | None = None) -> None:
        self.commit_error = commit_error
        self.commits = 0
        self.rollbacks = 0

    def commit(self) -> None:
        self.commits += 1
        if self.commit_error is not None:
            raise self.commit_error

    def rollback(self) -> None:
        self.rollbacks += 1


def _route() -> APIRoute:
    matches = [
        route
        for route in annuity_api.router.routes
        if isinstance(route, APIRoute)
        and route.path == "/pay-lists/{pay_list_id}/official-workbook"
        and route.methods == {"POST"}
    ]
    assert len(matches) == 1
    return matches[0]


def _permission_dependency() -> object:
    return next(item.call for item in _route().dependant.dependencies if item.name == "_perm")


def _payload(**changes: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "idempotency_key": "official-workbook-http-1",
        "rows": [
            {
                "sequence_number": 1,
                "application_number": "CN202610000001",
                "business_type": "专利",
                "invoice_title": "测试申请人有限公司",
                "unified_social_credit_code": "91110000TEST000001",
                "fee_type": "申请费",
                "foreign_currency_amount": None,
                "amount_cny": 900,
                "remark": "TEST_ONLY",
            }
        ],
    }
    payload.update(changes)
    return payload


def _result(disposition: str = "CREATED") -> object:
    return SimpleNamespace(
        artifact_id="11111111-1111-4111-8111-111111111216",
        filename="缴费清单-版本2026\r\n.xlsm",
        content_type="application/vnd.ms-excel.sheet.macroEnabled.12",
        content=b"official-xlsm",
        content_sha256="a" * 64,
        template_version="版本2026\r\n",
        template_content_hash="b" * 64,
        workbook_input_version_id="22222222-2222-4222-8222-222222222216",
        managed_storage_path="official-payment-workbooks/7/artifact.xlsm",
        disposition=disposition,
    )


def _client(
    monkeypatch: pytest.MonkeyPatch,
    *,
    commit_error: Exception | None = None,
    authenticated: bool = True,
) -> tuple[TestClient, RecordingSession]:
    transaction = RecordingSession(commit_error)
    app = create_app()
    app.dependency_overrides[get_db] = lambda: transaction
    if authenticated:
        app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(id=ACTOR_ID)
    app.dependency_overrides[_permission_dependency()] = lambda: None
    monkeypatch.setattr(annuity_api, "_official_workbook_utcnow", lambda: NOW)
    monkeypatch.setattr(annuity_api, "_official_workbook_runtime_profile", lambda: "production")
    return TestClient(app), transaction


def test_exact_route_permission_server_command_and_created_download(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    commands: list[object] = []

    def generate(command: object, transaction: object) -> object:
        commands.append((command, transaction))
        return _result()

    monkeypatch.setattr(annuity_api, "generate_official_payment_workbook", generate)
    client, transaction = _client(monkeypatch)
    response = client.post("/api/v1/pay-lists/7/official-workbook", json=_payload())

    assert response.status_code == 201
    assert response.content == b"official-xlsm"
    assert response.headers["content-type"] == "application/vnd.ms-excel.sheet.macroEnabled.12"
    assert response.headers["x-fpms-workbook-disposition"] == "CREATED"
    assert response.headers["x-fpms-artifact-id"] == _result().artifact_id
    assert response.headers["x-fpms-template-content-sha256"] == "b" * 64
    assert response.headers["x-fpms-template-version"] == "%E7%89%88%E6%9C%AC2026%0D%0A"
    assert "\r" not in response.headers["content-disposition"]
    assert "\n" not in response.headers["content-disposition"]
    assert "filename*=UTF-8''" in response.headers["content-disposition"]
    command, supplied_transaction = commands[0]
    assert supplied_transaction is transaction
    assert command.pay_list_id == 7
    assert command.actor_id == ACTOR_ID
    assert command.generated_at == NOW
    assert command.runtime_profile == "production"
    assert command.idempotency_key == "official-workbook-http-1"
    assert command.rows[0].amount_cny == 900
    assert inspect.getclosurevars(_permission_dependency()).nonlocals["code"] == "PayList.Export"
    assert transaction.commits == 1 and transaction.rollbacks == 0


def test_reused_download_is_200_and_commit_failure_compensation_is_disposition_safe(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    compensated: list[str] = []
    monkeypatch.setattr(annuity_api, "compensate_official_payment_workbook", compensated.append)
    monkeypatch.setattr(
        annuity_api,
        "generate_official_payment_workbook",
        lambda *_args: _result("REUSED"),
    )
    client, transaction = _client(monkeypatch)
    assert client.post("/api/v1/pay-lists/7/official-workbook", json=_payload()).status_code == 200
    assert compensated == []
    assert transaction.commits == 1 and transaction.rollbacks == 0

    failing, transaction = _client(monkeypatch, commit_error=RuntimeError("commit failed"))
    response = failing.post("/api/v1/pay-lists/7/official-workbook", json=_payload())
    assert response.status_code == 500
    assert compensated == []
    assert transaction.commits == 1 and transaction.rollbacks == 1

    monkeypatch.setattr(
        annuity_api,
        "generate_official_payment_workbook",
        lambda *_args: _result("CREATED"),
    )
    failing, transaction = _client(monkeypatch, commit_error=RuntimeError("commit failed"))
    assert failing.post("/api/v1/pay-lists/7/official-workbook", json=_payload()).status_code == 500
    assert compensated == [_result().managed_storage_path]
    assert transaction.commits == 1 and transaction.rollbacks == 1


def test_service_errors_and_request_or_auth_failures_are_fail_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def reject(*_args: object) -> object:
        raise BusinessError("PAYMENT_WORKBOOK_INPUT_CONFIG_REQUIRED", "missing", status_code=409)

    monkeypatch.setattr(annuity_api, "generate_official_payment_workbook", reject)
    client, transaction = _client(monkeypatch)
    response = client.post("/api/v1/pay-lists/7/official-workbook", json=_payload())
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "PAYMENT_WORKBOOK_INPUT_CONFIG_REQUIRED"
    assert transaction.commits == 0 and transaction.rollbacks == 1

    for payload in (
        {},
        _payload(actor_id=ACTOR_ID),
        _payload(rows=[]),
        _payload(rows=[{**_payload()["rows"][0], "amount_cny": "Infinity"}]),
        _payload(rows=[{**_payload()["rows"][0], "fee_type": "申请费\x00"}]),
    ):
        client, transaction = _client(monkeypatch)
        assert client.post("/api/v1/pay-lists/7/official-workbook", json=payload).status_code == 422
        assert transaction.commits == transaction.rollbacks == 0

    anonymous, transaction = _client(monkeypatch, authenticated=False)
    assert (
        anonymous.post("/api/v1/pay-lists/7/official-workbook", json=_payload()).status_code == 401
    )
    assert transaction.commits == transaction.rollbacks == 0
