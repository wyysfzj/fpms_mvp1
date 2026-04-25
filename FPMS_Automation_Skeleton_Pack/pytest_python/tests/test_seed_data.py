from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from framework.seed_data import (
    DuplicateSeedIdError,
    SeedCatalog,
    SeedNotFoundError,
)


def test_loads_existing_seed_files_and_lists_groups() -> None:
    catalog = SeedCatalog.load(run_id="RUN-SEED-001")

    countries = catalog.list_by_group("countries")

    assert len(countries) >= 5
    assert countries[0]["id"] == "DS-CTY-CN"
    assert catalog.get("DS-CTY-CN")["code"] == "CN"


def test_get_and_list_by_group_return_defensive_copies() -> None:
    catalog = SeedCatalog.load(run_id="RUN-SEED-001")

    country = catalog.get("DS-CTY-CN")
    country["code"] = "MUTATED"
    countries = catalog.list_by_group("countries")
    countries[0]["code"] = "MUTATED"

    assert catalog.get("DS-CTY-CN")["code"] == "CN"
    assert catalog.list_by_group("countries")[0]["code"] == "CN"


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("DS-CN", "CN"),
        ("DS-CTY-CN", "CN"),
        ("CN", "CN"),
        (" ds-cty-us ", "US"),
    ],
)
def test_country_code_resolves_aliases_and_real_codes(
    value: str, expected: str
) -> None:
    catalog = SeedCatalog.load(run_id="RUN-SEED-001")

    assert catalog.country_code(value) == expected


def test_country_code_rejects_empty_and_non_string_values() -> None:
    catalog = SeedCatalog.load(run_id="RUN-SEED-001")

    with pytest.raises(ValueError):
        catalog.country_code(" ")
    with pytest.raises(TypeError):
        catalog.country_code(123)  # type: ignore[arg-type]


def test_run_id_is_expanded_recursively(tmp_path: Path) -> None:
    seeds_root = tmp_path / "seeds"
    seeds_root.mkdir()
    (seeds_root / "dynamic.yaml").write_text(
        yaml.safe_dump(
            [
                {
                    "id": "DS-DYN-001",
                    "case_no": "CASE-A-${RUN_ID}-001",
                    "nested": {"value": "BILL-${RUN_ID}"},
                    "items": ["PAY-${RUN_ID}"],
                }
            ],
            allow_unicode=True,
        ),
        encoding="utf-8",
    )

    catalog = SeedCatalog.load(data_root=seeds_root, run_id="RUN42")

    record = catalog.get("DS-DYN-001")
    assert record["case_no"] == "CASE-A-RUN42-001"
    assert record["nested"]["value"] == "BILL-RUN42"
    assert record["items"] == ["PAY-RUN42"]


def test_normalized_returns_new_record_with_known_fields_normalized() -> None:
    catalog = SeedCatalog(
        {
            "cases": [
                {
                    "id": "DS-CASE-001",
                    "country": "DS-CN",
                    "from_country": "DS-CTY-CN",
                    "case_type": "PCT_NATIONAL",
                    "patent_category": "INVENTION",
                    "flow_dir": "IN_OUT",
                    "status": "sub_exam",
                }
            ]
        },
        run_id="RUN-SEED-001",
    )

    normalized = catalog.normalized("DS-CASE-001")

    assert normalized == {
        "id": "DS-CASE-001",
        "country": "CN",
        "from_country": "CN",
        "case_type": "PCT_NATL",
        "patent_category": "INV",
        "flow_dir": "CN_OUTBOUND",
        "status": "SUB_EXAM",
    }
    assert catalog.get("DS-CASE-001")["country"] == "DS-CN"


def test_missing_seed_id_behaviors_are_clear() -> None:
    catalog = SeedCatalog.load(run_id="RUN-SEED-001")

    assert catalog.maybe_get("DS-MISSING") is None
    with pytest.raises(SeedNotFoundError):
        catalog.get("DS-MISSING")


def test_conflicting_duplicate_seed_ids_are_rejected(tmp_path: Path) -> None:
    seeds_root = tmp_path / "seeds"
    seeds_root.mkdir()
    (seeds_root / "first.yaml").write_text(
        yaml.safe_dump([{"id": "DS-DUP-001", "value": "first"}]),
        encoding="utf-8",
    )
    (seeds_root / "second.json").write_text(
        json.dumps([{"id": "DS-DUP-001", "value": "second"}]),
        encoding="utf-8",
    )

    with pytest.raises(DuplicateSeedIdError):
        SeedCatalog.load(data_root=seeds_root, run_id="RUN-SEED-001")


def test_json_seed_files_are_loaded(tmp_path: Path) -> None:
    seeds_root = tmp_path / "seeds"
    seeds_root.mkdir()
    (seeds_root / "json_group.json").write_text(
        json.dumps({"items": [{"id": "DS-JSON-001", "value": "ok"}]}),
        encoding="utf-8",
    )

    catalog = SeedCatalog.load(data_root=seeds_root, run_id="RUN-SEED-001")

    assert catalog.get("DS-JSON-001")["value"] == "ok"
    assert catalog.list_by_group("json_group")[0]["id"] == "DS-JSON-001"
