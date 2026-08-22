from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.modules.system.grant_evidence_source_service import (
    GrantEvidenceScope,
    GrantEvidenceSourceDisposition,
    GrantEvidenceSourceReferenceKind,
    GrantEvidenceSourceReviewDecision,
)


class _StrictInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    @field_validator("*", mode="before")
    @classmethod
    def reject_non_exact_strings(cls, value: object) -> object:
        if isinstance(value, str) and (not value or value != value.strip() or "\x00" in value):
            raise ValueError("string must be non-blank, trimmed and NUL-free")
        return value


def _canonical_uuid(value: str | None) -> str | None:
    if value is None:
        return None
    if str(UUID(value)) != value:
        raise ValueError("UUID must be canonical")
    return value


def _naive_datetime(value: datetime | None) -> datetime | None:
    if value is not None and value.utcoffset() is not None:
        raise ValueError("timestamp must be timezone-naive UTC")
    return value


class RegisterGrantEvidenceSourceIn(_StrictInput):
    source_code: str = Field(max_length=64)
    source_version: str = Field(max_length=128)
    evidence_scope: GrantEvidenceScope
    source_reference_kind: GrantEvidenceSourceReferenceKind
    source_reference_value: str = Field(max_length=512)
    acquisition_method: str = Field(max_length=64)
    effective_from: datetime
    effective_to: datetime | None
    supersedes_source_id: str | None
    idempotency_key: str = Field(max_length=128)

    _validate_supersedes = field_validator("supersedes_source_id")(_canonical_uuid)
    _validate_effective_from = field_validator("effective_from")(_naive_datetime)
    _validate_effective_to = field_validator("effective_to")(_naive_datetime)

    @model_validator(mode="after")
    def validate_interval(self) -> RegisterGrantEvidenceSourceIn:
        if self.effective_to is not None and self.effective_to <= self.effective_from:
            raise ValueError("effective_to must be later than effective_from")
        return self


class ReviewGrantEvidenceSourceIn(_StrictInput):
    decision: GrantEvidenceSourceReviewDecision
    reason: str = Field(max_length=2048)


class ActivateGrantEvidenceSourceIn(_StrictInput):
    expected_current_source_id: str | None

    _validate_expected = field_validator("expected_current_source_id")(_canonical_uuid)


class RetireGrantEvidenceSourceIn(_StrictInput):
    expected_current_source_id: str

    _validate_expected = field_validator("expected_current_source_id")(_canonical_uuid)


class PublishGrantEvidenceSourceConfigIn(_StrictInput):
    evidence_scope: GrantEvidenceScope
    source_record_id: str
    config_version: str = Field(max_length=128)
    effective_from: datetime
    effective_to: datetime | None
    selection_reason: str = Field(max_length=2048)
    expected_current_config_id: str | None
    idempotency_key: str = Field(max_length=128)

    _validate_source = field_validator("source_record_id")(_canonical_uuid)
    _validate_expected = field_validator("expected_current_config_id")(_canonical_uuid)
    _validate_effective_from = field_validator("effective_from")(_naive_datetime)
    _validate_effective_to = field_validator("effective_to")(_naive_datetime)

    @model_validator(mode="after")
    def validate_interval(self) -> PublishGrantEvidenceSourceConfigIn:
        if self.effective_to is not None and self.effective_to <= self.effective_from:
            raise ValueError("effective_to must be later than effective_from")
        return self


class RevokeGrantEvidenceSourceConfigIn(_StrictInput):
    evidence_scope: GrantEvidenceScope
    config_version: str = Field(max_length=128)
    effective_from: datetime
    selection_reason: str = Field(max_length=2048)
    expected_current_config_id: str
    idempotency_key: str = Field(max_length=128)

    _validate_expected = field_validator("expected_current_config_id")(_canonical_uuid)
    _validate_effective_from = field_validator("effective_from")(_naive_datetime)


class GrantEvidenceSourceRecordOut(BaseModel):
    source_record_id: str
    review_status: str
    activation_status: str
    source_snapshot_hash: str
    current_identity_key: str | None
    disposition: GrantEvidenceSourceDisposition


class GrantEvidenceSourceConfigOut(BaseModel):
    config_id: str
    config_status: str
    config_snapshot_hash: str
    current_identity_key: str | None
    disposition: GrantEvidenceSourceDisposition
