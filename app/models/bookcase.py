from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.book import BookModel


class BookcaseModel(BaseModel):
    id: int
    user_id: int
    name: str
    created_at: Optional[datetime] = None
    books: Optional[list[BookModel]] = []

    class Config:
        from_attributes = True
