from app.models.book import BookModel
from typing import List, Optional
from pydantic import BaseModel


class AuthorModel(BaseModel):
    id: Optional[int] = None
    bio: Optional[str] = None
    name: str
    books: List[BookModel] = []

    class Config:
        from_attributes = True
