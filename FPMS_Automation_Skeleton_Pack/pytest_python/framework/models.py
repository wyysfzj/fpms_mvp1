from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class TestCase:
    id: str
    wave: str
    wave_title: str
    context: str
    priority: str
    categories: list[str]
    topic: str
    stage_code: str | None
    stage_name: str
    coverage_ids: list[str]
    requirement_ids: list[str]
    validation_ids: list[str]
    preconditions: str
    steps_summary: str
    expected: str
    automation_recommendation: str
    data_refs: list[str] = field(default_factory=list)
    dynamic_refs: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    status: str = "skeleton_ready"

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "TestCase":
        return cls(**payload)


@dataclass(frozen=True)
class BoundaryCase:
    id: str
    object: str
    boundary_point: str
    test_values: str
    expected: str
    tags: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "BoundaryCase":
        return cls(**payload)
