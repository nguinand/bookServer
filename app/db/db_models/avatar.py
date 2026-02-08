from typing import Optional

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.db_models.base import Base


class Avatar(Base):
    __tablename__ = "avatars"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, autoincrement=True
    )
    image_url: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Establish reverse relationship (if you want to access users from avatar)
    users = relationship("User", back_populates="avatar")
