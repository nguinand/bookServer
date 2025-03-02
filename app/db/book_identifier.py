from sqlalchemy import Column, ForeignKey, Integer, String
from app.db.base import Base
from sqlalchemy.orm import relationship


class BookIdentifier(Base):
    __tablename__ = "book_identifiers"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    book_id = Column(
        Integer, ForeignKey("books.id", ondelete="CASCADE"), nullable=False
    )
    identifier_type = Column(String(50), nullable=False)  # ISBN_10, ISBN_13, etc.
    identifier_value = Column(String(50), nullable=False)  # The actual identifier

    book = relationship("Book", back_populates="identifiers")
