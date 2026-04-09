from __future__ import annotations

from sqlalchemy import Boolean, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import AuditMixin, UUIDPrimaryKeyMixin


class Department(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "t_department"

    department_code: Mapped[str] = mapped_column(
        String(64), unique=True, index=True, nullable=False
    )
    name_cn: Mapped[str] = mapped_column(String(128), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("1"))
