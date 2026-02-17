from typing import List

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.crud.model_conversions import convert_book_to_model
from app.crud.shared_queries import get_book_by_book_id
from app.db.db_conn import db_manager
from app.db.db_models import Book, Bookcase
from app.models.bookcase import BookcaseModel


def create_bookcase(bookcase_model: BookcaseModel, session: Session) -> Bookcase:
    bookcase_data = Bookcase(
        id=bookcase_model.id,
        name=bookcase_model.name,
        created_at=bookcase_model.created_at,
        user_id=bookcase_model.user_id,
    )

    if bookcase_model.books:
        for book_model in bookcase_model.books:
            book = session.get(Book, book_model.book_id)
            if book:
                bookcase_data.books.append(book)

    session.add(bookcase_data)
    db_manager.commit_or_raise(session)
    session.refresh(bookcase_data)
    return bookcase_data


def get_bookcase_by_id(bookcase_id: int, session: Session) -> None | Bookcase:
    return session.get(Bookcase, bookcase_id)


def get_bookcases_by_user_id(
    user_id: int, session: Session, limit: int = 100, offset: int = 0
) -> List[Bookcase]:
    # A user can have multiple bookshelves. So there may be multiple entries with the same user_id
    stmt = (
        select(Bookcase)
        .where(Bookcase.user_id == user_id)
        .order_by(Bookcase.id)
        .limit(limit)
        .offset(offset)
    )
    return session.scalars(stmt).all()


def update_bookcase(
    bookcase_replacement: BookcaseModel, session: Session
) -> None | Bookcase:
    if bookcase_replacement.id is None:
        raise ValueError("bookcase_replacement must have an id")

    bookcase_record = get_bookcase_by_id(bookcase_replacement.id, session)
    if not bookcase_record:
        return None

    bookcase_record.name = bookcase_replacement.name
    bookcase_record.created_at = bookcase_replacement.created_at
    bookcase_record.user_id = bookcase_replacement.user_id

    # Handle books update (only if books are provided in the model)
    if bookcase_replacement.books is not None:
        bookcase_record.books.clear()

        for book_model in bookcase_replacement.books:
            book = get_book_by_book_id(book_id=book_model.book_id, session=session)
            book = session.get(Book, book_model.book_id)
            if book:
                bookcase_record.books.append(book)

    db_manager.commit_or_raise(session)
    session.refresh(bookcase_record)
    return bookcase_record


def delete_bookcase_by_id(bookcase_id: int, session: Session) -> bool:
    bookcase_info = get_bookcase_by_id(bookcase_id, session)
    if not bookcase_info:
        return False

    session.delete(bookcase_info)
    db_manager.commit_or_raise(session)
    return True


def convert_bookcase(bookcase_data: Bookcase) -> BookcaseModel:
    return BookcaseModel(
        id=bookcase_data.id,
        user_id=bookcase_data.user_id,
        name=bookcase_data.name,
        created_at=bookcase_data.created_at,
        books=[convert_book_to_model(book) for book in bookcase_data.books],
    )
