from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from base import Base
from book_authors import book_authors  # Import the association table

class Author(Base):
    __tablename__ = "authors"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    google_books_id = Column(String(50), unique=True, nullable=True)  # Keep for API lookups
    name = Column(String(255), unique=True, nullable=False)
    bio = Column(Text, nullable=True)

    # An author can write multiple books. N:N
    books = relationship("Book", secondary=book_authors, back_populates="authors")
