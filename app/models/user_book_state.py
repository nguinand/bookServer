from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from app.db.db_models.user_book_state import ReadingStatus


class UserBookStateModel(BaseModel):
    id: Optional[int] = None
    user_id: int
    book_id: int
    reading_status: ReadingStatus = ReadingStatus.WANT_TO_READ
    current_page: Optional[int] = Field(default=None, ge=0)
    percent_complete: Optional[int] = Field(default=None, ge=0, le=100)
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
