from sqlalchemy import Column, Integer, String, Text, TIMESTAMP
from base import Base


class admin_logs(Base):
    __table__ = "admin_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    event_type = Column(
        String(100), nullable=False
    )  # Type of event (e.g., "USER_DELETED", "BOOK_ADDED")
    event_description = Column(
        Text, nullable=False
    )  # Detailed description of the event
    created_at = Column(TIMESTAMP, server_default="CURRENT_TIMESTAMP")
