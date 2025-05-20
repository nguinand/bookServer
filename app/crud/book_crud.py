from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy import Integer
from sqlalchemy.orm import Session
from sqlalchemy.orm import Mapped, mapped_column

from app.db.db_models.book import Book


class BookModel(BaseModel):
    id: Optional[int] = None
