from datetime import datetime
from typing import Optional
from sqlalchemy import Integer, String, ForeignKey, TIMESTAMP, func
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.db.db_models.base import Base


class Bookcase(Base):
    __tablename__ = "bookcases"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP, server_default=func.current_timestamp()
    )

    # This is the owner
    # JUST TO MAKE SURE: A BOOKCASE is attached to a USER. When a USER is DELETED, that BOOKCASE also is deleted.
    # The USER themself does not have knowledge of the BOOKCASE in the USER table.
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    # A bookcase can contain multiple books N:N
    # A book can belong to multiple bookcases
    books = relationship("Book", secondary="bookcase_books", back_populates="bookcases")
