from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class User(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "users"

    mobile_e164: Mapped[str] = mapped_column(String(16), unique=True, index=True, nullable=False)
    preferred_language: Mapped[str] = mapped_column(String(10), default="en", nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE", nullable=False)

    roles: Mapped[list["UserRole"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class UserRole(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "user_roles"
    __table_args__ = (UniqueConstraint("user_id", "role", name="uq_user_role"),)

    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    user: Mapped[User] = relationship(back_populates="roles")


class OTPChallenge(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "otp_challenges"

    mobile_e164: Mapped[str] = mapped_column(String(16), index=True, nullable=False)
    purpose: Mapped[str] = mapped_column(String(30), default="LOGIN", nullable=False)
    otp_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    attempts: Mapped[int] = mapped_column(default=0, nullable=False)
    consumed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class RefreshSession(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "refresh_sessions"

    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    token_jti: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    device_label: Mapped[str | None] = mapped_column(String(120))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
