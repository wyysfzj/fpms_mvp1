from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import AuditMixin, UUIDPrimaryKeyMixin


class Client(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "t_client"

    client_code: Mapped[str | None] = mapped_column(String(64), unique=True, nullable=True)
    name_cn: Mapped[str] = mapped_column(String(256), nullable=False)
    name_en: Mapped[str | None] = mapped_column(String(256), nullable=True)
    email: Mapped[str | None] = mapped_column(String(254), nullable=True)
    client_type: Mapped[str] = mapped_column(
        String(32), nullable=False, server_default=text("'CLIENT'")
    )
    default_currency: Mapped[str] = mapped_column(
        String(8), nullable=False, server_default=text("'CNY'")
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("1"))


class ClientAddress(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "t_client_address"

    client_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("t_client.id", ondelete="CASCADE"), nullable=False
    )
    address_type: Mapped[str] = mapped_column(
        String(16), nullable=False, server_default=text("'GENERAL'")
    )
    address_line1: Mapped[str | None] = mapped_column(Text, nullable=True)
    address_line2: Mapped[str | None] = mapped_column(Text, nullable=True)
    city: Mapped[str | None] = mapped_column(String(128), nullable=True)
    province: Mapped[str | None] = mapped_column(String(128), nullable=True)
    postal_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    country_code: Mapped[str | None] = mapped_column(
        String(10), nullable=True, server_default=text("'CN'")
    )
    is_default: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("0"))


class ClientContact(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "t_client_contact"

    client_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("t_client.id", ondelete="CASCADE"), nullable=False
    )
    contact_name: Mapped[str] = mapped_column(String(200), nullable=False)
    title: Mapped[str | None] = mapped_column(String(100), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    mobile: Mapped[str | None] = mapped_column(String(50), nullable=True)
    email: Mapped[str | None] = mapped_column(String(254), nullable=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("0"))
