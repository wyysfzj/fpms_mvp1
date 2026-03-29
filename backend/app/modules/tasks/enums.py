"""Enumerations for Tasks module."""

from enum import Enum


class TaskStatus(str, Enum):
    OPEN = "OPEN"
    DONE = "DONE"
    CANCELLED = "CANCELLED"


class TaskAction(str, Enum):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    ASSIGN = "ASSIGN"
    CLOSE = "CLOSE"
    REOPEN = "REOPEN"
    CANCEL = "CANCEL"
    AUTO_CREATE = "AUTO_CREATE"
    AUTO_CREATE_FROM_DOCUMENT = "AUTO_CREATE_FROM_DOCUMENT"
    AUTO_WRITEOFF = "AUTO_WRITEOFF"
    STATUS_CHANGE = "STATUS_CHANGE"


class TaskTodayAs(str, Enum):
    WORKER = "worker"
    SUPERVISOR = "supervisor"


class TaskDeadlineBase(str, Enum):
    FILING_DATE = "FILING_DATE"
    RECEIVE_DATE = "RECEIVE_DATE"
    DISPATCH_DATE = "DISPATCH_DATE"
    PUB_DATE = "PUB_DATE"
    GRANT_DATE = "GRANT_DATE"
    CASE_EVENT = "CASE_EVENT"
    CUSTOM = "CUSTOM"


class TaskRemindBase(str, Enum):
    INNER = "INNER"
    DEADLINE = "DEADLINE"
