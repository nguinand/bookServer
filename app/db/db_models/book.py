from sqlalchemy import Column, Date, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from app.db.db_models.base import Base


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    google_books_id = Column(String(50), unique=True, nullable=False)
    title = Column(String(255), nullable=False)
    subtitle = Column(String(255), nullable=True)
    publisher_id = Column(Integer, ForeignKey("publishers.id"), nullable=True)
    published_date = Column(Date, nullable=True)
    description = Column(Text, nullable=True)
    page_count = Column(Integer, nullable=True)
    average_rating = Column(Float, nullable=True)
    ratings_count = Column(Integer, nullable=True)
    cover_image = Column(String(255), nullable=True)
    preview_link = Column(String(255), nullable=True)
    info_link = Column(String(255), nullable=True)
    language = Column(String(10), nullable=True)

    publisher = relationship("Publisher", back_populates="books")
    # A book can have multiple authors. N:N
    authors = relationship("Author", secondary="book_authors", back_populates="books")
    sale_info = relationship("BookSale", back_populates="book", uselist=False)
    access_info = relationship("BookAccess", back_populates="book", uselist=False)
    identifiers = relationship("BookIdentifier", back_populates="book")
    genres = relationship("Genre", secondary="book_genres", back_populates="books")
    ratings = relationship("UserBookAttributes", back_populates="book")

    bookcases = relationship(
        "Bookcase", secondary="bookcase_books", back_populates="books"
    )
