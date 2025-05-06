from typing import Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.db_models.author import Author


class AuthorModel(BaseModel):
    id: Optional[int] = None
    google_books_id: Optional[str] = None
    bio: Optional[str] = None
    name: str

    class Config:
        from_attributes = True


class AuthorCrud:
    def create_author(self, author_model: AuthorModel, session: Session) -> None:
        """
        Function that creates an entry in the Author table.
        """
        author_data = Author(**author_model.model_dump(by_alias=True))
        session.add(author_data)
        session.commit()
        session.refresh(author_data)
        return author_data

    def read_author(self): ...

    def update_author(self): ...

    def delete_author(self): ...
