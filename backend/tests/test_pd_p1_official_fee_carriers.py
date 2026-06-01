from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, event, inspect

from app.core.config import get_settings
from app.db.base import Base
from app.models import *  # noqa: F401,F403
from app.modules.annuity.models import PayList
from app.modules.annuity.schemas import PayListOfficialReadinessOut
from app.modules.fees.models import FeeDraft, OfficialFeeChecklist
from app.modules.fees.schemas import (
    OFFICIAL_FEE_TEMPLATE_STATUSES,
    FeeDraftOut,
    OfficialFeeChecklistOut,
)

FEE_DRAFT_OFFICIAL_COLUMNS = {
    "official_fee_reduction_note",
    "official_template_status",
    "official_template_version",
    "official_template_note",
}
PAY_LIST_OFFICIAL_COLUMNS = {
    "official_upload_template_status",
    "official_upload_template_name",
    "official_upload_batch_limit",
    "official_pay_list_boundary_note",
}
OFFICIAL_FEE_CHECKLIST_COLUMNS = {
    "fee_draft_id",
    "pay_list_id",
    "checklist_code",
    "checklist_label",
    "status",
    "required",
    "blocker_reason",
    "sort_order",
}


def _sqlite_engine(db_path: Path):
    engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False},
        future=True,
    )

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, _connection_record) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    return engine


def test_official_fee_carrier_models_expose_required_columns(tmp_path) -> None:
    db_path = tmp_path / "official_fee_carriers_model.db"
    engine = _sqlite_engine(db_path)

    Base.metadata.create_all(engine)

    assert FEE_DRAFT_OFFICIAL_COLUMNS <= set(FeeDraft.__table__.columns.keys())
    assert PAY_LIST_OFFICIAL_COLUMNS <= set(PayList.__table__.columns.keys())
    assert OfficialFeeChecklist.__tablename__ == "t_official_fee_checklist"

    inspector = inspect(engine)
    assert FEE_DRAFT_OFFICIAL_COLUMNS <= {
        column["name"] for column in inspector.get_columns("t_fee_draft")
    }
    assert PAY_LIST_OFFICIAL_COLUMNS <= {
        column["name"] for column in inspector.get_columns("t_pay_list")
    }
    assert OFFICIAL_FEE_CHECKLIST_COLUMNS <= {
        column["name"] for column in inspector.get_columns("t_official_fee_checklist")
    }

    engine.dispose()


def test_official_fee_schemas_preserve_readiness_metadata() -> None:
    assert {"UNCONFIRMED", "READY", "BLOCKED"} <= set(OFFICIAL_FEE_TEMPLATE_STATUSES)

    draft = FeeDraftOut(
        id="draft-1",
        case_id="case-1",
        draft_type="OFFICIAL",
        currency="CNY",
        status="OPEN",
        total_gov=Decimal("1000"),
        total_service=Decimal("0"),
        total_misc=Decimal("0"),
        amount=Decimal("1000"),
        created_at=datetime(2026, 5, 31, 10, 0, 0),
        updated_at=datetime(2026, 5, 31, 10, 0, 0),
        official_fee_reduction_note="旧系统 0 / 0.7 / 0.85 待客户确认含义",
        official_template_status="UNCONFIRMED",
        official_template_version="客户待提供",
        official_template_note="补充缴费信息模板字段待确认",
    )
    checklist = OfficialFeeChecklistOut(
        id="check-1",
        fee_draft_id="draft-1",
        pay_list_id=12,
        checklist_code="FEE_REDUCTION_RATE",
        checklist_label="费减比例解释已确认",
        status="BLOCKED",
        required=True,
        blocker_reason="客户未确认 0 / 0.7 / 0.85 的含义",
        sort_order=10,
    )
    pay_list = PayListOfficialReadinessOut(
        pay_list_id=12,
        official_upload_template_status="UNCONFIRMED",
        official_upload_template_name="补充缴费信息模板",
        official_upload_batch_limit=500,
        official_pay_list_boundary_note="P1 只记录清单边界，不声明已匹配官方 Excel",
    )

    assert draft.official_template_status == "UNCONFIRMED"
    assert checklist.status == "BLOCKED"
    assert pay_list.official_upload_batch_limit == 500


def test_official_fee_carrier_migration_creates_columns_and_table(
    tmp_path,
    monkeypatch,
) -> None:
    db_path = tmp_path / "official_fee_carriers_migration.db"
    db_url = f"sqlite:///{db_path}"
    monkeypatch.setenv("DATABASE_URL", db_url)
    get_settings.cache_clear()

    alembic_ini = Path(__file__).resolve().parents[1] / "alembic.ini"
    config = Config(str(alembic_ini))
    config.set_main_option(
        "script_location",
        str(Path(__file__).resolve().parents[1] / "alembic"),
    )
    config.set_main_option("sqlalchemy.url", db_url)

    command.upgrade(config, "head")

    engine = _sqlite_engine(db_path)
    inspector = inspect(engine)

    assert FEE_DRAFT_OFFICIAL_COLUMNS <= {
        column["name"] for column in inspector.get_columns("t_fee_draft")
    }
    assert PAY_LIST_OFFICIAL_COLUMNS <= {
        column["name"] for column in inspector.get_columns("t_pay_list")
    }
    assert "t_official_fee_checklist" in inspector.get_table_names()
    assert OFFICIAL_FEE_CHECKLIST_COLUMNS <= {
        column["name"] for column in inspector.get_columns("t_official_fee_checklist")
    }

    engine.dispose()
