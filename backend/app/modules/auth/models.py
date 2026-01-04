from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class T_User(Base):
    __tablename__ = "t_user"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("1"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False,
        server_default=func.current_timestamp(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )

    user_roles: Mapped[list["T_UserRole"]] = relationship(
        "T_UserRole",
        back_populates="user",
        cascade="all, delete-orphan",
    )


class T_Role(Base):
    __tablename__ = "t_role"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    code: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)

    user_roles: Mapped[list["T_UserRole"]] = relationship(
        "T_UserRole",
        back_populates="role",
        cascade="all, delete-orphan",
    )


class T_UserRole(Base):
    __tablename__ = "t_user_role"

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("t_user.id", ondelete="CASCADE"),
        primary_key=True,
    )
    role_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("t_role.id", ondelete="CASCADE"),
        primary_key=True,
    )

    user: Mapped["T_User"] = relationship("T_User", back_populates="user_roles")
    role: Mapped["T_Role"] = relationship("T_Role", back_populates="user_roles")
