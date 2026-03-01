"""Enumerations for Cases module."""

from enum import Enum


class CaseType(str, Enum):
    """Case type classification."""

    NORMAL = "NORMAL"  # Normal application
    PCT_INTL = "PCT_INTL"  # PCT international phase
    PCT_NATL = "PCT_NATL"  # PCT national phase
    PRIORITY = "PRIORITY"  # Priority claim only
    CONSULTING = "CONSULTING"  # Consulting project
    SEARCH = "SEARCH"  # Prior-art / patent search project


class FlowDir(str, Enum):
    """Application flow direction."""

    CN_DOMESTIC = "CN_DOMESTIC"  # China domestic
    CN_OUTBOUND = "CN_OUTBOUND"  # China to foreign
    FOREIGN_INBOUND = "FOREIGN_INBOUND"  # Foreign to China


class PatentCategory(str, Enum):
    """Patent category (type)."""

    INV = "INV"  # Invention patent
    UM = "UM"  # Utility model
    DES = "DES"  # Design patent


class CaseStatus(str, Enum):
    """Case lifecycle status."""

    # Existing (preserved for backward compatibility)
    NOT_FILED = "NOT_FILED"  # Not yet filed
    PENDING = "PENDING"  # Under examination
    GRANTED = "GRANTED"  # Patent granted
    REJECTED = "REJECTED"  # Application rejected
    WITHDRAWN = "WITHDRAWN"  # Application withdrawn
    ABANDONED = "ABANDONED"  # Abandoned
    EXPIRED = "EXPIRED"  # Patent expired

    # V3 Workflow Stepper statuses
    WAITING_RECEIPT = "WAITING_RECEIPT"  # 受理 - Waiting for receipt
    PRELIM_EXAM = "PRELIM_EXAM"  # 初审 - Preliminary examination
    PRELIM_PASS = "PRELIM_PASS"  # 初审通过 - Preliminary exam passed
    AMENDMENT = "AMENDMENT"  # 补正 - Amendment required
    PUBLISHED = "PUBLISHED"  # 公布 - Application published
    SUB_EXAM = "SUB_EXAM"  # 实审 - Substantive examination
    OA1 = "OA1"  # 第一次审查意见 - First office action
    OA2 = "OA2"  # 第二次审查意见 - Second office action
    REEXAM = "REEXAM"  # 复审 - Re-examination
    TERMINATED = "TERMINATED"  # 终止 - Patent terminated
    INVALIDATED = "INVALIDATED"  # 无效 - Patent invalidated
