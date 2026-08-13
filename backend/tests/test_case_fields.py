"""Tests for A3 case field expansion — 15 new columns on t_case."""

from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
_COUNTER = 0


def _unique_case_no(prefix: str = "A3") -> str:
    global _COUNTER
    _COUNTER += 1
    return f"{prefix}_TEST_{_COUNTER:04d}"


def _create_client(
    client: TestClient,
    auth_headers: dict,
    name_cn: str = "案件测试客户",
    *,
    client_type: str = "CLIENT",
) -> str:
    resp = client.post(
        "/api/v1/clients",
        json={
            "client_code": f"CASE-C-{uuid4().hex[:8]}",
            "name_cn": name_cn,
            "name_en": "Case Test Client",
            "client_type": client_type,
            "default_currency": "CNY",
            "is_active": True,
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


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
    "fee_reduction": "0",
    "applicant_kind": "ENTITY",
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
            "fee_reduction": "0",
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
            "fee_reduction": "0",
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
            "fee_reduction": "0",
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
            "fee_reduction": "0",
            "applicants": _MINIMAL_APPLICANT,
            **_GROUP4_FIELDS,
        }
        r = client.post("/api/v1/cases", json=payload, headers=auth_headers)
        assert r.status_code == 201, r.text
        data = r.json()
        assert data["is_fee_monitor"] is True
        assert data["fee_reduction"] == "0"
        assert data["applicant_kind"] == "ENTITY"


# ---------------------------------------------------------------------------
# Create with all 15 fields
# ---------------------------------------------------------------------------
class TestCreateAll15:
    def test_create_with_all_15_fields(self, client: TestClient, auth_headers: dict):
        case_no = _unique_case_no()
        payload = {
            "case_no": case_no,
            "fee_reduction": "0",
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
            "fee_reduction": "0",
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
            json={
                "case_no": case_no,
                "fee_reduction": "0",
                "applicants": _MINIMAL_APPLICANT,
            },
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
            json={
                "case_no": case_no,
                "fee_reduction": "0",
                "applicants": _MINIMAL_APPLICANT,
            },
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
                "fee_reduction": "0",
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
            "fee_reduction": "0",
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
            "fee_reduction": "0",
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
            json={
                "case_no": case_no,
                "fee_reduction": "0",
                "applicants": _MINIMAL_APPLICANT,
            },
            headers=auth_headers,
        )
        assert r.status_code == 201
        case_id = r.json()["id"]

        r2 = client.get(f"/api/v1/cases/{case_id}", headers=auth_headers)
        detail = r2.json()
        assert detail["has_exam_request"] is None
        assert detail["is_fee_monitor"] is None


# ---------------------------------------------------------------------------
# Business rules — validation and consistency
# ---------------------------------------------------------------------------
class TestBusinessRules:
    def test_create_rejects_unknown_client_id(self, client: TestClient, auth_headers: dict):
        resp = client.post(
            "/api/v1/cases",
            json={
                "case_no": _unique_case_no("CLIENT"),
                "fee_reduction": "0",
                "client_id": str(uuid4()),
                "applicants": _MINIMAL_APPLICANT,
            },
            headers=auth_headers,
        )
        assert resp.status_code == 404, resp.text
        payload = resp.json()["error"]
        assert payload["code"] == "CLIENT_NOT_FOUND"

    def test_create_rejects_incomplete_priority_record(
        self, client: TestClient, auth_headers: dict
    ):
        client_id = _create_client(client, auth_headers)
        resp = client.post(
            "/api/v1/cases",
            json={
                "case_no": _unique_case_no("PRIO"),
                "fee_reduction": "0",
                "client_id": client_id,
                "applicants": _MINIMAL_APPLICANT,
                "priorities": [
                    {
                        "seq": 1,
                        "country_code": "CN",
                        "prio_no": "202510001",
                    }
                ],
            },
            headers=auth_headers,
        )
        assert resp.status_code == 400, resp.text
        payload = resp.json()["error"]
        assert payload["code"] == "CASE_PRIORITY_INCOMPLETE"

    def test_create_rejects_priority_record_with_blank_text_fields(
        self, client: TestClient, auth_headers: dict
    ):
        client_id = _create_client(client, auth_headers)
        resp = client.post(
            "/api/v1/cases",
            json={
                "case_no": _unique_case_no("PRIOBLANK"),
                "fee_reduction": "0",
                "client_id": client_id,
                "applicants": _MINIMAL_APPLICANT,
                "priorities": [
                    {
                        "seq": 1,
                        "country_code": "",
                        "prio_no": "   ",
                        "prio_date": "2025-01-15",
                    }
                ],
            },
            headers=auth_headers,
        )
        assert resp.status_code == 400, resp.text
        payload = resp.json()["error"]
        assert payload["code"] == "CASE_PRIORITY_INCOMPLETE"

    def test_update_rejects_direct_status_write(self, client: TestClient, auth_headers: dict):
        create_resp = client.post(
            "/api/v1/cases",
            json={
                "case_no": _unique_case_no("STATUS"),
                "fee_reduction": "0",
                "applicants": _MINIMAL_APPLICANT,
            },
            headers=auth_headers,
        )
        assert create_resp.status_code == 201, create_resp.text
        case_id = create_resp.json()["id"]

        update_resp = client.put(
            f"/api/v1/cases/{case_id}",
            json={"status": "OA1"},
            headers=auth_headers,
        )
        assert update_resp.status_code == 409, update_resp.text
        payload = update_resp.json()["error"]
        assert payload["code"] == "CASE_STATUS_MANAGED_BY_LIFECYCLE"

    def test_update_accepts_legacy_title_alias(self, client: TestClient, auth_headers: dict):
        create_resp = client.post(
            "/api/v1/cases",
            json={
                "case_no": _unique_case_no("TITLE"),
                "fee_reduction": "0",
                "applicants": _MINIMAL_APPLICANT,
            },
            headers=auth_headers,
        )
        assert create_resp.status_code == 201, create_resp.text
        case_id = create_resp.json()["id"]

        update_resp = client.put(
            f"/api/v1/cases/{case_id}",
            json={"title": "兼容标题"},
            headers=auth_headers,
        )
        assert update_resp.status_code == 200, update_resp.text
        assert update_resp.json()["title_cn"] == "兼容标题"


class TestDeferredBatch1Fields:
    def test_create_rejects_foreign_flow_without_foreign_agent(
        self, client: TestClient, auth_headers: dict
    ):
        client_id = _create_client(client, auth_headers, "涉外客户")
        resp = client.post(
            "/api/v1/cases",
            json={
                "case_no": _unique_case_no("FOREIGN"),
                "fee_reduction": "0",
                "client_id": client_id,
                "flow_dir": "FOREIGN_INBOUND",
                "applicants": _MINIMAL_APPLICANT,
            },
            headers=auth_headers,
        )
        assert resp.status_code == 400, resp.text
        assert resp.json()["error"]["code"] == "CASE_FOREIGN_AGENT_REQUIRED"

    def test_create_rejects_foreign_agent_with_wrong_client_type(
        self, client: TestClient, auth_headers: dict
    ):
        client_id = _create_client(client, auth_headers, "涉外客户")
        wrong_agent_id = _create_client(client, auth_headers, "非代理所客户", client_type="CLIENT")
        resp = client.post(
            "/api/v1/cases",
            json={
                "case_no": _unique_case_no("FOREIGNAGENT"),
                "fee_reduction": "0",
                "client_id": client_id,
                "flow_dir": "FOREIGN_INBOUND",
                "foreign_agent_id": wrong_agent_id,
                "applicants": _MINIMAL_APPLICANT,
            },
            headers=auth_headers,
        )
        assert resp.status_code == 400, resp.text
        assert resp.json()["error"]["code"] == "CASE_FOREIGN_AGENT_INVALID_TYPE"

    def test_create_detail_roundtrip_foreign_agent_and_bio_deposits(
        self, client: TestClient, auth_headers: dict
    ):
        client_id = _create_client(client, auth_headers, "涉外客户")
        foreign_agent_id = _create_client(client, auth_headers, "外方代理所", client_type="AGENT")
        resp = client.post(
            "/api/v1/cases",
            json={
                "case_no": _unique_case_no("BIO"),
                "fee_reduction": "0",
                "client_id": client_id,
                "flow_dir": "FOREIGN_INBOUND",
                "foreign_agent_id": foreign_agent_id,
                "foreign_ref": "FA-2026-001",
                "applicants": _MINIMAL_APPLICANT,
                "bio_deposits": [
                    {
                        "seq": 1,
                        "deposit_no": "CGMCC-10001",
                        "deposit_unit_name": "CGMCC",
                        "deposit_date": "2026-03-01",
                        "name": "菌株A",
                    },
                    {
                        "seq": 2,
                        "deposit_no": "CCTCC-20002",
                        "deposit_unit_name": "CCTCC",
                        "deposit_date": "2026-03-02",
                        "name": "菌株B",
                    },
                ],
            },
            headers=auth_headers,
        )
        assert resp.status_code == 201, resp.text
        data = resp.json()
        assert data["foreign_agent_id"] == foreign_agent_id
        assert data["foreign_ref"] == "FA-2026-001"
        assert len(data["bio_deposits"]) == 2

        detail = client.get(f"/api/v1/cases/{data['id']}", headers=auth_headers)
        assert detail.status_code == 200, detail.text
        payload = detail.json()
        assert payload["foreign_agent_id"] == foreign_agent_id
        assert payload["foreign_ref"] == "FA-2026-001"
        assert payload["foreign_agent_name"] == "外方代理所"
        assert payload["bio_deposits"][0]["deposit_no"] == "CGMCC-10001"
        assert payload["bio_deposits"][1]["deposit_unit_name"] == "CCTCC"

    def test_create_rejects_partial_bio_deposit_row(self, client: TestClient, auth_headers: dict):
        resp = client.post(
            "/api/v1/cases",
            json={
                "case_no": _unique_case_no("BIOERR"),
                "fee_reduction": "0",
                "applicants": _MINIMAL_APPLICANT,
                "bio_deposits": [
                    {
                        "seq": 1,
                        "deposit_no": "CGMCC-10003",
                    }
                ],
            },
            headers=auth_headers,
        )
        assert resp.status_code == 400, resp.text
        assert resp.json()["error"]["code"] == "CASE_BIO_DEPOSIT_INCOMPLETE"

    def test_create_rejects_duplicate_bio_deposit_seq(self, client: TestClient, auth_headers: dict):
        resp = client.post(
            "/api/v1/cases",
            json={
                "case_no": _unique_case_no("BIOSEQ"),
                "fee_reduction": "0",
                "applicants": _MINIMAL_APPLICANT,
                "bio_deposits": [
                    {
                        "seq": 1,
                        "deposit_no": "CGMCC-10003",
                        "deposit_unit_name": "CGMCC",
                        "deposit_date": "2026-03-03",
                        "name": "菌株A",
                    },
                    {
                        "seq": 1,
                        "deposit_no": "CGMCC-10004",
                        "deposit_unit_name": "CGMCC",
                        "deposit_date": "2026-03-04",
                        "name": "菌株B",
                    },
                ],
            },
            headers=auth_headers,
        )
        assert resp.status_code == 400, resp.text
        assert resp.json()["error"]["code"] == "CASE_DUPLICATE_BIO_DEPOSIT_SEQ"

    def test_create_rejects_pct_intl_without_required_fields(
        self, client: TestClient, auth_headers: dict
    ):
        resp = client.post(
            "/api/v1/cases",
            json={
                "case_no": _unique_case_no("PCTI"),
                "fee_reduction": "0",
                "case_type": "PCT_INTL",
                "applicants": _MINIMAL_APPLICANT,
            },
            headers=auth_headers,
        )
        assert resp.status_code == 400, resp.text
        assert resp.json()["error"]["code"] == "CASE_PCT_INTL_REQUIRED"

    def test_create_roundtrip_pct_intl_fields(self, client: TestClient, auth_headers: dict):
        resp = client.post(
            "/api/v1/cases",
            json={
                "case_no": _unique_case_no("PCTI"),
                "fee_reduction": "0",
                "case_type": "PCT_INTL",
                "applicants": _MINIMAL_APPLICANT,
                "intl_app_no": "PCT/CN2026/000001",
                "intl_app_date": "2026-01-05",
                "ro": "CNIPA",
                "isa": "CNISA",
                "ipea": "IPEA-CN",
                "intl_pub_no": "WO2026/123456",
                "intl_pub_date": "2026-07-10",
                "intl_pub_lang": "EN",
                "need_iper": True,
                "iper_date": "2026-11-10",
            },
            headers=auth_headers,
        )
        assert resp.status_code == 201, resp.text
        data = resp.json()
        assert data["intl_app_no"] == "PCT/CN2026/000001"
        assert data["need_iper"] is True

    def test_create_rejects_pct_natl_without_entry_date(
        self, client: TestClient, auth_headers: dict
    ):
        resp = client.post(
            "/api/v1/cases",
            json={
                "case_no": _unique_case_no("PCTN"),
                "fee_reduction": "0",
                "case_type": "PCT_NATL",
                "applicants": _MINIMAL_APPLICANT,
            },
            headers=auth_headers,
        )
        assert resp.status_code == 400, resp.text
        assert resp.json()["error"]["code"] == "CASE_PCT_NATL_REQUIRED"

    def test_create_roundtrip_pct_natl_fields(self, client: TestClient, auth_headers: dict):
        resp = client.post(
            "/api/v1/cases",
            json={
                "case_no": _unique_case_no("PCTN"),
                "fee_reduction": "0",
                "case_type": "PCT_NATL",
                "applicants": _MINIMAL_APPLICANT,
                "pct_national_entry_date": "2026-09-15",
            },
            headers=auth_headers,
        )
        assert resp.status_code == 201, resp.text
        assert resp.json()["pct_national_entry_date"] == "2026-09-15"

    def test_create_rejects_invalidation_without_required_fields(
        self, client: TestClient, auth_headers: dict
    ):
        resp = client.post(
            "/api/v1/cases",
            json={
                "case_no": _unique_case_no("INV"),
                "fee_reduction": "0",
                "case_type": "INVALIDATION",
                "applicants": _MINIMAL_APPLICANT,
            },
            headers=auth_headers,
        )
        assert resp.status_code == 400, resp.text
        assert resp.json()["error"]["code"] == "CASE_INVALIDATION_REQUIRED"

    def test_create_roundtrip_invalidation_fields(self, client: TestClient, auth_headers: dict):
        invalid_client_id = _create_client(client, auth_headers, "无效案委托方")
        original_case = client.post(
            "/api/v1/cases",
            json={
                "case_no": _unique_case_no("ORIG"),
                "fee_reduction": "0",
                "applicants": _MINIMAL_APPLICANT,
            },
            headers=auth_headers,
        )
        assert original_case.status_code == 201, original_case.text
        original_case_id = original_case.json()["id"]

        resp = client.post(
            "/api/v1/cases",
            json={
                "case_no": _unique_case_no("INV"),
                "fee_reduction": "0",
                "case_type": "INVALIDATION",
                "applicants": _MINIMAL_APPLICANT,
                "original_case_id": original_case_id,
                "invalid_client_id": invalid_client_id,
                "invalid_patentee": "某专利权人",
                "invalid_role": "REQUESTER",
            },
            headers=auth_headers,
        )
        assert resp.status_code == 201, resp.text
        data = resp.json()
        assert data["invalid_client_id"] == invalid_client_id
        assert data["invalid_patentee"] == "某专利权人"
        assert data["invalid_role"] == "REQUESTER"
        assert data["original_case_id"] == original_case_id
