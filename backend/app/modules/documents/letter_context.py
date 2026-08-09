from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import Enum
from types import MappingProxyType

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.errors import BusinessError
from app.modules.cases.models import Case, T_CaseApplicant, T_CaseInventor
from app.modules.documents.extra_data import (
    DocumentExtraDataError,
    parse_document_extra_data,
)
from app.modules.documents.models import DocTemplate, Document, DocumentEvidenceVersion
from app.modules.fees.models import FeeObligation, FeeObligationLine
from app.modules.masterdata.clients.models import ClientContact
from app.modules.templates.models import FormatLetterMapping, Template

_TEMPLATE_CODES = frozenset(f"FORMAT_LETTER_{number:03d}" for number in range(1, 9))
_DEADLINE_TEMPLATE_CODES = frozenset(
    {
        "FORMAT_LETTER_001",
        "FORMAT_LETTER_003",
        "FORMAT_LETTER_006",
        "FORMAT_LETTER_007",
    }
)
_NOTICE_BY_TEMPLATE_AND_TITLE = {
    ("FORMAT_LETTER_001", "驳回决定"): "REJECTION_DECISION",
    ("FORMAT_LETTER_002", "初步审查合格"): "PRELIMINARY_PASS",
    ("FORMAT_LETTER_003", "公布通知书"): "PUBLICATION_NOTICE",
    ("FORMAT_LETTER_004", "进入实审通知"): "SUBSTANTIVE_ENTRY_NOTICE",
    ("FORMAT_LETTER_005", "受理通知-电子"): "ACCEPTANCE_NOTICE",
    ("FORMAT_LETTER_006", "授权通知书-电子"): "GRANT_REGISTRATION_NOTICE",
    ("FORMAT_LETTER_008", "专利证书"): "PATENT_CERTIFICATE",
}
_OA_ARABIC_TITLE = re.compile(r"第([1-9][0-9]*)次审查意见通知书")
_OA_CHINESE_TITLE = re.compile(r"第([一二三四五六七八九十百千万两〇零]+)次审查意见通知书")
_CHINESE_DIGITS = {
    "一": 1,
    "二": 2,
    "三": 3,
    "四": 4,
    "五": 5,
    "六": 6,
    "七": 7,
    "八": 8,
    "九": 9,
}
_CHINESE_UNITS = {"十": 10, "百": 100, "千": 1000}
_CHINESE_DIGIT_TEXT = "零一二三四五六七八九"


def _chinese_section_value(value: str) -> int | None:
    total = 0
    digit: int | None = None
    zero_gap = False
    for character in value:
        if character == "零":
            if total == 0 or digit is not None or zero_gap:
                return None
            zero_gap = True
            continue
        if character in _CHINESE_DIGITS:
            if digit is not None:
                return None
            digit = _CHINESE_DIGITS[character]
            zero_gap = False
            continue
        unit = _CHINESE_UNITS.get(character)
        if unit is None or zero_gap:
            return None
        if digit is None:
            if unit != 10 or total != 0:
                return None
            digit = 1
        total += digit * unit
        digit = None
    if zero_gap:
        return None
    return total + (digit or 0)


def _format_chinese_section(value: int, *, omit_leading_one: bool) -> str:
    parts: list[str] = []
    remaining = value
    zero_gap = False
    for divisor, suffix in ((1000, "千"), (100, "百"), (10, "十"), (1, "")):
        digit, remaining = divmod(remaining, divisor)
        if digit:
            if zero_gap:
                parts.append("零")
            if not (divisor == 10 and digit == 1 and not parts and omit_leading_one):
                parts.append(_CHINESE_DIGIT_TEXT[digit])
            parts.append(suffix)
            zero_gap = False
        elif parts and remaining:
            zero_gap = True
    return "".join(parts)


def _chinese_ordinal_value(value: str) -> int | None:
    normalized = value.replace("两", "二").replace("〇", "零")
    if normalized.count("万") > 1:
        return None
    if "万" in normalized:
        high_text, low_text = normalized.split("万")
        high = _chinese_section_value(high_text)
        low = _chinese_section_value(low_text) if low_text else 0
        if high is None or high == 0 or low is None:
            return None
        result = high * 10_000 + low
        canonical = _format_chinese_section(high, omit_leading_one=True) + "万"
        if low:
            if low < 1000:
                canonical += "零"
            canonical += _format_chinese_section(low, omit_leading_one=False)
    else:
        result = _chinese_section_value(normalized)
        if result is None:
            return None
        canonical = _format_chinese_section(result, omit_leading_one=True)
    if result <= 0 or result >= 100_000_000 or canonical != normalized:
        return None
    return result


class FormatLetterNoticeVariant(str, Enum):
    REJECTION_DECISION = "REJECTION_DECISION"
    PRELIMINARY_PASS = "PRELIMINARY_PASS"
    PUBLICATION_NOTICE = "PUBLICATION_NOTICE"
    SUBSTANTIVE_ENTRY_NOTICE = "SUBSTANTIVE_ENTRY_NOTICE"
    ACCEPTANCE_NOTICE = "ACCEPTANCE_NOTICE"
    GRANT_REGISTRATION_NOTICE = "GRANT_REGISTRATION_NOTICE"
    OA_FIRST = "OA_FIRST"
    OA_SUBSEQUENT = "OA_SUBSEQUENT"
    REEXAMINATION_NOTICE = "REEXAMINATION_NOTICE"
    PATENT_CERTIFICATE = "PATENT_CERTIFICATE"


@dataclass(frozen=True, slots=True)
class BuildFormatLetterContextCommand:
    case_id: str
    source_document_id: str
    selected_contact_id: str | None = None


@dataclass(frozen=True, slots=True)
class FormatLetterContextResult:
    case_id: str
    source_document_id: str
    source_evidence_version_id: str
    mapping_id: str
    template_id: str
    template_family_code: str
    template_variant_code: str
    template_file_path: str
    notice_variant: FormatLetterNoticeVariant
    selected_contact_id: str | None
    contact_selection_source: str
    salutation_source: str
    context: Mapping[str, str]


def _error(
    code: str,
    *,
    status_code: int,
    field: str | None = None,
) -> BusinessError:
    return BusinessError(
        code=code,
        message=code,
        details={"field": field} if field is not None else None,
        status_code=status_code,
    )


def _text(value: object) -> str:
    return value.strip() if type(value) is str else ""


def _code(value: object) -> str:
    return _text(value).upper()


def _validate_command(command: object) -> BuildFormatLetterContextCommand:
    if type(command) is not BuildFormatLetterContextCommand:
        raise _error(
            "FORMAT_LETTER_CONTEXT_INVALID",
            status_code=400,
            field="command",
        )
    for field_name in ("case_id", "source_document_id"):
        value = getattr(command, field_name)
        if type(value) is not str or not value or value != value.strip() or len(value) > 36:
            raise _error(
                "FORMAT_LETTER_CONTEXT_INVALID",
                status_code=400,
                field=field_name,
            )
    selected_contact_id = command.selected_contact_id
    if selected_contact_id is not None and (
        type(selected_contact_id) is not str
        or not selected_contact_id
        or selected_contact_id != selected_contact_id.strip()
        or len(selected_contact_id) > 36
    ):
        raise _error(
            "FORMAT_LETTER_CONTEXT_INVALID",
            status_code=400,
            field="selected_contact_id",
        )
    return command


def _eligible_evidence_statement():
    return (
        DocumentEvidenceVersion.role == "OFFICIAL_FINAL_PDF",
        DocumentEvidenceVersion.state == "FINAL",
        DocumentEvidenceVersion.review_state == "APPROVED",
        DocumentEvidenceVersion.current_identity_key.is_not(None),
    )


def _select_source_evidence(
    transaction: Session,
    *,
    case_id: str,
    source: Document,
) -> DocumentEvidenceVersion:
    rows = (
        transaction.execute(
            select(DocumentEvidenceVersion).where(
                DocumentEvidenceVersion.case_id == case_id,
                DocumentEvidenceVersion.document_id == source.id,
                *_eligible_evidence_statement(),
            )
        )
        .scalars()
        .all()
    )
    if not rows:
        raise _error("FORMAT_LETTER_SOURCE_UNREVIEWED", status_code=409)
    if len(rows) > 1:
        raise _error("FORMAT_LETTER_SOURCE_EVIDENCE_AMBIGUOUS", status_code=409)
    return rows[0]


def _require_latest_source(
    transaction: Session,
    *,
    case_id: str,
    source_id: str,
) -> None:
    latest = transaction.scalar(
        select(Document)
        .join(
            DocumentEvidenceVersion,
            DocumentEvidenceVersion.document_id == Document.id,
        )
        .where(
            Document.case_id == case_id,
            func.upper(func.trim(Document.direction)) == "IN",
            Document.doc_date.is_not(None),
            DocumentEvidenceVersion.case_id == case_id,
            *_eligible_evidence_statement(),
        )
        .group_by(Document.id)
        .having(func.count(DocumentEvidenceVersion.id) == 1)
        .order_by(
            Document.doc_date.desc(),
            Document.created_at.desc(),
            Document.id.desc(),
        )
        .limit(1)
    )
    if latest is None or latest.id != source_id:
        raise _error("FORMAT_LETTER_SOURCE_NOT_LATEST", status_code=409)


def _document_template_code(transaction: Session, source: Document) -> str:
    if not source.doc_template_id:
        return ""
    template = transaction.get(DocTemplate, source.doc_template_id)
    return _code(template.code) if template is not None else ""


def _select_mapping(
    transaction: Session,
    *,
    source: Document,
) -> FormatLetterMapping:
    mappings = (
        transaction.execute(
            select(FormatLetterMapping).where(FormatLetterMapping.enabled.is_(True))
        )
        .scalars()
        .all()
    )
    title = _text(source.title)
    doc_template_code = _document_template_code(transaction, source)
    levels = (
        [
            mapping
            for mapping in mappings
            if source.doc_template_id and mapping.official_doc_template_id == source.doc_template_id
        ],
        [
            mapping
            for mapping in mappings
            if doc_template_code and _code(mapping.official_doc_template_code) == doc_template_code
        ],
        [
            mapping
            for mapping in mappings
            if _text(mapping.official_doc_name_pattern)
            and _text(mapping.official_doc_name_pattern) == title
        ],
        [
            mapping
            for mapping in mappings
            if _text(mapping.official_doc_name_pattern)
            and _text(mapping.official_doc_name_pattern) in title
        ],
    )
    for matches in levels:
        if not matches:
            continue
        if len(matches) > 1:
            raise _error("FORMAT_LETTER_MAPPING_AMBIGUOUS", status_code=409)
        return matches[0]
    raise _error("FORMAT_LETTER_MAPPING_MISSING", status_code=409)


def _select_template(
    transaction: Session,
    mapping: FormatLetterMapping,
) -> tuple[Template, str]:
    mapping_id = _text(mapping.id)
    template_id = _text(mapping.format_letter_template_id)
    template_code = mapping.format_letter_template_code
    if (
        not mapping_id
        or not template_id
        or not isinstance(template_code, str)
        or template_code not in _TEMPLATE_CODES
    ):
        raise _error("FORMAT_LETTER_TEMPLATE_INVALID", status_code=409)
    template = transaction.get(Template, template_id)
    if (
        template is None
        or type(template.enabled) is not bool
        or not template.enabled
        or template.group != "FORMAT_LETTER"
        or template.name != template_code
        or not _text(template.file_path)
    ):
        raise _error("FORMAT_LETTER_TEMPLATE_INVALID", status_code=409)
    return template, template_code


def _notice_variant(
    *,
    template_code: str,
    title: str,
) -> FormatLetterNoticeVariant:
    exact = _NOTICE_BY_TEMPLATE_AND_TITLE.get((template_code, title))
    if exact is not None:
        return FormatLetterNoticeVariant(exact)
    if template_code == "FORMAT_LETTER_007":
        if title == "第一次审查意见通知书":
            return FormatLetterNoticeVariant.OA_FIRST
        if title == "复审通知书":
            return FormatLetterNoticeVariant.REEXAMINATION_NOTICE
        arabic = _OA_ARABIC_TITLE.fullmatch(title)
        if arabic is not None and int(arabic.group(1)) > 1:
            return FormatLetterNoticeVariant.OA_SUBSEQUENT
        chinese = _OA_CHINESE_TITLE.fullmatch(title)
        chinese_value = _chinese_ordinal_value(chinese.group(1)) if chinese is not None else None
        if chinese_value is not None and chinese_value > 1:
            return FormatLetterNoticeVariant.OA_SUBSEQUENT
    raise _error("FORMAT_LETTER_NOTICE_VARIANT_INVALID", status_code=409)


def _ordered_names(rows: list[T_CaseApplicant] | list[T_CaseInventor]) -> list[str]:
    return [name for row in rows if (name := (_text(row.name_cn) or _text(row.name_en)))]


def _case_context(
    transaction: Session,
    *,
    case: Case,
    source: Document,
    template_code: str,
) -> dict[str, str]:
    case_no = _text(case.case_no)
    if not case_no:
        raise _error(
            "FORMAT_LETTER_CASE_CONTEXT_MISSING",
            status_code=409,
            field="case_no",
        )
    invention_title = _text(case.title_cn) or _text(case.title_en)
    if not invention_title:
        raise _error(
            "FORMAT_LETTER_CASE_CONTEXT_MISSING",
            status_code=409,
            field="invention_title",
        )
    application_no = _text(case.app_no)
    if not application_no:
        raise _error(
            "FORMAT_LETTER_CASE_CONTEXT_MISSING",
            status_code=409,
            field="application_no",
        )
    source_notice_name = _text(source.title)
    if not source_notice_name:
        raise _error(
            "FORMAT_LETTER_CASE_CONTEXT_MISSING",
            status_code=409,
            field="source_notice_name",
        )

    applicants = (
        transaction.execute(
            select(T_CaseApplicant)
            .where(T_CaseApplicant.case_id == case.id)
            .order_by(T_CaseApplicant.seq.asc(), T_CaseApplicant.id.asc())
        )
        .scalars()
        .all()
    )
    first_markers = [row for row in applicants if row.is_first]
    if len(first_markers) > 1 or (
        first_markers and applicants and first_markers[0].seq != applicants[0].seq
    ):
        raise _error("FORMAT_LETTER_APPLICANT_CONFLICT", status_code=409)
    applicant_names = _ordered_names(applicants)
    if not applicant_names:
        raise _error("FORMAT_LETTER_APPLICANT_MISSING", status_code=409)

    inventor_names: list[str] = []
    if template_code in {"FORMAT_LETTER_005", "FORMAT_LETTER_008"}:
        inventors = (
            transaction.execute(
                select(T_CaseInventor)
                .where(T_CaseInventor.case_id == case.id)
                .order_by(T_CaseInventor.seq.asc(), T_CaseInventor.id.asc())
            )
            .scalars()
            .all()
        )
        inventor_names = _ordered_names(inventors)
        if not inventor_names:
            raise _error(
                "FORMAT_LETTER_CASE_CONTEXT_MISSING",
                status_code=409,
                field="inventor_names_text",
            )

    publication_date_text = ""
    if template_code == "FORMAT_LETTER_003":
        if type(case.pub_date) is not date:
            raise _error(
                "FORMAT_LETTER_CASE_CONTEXT_MISSING",
                status_code=409,
                field="publication_date_text",
            )
        publication_date_text = case.pub_date.isoformat()

    return {
        "client_reference_no": "",
        "case_no": case_no,
        "invention_title": invention_title,
        "application_no": application_no,
        "filing_date_text": (
            case.filing_date.isoformat() if type(case.filing_date) is date else ""
        ),
        "applicant_names_text": "、".join(applicant_names),
        "inventor_names_text": "、".join(inventor_names),
        "source_notice_name": source_notice_name,
        "publication_date_text": publication_date_text,
    }


def _contact_context(
    transaction: Session,
    *,
    case: Case,
    selected_contact_id: str | None,
) -> tuple[str | None, str, str, str]:
    contact: ClientContact | None = None
    selection_source = "DEFAULT"
    if selected_contact_id is not None:
        contact = transaction.get(ClientContact, selected_contact_id)
        if contact is None:
            raise _error("FORMAT_LETTER_CONTACT_NOT_FOUND", status_code=404)
        if not case.client_id or contact.client_id != case.client_id:
            raise _error("FORMAT_LETTER_CONTACT_CASE_MISMATCH", status_code=400)
        selection_source = "EXPLICIT"
    elif case.client_id:
        primary = (
            transaction.execute(
                select(ClientContact).where(
                    ClientContact.client_id == case.client_id,
                    ClientContact.is_primary.is_(True),
                )
            )
            .scalars()
            .all()
        )
        if len(primary) > 1:
            raise _error("FORMAT_LETTER_PRIMARY_CONTACT_AMBIGUOUS", status_code=409)
        if primary:
            contact = primary[0]
            selection_source = "PRIMARY"

    if contact is None:
        return None, selection_source, "DEFAULT", "尊敬的：您好"
    name = _text(contact.contact_name)
    if not name:
        raise _error("FORMAT_LETTER_CONTACT_INVALID", status_code=409)
    title = _text(contact.title)
    return (
        contact.id,
        selection_source,
        "SELECTED_CONTACT",
        f"尊敬的{name}{title}：您好",
    )


def _deadline(source: Document, template_code: str) -> date | None:
    if template_code not in _DEADLINE_TEMPLATE_CODES:
        return None
    try:
        parsed = parse_document_extra_data(source.extra_data)
    except DocumentExtraDataError as exc:
        raise _error("FORMAT_LETTER_DEADLINE_UNCONFIRMED", status_code=409) from exc
    if parsed.was_legacy_text:
        raise _error("FORMAT_LETTER_DEADLINE_UNCONFIRMED", status_code=409)
    if parsed.official_due_date is None:
        raise _error("FORMAT_LETTER_DEADLINE_MISSING", status_code=409)
    if parsed.official_due_date_status != "CONFIRMED" or parsed.official_due_date_source not in {
        "MANUAL_OFFICIAL_NOTICE",
        "IMPORTED_OFFICIAL_NOTICE",
    }:
        raise _error("FORMAT_LETTER_DEADLINE_UNCONFIRMED", status_code=409)
    return parsed.official_due_date


def _effective_grant_obligations(
    transaction: Session,
    *,
    case_id: str,
    source_document_id: str,
) -> list[FeeObligation]:
    candidates = (
        transaction.execute(
            select(FeeObligation).where(
                FeeObligation.case_id == case_id,
                FeeObligation.source_document_id == source_document_id,
                FeeObligation.fee_domain == "GOV",
                FeeObligation.obligation_status == "RECOGNIZED",
                FeeObligation.source_status == "VERIFIED",
            )
        )
        .scalars()
        .all()
    )
    superseded_ids = set(
        transaction.scalars(
            select(FeeObligation.supersedes_obligation_id).where(
                FeeObligation.case_id == case_id,
                FeeObligation.supersedes_obligation_id.is_not(None),
            )
        )
    )
    return [row for row in candidates if row.id not in superseded_ids]


def _amount_lines(
    transaction: Session,
    *,
    case_id: str,
    source_document_id: str,
    template_code: str,
    confirmed_deadline: date | None,
) -> str:
    if template_code != "FORMAT_LETTER_006":
        return ""
    obligations = _effective_grant_obligations(
        transaction,
        case_id=case_id,
        source_document_id=source_document_id,
    )
    if not obligations:
        raise _error("FORMAT_LETTER_AMOUNT_MISSING", status_code=409)
    if len(obligations) > 1:
        raise _error("FORMAT_LETTER_AMOUNT_CONFLICT", status_code=409)
    obligation = obligations[0]
    if obligation.due_date is None or obligation.due_date != confirmed_deadline:
        raise _error("FORMAT_LETTER_DEADLINE_CONFLICT", status_code=409)
    if obligation.currency != "CNY":
        raise _error("FORMAT_LETTER_AMOUNT_CONFLICT", status_code=409)

    lines = (
        transaction.execute(
            select(FeeObligationLine)
            .where(
                FeeObligationLine.case_id == case_id,
                FeeObligationLine.obligation_id == obligation.id,
                FeeObligationLine.current_identity_key.is_not(None),
            )
            .order_by(
                FeeObligationLine.fee_year_key.asc(),
                FeeObligationLine.fee_code.asc(),
                FeeObligationLine.id.asc(),
            )
        )
        .scalars()
        .all()
    )
    if not lines:
        raise _error("FORMAT_LETTER_AMOUNT_MISSING", status_code=409)
    rendered: list[str] = []
    for line in lines:
        if line.source_amount is None:
            raise _error("FORMAT_LETTER_AMOUNT_UNVERIFIED", status_code=409)
        amount = line.source_amount
        if (
            type(amount) is not Decimal
            or not amount.is_finite()
            or amount < 0
            or amount.as_tuple().exponent < -2
            or line.difference_review_state not in {"MATCHED", "SOURCE_PENDING"}
            or not _text(line.fee_name)
        ):
            raise _error("FORMAT_LETTER_AMOUNT_CONFLICT", status_code=409)
        rendered.append(f"{_text(line.fee_name)}：{amount:,.2f} 元")
    return "\n".join(rendered)


def build_format_letter_context(
    command: BuildFormatLetterContextCommand,
    transaction: Session,
) -> FormatLetterContextResult:
    command = _validate_command(command)
    case = transaction.get(Case, command.case_id)
    if case is None:
        raise _error("CASE_NOT_FOUND", status_code=404)
    source = transaction.get(Document, command.source_document_id)
    if source is None:
        raise _error("FORMAT_LETTER_SOURCE_NOT_FOUND", status_code=404)
    if source.case_id != case.id:
        raise _error("FORMAT_LETTER_SOURCE_CASE_MISMATCH", status_code=400)
    if _code(source.direction) != "IN":
        raise _error("FORMAT_LETTER_SOURCE_DIRECTION_INVALID", status_code=400)

    evidence = _select_source_evidence(
        transaction,
        case_id=case.id,
        source=source,
    )
    _require_latest_source(
        transaction,
        case_id=case.id,
        source_id=source.id,
    )
    mapping = _select_mapping(transaction, source=source)
    template, template_code = _select_template(transaction, mapping)
    title = _text(source.title)
    notice_variant = _notice_variant(
        template_code=template_code,
        title=title,
    )
    case_context = _case_context(
        transaction,
        case=case,
        source=source,
        template_code=template_code,
    )
    (
        selected_contact_id,
        contact_selection_source,
        salutation_source,
        salutation_text,
    ) = _contact_context(
        transaction,
        case=case,
        selected_contact_id=command.selected_contact_id,
    )
    deadline = _deadline(source, template_code)
    amount_lines_text = _amount_lines(
        transaction,
        case_id=case.id,
        source_document_id=source.id,
        template_code=template_code,
        confirmed_deadline=deadline,
    )
    context = MappingProxyType(
        {
            "salutation_text": salutation_text,
            "client_reference_no": case_context["client_reference_no"],
            "case_no": case_context["case_no"],
            "invention_title": case_context["invention_title"],
            "application_no": case_context["application_no"],
            "filing_date_text": case_context["filing_date_text"],
            "applicant_names_text": case_context["applicant_names_text"],
            "inventor_names_text": case_context["inventor_names_text"],
            "source_notice_name": case_context["source_notice_name"],
            "notice_variant_code": notice_variant.value,
            "publication_date_text": case_context["publication_date_text"],
            "deadline_text": deadline.isoformat() if deadline is not None else "",
            "amount_lines_text": amount_lines_text,
            "template_variant_code": template_code,
        }
    )
    return FormatLetterContextResult(
        case_id=case.id,
        source_document_id=source.id,
        source_evidence_version_id=evidence.id,
        mapping_id=mapping.id,
        template_id=template.id,
        template_family_code="FORMAT_LETTER",
        template_variant_code=template_code,
        template_file_path=_text(template.file_path),
        notice_variant=notice_variant,
        selected_contact_id=selected_contact_id,
        contact_selection_source=contact_selection_source,
        salutation_source=salutation_source,
        context=context,
    )


__all__ = (
    "BuildFormatLetterContextCommand",
    "FormatLetterContextResult",
    "FormatLetterNoticeVariant",
    "build_format_letter_context",
)
