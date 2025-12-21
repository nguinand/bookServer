from typing import Optional
from sqlalchemy import Float, Integer, String, Text
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.db.db_models.base import Base


class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, autoincrement=True
    )
    google_books_id: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    subtitle: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    publisher_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    published_date: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    page_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    average_rating: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    ratings_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    cover_image: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    preview_link: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    info_link: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    language: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    maturity_rating: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)

    # A book can have multiple authors. N:N
    authors = relationship("Author", secondary="book_authors", back_populates="books")
    book_sale_info = relationship(
        "BookSaleInfo",
        back_populates="book",
        uselist=False,
        cascade="all, delete-orphan",
    )
    access_info = relationship("BookAccess", back_populates="book", uselist=False)
    identifiers = relationship(
        "BookIdentifier", back_populates="book", cascade="all, delete-orphan"
    )
    genres = relationship("Genre", secondary="book_genres", back_populates="books")
    ratings = relationship(
        "UserBookAttributes", back_populates="book", cascade="all, delete-orphan"
    )

    bookcases = relationship(
        "Bookcase", secondary="bookcase_books", back_populates="books"
    )

    user_states = relationship(
        "UserBookState",
        back_populates="book",
        cascade="all, delete-orphan",
    )
