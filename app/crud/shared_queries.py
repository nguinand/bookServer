# This file was created to avoid circular imports.
# Some queries are shared between crud operations.

from sqlalchemy.orm import Session
from app.db.db_models.book import Book


def get_book_by_book_id(book_id: int, session: Session) -> None | Book:
    return session.query(Book).filter_by(book_id=book_id).first()
