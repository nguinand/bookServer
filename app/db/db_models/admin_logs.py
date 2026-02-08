from datetime import datetime

from sqlalchemy import TIMESTAMP, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.db_models.base import Base


class AdminLogs(Base):
    __tablename__ = "admin_logs"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, autoincrement=True
    )
    event_type: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # Type of event (e.g., "USER_DELETED", "BOOK_ADDED")
    event_description: Mapped[str] = mapped_column(
        Text, nullable=False
    )  # Detailed description of the event
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.current_timestamp()
    )
