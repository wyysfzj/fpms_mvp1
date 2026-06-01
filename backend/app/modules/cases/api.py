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
from app.modules.cases.document_gate_service import (
    GateCaseContext,
    GateDocumentInput,
    MaterialGateResult,
    evaluate_material_gate,
)
from app.modules.cases.models import (
    Case,
    T_BioDeposit,
    T_CaseAgentSplit,
    T_CaseApplicant,
    T_CaseInventor,
    T_Priority,
)
from app.modules.cases.schemas import (
    CaseBatchFilingActionIn,
    CaseCreateIn,
    CaseDocumentGateCheckOut,
    CaseDocumentGateFileEventOut,
    CaseDocumentGateMatchedDocumentOut,
    CaseDocumentGateMissingItemOut,
    CaseDocumentGatePreviewOut,
    CaseListReportResponse,
    CaseUpdateFull,
    CaseUpdateLimited,
)
from app.modules.cases.service import (
    create_case as create_case_service,
)
from app.modules.cases.service import (
    execute_batch_filing as execute_batch_filing_service,
)
from app.modules.cases.service import (
    list_batch_filing_candidates as list_batch_filing_candidates_service,
)
from app.modules.cases.service import (
    list_cases as list_cases_report_service,
)
from app.modules.cases.service import (
    update_case_full as update_case_full_service,
)
from app.modules.cases.service import (
    update_case_limited as update_case_limited_service,
)
from app.modules.documents.models import DocTemplate, Document
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
            T_CaseApplicant.nationality,
            T_CaseApplicant.certificate_type,
            T_CaseApplicant.certificate_no,
            T_CaseApplicant.official_postcode,
            T_CaseApplicant.official_applicant_kind,
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
            T_CaseInventor.nationality,
            T_CaseInventor.china_id_no,
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
    agent_splits = (
        db.query(
            T_CaseAgentSplit.agent_id,
            T_CaseAgentSplit.role,
            T_CaseAgentSplit.share_ratio,
        )
        .filter(T_CaseAgentSplit.case_id == case.id)
        .order_by(T_CaseAgentSplit.created_at, T_CaseAgentSplit.id)
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
        "from_country": case.from_country,
        "to_country": case.to_country,
        "doc_address_id": case.doc_address_id,
        "bill_address_id": case.bill_address_id,
        "title_cn": case.title_cn,
        "title_en": case.title_en,
        "app_no": case.app_no,
        "status": case.status,
        "filing_date": str(case.filing_date) if case.filing_date else None,
        "recv_date": str(case.recv_date) if case.recv_date else None,
        "pub_date": str(case.pub_date) if case.pub_date else None,
        "pub_no": case.pub_no,
        "issue_date": str(case.issue_date) if case.issue_date else None,
        "grant_date": str(case.grant_date) if case.grant_date else None,
        "grant_no": case.grant_no,
        "cert_no": case.cert_no,
        "patent_no": case.patent_no,
        "valid_until": str(case.valid_until) if case.valid_until else None,
        "spec_pages": case.spec_pages,
        "draw_pages": case.draw_pages,
        "claim_count": case.claim_count,
        "claim_pages": case.claim_pages,
        "manuscript_words": case.manuscript_words,
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
        "discount_rate": str(case.discount_rate) if case.discount_rate is not None else None,
        "no_power": case.no_power,
        "no_prio_text": case.no_prio_text,
        "require_hk": case.require_hk,
        "first_annuity_year": case.first_annuity_year,
        "agent_splits": [
            {
                "agent_id": agent_split.agent_id,
                "role": agent_split.role,
                "share_ratio": str(agent_split.share_ratio),
            }
            for agent_split in agent_splits
        ],
        "applicants": [
            {
                "seq": applicant.seq,
                "is_first": applicant.is_first,
                "name_cn": applicant.name_cn,
                "name_en": applicant.name_en,
                "address_cn": applicant.address_cn,
                "address_en": applicant.address_en,
                "nationality": applicant.nationality,
                "certificate_type": applicant.certificate_type,
                "certificate_no": applicant.certificate_no,
                "official_postcode": applicant.official_postcode,
                "official_applicant_kind": applicant.official_applicant_kind,
            }
            for applicant in applicants
        ],
        "inventors": [
            {
                "seq": inventor.seq,
                "name_cn": inventor.name_cn,
                "name_en": inventor.name_en,
                "nationality": inventor.nationality,
                "china_id_no": inventor.china_id_no,
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


def _load_gate_documents(
    db: Session,
    source_document_ids: list[str] | None,
) -> list[GateDocumentInput]:
    if not source_document_ids:
        return []

    unique_document_ids = list(dict.fromkeys(source_document_ids))
    rows = (
        db.query(Document, DocTemplate.code)
        .outerjoin(DocTemplate, Document.doc_template_id == DocTemplate.id)
        .filter(Document.id.in_(unique_document_ids))
        .all()
    )
    row_by_document_id = {
        document.id: (document, template_code) for document, template_code in rows
    }
    missing_document_ids = [
        document_id for document_id in unique_document_ids if document_id not in row_by_document_id
    ]
    if missing_document_ids:
        raise_business_error(
            "CASE_DOCUMENT_GATE_SOURCE_NOT_FOUND",
            "One or more source documents do not exist",
            details={"source_document_ids": missing_document_ids},
            status_code=status.HTTP_404_NOT_FOUND,
        )

    return [
        GateDocumentInput(
            id=document.id,
            title=document.title,
            doc_type=document.doc_type,
            direction=document.direction,
            template_code=template_code,
            has_attachment=True,
            extra_data=document.extra_data,
        )
        for document_id in unique_document_ids
        for document, template_code in [row_by_document_id[document_id]]
    ]


def _load_case_gate_documents(db: Session, case_id: str) -> list[GateDocumentInput]:
    rows = (
        db.query(Document, DocTemplate.code)
        .outerjoin(DocTemplate, Document.doc_template_id == DocTemplate.id)
        .filter(Document.case_id == case_id)
        .order_by(Document.doc_date.asc(), Document.created_at.asc(), Document.id.asc())
        .all()
    )
    return [
        GateDocumentInput(
            id=document.id,
            title=document.title,
            doc_type=document.doc_type,
            direction=document.direction,
            template_code=template_code,
            has_attachment=True,
            extra_data=document.extra_data,
        )
        for document, template_code in rows
    ]


def _document_event_status(document: Document) -> str:
    if document.reply_to_id:
        return "REPLY_FILE"
    if document.reply_date:
        return "REPLIED"
    if document.need_reply:
        return "NEED_REPLY"
    if document.outgoing_reg_no:
        return "MAILED"
    return "REGISTERED"


def _build_case_document_file_events(
    db: Session, case_id: str
) -> list[CaseDocumentGateFileEventOut]:
    documents = (
        db.query(Document)
        .filter(Document.case_id == case_id)
        .order_by(Document.doc_date.asc(), Document.created_at.asc(), Document.id.asc())
        .all()
    )
    return [
        CaseDocumentGateFileEventOut(
            document_id=document.id,
            title=document.title,
            doc_type=document.doc_type,
            direction=document.direction,
            event_status=_document_event_status(document),
            need_reply=document.need_reply,
            reply_date=str(document.reply_date) if document.reply_date else None,
            reply_to_id=document.reply_to_id,
        )
        for document in documents
    ]


def _build_document_gate_preview_out(
    *,
    case_type: str,
    patent_category: str,
    flow_dir: str,
    gate: MaterialGateResult,
    file_events: list[CaseDocumentGateFileEventOut] | None = None,
) -> CaseDocumentGatePreviewOut:
    return CaseDocumentGatePreviewOut(
        case_type=case_type,
        patent_category=patent_category,
        flow_dir=flow_dir,
        conclusion=gate.conclusion.value,
        hard_block=gate.hard_block,
        afterfill_audit_required=gate.afterfill_audit_required,
        material_count=gate.material_count,
        checks=[
            CaseDocumentGateCheckOut(
                requirement_code=check.requirement_code,
                requirement_name=check.requirement_name,
                role=check.role,
                blocks_submission=check.blocks_submission,
                afterfill_allowed=check.afterfill_allowed,
                status="MATCHED" if check.matched_documents else "MISSING",
                matched_documents=[
                    CaseDocumentGateMatchedDocumentOut(
                        id=document.id,
                        title=document.title,
                        doc_type=document.doc_type,
                        template_code=document.template_code,
                    )
                    for document in check.matched_documents
                ],
            )
            for check in gate.checks
        ],
        missing_items=[
            CaseDocumentGateMissingItemOut(
                requirement_code=item.requirement_code,
                requirement_name=item.requirement_name,
                role=item.role,
                blocks_submission=item.blocks_submission,
                afterfill_allowed=item.afterfill_allowed,
            )
            for item in gate.missing_items
        ],
        file_events=file_events or [],
        suggested_actions=gate.suggested_actions,
    )


@router.get("/cases", summary="List cases", response_model=CaseListReportResponse)
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
    country: str | None = Query(default=None),
    agent_id: str | None = Query(default=None),
    applicant_id: str | None = Query(default=None),
    patent_no: str | None = Query(default=None),
    fee_status: str | None = Query(default=None),
    sort_by: str | None = Query(default=None),
    sort_dir: str = Query(default="asc"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    _perm: None = Depends(require_perm("Case.Read")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    result = list_cases_report_service(
        db,
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
        page=page,
        page_size=page_size,
    )
    return result.model_dump()


@router.get("/cases/batch-filing/candidates", summary="List batch filing candidates")
def get_batch_filing_candidates(
    case_type: str | None = Query(default=None),
    flow_dir: str | None = Query(default=None),
    status: str = Query(default="NOT_FILED"),
    recv_date_from: date | None = Query(default=None),
    recv_date_to: date | None = Query(default=None),
    client_id: str | None = Query(default=None),
    primary_agent_id: str | None = Query(default=None),
    patent_category: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    _perm: None = Depends(require_perm("Case.Read")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    result = list_batch_filing_candidates_service(
        db,
        case_type=case_type,
        flow_dir=flow_dir,
        status=status,
        recv_date_from=recv_date_from,
        recv_date_to=recv_date_to,
        client_id=client_id,
        primary_agent_id=primary_agent_id,
        patent_category=patent_category,
        page=page,
        page_size=page_size,
    )
    return result.model_dump()


@router.post("/cases/batch-filing/submit", summary="Execute batch filing action")
def submit_batch_filing(
    payload: CaseBatchFilingActionIn,
    _perm: None = Depends(require_perm("Case.Edit")),
    current_user: T_User = current_user_dep,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    result = execute_batch_filing_service(
        db,
        selected_case_ids=payload.selected_case_ids,
        submitted_date=payload.submitted_date,
        apply_exam_now=payload.apply_exam_now,
        generate_list=payload.generate_list,
        user_id=current_user.id,
    )
    return result.model_dump()


@router.get(
    "/cases/document-gate/intake-preview",
    response_model=CaseDocumentGatePreviewOut,
    summary="Preview intake document material gate",
)
def preview_case_intake_document_gate(
    case_type: str = Query(default="NORMAL"),
    patent_category: str = Query(default="INV"),
    flow_dir: str = Query(default="CN_DOMESTIC"),
    has_exam_request: bool | None = Query(default=None),
    no_power: bool | None = Query(default=None),
    has_priority: bool | None = Query(default=None),
    source_document_ids: list[str] | None = Query(default=None),
    _perm: None = Depends(require_perm("Case.Read")),
    db: Session = Depends(get_db),
) -> CaseDocumentGatePreviewOut:
    documents = _load_gate_documents(db, source_document_ids)
    gate = evaluate_material_gate(
        GateCaseContext(
            case_type=case_type,
            patent_category=patent_category,
            flow_dir=flow_dir,
            has_exam_request=has_exam_request,
            no_power=no_power,
            has_priority=has_priority,
        ),
        documents=documents,
    )
    return _build_document_gate_preview_out(
        case_type=case_type,
        patent_category=patent_category,
        flow_dir=flow_dir,
        gate=gate,
    )


@router.get(
    "/cases/{case_id}/document-gate",
    response_model=CaseDocumentGatePreviewOut,
    summary="Get case document material gate",
)
def get_case_document_gate(
    case_id: str,
    _perm: None = Depends(require_perm("Case.Read")),
    db: Session = Depends(get_db),
) -> CaseDocumentGatePreviewOut:
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise_business_error(
            "CASE_NOT_FOUND",
            "Case not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    has_priority = db.query(T_Priority.id).filter(T_Priority.case_id == case.id).first() is not None
    gate = evaluate_material_gate(
        GateCaseContext(
            case_type=case.case_type,
            patent_category=case.patent_category,
            flow_dir=case.flow_dir,
            has_exam_request=case.has_exam_request,
            no_power=case.no_power,
            has_priority=has_priority,
        ),
        documents=_load_case_gate_documents(db, case.id),
    )
    return _build_document_gate_preview_out(
        case_type=case.case_type,
        patent_category=case.patent_category,
        flow_dir=case.flow_dir,
        gate=gate,
        file_events=_build_case_document_file_events(db, case.id),
    )


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
    payload: CaseUpdateLimited,
    _perm: None = Depends(require_perm("Case.EditLimited")),
    current_user: T_User = current_user_dep,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
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
    case = update_case_limited_service(db, case_id, payload, current_user.id)
    return _serialize_case(db, case)


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
