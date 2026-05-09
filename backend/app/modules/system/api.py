from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import current_user_dep, require_perm
from app.db.session import get_db
from app.modules.auth.models import T_User
from app.modules.system.schemas import (
    ConfigReadinessOut,
    OkOut,
    SystemParamListItemOut,
    SystemParamUpsertIn,
)
from app.modules.system.service import (
    build_config_readiness,
    list_system_params,
    mask_secret_param_value,
)
from app.modules.system.service import (
    upsert_system_param as upsert_system_param_service,
)

router = APIRouter()


@router.get("/system/params", summary="List system parameters")
def get_system_params(
    _perm: None = Depends(require_perm("SystemParam.Read")),
    db: Session = Depends(get_db),
) -> list[SystemParamListItemOut]:
    """
    List system parameters (secrets are masked).

    **Auth**: Bearer JWT
    **Permission**: SystemParam.Read
    **Request example**:
    `GET /api/v1/system/params`
    **Curl example**:
    ```bash
    curl -s -X GET http://localhost:8000/api/v1/system/params \\
      -H "Authorization: Bearer $FPMS_TOKEN"
    ```
    **Responses**:
    - 200: List of system params
    - 401: AUTH_REQUIRED
    - 403: FORBIDDEN
    - 422: VALIDATION_ERROR
    """
    params = list_system_params(db)
    return [
        SystemParamListItemOut(
            param_key=param.param_key,
            param_value=mask_secret_param_value(param),
            value_type=param.value_type,
            description=param.description,
            is_secret=param.is_secret,
            updated_at=param.updated_at,
            created_at=param.created_at,
        )
        for param in params
    ]


@router.get(
    "/system/config-readiness",
    response_model=ConfigReadinessOut,
    summary="Audit system configuration readiness",
)
def get_config_readiness(
    _perm: None = Depends(require_perm("SystemParam.Read")),
    db: Session = Depends(get_db),
) -> ConfigReadinessOut:
    """
    Read-only audit for seed/config readiness.

    **Auth**: Bearer JWT
    **Permission**: SystemParam.Read
    **Request example**:
    `GET /api/v1/system/config-readiness`
    **Responses**:
    - 200: Current config readiness counts and missing hard blockers
    - 401: AUTH_REQUIRED
    - 403: FORBIDDEN
    """
    return ConfigReadinessOut.model_validate(build_config_readiness(db))


@router.put(
    "/system/params/{param_key}",
    response_model=OkOut,
    summary="Upsert a system parameter",
)
def upsert_system_param(
    param_key: str,
    payload: SystemParamUpsertIn,
    _perm: None = Depends(require_perm("SystemParam.Edit")),
    current_user: T_User = current_user_dep,
    db: Session = Depends(get_db),
) -> OkOut:
    """
    Create or update a system parameter by key.

    **Auth**: Bearer JWT
    **Permission**: SystemParam.Edit
    **Request example**:
    ```json
    {"param_value": "templates/bill.docx", "value_type": "string", "is_secret": false}
    ```
    **Curl example**:
    ```bash
    curl -s -X PUT http://localhost:8000/api/v1/system/params/bill_template_path \\
      -H "Authorization: Bearer $FPMS_TOKEN" \\
      -H "Content-Type: application/json" \\
      -d '{"param_value":"templates/bill.docx","value_type":"string","is_secret":false}'
    ```
    **Responses**:
    - 200: Parameter upserted
    - 401: AUTH_REQUIRED
    - 403: FORBIDDEN
    - 422: VALIDATION_ERROR
    """
    upsert_system_param_service(
        db,
        param_key=param_key,
        data=payload,
        actor_id=current_user.id,
    )
    return OkOut()
