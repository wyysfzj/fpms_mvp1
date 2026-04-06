"""Enumerations for Documents module."""

from enum import Enum


class DocumentDirection(str, Enum):
    IN = "IN"
    OUT = "OUT"


class DocumentDocType(str, Enum):
    OFFICIAL_IN = "OFFICIAL_IN"
    OFFICIAL_OUT = "OFFICIAL_OUT"
    CLIENT_IN = "CLIENT_IN"
    CLIENT_OUT = "CLIENT_OUT"
