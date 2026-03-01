from __future__ import annotations

import calendar
from datetime import date, timedelta
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
        if not doc_type:
            return []

        templates = db.query(TaskTemplate).filter(TaskTemplate.code == doc_type).all()
        if not templates:
            return []

        created: list[Task] = []
        for template in templates:
            if hasattr(template, "enabled") and not template.enabled:
                continue

            due_date = self._compute_due_date(doc_date, template)
            title = template.name or template.code

            inner_offset = getattr(template, "inner_offset_days", None)
            internal_due_date = due_date - timedelta(days=inner_offset) if inner_offset else None

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
                internal_due_date=internal_due_date,
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
        return False

    def _get_document_type(self, db: Session, document) -> str | None:
        for attr in ("doc_type", "doc_code", "template_code"):
            value = getattr(document, attr, None)
            if value:
                return str(value)

        doc_template_id = getattr(document, "doc_template_id", None)
        if doc_template_id:
            doc_template = db.query(DocTemplate).filter(DocTemplate.id == doc_template_id).first()
            if doc_template:
                return getattr(doc_template, "deadline_template_code", None) or doc_template.code

        return None

    @staticmethod
    def _add_months(base: date, months: int) -> date:
        """Add *months* to *base*, clamping day to valid range."""
        month = base.month - 1 + months
        year = base.year + month // 12
        month = month % 12 + 1
        day = min(base.day, calendar.monthrange(year, month)[1])
        return date(year, month, day)

    def _compute_due_date(self, base: date, template) -> date:
        """Compute due date from add_days and/or add_months on the template."""
        add_days = getattr(template, "add_days", None) or 0
        add_months = getattr(template, "add_months", None) or 0

        if not add_days and not add_months:
            raise RuntimeError(
                f"TaskTemplate '{getattr(template, 'code', '?')}' missing add_days/add_months"
            )

        result = base
        if add_months:
            result = self._add_months(result, add_months)
        if add_days:
            result = result + timedelta(days=add_days)
        return result

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
