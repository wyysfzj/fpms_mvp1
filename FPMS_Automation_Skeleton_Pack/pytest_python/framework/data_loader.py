from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

from framework.models import BoundaryCase, TestCase

ROOT = Path(__file__).resolve().parents[2]
DATA_ROOT = ROOT / "data"


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _expand(value: Any, run_id: str) -> Any:
    if isinstance(value, str):
        return value.replace("${RUN_ID}", run_id)
    if isinstance(value, list):
        return [_expand(v, run_id) for v in value]
    if isinstance(value, dict):
        return {k: _expand(v, run_id) for k, v in value.items()}
    return value


def load_wave_cases(wave: str, run_id: str | None = None) -> list[TestCase]:
    payload = _load_yaml(DATA_ROOT / "testcases" / "by_wave" / f"{wave.lower()}.yaml")
    run_id = run_id or os.getenv("FPMS_RUN_ID", "LOCAL-RUN-001")
    return [TestCase.from_dict(_expand(item, run_id)) for item in payload["cases"]]


def load_all_cases(run_id: str | None = None) -> list[TestCase]:
    payload = _load_yaml(DATA_ROOT / "testcases" / "all_testcases.yaml")
    run_id = run_id or os.getenv("FPMS_RUN_ID", "LOCAL-RUN-001")
    return [TestCase.from_dict(_expand(item, run_id)) for item in payload["testcases"]]


def load_boundary_cases(run_id: str | None = None) -> list[BoundaryCase]:
    payload = _load_yaml(DATA_ROOT / "boundary" / "boundary_matrix.yaml")
    run_id = run_id or os.getenv("FPMS_RUN_ID", "LOCAL-RUN-001")
    return [
        BoundaryCase.from_dict(_expand(item, run_id))
        for item in payload["boundary_cases"]
    ]
