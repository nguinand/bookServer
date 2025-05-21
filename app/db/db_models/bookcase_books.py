from sqlalchemy import Table, Column, ForeignKey, Integer, TIMESTAMP, func
from app.db.db_models.base import Base

bookcase_books = Table(
    "bookcase_books",
    Base.metadata,
    Column(
        "bookcase_id",
        Integer,
        ForeignKey("bookcases.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "book_id", Integer, ForeignKey("books.id", ondelete="CASCADE"), primary_key=True
    ),
    Column("added_at", TIMESTAMP, server_default=func.current_timestamp()),
)
