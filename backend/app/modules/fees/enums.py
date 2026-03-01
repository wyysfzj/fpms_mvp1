"""Enumerations for Fees module."""

from enum import Enum


class FeeType(str, Enum):
    GOV = "GOV"
    SERVICE = "SERVICE"
    MISC = "MISC"


class CalcMode(str, Enum):
    FIXED = "FIXED"
    PER_CLAIM = "PER_CLAIM"
    PER_PAGE = "PER_PAGE"
    TIER = "TIER"


class FeeDraftStatus(str, Enum):
    OPEN = "OPEN"
    LOCKED = "LOCKED"
