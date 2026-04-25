from __future__ import annotations

import re
from typing import Any

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine


class DbAssertDisabledError(RuntimeError):
    """Raised when DB assertions are requested without a configured DSN."""


class DbAssertIdentifierError(ValueError):
    """Raised when a table or column identifier is unsafe."""


class DbAssert:
    """Read-only database assertion helper for pytest skeleton handlers."""

    _IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

    def __init__(self, dsn: str) -> None:
        self.dsn = dsn.strip()
        self._engine: Engine | None = None

    def enabled(self) -> bool:
        return bool(self.dsn)

    @property
    def engine(self) -> Engine:
        self._ensure_enabled()
        if self._engine is None:
            self._engine = create_engine(self.dsn, future=True)
        return self._engine

    def fetch_all(
        self, query: str, params: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        self._ensure_enabled()
        with self.engine.connect() as conn:
            rows = conn.execute(text(query), params or {}).mappings().all()
        return [dict(row) for row in rows]

    def fetch_one(
        self, query: str, params: dict[str, Any] | None = None
    ) -> dict[str, Any] | None:
        self._ensure_enabled()
        with self.engine.connect() as conn:
            row = conn.execute(text(query), params or {}).mappings().first()
        return dict(row) if row is not None else None

    def assert_row_exists(self, table: str, where: dict[str, Any]) -> dict[str, Any]:
        self._validate_identifier(table)
        if not where:
            raise ValueError("assert_row_exists requires at least one where condition")

        clauses = []
        params: dict[str, Any] = {}
        for index, (column, value) in enumerate(where.items()):
            self._validate_identifier(column)
            param_name = f"p{index}"
            clauses.append(f"{column} = :{param_name}")
            params[param_name] = value

        query = f"select * from {table} where {' and '.join(clauses)} limit 1"
        row = self.fetch_one(query, params)
        if row is None:
            raise AssertionError(
                f"Expected row in {table} matching {sorted(where.keys())}"
            )
        return row

    def assert_count(
        self,
        table: str,
        where: dict[str, Any] | None = None,
        expected: int | None = None,
    ) -> int:
        self._validate_identifier(table)
        where = where or {}
        clauses = []
        params: dict[str, Any] = {}
        for index, (column, value) in enumerate(where.items()):
            self._validate_identifier(column)
            param_name = f"p{index}"
            clauses.append(f"{column} = :{param_name}")
            params[param_name] = value

        query = f"select count(*) as count from {table}"
        if clauses:
            query = f"{query} where {' and '.join(clauses)}"

        row = self.fetch_one(query, params)
        count = int(row["count"] if row is not None else 0)
        if expected is not None and count != expected:
            raise AssertionError(f"Expected {expected} rows in {table}, found {count}")
        return count

    def _ensure_enabled(self) -> None:
        if not self.enabled():
            raise DbAssertDisabledError(
                "DB assertions are disabled because FPMS_DB_DSN is empty"
            )

    def _validate_identifier(self, identifier: str) -> None:
        if not self._IDENTIFIER_RE.fullmatch(identifier):
            raise DbAssertIdentifierError(f"Unsafe SQL identifier: {identifier!r}")
