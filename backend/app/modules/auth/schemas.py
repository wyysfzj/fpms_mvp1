from pydantic import BaseModel, Field, field_validator


class LoginRequest(BaseModel):
    """Login credentials."""

    username: str = Field(..., min_length=1, strip_whitespace=True)
    password: str = Field(..., min_length=1)

    @field_validator("username", mode="before")
    @classmethod
    def strip_username(cls, value: str) -> str:
        if isinstance(value, str):
            return value.strip()
        return value


class TokenResponse(BaseModel):
    """JWT access token response."""

    access_token: str
    token_type: str = "bearer"


class MeUser(BaseModel):
    """Current user basic profile."""

    id: str
    username: str
    is_active: bool


class MeResponse(BaseModel):
    """Current user profile with permissions."""

    user: MeUser
    roles: list[str]
    permissions: list[str]
