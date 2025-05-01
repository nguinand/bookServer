from sqlalchemy import Column, Integer, ForeignKey, Text, TIMESTAMP, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.db_models.base import Base


# Linking table
class UserBookAttributes(Base):
    __tablename__ = "user_book_attributes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    book_id = Column(
        Integer, ForeignKey("books.id", ondelete="CASCADE"), nullable=False
    )
    rating = Column(Integer, nullable=False)
    review_text = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, server_default="CURRENT_TIMESTAMP")
    updated_at = Column(
        TIMESTAMP, server_default="CURRENT_TIMESTAMP", onupdate="CURRENT_TIMESTAMP"
    )

    # A user can rate multiple books
    # A book can be rated by multiple users
    # 1:N
    user = relationship("User", back_populates="ratings")
    book = relationship("Book", back_populates="ratings")

    # Each user can only rate that one book.
    __table_args__ = (UniqueConstraint("user_id", "book_id", name="unique_user_book"),)
