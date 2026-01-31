from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.db.db_models.base import Base


class BookIdentifier(Base):
    __tablename__ = "book_identifiers"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, autoincrement=True
    )
    book_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("books.book_id", ondelete="CASCADE"), nullable=False
    )
    identifier_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # ISBN_10, ISBN_13, etc.
    identifier_value: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # The actual identifier

    book = relationship("Book", back_populates="identifiers")
