from __future__ import annotations

from dataclasses import dataclass

from framework.api_client import ApiClient
from framework.db_assert import DbAssert


@dataclass
class RuntimeContext:
    env_name: str
    base_url: str
    api_url: str
    db_dsn: str
    run_id: str
    timeout: int
    username: str
    password: str
    api: ApiClient
    db: DbAssert
