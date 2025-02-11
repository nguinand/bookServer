from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="user")
    avatar_id = Column(Integer, ForeignKey("avatars.id"), nullable=True)
    status_id = Column(Integer, ForeignKey("user_status.id"), nullable=True)
    created_at = Column(TIMESTAMP, server_default="CURRENT_TIMESTAMP")
    last_login = Column(TIMESTAMP, nullable=True)

    bookcases = relationship("Bookcase", back_populates="user")
    ratings = relationship("UserBookAttributes", back_populates="user")
