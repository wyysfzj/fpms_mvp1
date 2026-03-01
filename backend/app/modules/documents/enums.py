"""Enumerations for Documents module."""

from enum import Enum


class DocumentDirection(str, Enum):
    IN = "IN"
    OUT = "OUT"
