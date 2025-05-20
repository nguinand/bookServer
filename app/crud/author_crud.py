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
    def create_author(self, author_model: AuthorModel, session: Session) -> Author:
        """
        Function that creates an entry in the Author table.
        """
        author_data = Author(**author_model.model_dump(by_alias=True))
        session.add(author_data)
        session.commit()
        session.refresh(author_data)
        return author_data

    def get_author_by_name(self, name: str, session:Session) -> list[Author]:
        return session.query(Author).filter_by(name=name).all()
    
    def get_author_by_id(self, id: int, session: Session) -> Author:
        return session.query(Author).filter_by(id = id).first()

    def update_author(self): ...

    def delete_author(self): ...
