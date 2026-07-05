from __future__ import annotations

from decimal import Decimal

from sqlalchemy.orm import sessionmaker

from app.modules.fees.models import FeeRate
from scripts.seed_dev import seed_official_fee_rate_catalog


def _rate_by_code(session_factory: sessionmaker) -> dict[str, FeeRate]:
    with session_factory() as db:
        return {rate.fee_code: rate for rate in db.query(FeeRate).all()}


def test_seed_official_fee_rate_catalog_creates_gov_only_source_traced_rates(
    session_factory: sessionmaker,
):
    with session_factory() as db:
        seed_official_fee_rate_catalog(db)

    rates = _rate_by_code(session_factory)

    required_codes = {
        "CN_INV_APPLICATION_FEE",
        "CN_UM_APPLICATION_FEE",
        "CN_DES_APPLICATION_FEE",
        "CN_EXCESS_CLAIM_FEE",
        "CN_SPEC_PAGE_31_300_FEE",
        "CN_SPEC_PAGE_301_PLUS_FEE",
        "CN_PUBLICATION_PRINT_FEE",
        "CN_PRIORITY_CLAIM_FEE",
        "CN_SUBSTANTIVE_EXAM_FEE",
        "CN_REEXAM_FEE_INV",
        "CN_ANNUITY_FEE_INV",
        "CN_ANNUITY_FEE_UM",
        "CN_ANNUITY_FEE_DES",
        "CN_ANNUITY_LATE_FEE",
        "CN_RESTORE_RIGHT_FEE",
        "CN_EXTENSION_FIRST_MONTH_FEE",
        "CN_EXTENSION_REPEAT_MONTH_FEE",
        "CN_BIBLIO_CHANGE_FEE",
        "CN_PATENT_EVALUATION_REPORT_UM",
        "CN_INVALIDATION_REQUEST_INV",
        "CN_FILE_COPY_CERT_FEE",
        "PCT_SEARCH_FEE",
        "PCT_CN_GRACE_FEE",
        "CN_PATENT_TERM_COMPENSATION_REQUEST_FEE",
        "CN_HAGUE_DESIGN_CN_DESIGNATION_FEE",
        "CN_HAGUE_DESIGN_CN_DESIGNATION_FEE_FIRST",
        "CN_HAGUE_DESIGN_CN_DESIGNATION_FEE_SECOND",
        "IC_LAYOUT_REGISTRATION_FEE",
        "IC_LAYOUT_REEXAM_REQUEST_FEE",
        "IC_LAYOUT_BIBLIO_CHANGE_FEE",
        "IC_LAYOUT_EXTENSION_REQUEST_FEE",
        "IC_LAYOUT_RESTORE_RIGHT_FEE",
        "IC_LAYOUT_NONVOLUNTARY_LICENSE_REQUEST_FEE",
        "IC_LAYOUT_NONVOLUNTARY_LICENSE_REMUNERATION_ADJUDICATION_FEE",
    }
    assert required_codes <= set(rates)
    assert {rates[code].fee_type for code in required_codes} == {"GOV"}

    application = rates["CN_INV_APPLICATION_FEE"]
    assert application.default_amount == Decimal("900.00")
    assert application.rate_group == "DOMESTIC"
    assert application.patent_category == "INV"
    assert application.enabled is True
    assert application.allow_reduction is True
    assert application.fee_domain == "PATENT"
    assert application.fee_section == "专利收费-国内部分"
    assert application.fee_category == "申请费"
    assert application.fee_subtype == "发明专利"
    assert application.reduction_scope == "申请费（不包括公布印刷费、申请附加费）"
    assert application.source_doc == "docs/postdemo/专利收费场景-20260626.docx"
    assert application.source_url == "http://www.tianyueip.com/product/612"
    assert application.source_status == "CONFIRMED"

    annuity = rates["CN_ANNUITY_FEE_INV"]
    assert annuity.rate_group == "ANNUITY"
    assert annuity.calc_mode == "TIER"
    assert '"from": 1' in annuity.calc_params
    assert '"amount": "900.00"' in annuity.calc_params

    pct = rates["PCT_SEARCH_FEE"]
    assert pct.fee_category == "PCT 国际阶段费用"
    assert pct.fee_subtype == "检索费"
    assert pct.enabled is False
    assert pct.source_status == "PENDING_CONFIRMATION"

    compensation = rates["CN_PATENT_TERM_COMPENSATION_REQUEST_FEE"]
    assert compensation.fee_category == "专利权期限补偿请求费"
    assert compensation.fee_subtype == "每件"
    assert compensation.default_amount == Decimal("200.00")
    assert compensation.enabled is False
    assert compensation.source_status == "PENDING_CONFIRMATION"

    compensation_annuity = rates["CN_COMPENSATION_PERIOD_ANNUITY_FEE"]
    assert compensation_annuity.fee_category == "专利权补偿期年费"
    assert compensation_annuity.fee_subtype == "每年，不足一年部分不收取"
    assert compensation_annuity.default_amount == Decimal("8000.00")

    hague = rates["CN_HAGUE_DESIGN_CN_DESIGNATION_FEE"]
    assert hague.fee_section == "专利收费-外观设计国际注册申请"
    assert hague.fee_category == "指定中国单独指定费"
    assert hague.fee_subtype == "第三期"
    assert hague.default_amount == Decimal("15000.00")
    assert hague.allow_reduction is False

    hague_first = rates["CN_HAGUE_DESIGN_CN_DESIGNATION_FEE_FIRST"]
    assert hague_first.fee_subtype == "第一期"
    assert hague_first.default_amount == Decimal("4100.00")
    assert hague_first.allow_reduction is True

    hague_second = rates["CN_HAGUE_DESIGN_CN_DESIGNATION_FEE_SECOND"]
    assert hague_second.fee_subtype == "第二期"
    assert hague_second.default_amount == Decimal("7600.00")
    assert hague_second.allow_reduction is True

    ic_layout = rates["IC_LAYOUT_REGISTRATION_FEE"]
    assert ic_layout.fee_domain == "IC_LAYOUT"
    assert ic_layout.fee_section == "集成电路布图设计收费标准"
    assert ic_layout.fee_category == "布图设计登记费"
    assert ic_layout.fee_subtype == "每件"
    assert ic_layout.default_amount == Decimal("1000.00")

    ic_expected_amounts = {
        "IC_LAYOUT_REEXAM_REQUEST_FEE": Decimal("1000.00"),
        "IC_LAYOUT_BIBLIO_CHANGE_FEE": Decimal("50.00"),
        "IC_LAYOUT_EXTENSION_REQUEST_FEE": Decimal("150.00"),
        "IC_LAYOUT_RESTORE_RIGHT_FEE": Decimal("500.00"),
        "IC_LAYOUT_NONVOLUNTARY_LICENSE_REQUEST_FEE": Decimal("150.00"),
        "IC_LAYOUT_NONVOLUNTARY_LICENSE_REMUNERATION_ADJUDICATION_FEE": Decimal("150.00"),
    }
    for fee_code, amount in ic_expected_amounts.items():
        assert rates[fee_code].fee_domain == "IC_LAYOUT"
        assert rates[fee_code].default_amount == amount
        assert rates[fee_code].enabled is False


def test_seed_official_fee_rate_catalog_is_idempotent_and_updates_existing_rows(
    session_factory: sessionmaker,
):
    with session_factory() as db:
        seed_official_fee_rate_catalog(db)
        seed_official_fee_rate_catalog(db)

        all_rates = db.query(FeeRate).all()
        assert len({rate.fee_code for rate in all_rates}) == len(all_rates)

        existing = db.query(FeeRate).filter(FeeRate.fee_code == "CN_INV_APPLICATION_FEE").one()
        existing.default_amount = Decimal("1.00")
        db.commit()

        seed_official_fee_rate_catalog(db)
        refreshed = db.query(FeeRate).filter(FeeRate.fee_code == "CN_INV_APPLICATION_FEE").one()
        assert refreshed.default_amount == Decimal("900.00")
        assert refreshed.fee_category == "申请费"
        assert refreshed.fee_subtype == "发明专利"
