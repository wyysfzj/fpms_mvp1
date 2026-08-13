from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from app.modules.cases.models import Case
from app.modules.official_workflows.models import OfficialWorkPackage

PATH = "/api/v1/cases/{case_id}/official-work-packages/filing-preparation/resolve"


def _create_case(session_factory: sessionmaker, *, status: str = "NOT_FILED") -> str:
    with session_factory() as db:
        case = Case(
            id=str(uuid4()),
            case_no=f"ADDGAP-RESOLVE-{uuid4().hex[:8].upper()}",
            case_type="NORMAL",
            patent_category="INV",
            flow_dir="CN_DOMESTIC",
            title_cn="新申请递交包解析 API 测试案件",
            status=status,
            business_stage="NEW_CASE",
            official_procedure_stage="NOT_SUBMITTED",
            legal_status="NOT_ESTABLISHED",
            lifecycle_revision=0,
            lifecycle_verification_status="CONFIRMED",
        )
        db.add(case)
        db.commit()
        return case.id


def _resolve(client: TestClient, headers: dict[str, str], *, case_id: str):
    return client.post(PATH.format(case_id=case_id), headers=headers)


def test_resolve_filing_package_creates_then_reuses_one_package(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    case_id = _create_case(session_factory)

    created = _resolve(client, auth_headers, case_id=case_id)
    reused = _resolve(client, auth_headers, case_id=case_id)

    assert created.status_code == 200, created.text
    assert reused.status_code == 200, reused.text
    created_body = created.json()
    reused_body = reused.json()
    assert reused_body["package"]["id"] == created_body["package"]["id"]
    assert created_body["package"]["case_id"] == case_id
    assert created_body["package"]["package_kind"] == "FILING_PREP"
    assert {item["official_file_role"] for item in created_body["filing_file_roles"]} == {
        "TECHNICAL_DISCLOSURE",
        "COMMISSION_INSTRUCTION",
        "FILING_XML_ZIP",
        "FILING_MERGED_PDF",
    }
    assert {item["item_code"] for item in created_body["official_page_checklist"]} == {
        "PREVIEW_CONFIRMED",
        "SIGNATURE_CONFIRMED",
    }

    with session_factory() as db:
        packages = (
            db.execute(
                select(OfficialWorkPackage).where(
                    OfficialWorkPackage.case_id == case_id,
                    OfficialWorkPackage.package_kind == "FILING_PREP",
                )
            )
            .scalars()
            .all()
        )
        assert len(packages) == 1
        assert packages[0].resolve_key == f"FILING_PREP:{case_id}"


def test_resolve_filing_package_is_bodyless_in_openapi(client: TestClient) -> None:
    operation = client.get("/openapi.json").json()["paths"][PATH]["post"]

    assert "requestBody" not in operation
    response_schema = operation["responses"]["200"]["content"]["application/json"]["schema"]
    assert response_schema == {"$ref": "#/components/schemas/FilingPreparationPackageOut"}


def test_resolve_filing_package_returns_not_found_for_missing_case(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    response = _resolve(client, auth_headers, case_id=str(uuid4()))

    assert response.status_code == 404, response.text
    assert response.json()["error"]["code"] == "CASE_NOT_FOUND"


def test_resolve_filing_package_rejects_invalid_creation_state_without_writing(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    case_id = _create_case(session_factory, status="ACCEPTED")

    response = _resolve(client, auth_headers, case_id=case_id)

    assert response.status_code == 409, response.text
    assert response.json()["error"]["code"] == "FILING_PREPARATION_CASE_STATE_INVALID"
    with session_factory() as db:
        assert (
            db.execute(
                select(OfficialWorkPackage).where(
                    OfficialWorkPackage.case_id == case_id,
                    OfficialWorkPackage.package_kind == "FILING_PREP",
                )
            )
            .scalars()
            .all()
            == []
        )


def test_resolve_filing_package_requires_update_permission(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
    monkeypatch,
) -> None:
    import app.api.deps as deps

    case_id = _create_case(session_factory)
    monkeypatch.setattr(deps, "get_user_permissions", lambda _db, _user_id: set())

    response = _resolve(client, auth_headers, case_id=case_id)

    assert response.status_code == 403, response.text
    assert response.json()["error"]["details"]["required_perm"] == "OfficialWorkflow.Update"


def test_resolve_filing_package_rejects_invalid_case_id_path(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    response = _resolve(client, auth_headers, case_id="not-a-uuid")

    assert response.status_code == 422, response.text
