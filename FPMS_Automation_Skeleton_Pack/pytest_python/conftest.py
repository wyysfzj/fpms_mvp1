from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = ROOT.parent
ENV_KEYS = (
    "FPMS_ENV",
    "FPMS_BASE_URL",
    "FPMS_API_URL",
    "FPMS_DB_DSN",
    "FPMS_RUN_ID",
    "FPMS_TIMEOUT",
    "FPMS_USERNAME",
    "FPMS_PASSWORD",
)

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

EXTERNAL_ENV = {key: os.environ.get(key) for key in ENV_KEYS}
load_dotenv(ROOT / ".env.example")
load_dotenv(ROOT / ".env", override=True)
for key, value in EXTERNAL_ENV.items():
    if value is not None:
        os.environ[key] = value

from framework.api_client import ApiClient  # noqa: E402
from framework.db_assert import DbAssert  # noqa: E402
from framework.runtime import RuntimeContext  # noqa: E402


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--fpms-env", action="store", default=os.getenv("FPMS_ENV", "test")
    )
    parser.addoption(
        "--base-url",
        action="store",
        default=os.getenv("FPMS_BASE_URL", "http://localhost:3000"),
    )
    parser.addoption(
        "--api-url",
        action="store",
        default=os.getenv("FPMS_API_URL", "http://localhost:8000/api/v1"),
    )
    parser.addoption("--db-dsn", action="store", default=os.getenv("FPMS_DB_DSN", ""))
    parser.addoption(
        "--run-id", action="store", default=os.getenv("FPMS_RUN_ID", "LOCAL-RUN-001")
    )
    parser.addoption(
        "--timeout",
        action="store",
        type=int,
        default=int(os.getenv("FPMS_TIMEOUT", "30")),
    )
    parser.addoption(
        "--fpms-username", action="store", default=os.getenv("FPMS_USERNAME", "admin")
    )
    parser.addoption(
        "--fpms-password",
        action="store",
        default=os.getenv("FPMS_PASSWORD", "admin123"),
    )


@pytest.fixture(scope="session")
def runtime(pytestconfig: pytest.Config) -> RuntimeContext:
    return RuntimeContext(
        env_name=pytestconfig.getoption("--fpms-env"),
        base_url=pytestconfig.getoption("--base-url"),
        api_url=pytestconfig.getoption("--api-url"),
        db_dsn=pytestconfig.getoption("--db-dsn"),
        run_id=pytestconfig.getoption("--run-id"),
        timeout=pytestconfig.getoption("--timeout"),
        username=pytestconfig.getoption("--fpms-username"),
        password=pytestconfig.getoption("--fpms-password"),
        api=ApiClient(
            pytestconfig.getoption("--api-url"),
            timeout=pytestconfig.getoption("--timeout"),
        ),
        db=DbAssert(pytestconfig.getoption("--db-dsn")),
    )
