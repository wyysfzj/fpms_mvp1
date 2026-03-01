"""Tests for A3 case field expansion — 15 new columns on t_case."""

from __future__ import annotations

from fastapi.testclient import TestClient

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
_COUNTER = 0


def _unique_case_no(prefix: str = "A3") -> str:
    global _COUNTER
    _COUNTER += 1
    return f"{prefix}_TEST_{_COUNTER:04d}"


_GROUP1_FIELDS = {
    "pub_date": "2025-06-01",
    "pub_no": "CN202510001A",
    "grant_date": "2025-12-01",
    "grant_no": "CN202510001B",
    "patent_no": "ZL202510001.5",
    "valid_until": "2045-06-01",
}

_GROUP2_FIELDS = {
    "spec_pages": 42,
    "claim_count": 10,
    "has_exam_request": True,
}

_GROUP3_FIELDS = {
    "primary_agent_id": "aaaaaaaa-1111-1111-1111-aaaaaaaaaaaa",
    "second_agent_id": "bbbbbbbb-2222-2222-2222-bbbbbbbbbbbb",
    "draftor_id": "cccccccc-3333-3333-3333-cccccccccccc",
}

_GROUP4_FIELDS = {
    "is_fee_monitor": True,
    "fee_reduction": "70PCT",
    "applicant_kind": "ENTERPRISE",
}

_ALL_15 = {**_GROUP1_FIELDS, **_GROUP2_FIELDS, **_GROUP3_FIELDS, **_GROUP4_FIELDS}

_MINIMAL_APPLICANT = [{"seq": 1, "is_first": True, "name_cn": "测试申请人"}]


# ---------------------------------------------------------------------------
# Create tests — one per group
# ---------------------------------------------------------------------------
class TestCreateGroup1:
    def test_create_with_publication_grant_fields(self, client: TestClient, auth_headers: dict):
        payload = {
            "case_no": _unique_case_no(),
            "applicants": _MINIMAL_APPLICANT,
            **_GROUP1_FIELDS,
        }
        r = client.post("/api/v1/cases", json=payload, headers=auth_headers)
        assert r.status_code == 201, r.text
        data = r.json()
        assert data["pub_date"] == "2025-06-01"
        assert data["pub_no"] == "CN202510001A"
        assert data["grant_date"] == "2025-12-01"
        assert data["grant_no"] == "CN202510001B"
        assert data["patent_no"] == "ZL202510001.5"
        assert data["valid_until"] == "2045-06-01"


class TestCreateGroup2:
    def test_create_with_spec_detail_fields(self, client: TestClient, auth_headers: dict):
        payload = {
            "case_no": _unique_case_no(),
            "applicants": _MINIMAL_APPLICANT,
            **_GROUP2_FIELDS,
        }
        r = client.post("/api/v1/cases", json=payload, headers=auth_headers)
        assert r.status_code == 201, r.text
        data = r.json()
        assert data["spec_pages"] == 42
        assert data["claim_count"] == 10
        assert data["has_exam_request"] is True


class TestCreateGroup3:
    def test_create_with_agent_assignment_fields(self, client: TestClient, auth_headers: dict):
        payload = {
            "case_no": _unique_case_no(),
            "applicants": _MINIMAL_APPLICANT,
            **_GROUP3_FIELDS,
        }
        r = client.post("/api/v1/cases", json=payload, headers=auth_headers)
        assert r.status_code == 201, r.text
        data = r.json()
        assert data["primary_agent_id"] == _GROUP3_FIELDS["primary_agent_id"]
        assert data["second_agent_id"] == _GROUP3_FIELDS["second_agent_id"]
        assert data["draftor_id"] == _GROUP3_FIELDS["draftor_id"]


class TestCreateGroup4:
    def test_create_with_control_flag_fields(self, client: TestClient, auth_headers: dict):
        payload = {
            "case_no": _unique_case_no(),
            "applicants": _MINIMAL_APPLICANT,
            **_GROUP4_FIELDS,
        }
        r = client.post("/api/v1/cases", json=payload, headers=auth_headers)
        assert r.status_code == 201, r.text
        data = r.json()
        assert data["is_fee_monitor"] is True
        assert data["fee_reduction"] == "70PCT"
        assert data["applicant_kind"] == "ENTERPRISE"


# ---------------------------------------------------------------------------
# Create with all 15 fields
# ---------------------------------------------------------------------------
class TestCreateAll15:
    def test_create_with_all_15_fields(self, client: TestClient, auth_headers: dict):
        case_no = _unique_case_no()
        payload = {
            "case_no": case_no,
            "applicants": _MINIMAL_APPLICANT,
            **_ALL_15,
        }
        r = client.post("/api/v1/cases", json=payload, headers=auth_headers)
        assert r.status_code == 201, r.text
        data = r.json()
        # Verify all 15 fields round-trip
        for key in _ALL_15:
            assert key in data, f"Missing key {key} in response"
            if isinstance(_ALL_15[key], (int, bool)):
                assert data[key] == _ALL_15[key], f"{key}: {data[key]} != {_ALL_15[key]}"
            else:
                assert str(data[key]) == str(_ALL_15[key]), f"{key}: {data[key]} != {_ALL_15[key]}"


# ---------------------------------------------------------------------------
# GET detail returns all 15 fields
# ---------------------------------------------------------------------------
class TestGetDetail:
    def test_get_detail_includes_all_15(self, client: TestClient, auth_headers: dict):
        case_no = _unique_case_no()
        payload = {
            "case_no": case_no,
            "applicants": _MINIMAL_APPLICANT,
            **_ALL_15,
        }
        r = client.post("/api/v1/cases", json=payload, headers=auth_headers)
        assert r.status_code == 201
        case_id = r.json()["id"]

        r2 = client.get(f"/api/v1/cases/{case_id}", headers=auth_headers)
        assert r2.status_code == 200
        detail = r2.json()
        for key in _ALL_15:
            assert key in detail, f"Missing key {key} in detail response"


# ---------------------------------------------------------------------------
# PUT (full update) with new fields
# ---------------------------------------------------------------------------
class TestUpdateFull:
    def test_put_updates_new_fields(self, client: TestClient, auth_headers: dict):
        case_no = _unique_case_no()
        r = client.post(
            "/api/v1/cases",
            json={"case_no": case_no, "applicants": _MINIMAL_APPLICANT},
            headers=auth_headers,
        )
        assert r.status_code == 201
        case_id = r.json()["id"]

        # Update with all 15 fields via PUT
        r2 = client.put(
            f"/api/v1/cases/{case_id}",
            json=_ALL_15,
            headers=auth_headers,
        )
        assert r2.status_code == 200, r2.text
        data = r2.json()
        assert data["patent_no"] == "ZL202510001.5"
        assert data["spec_pages"] == 42
        assert data["primary_agent_id"] == _GROUP3_FIELDS["primary_agent_id"]
        assert data["is_fee_monitor"] is True


# ---------------------------------------------------------------------------
# POST limited-edit with spec_pages and claim_count
# ---------------------------------------------------------------------------
class TestLimitedEdit:
    def test_limited_edit_spec_fields(self, client: TestClient, auth_headers: dict):
        case_no = _unique_case_no()
        r = client.post(
            "/api/v1/cases",
            json={"case_no": case_no, "applicants": _MINIMAL_APPLICANT},
            headers=auth_headers,
        )
        assert r.status_code == 201
        case_id = r.json()["id"]

        r2 = client.post(
            f"/api/v1/cases/{case_id}/limited-edit",
            json={"spec_pages": 55, "claim_count": 8},
            headers=auth_headers,
        )
        assert r2.status_code == 200, r2.text

        # Verify via detail
        r3 = client.get(f"/api/v1/cases/{case_id}", headers=auth_headers)
        assert r3.status_code == 200
        detail = r3.json()
        assert detail["spec_pages"] == 55
        assert detail["claim_count"] == 8


# ---------------------------------------------------------------------------
# GET /cases (list) includes patent_no, primary_agent_id, app_no
# ---------------------------------------------------------------------------
class TestListFields:
    def test_list_includes_new_fields(self, client: TestClient, auth_headers: dict):
        case_no = _unique_case_no()
        r = client.post(
            "/api/v1/cases",
            json={
                "case_no": case_no,
                "applicants": _MINIMAL_APPLICANT,
                "patent_no": "ZL_LIST_001",
                "primary_agent_id": "dddddddd-4444-4444-4444-dddddddddddd",
                "app_no": "202510099999.X",
            },
            headers=auth_headers,
        )
        assert r.status_code == 201

        r2 = client.get(f"/api/v1/cases?case_no={case_no}", headers=auth_headers)
        assert r2.status_code == 200
        items = r2.json()["items"]
        assert len(items) >= 1
        item = items[0]
        assert item["patent_no"] == "ZL_LIST_001"
        assert item["primary_agent_id"] == "dddddddd-4444-4444-4444-dddddddddddd"
        assert item["app_no"] == "202510099999.X"


# ---------------------------------------------------------------------------
# Backward compatibility — create with no new fields
# ---------------------------------------------------------------------------
class TestBackwardCompat:
    def test_create_without_new_fields(self, client: TestClient, auth_headers: dict):
        """Existing callers that send no A3 fields should still work."""
        payload = {
            "case_no": _unique_case_no(),
            "applicants": _MINIMAL_APPLICANT,
        }
        r = client.post("/api/v1/cases", json=payload, headers=auth_headers)
        assert r.status_code == 201, r.text
        data = r.json()
        # All 15 fields should be None
        assert data["pub_date"] is None
        assert data["patent_no"] is None
        assert data["spec_pages"] is None
        assert data["primary_agent_id"] is None
        assert data["is_fee_monitor"] is None


# ---------------------------------------------------------------------------
# Date format validation — dates should be YYYY-MM-DD strings
# ---------------------------------------------------------------------------
class TestDateFormat:
    def test_date_fields_format(self, client: TestClient, auth_headers: dict):
        case_no = _unique_case_no()
        payload = {
            "case_no": case_no,
            "applicants": _MINIMAL_APPLICANT,
            "pub_date": "2025-06-15",
            "grant_date": "2025-12-20",
            "valid_until": "2045-06-15",
        }
        r = client.post("/api/v1/cases", json=payload, headers=auth_headers)
        assert r.status_code == 201
        case_id = r.json()["id"]

        r2 = client.get(f"/api/v1/cases/{case_id}", headers=auth_headers)
        assert r2.status_code == 200
        detail = r2.json()
        assert detail["pub_date"] == "2025-06-15"
        assert detail["grant_date"] == "2025-12-20"
        assert detail["valid_until"] == "2045-06-15"


# ---------------------------------------------------------------------------
# Boolean defaults — unset booleans should be None, not False
# ---------------------------------------------------------------------------
class TestBooleanDefaults:
    def test_unset_booleans_are_none(self, client: TestClient, auth_headers: dict):
        case_no = _unique_case_no()
        r = client.post(
            "/api/v1/cases",
            json={"case_no": case_no, "applicants": _MINIMAL_APPLICANT},
            headers=auth_headers,
        )
        assert r.status_code == 201
        case_id = r.json()["id"]

        r2 = client.get(f"/api/v1/cases/{case_id}", headers=auth_headers)
        detail = r2.json()
        assert detail["has_exam_request"] is None
        assert detail["is_fee_monitor"] is None
