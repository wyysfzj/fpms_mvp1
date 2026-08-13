from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient

from app.modules.annuity.models import PayList

assert PayList.__tablename__ == "t_pay_list"


def _case_no(prefix: str = "PD-P1-OFFICIAL") -> str:
    return f"{prefix}-{uuid4().hex[:10]}"


def _official_case_payload(case_no: str) -> dict:
    return {
        "case_no": case_no,
        "fee_reduction": "0",
        "case_type": "NORMAL",
        "patent_category": "INV",
        "flow_dir": "CN_DOMESTIC",
        "title_cn": "官方字段案件",
        "applicants": [
            {
                "seq": 1,
                "is_first": True,
                "name_cn": "官方字段申请人",
                "name_en": "Official Applicant",
                "address_cn": "上海市浦东新区",
                "nationality": "CN",
                "certificate_type": "统一社会信用代码",
                "certificate_no": "91310000123456789X",
                "official_postcode": "200120",
                "official_applicant_kind": "ENTITY",
            }
        ],
        "inventors": [
            {
                "seq": 1,
                "name_cn": "官方字段发明人",
                "name_en": "Official Inventor",
                "nationality": "CN",
                "china_id_no": "110101199001011234",
            }
        ],
    }


def test_case_create_detail_and_list_roundtrip_official_fields(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    case_no = _case_no()
    response = client.post(
        "/api/v1/cases",
        json=_official_case_payload(case_no),
        headers=auth_headers,
    )
    assert response.status_code == 201, response.text
    created = response.json()
    case_id = created["id"]

    applicant = created["applicants"][0]
    inventor = created["inventors"][0]
    assert applicant["nationality"] == "CN"
    assert applicant["certificate_type"] == "统一社会信用代码"
    assert applicant["certificate_no"] == "91310000123456789X"
    assert applicant["official_postcode"] == "200120"
    assert applicant["official_applicant_kind"] == "ENTITY"
    assert inventor["nationality"] == "CN"
    assert inventor["china_id_no"] == "110101199001011234"

    detail_response = client.get(f"/api/v1/cases/{case_id}", headers=auth_headers)
    assert detail_response.status_code == 200, detail_response.text
    detail = detail_response.json()
    assert detail["applicants"][0]["official_postcode"] == "200120"
    assert detail["inventors"][0]["china_id_no"] == "110101199001011234"

    list_response = client.get(f"/api/v1/cases?case_no={case_no}", headers=auth_headers)
    assert list_response.status_code == 200, list_response.text
    item = list_response.json()["items"][0]
    assert item["applicants"][0]["certificate_no"] == "91310000123456789X"
    assert item["inventors"][0]["china_id_no"] == "110101199001011234"


def test_case_full_update_replaces_official_fields(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    create_response = client.post(
        "/api/v1/cases",
        json=_official_case_payload(_case_no("PD-P1-UPD")),
        headers=auth_headers,
    )
    assert create_response.status_code == 201, create_response.text
    case_id = create_response.json()["id"]

    update_response = client.put(
        f"/api/v1/cases/{case_id}",
        json={
            "applicants": [
                {
                    "seq": 1,
                    "is_first": True,
                    "name_cn": "更新后申请人",
                    "nationality": "US",
                    "certificate_type": "护照",
                    "certificate_no": "P1234567",
                    "official_postcode": "10001",
                    "official_applicant_kind": "INDIVIDUAL",
                }
            ],
            "inventors": [
                {
                    "seq": 1,
                    "name_cn": "更新后发明人",
                    "nationality": "US",
                    "china_id_no": None,
                }
            ],
        },
        headers=auth_headers,
    )

    assert update_response.status_code == 200, update_response.text
    updated = update_response.json()
    assert updated["applicants"][0]["nationality"] == "US"
    assert updated["applicants"][0]["certificate_no"] == "P1234567"
    assert updated["inventors"][0]["nationality"] == "US"
    assert updated["inventors"][0]["china_id_no"] is None


def test_china_national_inventor_requires_china_id_no(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    payload = _official_case_payload(_case_no("PD-P1-CNID"))
    payload["inventors"] = [{"seq": 1, "name_cn": "缺身份证发明人", "nationality": "CN"}]

    response = client.post("/api/v1/cases", json=payload, headers=auth_headers)

    assert response.status_code == 400, response.text
    assert response.json()["error"]["code"] == "CASE_INVENTOR_CHINA_ID_REQUIRED"
