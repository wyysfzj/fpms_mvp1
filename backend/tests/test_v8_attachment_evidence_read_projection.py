from __future__ import annotations

from datetime import datetime

import pytest
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.modules.cases.models import Case
from app.modules.documents.api import router as documents_router
from app.modules.documents.evidence_contracts import (
    EvidenceReviewState,
    EvidenceRole,
    EvidenceVersionState,
)
from app.modules.documents.models import (
    DocAttachment,
    Document,
    DocumentEvidenceVersion,
)


def _id(value: int) -> str:
    return f"00000000-0000-0000-0000-{value:012d}"


def _login_headers(client: TestClient) -> dict[str, str]:
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "admin123"},
    )
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def _add_document_with_attachment(
    session_factory: sessionmaker,
    *,
    second_document: bool = False,
) -> tuple[str, str, str, str | None]:
    case_id = _id(1)
    document_id = _id(2)
    attachment_id = _id(3)
    other_document_id = _id(4) if second_document else None
    with session_factory() as transaction:
        transaction.add(Case(id=case_id, case_no="V8-EVIDENCE-READ-1"))
        transaction.add(
            Document(
                id=document_id,
                case_id=case_id,
                direction="IN",
                title="证据读取投影",
            )
        )
        if other_document_id is not None:
            transaction.add(
                Document(
                    id=other_document_id,
                    case_id=case_id,
                    direction="IN",
                    title="隐藏错链文书",
                )
            )
        transaction.add(
            DocAttachment(
                id=attachment_id,
                document_id=document_id,
                file_name="current.docx",
                file_path="attachments/current.docx",
            )
        )
        transaction.commit()
    return case_id, document_id, attachment_id, other_document_id


def _current_evidence_version(
    *,
    case_id: str,
    document_id: str,
    attachment_id: str,
    **overrides: object,
) -> DocumentEvidenceVersion:
    lineage_key = f"attachment:{attachment_id}"
    values: dict[str, object] = {
        "id": _id(5),
        "case_id": case_id,
        "document_id": document_id,
        "attachment_id": attachment_id,
        "lineage_key": lineage_key,
        "role": EvidenceRole.OFFICIAL_FINAL_PDF.value,
        "version_number": 1,
        "state": EvidenceVersionState.FINAL.value,
        "creator_id": _id(6),
        "review_state": EvidenceReviewState.APPROVED.value,
        "reviewer_id": _id(7),
        "reviewed_at": datetime(2026, 7, 19, 14, 0),
        "final_submitted_at": datetime(2026, 7, 19, 14, 5),
        "content_hash": f"sha256:{'b' * 64}",
        "current_identity_key": f"{case_id}|{lineage_key}",
    }
    values.update(overrides)
    return DocumentEvidenceVersion(**values)


def _assert_current_evidence_invalid(response) -> None:
    assert response.status_code == 409, response.text
    error = response.json()["error"]
    assert error["code"] == "DOCUMENT_ATTACHMENT_CURRENT_EVIDENCE_INVALID"
    assert error["message"] == "当前附件证据版本数据无效"


def test_document_detail_get_is_bodyless() -> None:
    routes = [
        route
        for route in documents_router.routes
        if isinstance(route, APIRoute)
        and route.path == "/documents/{document_id}"
        and route.methods == {"GET"}
    ]

    assert len(routes) == 1
    assert routes[0].body_field is None


def test_document_detail_projects_only_current_attachment_evidence_facts(
    client: TestClient,
    session_factory: sessionmaker,
) -> None:
    case_id = _id(1)
    document_id = _id(2)
    current_attachment_id = _id(3)
    legacy_attachment_id = _id(4)
    current_version_id = _id(5)
    creator_id = _id(6)
    reviewer_id = _id(7)
    lineage_key = f"attachment:{current_attachment_id}"

    with session_factory() as transaction:
        transaction.add(Case(id=case_id, case_no="V8-EVIDENCE-READ-1"))
        transaction.add(
            Document(
                id=document_id,
                case_id=case_id,
                direction="IN",
                title="证据读取投影",
            )
        )
        transaction.add_all(
            (
                DocAttachment(
                    id=current_attachment_id,
                    document_id=document_id,
                    file_name="current.docx",
                    file_path="attachments/current.docx",
                ),
                DocAttachment(
                    id=legacy_attachment_id,
                    document_id=document_id,
                    file_name="legacy.pdf",
                    file_path="attachments/legacy.pdf",
                ),
            )
        )
        transaction.flush()
        transaction.add_all(
            (
                DocumentEvidenceVersion(
                    id=_id(8),
                    case_id=case_id,
                    document_id=document_id,
                    attachment_id=current_attachment_id,
                    lineage_key=lineage_key,
                    role=EvidenceRole.RAW_ATTACHMENT.value,
                    version_number=1,
                    state=EvidenceVersionState.DRAFT.value,
                    creator_id=_id(9),
                    review_state=EvidenceReviewState.PENDING.value,
                    content_hash=f"sha256:{'a' * 64}",
                    current_identity_key=None,
                ),
                DocumentEvidenceVersion(
                    id=current_version_id,
                    case_id=case_id,
                    document_id=document_id,
                    attachment_id=current_attachment_id,
                    lineage_key=lineage_key,
                    role=EvidenceRole.OFFICIAL_FINAL_PDF.value,
                    version_number=2,
                    state=EvidenceVersionState.FINAL.value,
                    creator_id=creator_id,
                    review_state=EvidenceReviewState.APPROVED.value,
                    reviewer_id=reviewer_id,
                    reviewed_at=datetime(2026, 7, 19, 14, 0),
                    final_submitted_at=datetime(2026, 7, 19, 14, 5),
                    content_hash=f"sha256:{'b' * 64}",
                    current_identity_key=f"{case_id}|{lineage_key}",
                ),
            )
        )
        transaction.commit()

    response = client.get(
        f"/api/v1/documents/{document_id}",
        headers=_login_headers(client),
    )

    assert response.status_code == 200, response.text
    attachments = {item["id"]: item for item in response.json()["attachments"]}
    assert {
        key: attachments[current_attachment_id][key]
        for key in (
            "evidence_version_id",
            "role",
            "creator_id",
            "reviewer_id",
            "review_state",
            "is_current",
            "is_final",
        )
    } == {
        "evidence_version_id": current_version_id,
        "role": EvidenceRole.OFFICIAL_FINAL_PDF.value,
        "creator_id": creator_id,
        "reviewer_id": reviewer_id,
        "review_state": EvidenceReviewState.APPROVED.value,
        "is_current": True,
        "is_final": True,
    }
    assert {
        key: attachments[legacy_attachment_id][key]
        for key in (
            "evidence_version_id",
            "role",
            "creator_id",
            "reviewer_id",
            "review_state",
        )
    } == {
        "evidence_version_id": None,
        "role": None,
        "creator_id": None,
        "reviewer_id": None,
        "review_state": None,
    }
    assert attachments[legacy_attachment_id]["is_current"] is False
    assert attachments[legacy_attachment_id]["is_final"] is False
    assert "readiness" not in attachments[current_attachment_id]


def test_document_detail_rejects_hidden_current_evidence_document_mismatch(
    client: TestClient,
    session_factory: sessionmaker,
) -> None:
    case_id, document_id, attachment_id, other_document_id = _add_document_with_attachment(
        session_factory,
        second_document=True,
    )
    assert other_document_id is not None
    with session_factory() as transaction:
        transaction.add(
            _current_evidence_version(
                case_id=case_id,
                document_id=other_document_id,
                attachment_id=attachment_id,
            )
        )
        transaction.commit()

    response = client.get(
        f"/api/v1/documents/{document_id}",
        headers=_login_headers(client),
    )

    _assert_current_evidence_invalid(response)


@pytest.mark.parametrize(
    "overrides",
    (
        pytest.param({"role": "UNKNOWN_ROLE"}, id="unknown-role"),
        pytest.param({"state": "UNKNOWN_STATE"}, id="unknown-state"),
        pytest.param(
            {"role": EvidenceRole.GENERATED_ATTACHMENT.value},
            id="generated-attachment-final",
        ),
        pytest.param({"creator_id": ""}, id="blank-creator"),
        pytest.param({"creator_id": "x" * 37}, id="overlong-creator"),
        pytest.param({"review_state": "UNKNOWN_REVIEW_STATE"}, id="unknown-review-state"),
        pytest.param(
            {
                "role": EvidenceRole.RAW_ATTACHMENT.value,
                "state": EvidenceVersionState.DRAFT.value,
                "review_state": EvidenceReviewState.PENDING.value,
                "reviewer_id": _id(7),
                "reviewed_at": datetime(2026, 7, 19, 14, 0),
                "final_submitted_at": None,
            },
            id="inconsistent-pending-review",
        ),
        pytest.param(
            {
                "reviewer_id": None,
                "reviewed_at": None,
            },
            id="incomplete-terminal-review",
        ),
        pytest.param({"reviewer_id": _id(6)}, id="creator-self-review"),
    ),
)
def test_document_detail_rejects_corrupt_current_evidence_carriers(
    client: TestClient,
    session_factory: sessionmaker,
    overrides: dict[str, object],
) -> None:
    case_id, document_id, attachment_id, _other_document_id = _add_document_with_attachment(
        session_factory
    )
    with session_factory() as transaction:
        transaction.add(
            _current_evidence_version(
                case_id=case_id,
                document_id=document_id,
                attachment_id=attachment_id,
                **overrides,
            )
        )
        transaction.commit()

    response = client.get(
        f"/api/v1/documents/{document_id}",
        headers=_login_headers(client),
    )

    _assert_current_evidence_invalid(response)
