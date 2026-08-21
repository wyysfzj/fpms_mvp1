from __future__ import annotations

import hashlib
import runpy
from datetime import date
from pathlib import Path
from uuid import uuid4

import pytest

from app.core import demo_bundle
from app.modules.cases.models import Case, CaseActivityEvent
from app.modules.fees.models import FeeDraft, FeeItem, FeeObligation
from app.modules.masterdata.clients.models import Client


def _bundle(tmp_path: Path, *, integrated: bool = False):
    helpers = runpy.run_path(str(Path(__file__).with_name("test_demo_abc_runtime_bundle.py")))
    builder = "_valid_integrated_bundle" if integrated else "_valid_bundle"
    return helpers[builder](tmp_path)


def _seed_case(session_factory) -> tuple[str, str]:
    client_id = str(uuid4())
    case_id = str(uuid4())
    with session_factory() as db:
        db.add(
            Client(
                id=client_id,
                client_code=f"DEMO-{uuid4().hex[:8]}",
                name_cn="ABC 演示客户",
                client_type="CLIENT",
                default_currency="CNY",
                is_active=True,
            )
        )
        db.flush()
        db.add(
            Case(
                id=case_id,
                case_no=f"ABC-{uuid4().hex[:8]}",
                case_type="NORMAL",
                patent_category="INV",
                flow_dir="CN_DOMESTIC",
                client_id=client_id,
                title_cn="ABC 演示案件",
                status="NOT_FILED",
                business_stage="NEW_CASE",
                official_procedure_stage="NOT_SUBMITTED",
                legal_status="NOT_ESTABLISHED",
                lifecycle_revision=0,
                lifecycle_verification_status="CONFIRMED",
            )
        )
        db.commit()
    return client_id, case_id


def _configure_bundle(
    tmp_path: Path,
    monkeypatch,
    *,
    integrated: bool = False,
) -> tuple[Path, str]:
    root, _manifest, digest = _bundle(tmp_path, integrated=integrated)
    monkeypatch.setenv("FPMS_ENV", "demo")
    monkeypatch.setenv("FPMS_DEMO_SCOPE", "LOCAL_ABC_E2E")
    monkeypatch.setenv("FPMS_DEMO_RUN_PROFILE", "TECHNICAL_REHEARSAL")
    monkeypatch.setenv("FPMS_DEMO_BUNDLE_PATH", str(root))
    monkeypatch.setenv("FPMS_DEMO_EXPECTED_MANIFEST_SHA256", digest)
    monkeypatch.setenv(
        "FPMS_DEMO_EXPECTED_AUTHORITY_SHA256",
        hashlib.sha256((root / "authority.json").read_bytes()).hexdigest(),
    )
    monkeypatch.setenv(
        "FPMS_DEMO_EXPECTED_AUTHORITY_CLASSIFICATION", "SYNTHETIC_TEST_ONLY"
    )
    current_date = date(2026, 8, 21) if integrated else date(2026, 8, 16)
    monkeypatch.setattr(demo_bundle, "_current_demo_date", lambda: current_date)
    return root, digest


@pytest.mark.parametrize("integrated", [False, True])
def test_runtime_service_item_to_pay_locked_draft(
    client,
    auth_headers,
    session_factory,
    tmp_path,
    monkeypatch,
    integrated,
):
    _configure_bundle(tmp_path, monkeypatch, integrated=integrated)
    client_id, case_id = _seed_case(session_factory)
    expected_item = "DEMO_INTEGRATED_SERVICE_1" if integrated else "DEMO_SERVICE_1"
    expected_template = (
        "DEMO_INTEGRATED_LETTER_1" if integrated else "DEMO_INTERNAL_LETTER_1"
    )

    item_response = client.get("/api/v1/fees/demo-service-item", headers=auth_headers)
    assert item_response.status_code == 200, item_response.text
    assert item_response.json()["amount"] == "1200.00"
    assert item_response.json()["classification"] == "DEMO_ONLY"
    assert item_response.json()["template_code"] == expected_template
    assert len(item_response.json()["template_sha256"]) == 64
    assert item_response.json()["template_required_variables"] == ["case_no", "client_name"]

    command = {
        "case_id": case_id,
        "item_code": expected_item,
        "idempotency_key": "demo-service-intent-1",
    }
    create_response = client.post(
        "/api/v1/fees/demo-service-obligations", json=command, headers=auth_headers
    )
    assert create_response.status_code == 201, create_response.text
    created = create_response.json()
    obligation_id = created["obligation"]["id"]
    assert created["amount"] == "1200.00"
    assert created["manifest_sha256"]
    assert created["reused"] is False

    replay_response = client.post(
        "/api/v1/fees/demo-service-obligations", json=command, headers=auth_headers
    )
    assert replay_response.status_code == 200, replay_response.text
    assert replay_response.json()["obligation"]["id"] == obligation_id
    assert replay_response.json()["reused"] is True

    instruction = client.post(
        f"/api/v1/fees/obligations/{obligation_id}/instruction",
        json={"instruction": "PAY", "idempotency_key": "demo-service-pay-1"},
        headers=auth_headers,
    )
    assert instruction.status_code == 200, instruction.text

    draft_response = client.post(
        "/api/v1/fees/drafts",
        json={
            "case_id": case_id,
            "client_id": client_id,
            "draft_type": "GENERIC",
            "currency": "CNY",
            "obligation_id": obligation_id,
        },
        headers=auth_headers,
    )
    assert draft_response.status_code == 201, draft_response.text
    draft_id = draft_response.json()["id"]
    assert draft_response.json()["total_service"] == "1200.00"
    assert draft_response.json()["total_gov"] == "0.00"
    assert draft_response.json()["amount"] == "1200.00"

    lock_response = client.post(f"/api/v1/fees/drafts/{draft_id}/lock", headers=auth_headers)
    assert lock_response.status_code == 200, lock_response.text

    with session_factory() as db:
        assert db.get(FeeDraft, draft_id).status == "LOCKED"
        items = db.query(FeeItem).filter(FeeItem.draft_id == draft_id).all()
        assert len(items) == 1
        assert items[0].fee_type == "SERVICE"
        assert items[0].amount == 1200
        assert db.query(FeeObligation).count() == 1
        source_rows = (
            db.query(CaseActivityEvent)
            .filter(CaseActivityEvent.activity_type == "DEMO_SERVICE_PRICE_ITEM_SELECTED")
            .all()
        )
        assert len(source_rows) == 1


def test_demo_preflight_requires_validated_input_and_zero_business_counts(
    client,
    auth_headers,
    session_factory,
    tmp_path,
    monkeypatch,
):
    _configure_bundle(tmp_path, monkeypatch, integrated=True)

    response = client.get("/api/v1/fees/demo-preflight", headers=auth_headers)
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["readiness"] == "READY"
    assert payload["authority_classification"] == "SYNTHETIC_TEST_ONLY"
    assert payload["customer_activation_eligible"] is False
    assert payload["business_counts"] == {
        "client": 0,
        "contact": 0,
        "case": 0,
        "package": 0,
        "task": 0,
        "obligation": 0,
        "draft": 0,
        "bill": 0,
        "payment": 0,
        "offset": 0,
    }
    assert payload["template_code"] == "DEMO_INTEGRATED_LETTER_1"
    assert len(payload["template_sha256"]) == 64
    assert payload["item_code"] == "DEMO_INTEGRATED_SERVICE_1"
    assert len(payload["source_sha256"]) == 64

    _seed_case(session_factory)
    not_fresh = client.get("/api/v1/fees/demo-preflight", headers=auth_headers)
    assert not_fresh.status_code == 409
    assert not_fresh.json()["error"]["code"] == "DEMO_RUN_NOT_FRESH"


def test_demo_preflight_rejects_legacy_bundle_without_business_writes(
    client,
    auth_headers,
    session_factory,
    tmp_path,
    monkeypatch,
):
    _configure_bundle(tmp_path, monkeypatch)

    response = client.get("/api/v1/fees/demo-preflight", headers=auth_headers)

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "DEMO_INPUT_CONFIG_REQUIRED"
    with session_factory() as db:
        assert db.query(Client).count() == 0
        assert db.query(Case).count() == 0
        assert db.query(FeeObligation).count() == 0
        assert db.query(FeeDraft).count() == 0


def test_invalid_item_creates_no_fee_facts_and_cached_bundle_ignores_external_drift(
    client,
    auth_headers,
    session_factory,
    tmp_path,
    monkeypatch,
):
    root, _digest = _configure_bundle(tmp_path, monkeypatch)
    _client_id, case_id = _seed_case(session_factory)
    command = {
        "case_id": case_id,
        "item_code": "OTHER_ITEM",
        "idempotency_key": "demo-service-invalid-1",
    }

    wrong_item = client.post(
        "/api/v1/fees/demo-service-obligations", json=command, headers=auth_headers
    )
    assert wrong_item.status_code == 409, wrong_item.text

    first_item = client.get("/api/v1/fees/demo-service-item", headers=auth_headers)
    assert first_item.status_code == 200
    with (root / "manifest.json").open("ab") as stream:
        stream.write(b"tampered")
    cached_item = client.get("/api/v1/fees/demo-service-item", headers=auth_headers)
    assert cached_item.status_code == 200
    assert cached_item.json() == first_item.json()
    command["item_code"] = "DEMO_SERVICE_1"
    created_from_cached_snapshot = client.post(
        "/api/v1/fees/demo-service-obligations", json=command, headers=auth_headers
    )
    assert created_from_cached_snapshot.status_code == 201, created_from_cached_snapshot.text

    with session_factory() as db:
        assert db.query(FeeObligation).count() == 1
        assert db.query(FeeDraft).count() == 0
        assert db.query(FeeItem).count() == 0
