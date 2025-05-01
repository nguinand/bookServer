from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from app.db.db_models.base import Base


class UserStatus(Base):
    __tablename__ = "user_status"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)  # e.g. Bronze, Silver
    level = Column(Integer, unique=True, nullable=False)  # Numeric rank
    benefits = Column(Text, nullable=True)  # Optional description of perks

    # Reverse relationship to User
    users = relationship("User", back_populates="status")
