# This file was created to avoid circular imports.
# Some queries are shared between crud operations.
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.db_conn import DatabaseOperationError
from app.db.db_models.book import Book


def get_book_by_book_id(book_id: int, session: Session) -> None | Book:
    try:
        return session.get(Book, book_id)
    except SQLAlchemyError as e:
        raise DatabaseOperationError(e) from e
