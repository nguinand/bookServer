from typing import Optional
from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.db.db_models.base import Base


class UserStatus(Base):
    __tablename__ = "user_status"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False
    )  # e.g. Bronze, Silver
    level: Mapped[int] = mapped_column(
        Integer, unique=True, nullable=False
    )  # Numeric rank
    benefits: Mapped[Optional[Text]] = mapped_column(
        Text, nullable=True
    )  # Optional description of perks

    # Reverse relationship to User
    users = relationship("User", back_populates="status")
