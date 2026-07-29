from __future__ import annotations

import inspect
from contextlib import AbstractContextManager
from datetime import date, datetime
from decimal import Decimal
from hashlib import sha256
from types import SimpleNamespace
from typing import get_type_hints

import pytest
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.sql import Select

from app.api.deps import get_current_user
from app.core.errors import BusinessError
from app.db.session import get_db
from app.main import create_app
from app.modules.cases.models import Case
from app.modules.documents.models import DocAttachment, Document, DocumentEvidenceVersion
from app.modules.fees import api as fees_api
from app.modules.fees import fee_reduction_approval_schemas
from app.modules.fees.fee_reduction import FeeReductionApprovalScopeType
from app.modules.fees.models import FeeReductionApproval

PATH = "/api/v1/fees/cases/case-1/reduction-approvals"
ROUTER_PATH = "/fees/cases/{case_id}/reduction-approvals"
OUTPUT_FIELDS = (
    "approval_id",
    "scope_type",
    "case_id",
    "applicant_set_key",
    "reduction_ratio",
    "fee_codes",
    "fee_year_from",
    "fee_year_to",
    "effective_from",
    "effective_to",
    "source_evidence_version_id",
    "confirmation_status",
    "confirmed_at",
    "confirmed_by",
    "is_current",
)
FeeReductionApprovalListItemOut = getattr(
    fee_reduction_approval_schemas,
    "FeeReductionApprovalListItemOut",
    None,
)


class NoAutoflushSpy(AbstractContextManager[None]):
    def __init__(self, session: ApprovalListSessionSpy) -> None:
        self.session = session

    def __enter__(self) -> None:
        self.session.no_autoflush_enters += 1
        self.session.no_autoflush_depth += 1

    def __exit__(self, *_args: object) -> None:
        self.session.no_autoflush_depth -= 1
        self.session.no_autoflush_exits += 1


class MappingResult:
    def __init__(self, rows: list[dict[str, object]]) -> None:
        self.rows = rows

    def all(self) -> list[dict[str, object]]:
        return self.rows


class ExecuteResult:
    def __init__(self, rows: list[dict[str, object]]) -> None:
        self.rows = rows

    def mappings(self) -> MappingResult:
        return MappingResult(self.rows)


class ApprovalListSessionSpy:
    def __init__(
        self,
        rows: list[dict[str, object]] | None = None,
        *,
        case_exists: bool = True,
    ) -> None:
        self.rows = rows or []
        self.case_exists = case_exists
        self.get_calls: list[tuple[object, object]] = []
        self.get_inside_no_autoflush: list[bool] = []
        self.statements: list[Select[tuple[object, ...]]] = []
        self.no_autoflush_enters = 0
        self.no_autoflush_depth = 0
        self.no_autoflush_exits = 0

    @property
    def no_autoflush(self) -> NoAutoflushSpy:
        return NoAutoflushSpy(self)

    def get(self, model: object, key: object) -> object | None:
        self.get_calls.append((model, key))
        self.get_inside_no_autoflush.append(self.no_autoflush_depth > 0)
        if model is Case and self.case_exists:
            return SimpleNamespace(id=key)
        return None

    def execute(self, statement: Select[tuple[object, ...]]) -> ExecuteResult:
        self.statements.append(statement)
        return ExecuteResult(self.rows)

    def add(self, *_args: object, **_kwargs: object) -> None:
        raise AssertionError("approval list route called add")

    def flush(self, *_args: object, **_kwargs: object) -> None:
        raise AssertionError("approval list route called flush")

    def refresh(self, *_args: object, **_kwargs: object) -> None:
        raise AssertionError("approval list route called refresh")

    def expire(self, *_args: object, **_kwargs: object) -> None:
        raise AssertionError("approval list route called expire")

    def commit(self) -> None:
        raise AssertionError("approval list route called commit")

    def rollback(self) -> None:
        raise AssertionError("approval list route called rollback")


def _route() -> APIRoute:
    matches = [
        route
        for route in fees_api.router.routes
        if isinstance(route, APIRoute) and route.path == ROUTER_PATH and route.methods == {"GET"}
    ]
    assert len(matches) == 1
    return matches[0]


def _permission_dependency() -> object:
    dependency = next(item for item in _route().dependant.dependencies if item.name == "_perm")
    return dependency.call


def _row(
    approval_id: str,
    *,
    scope_type: str = "CASE",
    case_id: str | None = "case-1",
    applicant_set_key: str | None = None,
    reduction_ratio: Decimal = Decimal("0.8500"),
    fee_codes: tuple[str, ...] = ("ANNUITY", "APPLICATION"),
    fee_year_from: int | None = 1,
    fee_year_to: int | None = 3,
    effective_from: date = date(2026, 7, 1),
    effective_to: date | None = date(2027, 6, 30),
    source_evidence_version_id: str = "evidence-1",
    confirmed_at: datetime = datetime(2026, 7, 14, 9, 30),
    confirmed_by: str = "actor-1",
    evidence_case_id: str = "case-1",
    evidence_lineage_key: str = "fee-reduction",
    evidence_current_identity_key: str = "case-1|fee-reduction",
) -> dict[str, object]:
    fee_scope_snapshot = (
        '{"fee_codes":['
        + ",".join(f'"{fee_code}"' for fee_code in fee_codes)
        + '],"schema":"FPMS_FEE_REDUCTION_FEE_SCOPE_V1"}'
    )
    return {
        "approval_id": approval_id,
        "scope_type": scope_type,
        "case_id": case_id,
        "applicant_set_key": applicant_set_key,
        "reduction_ratio": reduction_ratio,
        "fee_scope_snapshot": fee_scope_snapshot,
        "fee_scope_hash": sha256(fee_scope_snapshot.encode("utf-8")).hexdigest(),
        "fee_year_from": fee_year_from,
        "fee_year_to": fee_year_to,
        "effective_from": effective_from,
        "effective_to": effective_to,
        "source_evidence_version_id": source_evidence_version_id,
        "confirmation_status": "CONFIRMED",
        "confirmed_at": confirmed_at,
        "confirmed_by": confirmed_by,
        "evidence_case_id": evidence_case_id,
        "evidence_lineage_key": evidence_lineage_key,
        "evidence_current_identity_key": evidence_current_identity_key,
        "is_current": True,
    }


def _client(
    session: ApprovalListSessionSpy,
    *,
    permission_error: BusinessError | None = None,
) -> TestClient:
    def permission() -> None:
        if permission_error is not None:
            raise permission_error

    app = create_app()
    app.dependency_overrides[get_db] = lambda: session
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(id="actor-1")
    app.dependency_overrides[_permission_dependency()] = permission
    return TestClient(app)


def test_list_item_schema_preserves_approval_facts_without_selecting_a_ratio() -> None:
    assert FeeReductionApprovalListItemOut is not None
    assert tuple(FeeReductionApprovalListItemOut.model_fields) == OUTPUT_FIELDS
    assert get_type_hints(FeeReductionApprovalListItemOut) == {
        "approval_id": str,
        "scope_type": FeeReductionApprovalScopeType,
        "case_id": str | None,
        "applicant_set_key": str | None,
        "reduction_ratio": Decimal,
        "fee_codes": tuple[str, ...],
        "fee_year_from": int | None,
        "fee_year_to": int | None,
        "effective_from": date,
        "effective_to": date | None,
        "source_evidence_version_id": str,
        "confirmation_status": str,
        "confirmed_at": datetime,
        "confirmed_by": str,
        "is_current": bool,
    }


def test_route_is_bodyless_get_with_case_path_fee_read_and_bare_list() -> None:
    route = _route()
    operation = create_app().openapi()["paths"][f"/api/v1{ROUTER_PATH}"]["get"]

    assert route.response_model == list[FeeReductionApprovalListItemOut]
    assert route.dependant.body_params == []
    assert [item.name for item in route.dependant.path_params] == ["case_id"]
    assert route.dependant.query_params == []
    assert "requestBody" not in operation
    assert [item["name"] for item in operation["parameters"]] == ["case_id"]
    assert inspect.getclosurevars(_permission_dependency()).nonlocals["code"] == "Fee.Read"


def test_empty_current_approval_set_returns_200_bare_empty_list() -> None:
    session = ApprovalListSessionSpy()

    with _client(session) as client:
        response = client.get(PATH)

    assert response.status_code == 200
    assert response.json() == []
    assert session.get_calls == [(Case, "case-1")]
    assert session.get_inside_no_autoflush == [True]
    assert session.no_autoflush_enters == 1
    assert session.no_autoflush_exits == 1
    assert len(session.statements) == 1


def test_all_confirmed_current_source_approvals_for_case_are_returned_in_stable_order() -> None:
    rows = [
        _row("approval-case"),
        _row(
            "approval-applicants",
            scope_type="APPLICANT_SET",
            case_id=None,
            applicant_set_key="applicant-set-key",
            reduction_ratio=Decimal("0.7000"),
            fee_codes=("REEXAMINATION",),
            source_evidence_version_id="evidence-2",
            confirmed_at=datetime(2026, 7, 15, 9, 30),
        ),
    ]
    session = ApprovalListSessionSpy(rows)

    with _client(session) as client:
        response = client.get(PATH)

    assert response.status_code == 200
    assert response.json() == [
        {
            "approval_id": "approval-case",
            "scope_type": "CASE",
            "case_id": "case-1",
            "applicant_set_key": None,
            "reduction_ratio": "0.8500",
            "fee_codes": ["ANNUITY", "APPLICATION"],
            "fee_year_from": 1,
            "fee_year_to": 3,
            "effective_from": "2026-07-01",
            "effective_to": "2027-06-30",
            "source_evidence_version_id": "evidence-1",
            "confirmation_status": "CONFIRMED",
            "confirmed_at": "2026-07-14T09:30:00",
            "confirmed_by": "actor-1",
            "is_current": True,
        },
        {
            "approval_id": "approval-applicants",
            "scope_type": "APPLICANT_SET",
            "case_id": None,
            "applicant_set_key": "applicant-set-key",
            "reduction_ratio": "0.7000",
            "fee_codes": ["REEXAMINATION"],
            "fee_year_from": 1,
            "fee_year_to": 3,
            "effective_from": "2026-07-01",
            "effective_to": "2027-06-30",
            "source_evidence_version_id": "evidence-2",
            "confirmation_status": "CONFIRMED",
            "confirmed_at": "2026-07-15T09:30:00",
            "confirmed_by": "actor-1",
            "is_current": True,
        },
    ]
    assert all(tuple(item) == OUTPUT_FIELDS for item in response.json())
    assert len(session.statements) == 1

    statement = session.statements[0]
    assert isinstance(statement, Select)
    assert tuple(statement.selected_columns.keys()) == (
        "approval_id",
        "scope_type",
        "case_id",
        "applicant_set_key",
        "reduction_ratio",
        "fee_scope_snapshot",
        "fee_scope_hash",
        "fee_year_from",
        "fee_year_to",
        "effective_from",
        "effective_to",
        "source_evidence_version_id",
        "confirmation_status",
        "confirmed_at",
        "confirmed_by",
        "evidence_case_id",
        "evidence_lineage_key",
        "evidence_current_identity_key",
        "is_current",
    )
    sql = " ".join(str(statement).split())
    assert "JOIN t_document_evidence_version" in sql
    assert "t_document_evidence_version.case_id =" in sql
    assert "t_fee_reduction_approval.confirmation_status =" in sql
    projection_sql, where_sql = sql.split(" WHERE ", maxsplit=1)
    assert (
        "t_document_evidence_version.current_identity_key = "
        "(t_document_evidence_version.case_id || "
    ) in projection_sql
    assert " || t_document_evidence_version.lineage_key)" in projection_sql
    assert "t_document_evidence_version.current_identity_key =" not in where_sql
    assert "t_document_evidence_version.current_identity_key IS NOT NULL" not in where_sql
    assert (
        "ORDER BY t_fee_reduction_approval.confirmed_at ASC, t_fee_reduction_approval.id ASC"
    ) in sql
    assert " LIMIT " not in f" {sql.upper()} "


def test_missing_case_returns_404_without_listing_or_writes() -> None:
    session = ApprovalListSessionSpy(case_exists=False)

    with _client(session) as client:
        response = client.get(PATH)

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "CASE_NOT_FOUND"
    assert session.get_calls == [(Case, "case-1")]
    assert session.get_inside_no_autoflush == [True]
    assert session.statements == []


@pytest.mark.parametrize(
    ("fee_scope_snapshot", "fee_scope_hash"),
    [
        pytest.param(
            '{"fee_codes":[],"schema":"FPMS_FEE_REDUCTION_FEE_SCOPE_V1"}',
            None,
            id="empty-fee-codes",
        ),
        pytest.param(
            '{"fee_codes":["APPLICATION","APPLICATION"],'
            '"schema":"FPMS_FEE_REDUCTION_FEE_SCOPE_V1"}',
            None,
            id="duplicate-fee-code",
        ),
        pytest.param(
            '{"fee_codes":["APPLICATION","ANNUITY"],"schema":"FPMS_FEE_REDUCTION_FEE_SCOPE_V1"}',
            None,
            id="unsorted-fee-codes",
        ),
        pytest.param(
            '{"fee_codes":[" APPLICATION"],"schema":"FPMS_FEE_REDUCTION_FEE_SCOPE_V1"}',
            None,
            id="noncanonical-fee-code",
        ),
        pytest.param(
            '{"fee_codes":["' + "X" * 65 + '"],"schema":"FPMS_FEE_REDUCTION_FEE_SCOPE_V1"}',
            None,
            id="overlong-fee-code",
        ),
        pytest.param(
            '{"fee_codes":["APPLICATION"],"fee_codes":["ANNUITY"],'
            '"schema":"FPMS_FEE_REDUCTION_FEE_SCOPE_V1"}',
            None,
            id="duplicate-json-key",
        ),
        pytest.param(
            '{ "fee_codes":["APPLICATION"],"schema":"FPMS_FEE_REDUCTION_FEE_SCOPE_V1"}',
            None,
            id="noncanonical-json-bytes",
        ),
        pytest.param(
            '{"fee_codes":["APPLICATION"],"schema":"FPMS_FEE_REDUCTION_FEE_SCOPE_V1"}',
            "A" * 64,
            id="nonlowercase-sha256",
        ),
        pytest.param(
            '{"fee_codes":["APPLICATION"],"schema":"FPMS_FEE_REDUCTION_FEE_SCOPE_V1"}',
            "0" * 64,
            id="sha256-mismatch",
        ),
    ],
)
def test_corrupt_persisted_fee_scope_fails_closed_with_409(
    fee_scope_snapshot: str,
    fee_scope_hash: str | None,
) -> None:
    row = _row("approval-corrupt")
    row["fee_scope_snapshot"] = fee_scope_snapshot
    row["fee_scope_hash"] = (
        sha256(fee_scope_snapshot.encode("utf-8")).hexdigest()
        if fee_scope_hash is None
        else fee_scope_hash
    )
    session = ApprovalListSessionSpy([row])

    with _client(session) as client:
        response = client.get(PATH)

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "FEE_REDUCTION_APPROVAL_SCOPE_CORRUPT"


def test_malformed_nonnull_evidence_current_identity_fails_closed_with_409() -> None:
    row = _row("approval-corrupt-identity", evidence_current_identity_key="case-1|wrong")
    row["is_current"] = False
    session = ApprovalListSessionSpy([row])

    with _client(session) as client:
        response = client.get(PATH)

    assert response.status_code == 409
    assert response.json()["error"]["code"] == ("FEE_REDUCTION_APPROVAL_SOURCE_IDENTITY_CORRUPT")


def test_sqlite_malformed_nonnull_evidence_identity_reaches_fail_closed_validation(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker[Session],
) -> None:
    fee_scope_snapshot = '{"fee_codes":["APPLICATION"],"schema":"FPMS_FEE_REDUCTION_FEE_SCOPE_V1"}'
    with session_factory() as transaction:
        transaction.add(Case(id="case-1", case_no="CASE-1"))
        transaction.add(Document(id="document-1", case_id="case-1"))
        transaction.flush()
        transaction.add(
            DocAttachment(
                id="attachment-1",
                document_id="document-1",
                file_name="fee-reduction.pdf",
                file_path="/evidence/fee-reduction.pdf",
            )
        )
        transaction.flush()
        transaction.add(
            DocumentEvidenceVersion(
                id="evidence-1",
                case_id="case-1",
                document_id="document-1",
                attachment_id="attachment-1",
                lineage_key="fee-reduction",
                role="OFFICIAL_NOTICE",
                version_number=1,
                state="FINAL",
                creator_id="creator-1",
                review_state="APPROVED",
                reviewer_id="reviewer-1",
                reviewed_at=datetime(2026, 7, 14, 9, 0),
                final_submitted_at=datetime(2026, 7, 14, 8, 0),
                content_hash="sha256:" + "a" * 64,
                current_identity_key="case-1|wrong",
            )
        )
        transaction.flush()
        transaction.add(
            FeeReductionApproval(
                id="approval-1",
                scope_type="CASE",
                case_id="case-1",
                applicant_set_key=None,
                reduction_ratio=Decimal("0.8500"),
                fee_scope_snapshot=fee_scope_snapshot,
                fee_scope_hash=sha256(fee_scope_snapshot.encode("utf-8")).hexdigest(),
                fee_year_from=1,
                fee_year_to=3,
                effective_from=date(2026, 7, 1),
                effective_to=date(2027, 6, 30),
                source_evidence_version_id="evidence-1",
                confirmation_status="CONFIRMED",
                confirmed_at=datetime(2026, 7, 14, 9, 30),
                confirmed_by="actor-1",
                eligibility_snapshot="{}",
                eligibility_snapshot_hash="0" * 64,
                approval_identity_key="1" * 64,
            )
        )
        transaction.commit()

    response = client.get(PATH, headers=auth_headers)

    assert response.status_code == 409
    assert response.json()["error"]["code"] == ("FEE_REDUCTION_APPROVAL_SOURCE_IDENTITY_CORRUPT")


def test_authentication_permission_and_path_validation_remain_401_403_422() -> None:
    unauthenticated_session = ApprovalListSessionSpy()
    app = create_app()
    app.dependency_overrides[get_db] = lambda: unauthenticated_session
    with TestClient(app) as client:
        unauthenticated = client.get(PATH)

    assert unauthenticated.status_code == 401
    assert unauthenticated.json()["error"]["code"] == "AUTH_REQUIRED"
    assert unauthenticated_session.get_calls == []
    assert unauthenticated_session.statements == []

    forbidden = BusinessError(
        "FORBIDDEN",
        "Permission denied",
        details={"required_perm": "Fee.Read"},
        status_code=403,
    )
    forbidden_session = ApprovalListSessionSpy()
    with _client(forbidden_session, permission_error=forbidden) as client:
        response = client.get(PATH)

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "FORBIDDEN"
    assert forbidden_session.get_calls == []
    assert forbidden_session.statements == []

    invalid_session = ApprovalListSessionSpy()
    with _client(invalid_session) as client:
        invalid = client.get("/api/v1/fees/cases/" + "x" * 37 + "/reduction-approvals")

    assert invalid.status_code == 422
    assert invalid_session.get_calls == []
    assert invalid_session.statements == []
