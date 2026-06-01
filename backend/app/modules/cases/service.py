from __future__ import annotations

import calendar
import json
from datetime import date, timedelta
from decimal import Decimal
from typing import Any
from uuid import uuid4

from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session

from app.core.errors import raise_business_error
from app.core.pagination import PageResult, offset_limit
from app.modules.auth.models import T_Role, T_User, T_UserRole
from app.modules.billing.models import BillItem, PaymentLine
from app.modules.cases.document_gate_service import (
    GateCaseContext,
    GateDocumentInput,
    MaterialGateResult,
    build_batch_execution_preview,
    evaluate_material_gate,
)
from app.modules.cases.enums import CaseStatus, CaseType, FlowDir, PatentCategory
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
    CaseBatchFilingExecutionPreviewOut,
    CaseBatchFilingFinalMaterialGateOut,
    CaseClientReportCountResponse,
    CaseCreate,
    CaseDocumentGateMissingItemOut,
    CaseInventorIn,
    CaseListItem,
    CaseListReportResponse,
    CaseReportCountResponse,
    CaseReportSummaryResponse,
    CaseTrendReportCountResponse,
    CaseUpdateFull,
    CaseUpdateLimited,
)
from app.modules.documents.enums import DocumentDirection, DocumentDocType
from app.modules.documents.models import DocTemplate, Document
from app.modules.fees.models import FeeDraft
from app.modules.masterdata.applicants.models import Applicant
from app.modules.masterdata.clients.models import Client, ClientAddress
from app.modules.tasks.enums import TaskAction, TaskDeadlineBase, TaskRemindBase
from app.modules.tasks.models import Task, TaskLog, TaskTemplate

_CONSULTING_CASE_TYPES = {CaseType.CONSULTING.value, CaseType.SEARCH.value}
_FOREIGN_FLOW_DIRS = {FlowDir.CN_OUTBOUND.value, FlowDir.FOREIGN_INBOUND.value}
_FOREIGN_AGENT_TYPES = {"AGENT", "代理所"}
_ORGANIZATION_LIKE_APPLICANT_TYPES = {"ENTITY", "UNIV", "GOV"}
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
_CASE_GRANTED_LINEAGE_STATUSES = {
    CaseStatus.GRANTED.value,
    CaseStatus.TERMINATED.value,
    CaseStatus.INVALIDATED.value,
    CaseStatus.EXPIRED.value,
}
_CASE_GRANTED_RATE_DENOMINATOR_STATUSES = _CASE_GRANTED_LINEAGE_STATUSES | {
    CaseStatus.REJECTED.value,
    CaseStatus.WITHDRAWN.value,
    CaseStatus.ABANDONED.value,
}
_APPLY_FEE_LIMIT_TEMPLATE_CODE = "APPLY_FEE_LIMIT"
_APPLY_FEE_LIMIT_TEMPLATE_NAME = "申请费时限"
_APPLY_FEE_LIMIT_DEFAULT_ADD_DAYS = 30
_APPLY_FEE_LIMIT_DEFAULT_INNER_OFFSET_DAYS = 7
_CHINA_NATIONALITY_VALUES = {"CN", "CHN", "CHINA", "PRC", "中国", "中华人民共和国"}


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


def _contains_control_characters(value: str) -> bool:
    return any(ord(char) < 32 or ord(char) == 127 for char in value)


def _normalize_app_no(value: str | None, *, required: bool) -> str | None:
    if value is None:
        return None

    normalized = value.strip()
    if not normalized:
        if required:
            raise_business_error(
                "CASE_APP_NO_INVALID",
                "app_no is invalid",
                details={"app_no": value},
                status_code=400,
            )
        return None

    if _contains_control_characters(normalized):
        raise_business_error(
            "CASE_APP_NO_INVALID",
            "app_no is invalid",
            details={"app_no": value},
            status_code=400,
        )
    return normalized


def _is_present_text(value: str | None) -> bool:
    return bool((value or "").strip())


def _is_china_nationality(value: str | None) -> bool:
    normalized = (value or "").strip()
    return normalized.upper() in _CHINA_NATIONALITY_VALUES or "中国" in normalized


def validate_inventor_official_fields(inventors: list[CaseInventorIn]) -> None:
    for inventor in inventors:
        if _is_china_nationality(inventor.nationality) and not _is_present_text(
            inventor.china_id_no
        ):
            raise_business_error(
                "CASE_INVENTOR_CHINA_ID_REQUIRED",
                "china_id_no is required for China-national inventors",
                details={"seq": inventor.seq, "nationality": inventor.nationality},
                status_code=400,
            )


def _earliest_priority_date_from_dicts(priorities: list[dict[str, Any]]) -> date | None:
    priority_dates = [
        priority.get("prio_date") for priority in priorities if priority.get("prio_date")
    ]
    return min(priority_dates) if priority_dates else None


def _earliest_priority_date_for_case(db: Session, case_id: str) -> date | None:
    row = (
        db.query(T_Priority.prio_date)
        .filter(T_Priority.case_id == case_id, T_Priority.prio_date.is_not(None))
        .order_by(T_Priority.prio_date.asc())
        .first()
    )
    return row.prio_date if row else None


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


def validate_case_applicant_kind_mismatch(
    db: Session,
    *,
    applicant_kind: str | None,
    first_applicant_id: str | None,
) -> None:
    normalized_applicant_kind = (applicant_kind or "").strip().upper()
    if not normalized_applicant_kind or not first_applicant_id:
        return

    first_applicant = db.query(Applicant).filter(Applicant.id == first_applicant_id).first()
    if not first_applicant:
        return

    first_applicant_type = (first_applicant.applicant_type or "").strip().upper()
    if not first_applicant_type:
        return

    if first_applicant_type == "INDIVIDUAL":
        if normalized_applicant_kind != "INDIVIDUAL":
            raise_business_error(
                "CASE_APPLICANT_KIND_MISMATCH",
                "applicant_kind does not match the first applicant type",
                details={
                    "applicant_kind": normalized_applicant_kind,
                    "first_applicant_type": first_applicant_type,
                    "first_applicant_id": first_applicant_id,
                },
                status_code=400,
            )
        return

    if first_applicant_type in _ORGANIZATION_LIKE_APPLICANT_TYPES:
        if normalized_applicant_kind not in _ORGANIZATION_LIKE_APPLICANT_TYPES:
            raise_business_error(
                "CASE_APPLICANT_KIND_MISMATCH",
                "applicant_kind does not match the first applicant type",
                details={
                    "applicant_kind": normalized_applicant_kind,
                    "first_applicant_type": first_applicant_type,
                    "first_applicant_id": first_applicant_id,
                },
                status_code=400,
            )


def _default_legacy_case_applicant(db: Session, client_id: str | None) -> CaseApplicantIn:
    client_name: str | None = None
    if client_id:
        client = db.query(Client.name_cn, Client.name_en).filter(Client.id == client_id).first()
        if client:
            client_name = (client.name_cn or client.name_en or "").strip() or None

    return CaseApplicantIn(
        seq=1,
        is_first=True,
        name_cn=client_name or "未录入申请人",
    )


def _normalize_create_case_applicants(db: Session, data: CaseCreate) -> list[CaseApplicantIn]:
    applicants = list(data.applicants)
    if applicants or "applicants" in data.model_fields_set:
        return applicants
    return [_default_legacy_case_applicant(db, data.client_id)]


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
    if normalized_flow_dir == FlowDir.CN_OUTBOUND.value and not normalized_to_country:
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


def validate_case_type_patent_category_combo(
    *, case_type: str | None, patent_category: str | None
) -> None:
    normalized_case_type = (case_type or "").strip().upper()
    normalized_patent_category = (patent_category or "").strip().upper()
    if (
        normalized_case_type == CaseType.SEARCH.value
        and normalized_patent_category == PatentCategory.DES.value
    ):
        raise_business_error(
            "CASE_TYPE_COMBO_INVALID",
            "case_type and patent_category are not a valid combination",
            details={
                "case_type": normalized_case_type,
                "patent_category": normalized_patent_category,
            },
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


def validate_filing_date_after_priority(
    *, filing_date: date | None, earliest_priority_date: date | None
) -> None:
    if filing_date is None or earliest_priority_date is None:
        return
    if filing_date < earliest_priority_date:
        raise_business_error(
            "CASE_FILING_BEFORE_PRIORITY",
            "filing_date must be on or after the earliest priority date",
            details={
                "filing_date": str(filing_date),
                "earliest_priority_date": str(earliest_priority_date),
            },
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
    *,
    status: str | None,
    app_no: str | None,
    filing_date: date | None,
    pub_no: str | None = None,
    pub_date: date | None = None,
    grant_no: str | None = None,
    grant_date: date | None = None,
    first_annuity_year: int | None = None,
    valid_until: date | None = None,
) -> None:
    normalized_status = (status or "").strip().upper()
    if normalized_status == CaseStatus.PUBLISHED.value:
        missing_fields: list[str] = []
        if app_no is None:
            missing_fields.append("app_no")
        if filing_date is None:
            missing_fields.append("filing_date")
        if not _is_present_text(pub_no):
            missing_fields.append("pub_no")
        if pub_date is None:
            missing_fields.append("pub_date")
        if missing_fields:
            raise_business_error(
                "CASE_PUBLISHED_FIELDS_REQUIRED",
                "PUBLISHED cases require app_no, filing_date, pub_no and pub_date",
                details={
                    "status": normalized_status,
                    "missing_fields": missing_fields,
                },
                status_code=400,
            )
        return

    if normalized_status == CaseStatus.GRANTED.value:
        missing_fields = []
        if app_no is None:
            missing_fields.append("app_no")
        if filing_date is None:
            missing_fields.append("filing_date")
        if not _is_present_text(pub_no):
            missing_fields.append("pub_no")
        if pub_date is None:
            missing_fields.append("pub_date")
        if not _is_present_text(grant_no):
            missing_fields.append("grant_no")
        if grant_date is None:
            missing_fields.append("grant_date")
        if first_annuity_year is None:
            missing_fields.append("first_annuity_year")
        if valid_until is None:
            missing_fields.append("valid_until")
        if missing_fields:
            raise_business_error(
                "CASE_GRANTED_FIELDS_REQUIRED",
                "GRANTED cases require publication, grant and annuity fields",
                details={
                    "status": normalized_status,
                    "missing_fields": missing_fields,
                },
                status_code=400,
            )
        return

    if normalized_status in _STATUSES_REQUIRING_APPLICATION_FIELDS:
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
    status_counts_map = {
        normalized_status: count
        for status_key, count in status_rows
        if (normalized_status := (status_key or "").strip())
    }
    case_type_rows = (
        query.with_entities(Case.case_type, func.count(Case.id))
        .group_by(Case.case_type)
        .order_by(Case.case_type.asc())
        .all()
    )
    client_counts: dict[str, dict[str, Any]] = {}
    country_counts: dict[str, int] = {}
    agent_counts: dict[str, int] = {}
    year_trends: dict[str, dict[str, int | str]] = {}
    month_trends: dict[str, dict[str, int | str]] = {}
    cases = (
        query.with_entities(
            Case.client_id,
            Client.name_cn,
            Client.name_en,
            Case.case_type,
            Case.from_country,
            Case.to_country,
            Case.primary_agent_id,
            Case.second_agent_id,
        )
        .outerjoin(Client, Client.id == Case.client_id)
        .all()
    )
    for (
        client_id,
        client_name_cn,
        client_name_en,
        case_type,
        from_country,
        to_country,
        primary_agent_id,
        second_agent_id,
    ) in cases:
        client_key = (client_id or "").strip() or "UNASSIGNED"
        client_label = (client_name_cn or client_name_en or client_id or "").strip() or "未分配客户"
        client_bucket = client_counts.setdefault(
            client_key,
            {"key": client_key, "label": client_label, "count": 0, "case_type_counts": {}},
        )
        client_bucket["count"] += 1
        case_type_key = (case_type or "").strip() or "UNSPECIFIED"
        case_type_counts = client_bucket["case_type_counts"]
        case_type_counts[case_type_key] = case_type_counts.get(case_type_key, 0) + 1

        country_key = (to_country or from_country or "").strip() or "未填写"
        country_counts[country_key] = country_counts.get(country_key, 0) + 1

        seen_agents: set[str] = set()
        for agent_id in (primary_agent_id, second_agent_id):
            normalized = (agent_id or "").strip()
            if not normalized or normalized in seen_agents:
                continue
            seen_agents.add(normalized)
            agent_counts[normalized] = agent_counts.get(normalized, 0) + 1

    trend_cases = (
        query.with_entities(
            Case.id,
            Case.filing_date,
            Case.grant_date,
            Case.terminated_date,
            Case.invalidated_date,
            Case.withdrawn_date,
            Case.abandoned_date,
        )
        .distinct()
        .all()
    )
    for (
        _case_id,
        filing_date,
        grant_date,
        terminated_date,
        invalidated_date,
        withdrawn_date,
        abandoned_date,
    ) in trend_cases:
        _accumulate_case_trend_bucket(
            year_trends,
            month_trends,
            filing_date=filing_date,
            grant_date=grant_date,
            terminated_date=terminated_date,
            invalidated_date=invalidated_date,
            withdrawn_date=withdrawn_date,
            abandoned_date=abandoned_date,
        )

    granted_count = sum(
        status_counts_map.get(status_key, 0) for status_key in _CASE_GRANTED_LINEAGE_STATUSES
    )
    grant_rate_denominator = sum(
        status_counts_map.get(status_key, 0)
        for status_key in _CASE_GRANTED_RATE_DENOMINATOR_STATUSES
    )
    terminated_count = status_counts_map.get(CaseStatus.TERMINATED.value, 0)
    invalidated_count = status_counts_map.get(CaseStatus.INVALIDATED.value, 0)
    in_prosecution_count = sum(
        count
        for status_key, count in status_counts_map.items()
        if status_key not in _CASE_GRANTED_RATE_DENOMINATOR_STATUSES
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
        client_counts=[
            CaseClientReportCountResponse(
                key=str(client_bucket["key"]),
                label=str(client_bucket["label"]),
                count=int(client_bucket["count"]),
                case_type_counts=[
                    CaseReportCountResponse(key=case_type_key, count=count)
                    for case_type_key, count in sorted(
                        client_bucket["case_type_counts"].items(), key=lambda item: item[0]
                    )
                ],
            )
            for client_bucket in sorted(
                client_counts.values(), key=lambda item: (-int(item["count"]), str(item["label"]))
            )
        ],
        country_counts=[
            CaseReportCountResponse(key=country_key, count=count)
            for country_key, count in sorted(country_counts.items(), key=lambda item: item[0])
        ],
        agent_counts=[
            CaseReportCountResponse(key=agent_key, count=count)
            for agent_key, count in sorted(agent_counts.items(), key=lambda item: item[0])
        ],
        year_trends=_build_case_trend_response(year_trends),
        month_trends=_build_case_trend_response(month_trends),
        granted_count=granted_count,
        grant_rate=(granted_count / grant_rate_denominator if grant_rate_denominator > 0 else None),
        terminated_count=terminated_count,
        invalidated_count=invalidated_count,
        in_prosecution_count=in_prosecution_count,
    )


def _empty_case_trend_bucket(*, key: str, label: str) -> dict[str, int | str]:
    return {
        "key": key,
        "label": label,
        "new_case_count": 0,
        "granted_count": 0,
        "terminated_count": 0,
        "invalidated_count": 0,
        "withdrawn_count": 0,
        "abandoned_count": 0,
    }


def _increment_case_trend(
    buckets: dict[str, dict[str, int | str]],
    *,
    event_date: date | None,
    metric: str,
    use_month: bool,
) -> None:
    if event_date is None:
        return
    key = event_date.strftime("%Y-%m") if use_month else str(event_date.year)
    label = key
    bucket = buckets.setdefault(key, _empty_case_trend_bucket(key=key, label=label))
    bucket[metric] = int(bucket[metric]) + 1


def _accumulate_case_trend_bucket(
    year_trends: dict[str, dict[str, int | str]],
    month_trends: dict[str, dict[str, int | str]],
    *,
    filing_date: date | None,
    grant_date: date | None,
    terminated_date: date | None,
    invalidated_date: date | None,
    withdrawn_date: date | None,
    abandoned_date: date | None,
) -> None:
    metrics = [
        ("new_case_count", filing_date),
        ("granted_count", grant_date),
        ("terminated_count", terminated_date),
        ("invalidated_count", invalidated_date),
        ("withdrawn_count", withdrawn_date),
        ("abandoned_count", abandoned_date),
    ]
    for metric, event_date in metrics:
        _increment_case_trend(year_trends, event_date=event_date, metric=metric, use_month=False)
        _increment_case_trend(month_trends, event_date=event_date, metric=metric, use_month=True)


def _build_case_trend_response(
    buckets: dict[str, dict[str, int | str]],
) -> list[CaseTrendReportCountResponse]:
    return [
        CaseTrendReportCountResponse(
            key=str(bucket["key"]),
            label=str(bucket["label"]),
            new_case_count=int(bucket["new_case_count"]),
            granted_count=int(bucket["granted_count"]),
            terminated_count=int(bucket["terminated_count"]),
            invalidated_count=int(bucket["invalidated_count"]),
            withdrawn_count=int(bucket["withdrawn_count"]),
            abandoned_count=int(bucket["abandoned_count"]),
        )
        for bucket in (buckets[key] for key in sorted(buckets))
    ]


def _serialize_applicant_official_fields(applicant: T_CaseApplicant) -> dict[str, Any]:
    return {
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


def _serialize_inventor_official_fields(inventor: T_CaseInventor) -> dict[str, Any]:
    return {
        "seq": inventor.seq,
        "name_cn": inventor.name_cn,
        "name_en": inventor.name_en,
        "nationality": inventor.nationality,
        "china_id_no": inventor.china_id_no,
    }


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
    case_ids = [case.id for case in items]
    client_ids = {case.client_id for case in items if case.client_id}
    client_name_map: dict[str, str] = {}
    if client_ids:
        clients = db.query(Client.id, Client.name_cn).filter(Client.id.in_(client_ids)).all()
        client_name_map = {client.id: client.name_cn for client in clients}

    applicants_by_case_id: dict[str, list[dict[str, Any]]] = {case_id: [] for case_id in case_ids}
    inventors_by_case_id: dict[str, list[dict[str, Any]]] = {case_id: [] for case_id in case_ids}
    if case_ids:
        applicant_rows = (
            db.query(T_CaseApplicant)
            .filter(T_CaseApplicant.case_id.in_(case_ids))
            .order_by(T_CaseApplicant.case_id.asc(), T_CaseApplicant.seq.asc())
            .all()
        )
        inventor_rows = (
            db.query(T_CaseInventor)
            .filter(T_CaseInventor.case_id.in_(case_ids))
            .order_by(T_CaseInventor.case_id.asc(), T_CaseInventor.seq.asc())
            .all()
        )
        for applicant in applicant_rows:
            applicants_by_case_id.setdefault(applicant.case_id, []).append(
                _serialize_applicant_official_fields(applicant)
            )
        for inventor in inventor_rows:
            inventors_by_case_id.setdefault(inventor.case_id, []).append(
                _serialize_inventor_official_fields(inventor)
            )

    list_items = [
        CaseListItem(
            id=case.id,
            case_no=case.case_no,
            case_type=case.case_type,
            patent_category=case.patent_category,
            client_id=case.client_id,
            client_name=client_name_map.get(case.client_id) if case.client_id else None,
            title_cn=case.title_cn,
            title_en=case.title_en,
            app_no=case.app_no,
            status=case.status,
            filing_date=str(case.filing_date) if case.filing_date else None,
            recv_date=str(case.recv_date) if case.recv_date else None,
            patent_no=case.patent_no,
            primary_agent_id=case.primary_agent_id,
            applicants=applicants_by_case_id.get(case.id, []),
            inventors=inventors_by_case_id.get(case.id, []),
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


def _load_batch_gate_documents(db: Session, case_id: str) -> list[GateDocumentInput]:
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


def _case_has_priority(db: Session, case_id: str) -> bool:
    return db.query(T_Priority.id).filter(T_Priority.case_id == case_id).first() is not None


def _build_batch_final_material_gate_out(
    gate: MaterialGateResult,
) -> CaseBatchFilingFinalMaterialGateOut:
    return CaseBatchFilingFinalMaterialGateOut(
        material_count=gate.material_count,
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
        conclusion=gate.conclusion.value,
        hard_block=gate.hard_block,
        afterfill_audit_required=gate.afterfill_audit_required,
        execution_preview=[
            CaseBatchFilingExecutionPreviewOut(
                kind=item.kind,
                label=item.label,
                enabled=item.enabled,
                detail=item.detail,
            )
            for item in build_batch_execution_preview(
                gate,
                apply_exam_now=False,
                generate_list=True,
            )
        ],
    )


def _evaluate_batch_final_material_gate(
    db: Session,
    case: Case,
) -> CaseBatchFilingFinalMaterialGateOut:
    gate = evaluate_material_gate(
        GateCaseContext(
            case_type=case.case_type,
            patent_category=case.patent_category,
            flow_dir=case.flow_dir,
            has_exam_request=case.has_exam_request,
            no_power=case.no_power,
            has_priority=_case_has_priority(db, case.id),
        ),
        documents=_load_batch_gate_documents(db, case.id),
    )
    return _build_batch_final_material_gate_out(gate)


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
            final_material_gate=_evaluate_batch_final_material_gate(db, case),
        )
        for case in items
    ]

    return PageResult(items=candidate_items, page=page, page_size=page_size, total=total)


def _batch_filing_ref(submitted_date: date, selected_case_ids: list[str]) -> str:
    first_case_marker = selected_case_ids[0][:8] if selected_case_ids else "EMPTY"
    return f"BATCH-FILING-{submitted_date.isoformat()}-{len(selected_case_ids)}-{first_case_marker}"


def _create_batch_filing_documents(
    db: Session,
    *,
    cases: list[Case],
    selected_case_ids: list[str],
    submitted_date: date,
    user_id: str,
) -> list[str]:
    batch_ref = _batch_filing_ref(submitted_date, selected_case_ids)
    extra_data = json.dumps(
        {
            "source": "batch_filing",
            "batch_ref": batch_ref,
            "selected_case_ids": selected_case_ids,
        },
        ensure_ascii=False,
    )
    document_ids: list[str] = []
    for case in cases:
        document = Document(
            id=str(uuid4()),
            case_id=case.id,
            doc_type=DocumentDocType.OFFICIAL_OUT.value,
            direction=DocumentDirection.OUT.value,
            doc_date=submitted_date,
            title=f"批量递交清单-{submitted_date.isoformat()}",
            ref_no=batch_ref,
            extra_data=extra_data,
            created_by=user_id,
            updated_by=user_id,
        )
        db.add(document)
        document_ids.append(document.id)
    return document_ids


def _get_or_create_apply_fee_limit_template(db: Session, *, user_id: str) -> TaskTemplate:
    template = (
        db.query(TaskTemplate)
        .filter(TaskTemplate.code == _APPLY_FEE_LIMIT_TEMPLATE_CODE)
        .one_or_none()
    )
    if template:
        return template

    template = TaskTemplate(
        id=str(uuid4()),
        code=_APPLY_FEE_LIMIT_TEMPLATE_CODE,
        name=_APPLY_FEE_LIMIT_TEMPLATE_NAME,
        enabled=True,
        deadline_base=TaskDeadlineBase.CASE_EVENT,
        add_days=_APPLY_FEE_LIMIT_DEFAULT_ADD_DAYS,
        add_months=0,
        inner_offset_days=_APPLY_FEE_LIMIT_DEFAULT_INNER_OFFSET_DAYS,
        remind_base=TaskRemindBase.DEADLINE,
        created_by=user_id,
        updated_by=user_id,
    )
    db.add(template)
    db.flush()
    return template


def _add_months(base: date, months: int) -> date:
    month = base.month - 1 + months
    year = base.year + month // 12
    month = month % 12 + 1
    day = min(base.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def _compute_task_dates(template: TaskTemplate, base_date: date) -> tuple[date, date | None]:
    due_date = base_date
    add_months = template.add_months or 0
    add_days = template.add_days or 0
    if add_months:
        due_date = _add_months(due_date, add_months)
    if add_days:
        due_date = due_date + timedelta(days=add_days)

    internal_due_date = None
    if template.inner_offset_days is not None:
        internal_due_date = due_date - timedelta(days=template.inner_offset_days)
    return due_date, internal_due_date


def _resolve_apply_fee_limit_base_date(
    case: Case, template: TaskTemplate, submitted_date: date
) -> date:
    deadline_base = template.deadline_base or TaskDeadlineBase.CASE_EVENT
    if deadline_base == TaskDeadlineBase.CASE_EVENT:
        return submitted_date
    if deadline_base == TaskDeadlineBase.FILING_DATE:
        base_date = case.filing_date
    elif deadline_base == TaskDeadlineBase.RECEIVE_DATE:
        base_date = case.recv_date
    elif deadline_base == TaskDeadlineBase.PUB_DATE:
        base_date = case.pub_date
    elif deadline_base == TaskDeadlineBase.GRANT_DATE:
        base_date = case.grant_date
    else:
        raise_business_error(
            "TASK_DEADLINE_BASE_UNSUPPORTED",
            "APPLY_FEE_LIMIT template deadline_base is not supported for batch filing",
            details={"deadline_base": str(deadline_base)},
            status_code=400,
        )
    if base_date is None:
        raise_business_error(
            "TASK_DEADLINE_BASE_DATE_REQUIRED",
            "APPLY_FEE_LIMIT base date is missing for batch filing",
            details={"deadline_base": deadline_base.value, "case_id": case.id},
            status_code=400,
        )
    return base_date


def _resolve_remind_base_date(
    template: TaskTemplate, *, due_date: date, internal_due_date: date | None
) -> date:
    if template.remind_base == TaskRemindBase.INNER and internal_due_date is not None:
        return internal_due_date
    return due_date


def _compute_task_reminders(
    template: TaskTemplate, *, due_date: date, internal_due_date: date | None
) -> tuple[date | None, date | None, date | None, date | None]:
    remind_base_date = _resolve_remind_base_date(
        template,
        due_date=due_date,
        internal_due_date=internal_due_date,
    )

    def _offset(days: int | None) -> date | None:
        if days is None:
            return None
        return remind_base_date - timedelta(days=days)

    remind1 = _offset(template.remind_1_offset_days)
    remind2 = _offset(template.remind_2_offset_days)
    remind3 = _offset(template.remind_3_offset_days)
    daily_remind_from = None
    if template.daily_remind:
        candidates = [value for value in (remind1, remind2, remind3) if value is not None]
        daily_remind_from = min(candidates) if candidates else remind_base_date
    return remind1, remind2, remind3, daily_remind_from


def _resolve_default_worker_id(db: Session, template: TaskTemplate) -> str | None:
    role_code = (template.default_worker_role or "").strip()
    if not role_code:
        return None

    return (
        db.query(T_User.id)
        .join(T_UserRole, T_UserRole.user_id == T_User.id)
        .join(T_Role, T_Role.id == T_UserRole.role_id)
        .filter(T_Role.code == role_code, T_User.is_active.is_(True))
        .order_by(T_User.created_at.asc(), T_User.id.asc())
        .scalar()
    )


def _create_apply_fee_limit_tasks(
    db: Session,
    *,
    cases: list[Case],
    submitted_date: date,
    user_id: str,
) -> list[str]:
    template = _get_or_create_apply_fee_limit_template(db, user_id=user_id)
    worker_id = _resolve_default_worker_id(db, template)

    created_task_ids: list[str] = []
    for case in cases:
        base_date = _resolve_apply_fee_limit_base_date(case, template, submitted_date)
        due_date, internal_due_date = _compute_task_dates(template, base_date)
        remind1, remind2, remind3, daily_remind_from = _compute_task_reminders(
            template,
            due_date=due_date,
            internal_due_date=internal_due_date,
        )
        existing_task = (
            db.query(Task)
            .filter(
                Task.case_id == case.id,
                Task.task_template_id == template.id,
                Task.status == "OPEN",
            )
            .one_or_none()
        )
        if existing_task:
            continue

        task = Task(
            id=str(uuid4()),
            case_id=case.id,
            task_template_id=template.id,
            title=template.name or template.code,
            base_date=base_date,
            due_date=due_date,
            internal_due_date=internal_due_date,
            remind1=remind1,
            remind2=remind2,
            remind3=remind3,
            daily_remind_from=daily_remind_from,
            daily_remind=bool(template.daily_remind),
            worker_id=worker_id,
            supervisor_id=template.default_supervisor_id,
            status="OPEN",
            created_by=user_id,
            updated_by=user_id,
        )
        db.add(task)
        db.add(
            TaskLog(
                id=str(uuid4()),
                task_id=task.id,
                action=TaskAction.AUTO_CREATE.value,
                from_status=None,
                to_status=task.status,
                remark="Created by batch filing submit",
                created_by=user_id,
                updated_by=user_id,
            )
        )
        created_task_ids.append(task.id)

    return created_task_ids


def execute_batch_filing(
    db: Session,
    *,
    selected_case_ids: list[str],
    submitted_date: date,
    apply_exam_now: bool,
    generate_list: bool = False,
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

    blocked_gate_case_nos: list[str] = []
    blocked_gate_case_ids: list[str] = []
    for case_id in unique_case_ids:
        case = case_by_id[case_id]
        material_gate = _evaluate_batch_final_material_gate(db, case)
        if material_gate.hard_block:
            blocked_gate_case_nos.append(case.case_no)
            blocked_gate_case_ids.append(case.id)
    if blocked_gate_case_ids:
        raise_business_error(
            "CASE_BATCH_FILING_MATERIAL_GATE_BLOCKED",
            "One or more selected cases are blocked by final material gate",
            details={
                "case_ids": blocked_gate_case_ids,
                "case_nos": blocked_gate_case_nos,
            },
            status_code=400,
        )

    updated_case_ids: list[str] = []
    ordered_cases: list[Case] = []
    for case_id in unique_case_ids:
        case = case_by_id[case_id]
        case.submitted_date = submitted_date
        case.status = CaseStatus.WAITING_RECEIPT.value
        if apply_exam_now:
            case.has_exam_request = True
        case.updated_by = user_id
        updated_case_ids.append(case.id)
        ordered_cases.append(case)

    document_ids = (
        _create_batch_filing_documents(
            db,
            cases=ordered_cases,
            selected_case_ids=unique_case_ids,
            submitted_date=submitted_date,
            user_id=user_id,
        )
        if generate_list
        else []
    )
    created_task_ids = _create_apply_fee_limit_tasks(
        db,
        cases=ordered_cases,
        submitted_date=submitted_date,
        user_id=user_id,
    )

    db.commit()
    return CaseBatchFilingActionOut(
        success_count=len(updated_case_ids),
        failure_count=0,
        updated_case_ids=updated_case_ids,
        document_ids=document_ids,
        created_task_ids=created_task_ids,
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

    applicants = _normalize_create_case_applicants(db, data)
    applicants_dict = [applicant.model_dump() for applicant in applicants]
    priorities_dict = [priority.model_dump() for priority in data.priorities]
    bio_deposits_dict = [bio_deposit.model_dump() for bio_deposit in data.bio_deposits]
    validate_applicants(applicants_dict)
    validate_inventor_official_fields(data.inventors)
    validate_case_applicant_links(db, applicants)
    first_applicant = next((applicant for applicant in applicants if applicant.is_first), None)
    validate_case_applicant_kind_mismatch(
        db,
        applicant_kind=data.applicant_kind,
        first_applicant_id=first_applicant.applicant_id if first_applicant else None,
    )
    validate_case_type_patent_category_combo(
        case_type=data.case_type.value,
        patent_category=data.patent_category.value,
    )
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
    normalized_app_no = _normalize_app_no(
        data.app_no,
        required=(data.status.value if data.status else None)
        in {CaseStatus.PUBLISHED.value, CaseStatus.GRANTED.value},
    )
    if "applicants" in data.model_fields_set:
        validate_status_required_fields(
            status=data.status.value if data.status else None,
            app_no=normalized_app_no,
            filing_date=data.filing_date,
            pub_no=data.pub_no,
            pub_date=data.pub_date,
            grant_no=data.grant_no,
            grant_date=data.grant_date,
            first_annuity_year=data.first_annuity_year,
            valid_until=data.valid_until,
        )
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
        app_no=normalized_app_no,
        status=data.status.value if data.status else "NOT_FILED",
        filing_date=data.filing_date,
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

    for applicant in applicants:
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
                nationality=applicant.nationality,
                certificate_type=applicant.certificate_type,
                certificate_no=applicant.certificate_no,
                official_postcode=applicant.official_postcode,
                official_applicant_kind=applicant.official_applicant_kind,
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
                nationality=inventor.nationality,
                china_id_no=inventor.china_id_no,
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
    target_patent_category = case.patent_category
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
    target_pub_no = data.pub_no if "pub_no" in provided_fields else case.pub_no
    target_pub_date = data.pub_date if "pub_date" in provided_fields else case.pub_date
    target_grant_no = data.grant_no if "grant_no" in provided_fields else case.grant_no
    target_grant_date = data.grant_date if "grant_date" in provided_fields else case.grant_date
    target_first_annuity_year = (
        data.first_annuity_year
        if "first_annuity_year" in provided_fields
        else case.first_annuity_year
    )
    target_valid_until = data.valid_until if "valid_until" in provided_fields else case.valid_until

    validate_case_status_transition(case.status, target_status)
    if data.priorities is not None:
        priorities_dict = [priority.model_dump() for priority in data.priorities]
        validate_priorities(priorities_dict)

    normalized_target_app_no = _normalize_app_no(
        target_app_no,
        required=target_status in {CaseStatus.PUBLISHED.value, CaseStatus.GRANTED.value},
    )
    validate_status_required_fields(
        status=target_status,
        app_no=normalized_target_app_no,
        filing_date=target_filing_date,
        pub_no=target_pub_no,
        pub_date=target_pub_date,
        grant_no=target_grant_no,
        grant_date=target_grant_date,
        first_annuity_year=target_first_annuity_year,
        valid_until=target_valid_until,
    )
    validate_case_type_patent_category_combo(
        case_type=target_case_type,
        patent_category=target_patent_category,
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
    if target_status in {CaseStatus.PUBLISHED.value, CaseStatus.GRANTED.value}:
        if data.priorities is not None:
            earliest_priority_date = _earliest_priority_date_from_dicts(priorities_dict)
        else:
            earliest_priority_date = _earliest_priority_date_for_case(db, case_id)
        validate_filing_date_after_priority(
            filing_date=target_filing_date,
            earliest_priority_date=earliest_priority_date,
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
        case.app_no = normalized_target_app_no
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
            first_applicant = next(
                (applicant for applicant in data.applicants if applicant.is_first), None
            )
            validate_case_applicant_kind_mismatch(
                db,
                applicant_kind=(
                    data.applicant_kind
                    if "applicant_kind" in provided_fields
                    else case.applicant_kind
                ),
                first_applicant_id=first_applicant.applicant_id if first_applicant else None,
            )

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
                    nationality=applicant.nationality,
                    certificate_type=applicant.certificate_type,
                    certificate_no=applicant.certificate_no,
                    official_postcode=applicant.official_postcode,
                    official_applicant_kind=applicant.official_applicant_kind,
                )
            )
    elif "applicant_kind" in provided_fields:
        first_applicant = (
            db.query(T_CaseApplicant.applicant_id)
            .filter(T_CaseApplicant.case_id == case_id)
            .order_by(T_CaseApplicant.seq)
            .first()
        )
        validate_case_applicant_kind_mismatch(
            db,
            applicant_kind=data.applicant_kind,
            first_applicant_id=first_applicant.applicant_id if first_applicant else None,
        )

    if data.inventors is not None:
        validate_inventor_official_fields(data.inventors)
        db.query(T_CaseInventor).filter(T_CaseInventor.case_id == case_id).delete()
        for inventor in data.inventors:
            db.add(
                T_CaseInventor(
                    id=str(uuid4()),
                    case_id=case.id,
                    seq=inventor.seq,
                    name_cn=inventor.name_cn,
                    name_en=inventor.name_en,
                    nationality=inventor.nationality,
                    china_id_no=inventor.china_id_no,
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
    if data.draw_pages is not None:
        case.draw_pages = data.draw_pages
    if data.claim_count is not None:
        case.claim_count = data.claim_count
    if data.claim_pages is not None:
        case.claim_pages = data.claim_pages
    if data.manuscript_words is not None:
        case.manuscript_words = data.manuscript_words

    case.updated_by = user_id

    if data.inventors is not None:
        validate_inventor_official_fields(data.inventors)
        db.query(T_CaseInventor).filter(T_CaseInventor.case_id == case_id).delete()
        for inventor in data.inventors:
            db.add(
                T_CaseInventor(
                    id=str(uuid4()),
                    case_id=case.id,
                    seq=inventor.seq,
                    name_cn=inventor.name_cn,
                    name_en=inventor.name_en,
                    nationality=inventor.nationality,
                    china_id_no=inventor.china_id_no,
                )
            )

    db.commit()
    db.refresh(case)
    return case
