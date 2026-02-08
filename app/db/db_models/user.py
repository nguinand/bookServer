from datetime import datetime
from typing import Optional

from sqlalchemy import TIMESTAMP, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.db_models.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, autoincrement=True
    )
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="user")
    avatar_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("avatars.id"), nullable=True
    )
    status_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("user_status.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.current_timestamp()
    )
    last_login: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP, nullable=True)

    # A user can have multiple bookcases 1:N
    bookcases = relationship(
        "Bookcase",
        backref=None,
        cascade="all, delete-orphan",
        passive_deletes=True,  # <— required for ON DELETE CASCADE to work properly
        lazy="selectin",
    )

    # A user can rate multiple books 1:N
    ratings = relationship(
        "UserBookAttributes", back_populates="user", cascade="all, delete-orphan"
    )
    status = relationship("UserStatus", back_populates="users")

    avatar = relationship("Avatar", back_populates="users")

    book_states = relationship(
        "UserBookState", back_populates="user", cascade="all, delete-orphan"
    )
