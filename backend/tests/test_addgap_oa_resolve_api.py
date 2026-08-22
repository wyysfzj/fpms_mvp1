from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from app.modules.cases.models import Case
from app.modules.documents.models import DocTemplate, Document
from app.modules.official_workflows.models import OfficialWorkPackage

PATH = "/api/v1/official-documents/{document_id}/official-work-packages/oa-reply/resolve"


def _create_source_document(
    session_factory: sessionmaker,
    *,
    case_status: str = "OA1",
    template_code: str = "OA_IN",
    direction: str = "IN",
) -> dict[str, str]:
    with session_factory() as db:
        case = Case(
            id=str(uuid4()),
            case_no=f"ADDGAP-OA-API-{uuid4().hex[:8].upper()}",
            case_type="NORMAL",
            patent_category="INV",
            flow_dir="CN_DOMESTIC",
            title_cn="OA 工作包解析 API 测试案件",
            status=case_status,
        )
        template = db.execute(
            select(DocTemplate).where(DocTemplate.code == template_code)
        ).scalar_one()
        source = Document(
            id=str(uuid4()),
            case_id=case.id,
            doc_template_id=template.id,
            doc_type="OFFICIAL_NOTICE",
            direction=direction,
            title="审查意见通知书",
            need_reply=bool(template.need_reply),
        )
        db.add_all([case, source])
        db.commit()
        return {"case_id": case.id, "document_id": source.id}


def _resolve(client: TestClient, headers: dict[str, str], *, document_id: str):
    return client.post(PATH.format(document_id=document_id), headers=headers)


def test_resolve_oa_package_creates_then_reuses_one_package(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    ids = _create_source_document(session_factory)

    created = _resolve(client, auth_headers, document_id=ids["document_id"])
    reused = _resolve(client, auth_headers, document_id=ids["document_id"])

    assert created.status_code == 200, created.text
    assert reused.status_code == 200, reused.text
    created_body = created.json()
    reused_body = reused.json()
    assert reused_body["package"]["id"] == created_body["package"]["id"]
    assert created_body["package"]["case_id"] == ids["case_id"]
    assert created_body["package"]["package_kind"] == "OA_REPLY"
    assert created_body["package"]["source_document_id"] == ids["document_id"]
    assert created_body["source_document"]["id"] == ids["document_id"]
    assert {item["official_file_role"] for item in created_body["oa_file_roles"]} == {
        "OA_STATEMENT_WORD",
        "OA_STATEMENT_PDF",
        "OA_MODIFIED_CLAIMS",
        "OA_AMENDMENT_COMPARISON",
        "OA_OTHER_PROOF",
        "OA_ADDITIONAL_FILE",
    }
    assert {item["item_code"] for item in created_body["official_page_checklist"]} == {
        "STATEMENT_TEXT_CONFIRMED",
        "PDF_FIDELITY_CONFIRMED",
        "MODIFIED_CLAIMS_CONFIRMED",
        "EXPERIMENT_DATA_FLAG_CONFIRMED",
        "PREVIEW_CONFIRMED",
        "SIGNATURE_CONFIRMED",
    }

    with session_factory() as db:
        packages = (
            db.execute(
                select(OfficialWorkPackage).where(
                    OfficialWorkPackage.source_document_id == ids["document_id"],
                    OfficialWorkPackage.package_kind == "OA_REPLY",
                )
            )
            .scalars()
            .all()
        )
        assert len(packages) == 1
        assert packages[0].resolve_key == f"OA_REPLY:{ids['document_id']}"


def test_resolve_oa_package_is_bodyless_in_openapi(client: TestClient) -> None:
    operation = client.get("/openapi.json").json()["paths"][PATH]["post"]

    assert "requestBody" not in operation
    response_schema = operation["responses"]["200"]["content"]["application/json"]["schema"]
    assert response_schema == {"$ref": "#/components/schemas/OaReplyPackageOut"}


def test_resolve_oa_package_returns_not_found_for_missing_document(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    response = _resolve(client, auth_headers, document_id=str(uuid4()))

    assert response.status_code == 404, response.text
    assert response.json()["error"]["code"] == "DOCUMENT_NOT_FOUND"


def test_resolve_oa_package_rejects_outgoing_source(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    ids = _create_source_document(session_factory, direction="OUT")

    response = _resolve(client, auth_headers, document_id=ids["document_id"])

    assert response.status_code == 400, response.text
    assert response.json()["error"]["code"] == "OA_REPLY_SOURCE_DIRECTION_INVALID"


def test_resolve_oa_package_rejects_reference_only_source(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    ids = _create_source_document(session_factory, template_code="CLIENT_IN")

    response = _resolve(client, auth_headers, document_id=ids["document_id"])

    assert response.status_code == 409, response.text
    assert response.json()["error"]["code"] == "OA_REPLY_SOURCE_SEMANTICS_INVALID"


def test_resolve_oa_package_rejects_wrong_case_state_without_writing(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    ids = _create_source_document(session_factory, case_status="SUB_EXAM")

    response = _resolve(client, auth_headers, document_id=ids["document_id"])

    assert response.status_code == 409, response.text
    assert response.json()["error"]["code"] == "OA_REPLY_CASE_STATE_INVALID"
    with session_factory() as db:
        assert (
            db.execute(
                select(OfficialWorkPackage).where(
                    OfficialWorkPackage.source_document_id == ids["document_id"],
                    OfficialWorkPackage.package_kind == "OA_REPLY",
                )
            )
            .scalars()
            .all()
            == []
        )


def test_resolve_oa_package_propagates_identity_conflict(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    ids = _create_source_document(session_factory)
    with session_factory() as db:
        db.add(
            OfficialWorkPackage(
                id=str(uuid4()),
                case_id=ids["case_id"],
                package_kind="OA_REPLY",
                status="PREPARING",
                source_document_id=ids["document_id"],
                resolve_key=None,
            )
        )
        db.commit()

    response = _resolve(client, auth_headers, document_id=ids["document_id"])

    assert response.status_code == 409, response.text
    assert response.json()["error"]["code"] == "OA_REPLY_IDENTITY_CONFLICT"


def test_resolve_oa_package_requires_update_permission(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
    monkeypatch,
) -> None:
    import app.api.deps as deps

    ids = _create_source_document(session_factory)
    monkeypatch.setattr(deps, "get_user_permissions", lambda _db, _user_id: set())

    response = _resolve(client, auth_headers, document_id=ids["document_id"])

    assert response.status_code == 403, response.text
    assert response.json()["error"]["details"]["required_perm"] == ("OfficialWorkflow.Update")


def test_resolve_oa_package_rejects_invalid_document_id_path(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    response = _resolve(client, auth_headers, document_id="not-a-uuid")

    assert response.status_code == 422, response.text
