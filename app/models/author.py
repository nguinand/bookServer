from app.crud.book_crud import BookModel
from typing import List, Optional
from pydantic import BaseModel


class AuthorModel(BaseModel):
    id: Optional[int] = None
    google_books_id: Optional[str] = None
    bio: Optional[str] = None
    name: str
    books: List[BookModel] = []

    class Config:
        from_attributes = True
