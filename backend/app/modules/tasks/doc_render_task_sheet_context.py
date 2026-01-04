from __future__ import annotations

from datetime import date, datetime
from typing import Any


class TaskSheetContextBuilder:
    def build(self, task, case, client) -> dict:
        return {
            "task": self._build_task(task),
            "case": self._build_case(case) if case else None,
            "client": self._build_client(client) if client else None,
        }

    def _build_task(self, task) -> dict:
        return {
            "id": task.id,
            "title": task.title,
            "status": task.status,
            "due_date": self._serialize_value(task.due_date),
            "worker": task.worker_id,
            "supervisor": task.supervisor_id,
        }

    def _build_case(self, case) -> dict:
        return {
            "id": case.id,
            "case_no": case.case_no,
            "title_cn": getattr(case, "title_cn", None),
            "title_en": getattr(case, "title_en", None),
        }

    def _build_client(self, client) -> dict:
        return {
            "id": client.id,
            "client_code": client.client_code,
            "name_cn": client.name_cn,
            "name_en": client.name_en,
        }

    def _serialize_value(self, value: Any) -> Any:
        if isinstance(value, (datetime, date)):
            return value.isoformat()
        return value
