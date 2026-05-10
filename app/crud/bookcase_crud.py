from typing import List

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.crud.model_conversions import convert_book_to_model
from app.crud.shared_queries import get_book_by_book_id
from app.db.db_conn import db_manager
from app.db.db_models import Book, Bookcase, Genre, book_genres, bookcase_books
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
    return session.scalars(stmt).all()  # type: ignore


def get_most_common_bookcase_genre_by_user_id(
    user_id: int, session: Session
) -> str | None:
    trimmed_genre_name = func.trim(Genre.name)
    stmt = (
        select(trimmed_genre_name)
        .select_from(Bookcase)
        .join(bookcase_books, Bookcase.id == bookcase_books.c.bookcase_id)
        .join(Book, Book.book_id == bookcase_books.c.book_id)
        .join(book_genres, Book.book_id == book_genres.c.book_id)
        .join(Genre, Genre.id == book_genres.c.genre_id)
        .where(Bookcase.user_id == user_id)
        .where(trimmed_genre_name != "")
        .group_by(trimmed_genre_name)
        .order_by(func.count().desc(), trimmed_genre_name.asc())
        .limit(1)
    )
    return session.scalars(stmt).first()


def get_bookcase_google_books_ids_by_user_id(
    user_id: int, session: Session
) -> set[str]:
    stmt = (
        select(Book.google_books_id)
        .select_from(Bookcase)
        .join(bookcase_books, Bookcase.id == bookcase_books.c.bookcase_id)
        .join(Book, Book.book_id == bookcase_books.c.book_id)
        .where(Bookcase.user_id == user_id)
    )
    return set(session.scalars(stmt).all())


def update_bookcase(bookcase_replacement: BookcaseModel, session: Session) -> bool:
    if bookcase_replacement.id is None:
        raise ValueError("bookcase_replacement must have an id")

    bookcase_record = get_bookcase_by_id(bookcase_replacement.id, session)
    if not bookcase_record:
        return False

    bookcase_record.name = bookcase_replacement.name
    bookcase_record.created_at = bookcase_replacement.created_at
    bookcase_record.user_id = bookcase_replacement.user_id

    # Handle books update (only if books are provided in the model)
    if bookcase_replacement.books is not None:
        bookcase_record.books.clear()

        for book_model in bookcase_replacement.books:
            if book_model.book_id:
                book = get_book_by_book_id(book_id=book_model.book_id, session=session)
                book = session.get(Book, book_model.book_id)
                if book:
                    bookcase_record.books.append(book)

    db_manager.commit_or_raise(session)
    session.refresh(bookcase_record)
    return True


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
