from __future__ import annotations

from uuid import uuid4

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.core.errors import raise_business_error
from app.modules.masterdata.clients.models import Client, ClientAddress, ClientContact
from app.modules.masterdata.clients.schemas import (
    ClientAddressCreateIn,
    ClientAddressUpdateIn,
    ClientContactCreateIn,
    ClientContactUpdateIn,
    ClientCreateIn,
    ClientUpdateIn,
)


def list_clients(
    db: Session,
    *,
    q: str | None,
    is_active: bool | None,
    page: int,
    page_size: int,
) -> tuple[list[Client], int]:
    stmt = select(Client)

    if q:
        needle = f"%{q.lower()}%"
        stmt = stmt.where(
            or_(
                func.lower(Client.client_code).like(needle),
                func.lower(Client.name_cn).like(needle),
                func.lower(Client.name_en).like(needle),
            )
        )

    if is_active is not None:
        stmt = stmt.where(Client.is_active == is_active)

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = db.execute(count_stmt).scalar_one()

    offset = (page - 1) * page_size
    stmt = (
        stmt.order_by(Client.updated_at.desc(), Client.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    items = db.execute(stmt).scalars().all()
    return items, total


def get_client(db: Session, *, client_id: str) -> Client:
    client = db.execute(select(Client).where(Client.id == client_id)).scalar_one_or_none()
    if not client:
        raise_business_error("CLIENT_NOT_FOUND", "Client not found", status_code=404)
    return client


def assert_client_code_unique(
    db: Session,
    *,
    client_code: str,
    exclude_client_id: str | None = None,
) -> None:
    stmt = select(Client).where(Client.client_code == client_code)
    if exclude_client_id:
        stmt = stmt.where(Client.id != exclude_client_id)
    existing = db.execute(stmt).scalar_one_or_none()
    if existing:
        raise_business_error(
            "CLIENT_CODE_DUPLICATE",
            "Client code already exists",
            status_code=400,
        )


def create_client(db: Session, *, data: ClientCreateIn, actor_id: str | None) -> Client:
    if data.client_code:
        assert_client_code_unique(db, client_code=data.client_code)

    client = Client(
        id=str(uuid4()),
        client_code=data.client_code,
        name_cn=data.name_cn,
        name_en=data.name_en,
        email=data.email,
        client_type=data.client_type,
        default_currency=data.default_currency,
        is_active=data.is_active,
    )
    db.add(client)
    db.commit()
    db.refresh(client)
    return client


def update_client(
    db: Session,
    *,
    client_id: str,
    data: ClientUpdateIn,
    actor_id: str | None,
) -> Client:
    client = get_client(db, client_id=client_id)
    updates = data.model_dump(exclude_unset=True)

    if "client_code" in updates and updates["client_code"]:
        assert_client_code_unique(
            db,
            client_code=updates["client_code"],
            exclude_client_id=client_id,
        )

    for field, value in updates.items():
        setattr(client, field, value)

    db.commit()
    db.refresh(client)
    return client


def deactivate_client(db: Session, *, client_id: str, actor_id: str | None) -> None:
    client = get_client(db, client_id=client_id)
    if client.is_active:
        client.is_active = False
        db.commit()


# ── Address CRUD ──────────────────────────────────────────


def list_client_addresses(db: Session, *, client_id: str) -> list[ClientAddress]:
    get_client(db, client_id=client_id)
    stmt = select(ClientAddress).where(ClientAddress.client_id == client_id)
    return list(db.execute(stmt).scalars().all())


def create_client_address(
    db: Session, *, client_id: str, data: ClientAddressCreateIn, actor_id: str | None
) -> ClientAddress:
    get_client(db, client_id=client_id)
    addr = ClientAddress(
        id=str(uuid4()),
        client_id=client_id,
        **data.model_dump(),
    )
    if actor_id:
        addr.created_by = actor_id
        addr.updated_by = actor_id
    db.add(addr)
    db.commit()
    db.refresh(addr)
    return addr


def update_client_address(
    db: Session,
    *,
    client_id: str,
    address_id: str,
    data: ClientAddressUpdateIn,
    actor_id: str | None,
) -> ClientAddress:
    get_client(db, client_id=client_id)
    addr = db.execute(
        select(ClientAddress).where(
            ClientAddress.id == address_id, ClientAddress.client_id == client_id
        )
    ).scalar_one_or_none()
    if not addr:
        raise_business_error("ADDRESS_NOT_FOUND", "Address not found", status_code=404)
    updates = data.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(addr, field, value)
    if actor_id:
        addr.updated_by = actor_id
    db.commit()
    db.refresh(addr)
    return addr


def delete_client_address(
    db: Session, *, client_id: str, address_id: str, actor_id: str | None
) -> None:
    get_client(db, client_id=client_id)
    addr = db.execute(
        select(ClientAddress).where(
            ClientAddress.id == address_id, ClientAddress.client_id == client_id
        )
    ).scalar_one_or_none()
    if not addr:
        raise_business_error("ADDRESS_NOT_FOUND", "Address not found", status_code=404)
    db.delete(addr)
    db.commit()


# ── Contact CRUD ──────────────────────────────────────────


def list_client_contacts(db: Session, *, client_id: str) -> list[ClientContact]:
    get_client(db, client_id=client_id)
    stmt = select(ClientContact).where(ClientContact.client_id == client_id)
    return list(db.execute(stmt).scalars().all())


def create_client_contact(
    db: Session, *, client_id: str, data: ClientContactCreateIn, actor_id: str | None
) -> ClientContact:
    get_client(db, client_id=client_id)
    contact = ClientContact(
        id=str(uuid4()),
        client_id=client_id,
        **data.model_dump(),
    )
    if actor_id:
        contact.created_by = actor_id
        contact.updated_by = actor_id
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


def update_client_contact(
    db: Session,
    *,
    client_id: str,
    contact_id: str,
    data: ClientContactUpdateIn,
    actor_id: str | None,
) -> ClientContact:
    get_client(db, client_id=client_id)
    contact = db.execute(
        select(ClientContact).where(
            ClientContact.id == contact_id, ClientContact.client_id == client_id
        )
    ).scalar_one_or_none()
    if not contact:
        raise_business_error("CONTACT_NOT_FOUND", "Contact not found", status_code=404)
    updates = data.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(contact, field, value)
    if actor_id:
        contact.updated_by = actor_id
    db.commit()
    db.refresh(contact)
    return contact


def delete_client_contact(
    db: Session, *, client_id: str, contact_id: str, actor_id: str | None
) -> None:
    get_client(db, client_id=client_id)
    contact = db.execute(
        select(ClientContact).where(
            ClientContact.id == contact_id, ClientContact.client_id == client_id
        )
    ).scalar_one_or_none()
    if not contact:
        raise_business_error("CONTACT_NOT_FOUND", "Contact not found", status_code=404)
    db.delete(contact)
    db.commit()
