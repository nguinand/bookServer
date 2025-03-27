from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from base import Base  # or from app.db.base if using absolute imports


class Avatar(Base):
    __tablename__ = "avatars"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    image_url = Column(String(255), unique=True, nullable=False)
    description = Column(String(100), nullable=True)

    # Establish reverse relationship (if you want to access users from avatar)
    users = relationship("User", back_populates="avatar")
