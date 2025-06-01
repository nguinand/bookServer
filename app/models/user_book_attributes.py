from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import relationship, Mapped, mapped_column

# This is the USER input for the book.
class UserBookAttributesModel(BaseModel):
    id: int
    user_id: int
    book_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("books.id", ondelete="CASCADE"), nullable=False
    )
    rating: int
    review_text: Optional[str] = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
