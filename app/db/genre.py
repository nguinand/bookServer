from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.base import Base


class Genre(Base):
    __tablename__ = "genres"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)

    # A Book can belong to multiple genres.
    # A genre can be associated with multiple books.
    # N:N
    books = relationship("Book", secondary="book_genres", back_populates="genres")
