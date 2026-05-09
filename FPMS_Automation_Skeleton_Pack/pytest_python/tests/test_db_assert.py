from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from framework.db_assert import (
    DbAssert,
    DbAssertDisabledError,
    DbAssertIdentifierError,
)


@pytest.fixture
def sqlite_dsn(tmp_path: Path) -> str:
    db_path = tmp_path / "db_assert_test.db"
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            """
            CREATE TABLE t_client (
                id TEXT PRIMARY KEY,
                client_code TEXT NOT NULL,
                name_cn TEXT NOT NULL,
                is_active INTEGER NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE t_template_source (
                id TEXT PRIMARY KEY,
                "group" TEXT NOT NULL,
                file_path TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE t_bill_item (
                id TEXT PRIMARY KEY,
                bill_id TEXT NOT NULL,
                case_id TEXT NULL
            )
            """
        )
        conn.executemany(
            "INSERT INTO t_client (id, client_code, name_cn, is_active) VALUES (?, ?, ?, ?)",
            [
                ("c1", "CL-001", "北京创新科技有限公司", 1),
                ("c2", "CL-002", "Wilson & Partners LLP", 1),
            ],
        )
        conn.execute(
            'INSERT INTO t_template_source (id, "group", file_path) VALUES (?, ?, ?)',
            ("tpl1", "DOC_TEMPLATE", "/tmp/template.docx"),
        )
        conn.executemany(
            "INSERT INTO t_bill_item (id, bill_id, case_id) VALUES (?, ?, ?)",
            [
                ("bi1", "bill-1", None),
                ("bi2", "bill-1", "case-1"),
            ],
        )
        conn.commit()
    finally:
        conn.close()
    return f"sqlite:///{db_path}"


def test_empty_dsn_is_disabled_and_query_methods_raise_clear_error() -> None:
    db = DbAssert("")

    assert db.enabled() is False
    with pytest.raises(DbAssertDisabledError):
        db.fetch_one("select 1")


def test_fetch_one_returns_dict_or_none(sqlite_dsn: str) -> None:
    db = DbAssert(sqlite_dsn)

    row = db.fetch_one(
        "select id, client_code, name_cn from t_client where client_code = :code",
        {"code": "CL-001"},
    )
    missing = db.fetch_one(
        "select id, client_code from t_client where client_code = :code",
        {"code": "MISSING"},
    )

    assert db.enabled() is True
    assert row == {
        "id": "c1",
        "client_code": "CL-001",
        "name_cn": "北京创新科技有限公司",
    }
    assert missing is None


def test_fetch_all_returns_dict_rows(sqlite_dsn: str) -> None:
    db = DbAssert(sqlite_dsn)

    rows = db.fetch_all(
        "select client_code from t_client where is_active = :active order by client_code",
        {"active": 1},
    )

    assert rows == [{"client_code": "CL-001"}, {"client_code": "CL-002"}]


def test_assert_row_exists_returns_row_or_raises(sqlite_dsn: str) -> None:
    db = DbAssert(sqlite_dsn)

    row = db.assert_row_exists("t_client", {"client_code": "CL-002"})

    assert row["id"] == "c2"
    with pytest.raises(AssertionError):
        db.assert_row_exists("t_client", {"client_code": "MISSING"})


def test_assert_row_exists_quotes_safe_identifiers(sqlite_dsn: str) -> None:
    db = DbAssert(sqlite_dsn)

    row = db.assert_row_exists("t_template_source", {"group": "DOC_TEMPLATE"})

    assert row["id"] == "tpl1"


def test_assert_row_exists_matches_none_with_is_null(sqlite_dsn: str) -> None:
    db = DbAssert(sqlite_dsn)

    row = db.assert_row_exists("t_bill_item", {"bill_id": "bill-1", "case_id": None})

    assert row["id"] == "bi1"


def test_assert_count_returns_count_and_checks_expected(sqlite_dsn: str) -> None:
    db = DbAssert(sqlite_dsn)

    assert db.assert_count("t_client") == 2
    assert db.assert_count("t_client", {"is_active": 1}, expected=2) == 2
    assert db.assert_count("t_bill_item", {"case_id": None}, expected=1) == 1
    with pytest.raises(AssertionError):
        db.assert_count("t_client", {"is_active": 1}, expected=1)


@pytest.mark.parametrize(
    ("table", "where"),
    [
        ("t_client; drop table t_client", {"client_code": "CL-001"}),
        ("1_client", {"client_code": "CL-001"}),
        ("t_client", {"client_code;drop": "CL-001"}),
        ("t_client", {"1_code": "CL-001"}),
    ],
)
def test_unsafe_identifiers_are_rejected(
    sqlite_dsn: str, table: str, where: dict[str, str]
) -> None:
    db = DbAssert(sqlite_dsn)

    with pytest.raises(DbAssertIdentifierError):
        db.assert_row_exists(table, where)
