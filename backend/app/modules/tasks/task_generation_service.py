from __future__ import annotations

from datetime import timedelta
from uuid import uuid4

from sqlalchemy.orm import Session

from app.modules.documents.models import DocTemplate
from app.modules.tasks.models import Task, TaskLog, TaskTemplate


class TaskGenerationService:
    def generate_from_document(self, db: Session, document) -> list[Task]:
        case_id = getattr(document, "case_id", None)
        doc_date = getattr(document, "doc_date", None)
        if not case_id or not doc_date:
            return []

        if not self._is_incoming(document):
            return []

        doc_type = self._get_document_type(db, document)
        if not doc_type or not self._is_office_action(doc_type, document):
            return []

        templates = db.query(TaskTemplate).filter(TaskTemplate.code == doc_type).all()
        if not templates:
            return []

        created: list[Task] = []
        for template in templates:
            if hasattr(template, "enabled") and not template.enabled:
                continue

            offset_days = self._get_offset_days(template)
            due_date = doc_date + timedelta(days=offset_days)
            title = template.name or template.code

            if self._task_exists(db, document, template, case_id, due_date, title):
                continue

            task = Task(
                id=str(uuid4()),
                case_id=case_id,
                document_id=document.id,
                task_template_id=template.id,
                title=title,
                base_date=doc_date,
                due_date=due_date,
                status="OPEN",
            )
            db.add(task)
            db.add(
                TaskLog(
                    id=str(uuid4()),
                    task_id=task.id,
                    action="AUTO_CREATE_FROM_DOCUMENT",
                    from_status=None,
                    to_status=task.status,
                    remark=None,
                )
            )
            created.append(task)

        return created

    def _is_incoming(self, document) -> bool:
        direction = getattr(document, "direction", None)
        if direction:
            return str(direction).upper() == "IN"

        flow_dir = getattr(document, "flow_dir", None)
        if flow_dir:
            return str(flow_dir).upper() in {"IN", "INBOUND"}

        return False

    def _is_office_action(self, doc_type: str, document) -> bool:
        if "OA" in doc_type.upper():
            return True

        title = getattr(document, "title", None)
        return bool(title) and "OA" in str(title).upper()

    def _get_document_type(self, db: Session, document) -> str | None:
        for attr in ("doc_type", "doc_code", "template_code"):
            value = getattr(document, attr, None)
            if value:
                return str(value)

        doc_template_id = getattr(document, "doc_template_id", None)
        if doc_template_id:
            doc_template = db.query(DocTemplate).filter(DocTemplate.id == doc_template_id).first()
            if doc_template:
                return doc_template.code

        return None

    def _get_offset_days(self, template) -> int:
        for attr in ("offset_days", "due_offset_days", "offset_day", "due_days"):
            if hasattr(template, attr):
                value = getattr(template, attr)
                if value is None:
                    raise RuntimeError("TaskTemplate missing offset_days mapping")
                return int(value)

        raise RuntimeError("TaskTemplate missing offset_days mapping")

    def _task_exists(
        self,
        db: Session,
        document,
        template,
        case_id: str,
        due_date,
        title: str,
    ) -> bool:
        if getattr(document, "id", None) is not None and hasattr(Task, "document_id"):
            existing = (
                db.query(Task)
                .filter(Task.document_id == document.id, Task.task_template_id == template.id)
                .first()
            )
            return existing is not None

        existing = (
            db.query(Task)
            .filter(
                Task.case_id == case_id,
                Task.task_template_id == template.id,
                Task.due_date == due_date,
                Task.title == title,
            )
            .first()
        )
        return existing is not None
