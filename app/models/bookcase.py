from pydantic import BaseModel

from app.models.book import BookModel


class BookcaseModel(BaseModel):
    id: int
    user_id: int
    name: str
    created_at: int
    books: list[BookModel] = []

    class Config:
        from_attributes = True
