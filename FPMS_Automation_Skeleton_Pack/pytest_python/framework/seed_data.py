from __future__ import annotations

import copy
import json
import os
from pathlib import Path
from typing import Any

import yaml

from framework.data_loader import DATA_ROOT, _expand
from framework.helpers import normalize_country_ref, normalize_payload_enums


class SeedDataError(RuntimeError):
    pass


class SeedNotFoundError(SeedDataError):
    pass


class DuplicateSeedIdError(SeedDataError):
    pass


class SeedCatalog:
    def __init__(self, records_by_group: dict[str, list[dict[str, Any]]], run_id: str):
        self.run_id = run_id
        self._records_by_group = copy.deepcopy(records_by_group)
        self._records_by_id: dict[str, dict[str, Any]] = {}
        self._build_index()

    @classmethod
    def load(
        cls, data_root: Path | None = None, run_id: str | None = None
    ) -> "SeedCatalog":
        seeds_root = data_root or DATA_ROOT / "seeds"
        resolved_run_id = run_id or os.getenv("FPMS_RUN_ID", "LOCAL-RUN-001")
        records_by_group: dict[str, list[dict[str, Any]]] = {}

        for path in sorted(seeds_root.iterdir()):
            if path.suffix not in {".yaml", ".yml", ".json"}:
                continue
            loaded = _load_seed_file(path)
            records_by_group[path.stem] = _extract_records(loaded)

        expanded = _expand(records_by_group, resolved_run_id)
        return cls(expanded, resolved_run_id)

    def get(self, seed_id: str) -> dict[str, Any]:
        record = self.maybe_get(seed_id)
        if record is None:
            raise SeedNotFoundError(f"Seed id not found: {seed_id}")
        return record

    def maybe_get(self, seed_id: str) -> dict[str, Any] | None:
        record = self._records_by_id.get(seed_id)
        if record is None:
            return None
        return copy.deepcopy(record)

    def list_by_group(self, group: str) -> list[dict[str, Any]]:
        return copy.deepcopy(self._records_by_group.get(group, []))

    def country_code(self, seed_or_code: str) -> str:
        if not isinstance(seed_or_code, str):
            raise TypeError("seed_or_code must be a string")
        value = seed_or_code.strip()
        if not value:
            raise ValueError("seed_or_code must not be empty")

        record = self._records_by_id.get(value)
        if record and isinstance(record.get("code"), str):
            return normalize_country_ref(record["code"])

        canonical = normalize_country_ref(value)
        record = self._records_by_id.get(canonical)
        if record and isinstance(record.get("code"), str):
            return normalize_country_ref(record["code"])
        return canonical

    def normalized(self, seed_id: str) -> dict[str, Any]:
        record = self.get(seed_id)
        normalized = normalize_payload_enums(record)
        if "country" in normalized:
            normalized["country"] = self.country_code(normalized["country"])
        return normalized

    def _build_index(self) -> None:
        for records in self._records_by_group.values():
            for record in records:
                seed_id = record.get("id")
                if not isinstance(seed_id, str) or not seed_id:
                    continue
                existing = self._records_by_id.get(seed_id)
                if existing is not None and existing != record:
                    raise DuplicateSeedIdError(f"Duplicate seed id: {seed_id}")
                self._records_by_id[seed_id] = copy.deepcopy(record)


def _load_seed_file(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        if path.suffix == ".json":
            return json.load(f)
        return yaml.safe_load(f)


def _extract_records(payload: Any) -> list[dict[str, Any]]:
    if payload is None:
        return []
    if isinstance(payload, list):
        return [copy.deepcopy(item) for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict):
        records: list[dict[str, Any]] = []
        for value in payload.values():
            if isinstance(value, list):
                records.extend(
                    copy.deepcopy(item) for item in value if isinstance(item, dict)
                )
            elif isinstance(value, dict):
                records.append(copy.deepcopy(value))
        return records
    return []
