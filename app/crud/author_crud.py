from sqlalchemy.orm import Session
from app.crud.book_crud import BookCrud
from app.db.db_models.author import Author
from app.db.sql_queries.author_queries import get_author_by_id, get_author_by_name
from app.db.sql_queries.book_queries import get_book_by_id
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
        return get_author_by_name(name, session)

    def get_author_by_id(self, id: int, session: Session) -> Author | None:
        return get_author_by_id(id, session)

    def update_author(
        self, author_replacement: AuthorModel, session: Session
    ) -> None | Author:
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

    def delete_author_by_id(self, author_id: int, session: Session) -> bool:
        author = self.get_author_by_id(author_id, session)

        if not author:
            return False  # could have returned an exception

        session.delete(author)
        session.commit()
        return True

    def convert_author(self, author_data: Author) -> AuthorModel:
        return AuthorModel(
            id=author_data.id,
            bio=author_data.bio,
            name=author_data.name,
            books=[
                BookCrud().convert_book_to_model(book) for book in author_data.books
            ],
        )
