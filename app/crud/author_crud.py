from sqlalchemy.orm import Session
from app.db.db_models.author import Author
from app.db.db_models.book import Book
from app.models.author import AuthorModel


class AuthorCrud:
    def create_author(self, author_model: AuthorModel, session: Session) -> AuthorModel:
        """
        Function that creates an entry in the Author table.
        """
        author_data = Author(**author_model.model_dump(by_alias=True))
        session.add(author_data)
        session.commit()
        session.refresh(author_data)
        return author_data

    # Assuming any author is unique
    def get_author_by_name(self, name: str, session: Session) -> list[Author]:
        authors = session.query(Author).filter_by(name=name).first()
        return authors

    def get_author_by_id(self, id: int, session: Session) -> AuthorModel | None:
        author_record = session.query(Author).filter_by(id=id).first()
        return author_record

    def update_author(
        self, author_replacement: AuthorModel, session: Session
    ) -> None | Author:
        # find original author and replace contents
        if author_replacement.id is None:
            raise ValueError(
                f"Cannot replace author without an ID. {author_replacement.id} - {author_replacement.name}"
            )

        author_record = (
            session.query(Author).filter_by(id=author_replacement.id).first()
        )

        if not author_record:
            return None

        author_record.name = author_replacement.name
        author_record.bio = author_replacement.bio
        author_record.google_books_id = author_replacement.google_books_id
        author_record.books = [
            session.query(Book).filter_by(id=book.id).first()
            for book in author_replacement.books
            if book.id is not None
        ]
        author_record.books = author_replacement.books
        session.commit()

        return author_record

    def delete_author_by_id(self, author_id: int, session: Session) -> bool:
        author = session.query(Author).filter_by(id=author_id).first()

        if not author:
            return False  # could have returned an exception

        session.delete(author)
        session.commit()
        return True

    def convert_author(self, author_data: Author) -> AuthorModel: ...
