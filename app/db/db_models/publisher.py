from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.db_models.base import Base


class Publisher(Base):
    __tablename__ = "publishers"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), unique=True, nullable=False)

    # A publisher can publish multiple books.
    # A book belongs to one publisher.
    # 1:N
    books = relationship("Book", back_populates="publisher")
