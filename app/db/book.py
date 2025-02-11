from sqlalchemy import Column, Date, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from base import Base


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    google_books_id = Column(String(50), unique=True, nullable=False)
    title = Column(String(255), nullable=False)
    subtitle = Column(String(255), nullable=True)
    author_id = Column(Integer, ForeignKey("authors.id"), nullable=False)
    publisher_id = Column(Integer, ForeignKey("publishers.id"), nullable=True)
    published_date = Column(Date, nullable=True)
    description = Column(Text, nullable=True)
    page_count = Column(Integer, nullable=True)
    average_rating = Column(Float, nullable=True)
    ratings_count = Column(Integer, nullable=True)
    isbn_10 = Column(String(20), nullable=True)
    isbn_13 = Column(String(20), nullable=True)
    cover_image = Column(String(255), nullable=True)
    preview_link = Column(String(255), nullable=True)
    language = Column(String(10), nullable=True)

    author = relationship("Author", back_populates="books")
    publisher = relationship("Publisher", back_populates="books")
