from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.db_models.base import Base


class Avatar(Base):
    __tablename__ = "avatars"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    image_url = Column(String(255), unique=True, nullable=False)
    description = Column(String(100), nullable=True)

    # Establish reverse relationship (if you want to access users from avatar)
    users = relationship("User", back_populates="avatar")
