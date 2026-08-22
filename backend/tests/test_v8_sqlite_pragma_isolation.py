from __future__ import annotations

from sqlalchemy.engine import Engine


def test_engine_checkout_restores_default_sqlite_busy_timeout(engine: Engine) -> None:
    with engine.connect() as connection:
        connection.exec_driver_sql("PRAGMA busy_timeout = 0")
        assert connection.exec_driver_sql("PRAGMA busy_timeout").scalar_one() == 0

    with engine.connect() as connection:
        assert connection.exec_driver_sql("PRAGMA busy_timeout").scalar_one() == 5000
