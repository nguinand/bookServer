from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from base import Base


class Author(Base):
    __tablename__ = "authors"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), unique=True, nullable=False)
    bio = Column(Text, nullable=True)
    google_books_id = Column(String(50), unique=True, nullable=True)

    books = relationship("Book", back_populates="author")
