from __future__ import annotations

import os

import pytest
from sqlalchemy.exc import SQLAlchemyError

from framework.db_assert import DbAssert


def test_real_db_smoke_reads_user_table_when_dsn_is_available() -> None:
    dsn = os.getenv("FPMS_DB_DSN", "").strip()
    if not dsn:
        pytest.skip("FPMS_DB_DSN is not configured; real DB smoke skipped")
    if "user:password@localhost:5432/fpms" in dsn:
        pytest.skip(
            "FPMS_DB_DSN contains the skeleton placeholder; real DB smoke skipped"
        )

    db = DbAssert(dsn)
    try:
        count = db.assert_count("t_user")
    except ModuleNotFoundError as exc:
        pytest.skip(f"DB driver unavailable for configured FPMS_DB_DSN: {exc.name}")
    except SQLAlchemyError as exc:
        pytest.fail(f"Real DB smoke query failed: {type(exc).__name__}")

    assert count >= 0
