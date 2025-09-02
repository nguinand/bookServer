from sqlalchemy.orm import Session

from app.crud.book_crud import convert_book_to_model
from app.db.db_models import Bookcase, Book
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
            book = session.query(Book).filter_by(id=book_model.id).first()
            if book:
                bookcase_data.books.append(book)

    session.add(bookcase_data)
    session.commit()
    session.refresh(bookcase_data)
    return bookcase_data


def get_bookcase_by_id(bookcase_id: int, session: Session) -> None | Bookcase:
    return session.query(Bookcase).filter_by(id=bookcase_id).first()


def get_bookcase_by_user_id(user_id: int, session: Session) -> None | Bookcase:
    return session.query(Bookcase).filter_by(user_id=user_id).first()


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
            book = session.query(Book).filter_by(id=book_model.id).first()
            if book:
                bookcase_record.books.append(book)

    session.commit()
    session.refresh(bookcase_record)
    return bookcase_record


def delete_bookcase_by_id(bookcase_id: int, session: Session) -> bool:
    bookcase_info = get_bookcase_by_id(bookcase_id, session)
    if not bookcase_info:
        return False

    session.delete(bookcase_info)
    session.commit()
    return True


def convert_bookcase(bookcase_data: Bookcase) -> BookcaseModel:
    return BookcaseModel(
        id=bookcase_data.id,
        user_id=bookcase_data.user_id,
        name=bookcase_data.name,
        created_at=bookcase_data.created_at,
        books=[convert_book_to_model(book) for book in bookcase_data.books],
    )
