"""B4 — FeeRate Dimensions + CalcMode Stub — Tests.

Covers:
  T1-T3:  CRUD via HTTP for new dimension fields
  T4-T6:  List filters (rate_group, country_code, calc_mode)
  T7-T10: Unit tests for calculate_fee_amount()
  T11:    Schema field presence check
"""

from __future__ import annotations

import uuid
from decimal import Decimal

# ---------------------------------------------------------------------------
# Constants & helpers
# ---------------------------------------------------------------------------
RATE_URL = "/api/v1/fees/rates"


def _unique(prefix: str = "B4") -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8].upper()}"


def _create_rate(client, auth_headers, **overrides) -> dict:
    payload = {
        "fee_code": _unique("RATE"),
        "fee_name": "Test Rate",
        "fee_type": "SERVICE",
        "currency": "CNY",
        "default_amount": "100.00",
        "enabled": True,
        **overrides,
    }
    resp = client.post(RATE_URL, json=payload, headers=auth_headers)
    assert resp.status_code == 201, f"Rate creation failed: {resp.text}"
    return resp.json()


# ---------------------------------------------------------------------------
# T1 — Create rate with ALL 9 new dimension fields
# ---------------------------------------------------------------------------
def test_create_fee_rate_with_dimensions(client, auth_headers):
    data = _create_rate(
        client,
        auth_headers,
        rate_group="PATENT_GOV",
        country_code="CN",
        case_type="NORMAL",
        patent_category="INV",
        calc_mode="FIXED",
        calc_params='{"note": "test"}',
        allow_reduction=True,
        effective_from="2026-01-01",
        effective_to="2026-12-31",
    )

    assert data["rate_group"] == "PATENT_GOV"
    assert data["country_code"] == "CN"
    assert data["case_type"] == "NORMAL"
    assert data["patent_category"] == "INV"
    assert data["calc_mode"] == "FIXED"
    assert data["calc_params"] == '{"note": "test"}'
    assert data["allow_reduction"] is True
    assert data["effective_from"] == "2026-01-01"
    assert data["effective_to"] == "2026-12-31"


# ---------------------------------------------------------------------------
# T2 — Backward compatibility: create rate without new fields
# ---------------------------------------------------------------------------
def test_create_fee_rate_without_dimensions(client, auth_headers):
    data = _create_rate(client, auth_headers)

    # Original fields still present
    assert data["fee_type"] == "SERVICE"
    assert data["currency"] == "CNY"
    assert data["enabled"] is True

    # New dimension fields should be None (service passes None explicitly)
    assert data["rate_group"] is None
    assert data["country_code"] is None
    assert data["case_type"] is None
    assert data["patent_category"] is None
    assert data["calc_params"] is None
    assert data["effective_from"] is None
    assert data["effective_to"] is None

    # calc_mode: service passes None when not provided; DB server_default
    # is 'FIXED' but explicit None in constructor overrides it.
    # allow_reduction: same pattern — explicit None overrides server_default 0.
    # Accept either None or the server_default value.
    assert data["calc_mode"] in (None, "FIXED")
    assert data["allow_reduction"] in (None, False)


# ---------------------------------------------------------------------------
# T3 — Update rate with new dimension fields
# ---------------------------------------------------------------------------
def test_update_fee_rate_dimensions(client, auth_headers):
    created = _create_rate(client, auth_headers)
    rate_id = created["id"]

    update_payload = {
        "rate_group": "ANNUITY",
        "country_code": "US",
        "case_type": "PCT",
        "patent_category": "UM",
        "calc_mode": "PER_CLAIM",
        "calc_params": '{"base": 150}',
        "allow_reduction": False,
        "effective_from": "2026-06-01",
        "effective_to": "2027-05-31",
    }
    resp = client.put(f"{RATE_URL}/{rate_id}", json=update_payload, headers=auth_headers)
    assert resp.status_code == 200, f"Update failed: {resp.text}"
    data = resp.json()

    assert data["rate_group"] == "ANNUITY"
    assert data["country_code"] == "US"
    assert data["case_type"] == "PCT"
    assert data["patent_category"] == "UM"
    assert data["calc_mode"] == "PER_CLAIM"
    assert data["calc_params"] == '{"base": 150}'
    assert data["allow_reduction"] is False
    assert data["effective_from"] == "2026-06-01"
    assert data["effective_to"] == "2027-05-31"


# ---------------------------------------------------------------------------
# T4 — Filter by rate_group
# ---------------------------------------------------------------------------
def test_list_fee_rates_filter_by_rate_group(client, auth_headers):
    group_a = _unique("GRP")
    group_b = _unique("GRP")

    _create_rate(client, auth_headers, rate_group=group_a)
    _create_rate(client, auth_headers, rate_group=group_a)
    _create_rate(client, auth_headers, rate_group=group_b)

    resp = client.get(RATE_URL, params={"rate_group": group_a}, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()

    assert data["total"] == 2
    assert all(item["rate_group"] == group_a for item in data["items"])


# ---------------------------------------------------------------------------
# T5 — Filter by country_code
# ---------------------------------------------------------------------------
def test_list_fee_rates_filter_by_country_code(client, auth_headers):
    cc = _unique("CC")[:10]  # country_code max 10 chars

    _create_rate(client, auth_headers, country_code=cc)
    _create_rate(client, auth_headers, country_code="XX")

    resp = client.get(RATE_URL, params={"country_code": cc}, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()

    assert data["total"] == 1
    assert data["items"][0]["country_code"] == cc


# ---------------------------------------------------------------------------
# T6 — Filter by calc_mode
# ---------------------------------------------------------------------------
def test_list_fee_rates_filter_by_calc_mode(client, auth_headers):
    tag = _unique("CM")
    _create_rate(client, auth_headers, fee_code=f"{tag}-FIX", calc_mode="FIXED")
    _create_rate(client, auth_headers, fee_code=f"{tag}-PC", calc_mode="PER_CLAIM")

    resp = client.get(RATE_URL, params={"calc_mode": "PER_CLAIM"}, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()

    per_claim_codes = [item["fee_code"] for item in data["items"]]
    assert f"{tag}-PC" in per_claim_codes
    # The FIXED one should NOT appear when filtering for PER_CLAIM
    assert f"{tag}-FIX" not in per_claim_codes


def test_fee_rate_api_accepts_skeleton_calc_mode_metadata(client, auth_headers):
    tag = _unique("SKELCM")
    mode_params = {
        "BY_YEAR": '{"year_no":1}',
        "BY_PAGES": '{"base_pages":30}',
        "COMPOSITE": '{"fixed":"100","per_claim":"20","base_claims":10}',
    }

    for mode, calc_params in mode_params.items():
        fee_code = f"{tag}-{mode}"
        data = _create_rate(
            client,
            auth_headers,
            fee_code=fee_code,
            calc_mode=mode,
            calc_params=calc_params,
        )

        assert data["calc_mode"] == mode
        assert data["calc_params"] == calc_params

        resp = client.get(RATE_URL, params={"calc_mode": mode}, headers=auth_headers)
        assert resp.status_code == 200
        items = resp.json()["items"]
        assert any(item["fee_code"] == fee_code and item["calc_mode"] == mode for item in items)

    created = _create_rate(client, auth_headers, fee_code=f"{tag}-UPDATE", calc_mode="FIXED")
    for mode, calc_params in mode_params.items():
        resp = client.put(
            f"{RATE_URL}/{created['id']}",
            json={"calc_mode": mode, "calc_params": calc_params},
            headers=auth_headers,
        )
        assert resp.status_code == 200, f"Update failed for {mode}: {resp.text}"
        updated = resp.json()
        assert updated["calc_mode"] == mode
        assert updated["calc_params"] == calc_params


# ---------------------------------------------------------------------------
# T7 — calculate_fee_amount: FIXED mode returns default_amount
# ---------------------------------------------------------------------------
def test_calc_fee_amount_fixed_mode():
    from app.modules.fees.models import FeeRate
    from app.modules.fees.service import calculate_fee_amount

    rate = FeeRate(
        id=str(uuid.uuid4()),
        fee_code="UNIT-FIX",
        fee_type="SERVICE",
        currency="CNY",
        default_amount=Decimal("250.00"),
        calc_mode="FIXED",
        enabled=True,
    )
    result = calculate_fee_amount(rate)
    assert result == Decimal("250.00")


# ---------------------------------------------------------------------------
# T8 — calculate_fee_amount: no calc_mode → falls back to FIXED
# ---------------------------------------------------------------------------
def test_calc_fee_amount_fixed_is_default():
    from app.modules.fees.models import FeeRate
    from app.modules.fees.service import calculate_fee_amount

    rate = FeeRate(
        id=str(uuid.uuid4()),
        fee_code="UNIT-NONE",
        fee_type="SERVICE",
        currency="CNY",
        default_amount=Decimal("500.00"),
        calc_mode=None,
        enabled=True,
    )
    result = calculate_fee_amount(rate)
    assert result == Decimal("500.00")


# ---------------------------------------------------------------------------
# T9 — calculate_fee_amount: PER_CLAIM (stub) → returns default_amount
# ---------------------------------------------------------------------------
def test_calc_fee_amount_per_claim_stub():
    from app.modules.fees.models import FeeRate
    from app.modules.fees.service import calculate_fee_amount

    rate = FeeRate(
        id=str(uuid.uuid4()),
        fee_code="UNIT-PC",
        fee_type="SERVICE",
        currency="CNY",
        default_amount=Decimal("75.00"),
        calc_mode="PER_CLAIM",
        enabled=True,
    )
    result = calculate_fee_amount(rate)
    # Stub: unimplemented modes return default_amount
    assert result == Decimal("75.00")


def test_calc_fee_amount_metadata_modes_fall_back_to_default_amount():
    from app.modules.fees.models import FeeRate
    from app.modules.fees.service import calculate_fee_amount

    for mode in ("BY_YEAR", "BY_PAGES", "COMPOSITE"):
        rate = FeeRate(
            id=str(uuid.uuid4()),
            fee_code=f"UNIT-{mode}",
            fee_type="SERVICE",
            currency="CNY",
            default_amount=Decimal("125.00"),
            calc_mode=mode,
            calc_params='{"note":"metadata-only"}',
            enabled=True,
        )
        result = calculate_fee_amount(rate)
        assert result == Decimal("125.00")


# ---------------------------------------------------------------------------
# T10 — calculate_fee_amount: default_amount=None → Decimal("0")
# ---------------------------------------------------------------------------
def test_calc_fee_amount_none_default_amount():
    from app.modules.fees.models import FeeRate
    from app.modules.fees.service import calculate_fee_amount

    rate = FeeRate(
        id=str(uuid.uuid4()),
        fee_code="UNIT-ZERO",
        fee_type="SERVICE",
        currency="CNY",
        default_amount=None,
        calc_mode="FIXED",
        enabled=True,
    )
    result = calculate_fee_amount(rate)
    assert result == Decimal("0")


# ---------------------------------------------------------------------------
# T11 — FeeRateOut schema includes all 9 new fields
# ---------------------------------------------------------------------------
def test_fee_rate_out_schema_has_new_fields():
    from app.modules.fees.schemas import FeeRateOut

    expected_fields = {
        "rate_group",
        "country_code",
        "case_type",
        "patent_category",
        "calc_mode",
        "calc_params",
        "allow_reduction",
        "effective_from",
        "effective_to",
    }
    actual_fields = set(FeeRateOut.model_fields.keys())
    missing = expected_fields - actual_fields
    assert not missing, f"FeeRateOut is missing fields: {missing}"
