from sqlalchemy import select
from sqlalchemy.orm import Session

from app.crud.model_conversions import convert_book_to_model
from app.crud.shared_queries import get_book_by_book_id
from app.db.db_conn import db_manager
from app.db.db_models.author import Author
from app.models.author import AuthorModel


def create_author(author_model: AuthorModel, session: Session) -> AuthorModel:
    """
    Function that creates an entry in the Author table.
    """
    author_data = Author(**author_model.model_dump(by_alias=True))
    session.add(author_data)
    db_manager.commit_or_raise(session)
    session.refresh(author_data)
    return author_data


def get_author_by_name(name: str, session: Session, limit=100, offset=0) -> Author:
    stmt = (
        select(Author)
        .where(Author.name == name)
        .order_by(Author.id)
        .limit(limit)
        .offset(offset)
    )
    return session.scalars(stmt).one_or_none()


def get_author_by_id(author_id: int, session: Session) -> Author | None:
    return session.get(Author, author_id)


def update_author(author_replacement: AuthorModel, session: Session) -> None | Author:
    # find original author and replace contents
    if author_replacement.id is None:
        raise ValueError(
            f"Cannot replace author without an ID. {author_replacement.id} - {author_replacement.name}"
        )

    author_record = get_author_by_id(author_replacement.id, session)

    if not author_record:
        return None

    author_record.name = author_replacement.name
    author_record.bio = author_replacement.bio
    author_record.books = [
        get_book_by_book_id(book.book_id, session)
        for book in author_replacement.books
        if book.book_id is not None
    ]
    author_record.books = author_replacement.books
    db_manager.commit_or_raise(session)

    return author_record


def delete_author_by_id(author_id: int, session: Session) -> bool:
    author_record = get_author_by_id(author_id, session)

    if not author_record:
        return False  # could have returned an exception

    session.delete(author_record)
    db_manager.commit_or_raise(session)
    return True


def convert_author(author_data: Author) -> AuthorModel:
    return AuthorModel(
        id=author_data.id,
        bio=author_data.bio,
        name=author_data.name,
        books=[convert_book_to_model(book) for book in author_data.books],
    )
