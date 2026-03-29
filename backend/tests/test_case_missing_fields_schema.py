from __future__ import annotations

from sqlalchemy import create_engine, event, inspect

from app.db.base import Base
from app.models import *  # noqa: F401,F403
from app.modules.cases.models import Case


def test_case_model_exposes_missing_fields_and_sqlite_columns(tmp_path) -> None:
    db_path = tmp_path / "case_missing_fields.db"
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

    Base.metadata.create_all(engine)

    case_columns = Case.__table__.columns
    expected_columns = {
        "recv_date",
        "draw_pages",
        "claim_pages",
        "manuscript_words",
        "discount_rate",
        "no_power",
        "no_prio_text",
        "require_hk",
        "from_country",
        "to_country",
        "doc_address_id",
        "bill_address_id",
        "issue_date",
        "cert_no",
        "first_annuity_year",
    }
    assert expected_columns.issubset(set(case_columns.keys()))

    assert getattr(case_columns["discount_rate"].type, "precision", None) == 5
    assert getattr(case_columns["discount_rate"].type, "scale", None) == 4

    inspector = inspect(engine)
    db_columns = {column["name"] for column in inspector.get_columns("t_case")}
    assert expected_columns.issubset(db_columns)

    case_fks = {
        (
            tuple(fk.get("constrained_columns") or []),
            fk.get("referred_table"),
            tuple(fk.get("referred_columns") or []),
        )
        for fk in inspector.get_foreign_keys("t_case")
    }
    assert (("doc_address_id",), "t_client_address", ("id",)) in case_fks
    assert (("bill_address_id",), "t_client_address", ("id",)) in case_fks

    engine.dispose()
