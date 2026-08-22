from __future__ import annotations

from sqlalchemy.orm import sessionmaker

from app.modules.fees.models import FeeRate
from scripts.seed_dev import seed_official_fee_rate_catalog


def test_seed_corrects_publication_print_classification_in_place(
    session_factory: sessionmaker,
):
    with session_factory() as db:
        seed_official_fee_rate_catalog(db)
        publication_print = (
            db.query(FeeRate).filter(FeeRate.fee_code == "CN_PUBLICATION_PRINT_FEE").one()
        )
        original_id = publication_print.id
        original_created_at = publication_print.created_at

        publication_print.fee_category = "复审费"
        publication_print.fee_subtype = "发明专利"
        publication_print.reduction_scope = "复审费"
        db.commit()

        seed_official_fee_rate_catalog(db)
        corrected = db.query(FeeRate).filter(FeeRate.fee_code == "CN_PUBLICATION_PRINT_FEE").one()

        assert corrected.id == original_id
        assert corrected.created_at == original_created_at
        assert corrected.fee_code == "CN_PUBLICATION_PRINT_FEE"
        assert corrected.fee_category == "公布印刷费"
        assert corrected.fee_subtype == "仅发明专利"
        assert corrected.reduction_scope == "不可费减"
        assert corrected.allow_reduction is False
