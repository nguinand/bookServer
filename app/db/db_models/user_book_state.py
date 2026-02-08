import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.db_models.base import Base


class ReadingStatus(str, enum.Enum):
    WANT_TO_READ = "want_to_read"
    READING = "reading"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class UserBookState(Base):
    __tablename__ = "user_book_state"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, autoincrement=True
    )

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    book_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("books.book_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    reading_status: Mapped[ReadingStatus] = mapped_column(
        Enum(ReadingStatus, name="reading_status"),
        nullable=False,
        default=ReadingStatus.WANT_TO_READ,
    )

    current_page: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    percent_complete: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    user = relationship("User", back_populates="book_states")
    book = relationship("Book", back_populates="user_states")

    __table_args__ = (
        UniqueConstraint("user_id", "book_id", name="unique_user_book_state"),
    )
