from __future__ import annotations

from pydantic import BaseModel


class CaseCreateIn(BaseModel):
    case_no: str
    case_type: str | None = None
    patent_category: str | None = None
    flow_dir: str | None = None
    client_id: str | None = None
