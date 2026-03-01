from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import current_user_dep
from app.core.config import get_settings
from app.core.errors import raise_business_error
from app.core.security import create_access_token
from app.db.session import get_db
from app.modules.auth.models import T_Role, T_User, T_UserRole
from app.modules.auth.schemas import LoginRequest, MeResponse, MeUser, TokenResponse
from app.modules.auth.service import authenticate_user
from app.modules.rbac.service import get_user_permissions

router = APIRouter()


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Login and receive JWT token",
)
def login(credentials: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    """
    Authenticate user and return JWT token.

    **Auth**: Bearer JWT (not required for login)
    **Permission**: None
    **Request example**:
    ```json
    {"username": "admin", "password": "admin123"}
    ```
    **Curl example**:
    ```bash
    curl -s -X POST http://localhost:8000/api/v1/auth/login \\
      -H "Content-Type: application/json" \\
      -d '{"username":"admin","password":"admin123"}'
    ```
    **Responses**:
    - 200: Token issued
    - 401: AUTH_INVALID
    - 422: VALIDATION_ERROR
    """
    user = authenticate_user(db, credentials.username, credentials.password)

    if not user:
        raise_business_error(
            code="AUTH_INVALID",
            message="Invalid username or password",
            status_code=401,
        )

    settings = get_settings()
    access_token = create_access_token(
        subject=user.id,
        secret=settings.jwt_secret,
        expires_minutes=settings.jwt_expire_minutes or 60,
    )

    return TokenResponse(access_token=access_token)


@router.get(
    "/me",
    response_model=MeResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current authenticated user profile",
)
def get_me(
    current_user: T_User = current_user_dep,
    db: Session = Depends(get_db),
) -> MeResponse:
    """
    Return current user profile with role and permission lists.

    **Auth**: Bearer JWT (required)
    **Permission**: Authenticated user
    **Responses**:
    - 200: Current user profile
    - 401: AUTH_REQUIRED
    """
    role_rows = (
        db.query(T_Role.code)
        .join(T_UserRole, T_UserRole.role_id == T_Role.id)
        .filter(T_UserRole.user_id == current_user.id)
        .all()
    )
    roles = sorted(row[0] for row in role_rows)
    permissions = sorted(get_user_permissions(db, current_user.id))

    return MeResponse(
        user=MeUser(
            id=current_user.id,
            username=current_user.username,
            is_active=current_user.is_active,
        ),
        roles=roles,
        permissions=permissions,
    )
