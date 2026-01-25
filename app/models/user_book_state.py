from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

from app.db.db_models.user_book_state import ReadingStatus


class UserBookStateModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(
        description="The id of the book state. Most likely comes from database.",
        examples=[1234],
        gt=0,
    )
    user_id: int = Field(
        description="The user id of the book state", examples=[1234], gt=0
    )
    book_id: int = Field(
        description="The book id of the book state", examples=[1234], gt=0
    )
    reading_status: ReadingStatus = Field(
        ReadingStatus.WANT_TO_READ,
        description="The reading status of the book",
        examples=["want_to_read", "reading", "completed", "abandoned"],
    )
    current_page: int = Field(0, ge=0)
    percent_complete: int = Field(0, ge=0, le=100)
    started_at: datetime | None = Field(
        None,
        description="The time the user started the book state",
        examples=[datetime(2020, 1, 1)],
    )
    finished_at: datetime | None = Field(
        None,
        description="The time the user finished the book state",
        examples=[datetime(2020, 1, 1)],
    )
