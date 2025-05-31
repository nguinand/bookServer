from typing import List
from sqlalchemy.orm import Session

from app.db.db_models.book import Book


def get_books_by_title(name: str, session: Session) -> List[Book]:
    return session.query(Book).filter_by(title=name).all()


def get_books_by_google_id(google_id: str, session: Session) -> Book:
    return session.query(Book).filter_by(google_id=google_id).first()


def get_book_by_id(id: int, session: Session) -> Book:
    return session.query(Book).filter_by(id=id).first()
