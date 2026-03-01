from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, String, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import AuditMixin, UUIDPrimaryKeyMixin


class T_User(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "t_user"

    username: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("1"))

    user_roles: Mapped[list["T_UserRole"]] = relationship(
        "T_UserRole",
        back_populates="user",
        cascade="all, delete-orphan",
    )


class T_Role(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "t_role"

    code: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)

    user_roles: Mapped[list["T_UserRole"]] = relationship(
        "T_UserRole",
        back_populates="role",
        cascade="all, delete-orphan",
    )


class T_RolePerm(UUIDPrimaryKeyMixin, AuditMixin, Base):
    """Maps permissions to roles."""

    __tablename__ = "t_role_perm"

    role_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("t_role.id", ondelete="CASCADE"),
        index=True,
    )
    perm_code: Mapped[str] = mapped_column(String(128), nullable=False, index=True)

    __table_args__ = (UniqueConstraint("role_id", "perm_code", name="uq_role_perm"),)


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
