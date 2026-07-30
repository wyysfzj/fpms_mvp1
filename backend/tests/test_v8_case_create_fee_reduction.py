from __future__ import annotations

import hashlib
import json
import unittest
from datetime import date, datetime
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import patch
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.api import deps as api_deps
from app.core.errors import BusinessError
from app.modules.cases.models import Case
from app.modules.cases.schemas import CaseApplicantIn, CaseCreate
from app.modules.cases.service import _canonical_create_fee_reduction
from app.modules.documents.evidence_contracts import EvidenceReviewState, EvidenceVersionState
from app.modules.documents.models import DocAttachment, Document, DocumentEvidenceVersion
from app.modules.fees.fee_reduction import (
    FeeReductionApprovalScopeType,
    FeeReductionValidationResult,
)
from app.modules.fees.models import FeeReductionApproval
from app.modules.masterdata.applicants.models import Applicant


class _ApprovalQuery:
    def __init__(self, rows: list[SimpleNamespace]) -> None:
        self._rows = rows

    def filter(self, *_conditions: object) -> _ApprovalQuery:
        return self

    def order_by(self, *_columns: object) -> _ApprovalQuery:
        return self

    def all(self) -> list[SimpleNamespace]:
        return self._rows


class _Transaction:
    def __init__(
        self,
        approvals: list[SimpleNamespace] | None = None,
        evidence: SimpleNamespace | dict[str, SimpleNamespace] | None = None,
    ) -> None:
        self.approvals = approvals or []
        self.evidence = evidence
        self.query_count = 0

    def query(self, _model: object) -> _ApprovalQuery:
        self.query_count += 1
        return _ApprovalQuery(self.approvals)

    def get(self, _model: object, _identity: str) -> SimpleNamespace | None:
        if isinstance(self.evidence, dict):
            return self.evidence.get(_identity)
        return self.evidence


def _applicant(applicant_id: str) -> CaseApplicantIn:
    return CaseApplicantIn(
        seq=1,
        is_first=True,
        applicant_id=applicant_id,
        name_cn="申请人",
    )


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


def _approval(
    *,
    approval_id: str = "approval-1",
    applicant_ids: tuple[str, ...] = ("applicant-1",),
    ratio: Decimal = Decimal("0.8500"),
    fee_codes: tuple[str, ...] = ("CASE_CREATE",),
    source_evidence_version_id: str = "evidence-1",
) -> SimpleNamespace:
    eligibility_snapshot = _canonical_json(
        {
            "applicants": [
                {"applicant_id": applicant_id, "attributes": {}}
                for applicant_id in sorted(applicant_ids)
            ],
            "attributes_version": "v1",
            "schema": "FPMS_FEE_REDUCTION_ELIGIBILITY_V1",
        }
    )
    eligibility_hash = _digest(eligibility_snapshot)
    applicant_set_key = _digest(
        _canonical_json(
            {
                "applicant_ids": sorted(applicant_ids),
                "eligibility_snapshot_hash": eligibility_hash,
                "schema": "FPMS_FEE_REDUCTION_APPLICANT_SET_V1",
            }
        )
    )
    fee_scope_snapshot = _canonical_json(
        {
            "fee_codes": sorted(fee_codes),
            "schema": "FPMS_FEE_REDUCTION_FEE_SCOPE_V1",
        }
    )
    return SimpleNamespace(
        id=approval_id,
        scope_type="APPLICANT_SET",
        case_id=None,
        applicant_set_key=applicant_set_key,
        reduction_ratio=ratio,
        fee_scope_snapshot=fee_scope_snapshot,
        fee_scope_hash=_digest(fee_scope_snapshot),
        fee_year_from=None,
        fee_year_to=None,
        effective_from=date(2020, 1, 1),
        effective_to=date(2100, 1, 1),
        source_evidence_version_id=source_evidence_version_id,
        confirmation_status="CONFIRMED",
        confirmed_at=datetime(2026, 1, 1),
        confirmed_by="reviewer-1",
        eligibility_snapshot=eligibility_snapshot,
        eligibility_snapshot_hash=eligibility_hash,
        approval_identity_key="approval-identity-1",
    )


def _current_source() -> SimpleNamespace:
    return SimpleNamespace(
        case_id="source-case",
        lineage_key="eligibility",
        state=EvidenceVersionState.FINAL.value,
        review_state=EvidenceReviewState.APPROVED.value,
        creator_id="creator-1",
        reviewer_id="reviewer-1",
        reviewed_at=datetime(2026, 1, 1),
        current_identity_key="source-case|eligibility",
    )


class CaseCreateFeeReductionSchemaTests(unittest.TestCase):
    def test_missing_or_ambiguous_reduction_is_rejected(self) -> None:
        for value in (None, "", "NONE", "PARTIAL", "FULL", "0.0", 0, 0.7):
            with self.subTest(value=value), self.assertRaises(ValidationError):
                CaseCreate(case_no="CASE-1", fee_reduction=value)

        with self.assertRaises(ValidationError):
            CaseCreate(case_no="CASE-1")

    def test_only_exact_canonical_reduction_selections_are_accepted(self) -> None:
        for value in ("0", "0.7", "0.85"):
            with self.subTest(value=value):
                payload = CaseCreate(case_no="CASE-1", fee_reduction=value)
                self.assertEqual(payload.fee_reduction, value)


class CaseCreateFeeReductionServiceTests(unittest.TestCase):
    def test_explicit_no_reduction_is_canonical_and_never_queries_approval(self) -> None:
        transaction = _Transaction()

        result = _canonical_create_fee_reduction(
            transaction,
            reduction_value="0",
            applicants=[_applicant("applicant-1")],
            case_id="new-case-1",
        )

        self.assertEqual(result, "0")
        self.assertEqual(transaction.query_count, 0)

    def test_reduced_ratio_without_matching_applicant_approval_is_409(self) -> None:
        transaction = _Transaction(approvals=[_approval(applicant_ids=("someone-else",))])

        with self.assertRaises(BusinessError) as raised:
            _canonical_create_fee_reduction(
                transaction,
                reduction_value="0.85",
                applicants=[_applicant("applicant-1")],
                case_id="new-case-1",
            )

        self.assertEqual(raised.exception.status_code, 409)
        self.assertEqual(raised.exception.code, "FEE_REDUCTION_APPROVAL_REQUIRED")

    def test_matching_applicant_approval_is_delegated_to_validator(self) -> None:
        transaction = _Transaction(
            approvals=[_approval()],
            evidence=_current_source(),
        )
        validator_result = FeeReductionValidationResult(
            reduction_ratio=Decimal("0.8500"),
            payable_ratio=Decimal("0.1500"),
            provenance=object(),
            approval_id="approval-1",
            source_evidence_version_id="evidence-1",
            scope_type=FeeReductionApprovalScopeType.APPLICANT_SET,
        )

        with patch(
            "app.modules.cases.service.validate_fee_reduction",
            return_value=validator_result,
        ) as validator:
            result = _canonical_create_fee_reduction(
                transaction,
                reduction_value="0.85",
                applicants=[_applicant("applicant-1")],
                case_id="new-case-1",
            )

        self.assertEqual(result, "0.85")
        validator.assert_called_once()
        reduction_input = validator.call_args.kwargs["reduction_input"]
        context = validator.call_args.kwargs["context"]
        approval = validator.call_args.kwargs["approval"]
        self.assertEqual(reduction_input.reduction_ratio, Decimal("0.85"))
        self.assertEqual(context.case_id, "new-case-1")
        self.assertEqual(context.fee_code, "CASE_CREATE")
        self.assertEqual(context.applicant_set_key, approval.applicant_set_key)
        self.assertEqual(approval.scope_type, FeeReductionApprovalScopeType.APPLICANT_SET)
        self.assertEqual(approval.applicant_set_key, context.applicant_set_key)

    def test_matching_current_applicant_approval_allows_reduced_ratio(self) -> None:
        transaction = _Transaction(
            approvals=[_approval()],
            evidence=_current_source(),
        )

        result = _canonical_create_fee_reduction(
            transaction,
            reduction_value="0.85",
            applicants=[_applicant("applicant-1")],
            case_id="new-case-1",
        )

        self.assertEqual(result, "0.85")

    def test_multiple_valid_approvals_are_rejected_order_independently(self) -> None:
        for ratio in ("0.7", "0.85"):
            first = _approval(
                approval_id="approval-first",
                ratio=Decimal(ratio),
                source_evidence_version_id="evidence-first",
            )
            second = _approval(
                approval_id="approval-second",
                ratio=Decimal(ratio),
                source_evidence_version_id="evidence-second",
            )
            evidence = {
                "evidence-first": _current_source(),
                "evidence-second": _current_source(),
            }
            for approvals in ([first, second], [second, first]):
                with self.subTest(ratio=ratio, first_row=approvals[0].id):
                    transaction = _Transaction(
                        approvals=approvals,
                        evidence=evidence,
                    )

                    with self.assertRaises(BusinessError) as raised:
                        _canonical_create_fee_reduction(
                            transaction,
                            reduction_value=ratio,
                            applicants=[_applicant("applicant-1")],
                            case_id="new-case-1",
                        )

                    self.assertEqual(raised.exception.status_code, 409)
                    self.assertEqual(
                        raised.exception.code,
                        "FEE_REDUCTION_AMBIGUOUS_PROVENANCE",
                    )
                    self.assertEqual(
                        raised.exception.details,
                        {
                            "scope_type": "APPLICANT_SET",
                            "fee_code": "CASE_CREATE",
                        },
                    )

    def test_one_valid_and_one_stale_approval_is_not_ambiguous(self) -> None:
        for ratio in ("0.7", "0.85"):
            valid = _approval(
                approval_id="approval-valid",
                ratio=Decimal(ratio),
                source_evidence_version_id="evidence-valid",
            )
            stale = _approval(
                approval_id="approval-stale",
                ratio=Decimal(ratio),
                source_evidence_version_id="evidence-stale",
            )
            stale_source = SimpleNamespace(
                **{
                    **vars(_current_source()),
                    "current_identity_key": "arbitrary-nonempty-marker",
                }
            )
            evidence = {
                "evidence-valid": _current_source(),
                "evidence-stale": stale_source,
            }
            for approvals in ([valid, stale], [stale, valid]):
                with self.subTest(ratio=ratio, first_row=approvals[0].id):
                    transaction = _Transaction(
                        approvals=approvals,
                        evidence=evidence,
                    )

                    result = _canonical_create_fee_reduction(
                        transaction,
                        reduction_value=ratio,
                        applicants=[_applicant("applicant-1")],
                        case_id="new-case-1",
                    )

                    self.assertEqual(result, ratio)

    def test_stale_matching_approval_is_409(self) -> None:
        transaction = _Transaction(
            approvals=[_approval()],
            evidence=SimpleNamespace(
                **{
                    **vars(_current_source()),
                    "current_identity_key": "arbitrary-nonempty-marker",
                }
            ),
        )

        with self.assertRaises(BusinessError) as raised:
            _canonical_create_fee_reduction(
                transaction,
                reduction_value="0.85",
                applicants=[_applicant("applicant-1")],
                case_id="new-case-1",
            )

        self.assertEqual(raised.exception.status_code, 409)
        self.assertEqual(raised.exception.code, "FEE_REDUCTION_APPROVAL_NOT_CURRENT")

    def test_approval_must_cover_case_create_and_match_fee_scope_hash(self) -> None:
        transaction = _Transaction(
            approvals=[_approval(fee_codes=("UNRELATED_FEE",))],
            evidence=_current_source(),
        )

        with self.assertRaises(BusinessError) as raised:
            _canonical_create_fee_reduction(
                transaction,
                reduction_value="0.85",
                applicants=[_applicant("applicant-1")],
                case_id="new-case-1",
            )

        self.assertEqual(raised.exception.status_code, 409)
        self.assertEqual(
            raised.exception.code,
            "FEE_REDUCTION_APPROVAL_FEE_SCOPE_MISMATCH",
        )

        corrupt = _approval()
        corrupt.fee_scope_hash = "0" * 64
        transaction = _Transaction(approvals=[corrupt], evidence=_current_source())
        with self.assertRaises(BusinessError) as corrupt_error:
            _canonical_create_fee_reduction(
                transaction,
                reduction_value="0.85",
                applicants=[_applicant("applicant-1")],
                case_id="new-case-1",
            )
        self.assertEqual(corrupt_error.exception.status_code, 409)
        self.assertEqual(corrupt_error.exception.code, "FEE_REDUCTION_APPROVAL_INVALID")

    def test_approval_applicant_set_key_is_recomputed_from_submitted_composition(self) -> None:
        corrupt = _approval()
        corrupt.applicant_set_key = "unrelated-key"
        transaction = _Transaction(approvals=[corrupt], evidence=_current_source())

        with self.assertRaises(BusinessError) as raised:
            _canonical_create_fee_reduction(
                transaction,
                reduction_value="0.85",
                applicants=[_applicant("applicant-1")],
                case_id="new-case-1",
            )

        self.assertEqual(raised.exception.status_code, 409)
        self.assertEqual(raised.exception.code, "FEE_REDUCTION_APPROVAL_REQUIRED")

    def test_reduced_ratio_requires_only_linked_applicant_ids(self) -> None:
        transaction = _Transaction(approvals=[_approval()])
        unlinked = CaseApplicantIn(seq=1, is_first=True, name_cn="未关联申请人")

        with self.assertRaises(BusinessError) as raised:
            _canonical_create_fee_reduction(
                transaction,
                reduction_value="0.85",
                applicants=[unlinked],
                case_id="new-case-1",
            )

        self.assertEqual(raised.exception.status_code, 409)
        self.assertEqual(raised.exception.code, "FEE_REDUCTION_APPROVAL_REQUIRED")


def _seed_applicants(session_factory, count: int) -> tuple[str, ...]:
    applicant_ids = tuple(str(uuid4()) for _ in range(count))
    with session_factory() as db:
        for applicant_id in applicant_ids:
            unique = uuid4().hex
            db.add(
                Applicant(
                    id=applicant_id,
                    code=f"V8-REDUCTION-{unique}",
                    name_cn=f"费减申请人-{unique}",
                    applicant_type="INDIVIDUAL" if count == 1 else "ENTITY",
                    is_active=True,
                )
            )
        db.commit()
    return applicant_ids


def _seed_approval_record(
    session_factory,
    *,
    applicant_ids: tuple[str, ...],
    ratio: str,
    current_identity_key: str | None = None,
) -> None:
    approval = _approval(
        applicant_ids=applicant_ids,
        ratio=Decimal(ratio).quantize(Decimal("0.0001")),
    )
    source_case_id = str(uuid4())
    document_id = str(uuid4())
    attachment_id = str(uuid4())
    evidence_id = str(uuid4())
    lineage_key = f"eligibility-{uuid4().hex}"
    with session_factory() as db:
        db.add(
            Case(
                id=source_case_id,
                case_no=f"SOURCE-{uuid4().hex}",
                fee_reduction="0",
            )
        )
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
                reviewed_at=datetime(2026, 7, 20, 9, 0),
                content_hash="sha256:" + "a" * 64,
                current_identity_key=(
                    current_identity_key
                    if current_identity_key is not None
                    else f"{source_case_id}|{lineage_key}"
                ),
            )
        )
        db.flush()
        db.add(
            FeeReductionApproval(
                id=str(uuid4()),
                scope_type=approval.scope_type,
                case_id=None,
                applicant_set_key=approval.applicant_set_key,
                reduction_ratio=approval.reduction_ratio,
                fee_scope_snapshot=approval.fee_scope_snapshot,
                fee_scope_hash=approval.fee_scope_hash,
                fee_year_from=None,
                fee_year_to=None,
                effective_from=date(2020, 1, 1),
                effective_to=date(2100, 1, 1),
                source_evidence_version_id=evidence_id,
                confirmation_status="CONFIRMED",
                confirmed_at=datetime(2026, 7, 20, 9, 0),
                confirmed_by="reviewer-1",
                eligibility_snapshot=approval.eligibility_snapshot,
                eligibility_snapshot_hash=approval.eligibility_snapshot_hash,
                approval_identity_key=_digest(f"approval-{uuid4().hex}"),
                created_by="reviewer-1",
                updated_by="reviewer-1",
            )
        )
        db.commit()


def _case_payload(
    *,
    case_no: str,
    applicant_ids: tuple[str, ...],
    fee_reduction: object,
) -> dict[str, object]:
    return {
        "case_no": case_no,
        "case_type": "NORMAL",
        "patent_category": "INV",
        "flow_dir": "CN_DOMESTIC",
        "fee_reduction": fee_reduction,
        "applicants": [
            {
                "seq": index,
                "is_first": index == 1,
                "applicant_id": applicant_id,
                "name_cn": f"费减申请人-{index}",
            }
            for index, applicant_id in enumerate(applicant_ids, start=1)
        ],
    }


def _assert_error_envelope(response, status_code: int, code: str) -> None:
    assert response.status_code == status_code, response.text
    assert response.json()["error"]["code"] == code
    assert response.json()["error"]["message"]


def test_case_post_preserves_401_and_403(
    client: TestClient,
    auth_headers: dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    payload = {"case_no": f"AUTH-{uuid4().hex}", "fee_reduction": "0"}
    unauthenticated = client.post("/api/v1/cases", json=payload)
    _assert_error_envelope(unauthenticated, 401, "AUTH_REQUIRED")

    monkeypatch.setattr(api_deps, "get_user_permissions", lambda _db, _user_id: set())
    forbidden = client.post("/api/v1/cases", headers=auth_headers, json=payload)
    _assert_error_envelope(forbidden, 403, "FORBIDDEN")
    assert forbidden.json()["error"]["details"]["required_perm"] == "Case.Create"


@pytest.mark.parametrize("value", [None, "", "NONE", "PARTIAL", "FULL", "0.0", 0, 0.7])
def test_case_post_rejects_ambiguous_reduction_with_422_envelope(
    client: TestClient,
    auth_headers: dict[str, str],
    value: object,
) -> None:
    response = client.post(
        "/api/v1/cases",
        headers=auth_headers,
        json={"case_no": f"AMBIG-{uuid4().hex}", "fee_reduction": value},
    )
    _assert_error_envelope(response, 422, "VALIDATION_ERROR")


def test_case_post_rejects_missing_reduction_with_422_envelope(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    response = client.post(
        "/api/v1/cases",
        headers=auth_headers,
        json={"case_no": f"MISSING-{uuid4().hex}"},
    )
    _assert_error_envelope(response, 422, "VALIDATION_ERROR")


def test_case_post_rejects_mismatched_applicant_approval_with_409_envelope(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory,
) -> None:
    requested_id, approved_id = _seed_applicants(session_factory, 2)
    _seed_approval_record(
        session_factory,
        applicant_ids=(approved_id,),
        ratio="0.85",
    )
    response = client.post(
        "/api/v1/cases",
        headers=auth_headers,
        json=_case_payload(
            case_no=f"MISMATCH-{uuid4().hex}",
            applicant_ids=(requested_id,),
            fee_reduction="0.85",
        ),
    )
    _assert_error_envelope(response, 409, "FEE_REDUCTION_APPROVAL_REQUIRED")


def test_case_post_rejects_internally_inconsistent_source_with_409_envelope(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory,
) -> None:
    applicant_ids = _seed_applicants(session_factory, 1)
    _seed_approval_record(
        session_factory,
        applicant_ids=applicant_ids,
        ratio="0.85",
        current_identity_key="arbitrary-nonempty-marker",
    )
    response = client.post(
        "/api/v1/cases",
        headers=auth_headers,
        json=_case_payload(
            case_no=f"STALE-{uuid4().hex}",
            applicant_ids=applicant_ids,
            fee_reduction="0.85",
        ),
    )
    _assert_error_envelope(response, 409, "FEE_REDUCTION_APPROVAL_NOT_CURRENT")


@pytest.mark.parametrize(
    ("ratio", "applicant_count"),
    (("0", 1), ("0.7", 2), ("0.85", 1)),
)
def test_case_post_persists_canonical_reduction(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory,
    ratio: str,
    applicant_count: int,
) -> None:
    applicant_ids = _seed_applicants(session_factory, applicant_count)
    if ratio != "0":
        _seed_approval_record(
            session_factory,
            applicant_ids=applicant_ids,
            ratio=ratio,
        )
    case_no = f"CANONICAL-{ratio}-{uuid4().hex}"
    response = client.post(
        "/api/v1/cases",
        headers=auth_headers,
        json=_case_payload(
            case_no=case_no,
            applicant_ids=applicant_ids,
            fee_reduction=ratio,
        ),
    )

    assert response.status_code == 201, response.text
    assert response.json()["fee_reduction"] == ratio
    with session_factory() as db:
        persisted = db.query(Case).filter(Case.case_no == case_no).one()
        assert persisted.fee_reduction == ratio


if __name__ == "__main__":
    unittest.main()
