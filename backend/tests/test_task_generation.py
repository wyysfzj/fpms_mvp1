from __future__ import annotations

from datetime import date, timedelta
from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.modules.cases.models import Case
from app.modules.tasks.enums import TaskDeadlineBase, TaskRemindBase
from app.modules.tasks.models import TaskTemplate
from app.modules.tasks.task_generation_service import TaskGenerationService


class _FakeQuery:
    def __init__(self, model, template=None, case=None) -> None:
        self.model = model
        self.template = template
        self.case = case

    def filter(self, *_args, **_kwargs) -> "_FakeQuery":
        return self

    def all(self) -> list[TaskTemplate]:
        if self.model is TaskTemplate:
            return [self.template]
        return []

    def first(self):
        if self.model is Case:
            return self.case
        return None


class _FakeDB:
    def __init__(self, template, case) -> None:
        self.template = template
        self.case = case

    def query(self, model) -> _FakeQuery:
        return _FakeQuery(model, template=self.template, case=self.case)

    def add(self, _obj) -> None:
        return None


def test_generate_from_document_uses_template_deadline_and_reminder_bases() -> None:
    svc = TaskGenerationService()

    template = SimpleNamespace(
        id=str(uuid4()),
        code="OA_REPLY",
        name="OA答复期限",
        enabled=True,
        deadline_base=TaskDeadlineBase.RECEIVE_DATE,
        add_days=30,
        add_months=0,
        inner_offset_days=7,
        remind_base=TaskRemindBase.INNER,
        remind_1_offset_days=1,
        remind_2_offset_days=3,
        remind_3_offset_days=5,
        daily_remind=True,
    )
    case = SimpleNamespace(
        id=str(uuid4()),
        recv_date=date(2025, 1, 5),
        filing_date=date(2025, 1, 6),
        pub_date=date(2025, 1, 7),
        grant_date=date(2025, 1, 8),
    )
    document = SimpleNamespace(
        id=str(uuid4()),
        case_id=case.id,
        doc_date=date(2025, 1, 10),
        direction="IN",
        doc_type="OA_REPLY",
        title="第一次审查意见通知书",
        case=None,
    )
    db = _FakeDB(template=template, case=case)

    tasks = svc.generate_from_document(db, document)

    assert len(tasks) == 1
    task = tasks[0]
    expected_due = date(2025, 1, 5) + timedelta(days=30)
    expected_internal_due = expected_due - timedelta(days=7)
    assert task.due_date == expected_due
    assert task.internal_due_date == expected_internal_due
    assert task.remind1 == expected_internal_due - timedelta(days=1)
    assert task.remind2 == expected_internal_due - timedelta(days=3)
    assert task.remind3 == expected_internal_due - timedelta(days=5)
    assert task.daily_remind is True
    assert task.daily_remind_from == expected_internal_due - timedelta(days=5)


def test_generate_from_document_uses_deadline_reminder_base_when_configured() -> None:
    svc = TaskGenerationService()

    template = SimpleNamespace(
        id=str(uuid4()),
        code="OA_REPLY",
        name="OA答复期限",
        enabled=True,
        deadline_base=TaskDeadlineBase.RECEIVE_DATE,
        add_days=30,
        add_months=0,
        inner_offset_days=7,
        remind_base=TaskRemindBase.DEADLINE,
        remind_1_offset_days=1,
        remind_2_offset_days=3,
        remind_3_offset_days=5,
        daily_remind=True,
    )
    case = SimpleNamespace(
        id=str(uuid4()),
        recv_date=date(2025, 1, 5),
    )
    document = SimpleNamespace(
        id=str(uuid4()),
        case_id=case.id,
        doc_date=date(2025, 1, 10),
        direction="IN",
        doc_type="OA_REPLY",
        title="第一次审查意见通知书",
        case=None,
    )
    db = _FakeDB(template=template, case=case)

    tasks = svc.generate_from_document(db, document)

    assert len(tasks) == 1
    task = tasks[0]
    expected_due = date(2025, 1, 5) + timedelta(days=30)
    assert task.due_date == expected_due
    assert task.internal_due_date == expected_due - timedelta(days=7)
    assert task.remind1 == expected_due - timedelta(days=1)
    assert task.remind2 == expected_due - timedelta(days=3)
    assert task.remind3 == expected_due - timedelta(days=5)
    assert task.daily_remind is True
    assert task.daily_remind_from == expected_due - timedelta(days=5)


@pytest.mark.parametrize(
    ("deadline_base", "expected_base_date"),
    [
        (TaskDeadlineBase.FILING_DATE, date(2025, 1, 6)),
        (TaskDeadlineBase.RECEIVE_DATE, date(2025, 1, 5)),
        (TaskDeadlineBase.DISPATCH_DATE, date(2025, 1, 10)),
        (TaskDeadlineBase.PUB_DATE, date(2025, 1, 7)),
        (TaskDeadlineBase.GRANT_DATE, date(2025, 1, 8)),
        (TaskDeadlineBase.CASE_EVENT, date(2025, 1, 10)),
        (TaskDeadlineBase.CUSTOM, date(2025, 1, 10)),
    ],
)
def test_generate_from_document_uses_each_supported_deadline_base(
    deadline_base: TaskDeadlineBase,
    expected_base_date: date,
) -> None:
    svc = TaskGenerationService()

    template = SimpleNamespace(
        id=str(uuid4()),
        code="OA_REPLY",
        name="OA答复期限",
        enabled=True,
        deadline_base=deadline_base,
        add_days=30,
        add_months=0,
        inner_offset_days=7,
        remind_base=TaskRemindBase.DEADLINE,
        remind_1_offset_days=1,
        remind_2_offset_days=3,
        remind_3_offset_days=5,
        daily_remind=False,
    )
    case = SimpleNamespace(
        id=str(uuid4()),
        recv_date=date(2025, 1, 5),
        filing_date=date(2025, 1, 6),
        pub_date=date(2025, 1, 7),
        grant_date=date(2025, 1, 8),
    )
    document = SimpleNamespace(
        id=str(uuid4()),
        case_id=case.id,
        doc_date=date(2025, 1, 10),
        direction="IN",
        doc_type="OA_REPLY",
        title="第一次审查意见通知书",
        case=None,
    )
    db = _FakeDB(template=template, case=case)

    tasks = svc.generate_from_document(db, document)

    assert len(tasks) == 1
    assert tasks[0].due_date == expected_base_date + timedelta(days=30)


def test_generate_from_document_raises_when_deadline_base_case_date_missing() -> None:
    svc = TaskGenerationService()

    template = SimpleNamespace(
        id=str(uuid4()),
        code="OA_REPLY",
        name="OA答复期限",
        enabled=True,
        deadline_base=TaskDeadlineBase.RECEIVE_DATE,
        add_days=30,
        add_months=0,
        inner_offset_days=7,
        remind_base=TaskRemindBase.DEADLINE,
        remind_1_offset_days=1,
        remind_2_offset_days=3,
        remind_3_offset_days=5,
        daily_remind=False,
    )
    case = SimpleNamespace(
        id=str(uuid4()),
        recv_date=None,
    )
    document = SimpleNamespace(
        id=str(uuid4()),
        case_id=case.id,
        doc_date=date(2025, 1, 10),
        direction="IN",
        doc_type="OA_REPLY",
        title="第一次审查意见通知书",
        case=None,
    )
    db = _FakeDB(template=template, case=case)

    with pytest.raises(RuntimeError, match="missing recv_date for deadline_base=RECEIVE_DATE"):
        svc.generate_from_document(db, document)


def test_generate_from_document_raises_on_unsupported_deadline_or_remind_base() -> None:
    svc = TaskGenerationService()

    template = SimpleNamespace(
        id=str(uuid4()),
        code="OA_REPLY",
        name="OA答复期限",
        enabled=True,
        deadline_base=TaskDeadlineBase.RECEIVE_DATE,
        add_days=30,
        add_months=0,
        inner_offset_days=7,
        remind_base="BROKEN",
        remind_1_offset_days=1,
        remind_2_offset_days=3,
        remind_3_offset_days=5,
        daily_remind=True,
    )
    case = SimpleNamespace(
        id=str(uuid4()),
        recv_date=date(2025, 1, 5),
    )
    document = SimpleNamespace(
        id=str(uuid4()),
        case_id=case.id,
        doc_date=date(2025, 1, 10),
        direction="IN",
        doc_type="OA_REPLY",
        title="第一次审查意见通知书",
        case=None,
    )
    db = _FakeDB(template=template, case=case)

    with pytest.raises(RuntimeError, match="unsupported remind_base"):
        svc.generate_from_document(db, document)
