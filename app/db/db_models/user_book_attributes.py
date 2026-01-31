from datetime import datetime
from typing import Optional
from sqlalchemy import Integer, ForeignKey, Text, TIMESTAMP, UniqueConstraint, func
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.db.db_models.base import Base


# Linking table
class UserBookAttributes(Base):
    __tablename__ = "user_book_attributes"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, autoincrement=True
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    book_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("books.book_id", ondelete="CASCADE"), nullable=False
    )
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    review_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP, server_default=func.current_timestamp()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )

    # A user can rate multiple books
    # A book can be rated by multiple users
    # 1:N
    user = relationship("User", back_populates="ratings")
    book = relationship("Book", back_populates="ratings")

    # Each user can only rate that one book.
    __table_args__ = (UniqueConstraint("user_id", "book_id", name="unique_user_book"),)
