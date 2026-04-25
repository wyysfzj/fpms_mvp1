from __future__ import annotations

import pytest

from framework.helpers import (
    normalize_case_status,
    normalize_case_type,
    normalize_country_ref,
    normalize_flow_dir,
    normalize_patent_category,
    normalize_payload_enums,
    unique_code,
)


def test_unique_code_builds_stable_run_id_based_values() -> None:
    assert unique_code("CASE-A", "LOCAL-RUN-001", "001") == "CASE-A-LOCAL-RUN-001-001"
    assert unique_code(" PAY ", " RUN42 ") == "PAY-RUN42"
    assert unique_code("CASE", "RUN42", 7) == "CASE-RUN42-7"


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("DS-CN", "CN"),
        ("DS-CTY-CN", "CN"),
        ("CN", "CN"),
        (" ds-cty-us ", "US"),
    ],
)
def test_normalize_country_ref_maps_skeleton_refs_to_real_country_codes(
    value: str, expected: str
) -> None:
    assert normalize_country_ref(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("NORMAL", "NORMAL"),
        ("PCT_NATIONAL", "PCT_NATL"),
        ("PCT_NATL", "PCT_NATL"),
        ("priority", "PRIORITY"),
    ],
)
def test_normalize_case_type_maps_skeleton_values_to_real_enums(
    value: str, expected: str
) -> None:
    assert normalize_case_type(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("INVENTION", "INV"),
        ("UTILITY", "UM"),
        ("UTILITY_MODEL", "UM"),
        ("DESIGN", "DES"),
        ("INV", "INV"),
        ("um", "UM"),
    ],
)
def test_normalize_patent_category_maps_skeleton_values_to_real_enums(
    value: str, expected: str
) -> None:
    assert normalize_patent_category(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("IN_IN", "CN_DOMESTIC"),
        ("IN_OUT", "CN_OUTBOUND"),
        ("OUT_IN", "FOREIGN_INBOUND"),
        ("CN_DOMESTIC", "CN_DOMESTIC"),
        ("cn_outbound", "CN_OUTBOUND"),
    ],
)
def test_normalize_flow_dir_maps_skeleton_values_to_real_enums(
    value: str, expected: str
) -> None:
    assert normalize_flow_dir(value) == expected


@pytest.mark.parametrize(
    "value",
    [
        "NOT_FILED",
        "WAITING_RECEIPT",
        "SUB_EXAM",
        "OA1",
        "OA2",
        "GRANTED",
        "TERMINATED",
    ],
)
def test_normalize_case_status_keeps_real_case_status_values(value: str) -> None:
    assert normalize_case_status(value.lower()) == value


def test_unknown_non_empty_values_are_preserved_after_normalization() -> None:
    assert normalize_case_type("future_type") == "FUTURE_TYPE"
    assert normalize_flow_dir("future_flow") == "FUTURE_FLOW"


@pytest.mark.parametrize(
    "normalizer",
    [
        normalize_country_ref,
        normalize_case_type,
        normalize_patent_category,
        normalize_flow_dir,
        normalize_case_status,
    ],
)
def test_normalizers_reject_non_string_and_empty_values(normalizer) -> None:
    with pytest.raises(TypeError):
        normalizer(123)
    with pytest.raises(ValueError):
        normalizer(" ")


def test_normalize_payload_enums_returns_new_dict_without_mutating_input() -> None:
    payload = {
        "from_country": "DS-CN",
        "to_country": "ds-cty-us",
        "country_code": "DS-CTY-JP",
        "case_type": "PCT_NATIONAL",
        "patent_category": "INVENTION",
        "flow_dir": "IN_OUT",
        "status": "sub_exam",
        "title_cn": "测试案卷",
    }

    normalized = normalize_payload_enums(payload)

    assert normalized is not payload
    assert payload["case_type"] == "PCT_NATIONAL"
    assert normalized == {
        "from_country": "CN",
        "to_country": "US",
        "country_code": "JP",
        "case_type": "PCT_NATL",
        "patent_category": "INV",
        "flow_dir": "CN_OUTBOUND",
        "status": "SUB_EXAM",
        "title_cn": "测试案卷",
    }
