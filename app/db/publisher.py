from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from base import Base


class Publisher(Base):
    __tablename__ = "publishers"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), unique=True, nullable=False)

    books = relationship("Book", back_populates="publisher")
