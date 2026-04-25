from __future__ import annotations

from uuid import uuid4

import pytest

from app.core.errors import BusinessError
from app.modules.cases.service import validate_applicants
from app.modules.masterdata.applicants.models import Applicant


def _case_no(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:8].upper()}"


def _seed_applicant(session_factory, *, applicant_type: str, name_cn: str) -> str:
    unique_name_cn = f"{name_cn}-{uuid4().hex[:8].upper()}"
    applicant_id = str(uuid4())
    with session_factory() as db:
        db.add(
            Applicant(
                id=applicant_id,
                code=f"APP-{uuid4().hex[:8].upper()}",
                name_cn=unique_name_cn,
                name_en=None,
                applicant_type=applicant_type,
                is_active=True,
            )
        )
        db.commit()
    return applicant_id


def _first_applicant_payload(applicant_id: str, *, name_cn: str) -> list[dict[str, object]]:
    return [
        {
            "seq": 1,
            "is_first": True,
            "applicant_id": applicant_id,
            "name_cn": name_cn,
        }
    ]


def _assert_error(response, status_code: int, error_code: str) -> dict:
    assert response.status_code == status_code, response.text
    payload = response.json()
    assert payload["error"]["code"] == error_code
    assert payload["error"]["message"]
    return payload


def test_validate_applicants_keeps_existing_required_and_duplicate_first_errors() -> None:
    with pytest.raises(BusinessError) as empty_exc:
        validate_applicants([])

    assert empty_exc.value.code == "CASE_APPLICANT_REQUIRED"
    assert empty_exc.value.status_code == 400

    with pytest.raises(BusinessError) as duplicate_first_exc:
        validate_applicants(
            [
                {"seq": 1, "is_first": True},
                {"seq": 2, "is_first": True},
            ]
        )

    assert duplicate_first_exc.value.code == "CASE_DUPLICATE_FIRST_APPLICANT"
    assert duplicate_first_exc.value.status_code == 400


@pytest.mark.parametrize(
    ("seed_applicant_type", "first_applicant_type", "applicant_kind"),
    [
        ("INDIVIDUAL", "INDIVIDUAL", "ENTITY"),
        ("ENTITY", "ENTITY", "INDIVIDUAL"),
    ],
)
def test_create_case_rejects_applicant_kind_mismatch(
    client,
    auth_headers,
    session_factory,
    seed_applicant_type: str,
    first_applicant_type: str,
    applicant_kind: str,
) -> None:
    applicant_id = _seed_applicant(
        session_factory,
        applicant_type=seed_applicant_type,
        name_cn=f"{first_applicant_type} 申请人",
    )

    response = client.post(
        "/api/v1/cases",
        headers=auth_headers,
        json={
            "case_no": _case_no("APPKIND-ERR"),
            "applicants": _first_applicant_payload(
                applicant_id,
                name_cn=f"{first_applicant_type} 申请人",
            ),
            "applicant_kind": applicant_kind,
        },
    )

    payload = _assert_error(response, 400, "CASE_APPLICANT_KIND_MISMATCH")
    details = payload["error"]["details"]
    assert details["applicant_kind"] == applicant_kind
    assert details["first_applicant_type"] == first_applicant_type
    assert details["first_applicant_id"] == applicant_id


@pytest.mark.parametrize(
    ("seed_applicant_type", "first_applicant_type", "applicant_kind"),
    [
        ("INDIVIDUAL", "INDIVIDUAL", "INDIVIDUAL"),
        ("ENTITY", "ENTITY", "ENTITY"),
        ("ENTITY", "ENTITY", "UNIV"),
        ("ENTITY", "ENTITY", "GOV"),
        ("ENTITY", "ENTITY", None),
        ("ENTITY", "ENTITY", ""),
    ],
)
def test_create_case_allows_matching_or_blank_applicant_kind(
    client,
    auth_headers,
    session_factory,
    seed_applicant_type: str,
    first_applicant_type: str,
    applicant_kind: str | None,
) -> None:
    applicant_id = _seed_applicant(
        session_factory,
        applicant_type=seed_applicant_type,
        name_cn=f"{first_applicant_type} 申请人",
    )
    payload: dict[str, object] = {
        "case_no": _case_no("APPKIND-OK"),
        "applicants": _first_applicant_payload(
            applicant_id,
            name_cn=f"{first_applicant_type} 申请人",
        ),
    }
    if applicant_kind is not None:
        payload["applicant_kind"] = applicant_kind
    else:
        payload["applicant_kind"] = None

    response = client.post("/api/v1/cases", headers=auth_headers, json=payload)

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["applicant_kind"] == applicant_kind


def test_create_case_keeps_duplicate_first_error_when_applicant_kind_present(
    client,
    auth_headers,
    session_factory,
) -> None:
    applicant_id = _seed_applicant(
        session_factory,
        applicant_type="INDIVIDUAL",
        name_cn="重复首位申请人",
    )

    response = client.post(
        "/api/v1/cases",
        headers=auth_headers,
        json={
            "case_no": _case_no("APPKIND-DUP"),
            "applicants": [
                {
                    "seq": 1,
                    "is_first": True,
                    "applicant_id": applicant_id,
                    "name_cn": "重复首位申请人A",
                },
                {
                    "seq": 2,
                    "is_first": True,
                    "applicant_id": applicant_id,
                    "name_cn": "重复首位申请人B",
                },
            ],
            "applicant_kind": "ENTITY",
        },
    )

    payload = _assert_error(response, 400, "CASE_DUPLICATE_FIRST_APPLICANT")
    assert payload["error"]["details"] is None


def test_create_case_keeps_empty_applicant_error_when_applicant_kind_present(
    client,
    auth_headers,
) -> None:
    response = client.post(
        "/api/v1/cases",
        headers=auth_headers,
        json={
            "case_no": _case_no("APPKIND-EMPTY"),
            "applicants": [],
            "applicant_kind": "ENTITY",
        },
    )

    payload = _assert_error(response, 400, "CASE_APPLICANT_REQUIRED")
    assert payload["error"]["details"] is None


def test_put_case_rejects_applicant_kind_change_mismatch(
    client,
    auth_headers,
    session_factory,
) -> None:
    applicant_id = _seed_applicant(
        session_factory,
        applicant_type="INDIVIDUAL",
        name_cn="自然人申请人",
    )
    create_resp = client.post(
        "/api/v1/cases",
        headers=auth_headers,
        json={
            "case_no": _case_no("APPKIND-PUT"),
            "applicants": _first_applicant_payload(applicant_id, name_cn="自然人申请人"),
            "applicant_kind": "INDIVIDUAL",
        },
    )
    assert create_resp.status_code == 201, create_resp.text
    case_id = create_resp.json()["id"]

    update_resp = client.put(
        f"/api/v1/cases/{case_id}",
        headers=auth_headers,
        json={"applicant_kind": "ENTITY"},
    )

    payload = _assert_error(update_resp, 400, "CASE_APPLICANT_KIND_MISMATCH")
    details = payload["error"]["details"]
    assert details["applicant_kind"] == "ENTITY"
    assert details["first_applicant_type"] == "INDIVIDUAL"
    assert details["first_applicant_id"] == applicant_id


def test_put_case_rejects_applicant_update_kind_mismatch(
    client,
    auth_headers,
    session_factory,
) -> None:
    entity_applicant_id = _seed_applicant(
        session_factory,
        applicant_type="ENTITY",
        name_cn="法人申请人",
    )
    individual_applicant_id = _seed_applicant(
        session_factory,
        applicant_type="INDIVIDUAL",
        name_cn="自然人申请人",
    )
    create_resp = client.post(
        "/api/v1/cases",
        headers=auth_headers,
        json={
            "case_no": _case_no("APPKIND-PUT2"),
            "applicants": _first_applicant_payload(entity_applicant_id, name_cn="法人申请人"),
            "applicant_kind": "ENTITY",
        },
    )
    assert create_resp.status_code == 201, create_resp.text
    case_id = create_resp.json()["id"]

    update_resp = client.put(
        f"/api/v1/cases/{case_id}",
        headers=auth_headers,
        json={
            "applicant_kind": "ENTITY",
            "applicants": _first_applicant_payload(individual_applicant_id, name_cn="自然人申请人"),
        },
    )

    payload = _assert_error(update_resp, 400, "CASE_APPLICANT_KIND_MISMATCH")
    details = payload["error"]["details"]
    assert details["applicant_kind"] == "ENTITY"
    assert details["first_applicant_type"] == "INDIVIDUAL"
    assert details["first_applicant_id"] == individual_applicant_id
