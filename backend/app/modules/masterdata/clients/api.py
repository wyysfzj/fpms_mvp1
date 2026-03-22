from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import current_user_dep, require_perm
from app.db.session import get_db
from app.modules.auth.models import T_User
from app.modules.masterdata.clients.schemas import (
    ClientAddressCreateIn,
    ClientAddressOut,
    ClientAddressUpdateIn,
    ClientContactCreateIn,
    ClientContactOut,
    ClientContactUpdateIn,
    ClientCreateIn,
    ClientListItemOut,
    ClientOut,
    ClientUpdateIn,
    OkOut,
)
from app.modules.masterdata.clients.service import create_client as create_client_service
from app.modules.masterdata.clients.service import (
    create_client_address,
    create_client_contact,
    delete_client_address,
    delete_client_contact,
    list_client_addresses,
    list_client_contacts,
    list_clients,
    update_client_address,
    update_client_contact,
)
from app.modules.masterdata.clients.service import deactivate_client as deactivate_client_service
from app.modules.masterdata.clients.service import (
    get_client as get_client_service,
)
from app.modules.masterdata.clients.service import update_client as update_client_service

router = APIRouter()


@router.get("/clients", summary="List clients")
def get_clients(
    q: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1),
    is_active: bool | None = Query(default=None),
    _perm: None = Depends(require_perm("Client.Read")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """
    List clients with filters and pagination.

    **Auth**: Bearer JWT
    **Permission**: Client.Read
    **Request example**:
    `GET /api/v1/clients?page=1&page_size=20&q=Acme`
    **Curl example**:
    ```bash
    curl -s -X GET "http://localhost:8000/api/v1/clients?page=1&page_size=20" \\
      -H "Authorization: Bearer $FPMS_TOKEN"
    ```
    **Responses**:
    - 200: List of clients
    - 401: AUTH_REQUIRED
    - 403: FORBIDDEN
    - 422: VALIDATION_ERROR
    """
    clients, total = list_clients(
        db,
        q=q,
        is_active=is_active,
        page=page,
        page_size=page_size,
    )
    items = [ClientListItemOut.model_validate(client) for client in clients]
    return {"items": items, "page": page, "page_size": page_size, "total": total}


@router.get("/clients/{client_id}", response_model=ClientOut, summary="Get a client")
def get_client(
    client_id: str,
    _perm: None = Depends(require_perm("Client.Read")),
    db: Session = Depends(get_db),
) -> ClientOut:
    """
    Get a client by ID.

    **Auth**: Bearer JWT
    **Permission**: Client.Read
    **Request example**:
    `GET /api/v1/clients/CLIENT_ID`
    **Curl example**:
    ```bash
    curl -s -X GET http://localhost:8000/api/v1/clients/CLIENT_ID \\
      -H "Authorization: Bearer $FPMS_TOKEN"
    ```
    **Responses**:
    - 200: Client details
    - 401: AUTH_REQUIRED
    - 403: FORBIDDEN
    - 404: Client not found
    - 422: VALIDATION_ERROR
    """
    client = get_client_service(db, client_id=client_id)
    return ClientOut.model_validate(client)


@router.post(
    "/clients",
    status_code=status.HTTP_201_CREATED,
    response_model=ClientOut,
    summary="Create a client",
)
def create_client(
    payload: ClientCreateIn,
    _perm: None = Depends(require_perm("Client.Create")),
    current_user: T_User = current_user_dep,
    db: Session = Depends(get_db),
) -> ClientOut:
    """
    Create a client.

    **Auth**: Bearer JWT
    **Permission**: Client.Create
    **Request example**:
    ```json
    {"client_code": "CURL_C001", "name_cn": "CURL Client CN", "default_currency": "CNY"}
    ```
    **Curl example**:
    ```bash
    curl -s -X POST http://localhost:8000/api/v1/clients \\
      -H "Authorization: Bearer $FPMS_TOKEN" \\
      -H "Content-Type: application/json" \\
      -d '{"client_code":"CURL_C001","name_cn":"CURL Client CN","default_currency":"CNY"}'
    ```
    **Responses**:
    - 201: Client created
    - 400: Client code already exists
    - 401: AUTH_REQUIRED
    - 403: FORBIDDEN
    - 422: VALIDATION_ERROR
    """
    client = create_client_service(db, data=payload, actor_id=current_user.id)
    return ClientOut.model_validate(client)


@router.put(
    "/clients/{client_id}/deactivate",
    response_model=OkOut,
    summary="Deactivate a client",
)
def deactivate_client(
    client_id: str,
    _perm: None = Depends(require_perm("Client.Action")),
    current_user: T_User = current_user_dep,
    db: Session = Depends(get_db),
) -> OkOut:
    """
    Deactivate a client.

    **Auth**: Bearer JWT
    **Permission**: Client.Action
    **Request example**:
    `PUT /api/v1/clients/CLIENT_ID/deactivate`
    **Curl example**:
    ```bash
    curl -s -X PUT http://localhost:8000/api/v1/clients/CLIENT_ID/deactivate \\
      -H "Authorization: Bearer $FPMS_TOKEN"
    ```
    **Responses**:
    - 200: Client deactivated
    - 401: AUTH_REQUIRED
    - 403: FORBIDDEN
    - 404: Client not found
    - 422: VALIDATION_ERROR
    """
    deactivate_client_service(db, client_id=client_id, actor_id=current_user.id)
    return OkOut()


@router.put("/clients/{client_id}", response_model=ClientOut, summary="Update a client")
def update_client(
    client_id: str,
    payload: ClientUpdateIn,
    _perm: None = Depends(require_perm("Client.Edit")),
    current_user: T_User = current_user_dep,
    db: Session = Depends(get_db),
) -> ClientOut:
    """
    Update a client.

    **Auth**: Bearer JWT
    **Permission**: Client.Edit
    **Request example**:
    ```json
    {"name_cn": "Updated Client CN", "is_active": true}
    ```
    **Curl example**:
    ```bash
    curl -s -X PUT http://localhost:8000/api/v1/clients/CLIENT_ID \\
      -H "Authorization: Bearer $FPMS_TOKEN" \\
      -H "Content-Type: application/json" \\
      -d '{"name_cn":"Updated Client CN","is_active":true}'
    ```
    **Responses**:
    - 200: Client updated
    - 400: Client code already exists
    - 401: AUTH_REQUIRED
    - 403: FORBIDDEN
    - 404: Client not found
    - 422: VALIDATION_ERROR
    """
    client = update_client_service(db, client_id=client_id, data=payload, actor_id=current_user.id)
    return ClientOut.model_validate(client)


# ── Address endpoints ─────────────────────────────────────


@router.get(
    "/clients/{client_id}/addresses",
    response_model=list[ClientAddressOut],
    summary="List client addresses",
)
def get_client_addresses(
    client_id: str,
    _perm: None = Depends(require_perm("Client.Read")),
    db: Session = Depends(get_db),
) -> list[ClientAddressOut]:
    items = list_client_addresses(db, client_id=client_id)
    return [ClientAddressOut.model_validate(a) for a in items]


@router.post(
    "/clients/{client_id}/addresses",
    status_code=status.HTTP_201_CREATED,
    response_model=ClientAddressOut,
    summary="Create client address",
)
def create_address(
    client_id: str,
    payload: ClientAddressCreateIn,
    _perm: None = Depends(require_perm("Client.Edit")),
    current_user: T_User = current_user_dep,
    db: Session = Depends(get_db),
) -> ClientAddressOut:
    addr = create_client_address(db, client_id=client_id, data=payload, actor_id=current_user.id)
    return ClientAddressOut.model_validate(addr)


@router.put(
    "/clients/{client_id}/addresses/{address_id}",
    response_model=ClientAddressOut,
    summary="Update client address",
)
def update_address(
    client_id: str,
    address_id: str,
    payload: ClientAddressUpdateIn,
    _perm: None = Depends(require_perm("Client.Edit")),
    current_user: T_User = current_user_dep,
    db: Session = Depends(get_db),
) -> ClientAddressOut:
    addr = update_client_address(
        db, client_id=client_id, address_id=address_id, data=payload, actor_id=current_user.id
    )
    return ClientAddressOut.model_validate(addr)


@router.delete(
    "/clients/{client_id}/addresses/{address_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
    summary="Delete client address",
)
def delete_address(
    client_id: str,
    address_id: str,
    _perm: None = Depends(require_perm("Client.Edit")),
    current_user: T_User = current_user_dep,
    db: Session = Depends(get_db),
) -> None:
    delete_client_address(db, client_id=client_id, address_id=address_id, actor_id=current_user.id)


# ── Contact endpoints ─────────────────────────────────────


@router.get(
    "/clients/{client_id}/contacts",
    response_model=list[ClientContactOut],
    summary="List client contacts",
)
def get_client_contacts(
    client_id: str,
    _perm: None = Depends(require_perm("Client.Read")),
    db: Session = Depends(get_db),
) -> list[ClientContactOut]:
    items = list_client_contacts(db, client_id=client_id)
    return [ClientContactOut.model_validate(c) for c in items]


@router.post(
    "/clients/{client_id}/contacts",
    status_code=status.HTTP_201_CREATED,
    response_model=ClientContactOut,
    summary="Create client contact",
)
def create_contact(
    client_id: str,
    payload: ClientContactCreateIn,
    _perm: None = Depends(require_perm("Client.Edit")),
    current_user: T_User = current_user_dep,
    db: Session = Depends(get_db),
) -> ClientContactOut:
    contact = create_client_contact(db, client_id=client_id, data=payload, actor_id=current_user.id)
    return ClientContactOut.model_validate(contact)


@router.put(
    "/clients/{client_id}/contacts/{contact_id}",
    response_model=ClientContactOut,
    summary="Update client contact",
)
def update_contact_endpoint(
    client_id: str,
    contact_id: str,
    payload: ClientContactUpdateIn,
    _perm: None = Depends(require_perm("Client.Edit")),
    current_user: T_User = current_user_dep,
    db: Session = Depends(get_db),
) -> ClientContactOut:
    contact = update_client_contact(
        db, client_id=client_id, contact_id=contact_id, data=payload, actor_id=current_user.id
    )
    return ClientContactOut.model_validate(contact)


@router.delete(
    "/clients/{client_id}/contacts/{contact_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
    summary="Delete client contact",
)
def delete_contact_endpoint(
    client_id: str,
    contact_id: str,
    _perm: None = Depends(require_perm("Client.Edit")),
    current_user: T_User = current_user_dep,
    db: Session = Depends(get_db),
) -> None:
    delete_client_contact(db, client_id=client_id, contact_id=contact_id, actor_id=current_user.id)
