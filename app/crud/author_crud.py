from sqlalchemy.orm import Session

from app.crud.book_crud import get_book_by_id
from app.crud.book_utils import convert_book_to_model
from app.db.db_models.author import Author
from app.models.author import AuthorModel


def create_author(author_model: AuthorModel, session: Session) -> AuthorModel:
    """
    Function that creates an entry in the Author table.
    """
    author_data = Author(**author_model.model_dump(by_alias=True))
    session.add(author_data)
    session.commit()
    session.refresh(author_data)
    return author_data


def get_authors_by_name(name: str, session: Session) -> list[Author]:
    return session.query(Author).filter_by(name=name).all()


def get_author_by_id(id: int, session: Session) -> Author | None:
    return session.query(Author).filter_by(id=id).first()


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
        get_book_by_id(book.id, session)
        for book in author_replacement.books
        if book.id is not None
    ]
    author_record.books = author_replacement.books
    session.commit()

    return author_record


def delete_author_by_id(author_id: int, session: Session) -> bool:
    author_record = get_author_by_id(author_id, session)

    if not author_record:
        return False  # could have returned an exception

    session.delete(author_record)
    session.commit()
    return True


def convert_author(author_data: Author) -> AuthorModel:
    return AuthorModel(
        id=author_data.id,
        bio=author_data.bio,
        name=author_data.name,
        books=[convert_book_to_model(book) for book in author_data.books],
    )


def resolve_author(name: str, book_title: str, session: Session) -> Author:
    possible_authors = get_authors_by_name(name, session)

    for author in possible_authors:
        for book in author.books:
            if book.title.lower().strip() == book_title.lower().strip():
                return author  # We found a likely match

    # No overlap match found — create a new one
    new_author = Author(name=name)
    session.add(new_author)
    session.flush()
    return new_author
