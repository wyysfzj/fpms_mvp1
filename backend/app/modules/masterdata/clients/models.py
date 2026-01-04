from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, func, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Client(Base):
    __tablename__ = "t_client"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    client_code: Mapped[str | None] = mapped_column(String(64), unique=True, nullable=True)
    name_cn: Mapped[str] = mapped_column(String(256), nullable=False)
    name_en: Mapped[str | None] = mapped_column(String(256), nullable=True)
    client_type: Mapped[str] = mapped_column(
        String(32), nullable=False, server_default=text("'CLIENT'")
    )
    default_currency: Mapped[str] = mapped_column(
        String(8), nullable=False, server_default=text("'CNY'")
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("1"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=func.current_timestamp()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )
