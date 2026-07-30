from __future__ import annotations

import hashlib
import json
from contextlib import contextmanager
from datetime import date, datetime, timezone
from decimal import Decimal
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlalchemy import event

from app.api import deps as api_deps
from app.modules.auth.models import T_User
from app.modules.cases.models import Case, T_CaseApplicant
from app.modules.cases.schemas import CaseUpdateFull
from app.modules.documents.evidence_contracts import EvidenceReviewState, EvidenceVersionState
from app.modules.documents.models import DocAttachment, Document, DocumentEvidenceVersion
from app.modules.fees.models import FeeReductionApproval
from app.modules.masterdata.applicants.models import Applicant


def _canonical_json(value: object) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def _digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _seed_applicants(session_factory, count: int) -> tuple[str, ...]:
    applicant_ids = tuple(str(uuid4()) for _ in range(count))
    with session_factory() as db:
        for applicant_id in applicant_ids:
            unique = uuid4().hex
            db.add(
                Applicant(
                    id=applicant_id,
                    code=f"V8-UPDATE-{unique}",
                    name_cn=f"更新费减申请人-{unique}",
                    applicant_type="INDIVIDUAL" if count == 1 else "ENTITY",
                    is_active=True,
                )
            )
        db.commit()
    return applicant_ids


def _seed_case(
    session_factory,
    *,
    fee_reduction: str | None,
    applicant_ids: tuple[str, ...] = (),
) -> str:
    case_id = str(uuid4())
    initial_time = datetime(2020, 1, 1, tzinfo=timezone.utc)
    with session_factory() as db:
        db.add(
            Case(
                id=case_id,
                case_no=f"UPDATE-{uuid4().hex}",
                title_cn="原始标题",
                fee_reduction=fee_reduction,
                created_at=initial_time,
                updated_at=initial_time,
                created_by="creator-1",
                updated_by="creator-1",
            )
        )
        db.flush()
        for index, applicant_id in enumerate(applicant_ids, start=1):
            db.add(
                T_CaseApplicant(
                    id=str(uuid4()),
                    case_id=case_id,
                    applicant_id=applicant_id,
                    seq=index,
                    is_first=index == 1,
                    name_cn=f"更新费减申请人-{index}",
                )
            )
        db.commit()
    return case_id


def _approval_carriers(
    *,
    applicant_ids: tuple[str, ...],
    ratio: str,
) -> dict[str, object]:
    sorted_ids = sorted(applicant_ids)
    eligibility_snapshot = _canonical_json(
        {
            "applicants": [
                {"applicant_id": applicant_id, "attributes": {}}
                for applicant_id in sorted_ids
            ],
            "attributes_version": "v1",
            "schema": "FPMS_FEE_REDUCTION_ELIGIBILITY_V1",
        }
    )
    eligibility_hash = _digest(eligibility_snapshot)
    applicant_set_key = _digest(
        _canonical_json(
            {
                "applicant_ids": sorted_ids,
                "eligibility_snapshot_hash": eligibility_hash,
                "schema": "FPMS_FEE_REDUCTION_APPLICANT_SET_V1",
            }
        )
    )
    fee_scope_snapshot = _canonical_json(
        {
            "fee_codes": ["CASE_CREATE"],
            "schema": "FPMS_FEE_REDUCTION_FEE_SCOPE_V1",
        }
    )
    return {
        "applicant_set_key": applicant_set_key,
        "reduction_ratio": Decimal(ratio).quantize(Decimal("0.0001")),
        "fee_scope_snapshot": fee_scope_snapshot,
        "fee_scope_hash": _digest(fee_scope_snapshot),
        "eligibility_snapshot": eligibility_snapshot,
        "eligibility_snapshot_hash": eligibility_hash,
    }


def _seed_approval(
    session_factory,
    *,
    applicant_ids: tuple[str, ...],
    ratio: str,
    approval_id: str | None = None,
) -> None:
    carriers = _approval_carriers(applicant_ids=applicant_ids, ratio=ratio)
    source_case_id = str(uuid4())
    document_id = str(uuid4())
    attachment_id = str(uuid4())
    evidence_id = str(uuid4())
    lineage_key = f"eligibility-{uuid4().hex}"
    with session_factory() as db:
        db.add(Case(id=source_case_id, case_no=f"SOURCE-{uuid4().hex}", fee_reduction="0"))
        db.flush()
        db.add(
            Document(
                id=document_id,
                case_id=source_case_id,
                direction="IN",
                title="费减资格来源",
            )
        )
        db.flush()
        db.add(
            DocAttachment(
                id=attachment_id,
                document_id=document_id,
                file_name="eligibility.pdf",
                file_path="/test/eligibility.pdf",
            )
        )
        db.flush()
        db.add(
            DocumentEvidenceVersion(
                id=evidence_id,
                case_id=source_case_id,
                document_id=document_id,
                attachment_id=attachment_id,
                lineage_key=lineage_key,
                role="RAW_ATTACHMENT",
                version_number=1,
                state=EvidenceVersionState.FINAL.value,
                creator_id="creator-1",
                review_state=EvidenceReviewState.APPROVED.value,
                reviewer_id="reviewer-1",
                reviewed_at=datetime(2026, 7, 21, 9, 0),
                content_hash="sha256:" + "a" * 64,
                current_identity_key=f"{source_case_id}|{lineage_key}",
            )
        )
        db.flush()
        db.add(
            FeeReductionApproval(
                id=approval_id or str(uuid4()),
                scope_type="APPLICANT_SET",
                case_id=None,
                applicant_set_key=carriers["applicant_set_key"],
                reduction_ratio=carriers["reduction_ratio"],
                fee_scope_snapshot=carriers["fee_scope_snapshot"],
                fee_scope_hash=carriers["fee_scope_hash"],
                fee_year_from=None,
                fee_year_to=None,
                effective_from=date(2020, 1, 1),
                effective_to=date(2100, 1, 1),
                source_evidence_version_id=evidence_id,
                confirmation_status="CONFIRMED",
                confirmed_at=datetime(2026, 7, 21, 9, 0),
                confirmed_by="reviewer-1",
                eligibility_snapshot=carriers["eligibility_snapshot"],
                eligibility_snapshot_hash=carriers["eligibility_snapshot_hash"],
                approval_identity_key=_digest(f"approval-{uuid4().hex}"),
                created_by="reviewer-1",
                updated_by="reviewer-1",
            )
        )
        db.commit()


def _applicant_payload(applicant_ids: tuple[str, ...]) -> list[dict[str, object]]:
    return [
        {
            "seq": index,
            "is_first": index == 1,
            "applicant_id": applicant_id,
            "name_cn": f"更新费减申请人-{index}",
        }
        for index, applicant_id in enumerate(applicant_ids, start=1)
    ]


def _assert_error(response, status_code: int, code: str) -> None:
    assert response.status_code == status_code, response.text
    assert response.json()["error"]["code"] == code


@contextmanager
def _track_approval_selects(engine):
    statements: list[str] = []

    def before_cursor_execute(
        _connection,
        _cursor,
        statement: str,
        _parameters,
        _context,
        _executemany,
    ) -> None:
        normalized = statement.upper()
        if "SELECT" in normalized and "T_FEE_REDUCTION_APPROVAL" in normalized:
            statements.append(statement)

    event.listen(engine, "before_cursor_execute", before_cursor_execute)
    try:
        yield statements
    finally:
        event.remove(engine, "before_cursor_execute", before_cursor_execute)


def test_update_schema_distinguishes_absent_from_exact_canonical_replacement() -> None:
    class StringSubclass(str):
        pass

    absent = CaseUpdateFull(title_cn="无关更新")
    assert "fee_reduction" not in absent.model_fields_set

    for value in ("0", "0.7", "0.85"):
        payload = CaseUpdateFull(fee_reduction=value)
        assert payload.fee_reduction == value
        assert "fee_reduction" in payload.model_fields_set

    for value in (
        True,
        False,
        0,
        0.7,
        None,
        "",
        "NONE",
        "PARTIAL",
        "FULL",
        "0.0",
        " 0",
        "0.7 ",
        StringSubclass("0.85"),
    ):
        with pytest.raises(ValidationError):
            CaseUpdateFull(fee_reduction=value)


def test_put_preserves_existing_auth_permission_and_not_found_semantics(
    client: TestClient,
    auth_headers: dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    case_id = str(uuid4())
    unauthenticated = client.put(f"/api/v1/cases/{case_id}", json={"fee_reduction": "0"})
    _assert_error(unauthenticated, 401, "AUTH_REQUIRED")

    monkeypatch.setattr(api_deps, "get_user_permissions", lambda _db, _user_id: set())
    forbidden = client.put(
        f"/api/v1/cases/{case_id}",
        headers=auth_headers,
        json={"fee_reduction": "0"},
    )
    _assert_error(forbidden, 403, "FORBIDDEN")
    assert forbidden.json()["error"]["details"]["required_perm"] == "Case.Edit"

    monkeypatch.undo()
    missing = client.put(
        f"/api/v1/cases/{case_id}",
        headers=auth_headers,
        json={"fee_reduction": "0"},
    )
    _assert_error(missing, 404, "CASE_NOT_FOUND")


@pytest.mark.parametrize(
    "value",
    [True, False, 0, 0.7, None, "", "NONE", "PARTIAL", "FULL", "0.0", " 0", "0.85 "],
)
def test_present_noncanonical_wire_value_is_422_without_mutation(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory,
    value: object,
) -> None:
    case_id = _seed_case(session_factory, fee_reduction="LEGACY_UNKNOWN")

    response = client.put(
        f"/api/v1/cases/{case_id}",
        headers=auth_headers,
        json={"title_cn": "不应写入", "fee_reduction": value},
    )

    _assert_error(response, 422, "VALIDATION_ERROR")
    with session_factory() as db:
        case = db.get(Case, case_id)
        assert case.title_cn == "原始标题"
        assert case.fee_reduction == "LEGACY_UNKNOWN"


@pytest.mark.parametrize("stored", [None, "LEGACY_UNKNOWN", "NONE"])
def test_unrelated_partial_put_preserves_stored_value_and_skips_approval_query(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory,
    engine,
    stored: str | None,
) -> None:
    case_id = _seed_case(session_factory, fee_reduction=stored)

    with _track_approval_selects(engine) as approval_selects:
        response = client.put(
            f"/api/v1/cases/{case_id}",
            headers=auth_headers,
            json={"title_cn": "无关字段已更新"},
        )

    assert response.status_code == 200, response.text
    assert response.json()["fee_reduction"] == stored
    assert approval_selects == []
    with session_factory() as db:
        case = db.get(Case, case_id)
        assert case.fee_reduction == stored
        assert case.title_cn == "无关字段已更新"


def test_changed_applicants_require_explicit_selection_before_any_write(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory,
) -> None:
    original_ids = _seed_applicants(session_factory, 1)
    replacement_ids = _seed_applicants(session_factory, 1)
    case_id = _seed_case(
        session_factory,
        fee_reduction="0.85",
        applicant_ids=original_ids,
    )

    response = client.put(
        f"/api/v1/cases/{case_id}",
        headers=auth_headers,
        json={
            "title_cn": "不应写入",
            "status": "PENDING",
            "app_no": "CN-UNCHANGED-ON-ERROR",
            "filing_date": "2026-07-21",
            "applicants": _applicant_payload(replacement_ids),
        },
    )

    _assert_error(response, 409, "FEE_REDUCTION_EXPLICIT_SELECTION_REQUIRED")
    assert response.json()["error"]["details"] == {
        "case_id": case_id,
        "field": "fee_reduction",
    }
    with session_factory() as db:
        case = db.get(Case, case_id)
        persisted_ids = tuple(
            row.applicant_id
            for row in db.query(T_CaseApplicant)
            .filter(T_CaseApplicant.case_id == case_id)
            .order_by(T_CaseApplicant.seq)
            .all()
        )
        assert case.title_cn == "原始标题"
        assert case.status == "NOT_FILED"
        assert case.app_no is None
        assert case.filing_date is None
        assert case.fee_reduction == "0.85"
        assert persisted_ids == original_ids


def test_explicit_zero_with_changed_applicants_skips_approval_and_updates_audit(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory,
    engine,
) -> None:
    original_ids = _seed_applicants(session_factory, 1)
    replacement_ids = _seed_applicants(session_factory, 2)
    case_id = _seed_case(
        session_factory,
        fee_reduction="LEGACY_UNKNOWN",
        applicant_ids=original_ids,
    )
    with session_factory() as db:
        admin_id = db.query(T_User.id).filter(T_User.username == "admin").scalar()
        previous_updated_at = db.get(Case, case_id).updated_at

    with _track_approval_selects(engine) as approval_selects:
        response = client.put(
            f"/api/v1/cases/{case_id}",
            headers=auth_headers,
            json={
                "fee_reduction": "0",
                "applicants": _applicant_payload(replacement_ids),
            },
        )

    assert response.status_code == 200, response.text
    assert response.json()["fee_reduction"] == "0"
    assert approval_selects == []
    with session_factory() as db:
        case = db.get(Case, case_id)
        assert case.fee_reduction == "0"
        assert case.updated_by == admin_id
        assert case.updated_at > previous_updated_at


@pytest.mark.parametrize("ratio", ["0.7", "0.85"])
def test_reduced_ratio_uses_current_persisted_applicant_composition(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory,
    ratio: str,
) -> None:
    applicant_ids = _seed_applicants(session_factory, 2)
    case_id = _seed_case(
        session_factory,
        fee_reduction="0",
        applicant_ids=applicant_ids,
    )
    _seed_approval(session_factory, applicant_ids=applicant_ids, ratio=ratio)

    response = client.put(
        f"/api/v1/cases/{case_id}",
        headers=auth_headers,
        json={"fee_reduction": ratio},
    )

    assert response.status_code == 200, response.text
    assert response.json()["fee_reduction"] == ratio
    with session_factory() as db:
        assert db.get(Case, case_id).fee_reduction == ratio


def test_reduced_ratio_uses_submitted_composition_and_validates_before_writes(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory,
) -> None:
    original_ids = _seed_applicants(session_factory, 1)
    requested_ids = _seed_applicants(session_factory, 1)
    other_ids = _seed_applicants(session_factory, 1)
    case_id = _seed_case(
        session_factory,
        fee_reduction="0",
        applicant_ids=original_ids,
    )
    _seed_approval(session_factory, applicant_ids=other_ids, ratio="0.85")

    rejected = client.put(
        f"/api/v1/cases/{case_id}",
        headers=auth_headers,
        json={
            "title_cn": "不应写入",
            "status": "PENDING",
            "app_no": "CN-UNCHANGED-ON-ERROR",
            "filing_date": "2026-07-21",
            "fee_reduction": "0.85",
            "applicants": _applicant_payload(requested_ids),
        },
    )
    _assert_error(rejected, 409, "FEE_REDUCTION_APPROVAL_REQUIRED")
    with session_factory() as db:
        case = db.get(Case, case_id)
        assert case.title_cn == "原始标题"
        assert case.status == "NOT_FILED"
        assert case.app_no is None
        assert case.filing_date is None
        assert case.fee_reduction == "0"
        assert tuple(
            row.applicant_id
            for row in db.query(T_CaseApplicant)
            .filter(T_CaseApplicant.case_id == case_id)
            .order_by(T_CaseApplicant.seq)
            .all()
        ) == original_ids

    _seed_approval(session_factory, applicant_ids=requested_ids, ratio="0.85")
    accepted = client.put(
        f"/api/v1/cases/{case_id}",
        headers=auth_headers,
        json={
            "fee_reduction": "0.85",
            "applicants": _applicant_payload(requested_ids),
        },
    )
    assert accepted.status_code == 200, accepted.text
    assert accepted.json()["fee_reduction"] == "0.85"


def test_multiple_valid_approvals_are_ambiguous_with_exact_details(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory,
) -> None:
    applicant_ids = _seed_applicants(session_factory, 1)
    case_id = _seed_case(
        session_factory,
        fee_reduction="0",
        applicant_ids=applicant_ids,
    )
    _seed_approval(
        session_factory,
        applicant_ids=applicant_ids,
        ratio="0.85",
        approval_id="approval-z",
    )
    _seed_approval(
        session_factory,
        applicant_ids=applicant_ids,
        ratio="0.85",
        approval_id="approval-a",
    )

    response = client.put(
        f"/api/v1/cases/{case_id}",
        headers=auth_headers,
        json={"fee_reduction": "0.85"},
    )

    _assert_error(response, 409, "FEE_REDUCTION_AMBIGUOUS_PROVENANCE")
    assert response.json()["error"]["details"] == {
        "scope_type": "APPLICANT_SET",
        "fee_code": "CASE_CREATE",
    }
    with session_factory() as db:
        assert db.get(Case, case_id).fee_reduction == "0"


@pytest.mark.parametrize("composition", [(), (None,), ("duplicate", "duplicate")])
def test_nonexact_current_composition_cannot_match_reduced_approval(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory,
    composition: tuple[str | None, ...],
) -> None:
    linked_ids = _seed_applicants(session_factory, 1)
    case_id = _seed_case(session_factory, fee_reduction="0")
    with session_factory() as db:
        for index, marker in enumerate(composition, start=1):
            applicant_id = linked_ids[0] if marker == "duplicate" else marker
            db.add(
                T_CaseApplicant(
                    id=str(uuid4()),
                    case_id=case_id,
                    applicant_id=applicant_id,
                    seq=index,
                    is_first=index == 1,
                    name_cn=f"异常申请人-{index}",
                )
            )
        db.commit()
    _seed_approval(session_factory, applicant_ids=linked_ids, ratio="0.85")

    response = client.put(
        f"/api/v1/cases/{case_id}",
        headers=auth_headers,
        json={"fee_reduction": "0.85"},
    )

    _assert_error(response, 409, "FEE_REDUCTION_APPROVAL_REQUIRED")
    with session_factory() as db:
        assert db.get(Case, case_id).fee_reduction == "0"
