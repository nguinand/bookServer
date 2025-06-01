from datetime import datetime
from typing import Optional
from pydantic import BaseModel


# This is the USER input for the book.
class UserBookAttributesModel(BaseModel):
    id: int
    user_id: int
    book_id: int
    rating: int
    review_text: Optional[str] = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
