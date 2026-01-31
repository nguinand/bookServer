from sqlalchemy import Column, Integer, ForeignKey, Table

from app.db.db_models.base import Base

# Association table to many-many relationship. Between a Genre and a Book.
# A book can have multiple Genres.
# A Genre can have multiple Books.
book_genres = Table(
    "book_genres",
    Base.metadata,
    Column(
        "book_id", Integer, ForeignKey("books.book_id", ondelete="CASCADE"), primary_key=True
    ),
    Column(
        "genre_id",
        Integer,
        ForeignKey("genres.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)
