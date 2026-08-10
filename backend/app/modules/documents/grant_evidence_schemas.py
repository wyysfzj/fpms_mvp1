from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.modules.system.grant_evidence_source_service import GrantEvidenceScope


def _exact_text(value: str) -> str:
    if not value or value != value.strip() or "\x00" in value:
        raise ValueError("string must be non-blank, trimmed and NUL-free")
    return value


class GrantEvidenceFactIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(max_length=4096)
    raw_value: str = Field(max_length=4096)

    @field_validator("name", "raw_value")
    @classmethod
    def validate_exact_text(cls, value: str) -> str:
        return _exact_text(value)


class GrantEvidenceConflictIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(max_length=4096)
    raw_values: tuple[str, ...] = Field(min_length=2)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        return _exact_text(value)

    @field_validator("raw_values")
    @classmethod
    def validate_raw_values(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        for value in values:
            if len(value) > 4096:
                raise ValueError("raw value is too long")
            _exact_text(value)
        if len(set(values)) != len(values) or values != tuple(sorted(values)):
            raise ValueError("raw values must be distinct and sorted")
        return values


class GrantEvidenceCandidateIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    case_id: UUID
    evidence_version_id: UUID
    evidence_scope: GrantEvidenceScope
    expected_terminal_event_id: UUID
    facts: tuple[GrantEvidenceFactIn, ...] = Field(min_length=1)
    conflicts: tuple[GrantEvidenceConflictIn, ...] = ()

    @model_validator(mode="after")
    def validate_order_and_identity(self) -> GrantEvidenceCandidateIn:
        fact_pairs = tuple((fact.name, fact.raw_value) for fact in self.facts)
        if len({name for name, _value in fact_pairs}) != len(fact_pairs) or fact_pairs != tuple(
            sorted(fact_pairs)
        ):
            raise ValueError("facts must have unique names and canonical order")
        fact_names = {name for name, _value in fact_pairs}
        conflict_names = tuple(conflict.name for conflict in self.conflicts)
        if (
            len(set(conflict_names)) != len(conflict_names)
            or conflict_names != tuple(sorted(conflict_names))
            or any(name not in fact_names for name in conflict_names)
        ):
            raise ValueError("conflicts must reference facts in canonical order")
        return self


class GrantEvidenceCandidateOut(BaseModel):
    candidate_id: str
    evidence_version_id: str
    terminal_event_id: str
    source_config_id: str
    source_record_id: str
    proposal_role_config_id: str
    evidence_scope: GrantEvidenceScope
    acquisition_snapshot_hash: str
    candidate_snapshot_hash: str
    review_status: str
    disposition: str
