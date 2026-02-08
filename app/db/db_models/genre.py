from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.db_models.base import Base


class Genre(Base):
    __tablename__ = "genres"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    # A Book can belong to multiple genres.
    # A genre can be associated with multiple books.
    # N:N
    books = relationship("Book", secondary="book_genres", back_populates="genres")
