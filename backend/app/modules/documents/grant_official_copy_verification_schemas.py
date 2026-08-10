from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.modules.documents.grant_official_copy_verification_service import (
    GrantOfficialCopyDisposition,
    GrantOfficialCopyEventType,
)
from app.modules.system.grant_evidence_source_service import GrantEvidenceScope


class GrantOfficialCopyEventIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    evidence_scope: GrantEvidenceScope
    event_type: GrantOfficialCopyEventType
    reason: str = Field(max_length=4096)
    original_reference: str | None = Field(max_length=512)
    expected_current_event_id: str | None
    idempotency_key: str = Field(max_length=128)

    @field_validator("*", mode="before")
    @classmethod
    def reject_non_exact_strings(cls, value: object) -> object:
        if isinstance(value, str) and (
            not value or value != value.strip() or "\x00" in value
        ):
            raise ValueError("string must be non-blank, trimmed and NUL-free")
        return value

    @field_validator("expected_current_event_id")
    @classmethod
    def validate_expected_current_event_id(cls, value: str | None) -> str | None:
        if value is not None and str(UUID(value)) != value:
            raise ValueError("UUID must be canonical")
        return value

    @model_validator(mode="after")
    def validate_stage_shape(self) -> GrantOfficialCopyEventIn:
        if self.event_type is GrantOfficialCopyEventType.ACQUIRED:
            if self.original_reference is None or self.expected_current_event_id is not None:
                raise ValueError("ACQUIRED requires reference and no expected current event")
        elif self.original_reference is not None or self.expected_current_event_id is None:
            raise ValueError("verification requires expected current event and no reference")
        return self


class GrantOfficialCopyEventOut(BaseModel):
    event_id: str
    evidence_version_id: str
    evidence_scope: GrantEvidenceScope
    event_type: GrantOfficialCopyEventType
    source_config_id: str
    source_record_id: str
    role_config_id: str
    event_snapshot_hash: str
    current_identity_key: str | None
    disposition: GrantOfficialCopyDisposition
