from pydantic import BaseModel, EmailStr
from typing import List
from app.models.book import Book  # Import your Book model


class User(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    favorite_books: List[Book] = []  # A list of Book objects (can also be Optional)

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "first_name": "Jane",
                "last_name": "Doe",
                "email": "janedoe@example.com",
                "favorite_books": [
                    {
                        "title": "The Catcher in the Rye",
                        "authors": ["J.D. Salinger"],
                        "publisher": "Little, Brown and Company",
                        "published_year": 1951,
                        "isbn_10": "0316769487",
                        "isbn_13": "9780316769488",
                        "description": "A story about teenage rebellion.",
                        "page_count": 277,
                        "categories": ["Fiction", "Classic"],
                        "average_rating": 4.1,
                        "ratings_count": 3487,
                    }
                ],
            }
        }
