from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient

from app.modules.masterdata.applicants.models import Applicant


def _case_no(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:8].upper()}"


def _seed_applicant(session_factory, *, applicant_type: str = "ENTITY") -> str:
    applicant_id = str(uuid4())
    unique_suffix = uuid4().hex[:8].upper()
    with session_factory() as db:
        db.add(
            Applicant(
                id=applicant_id,
                code=f"APP-{unique_suffix}",
                name_cn=f"案件组合测试申请人-{unique_suffix}",
                name_en=None,
                applicant_type=applicant_type,
                is_active=True,
            )
        )
        db.commit()
    return applicant_id


def _minimal_applicants_payload(applicant_id: str) -> list[dict[str, object]]:
    return [
        {
            "seq": 1,
            "is_first": True,
            "applicant_id": applicant_id,
            "name_cn": "案件组合测试申请人",
        }
    ]


def _assert_error(response, status_code: int, error_code: str) -> dict:
    assert response.status_code == status_code, response.text
    payload = response.json()
    assert payload["error"]["code"] == error_code
    assert payload["error"]["message"]
    return payload


def test_create_case_rejects_illegal_case_type_patent_category_combo(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory,
) -> None:
    applicant_id = _seed_applicant(session_factory, applicant_type="ENTITY")
    response = client.post(
        "/api/v1/cases",
        headers=auth_headers,
        json={
            "case_no": _case_no("BADCOMBO"),
            "fee_reduction": "0",
            "case_type": "SEARCH",
            "patent_category": "DES",
            "flow_dir": "CN_DOMESTIC",
            "applicants": _minimal_applicants_payload(applicant_id),
            "title_cn": "非法组合测试",
        },
    )

    payload = _assert_error(response, 400, "CASE_TYPE_COMBO_INVALID")
    details = payload["error"]["details"]
    assert details["case_type"] == "SEARCH"
    assert details["patent_category"] == "DES"


def test_create_case_allows_normal_invention_combo(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory,
) -> None:
    case_no = _case_no("GOODCOMBO")
    applicant_id = _seed_applicant(session_factory, applicant_type="ENTITY")

    response = client.post(
        "/api/v1/cases",
        headers=auth_headers,
        json={
            "case_no": case_no,
            "fee_reduction": "0",
            "case_type": "NORMAL",
            "patent_category": "INV",
            "flow_dir": "CN_DOMESTIC",
            "applicants": _minimal_applicants_payload(applicant_id),
            "title_cn": "合法组合测试",
        },
    )

    assert response.status_code == 201, response.text
    payload = response.json()
    assert payload["case_no"] == case_no
    assert payload["case_type"] == "NORMAL"
    assert payload["patent_category"] == "INV"


def test_duplicate_case_no_keeps_duplicate_error_semantics(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory,
) -> None:
    case_no = _case_no("DUPCOMBO")
    applicant_id = _seed_applicant(session_factory, applicant_type="ENTITY")
    payload = {
        "case_no": case_no,
        "fee_reduction": "0",
        "case_type": "NORMAL",
        "patent_category": "INV",
        "flow_dir": "CN_DOMESTIC",
        "applicants": _minimal_applicants_payload(applicant_id),
        "title_cn": "重复案号语义测试",
    }
    created = client.post("/api/v1/cases", headers=auth_headers, json=payload)
    assert created.status_code == 201, created.text

    duplicate = client.post("/api/v1/cases", headers=auth_headers, json=payload)

    _assert_error(duplicate, 400, "CASE_NO_DUPLICATE")
