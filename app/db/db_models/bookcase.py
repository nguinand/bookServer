from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from base import Base


class Bookcase(Base):
    __tablename__ = "bookcases"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP, server_default="CURRENT_TIMESTAMP")

    # A user can have multiple bookcases 1:N
    user = relationship("User", back_populates="bookcases")
    # A bookcase can contain multiple books N:N
    # A book can belong to multiple bookcases
    books = relationship("Book", secondary="bookcase_books", back_populates="bookcases")
