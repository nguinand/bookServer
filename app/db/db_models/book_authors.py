from sqlalchemy import Column, ForeignKey, Integer, Table

from app.db.db_models.base import Base

book_authors = Table(
    "book_authors",
    Base.metadata,
    Column(
        "book_id",
        Integer,
        ForeignKey("books.book_id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "author_id",
        Integer,
        ForeignKey("authors.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)
