from __future__ import annotations

from datetime import date
from uuid import uuid4

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.errors import raise_business_error
from app.core.pagination import PageResult, offset_limit
from app.modules.cases.enums import CaseType
from app.modules.cases.models import Case, T_CaseApplicant, T_CaseInventor, T_Priority
from app.modules.cases.schemas import (
    CaseCreate,
    CaseListItem,
    CaseUpdateFull,
    CaseUpdateLimited,
)

_CONSULTING_CASE_TYPES = {CaseType.CONSULTING.value, CaseType.SEARCH.value}


def _normalize_required_text(value: str | None, field_name: str) -> str:
    normalized = (value or "").strip()
    if not normalized:
        raise_business_error(
            "CONSULTING_CASE_INVALID",
            f"{field_name} is required",
            status_code=400,
        )
    return normalized


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


def list_cases(
    db: Session,
    q: str | None = None,
    client_id: str | None = None,
    status: str | None = None,
    case_type: str | None = None,
    patent_category: str | None = None,
    flow_dir: str | None = None,
    filing_date_from: date | None = None,
    filing_date_to: date | None = None,
    primary_agent_id: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> PageResult[CaseListItem]:
    """List cases with pagination and filters."""
    query = db.query(Case)

    if q:
        query = query.filter(
            or_(
                Case.case_no.contains(q),
                Case.title_cn.contains(q),
                Case.title_en.contains(q),
                Case.app_no.contains(q),
            )
        )

    if client_id:
        query = query.filter(Case.client_id == client_id)
    if status:
        query = query.filter(Case.status == status)
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

    total = query.count()

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

    return PageResult(items=list_items, page=page, page_size=page_size, total=total)


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
    validate_applicants(applicants_dict)

    case = Case(
        id=str(uuid4()),
        case_no=data.case_no,
        case_type=data.case_type,
        patent_category=data.patent_category,
        flow_dir=data.flow_dir,
        client_id=data.client_id,
        title_cn=data.title_cn,
        title_en=data.title_en,
        app_no=data.app_no,
        status="NOT_FILED",
        # A3 — Publication / Grant
        pub_date=data.pub_date,
        pub_no=data.pub_no,
        grant_date=data.grant_date,
        grant_no=data.grant_no,
        patent_no=data.patent_no,
        valid_until=data.valid_until,
        # A3 — Spec details
        spec_pages=data.spec_pages,
        claim_count=data.claim_count,
        has_exam_request=data.has_exam_request,
        # A3 — Agent assignment
        primary_agent_id=data.primary_agent_id,
        second_agent_id=data.second_agent_id,
        draftor_id=data.draftor_id,
        # A3 — Control flags
        is_fee_monitor=data.is_fee_monitor,
        fee_reduction=data.fee_reduction,
        applicant_kind=data.applicant_kind,
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

    if data.title_cn is not None:
        case.title_cn = data.title_cn
    if data.title_en is not None:
        case.title_en = data.title_en
    if data.app_no is not None:
        case.app_no = data.app_no
    if data.status is not None:
        case.status = data.status
    # A3 — Publication / Grant
    if data.pub_date is not None:
        case.pub_date = data.pub_date
    if data.pub_no is not None:
        case.pub_no = data.pub_no
    if data.grant_date is not None:
        case.grant_date = data.grant_date
    if data.grant_no is not None:
        case.grant_no = data.grant_no
    if data.patent_no is not None:
        case.patent_no = data.patent_no
    if data.valid_until is not None:
        case.valid_until = data.valid_until
    # A3 — Spec details
    if data.spec_pages is not None:
        case.spec_pages = data.spec_pages
    if data.claim_count is not None:
        case.claim_count = data.claim_count
    if data.has_exam_request is not None:
        case.has_exam_request = data.has_exam_request
    # A3 — Agent assignment
    if data.primary_agent_id is not None:
        case.primary_agent_id = data.primary_agent_id
    if data.second_agent_id is not None:
        case.second_agent_id = data.second_agent_id
    if data.draftor_id is not None:
        case.draftor_id = data.draftor_id
    # A3 — Control flags
    if data.is_fee_monitor is not None:
        case.is_fee_monitor = data.is_fee_monitor
    if data.fee_reduction is not None:
        case.fee_reduction = data.fee_reduction
    if data.applicant_kind is not None:
        case.applicant_kind = data.applicant_kind

    case.updated_by = user_id

    if data.applicants is not None:
        applicants_dict = [applicant.model_dump() for applicant in data.applicants]
        validate_applicants(applicants_dict)

        db.query(T_CaseApplicant).filter(T_CaseApplicant.case_id == case_id).delete()

        for applicant in data.applicants:
            db.add(
                T_CaseApplicant(
                    id=str(uuid4()),
                    case_id=case.id,
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
