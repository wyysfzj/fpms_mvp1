from __future__ import annotations

from collections.abc import Iterable
from typing import Any

import pytest

from framework.models import BoundaryCase, TestCase

COUNTRY_REF_ALIASES = {
    "DS-CN": "CN",
    "DS-CTY-CN": "CN",
    "DS-CTY-US": "US",
    "DS-CTY-JP": "JP",
    "DS-CTY-HK": "HK",
    "DS-CTY-EP": "EP",
    "CN": "CN",
    "US": "US",
    "JP": "JP",
    "HK": "HK",
    "EP": "EP",
}

CASE_TYPE_ALIASES = {
    "NORMAL": "NORMAL",
    "PCT_INTL": "PCT_INTL",
    "PCT_NATIONAL": "PCT_NATL",
    "PCT_NATL": "PCT_NATL",
    "INVALIDATION": "INVALIDATION",
    "PRIORITY": "PRIORITY",
    "CONSULTING": "CONSULTING",
    "SEARCH": "SEARCH",
}

PATENT_CATEGORY_ALIASES = {
    "INVENTION": "INV",
    "UTILITY": "UM",
    "UTILITY_MODEL": "UM",
    "DESIGN": "DES",
    "INV": "INV",
    "UM": "UM",
    "DES": "DES",
}

FLOW_DIR_ALIASES = {
    "IN_IN": "CN_DOMESTIC",
    "IN_OUT": "CN_OUTBOUND",
    "OUT_IN": "FOREIGN_INBOUND",
    "CN_DOMESTIC": "CN_DOMESTIC",
    "CN_OUTBOUND": "CN_OUTBOUND",
    "FOREIGN_INBOUND": "FOREIGN_INBOUND",
}

CASE_STATUS_ALIASES = {
    "NOT_FILED": "NOT_FILED",
    "PENDING": "PENDING",
    "GRANTED": "GRANTED",
    "REJECTED": "REJECTED",
    "WITHDRAWN": "WITHDRAWN",
    "ABANDONED": "ABANDONED",
    "EXPIRED": "EXPIRED",
    "WAITING_RECEIPT": "WAITING_RECEIPT",
    "PRELIM_EXAM": "PRELIM_EXAM",
    "PRELIM_PASS": "PRELIM_PASS",
    "AMENDMENT": "AMENDMENT",
    "PUBLISHED": "PUBLISHED",
    "SUB_EXAM": "SUB_EXAM",
    "OA1": "OA1",
    "OA2": "OA2",
    "REEXAM": "REEXAM",
    "ACCEPTED": "ACCEPTED",
    "GRANT_PENDING": "GRANT_PENDING",
    "TERMINATED": "TERMINATED",
    "INVALIDATED": "INVALIDATED",
}


def skeleton_case(func):
    func._is_skeleton = True  # type: ignore[attr-defined]
    return func


def case_mark_list(case: TestCase) -> list[pytest.MarkDecorator]:
    marks: list[pytest.MarkDecorator] = []
    priority_mark = getattr(pytest.mark, case.priority.lower(), None)
    if priority_mark:
        marks.append(priority_mark)
    wave_mark_name = f"wave_{case.wave.lower()}"
    wave_mark = getattr(pytest.mark, wave_mark_name, None)
    if wave_mark:
        marks.append(wave_mark)
    for category in case.categories:
        cat = category.lower().replace(" ", "_")
        if hasattr(pytest.mark, cat):
            marks.append(getattr(pytest.mark, cat))
    return marks


def build_case_params(cases: Iterable[TestCase]) -> list[pytest.ParameterSet]:
    params: list[pytest.ParameterSet] = []
    for case in cases:
        params.append(pytest.param(case, id=case.id, marks=case_mark_list(case)))
    return params


def build_boundary_params(cases: Iterable[BoundaryCase]) -> list[pytest.ParameterSet]:
    params: list[pytest.ParameterSet] = []
    for case in cases:
        params.append(pytest.param(case, id=case.id, marks=[pytest.mark.boundary]))
    return params


def unique_code(prefix: str, run_id: str, suffix: str | int | None = None) -> str:
    clean_prefix = _clean_required_text(prefix, "prefix")
    clean_run_id = _clean_required_text(run_id, "run_id")
    parts = [clean_prefix, clean_run_id]
    if suffix is not None:
        clean_suffix = _clean_required_text(str(suffix), "suffix")
        parts.append(clean_suffix)
    return "-".join(parts)


def normalize_country_ref(value: str) -> str:
    return _normalize_alias(value, COUNTRY_REF_ALIASES)


def normalize_case_type(value: str) -> str:
    return _normalize_alias(value, CASE_TYPE_ALIASES)


def normalize_patent_category(value: str) -> str:
    return _normalize_alias(value, PATENT_CATEGORY_ALIASES)


def normalize_flow_dir(value: str) -> str:
    return _normalize_alias(value, FLOW_DIR_ALIASES)


def normalize_case_status(value: str) -> str:
    return _normalize_alias(value, CASE_STATUS_ALIASES)


def normalize_payload_enums(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise TypeError("payload must be a dict")

    normalized = dict(payload)
    country_fields = ("from_country", "to_country", "country_code")
    for field in country_fields:
        if field in normalized:
            normalized[field] = normalize_country_ref(normalized[field])

    enum_normalizers = {
        "case_type": normalize_case_type,
        "patent_category": normalize_patent_category,
        "flow_dir": normalize_flow_dir,
        "status": normalize_case_status,
    }
    for field, normalizer in enum_normalizers.items():
        if field in normalized:
            normalized[field] = normalizer(normalized[field])
    return normalized


def _clean_required_text(value: str, field_name: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be a string")
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


def _normalize_alias(value: str, aliases: dict[str, str]) -> str:
    normalized = _clean_required_text(value, "value").upper()
    return aliases.get(normalized, normalized)
