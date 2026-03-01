from __future__ import annotations

from datetime import date
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.api.deps import require_perm
from app.core.errors import raise_business_error
from app.db.session import get_db
from app.modules.cases.models import Case
from app.modules.cases.schemas import CaseCreateIn
from app.modules.masterdata.clients.models import Client

router = APIRouter()


@router.get("/cases", summary="List cases")
def get_cases(
    q: str | None = Query(default=None),
    case_no: str | None = Query(default=None),
    app_no: str | None = Query(default=None),
    client_id: str | None = Query(default=None),
    status: str | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    case_type: str | None = Query(default=None),
    patent_category: str | None = Query(default=None),
    flow_dir: str | None = Query(default=None),
    filing_date_from: date | None = Query(default=None),
    filing_date_to: date | None = Query(default=None),
    primary_agent_id: str | None = Query(default=None),
    sort_by: str | None = Query(default=None),
    sort_dir: str = Query(default="asc"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    _perm: None = Depends(require_perm("Case.Read")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """
    List cases with filters and pagination.

    **Auth**: Bearer JWT
    **Permission**: Case.Read
    **Request example**:
    `GET /api/v1/cases?page=1&page_size=20&case_no=CURL_CASE_001`
    **Curl example**:
    ```bash
    curl -s -X GET "http://localhost:8000/api/v1/cases?page=1&page_size=20" \\
      -H "Authorization: Bearer $FPMS_TOKEN"
    ```
    **Responses**:
    - 200: List of cases
    - 401: AUTH_REQUIRED
    - 403: FORBIDDEN
    - 422: VALIDATION_ERROR
    """
    query = db.query(Case)

    if q:
        pattern = f"%{q}%"
        query = query.filter(
            or_(
                Case.case_no.ilike(pattern),
                Case.title_cn.ilike(pattern),
                Case.title_en.ilike(pattern),
                Case.app_no.ilike(pattern),
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

    total = query.count()

    sort_field = Case.case_no
    allowed_sort_fields = {
        "case_no": Case.case_no,
        "recv_date": Case.recv_date,
        "filing_date": Case.filing_date,
        "created_at": Case.created_at,
    }
    if sort_by in allowed_sort_fields:
        sort_field = allowed_sort_fields[sort_by]

    if sort_dir.lower() == "desc":
        query = query.order_by(sort_field.desc())
    else:
        query = query.order_by(sort_field.asc())

    cases = query.offset((page - 1) * page_size).limit(page_size).all()

    # Batch-resolve client names for all cases in this page
    client_ids = {case.client_id for case in cases if case.client_id}
    client_name_map: dict[str, str] = {}
    if client_ids:
        clients = db.query(Client.id, Client.name_cn).filter(Client.id.in_(client_ids)).all()
        client_name_map = {c.id: c.name_cn for c in clients}

    items = [
        {
            "id": case.id,
            "case_no": case.case_no,
            "case_type": case.case_type,
            "patent_category": case.patent_category,
            "client_id": case.client_id,
            "client_name": client_name_map.get(case.client_id) if case.client_id else None,
            "title_cn": case.title_cn,
            "title_en": case.title_en,
            "app_no": case.app_no,
            "status": case.status,
            "filing_date": str(case.filing_date) if case.filing_date else None,
            "recv_date": str(case.recv_date) if case.recv_date else None,
            "patent_no": case.patent_no,
            "primary_agent_id": case.primary_agent_id,
        }
        for case in cases
    ]

    return {"items": items, "page": page, "page_size": page_size, "total": total}


@router.post("/cases", status_code=status.HTTP_201_CREATED, summary="Create a case")
def create_case(
    payload: CaseCreateIn,
    _perm: None = Depends(require_perm("Case.Create")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """
    Create a case.

    **Auth**: Bearer JWT
    **Permission**: Case.Create
    **Request example**:
    ```json
    {
      "case_no": "CURL_CASE_001",
      "case_type": "NORMAL",
      "patent_category": "INV",
      "flow_dir": "CN_DOMESTIC",
      "client_id": "CLIENT_ID"
    }
    ```
    **Curl example**:
    ```bash
    curl -s -X POST http://localhost:8000/api/v1/cases \\
      -H "Authorization: Bearer $FPMS_TOKEN" \\
      -H "Content-Type: application/json" \\
      -d '{"case_no":"CURL_CASE_001","case_type":"NORMAL","patent_category":"INV","flow_dir":"CN_DOMESTIC","client_id":"CLIENT_ID"}'
    ```
    **Responses**:
    - 201: Case created
    - 400: case_no is required
    - 401: AUTH_REQUIRED
    - 403: FORBIDDEN
    - 409: case_no already exists
    - 422: VALIDATION_ERROR
    """
    case_no = payload.case_no
    if not case_no:
        raise_business_error(
            "CASE_INVALID",
            "case_no is required",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    exists = db.query(Case).filter(Case.case_no == case_no).first()
    if exists:
        raise_business_error(
            "CASE_NO_DUPLICATE",
            "case_no already exists",
            status_code=status.HTTP_409_CONFLICT,
        )

    from sqlalchemy import text as sa_text

    case = Case(
        id=str(uuid4()),
        case_no=case_no,
        case_type=payload.case_type or "NORMAL",
        patent_category=payload.patent_category or "INV",
        flow_dir=payload.flow_dir or "CN_DOMESTIC",
        client_id=payload.client_id,
        title_cn=payload.title_cn,
        title_en=payload.title_en,
        app_no=payload.app_no,
        # A3 — Publication / Grant
        pub_date=payload.pub_date,
        pub_no=payload.pub_no,
        grant_date=payload.grant_date,
        grant_no=payload.grant_no,
        patent_no=payload.patent_no,
        valid_until=payload.valid_until,
        # A3 — Spec details
        spec_pages=payload.spec_pages,
        claim_count=payload.claim_count,
        has_exam_request=payload.has_exam_request,
        # A3 — Agent assignment
        primary_agent_id=payload.primary_agent_id,
        second_agent_id=payload.second_agent_id,
        draftor_id=payload.draftor_id,
        # A3 — Control flags
        is_fee_monitor=payload.is_fee_monitor,
        fee_reduction=payload.fee_reduction,
        applicant_kind=payload.applicant_kind,
    )
    db.add(case)
    db.flush()

    # Use raw SQL for sub-tables to avoid AuditMixin column mismatch
    for applicant in payload.applicants:
        db.execute(
            sa_text(
                "INSERT INTO t_case_applicant"
                " (id, case_id, seq, is_first, name_cn, name_en, address_cn, address_en)"
                " VALUES (:id, :case_id, :seq, :is_first, :name_cn, :name_en,"
                " :address_cn, :address_en)"
            ),
            {
                "id": str(uuid4()),
                "case_id": case.id,
                "seq": applicant.seq,
                "is_first": applicant.is_first,
                "name_cn": applicant.name_cn,
                "name_en": applicant.name_en,
                "address_cn": applicant.address_cn,
                "address_en": applicant.address_en,
            },
        )

    for inventor in payload.inventors:
        db.execute(
            sa_text(
                "INSERT INTO t_case_inventor"
                " (id, case_id, seq, name_cn, name_en)"
                " VALUES (:id, :case_id, :seq, :name_cn, :name_en)"
            ),
            {
                "id": str(uuid4()),
                "case_id": case.id,
                "seq": inventor.seq,
                "name_cn": inventor.name_cn,
                "name_en": inventor.name_en,
            },
        )

    for prio in payload.priorities:
        db.execute(
            sa_text(
                "INSERT INTO t_priority"
                " (id, case_id, seq, country_code, prio_no, prio_date)"
                " VALUES (:id, :case_id, :seq, :country_code, :prio_no, :prio_date)"
            ),
            {
                "id": str(uuid4()),
                "case_id": case.id,
                "seq": prio.seq,
                "country_code": prio.country_code,
                "prio_no": prio.prio_no,
                "prio_date": prio.prio_date,
            },
        )

    db.commit()
    db.refresh(case)

    return {
        "id": case.id,
        "case_no": case.case_no,
        "case_type": case.case_type,
        "patent_category": case.patent_category,
        "flow_dir": case.flow_dir,
        "client_id": case.client_id,
        "title_cn": case.title_cn,
        "title_en": case.title_en,
        "app_no": case.app_no,
        "status": case.status,
        "pub_date": str(case.pub_date) if case.pub_date else None,
        "pub_no": case.pub_no,
        "grant_date": str(case.grant_date) if case.grant_date else None,
        "grant_no": case.grant_no,
        "patent_no": case.patent_no,
        "valid_until": str(case.valid_until) if case.valid_until else None,
        "spec_pages": case.spec_pages,
        "claim_count": case.claim_count,
        "has_exam_request": case.has_exam_request,
        "primary_agent_id": case.primary_agent_id,
        "second_agent_id": case.second_agent_id,
        "draftor_id": case.draftor_id,
        "is_fee_monitor": case.is_fee_monitor,
        "fee_reduction": case.fee_reduction,
        "applicant_kind": case.applicant_kind,
    }


@router.post("/cases/{case_id}/limited-edit", summary="Limited edit of a case")
def limited_edit_case(
    case_id: str,
    payload: dict[str, Any],
    _perm: None = Depends(require_perm("Case.EditLimited")),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    """
    Limited edit for a case (title fields only).

    **Auth**: Bearer JWT
    **Permission**: Case.EditLimited
    **Request example**:
    ```json
    {"title_cn": "新标题", "title_en": "New Title"}
    ```
    **Curl example**:
    ```bash
    curl -s -X POST http://localhost:8000/api/v1/cases/CASE_ID/limited-edit \\
      -H "Authorization: Bearer $FPMS_TOKEN" \\
      -H "Content-Type: application/json" \\
      -d '{"title_cn":"新标题","title_en":"New Title"}'
    ```
    **Responses**:
    - 200: Updated
    - 401: AUTH_REQUIRED
    - 403: FORBIDDEN
    - 404: Case not found
    - 422: VALIDATION_ERROR
    """
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise_business_error(
            "CASE_NOT_FOUND",
            "Case not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    if "title_cn" in payload:
        case.title_cn = payload.get("title_cn")
    if "title_en" in payload:
        case.title_en = payload.get("title_en")
    # A3 — Spec details (Agent-editable)
    if "spec_pages" in payload:
        case.spec_pages = payload.get("spec_pages")
    if "claim_count" in payload:
        case.claim_count = payload.get("claim_count")

    db.commit()
    return {"status": "ok"}


@router.get("/cases/export", summary="Export cases (filtered list)")
def export_cases(
    q: str | None = Query(default=None),
    case_no: str | None = Query(default=None),
    app_no: str | None = Query(default=None),
    client_id: str | None = Query(default=None),
    status: str | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    case_type: str | None = Query(default=None),
    patent_category: str | None = Query(default=None),
    flow_dir: str | None = Query(default=None),
    filing_date_from: date | None = Query(default=None),
    filing_date_to: date | None = Query(default=None),
    primary_agent_id: str | None = Query(default=None),
    sort_by: str | None = Query(default=None),
    sort_dir: str = Query(default="asc"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    _perm: None = Depends(require_perm("Case.Export")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """
    Export cases with filters and pagination.

    **Auth**: Bearer JWT
    **Permission**: Case.Export
    **Request example**:
    `GET /api/v1/cases/export?page=1&page_size=20&status=NOT_FILED`
    **Curl example**:
    ```bash
    curl -s -X GET "http://localhost:8000/api/v1/cases/export?page=1&page_size=20" \\
      -H "Authorization: Bearer $FPMS_TOKEN"
    ```
    **Responses**:
    - 200: Exported list
    - 401: AUTH_REQUIRED
    - 403: FORBIDDEN
    - 422: VALIDATION_ERROR
    """
    query = db.query(Case)

    if q:
        pattern = f"%{q}%"
        query = query.filter(
            or_(
                Case.case_no.ilike(pattern),
                Case.title_cn.ilike(pattern),
                Case.title_en.ilike(pattern),
                Case.app_no.ilike(pattern),
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

    total = query.count()

    sort_field = Case.case_no
    allowed_sort_fields = {
        "case_no": Case.case_no,
        "recv_date": Case.recv_date,
        "filing_date": Case.filing_date,
        "created_at": Case.created_at,
    }
    if sort_by in allowed_sort_fields:
        sort_field = allowed_sort_fields[sort_by]

    if sort_dir.lower() == "desc":
        query = query.order_by(sort_field.desc())
    else:
        query = query.order_by(sort_field.asc())

    cases = query.offset((page - 1) * page_size).limit(page_size).all()

    # Batch-resolve client names for all cases in this page
    client_ids = {case.client_id for case in cases if case.client_id}
    client_name_map: dict[str, str] = {}
    if client_ids:
        clients = db.query(Client.id, Client.name_cn).filter(Client.id.in_(client_ids)).all()
        client_name_map = {c.id: c.name_cn for c in clients}

    items = [
        {
            "id": case.id,
            "case_no": case.case_no,
            "case_type": case.case_type,
            "patent_category": case.patent_category,
            "client_id": case.client_id,
            "client_name": client_name_map.get(case.client_id) if case.client_id else None,
            "title_cn": case.title_cn,
            "title_en": case.title_en,
            "app_no": case.app_no,
            "status": case.status,
            "filing_date": str(case.filing_date) if case.filing_date else None,
            "recv_date": str(case.recv_date) if case.recv_date else None,
            "patent_no": case.patent_no,
            "primary_agent_id": case.primary_agent_id,
        }
        for case in cases
    ]

    return {"items": items, "page": page, "page_size": page_size, "total": total}


@router.put("/cases/{case_id}", summary="Update a case")
def update_case(
    case_id: str,
    payload: dict[str, Any],
    _perm: None = Depends(require_perm("Case.Edit")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """
    Update case fields.

    **Auth**: Bearer JWT
    **Permission**: Case.Edit
    **Request example**:
    ```json
    {"case_no": "CURL_CASE_002", "case_type": "NORMAL"}
    ```
    **Curl example**:
    ```bash
    curl -s -X PUT http://localhost:8000/api/v1/cases/CASE_ID \\
      -H "Authorization: Bearer $FPMS_TOKEN" \\
      -H "Content-Type: application/json" \\
      -d '{"case_no":"CURL_CASE_002","case_type":"NORMAL"}'
    ```
    **Responses**:
    - 200: Case updated
    - 400: case_no already exists
    - 401: AUTH_REQUIRED
    - 403: FORBIDDEN
    - 404: Case not found
    - 422: VALIDATION_ERROR
    """
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise_business_error(
            "CASE_NOT_FOUND",
            "Case not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    new_case_no = payload.get("case_no")
    if new_case_no and new_case_no != case.case_no:
        exists = db.query(Case).filter(Case.case_no == new_case_no, Case.id != case_id).first()
        if exists:
            raise_business_error(
                "CASE_NO_DUPLICATE",
                "case_no already exists",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        case.case_no = new_case_no

    case.case_type = payload.get("case_type", case.case_type)
    case.patent_category = payload.get("patent_category", case.patent_category)
    case.flow_dir = payload.get("flow_dir", case.flow_dir)
    case.client_id = payload.get("client_id", case.client_id)

    # A3 — new scalar fields (only update if key present)
    if "title_cn" in payload:
        case.title_cn = payload["title_cn"]
    if "title_en" in payload:
        case.title_en = payload["title_en"]
    if "app_no" in payload:
        case.app_no = payload["app_no"]
    if "status" in payload:
        case.status = payload["status"]
    if "pub_date" in payload:
        v = payload["pub_date"]
        case.pub_date = date.fromisoformat(v) if isinstance(v, str) else v
    if "pub_no" in payload:
        case.pub_no = payload["pub_no"]
    if "grant_date" in payload:
        v = payload["grant_date"]
        case.grant_date = date.fromisoformat(v) if isinstance(v, str) else v
    if "grant_no" in payload:
        case.grant_no = payload["grant_no"]
    if "patent_no" in payload:
        case.patent_no = payload["patent_no"]
    if "valid_until" in payload:
        v = payload["valid_until"]
        case.valid_until = date.fromisoformat(v) if isinstance(v, str) else v
    if "spec_pages" in payload:
        case.spec_pages = payload["spec_pages"]
    if "claim_count" in payload:
        case.claim_count = payload["claim_count"]
    if "has_exam_request" in payload:
        case.has_exam_request = payload["has_exam_request"]
    if "primary_agent_id" in payload:
        case.primary_agent_id = payload["primary_agent_id"]
    if "second_agent_id" in payload:
        case.second_agent_id = payload["second_agent_id"]
    if "draftor_id" in payload:
        case.draftor_id = payload["draftor_id"]
    if "is_fee_monitor" in payload:
        case.is_fee_monitor = payload["is_fee_monitor"]
    if "fee_reduction" in payload:
        case.fee_reduction = payload["fee_reduction"]
    if "applicant_kind" in payload:
        case.applicant_kind = payload["applicant_kind"]

    db.commit()
    db.refresh(case)

    return {
        "id": case.id,
        "case_no": case.case_no,
        "case_type": case.case_type,
        "patent_category": case.patent_category,
        "flow_dir": case.flow_dir,
        "client_id": case.client_id,
        "title_cn": case.title_cn,
        "title_en": case.title_en,
        "app_no": case.app_no,
        "status": case.status,
        "pub_date": str(case.pub_date) if case.pub_date else None,
        "pub_no": case.pub_no,
        "grant_date": str(case.grant_date) if case.grant_date else None,
        "grant_no": case.grant_no,
        "patent_no": case.patent_no,
        "valid_until": str(case.valid_until) if case.valid_until else None,
        "spec_pages": case.spec_pages,
        "claim_count": case.claim_count,
        "has_exam_request": case.has_exam_request,
        "primary_agent_id": case.primary_agent_id,
        "second_agent_id": case.second_agent_id,
        "draftor_id": case.draftor_id,
        "is_fee_monitor": case.is_fee_monitor,
        "fee_reduction": case.fee_reduction,
        "applicant_kind": case.applicant_kind,
    }


@router.get("/cases/{case_id}", summary="Get case by ID")
def get_case(
    case_id: str,
    _perm: None = Depends(require_perm("Case.Read")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """
    Get a case by ID.

    **Auth**: Bearer JWT
    **Permission**: Case.Read
    **Request example**:
    `GET /api/v1/cases/CASE_ID`
    **Curl example**:
    ```bash
    curl -s -X GET http://localhost:8000/api/v1/cases/CASE_ID \\
      -H "Authorization: Bearer $FPMS_TOKEN"
    ```
    **Responses**:
    - 200: Case details
    - 401: AUTH_REQUIRED
    - 403: FORBIDDEN
    - 404: Case not found
    - 422: VALIDATION_ERROR
    """
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise_business_error(
            "CASE_NOT_FOUND",
            "Case not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    # Resolve client name
    client_name = None
    if case.client_id:
        client = db.query(Client.name_cn).filter(Client.id == case.client_id).first()
        if client:
            client_name = client.name_cn

    # Resolve applicants, inventors, priorities
    from app.modules.cases.models import T_CaseApplicant, T_CaseInventor, T_Priority

    applicants = (
        db.query(
            T_CaseApplicant.seq,
            T_CaseApplicant.is_first,
            T_CaseApplicant.name_cn,
            T_CaseApplicant.name_en,
            T_CaseApplicant.address_cn,
            T_CaseApplicant.address_en,
        )
        .filter(T_CaseApplicant.case_id == case_id)
        .order_by(T_CaseApplicant.seq)
        .all()
    )
    inventors = (
        db.query(
            T_CaseInventor.seq,
            T_CaseInventor.name_cn,
            T_CaseInventor.name_en,
        )
        .filter(T_CaseInventor.case_id == case_id)
        .order_by(T_CaseInventor.seq)
        .all()
    )
    priorities = (
        db.query(
            T_Priority.seq,
            T_Priority.country_code,
            T_Priority.prio_no,
            T_Priority.prio_date,
        )
        .filter(T_Priority.case_id == case_id)
        .order_by(T_Priority.seq)
        .all()
    )

    return {
        "id": case.id,
        "case_no": case.case_no,
        "case_type": case.case_type,
        "patent_category": case.patent_category,
        "flow_dir": case.flow_dir,
        "client_id": case.client_id,
        "client_name": client_name,
        "title_cn": case.title_cn,
        "title_en": case.title_en,
        "app_no": case.app_no,
        "status": case.status,
        "filing_date": str(case.filing_date) if case.filing_date else None,
        "recv_date": str(case.recv_date) if case.recv_date else None,
        # A3 — Publication / Grant
        "pub_date": str(case.pub_date) if case.pub_date else None,
        "pub_no": case.pub_no,
        "grant_date": str(case.grant_date) if case.grant_date else None,
        "grant_no": case.grant_no,
        "patent_no": case.patent_no,
        "valid_until": str(case.valid_until) if case.valid_until else None,
        # A3 — Spec details
        "spec_pages": case.spec_pages,
        "claim_count": case.claim_count,
        "has_exam_request": case.has_exam_request,
        # A3 — Agent assignment
        "primary_agent_id": case.primary_agent_id,
        "second_agent_id": case.second_agent_id,
        "draftor_id": case.draftor_id,
        # A3 — Control flags
        "is_fee_monitor": case.is_fee_monitor,
        "fee_reduction": case.fee_reduction,
        "applicant_kind": case.applicant_kind,
        # Sub-tables
        "applicants": [
            {
                "seq": a.seq,
                "is_first": a.is_first,
                "name_cn": a.name_cn,
                "name_en": a.name_en,
                "address_cn": a.address_cn,
                "address_en": a.address_en,
            }
            for a in applicants
        ],
        "inventors": [
            {"seq": i.seq, "name_cn": i.name_cn, "name_en": i.name_en} for i in inventors
        ],
        "priorities": [
            {
                "seq": p.seq,
                "country_code": p.country_code,
                "prio_no": p.prio_no,
                "prio_date": str(p.prio_date) if p.prio_date else None,
            }
            for p in priorities
        ],
        "created_at": str(case.created_at) if case.created_at else None,
        "updated_at": str(case.updated_at) if case.updated_at else None,
    }
