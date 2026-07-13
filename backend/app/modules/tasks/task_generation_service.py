from __future__ import annotations

import calendar
import json
from datetime import date, timedelta
from uuid import uuid4

from sqlalchemy.orm import Session

from app.core.errors import raise_business_error
from app.modules.cases.models import Case
from app.modules.documents.extra_data import DocumentExtraDataError, parse_document_extra_data
from app.modules.documents.models import DocTemplate
from app.modules.tasks.enums import TaskAction, TaskDeadlineBase, TaskRemindBase, TaskStatus
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

        case = self._get_case(db, document)
        created: list[Task] = []
        for template in templates:
            if hasattr(template, "enabled") and not template.enabled:
                continue

            due_date = self._compute_due_date(document, case, template)
            title = template.name or template.code

            inner_offset = getattr(template, "inner_offset_days", None)
            internal_due_date = (
                due_date - timedelta(days=inner_offset) if inner_offset is not None else None
            )
            remind1, remind2, remind3, daily_remind_from = self._compute_reminders(
                due_date,
                internal_due_date,
                template,
            )

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
                remind1=remind1,
                remind2=remind2,
                remind3=remind3,
                daily_remind_from=daily_remind_from,
                daily_remind=getattr(template, "daily_remind", False) is True,
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
            direction_value = getattr(direction, "value", direction)
            return str(direction_value).upper() == "IN"
        return False

    def _get_document_type(self, db: Session, document) -> str | None:
        doc_template_id = getattr(document, "doc_template_id", None)
        if isinstance(doc_template_id, str) and doc_template_id.strip():
            doc_template = db.query(DocTemplate).filter(DocTemplate.id == doc_template_id).first()
            if doc_template and getattr(doc_template, "deadline_template_code", None):
                return doc_template.deadline_template_code

        for attr in ("doc_type", "doc_code", "template_code"):
            value = getattr(document, attr, None)
            if value:
                return str(value)

        if isinstance(doc_template_id, str) and doc_template_id.strip():
            doc_template = db.query(DocTemplate).filter(DocTemplate.id == doc_template_id).first()
            if doc_template:
                return doc_template.code

        return None

    def _get_case(self, db: Session, document):
        case = getattr(document, "case", None)
        if case is not None:
            return case

        case_id = getattr(document, "case_id", None)
        if not case_id:
            return None

        return db.query(Case).filter(Case.id == case_id).first()

    @staticmethod
    def _add_months(base: date, months: int) -> date:
        """Add *months* to *base*, clamping day to valid range."""
        month = base.month - 1 + months
        year = base.year + month // 12
        month = month % 12 + 1
        day = min(base.day, calendar.monthrange(year, month)[1])
        return date(year, month, day)

    def _resolve_deadline_base_date(self, document, case, template) -> date:
        doc_date = getattr(document, "doc_date", None)
        template_base = getattr(template, "deadline_base", None)
        if template_base is None or not isinstance(template_base, (TaskDeadlineBase, str)):
            return doc_date
        try:
            template_base = TaskDeadlineBase(template_base)
        except ValueError:
            template_code = getattr(template, "code", "?")
            raise RuntimeError(
                f"TaskTemplate '{template_code}' has unsupported deadline_base={template_base}"
            ) from None

        template_code = getattr(template, "code", "?")
        if template_base == TaskDeadlineBase.RECEIVE_DATE:
            base_date = getattr(case, "recv_date", None)
            if base_date is None:
                raise RuntimeError(
                    f"TaskTemplate '{template_code}' missing recv_date for deadline_base=RECEIVE_DATE"
                )
            return base_date
        if template_base == TaskDeadlineBase.FILING_DATE:
            base_date = getattr(case, "filing_date", None)
            if base_date is None:
                raise RuntimeError(
                    f"TaskTemplate '{template_code}' missing filing_date for deadline_base=FILING_DATE"
                )
            return base_date
        if template_base == TaskDeadlineBase.PUB_DATE:
            base_date = getattr(case, "pub_date", None)
            if base_date is None:
                raise RuntimeError(
                    f"TaskTemplate '{template_code}' missing pub_date for deadline_base=PUB_DATE"
                )
            return base_date
        if template_base == TaskDeadlineBase.GRANT_DATE:
            base_date = getattr(case, "grant_date", None)
            if base_date is None:
                raise RuntimeError(
                    f"TaskTemplate '{template_code}' missing grant_date for deadline_base=GRANT_DATE"
                )
            return base_date
        if template_base in {
            TaskDeadlineBase.DISPATCH_DATE,
            TaskDeadlineBase.CASE_EVENT,
            TaskDeadlineBase.CUSTOM,
        }:
            return doc_date
        raise RuntimeError(
            f"TaskTemplate '{template_code}' has unsupported deadline_base={template_base}"
        )

    def _compute_due_date(self, document, case, template) -> date:
        """Compute due date from the template deadline base plus add_days/add_months."""
        confirmed_oa_due_date = self._resolve_confirmed_oa_due_date(document, template)
        if confirmed_oa_due_date is not None:
            return confirmed_oa_due_date

        official_due_date = self._resolve_official_due_date(document)
        if official_due_date is not None:
            return official_due_date

        base = self._resolve_deadline_base_date(document, case, template)
        if base is None:
            raise RuntimeError(
                f"TaskTemplate '{getattr(template, 'code', '?')}' missing a deadline base date"
            )
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

    def _resolve_confirmed_oa_due_date(self, document, template) -> date | None:
        if getattr(template, "code", None) not in {"OA_REPLY", "OA_REPLY_SUBSEQUENT"}:
            return None

        try:
            parsed = parse_document_extra_data(getattr(document, "extra_data", None))
        except DocumentExtraDataError as exc:
            raise_business_error(
                "OA_OFFICIAL_DUE_DATE_CONFLICT",
                "Executable OA task generation requires a consistent official due date tuple",
                details={"field": exc.field, "reason": exc.reason},
                status_code=409,
            )
        if parsed.official_due_date_status != "CONFIRMED":
            raise_business_error(
                "OA_OFFICIAL_DUE_DATE_REQUIRED",
                "Executable OA task generation requires a confirmed explicit official due date",
                details={"status": parsed.official_due_date_status},
                status_code=409,
            )
        return parsed.official_due_date

    def _resolve_official_due_date(self, document) -> date | None:
        raw_extra_data = getattr(document, "extra_data", None)
        if not raw_extra_data:
            return None

        try:
            extra_data = json.loads(raw_extra_data)
        except (TypeError, json.JSONDecodeError):
            return None

        if not isinstance(extra_data, dict) or "OfficialDueDate" not in extra_data:
            return None

        raw_due_date = extra_data.get("OfficialDueDate")
        if not isinstance(raw_due_date, str) or not raw_due_date.strip():
            raise_business_error(
                "DOCUMENT_OFFICIAL_DUE_DATE_INVALID",
                "OfficialDueDate must be an ISO date string",
                status_code=400,
            )

        try:
            return date.fromisoformat(raw_due_date.strip())
        except ValueError:
            raise_business_error(
                "DOCUMENT_OFFICIAL_DUE_DATE_INVALID",
                "OfficialDueDate must be an ISO date string",
                status_code=400,
            )

    def _resolve_remind_base_date(self, due_date: date, internal_due_date: date | None, template):
        remind_base = getattr(template, "remind_base", None)
        template_code = getattr(template, "code", "?")
        if remind_base is None or not isinstance(remind_base, (TaskRemindBase, str)):
            return due_date
        try:
            remind_base = TaskRemindBase(remind_base)
        except ValueError:
            raise RuntimeError(
                f"TaskTemplate '{template_code}' has unsupported remind_base={remind_base}"
            ) from None
        if remind_base == TaskRemindBase.DEADLINE:
            return due_date
        if remind_base == TaskRemindBase.INNER:
            if internal_due_date is None:
                raise RuntimeError(
                    f"TaskTemplate '{template_code}' missing internal_due_date for remind_base=INNER"
                )
            return internal_due_date
        raise RuntimeError(
            f"TaskTemplate '{template_code}' has unsupported remind_base={remind_base}"
        )

    def _compute_reminders(self, due_date: date, internal_due_date: date | None, template):
        remind_base_date = self._resolve_remind_base_date(due_date, internal_due_date, template)

        def _offset(base: date, days) -> date | None:
            if days is None or not isinstance(days, int):
                return None
            return base - timedelta(days=days)

        remind1 = _offset(remind_base_date, getattr(template, "remind_1_offset_days", None))
        remind2 = _offset(remind_base_date, getattr(template, "remind_2_offset_days", None))
        remind3 = _offset(remind_base_date, getattr(template, "remind_3_offset_days", None))

        if getattr(template, "daily_remind", False) is True:
            candidates = [d for d in (remind1, remind2, remind3) if d is not None]
            daily_remind_from = min(candidates) if candidates else remind_base_date
        else:
            daily_remind_from = None

        return remind1, remind2, remind3, daily_remind_from

    def synchronize_confirmed_oa_deadline(
        self,
        db: Session,
        *,
        document,
        case_id: str,
        task_template_code: str,
        due_date: date,
    ) -> Task:
        matching_rows = (
            db.query(Task, TaskTemplate)
            .join(TaskTemplate, Task.task_template_id == TaskTemplate.id)
            .filter(
                Task.case_id == case_id,
                Task.document_id == document.id,
                Task.status == TaskStatus.OPEN.value,
                TaskTemplate.code == task_template_code,
            )
            .all()
        )
        if len(matching_rows) != 1:
            raise_business_error(
                "OA_DEADLINE_TASK_MATCH_INVALID",
                "Deadline confirmation requires exactly one matching open OA task",
                details={
                    "source_document_id": document.id,
                    "task_template_code": task_template_code,
                    "matching_open_task_count": len(matching_rows),
                    "matching_open_task_ids": [task.id for task, _ in matching_rows],
                },
                status_code=409,
            )

        task, template = matching_rows[0]
        inner_offset = getattr(template, "inner_offset_days", None)
        internal_due_date = (
            due_date - timedelta(days=inner_offset) if inner_offset is not None else None
        )
        try:
            remind1, remind2, remind3, daily_remind_from = self._compute_reminders(
                due_date,
                internal_due_date,
                template,
            )
        except RuntimeError as exc:
            raise_business_error(
                "OA_DEADLINE_TASK_SYNC_CONFLICT",
                "OA task reminder configuration cannot be recalculated",
                details={
                    "source_document_id": document.id,
                    "task_id": task.id,
                    "task_template_code": task_template_code,
                    "reason": str(exc),
                },
                status_code=409,
            )

        def _iso(value: date | None) -> str | None:
            return value.isoformat() if value is not None else None

        evidence = json.dumps(
            {
                "event": "OFFICIAL_DEADLINE_CONFIRMED",
                "previous": {
                    "daily_remind_from": _iso(task.daily_remind_from),
                    "due_date": _iso(task.due_date),
                    "internal_due_date": _iso(task.internal_due_date),
                    "remind1": _iso(task.remind1),
                    "remind2": _iso(task.remind2),
                    "remind3": _iso(task.remind3),
                },
                "source_document_id": document.id,
                "task_template_code": task_template_code,
                "updated": {
                    "daily_remind_from": _iso(daily_remind_from),
                    "due_date": due_date.isoformat(),
                    "internal_due_date": _iso(internal_due_date),
                    "remind1": _iso(remind1),
                    "remind2": _iso(remind2),
                    "remind3": _iso(remind3),
                },
            },
            ensure_ascii=False,
            sort_keys=True,
        )
        task.due_date = due_date
        task.internal_due_date = internal_due_date
        task.remind1 = remind1
        task.remind2 = remind2
        task.remind3 = remind3
        task.daily_remind_from = daily_remind_from
        db.add(
            TaskLog(
                id=str(uuid4()),
                task_id=task.id,
                action=TaskAction.UPDATE.value,
                from_status=task.status,
                to_status=task.status,
                remark=evidence,
            )
        )
        return task

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
