from __future__ import annotations

import importlib
import inspect
import json
from dataclasses import fields, is_dataclass, replace
from datetime import date, datetime, timezone
from decimal import Decimal
from enum import Enum
from types import MappingProxyType
from typing import cast, get_type_hints

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from app.core.errors import BusinessError
from app.modules.cases.models import Case, CaseActivityEvent, T_CaseApplicant, T_CaseInventor
from app.modules.documents.models import (
    DocAttachment,
    DocTemplate,
    Document,
    DocumentEvidenceVersion,
)
from app.modules.fees.models import FeeObligation, FeeObligationLine
from app.modules.masterdata.clients.models import Client, ClientContact
from app.modules.templates.models import FormatLetterMapping, Template

CASE_ID = "00000000-0000-0000-0000-000000000001"
OTHER_CASE_ID = "00000000-0000-0000-0000-000000000002"
CLIENT_ID = "00000000-0000-0000-0000-000000000003"
OTHER_CLIENT_ID = "00000000-0000-0000-0000-000000000004"
SOURCE_ID = "00000000-0000-0000-0000-000000000005"
DOC_TEMPLATE_ID = "00000000-0000-0000-0000-000000000006"
EVIDENCE_ID = "00000000-0000-0000-0000-000000000007"
ATTACHMENT_ID = "00000000-0000-0000-0000-000000000008"
MAPPING_ID = "00000000-0000-0000-0000-000000000009"
TEMPLATE_ID = "00000000-0000-0000-0000-000000000010"
CONTACT_ID = "00000000-0000-0000-0000-000000000011"
ACTIVITY_ID = "00000000-0000-0000-0000-000000000012"
OBLIGATION_ID = "00000000-0000-0000-0000-000000000013"

EXPECTED_KEYS = (
    "salutation_text",
    "client_reference_no",
    "case_no",
    "invention_title",
    "application_no",
    "filing_date_text",
    "applicant_names_text",
    "inventor_names_text",
    "source_notice_name",
    "notice_variant_code",
    "publication_date_text",
    "deadline_text",
    "amount_lines_text",
    "template_variant_code",
)


def _module():
    return importlib.import_module("app.modules.documents.letter_context")


def _deadline(value: str = "2026-09-30", *, status: str = "CONFIRMED") -> str:
    return json.dumps(
        {
            "OfficialDueDate": value,
            "OfficialDueDateSource": "MANUAL_OFFICIAL_NOTICE",
            "OfficialDueDateStatus": status,
        }
    )


def _seed(
    db: Session,
    *,
    template_code: str = "FORMAT_LETTER_002",
    title: str = "初步审查合格",
    direction: str = "IN",
    extra_data: str | None = None,
    with_client: bool = True,
) -> dict[str, object]:
    client = Client(
        id=CLIENT_ID,
        client_code="CLIENT-1",
        name_cn="客户一",
        client_type="CLIENT",
        default_currency="CNY",
        is_active=True,
    )
    case = Case(
        id=CASE_ID,
        case_no=" CASE-001 ",
        status="OPEN",
        client_id=CLIENT_ID if with_client else None,
        title_cn=" 发明名称 ",
        title_en="English invention",
        app_no=" APP-001 ",
        filing_date=date(2025, 1, 2),
        pub_date=date(2026, 3, 4),
    )
    doc_template = DocTemplate(
        id=DOC_TEMPLATE_ID,
        code="OFFICIAL-IN-001",
        name="官方来文",
        direction="IN",
        enabled=True,
    )
    source = Document(
        id=SOURCE_ID,
        case_id=CASE_ID,
        doc_template_id=DOC_TEMPLATE_ID,
        direction=direction,
        doc_date=date(2026, 7, 18),
        title=title,
        extra_data=extra_data,
        created_at=datetime(2026, 7, 18, 10, 0, tzinfo=timezone.utc),
        updated_at=datetime(2026, 7, 18, 10, 0, tzinfo=timezone.utc),
    )
    attachment = DocAttachment(
        id=ATTACHMENT_ID,
        document_id=SOURCE_ID,
        file_name="official.pdf",
        file_path="/evidence/official.pdf",
        content_hash=f"sha256:{'a' * 64}",
    )
    evidence = DocumentEvidenceVersion(
        id=EVIDENCE_ID,
        case_id=CASE_ID,
        document_id=SOURCE_ID,
        attachment_id=ATTACHMENT_ID,
        lineage_key="official:source",
        role="OFFICIAL_FINAL_PDF",
        version_number=1,
        state="FINAL",
        creator_id="creator",
        review_state="APPROVED",
        reviewer_id="reviewer",
        reviewed_at=datetime(2026, 7, 18, 10, 5),
        content_hash=f"sha256:{'a' * 64}",
        current_identity_key="official:source:current",
    )
    template = Template(
        id=TEMPLATE_ID,
        name=template_code,
        group="FORMAT_LETTER",
        language="zh-CN",
        file_path=f"/templates/{template_code}.docx",
        enabled=True,
    )
    mapping = FormatLetterMapping(
        id=MAPPING_ID,
        official_doc_name_pattern=title,
        format_letter_template_id=TEMPLATE_ID,
        format_letter_template_code=template_code,
        enabled=True,
    )
    applicant = T_CaseApplicant(
        id="00000000-0000-0000-0000-000000000014",
        case_id=CASE_ID,
        seq=1,
        is_first=True,
        name_cn="申请人甲",
    )
    if with_client:
        db.add(client)
        db.flush()
    db.add_all([case, doc_template, template])
    db.flush()
    db.add_all(
        [
            source,
            mapping,
            applicant,
        ]
    )
    if template_code in {"FORMAT_LETTER_005", "FORMAT_LETTER_008"}:
        db.add(
            T_CaseInventor(
                id="00000000-0000-0000-0000-000000000015",
                case_id=CASE_ID,
                seq=1,
                name_cn="发明人甲",
            )
        )
    db.flush()
    db.add(attachment)
    db.flush()
    db.add(evidence)
    db.flush()
    return {
        "case": case,
        "source": source,
        "evidence": evidence,
        "mapping": mapping,
        "template": template,
    }


def _command(*, selected_contact_id: str | None = None):
    return _module().BuildFormatLetterContextCommand(
        case_id=CASE_ID,
        source_document_id=SOURCE_ID,
        selected_contact_id=selected_contact_id,
    )


def _build(db: Session, *, selected_contact_id: str | None = None):
    return _module().build_format_letter_context(
        _command(selected_contact_id=selected_contact_id),
        db,
    )


def _assert_error(
    code: str,
    status: int,
    callable_: object,
    *,
    field: str | None = None,
) -> BusinessError:
    with pytest.raises(BusinessError) as caught:
        cast(object, callable_)()
    error = caught.value
    assert error.code == code
    assert error.status_code == status
    if field is not None:
        assert error.details == {"field": field}
    return error


def _add_eligible_source(
    db: Session,
    *,
    number: int,
    doc_date: date | None,
    created_at: datetime,
    case_id: str = CASE_ID,
) -> Document:
    document_id = f"10000000-0000-0000-0000-{number:012d}"
    attachment_id = f"20000000-0000-0000-0000-{number:012d}"
    document = Document(
        id=document_id,
        case_id=case_id,
        doc_template_id=DOC_TEMPLATE_ID,
        direction="IN",
        doc_date=doc_date,
        title="初步审查合格",
        created_at=created_at,
        updated_at=created_at,
    )
    db.add(document)
    db.flush()
    db.add(
        DocAttachment(
            id=attachment_id,
            document_id=document_id,
            file_name=f"{number}.pdf",
            file_path=f"/evidence/{number}.pdf",
        )
    )
    db.flush()
    db.add(
        DocumentEvidenceVersion(
            id=f"30000000-0000-0000-0000-{number:012d}",
            case_id=case_id,
            document_id=document_id,
            attachment_id=attachment_id,
            lineage_key=f"official:{number}",
            role="OFFICIAL_FINAL_PDF",
            version_number=1,
            state="FINAL",
            creator_id="creator",
            review_state="APPROVED",
            reviewer_id="reviewer",
            reviewed_at=datetime(2026, 7, 18, 10, 5),
            content_hash=f"sha256:{number:064x}",
            current_identity_key=f"official:{number}:current",
        )
    )
    db.flush()
    return document


def _add_grant_obligation(
    db: Session,
    *,
    obligation_id: str = OBLIGATION_ID,
    due_date: date = date(2026, 9, 30),
    currency: str = "CNY",
    source_status: str = "VERIFIED",
    supersedes_obligation_id: str | None = None,
    line_specs: tuple[tuple[str, str, int, Decimal | None, Decimal, str], ...] = (
        ("ANNUITY", "年费", 2, Decimal("1200.00"), Decimal("9999.00"), "MATCHED"),
        ("REGISTRATION", "登记费", 1, Decimal("200.50"), Decimal("8888.00"), "SOURCE_PENDING"),
    ),
) -> FeeObligation:
    if db.get(CaseActivityEvent, ACTIVITY_ID) is None:
        db.add(
            CaseActivityEvent(
                id=ACTIVITY_ID,
                case_id=CASE_ID,
                sequence=1,
                lane="FEE",
                activity_type="GRANT_FEE_RECOGNIZED",
                effective_at=datetime(2026, 7, 18, 11, 0),
                confirmation_status="CONFIRMED",
                actor_id="actor",
                idempotency_key="grant-fee",
                payload_json="{}",
            )
        )
        db.flush()
    obligation = FeeObligation(
        id=obligation_id,
        case_id=CASE_ID,
        source_activity_id=ACTIVITY_ID,
        source_document_id=SOURCE_ID,
        fee_domain="GOV",
        obligation_type="GRANT_YEAR",
        obligation_status="RECOGNIZED",
        due_date=due_date,
        currency=currency,
        source_status=source_status,
        client_instruction_status="PENDING",
        draft_status="NOT_CREATED",
        payment_status="UNPAID",
        official_evidence_status="CONFIRMED",
        supersedes_obligation_id=supersedes_obligation_id,
    )
    db.add(obligation)
    db.flush()
    obligation_number = int(obligation_id[-12:])
    for index, (code, name, year, source, payable, review) in enumerate(line_specs, 1):
        db.add(
            FeeObligationLine(
                id=f"40000000-0000-0000-{index:04d}-{obligation_number:012d}",
                obligation_id=obligation_id,
                case_id=CASE_ID,
                source_activity_id=ACTIVITY_ID,
                fee_code=code,
                fee_name=name,
                fee_year_key=year,
                official_full_amount=payable,
                reduction_ratio=Decimal("0"),
                payable_amount=payable,
                source_amount=source,
                difference_review_state=review,
                current_identity_key=f"grant:{obligation_number}:{index}",
            )
        )
    db.flush()
    return obligation


def test_public_contract_is_exact() -> None:
    module = _module()

    assert issubclass(module.FormatLetterNoticeVariant, str)
    assert issubclass(module.FormatLetterNoticeVariant, Enum)
    assert tuple(member.value for member in module.FormatLetterNoticeVariant) == (
        "REJECTION_DECISION",
        "PRELIMINARY_PASS",
        "PUBLICATION_NOTICE",
        "SUBSTANTIVE_ENTRY_NOTICE",
        "ACCEPTANCE_NOTICE",
        "GRANT_REGISTRATION_NOTICE",
        "OA_FIRST",
        "OA_SUBSEQUENT",
        "REEXAMINATION_NOTICE",
        "PATENT_CERTIFICATE",
    )
    for type_, expected in (
        (
            module.BuildFormatLetterContextCommand,
            ("case_id", "source_document_id", "selected_contact_id"),
        ),
        (
            module.FormatLetterContextResult,
            (
                "case_id",
                "source_document_id",
                "source_evidence_version_id",
                "mapping_id",
                "template_id",
                "template_family_code",
                "template_variant_code",
                "template_file_path",
                "notice_variant",
                "selected_contact_id",
                "contact_selection_source",
                "salutation_source",
                "context",
            ),
        ),
    ):
        assert is_dataclass(type_)
        assert type_.__dataclass_params__.frozen is True
        assert type_.__slots__ == expected
        assert tuple(field.name for field in fields(type_)) == expected
    signature = inspect.signature(module.build_format_letter_context)
    assert tuple(signature.parameters) == ("command", "transaction")
    assert get_type_hints(module.build_format_letter_context) == {
        "command": module.BuildFormatLetterContextCommand,
        "transaction": Session,
        "return": module.FormatLetterContextResult,
    }


def test_success_returns_fresh_immutable_exact_context_and_is_read_only(
    session_factory: sessionmaker,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with session_factory() as db:
        seeded = _seed(db)
        db.autoflush = False

        def forbidden(*_args: object, **_kwargs: object) -> None:
            raise AssertionError("format-letter context builder must remain read-only")

        for name in ("add", "delete", "flush", "commit", "rollback"):
            monkeypatch.setattr(db, name, forbidden)

        result = _build(db)
        second = _build(db)

        assert result.case_id == CASE_ID
        assert result.source_document_id == SOURCE_ID
        assert result.source_evidence_version_id == EVIDENCE_ID
        assert result.mapping_id == MAPPING_ID
        assert result.template_id == TEMPLATE_ID
        assert result.template_family_code == "FORMAT_LETTER"
        assert result.template_variant_code == "FORMAT_LETTER_002"
        assert result.template_file_path == "/templates/FORMAT_LETTER_002.docx"
        assert result.notice_variant is _module().FormatLetterNoticeVariant.PRELIMINARY_PASS
        assert result.selected_contact_id is None
        assert result.contact_selection_source == "DEFAULT"
        assert result.salutation_source == "DEFAULT"
        assert type(result.context) is MappingProxyType
        assert tuple(result.context) == EXPECTED_KEYS
        assert result.context == {
            "salutation_text": "尊敬的：您好",
            "client_reference_no": "",
            "case_no": "CASE-001",
            "invention_title": "发明名称",
            "application_no": "APP-001",
            "filing_date_text": "2025-01-02",
            "applicant_names_text": "申请人甲",
            "inventor_names_text": "",
            "source_notice_name": "初步审查合格",
            "notice_variant_code": "PRELIMINARY_PASS",
            "publication_date_text": "",
            "deadline_text": "",
            "amount_lines_text": "",
            "template_variant_code": "FORMAT_LETTER_002",
        }
        assert second.context == result.context
        assert second.context is not result.context
        with pytest.raises(TypeError):
            cast(dict[str, str], result.context)["case_no"] = "changed"
        assert not db.new and not db.dirty and not db.deleted
        assert seeded["case"] is not None


@pytest.mark.parametrize(
    ("field_name", "value"),
    (
        ("case_id", ""),
        ("case_id", " case "),
        ("case_id", "x" * 37),
        ("source_document_id", ""),
        ("source_document_id", " source "),
        ("source_document_id", "x" * 37),
        ("selected_contact_id", ""),
        ("selected_contact_id", " contact "),
        ("selected_contact_id", "x" * 37),
    ),
)
def test_invalid_command_fields_fail_first(
    session_factory: sessionmaker,
    field_name: str,
    value: str,
) -> None:
    with session_factory() as db:
        command = _module().BuildFormatLetterContextCommand(
            case_id=CASE_ID,
            source_document_id=SOURCE_ID,
        )
        command = replace(command, **{field_name: value})
        _assert_error(
            "FORMAT_LETTER_CONTEXT_INVALID",
            400,
            lambda: _module().build_format_letter_context(command, db),
            field=field_name,
        )


def test_non_exact_command_fails_closed(session_factory: sessionmaker) -> None:
    with session_factory() as db:
        _assert_error(
            "FORMAT_LETTER_CONTEXT_INVALID",
            400,
            lambda: _module().build_format_letter_context(cast(object, {}), db),
            field="command",
        )


def test_source_lookup_case_direction_and_latest_order(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as db:
        _assert_error(
            "CASE_NOT_FOUND",
            404,
            lambda: _module().build_format_letter_context(_command(), db),
        )
        db.add(
            Case(
                id=CASE_ID,
                case_no="CASE-LOOKUP",
                status="OPEN",
                title_cn="标题",
                app_no="APP",
            )
        )
        db.flush()
        _assert_error(
            "FORMAT_LETTER_SOURCE_NOT_FOUND",
            404,
            lambda: _module().build_format_letter_context(_command(), db),
        )

    with session_factory() as db:
        seeded = _seed(db)
        source = cast(Document, seeded["source"])
        db.add(Case(id=OTHER_CASE_ID, case_no="OTHER", status="OPEN"))
        db.flush()
        source.case_id = OTHER_CASE_ID
        db.flush()
        _assert_error(
            "FORMAT_LETTER_SOURCE_CASE_MISMATCH",
            400,
            lambda: _build(db),
        )

    with session_factory() as db:
        seeded = _seed(db, direction=" out ")
        assert seeded
        _assert_error(
            "FORMAT_LETTER_SOURCE_DIRECTION_INVALID",
            400,
            lambda: _build(db),
        )

    with session_factory() as db:
        _seed(db)
        _add_eligible_source(
            db,
            number=2,
            doc_date=date(2026, 7, 19),
            created_at=datetime(2026, 7, 17, 9, 0, tzinfo=timezone.utc),
        )
        _assert_error("FORMAT_LETTER_SOURCE_NOT_LATEST", 409, lambda: _build(db))

    with session_factory() as db:
        _seed(db)
        _add_eligible_source(
            db,
            number=3,
            doc_date=None,
            created_at=datetime(2026, 7, 20, 9, 0, tzinfo=timezone.utc),
        )
        assert _build(db).source_document_id == SOURCE_ID


@pytest.mark.parametrize(
    ("field_name", "value"),
    (
        ("role", "SUBMITTED_XML"),
        ("state", "DRAFT"),
        ("review_state", "PENDING"),
        ("current_identity_key", None),
        ("case_id", OTHER_CASE_ID),
        ("document_id", "00000000-0000-0000-0000-000000000099"),
    ),
)
def test_source_requires_exact_current_approved_official_pdf_shape(
    session_factory: sessionmaker,
    field_name: str,
    value: object,
) -> None:
    with session_factory() as db:
        seeded = _seed(db)
        evidence = cast(DocumentEvidenceVersion, seeded["evidence"])
        if field_name == "case_id":
            db.add(Case(id=OTHER_CASE_ID, case_no="OTHER-EVIDENCE", status="OPEN"))
            db.flush()
        if field_name == "document_id":
            db.add(
                Document(
                    id=cast(str, value),
                    case_id=CASE_ID,
                    direction="IN",
                    doc_date=date(2026, 1, 1),
                )
            )
            db.flush()
        setattr(evidence, field_name, value)
        db.flush()
        _assert_error("FORMAT_LETTER_SOURCE_UNREVIEWED", 409, lambda: _build(db))


def test_source_rejects_multiple_eligible_current_rows(session_factory: sessionmaker) -> None:
    with session_factory() as db:
        _seed(db)
        db.add(
            DocumentEvidenceVersion(
                id="00000000-0000-0000-0000-000000000090",
                case_id=CASE_ID,
                document_id=SOURCE_ID,
                attachment_id=ATTACHMENT_ID,
                lineage_key="official:second",
                role="OFFICIAL_FINAL_PDF",
                version_number=2,
                state="FINAL",
                creator_id="creator",
                review_state="APPROVED",
                reviewer_id="reviewer",
                reviewed_at=datetime(2026, 7, 18, 10, 6),
                content_hash=f"sha256:{'b' * 64}",
                current_identity_key="official:second:current",
            )
        )
        db.flush()
        _assert_error(
            "FORMAT_LETTER_SOURCE_EVIDENCE_AMBIGUOUS",
            409,
            lambda: _build(db),
        )


def test_mapping_precedence_and_same_level_ambiguity(session_factory: sessionmaker) -> None:
    with session_factory() as db:
        seeded = _seed(db)
        mapping = cast(FormatLetterMapping, seeded["mapping"])
        mapping.official_doc_name_pattern = "审查"
        db.add_all(
            [
                FormatLetterMapping(
                    id="00000000-0000-0000-0000-000000000070",
                    official_doc_template_code=" official-in-001 ",
                    format_letter_template_id=TEMPLATE_ID,
                    format_letter_template_code="FORMAT_LETTER_002",
                    enabled=True,
                ),
                FormatLetterMapping(
                    id="00000000-0000-0000-0000-000000000071",
                    official_doc_template_id=DOC_TEMPLATE_ID,
                    format_letter_template_id=TEMPLATE_ID,
                    format_letter_template_code="FORMAT_LETTER_002",
                    enabled=True,
                ),
            ]
        )
        db.flush()
        assert _build(db).mapping_id == "00000000-0000-0000-0000-000000000071"

        db.add(
            FormatLetterMapping(
                id="00000000-0000-0000-0000-000000000072",
                official_doc_template_id=DOC_TEMPLATE_ID,
                format_letter_template_id=TEMPLATE_ID,
                format_letter_template_code="FORMAT_LETTER_002",
                enabled=True,
            )
        )
        db.flush()
        _assert_error("FORMAT_LETTER_MAPPING_AMBIGUOUS", 409, lambda: _build(db))


def test_mapping_missing_and_template_link_fail_closed(session_factory: sessionmaker) -> None:
    with session_factory() as db:
        seeded = _seed(db)
        mapping = cast(FormatLetterMapping, seeded["mapping"])
        mapping.enabled = False
        db.flush()
        _assert_error("FORMAT_LETTER_MAPPING_MISSING", 409, lambda: _build(db))

    mutations = (
        ("format_letter_template_id", None),
        ("format_letter_template_code", "FORMAT_LETTER_009"),
        ("format_letter_template_code", " format_letter_002 "),
        ("template_group", "OTHER"),
        ("template_name", "FORMAT_LETTER_001"),
        ("template_file_path", ""),
        ("template_enabled", False),
    )
    for field_name, value in mutations:
        with session_factory() as db:
            seeded = _seed(db)
            mapping = cast(FormatLetterMapping, seeded["mapping"])
            template = cast(Template, seeded["template"])
            if field_name.startswith("template_"):
                setattr(template, field_name.removeprefix("template_"), value)
            else:
                setattr(mapping, field_name, value)
            db.flush()
            _assert_error("FORMAT_LETTER_TEMPLATE_INVALID", 409, lambda: _build(db))


@pytest.mark.parametrize(
    ("template_code", "title", "variant"),
    (
        ("FORMAT_LETTER_001", "驳回决定", "REJECTION_DECISION"),
        ("FORMAT_LETTER_002", "初步审查合格", "PRELIMINARY_PASS"),
        ("FORMAT_LETTER_003", "公布通知书", "PUBLICATION_NOTICE"),
        ("FORMAT_LETTER_004", "进入实审通知", "SUBSTANTIVE_ENTRY_NOTICE"),
        ("FORMAT_LETTER_005", "受理通知-电子", "ACCEPTANCE_NOTICE"),
        ("FORMAT_LETTER_006", "授权通知书-电子", "GRANT_REGISTRATION_NOTICE"),
        ("FORMAT_LETTER_007", "第一次审查意见通知书", "OA_FIRST"),
        ("FORMAT_LETTER_007", "第2次审查意见通知书", "OA_SUBSEQUENT"),
        ("FORMAT_LETTER_007", "第三次审查意见通知书", "OA_SUBSEQUENT"),
        ("FORMAT_LETTER_007", "第十二次审查意见通知书", "OA_SUBSEQUENT"),
        ("FORMAT_LETTER_007", "第一百零二次审查意见通知书", "OA_SUBSEQUENT"),
        ("FORMAT_LETTER_007", "复审通知书", "REEXAMINATION_NOTICE"),
        ("FORMAT_LETTER_008", "专利证书", "PATENT_CERTIFICATE"),
    ),
)
def test_all_frozen_notice_variants(
    session_factory: sessionmaker,
    template_code: str,
    title: str,
    variant: str,
) -> None:
    needs_deadline = template_code in {
        "FORMAT_LETTER_001",
        "FORMAT_LETTER_003",
        "FORMAT_LETTER_006",
        "FORMAT_LETTER_007",
    }
    with session_factory() as db:
        _seed(
            db,
            template_code=template_code,
            title=title,
            extra_data=_deadline() if needs_deadline else None,
        )
        if template_code == "FORMAT_LETTER_006":
            _add_grant_obligation(db)
        result = _build(db)
        assert result.notice_variant.value == variant
        assert result.context["notice_variant_code"] == variant
        assert result.context["template_variant_code"] == template_code


def test_template_title_mismatch_rejects_variant(session_factory: sessionmaker) -> None:
    for title in (
        "任意通知",
        "第零零次审查意见通知书",
        "第零一次审查意见通知书",
        "第一一次审查意见通知书",
        "第十十次审查意见通知书",
    ):
        with session_factory() as db:
            _seed(
                db,
                template_code="FORMAT_LETTER_007",
                title=title,
                extra_data=_deadline(),
            )
            _assert_error("FORMAT_LETTER_NOTICE_VARIANT_INVALID", 409, lambda: _build(db))


def test_applicant_order_fallback_conflicts_and_required_case_context(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as db:
        _seed(db)
        first = db.scalar(select(T_CaseApplicant).where(T_CaseApplicant.case_id == CASE_ID))
        assert first is not None
        first.is_first = False
        first.name_cn = " "
        first.name_en = "Applicant One"
        db.add_all(
            [
                T_CaseApplicant(
                    id="00000000-0000-0000-0000-000000000081",
                    case_id=CASE_ID,
                    seq=2,
                    is_first=False,
                    name_cn="申请人乙",
                ),
                T_CaseApplicant(
                    id="00000000-0000-0000-0000-000000000082",
                    case_id=CASE_ID,
                    seq=3,
                    is_first=False,
                    name_en="Applicant Three",
                ),
                T_CaseApplicant(
                    id="00000000-0000-0000-0000-000000000083",
                    case_id=CASE_ID,
                    seq=4,
                    is_first=False,
                    name_cn="申请人丁",
                ),
            ]
        )
        db.flush()
        assert (
            _build(db).context["applicant_names_text"]
            == "Applicant One、申请人乙、Applicant Three、申请人丁"
        )

        second = db.get(T_CaseApplicant, "00000000-0000-0000-0000-000000000081")
        assert second is not None
        second.is_first = True
        db.flush()
        _assert_error("FORMAT_LETTER_APPLICANT_CONFLICT", 409, lambda: _build(db))

    with session_factory() as db:
        _seed(db)
        applicant = db.scalar(select(T_CaseApplicant).where(T_CaseApplicant.case_id == CASE_ID))
        assert applicant is not None
        applicant.name_cn = " "
        applicant.name_en = None
        db.flush()
        _assert_error("FORMAT_LETTER_APPLICANT_MISSING", 409, lambda: _build(db))

    for field_name, model_field in (
        ("case_no", "case_no"),
        ("invention_title", "title_cn"),
        ("application_no", "app_no"),
    ):
        with session_factory() as db:
            seeded = _seed(db)
            case = cast(Case, seeded["case"])
            setattr(case, model_field, " ")
            if model_field == "title_cn":
                case.title_en = " "
            db.flush()
            _assert_error(
                "FORMAT_LETTER_CASE_CONTEXT_MISSING",
                409,
                lambda: _build(db),
                field=field_name,
            )


def test_required_inventors_and_source_title(session_factory: sessionmaker) -> None:
    with session_factory() as db:
        _seed(db, template_code="FORMAT_LETTER_005", title="受理通知-电子")
        db.add(
            T_CaseInventor(
                id="00000000-0000-0000-0000-000000000085",
                case_id=CASE_ID,
                seq=2,
                name_en="Inventor Two",
            )
        )
        db.flush()
        assert _build(db).context["inventor_names_text"] == "发明人甲、Inventor Two"

        for inventor in db.scalars(select(T_CaseInventor).where(T_CaseInventor.case_id == CASE_ID)):
            db.delete(inventor)
        db.flush()
        _assert_error(
            "FORMAT_LETTER_CASE_CONTEXT_MISSING",
            409,
            lambda: _build(db),
            field="inventor_names_text",
        )

    with session_factory() as db:
        seeded = _seed(db)
        cast(Document, seeded["source"]).title = " "
        db.flush()
        _assert_error(
            "FORMAT_LETTER_MAPPING_MISSING",
            409,
            lambda: _build(db),
        )


def test_contact_precedence_and_exact_salutation(session_factory: sessionmaker) -> None:
    with session_factory() as db:
        _seed(db)
        db.add_all(
            [
                ClientContact(
                    id=CONTACT_ID,
                    client_id=CLIENT_ID,
                    contact_name=" 王女士 ",
                    title=" 总监 ",
                    is_primary=False,
                ),
                ClientContact(
                    id="00000000-0000-0000-0000-000000000086",
                    client_id=CLIENT_ID,
                    contact_name="李先生",
                    title=None,
                    is_primary=True,
                ),
            ]
        )
        db.flush()
        explicit = _build(db, selected_contact_id=CONTACT_ID)
        assert explicit.selected_contact_id == CONTACT_ID
        assert explicit.contact_selection_source == "EXPLICIT"
        assert explicit.salutation_source == "SELECTED_CONTACT"
        assert explicit.context["salutation_text"] == "尊敬的王女士总监：您好"

        primary = _build(db)
        assert primary.contact_selection_source == "PRIMARY"
        assert primary.context["salutation_text"] == "尊敬的李先生：您好"

        db.add(
            ClientContact(
                id="00000000-0000-0000-0000-000000000087",
                client_id=CLIENT_ID,
                contact_name="另一联系人",
                is_primary=True,
            )
        )
        db.flush()
        _assert_error("FORMAT_LETTER_PRIMARY_CONTACT_AMBIGUOUS", 409, lambda: _build(db))

    with session_factory() as db:
        _seed(db)
        assert _build(db).context["salutation_text"] == "尊敬的：您好"
        _assert_error(
            "FORMAT_LETTER_CONTACT_NOT_FOUND",
            404,
            lambda: _build(db, selected_contact_id=CONTACT_ID),
        )

    with session_factory() as db:
        _seed(db)
        db.add(
            Client(
                id=OTHER_CLIENT_ID,
                client_code="OTHER",
                name_cn="其他客户",
                client_type="CLIENT",
                default_currency="CNY",
                is_active=True,
            )
        )
        db.flush()
        db.add(
            ClientContact(
                id=CONTACT_ID,
                client_id=OTHER_CLIENT_ID,
                contact_name="其他联系人",
                is_primary=True,
            )
        )
        db.flush()
        _assert_error(
            "FORMAT_LETTER_CONTACT_CASE_MISMATCH",
            400,
            lambda: _build(db, selected_contact_id=CONTACT_ID),
        )


def test_contact_name_must_be_usable(session_factory: sessionmaker) -> None:
    with session_factory() as db:
        _seed(db)
        db.add(
            ClientContact(
                id=CONTACT_ID,
                client_id=CLIENT_ID,
                contact_name=" ",
                is_primary=True,
            )
        )
        db.flush()
        _assert_error("FORMAT_LETTER_CONTACT_INVALID", 409, lambda: _build(db))


def test_deadline_and_publication_contract(session_factory: sessionmaker) -> None:
    with session_factory() as db:
        _seed(db, template_code="FORMAT_LETTER_001", title="驳回决定")
        _assert_error("FORMAT_LETTER_DEADLINE_MISSING", 409, lambda: _build(db))

    for raw in (
        _deadline(status="NEEDS_CONFIRMATION"),
        '{"OfficialDueDate":"2026-99-99","OfficialDueDateSource":'
        '"MANUAL_OFFICIAL_NOTICE","OfficialDueDateStatus":"CONFIRMED"}',
        '{"OfficialDueDate":"2026-09-30"}',
        "legacy deadline text",
        "[]",
    ):
        with session_factory() as db:
            _seed(
                db,
                template_code="FORMAT_LETTER_001",
                title="驳回决定",
                extra_data=raw,
            )
            _assert_error("FORMAT_LETTER_DEADLINE_UNCONFIRMED", 409, lambda: _build(db))

    with session_factory() as db:
        seeded = _seed(
            db,
            template_code="FORMAT_LETTER_003",
            title="公布通知书",
            extra_data=_deadline("2026-10-01"),
        )
        result = _build(db)
        assert result.context["deadline_text"] == "2026-10-01"
        assert result.context["publication_date_text"] == "2026-03-04"
        cast(Case, seeded["case"]).pub_date = None
        db.flush()
        _assert_error(
            "FORMAT_LETTER_CASE_CONTEXT_MISSING",
            409,
            lambda: _build(db),
            field="publication_date_text",
        )


def test_grant_amounts_are_verified_ordered_and_source_exact(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as db:
        _seed(
            db,
            template_code="FORMAT_LETTER_006",
            title="授权通知书-电子",
            extra_data=_deadline(),
        )
        _add_grant_obligation(db)
        result = _build(db)
        assert result.context["deadline_text"] == "2026-09-30"
        assert result.context["amount_lines_text"] == "登记费：200.50 元\n年费：1,200.00 元"
        assert "8,888.00" not in result.context["amount_lines_text"]
        assert "9,999.00" not in result.context["amount_lines_text"]


def test_grant_amount_and_deadline_fail_closed(session_factory: sessionmaker) -> None:
    with session_factory() as db:
        _seed(
            db,
            template_code="FORMAT_LETTER_006",
            title="授权通知书-电子",
            extra_data=_deadline(),
        )
        _assert_error("FORMAT_LETTER_AMOUNT_MISSING", 409, lambda: _build(db))

    cases = (
        ({"due_date": date(2026, 10, 1)}, "FORMAT_LETTER_DEADLINE_CONFLICT"),
        ({"currency": "USD"}, "FORMAT_LETTER_AMOUNT_CONFLICT"),
        ({"source_status": "PENDING"}, "FORMAT_LETTER_AMOUNT_MISSING"),
        (
            {"line_specs": (("REG", "登记费", 1, None, Decimal("500.00"), "MATCHED"),)},
            "FORMAT_LETTER_AMOUNT_UNVERIFIED",
        ),
        (
            {
                "line_specs": (
                    (
                        "REG",
                        "登记费",
                        1,
                        Decimal("-1.00"),
                        Decimal("500.00"),
                        "MATCHED",
                    ),
                )
            },
            "FORMAT_LETTER_AMOUNT_CONFLICT",
        ),
        (
            {
                "line_specs": (
                    (
                        "REG",
                        "登记费",
                        1,
                        Decimal("500.00"),
                        Decimal("500.00"),
                        "REVIEW_REQUIRED",
                    ),
                )
            },
            "FORMAT_LETTER_AMOUNT_CONFLICT",
        ),
    )
    for kwargs, code in cases:
        with session_factory() as db:
            _seed(
                db,
                template_code="FORMAT_LETTER_006",
                title="授权通知书-电子",
                extra_data=_deadline(),
            )
            _add_grant_obligation(db, **kwargs)
            _assert_error(code, 409, lambda: _build(db))


def test_grant_obligation_ambiguity_and_supersession(session_factory: sessionmaker) -> None:
    with session_factory() as db:
        _seed(
            db,
            template_code="FORMAT_LETTER_006",
            title="授权通知书-电子",
            extra_data=_deadline(),
        )
        old = _add_grant_obligation(db)
        replacement_id = "00000000-0000-0000-0000-000000000099"
        _add_grant_obligation(
            db,
            obligation_id=replacement_id,
            supersedes_obligation_id=old.id,
            line_specs=(("REG", "登记费", 1, Decimal("300.00"), Decimal("900.00"), "MATCHED"),),
        )
        result = _build(db)
        assert result.context["amount_lines_text"] == "登记费：300.00 元"

        db.add(
            FeeObligation(
                id="00000000-0000-0000-0000-000000000098",
                case_id=CASE_ID,
                source_activity_id=ACTIVITY_ID,
                source_document_id=SOURCE_ID,
                fee_domain="GOV",
                obligation_type="OTHER",
                obligation_status="RECOGNIZED",
                due_date=date(2026, 9, 30),
                currency="CNY",
                source_status="VERIFIED",
                client_instruction_status="PENDING",
                draft_status="NOT_CREATED",
                payment_status="UNPAID",
                official_evidence_status="CONFIRMED",
            )
        )
        db.flush()
        _assert_error("FORMAT_LETTER_AMOUNT_CONFLICT", 409, lambda: _build(db))


def test_non_grant_never_reads_or_mutates_fee_rows(session_factory: sessionmaker) -> None:
    with session_factory() as db:
        _seed(db)
        before = db.scalar(select(func.count()).select_from(FeeObligation))
        result = _build(db)
        after = db.scalar(select(func.count()).select_from(FeeObligation))
        assert result.context["amount_lines_text"] == ""
        assert before == after == 0
