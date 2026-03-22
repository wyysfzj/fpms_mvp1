from __future__ import annotations

from datetime import date
from typing import Any

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.api.deps import current_user_dep, require_perm
from app.core.errors import raise_business_error
from app.db.session import get_db
from app.modules.auth.models import T_User
from app.modules.cases.models import Case, T_BioDeposit, T_CaseApplicant, T_CaseInventor, T_Priority
from app.modules.cases.schemas import CaseCreateIn, CaseUpdateFull
from app.modules.cases.service import (
    create_case as create_case_service,
)
from app.modules.cases.service import (
    update_case_full as update_case_full_service,
)
from app.modules.masterdata.clients.models import Client

router = APIRouter()


def _serialize_case(db: Session, case: Case) -> dict[str, Any]:
    client_names = {}
    related_client_ids = {case.client_id, case.foreign_agent_id, case.invalid_client_id}
    related_client_ids = {client_id for client_id in related_client_ids if client_id}
    if related_client_ids:
        clients = (
            db.query(Client.id, Client.name_cn).filter(Client.id.in_(related_client_ids)).all()
        )
        client_names = {client.id: client.name_cn for client in clients}

    applicants = (
        db.query(
            T_CaseApplicant.seq,
            T_CaseApplicant.is_first,
            T_CaseApplicant.name_cn,
            T_CaseApplicant.name_en,
            T_CaseApplicant.address_cn,
            T_CaseApplicant.address_en,
        )
        .filter(T_CaseApplicant.case_id == case.id)
        .order_by(T_CaseApplicant.seq)
        .all()
    )
    inventors = (
        db.query(
            T_CaseInventor.seq,
            T_CaseInventor.name_cn,
            T_CaseInventor.name_en,
        )
        .filter(T_CaseInventor.case_id == case.id)
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
        .filter(T_Priority.case_id == case.id)
        .order_by(T_Priority.seq)
        .all()
    )
    bio_deposits = (
        db.query(
            T_BioDeposit.seq,
            T_BioDeposit.deposit_no,
            T_BioDeposit.deposit_unit_name,
            T_BioDeposit.deposit_date,
            T_BioDeposit.name,
        )
        .filter(T_BioDeposit.case_id == case.id)
        .order_by(T_BioDeposit.seq)
        .all()
    )

    return {
        "id": case.id,
        "case_no": case.case_no,
        "case_type": case.case_type,
        "patent_category": case.patent_category,
        "flow_dir": case.flow_dir,
        "client_id": case.client_id,
        "client_name": client_names.get(case.client_id) if case.client_id else None,
        "foreign_agent_id": case.foreign_agent_id,
        "foreign_agent_name": (
            client_names.get(case.foreign_agent_id) if case.foreign_agent_id else None
        ),
        "foreign_ref": case.foreign_ref,
        "title_cn": case.title_cn,
        "title_en": case.title_en,
        "app_no": case.app_no,
        "status": case.status,
        "filing_date": str(case.filing_date) if case.filing_date else None,
        "recv_date": str(case.recv_date) if case.recv_date else None,
        "pub_date": str(case.pub_date) if case.pub_date else None,
        "pub_no": case.pub_no,
        "grant_date": str(case.grant_date) if case.grant_date else None,
        "grant_no": case.grant_no,
        "patent_no": case.patent_no,
        "valid_until": str(case.valid_until) if case.valid_until else None,
        "spec_pages": case.spec_pages,
        "claim_count": case.claim_count,
        "has_exam_request": case.has_exam_request,
        "ro": case.ro,
        "isa": case.isa,
        "ipea": case.ipea,
        "intl_app_no": case.intl_app_no,
        "intl_app_date": str(case.intl_app_date) if case.intl_app_date else None,
        "intl_pub_no": case.intl_pub_no,
        "intl_pub_date": str(case.intl_pub_date) if case.intl_pub_date else None,
        "intl_pub_lang": case.intl_pub_lang,
        "need_iper": case.need_iper,
        "iper_date": str(case.iper_date) if case.iper_date else None,
        "pct_national_entry_date": (
            str(case.pct_national_entry_date) if case.pct_national_entry_date else None
        ),
        "original_case_id": case.original_case_id,
        "invalid_client_id": case.invalid_client_id,
        "invalid_client_name": (
            client_names.get(case.invalid_client_id) if case.invalid_client_id else None
        ),
        "invalid_patentee": case.invalid_patentee,
        "invalid_requester": case.invalid_requester,
        "invalid_role": case.invalid_role,
        "primary_agent_id": case.primary_agent_id,
        "second_agent_id": case.second_agent_id,
        "draftor_id": case.draftor_id,
        "is_fee_monitor": case.is_fee_monitor,
        "fee_reduction": case.fee_reduction,
        "applicant_kind": case.applicant_kind,
        "applicants": [
            {
                "seq": applicant.seq,
                "is_first": applicant.is_first,
                "name_cn": applicant.name_cn,
                "name_en": applicant.name_en,
                "address_cn": applicant.address_cn,
                "address_en": applicant.address_en,
            }
            for applicant in applicants
        ],
        "inventors": [
            {
                "seq": inventor.seq,
                "name_cn": inventor.name_cn,
                "name_en": inventor.name_en,
            }
            for inventor in inventors
        ],
        "priorities": [
            {
                "seq": priority.seq,
                "country_code": priority.country_code,
                "prio_no": priority.prio_no,
                "prio_date": str(priority.prio_date) if priority.prio_date else None,
            }
            for priority in priorities
        ],
        "bio_deposits": [
            {
                "seq": bio_deposit.seq,
                "deposit_no": bio_deposit.deposit_no,
                "deposit_unit_name": bio_deposit.deposit_unit_name,
                "deposit_date": str(bio_deposit.deposit_date) if bio_deposit.deposit_date else None,
                "name": bio_deposit.name,
            }
            for bio_deposit in bio_deposits
        ],
        "created_at": str(case.created_at) if case.created_at else None,
        "updated_at": str(case.updated_at) if case.updated_at else None,
    }


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
    current_user: T_User = current_user_dep,
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
    case = create_case_service(db, payload, current_user.id)
    return _serialize_case(db, case)


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
    payload: CaseUpdateFull,
    _perm: None = Depends(require_perm("Case.Edit")),
    current_user: T_User = current_user_dep,
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
    case = update_case_full_service(db, case_id, payload, current_user.id)
    return _serialize_case(db, case)


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

    return _serialize_case(db, case)
