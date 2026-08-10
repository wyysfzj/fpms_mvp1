from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.modules.system.grant_manual_review_role_service import (
    GrantManualReviewRoleDisposition,
)


class _StrictInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    @field_validator("*", mode="before")
    @classmethod
    def reject_non_exact_strings(cls, value: object) -> object:
        if isinstance(value, str) and (
            not value or value != value.strip() or "\x00" in value
        ):
            raise ValueError("string must be non-blank, trimmed and NUL-free")
        return value


def _canonical_uuid(value: str | None) -> str | None:
    if value is None:
        return None
    if str(UUID(value)) != value:
        raise ValueError("UUID must be canonical")
    return value


def _naive_datetime(value: datetime) -> datetime:
    if value.utcoffset() is not None:
        raise ValueError("timestamp must be timezone-naive UTC")
    return value


class PublishGrantManualReviewRoleConfigIn(_StrictInput):
    official_copy_acquirer_role_id: str
    first_verifier_role_id: str
    second_verifier_role_id: str
    manual_review_proposer_role_id: str
    manual_review_second_reviewer_role_id: str
    config_version: str = Field(max_length=128)
    effective_from: datetime
    effective_to: datetime | None
    expected_current_config_id: str | None
    idempotency_key: str = Field(max_length=128)

    _validate_acquirer = field_validator("official_copy_acquirer_role_id")(_canonical_uuid)
    _validate_first = field_validator("first_verifier_role_id")(_canonical_uuid)
    _validate_second = field_validator("second_verifier_role_id")(_canonical_uuid)
    _validate_proposer = field_validator("manual_review_proposer_role_id")(_canonical_uuid)
    _validate_second_reviewer = field_validator("manual_review_second_reviewer_role_id")(
        _canonical_uuid
    )
    _validate_expected = field_validator("expected_current_config_id")(_canonical_uuid)
    _validate_effective_from = field_validator("effective_from")(_naive_datetime)
    _validate_effective_to = field_validator("effective_to")(_naive_datetime)

    @model_validator(mode="after")
    def validate_interval(self) -> PublishGrantManualReviewRoleConfigIn:
        if self.effective_to is not None and self.effective_to <= self.effective_from:
            raise ValueError("effective_to must be later than effective_from")
        return self


class RevokeGrantManualReviewRoleConfigIn(_StrictInput):
    config_version: str = Field(max_length=128)
    effective_from: datetime
    expected_current_config_id: str
    idempotency_key: str = Field(max_length=128)

    _validate_effective_from = field_validator("effective_from")(_naive_datetime)
    _validate_expected = field_validator("expected_current_config_id")(_canonical_uuid)


class GrantManualReviewRoleConfigOut(BaseModel):
    config_id: str
    config_status: str
    config_snapshot_hash: str
    current_identity_key: str | None
    disposition: GrantManualReviewRoleDisposition
