from __future__ import annotations

from sqlalchemy import Boolean, String, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import UUIDPrimaryKeyMixin


class Applicant(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "t_applicant"

    code: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    name_cn: Mapped[str] = mapped_column(String(256), nullable=False)
    name_en: Mapped[str | None] = mapped_column(String(256), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("1"))

    __table_args__ = (UniqueConstraint("name_cn", name="uq_applicant_name_cn"),)
