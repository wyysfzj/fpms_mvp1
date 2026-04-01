from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session

from app.core.errors import raise_business_error
from app.core.pagination import PageResult, offset_limit
from app.modules.auth.models import T_Role, T_User, T_UserRole
from app.modules.billing.models import BillItem, PaymentLine
from app.modules.cases.enums import CaseStatus, CaseType, FlowDir
from app.modules.cases.models import (
    Case,
    T_BioDeposit,
    T_CaseAgentSplit,
    T_CaseApplicant,
    T_CaseInventor,
    T_Priority,
)
from app.modules.cases.schemas import (
    CaseAgentSplitIn,
    CaseApplicantIn,
    CaseBatchFilingActionOut,
    CaseBatchFilingCandidateItem,
    CaseCreate,
    CaseListItem,
    CaseListReportResponse,
    CaseReportCountResponse,
    CaseReportSummaryResponse,
    CaseUpdateFull,
    CaseUpdateLimited,
)
from app.modules.fees.models import FeeDraft
from app.modules.masterdata.applicants.models import Applicant
from app.modules.masterdata.clients.models import Client, ClientAddress

_CONSULTING_CASE_TYPES = {CaseType.CONSULTING.value, CaseType.SEARCH.value}
_FOREIGN_FLOW_DIRS = {FlowDir.CN_OUTBOUND.value, FlowDir.FOREIGN_INBOUND.value}
_FOREIGN_AGENT_TYPES = {"AGENT", "代理所"}
_AGENT_ROLE_CODE = "Agent"
_INVALIDATION_ROLES = {"PATENTEE", "REQUESTER", "BOTH"}
_TERMINAL_STATUS_ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    CaseStatus.GRANTED.value: {
        CaseStatus.GRANTED.value,
        CaseStatus.TERMINATED.value,
        CaseStatus.INVALIDATED.value,
        CaseStatus.EXPIRED.value,
    },
    CaseStatus.REJECTED.value: {CaseStatus.REJECTED.value},
    CaseStatus.WITHDRAWN.value: {CaseStatus.WITHDRAWN.value},
    CaseStatus.ABANDONED.value: {CaseStatus.ABANDONED.value},
    CaseStatus.TERMINATED.value: {CaseStatus.TERMINATED.value},
    CaseStatus.INVALIDATED.value: {CaseStatus.INVALIDATED.value},
    CaseStatus.EXPIRED.value: {CaseStatus.EXPIRED.value},
}
_STATUSES_REQUIRING_APPLICATION_FIELDS = {
    status.value for status in CaseStatus if status != CaseStatus.NOT_FILED
}
_CASE_FEE_STATUSES = {"DRAFT", "BILLED", "PAID"}


def _normalize_required_text(value: str | None, field_name: str) -> str:
    normalized = (value or "").strip()
    if not normalized:
        raise_business_error(
            "CONSULTING_CASE_INVALID",
            f"{field_name} is required",
            status_code=400,
        )
    return normalized


def _normalize_search_token(value: str | None) -> str | None:
    normalized = (value or "").strip().lower().replace(" ", "").replace("-", "")
    return normalized or None


def validate_applicants(applicants: list[dict]) -> None:
    """
    Validate applicants list per business rules.

    Rules:
    - Must have at least 1 applicant
    - Exactly 1 applicant must have is_first=True
    - seq values must be unique

    Raises:
        BusinessError with appropriate code
    """
    if not applicants:
        raise_business_error(
            "CASE_APPLICANT_REQUIRED",
            "At least one applicant is required",
            status_code=400,
        )

    first_count = sum(1 for applicant in applicants if applicant.get("is_first"))
    if first_count == 0:
        raise_business_error(
            "CASE_FIRST_APPLICANT_REQUIRED",
            "Exactly one applicant must be marked as first",
            status_code=400,
        )
    if first_count > 1:
        raise_business_error(
            "CASE_DUPLICATE_FIRST_APPLICANT",
            "Only one applicant can be marked as first",
            status_code=400,
        )

    seqs = [applicant.get("seq") for applicant in applicants]
    if len(seqs) != len(set(seqs)):
        raise_business_error(
            "CASE_DUPLICATE_APPLICANT_SEQ",
            "Applicant seq values must be unique",
            status_code=400,
        )


def validate_client_exists(db: Session, client_id: str | None) -> None:
    if not client_id:
        return
    exists = db.query(Client.id).filter(Client.id == client_id).first()
    if not exists:
        raise_business_error("CLIENT_NOT_FOUND", "Client not found", status_code=404)


def validate_case_applicant_links(db: Session, applicants: list[CaseApplicantIn]) -> None:
    for applicant in applicants:
        applicant_id = getattr(applicant, "applicant_id", None)
        if not applicant_id:
            continue
        exists = db.query(Applicant.id).filter(Applicant.id == applicant_id).first()
        if not exists:
            raise_business_error("APPLICANT_NOT_FOUND", "Applicant not found", status_code=404)


def validate_foreign_agent(
    db: Session,
    *,
    flow_dir: str | None,
    foreign_agent_id: str | None,
) -> None:
    normalized_flow_dir = (flow_dir or "").strip()
    if normalized_flow_dir in _FOREIGN_FLOW_DIRS and not foreign_agent_id:
        raise_business_error(
            "CASE_FOREIGN_AGENT_REQUIRED",
            "foreign_agent_id is required for foreign-facing cases",
            status_code=400,
        )
    if not foreign_agent_id:
        return
    foreign_agent = (
        db.query(Client.id, Client.client_type).filter(Client.id == foreign_agent_id).first()
    )
    if not foreign_agent:
        raise_business_error("CLIENT_NOT_FOUND", "Client not found", status_code=404)
    normalized_client_type = (foreign_agent.client_type or "").strip().upper()
    if normalized_client_type not in _FOREIGN_AGENT_TYPES:
        raise_business_error(
            "CASE_FOREIGN_AGENT_INVALID_TYPE",
            "foreign_agent_id must reference an agent client",
            status_code=400,
        )


def validate_country_fields(*, flow_dir: str | None, to_country: str | None) -> None:
    normalized_flow_dir = (flow_dir or "").strip()
    normalized_to_country = (to_country or "").strip()
    if normalized_flow_dir in _FOREIGN_FLOW_DIRS and not normalized_to_country:
        raise_business_error(
            "CASE_TO_COUNTRY_REQUIRED",
            "to_country is required for foreign-facing cases",
            status_code=400,
        )


def _validate_case_address(
    db: Session,
    *,
    client_id: str | None,
    address_id: str | None,
    field_name: str,
) -> None:
    if not address_id:
        return
    address = (
        db.query(ClientAddress.id, ClientAddress.client_id)
        .filter(ClientAddress.id == address_id)
        .first()
    )
    if not address:
        raise_business_error("ADDRESS_NOT_FOUND", f"{field_name} not found", status_code=404)
    if client_id and address.client_id != client_id:
        raise_business_error(
            "CASE_ADDRESS_CLIENT_MISMATCH",
            f"{field_name} must belong to the selected client",
            status_code=400,
        )


def validate_case_addresses(
    db: Session,
    *,
    client_id: str | None,
    doc_address_id: str | None,
    bill_address_id: str | None,
) -> None:
    _validate_case_address(
        db,
        client_id=client_id,
        address_id=doc_address_id,
        field_name="doc_address_id",
    )
    _validate_case_address(
        db,
        client_id=client_id,
        address_id=bill_address_id,
        field_name="bill_address_id",
    )


def validate_priorities(priorities: list[dict]) -> None:
    seqs = [priority.get("seq") for priority in priorities]
    if len(seqs) != len(set(seqs)):
        raise_business_error(
            "CASE_DUPLICATE_PRIORITY_SEQ",
            "Priority seq values must be unique",
            status_code=400,
        )

    for priority in priorities:
        normalized_country_code = (priority.get("country_code") or "").strip() or None
        normalized_prio_no = (priority.get("prio_no") or "").strip() or None
        normalized_prio_date = priority.get("prio_date")
        has_any_value = any(
            value is not None
            for value in (normalized_country_code, normalized_prio_no, normalized_prio_date)
        )
        has_all_values = all(
            value is not None
            for value in (normalized_country_code, normalized_prio_no, normalized_prio_date)
        )
        if has_any_value and not has_all_values:
            raise_business_error(
                "CASE_PRIORITY_INCOMPLETE",
                "Priority country_code, prio_no and prio_date must all be provided",
                status_code=400,
            )


def validate_bio_deposits(bio_deposits: list[dict]) -> None:
    seqs = [bio_deposit.get("seq") for bio_deposit in bio_deposits]
    if len(seqs) != len(set(seqs)):
        raise_business_error(
            "CASE_DUPLICATE_BIO_DEPOSIT_SEQ",
            "Bio deposit seq values must be unique",
            status_code=400,
        )

    for bio_deposit in bio_deposits:
        normalized_deposit_no = (bio_deposit.get("deposit_no") or "").strip() or None
        normalized_unit_name = (bio_deposit.get("deposit_unit_name") or "").strip() or None
        normalized_deposit_date = bio_deposit.get("deposit_date")
        normalized_name = (bio_deposit.get("name") or "").strip() or None
        has_any_value = any(
            value is not None
            for value in (
                normalized_deposit_no,
                normalized_unit_name,
                normalized_deposit_date,
                normalized_name,
            )
        )
        has_all_values = all(
            value is not None
            for value in (
                normalized_deposit_no,
                normalized_unit_name,
                normalized_deposit_date,
                normalized_name,
            )
        )
        if has_any_value and not has_all_values:
            raise_business_error(
                "CASE_BIO_DEPOSIT_INCOMPLETE",
                "Bio deposit rows must include deposit_no, deposit_unit_name, deposit_date and name",
                status_code=400,
            )


def validate_case_agent_splits(db: Session, agent_splits: list[CaseAgentSplitIn]) -> None:
    if not agent_splits:
        return

    agent_ids = [split.agent_id for split in agent_splits]
    if len(agent_ids) != len(set(agent_ids)):
        raise_business_error(
            "CASE_AGENT_SPLIT_DUPLICATE_MEMBER",
            "agent_id values must be unique",
            status_code=400,
        )

    if any((split.role or "").strip() not in {_AGENT_ROLE_CODE} for split in agent_splits):
        raise_business_error(
            "CASE_AGENT_SPLIT_INVALID_ROLE",
            "split role must be Agent",
            status_code=400,
        )

    if any(split.share_ratio <= 0 or split.share_ratio > Decimal("100") for split in agent_splits):
        raise_business_error(
            "CASE_AGENT_SPLIT_RATIO_INVALID",
            "share_ratio must be greater than 0 and at most 100",
            status_code=400,
        )

    total_ratio = sum((split.share_ratio for split in agent_splits), Decimal("0"))
    if total_ratio != Decimal("100"):
        raise_business_error(
            "CASE_AGENT_SPLIT_RATIO_INVALID",
            "share_ratio values must sum to 100",
            status_code=400,
        )

    eligible_agent_ids = {
        row[0]
        for row in (
            db.query(T_User.id)
            .join(T_UserRole, T_UserRole.user_id == T_User.id)
            .join(T_Role, T_Role.id == T_UserRole.role_id)
            .filter(T_User.id.in_(agent_ids), T_Role.code == _AGENT_ROLE_CODE)
            .all()
        )
    }
    if eligible_agent_ids != set(agent_ids):
        raise_business_error(
            "CASE_AGENT_SPLIT_INVALID_MEMBER",
            "split members must be internal users with Agent role",
            status_code=400,
        )


def validate_case_type_specific_fields(
    db: Session,
    *,
    case_type: str | None,
    intl_app_no: str | None,
    intl_app_date: date | None,
    pct_national_entry_date: date | None,
    original_case_id: str | None,
    invalid_client_id: str | None,
    invalid_patentee: str | None,
    invalid_requester: str | None,
    invalid_role: str | None,
) -> None:
    normalized_case_type = (case_type or "").strip()
    if normalized_case_type == CaseType.PCT_INTL.value:
        if not ((intl_app_no or "").strip() and intl_app_date):
            raise_business_error(
                "CASE_PCT_INTL_REQUIRED",
                "intl_app_no and intl_app_date are required for PCT_INTL cases",
                status_code=400,
            )
    if normalized_case_type == CaseType.PCT_NATL.value and not pct_national_entry_date:
        raise_business_error(
            "CASE_PCT_NATL_REQUIRED",
            "pct_national_entry_date is required for PCT_NATL cases",
            status_code=400,
        )
    if normalized_case_type == CaseType.INVALIDATION.value:
        if not invalid_client_id or not (invalid_role or "").strip():
            raise_business_error(
                "CASE_INVALIDATION_REQUIRED",
                "invalid_client_id and invalid_role are required for INVALIDATION cases",
                status_code=400,
            )
        normalized_invalid_role = (invalid_role or "").strip().upper()
        if normalized_invalid_role not in _INVALIDATION_ROLES:
            raise_business_error(
                "CASE_INVALID_ROLE_INVALID",
                "invalid_role must be PATENTEE, REQUESTER or BOTH",
                status_code=400,
            )
        if not ((invalid_patentee or "").strip() or (invalid_requester or "").strip()):
            raise_business_error(
                "CASE_INVALIDATION_REQUIRED",
                "invalid_patentee or invalid_requester is required for INVALIDATION cases",
                status_code=400,
            )
    validate_client_exists(db, invalid_client_id)
    if original_case_id:
        exists = db.query(Case.id).filter(Case.id == original_case_id).first()
        if not exists:
            raise_business_error("CASE_NOT_FOUND", "Original case not found", status_code=404)


def validate_status_required_fields(
    *, status: str | None, app_no: str | None, filing_date: date | None
) -> None:
    if not status or status not in _STATUSES_REQUIRING_APPLICATION_FIELDS:
        return
    if not (app_no and filing_date):
        raise_business_error(
            "CASE_STATUS_REQUIRES_APPLICATION_FIELDS",
            "app_no and filing_date are required for the target status",
            status_code=400,
        )


def _apply_case_report_filters(
    query,
    *,
    q: str | None = None,
    case_no: str | None = None,
    app_no: str | None = None,
    client_id: str | None = None,
    status: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    case_type: str | None = None,
    patent_category: str | None = None,
    flow_dir: str | None = None,
    filing_date_from: date | None = None,
    filing_date_to: date | None = None,
    primary_agent_id: str | None = None,
    country: str | None = None,
    agent_id: str | None = None,
    applicant_id: str | None = None,
    patent_no: str | None = None,
    fee_status: str | None = None,
):
    if q:
        query = query.filter(
            or_(
                Case.case_no.contains(q),
                Case.title_cn.contains(q),
                Case.title_en.contains(q),
                Case.app_no.contains(q),
            )
        )
    if case_no:
        query = query.filter(Case.case_no == case_no)
    if app_no:
        query = query.filter(Case.app_no == app_no)
    if client_id:
        query = query.filter(Case.client_id == client_id)
    if status:
        query = query.filter(Case.status == status)
    if date_from:
        query = query.filter(Case.recv_date >= date_from)
    if date_to:
        query = query.filter(Case.recv_date <= date_to)
    if case_type:
        query = query.filter(Case.case_type == case_type)
    if patent_category:
        query = query.filter(Case.patent_category == patent_category)
    if flow_dir:
        query = query.filter(Case.flow_dir == flow_dir)
    if filing_date_from:
        query = query.filter(Case.filing_date >= filing_date_from)
    if filing_date_to:
        query = query.filter(Case.filing_date <= filing_date_to)
    if primary_agent_id:
        query = query.filter(Case.primary_agent_id == primary_agent_id)
    if country:
        query = query.filter(or_(Case.from_country == country, Case.to_country == country))
    if agent_id:
        query = query.filter(
            or_(Case.primary_agent_id == agent_id, Case.second_agent_id == agent_id)
        )
    normalized_applicant_id = (applicant_id or "").strip()
    if normalized_applicant_id:
        applicant_case_ids = select(T_CaseApplicant.case_id).where(
            T_CaseApplicant.applicant_id == normalized_applicant_id
        )
        query = query.filter(Case.id.in_(applicant_case_ids))
    normalized_patent_no = _normalize_search_token(patent_no)
    if normalized_patent_no:
        patent_no_expr = func.replace(
            func.replace(func.lower(func.coalesce(Case.patent_no, "")), " ", ""),
            "-",
            "",
        )
        query = query.filter(patent_no_expr.contains(normalized_patent_no))
    normalized_fee_status = (fee_status or "").strip().upper()
    if normalized_fee_status:
        if normalized_fee_status not in _CASE_FEE_STATUSES:
            raise_business_error(
                "CASE_FEE_STATUS_INVALID",
                "Unsupported fee_status",
                status_code=400,
            )
        has_payment = select(PaymentLine.id).where(PaymentLine.case_id == Case.id).exists()
        has_bill = select(BillItem.id).where(BillItem.case_id == Case.id).exists()
        has_draft = select(FeeDraft.id).where(FeeDraft.case_id == Case.id).exists()
        if normalized_fee_status == "PAID":
            query = query.filter(has_payment)
        elif normalized_fee_status == "BILLED":
            query = query.filter(and_(~has_payment, has_bill))
        else:
            query = query.filter(and_(~has_payment, ~has_bill, has_draft))
    return query


def _build_case_report_summary(query) -> CaseReportSummaryResponse:
    status_rows = (
        query.with_entities(Case.status, func.count(Case.id))
        .group_by(Case.status)
        .order_by(Case.status.asc())
        .all()
    )
    case_type_rows = (
        query.with_entities(Case.case_type, func.count(Case.id))
        .group_by(Case.case_type)
        .order_by(Case.case_type.asc())
        .all()
    )
    return CaseReportSummaryResponse(
        total_case_count=query.count(),
        status_counts=[
            CaseReportCountResponse(key=status_key, count=count)
            for status_key, count in status_rows
        ],
        case_type_counts=[
            CaseReportCountResponse(key=case_type_key, count=count)
            for case_type_key, count in case_type_rows
        ],
    )


def validate_case_status_transition(current_status: str | None, target_status: str | None) -> None:
    if not target_status or not current_status or target_status == current_status:
        return

    try:
        CaseStatus(target_status)
    except ValueError:
        raise_business_error(
            "CASE_STATUS_INVALID",
            f"Unsupported case status '{target_status}'",
            status_code=409,
        )

    allowed = _TERMINAL_STATUS_ALLOWED_TRANSITIONS.get(current_status)
    if allowed and target_status not in allowed:
        raise_business_error(
            "CASE_STATUS_TRANSITION_INVALID",
            f"Cannot change case status from {current_status} to {target_status}",
            status_code=409,
        )


def list_cases(
    db: Session,
    q: str | None = None,
    case_no: str | None = None,
    app_no: str | None = None,
    client_id: str | None = None,
    status: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    case_type: str | None = None,
    patent_category: str | None = None,
    flow_dir: str | None = None,
    filing_date_from: date | None = None,
    filing_date_to: date | None = None,
    primary_agent_id: str | None = None,
    country: str | None = None,
    agent_id: str | None = None,
    applicant_id: str | None = None,
    patent_no: str | None = None,
    fee_status: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> CaseListReportResponse:
    """List cases with pagination, filters, and report summary."""
    query = _apply_case_report_filters(
        db.query(Case),
        q=q,
        case_no=case_no,
        app_no=app_no,
        client_id=client_id,
        status=status,
        date_from=date_from,
        date_to=date_to,
        case_type=case_type,
        patent_category=patent_category,
        flow_dir=flow_dir,
        filing_date_from=filing_date_from,
        filing_date_to=filing_date_to,
        primary_agent_id=primary_agent_id,
        country=country,
        agent_id=agent_id,
        applicant_id=applicant_id,
        patent_no=patent_no,
        fee_status=fee_status,
    )

    total = query.count()
    summary = _build_case_report_summary(query)

    off, lim = offset_limit(page, page_size)
    items = query.order_by(Case.created_at.desc()).offset(off).limit(lim).all()

    list_items = [
        CaseListItem(
            id=case.id,
            case_no=case.case_no,
            case_type=case.case_type,
            patent_category=case.patent_category,
            client_id=case.client_id,
            title_cn=case.title_cn,
            title_en=case.title_en,
            app_no=case.app_no,
            status=case.status,
            patent_no=case.patent_no,
            primary_agent_id=case.primary_agent_id,
        )
        for case in items
    ]

    return CaseListReportResponse(
        items=list_items,
        page=page,
        page_size=page_size,
        total=total,
        summary=summary,
    )


def list_batch_filing_candidates(
    db: Session,
    *,
    case_type: str | None = None,
    flow_dir: str | None = None,
    status: str = CaseStatus.NOT_FILED.value,
    recv_date_from: date | None = None,
    recv_date_to: date | None = None,
    client_id: str | None = None,
    primary_agent_id: str | None = None,
    patent_category: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> PageResult[CaseBatchFilingCandidateItem]:
    query = db.query(Case)

    if case_type:
        query = query.filter(Case.case_type == case_type)
    if flow_dir:
        query = query.filter(Case.flow_dir == flow_dir)
    if status:
        query = query.filter(Case.status == status)
    if recv_date_from:
        query = query.filter(Case.recv_date >= recv_date_from)
    if recv_date_to:
        query = query.filter(Case.recv_date <= recv_date_to)
    if client_id:
        query = query.filter(Case.client_id == client_id)
    if primary_agent_id:
        query = query.filter(Case.primary_agent_id == primary_agent_id)
    if patent_category:
        query = query.filter(Case.patent_category == patent_category)

    total = query.count()
    off, lim = offset_limit(page, page_size)
    items = query.order_by(Case.recv_date.asc(), Case.case_no.asc()).offset(off).limit(lim).all()

    client_ids = {case.client_id for case in items if case.client_id}
    client_name_map: dict[str, str] = {}
    if client_ids:
        clients = db.query(Client.id, Client.name_cn).filter(Client.id.in_(client_ids)).all()
        client_name_map = {client.id: client.name_cn for client in clients}

    candidate_items = [
        CaseBatchFilingCandidateItem(
            id=case.id,
            case_no=case.case_no,
            title_cn=case.title_cn,
            client_name=client_name_map.get(case.client_id) if case.client_id else None,
            case_type=case.case_type,
            patent_category=case.patent_category,
            flow_dir=case.flow_dir,
            recv_date=str(case.recv_date) if case.recv_date else None,
            status=case.status,
            has_exam_request=case.has_exam_request,
        )
        for case in items
    ]

    return PageResult(items=candidate_items, page=page, page_size=page_size, total=total)


def execute_batch_filing(
    db: Session,
    *,
    selected_case_ids: list[str],
    submitted_date: date,
    apply_exam_now: bool,
    user_id: str,
) -> CaseBatchFilingActionOut:
    if not selected_case_ids:
        raise_business_error(
            "CASE_BATCH_FILING_SELECTION_REQUIRED",
            "selected_case_ids must not be empty",
            status_code=400,
        )

    unique_case_ids = list(dict.fromkeys(selected_case_ids))
    cases = db.query(Case).filter(Case.id.in_(unique_case_ids)).all()
    case_by_id = {case.id: case for case in cases}
    missing_case_ids = [case_id for case_id in unique_case_ids if case_id not in case_by_id]
    if missing_case_ids:
        raise_business_error(
            "CASE_BATCH_FILING_CASE_NOT_FOUND",
            "One or more selected cases do not exist",
            status_code=404,
        )

    invalid_status_case_nos = [
        case.case_no for case in cases if case.status != CaseStatus.NOT_FILED.value
    ]
    if invalid_status_case_nos:
        raise_business_error(
            "CASE_BATCH_FILING_STATUS_INVALID",
            "Only NOT_FILED cases can be batch filed",
            status_code=400,
        )

    invalid_recv_date_case_nos = [
        case.case_no
        for case in cases
        if case.recv_date is not None and submitted_date < case.recv_date
    ]
    if invalid_recv_date_case_nos:
        raise_business_error(
            "CASE_BATCH_FILING_SUBMITTED_DATE_INVALID",
            "submitted_date must be greater than or equal to recv_date",
            status_code=400,
        )

    updated_case_ids: list[str] = []
    for case_id in unique_case_ids:
        case = case_by_id[case_id]
        case.submitted_date = submitted_date
        case.status = CaseStatus.WAITING_RECEIPT.value
        if apply_exam_now:
            case.has_exam_request = True
        case.updated_by = user_id
        updated_case_ids.append(case.id)

    db.commit()
    return CaseBatchFilingActionOut(
        success_count=len(updated_case_ids),
        failure_count=0,
        updated_case_ids=updated_case_ids,
    )


def create_case(db: Session, data: CaseCreate, user_id: str) -> Case:
    """Create new case with applicants, inventors, priorities."""
    existing = db.query(Case).filter(Case.case_no == data.case_no).first()
    if existing:
        raise_business_error(
            "CASE_NO_DUPLICATE",
            f"Case number '{data.case_no}' already exists",
            status_code=400,
        )

    applicants_dict = [applicant.model_dump() for applicant in data.applicants]
    priorities_dict = [priority.model_dump() for priority in data.priorities]
    bio_deposits_dict = [bio_deposit.model_dump() for bio_deposit in data.bio_deposits]
    if applicants_dict:
        validate_applicants(applicants_dict)
        validate_case_applicant_links(db, data.applicants)
    validate_client_exists(db, data.client_id)
    validate_foreign_agent(db, flow_dir=data.flow_dir.value, foreign_agent_id=data.foreign_agent_id)
    validate_country_fields(flow_dir=data.flow_dir.value, to_country=data.to_country)
    validate_case_addresses(
        db,
        client_id=data.client_id,
        doc_address_id=data.doc_address_id,
        bill_address_id=data.bill_address_id,
    )
    validate_priorities(priorities_dict)
    validate_bio_deposits(bio_deposits_dict)
    validate_case_type_specific_fields(
        db,
        case_type=data.case_type.value,
        intl_app_no=data.intl_app_no,
        intl_app_date=data.intl_app_date,
        pct_national_entry_date=data.pct_national_entry_date,
        original_case_id=data.original_case_id,
        invalid_client_id=data.invalid_client_id,
        invalid_patentee=data.invalid_patentee,
        invalid_requester=data.invalid_requester,
        invalid_role=data.invalid_role,
    )

    case = Case(
        id=str(uuid4()),
        case_no=data.case_no,
        case_type=data.case_type,
        patent_category=data.patent_category,
        flow_dir=data.flow_dir,
        client_id=data.client_id,
        foreign_agent_id=data.foreign_agent_id,
        foreign_ref=data.foreign_ref,
        from_country=data.from_country,
        to_country=data.to_country,
        doc_address_id=data.doc_address_id,
        bill_address_id=data.bill_address_id,
        title_cn=data.title_cn,
        title_en=data.title_en,
        app_no=data.app_no,
        status=data.status.value if data.status else "NOT_FILED",
        recv_date=data.recv_date,
        # A3 — Publication / Grant
        pub_date=data.pub_date,
        pub_no=data.pub_no,
        issue_date=data.issue_date,
        grant_date=data.grant_date,
        grant_no=data.grant_no,
        cert_no=data.cert_no,
        patent_no=data.patent_no,
        valid_until=data.valid_until,
        # A3 — Spec details
        spec_pages=data.spec_pages,
        draw_pages=data.draw_pages,
        claim_count=data.claim_count,
        claim_pages=data.claim_pages,
        manuscript_words=data.manuscript_words,
        has_exam_request=data.has_exam_request,
        ro=data.ro,
        isa=data.isa,
        ipea=data.ipea,
        intl_app_no=data.intl_app_no,
        intl_app_date=data.intl_app_date,
        intl_pub_no=data.intl_pub_no,
        intl_pub_date=data.intl_pub_date,
        intl_pub_lang=data.intl_pub_lang,
        need_iper=data.need_iper,
        iper_date=data.iper_date,
        pct_national_entry_date=data.pct_national_entry_date,
        original_case_id=data.original_case_id,
        invalid_client_id=data.invalid_client_id,
        invalid_patentee=data.invalid_patentee,
        invalid_requester=data.invalid_requester,
        invalid_role=(data.invalid_role or "").strip().upper() or None,
        # A3 — Agent assignment
        primary_agent_id=data.primary_agent_id,
        second_agent_id=data.second_agent_id,
        draftor_id=data.draftor_id,
        # A3 — Control flags
        is_fee_monitor=data.is_fee_monitor,
        fee_reduction=data.fee_reduction,
        applicant_kind=data.applicant_kind,
        discount_rate=data.discount_rate,
        no_power=data.no_power,
        no_prio_text=data.no_prio_text,
        require_hk=data.require_hk,
        first_annuity_year=data.first_annuity_year,
        created_by=user_id,
        updated_by=user_id,
    )
    db.add(case)
    db.flush()

    for applicant in data.applicants:
        db.add(
            T_CaseApplicant(
                id=str(uuid4()),
                case_id=case.id,
                applicant_id=applicant.applicant_id,
                seq=applicant.seq,
                is_first=applicant.is_first,
                name_cn=applicant.name_cn,
                name_en=applicant.name_en,
                address_cn=applicant.address_cn,
                address_en=applicant.address_en,
            )
        )

    for inventor in data.inventors:
        db.add(
            T_CaseInventor(
                id=str(uuid4()),
                case_id=case.id,
                seq=inventor.seq,
                name_cn=inventor.name_cn,
                name_en=inventor.name_en,
            )
        )

    for prio in data.priorities:
        db.add(
            T_Priority(
                id=str(uuid4()),
                case_id=case.id,
                seq=prio.seq,
                country_code=prio.country_code,
                prio_no=prio.prio_no,
                prio_date=prio.prio_date,
            )
        )

    for bio_deposit in data.bio_deposits:
        db.add(
            T_BioDeposit(
                id=str(uuid4()),
                case_id=case.id,
                seq=bio_deposit.seq,
                deposit_no=bio_deposit.deposit_no,
                deposit_unit_name=bio_deposit.deposit_unit_name,
                deposit_date=bio_deposit.deposit_date,
                name=bio_deposit.name,
            )
        )

    db.commit()
    db.refresh(case)
    return case


def create_consulting_or_search_case(
    db: Session,
    *,
    case_no: str | None,
    case_type: str | None,
    client_id: str | None,
    title_cn: str | None,
    primary_agent_id: str | None,
    recv_date: date | None,
    actor_id: str | None = None,
) -> Case:
    normalized_case_no = _normalize_required_text(case_no, "case_no")
    normalized_case_type = _normalize_required_text(case_type, "case_type").upper()
    normalized_client_id = _normalize_required_text(client_id, "client_id")
    normalized_title_cn = _normalize_required_text(title_cn, "title_cn")
    normalized_primary_agent_id = _normalize_required_text(primary_agent_id, "primary_agent_id")

    if recv_date is None:
        raise_business_error(
            "CONSULTING_CASE_INVALID",
            "recv_date is required",
            status_code=400,
        )

    if normalized_case_type not in _CONSULTING_CASE_TYPES:
        raise_business_error(
            "CONSULTING_CASE_INVALID",
            "case_type must be CONSULTING or SEARCH",
            status_code=400,
        )

    existing = db.query(Case).filter(Case.case_no == normalized_case_no).first()
    if existing:
        raise_business_error(
            "CASE_NO_DUPLICATE",
            f"Case number '{normalized_case_no}' already exists",
            status_code=409,
        )

    case = Case(
        id=str(uuid4()),
        case_no=normalized_case_no,
        case_type=normalized_case_type,
        client_id=normalized_client_id,
        title_cn=normalized_title_cn,
        primary_agent_id=normalized_primary_agent_id,
        recv_date=recv_date,
        status="NOT_FILED",
        created_by=actor_id,
        updated_by=actor_id,
    )
    db.add(case)
    db.commit()
    db.refresh(case)
    return case


def update_case_full(db: Session, case_id: str, data: CaseUpdateFull, user_id: str) -> Case:
    """Full update for Admin/Formalities roles."""
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise_business_error("CASE_NOT_FOUND", "Case not found", status_code=404)

    provided_fields = data.model_fields_set
    target_status = data.status.value if data.status is not None else case.status
    target_app_no = data.app_no if "app_no" in provided_fields else case.app_no
    target_filing_date = data.filing_date if "filing_date" in provided_fields else case.filing_date
    target_case_type = (
        data.case_type.value
        if "case_type" in provided_fields and data.case_type
        else case.case_type
    )
    target_flow_dir = (
        data.flow_dir.value if "flow_dir" in provided_fields and data.flow_dir else case.flow_dir
    )
    target_to_country = data.to_country if "to_country" in provided_fields else case.to_country
    target_foreign_agent_id = (
        data.foreign_agent_id if "foreign_agent_id" in provided_fields else case.foreign_agent_id
    )
    target_doc_address_id = (
        data.doc_address_id if "doc_address_id" in provided_fields else case.doc_address_id
    )
    target_bill_address_id = (
        data.bill_address_id if "bill_address_id" in provided_fields else case.bill_address_id
    )

    validate_case_status_transition(case.status, target_status)
    validate_status_required_fields(
        status=target_status,
        app_no=target_app_no,
        filing_date=target_filing_date,
    )
    validate_foreign_agent(
        db,
        flow_dir=target_flow_dir,
        foreign_agent_id=target_foreign_agent_id,
    )
    validate_country_fields(flow_dir=target_flow_dir, to_country=target_to_country)
    validate_case_addresses(
        db,
        client_id=case.client_id,
        doc_address_id=target_doc_address_id,
        bill_address_id=target_bill_address_id,
    )
    validate_case_type_specific_fields(
        db,
        case_type=target_case_type,
        intl_app_no=data.intl_app_no if "intl_app_no" in provided_fields else case.intl_app_no,
        intl_app_date=(
            data.intl_app_date if "intl_app_date" in provided_fields else case.intl_app_date
        ),
        pct_national_entry_date=(
            data.pct_national_entry_date
            if "pct_national_entry_date" in provided_fields
            else case.pct_national_entry_date
        ),
        original_case_id=(
            data.original_case_id
            if "original_case_id" in provided_fields
            else case.original_case_id
        ),
        invalid_client_id=(
            data.invalid_client_id
            if "invalid_client_id" in provided_fields
            else case.invalid_client_id
        ),
        invalid_patentee=(
            data.invalid_patentee
            if "invalid_patentee" in provided_fields
            else case.invalid_patentee
        ),
        invalid_requester=(
            data.invalid_requester
            if "invalid_requester" in provided_fields
            else case.invalid_requester
        ),
        invalid_role=data.invalid_role if "invalid_role" in provided_fields else case.invalid_role,
    )

    if "case_type" in provided_fields and data.case_type is not None:
        case.case_type = data.case_type
    if "flow_dir" in provided_fields and data.flow_dir is not None:
        case.flow_dir = data.flow_dir
    if "title_cn" in provided_fields:
        case.title_cn = data.title_cn
    if "title_en" in provided_fields:
        case.title_en = data.title_en
    if "app_no" in provided_fields:
        case.app_no = data.app_no
    if "filing_date" in provided_fields:
        case.filing_date = data.filing_date
    if "recv_date" in provided_fields:
        case.recv_date = data.recv_date
    if "foreign_agent_id" in provided_fields:
        case.foreign_agent_id = data.foreign_agent_id
    if "foreign_ref" in provided_fields:
        case.foreign_ref = data.foreign_ref
    if "from_country" in provided_fields:
        case.from_country = data.from_country
    if "to_country" in provided_fields:
        case.to_country = data.to_country
    if "doc_address_id" in provided_fields:
        case.doc_address_id = data.doc_address_id
    if "bill_address_id" in provided_fields:
        case.bill_address_id = data.bill_address_id
    if data.status is not None:
        case.status = data.status
    # A3 — Publication / Grant
    if "pub_date" in provided_fields:
        case.pub_date = data.pub_date
    if "pub_no" in provided_fields:
        case.pub_no = data.pub_no
    if "issue_date" in provided_fields:
        case.issue_date = data.issue_date
    if "grant_date" in provided_fields:
        case.grant_date = data.grant_date
    if "grant_no" in provided_fields:
        case.grant_no = data.grant_no
    if "cert_no" in provided_fields:
        case.cert_no = data.cert_no
    if "patent_no" in provided_fields:
        case.patent_no = data.patent_no
    if "valid_until" in provided_fields:
        case.valid_until = data.valid_until
    # A3 — Spec details
    if "spec_pages" in provided_fields:
        case.spec_pages = data.spec_pages
    if "draw_pages" in provided_fields:
        case.draw_pages = data.draw_pages
    if "claim_count" in provided_fields:
        case.claim_count = data.claim_count
    if "claim_pages" in provided_fields:
        case.claim_pages = data.claim_pages
    if "manuscript_words" in provided_fields:
        case.manuscript_words = data.manuscript_words
    if "has_exam_request" in provided_fields:
        case.has_exam_request = data.has_exam_request
    if "ro" in provided_fields:
        case.ro = data.ro
    if "isa" in provided_fields:
        case.isa = data.isa
    if "ipea" in provided_fields:
        case.ipea = data.ipea
    if "intl_app_no" in provided_fields:
        case.intl_app_no = data.intl_app_no
    if "intl_app_date" in provided_fields:
        case.intl_app_date = data.intl_app_date
    if "intl_pub_no" in provided_fields:
        case.intl_pub_no = data.intl_pub_no
    if "intl_pub_date" in provided_fields:
        case.intl_pub_date = data.intl_pub_date
    if "intl_pub_lang" in provided_fields:
        case.intl_pub_lang = data.intl_pub_lang
    if "need_iper" in provided_fields:
        case.need_iper = data.need_iper
    if "iper_date" in provided_fields:
        case.iper_date = data.iper_date
    if "pct_national_entry_date" in provided_fields:
        case.pct_national_entry_date = data.pct_national_entry_date
    if "original_case_id" in provided_fields:
        case.original_case_id = data.original_case_id
    if "invalid_client_id" in provided_fields:
        case.invalid_client_id = data.invalid_client_id
    if "invalid_patentee" in provided_fields:
        case.invalid_patentee = data.invalid_patentee
    if "invalid_requester" in provided_fields:
        case.invalid_requester = data.invalid_requester
    if "invalid_role" in provided_fields:
        case.invalid_role = (data.invalid_role or "").strip().upper() or None
    # A3 — Agent assignment
    if "primary_agent_id" in provided_fields:
        case.primary_agent_id = data.primary_agent_id
    if "second_agent_id" in provided_fields:
        case.second_agent_id = data.second_agent_id
    if "draftor_id" in provided_fields:
        case.draftor_id = data.draftor_id
    # A3 — Control flags
    if "is_fee_monitor" in provided_fields:
        case.is_fee_monitor = data.is_fee_monitor
    if "fee_reduction" in provided_fields:
        case.fee_reduction = data.fee_reduction
    if "applicant_kind" in provided_fields:
        case.applicant_kind = data.applicant_kind
    if "discount_rate" in provided_fields:
        case.discount_rate = data.discount_rate
    if "no_power" in provided_fields:
        case.no_power = data.no_power
    if "no_prio_text" in provided_fields:
        case.no_prio_text = data.no_prio_text
    if "require_hk" in provided_fields:
        case.require_hk = data.require_hk
    if "first_annuity_year" in provided_fields:
        case.first_annuity_year = data.first_annuity_year

    case.updated_by = user_id

    if data.applicants is not None:
        applicants_dict = [applicant.model_dump() for applicant in data.applicants]
        if applicants_dict:
            validate_applicants(applicants_dict)
            validate_case_applicant_links(db, data.applicants)

        db.query(T_CaseApplicant).filter(T_CaseApplicant.case_id == case_id).delete()

        for applicant in data.applicants:
            db.add(
                T_CaseApplicant(
                    id=str(uuid4()),
                    case_id=case.id,
                    applicant_id=applicant.applicant_id,
                    seq=applicant.seq,
                    is_first=applicant.is_first,
                    name_cn=applicant.name_cn,
                    name_en=applicant.name_en,
                    address_cn=applicant.address_cn,
                    address_en=applicant.address_en,
                )
            )

    if data.inventors is not None:
        db.query(T_CaseInventor).filter(T_CaseInventor.case_id == case_id).delete()
        for inventor in data.inventors:
            db.add(
                T_CaseInventor(
                    id=str(uuid4()),
                    case_id=case.id,
                    seq=inventor.seq,
                    name_cn=inventor.name_cn,
                    name_en=inventor.name_en,
                )
            )

    if data.priorities is not None:
        priorities_dict = [priority.model_dump() for priority in data.priorities]
        validate_priorities(priorities_dict)
        db.query(T_Priority).filter(T_Priority.case_id == case_id).delete()
        for prio in data.priorities:
            db.add(
                T_Priority(
                    id=str(uuid4()),
                    case_id=case.id,
                    seq=prio.seq,
                    country_code=prio.country_code,
                    prio_no=prio.prio_no,
                    prio_date=prio.prio_date,
                )
            )

    if data.bio_deposits is not None:
        bio_deposits_dict = [bio_deposit.model_dump() for bio_deposit in data.bio_deposits]
        validate_bio_deposits(bio_deposits_dict)
        db.query(T_BioDeposit).filter(T_BioDeposit.case_id == case_id).delete()
        for bio_deposit in data.bio_deposits:
            db.add(
                T_BioDeposit(
                    id=str(uuid4()),
                    case_id=case.id,
                    seq=bio_deposit.seq,
                    deposit_no=bio_deposit.deposit_no,
                    deposit_unit_name=bio_deposit.deposit_unit_name,
                    deposit_date=bio_deposit.deposit_date,
                    name=bio_deposit.name,
                )
            )

    if data.agent_splits is not None:
        validate_case_agent_splits(db, data.agent_splits)
        db.query(T_CaseAgentSplit).filter(T_CaseAgentSplit.case_id == case_id).delete()
        for split in data.agent_splits:
            db.add(
                T_CaseAgentSplit(
                    id=str(uuid4()),
                    case_id=case.id,
                    agent_id=split.agent_id,
                    role=(split.role or "").strip() or None,
                    share_ratio=split.share_ratio,
                )
            )

    db.commit()
    db.refresh(case)
    return case


def update_case_limited(db: Session, case_id: str, data: CaseUpdateLimited, user_id: str) -> Case:
    """Limited update for Agent role - titles and inventors only."""
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise_business_error("CASE_NOT_FOUND", "Case not found", status_code=404)

    if data.title_cn is not None:
        case.title_cn = data.title_cn
    if data.title_en is not None:
        case.title_en = data.title_en
    # A3 — Spec details (Agent-editable)
    if data.spec_pages is not None:
        case.spec_pages = data.spec_pages
    if data.claim_count is not None:
        case.claim_count = data.claim_count

    case.updated_by = user_id

    if data.inventors is not None:
        db.query(T_CaseInventor).filter(T_CaseInventor.case_id == case_id).delete()
        for inventor in data.inventors:
            db.add(
                T_CaseInventor(
                    id=str(uuid4()),
                    case_id=case.id,
                    seq=inventor.seq,
                    name_cn=inventor.name_cn,
                    name_en=inventor.name_en,
                )
            )

    db.commit()
    db.refresh(case)
    return case
