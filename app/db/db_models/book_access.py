from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.db.db_models.base import Base


class BookAccess(Base):
    __tablename__ = "book_access"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    country = Column(String(10), nullable=True)
    viewability = Column(String(50), nullable=True)
    embeddable = Column(Boolean, nullable=True)
    public_domain = Column(Boolean, nullable=True)
    epub_available = Column(Boolean, nullable=True)
    pdf_available = Column(Boolean, nullable=True)
    web_reader_link = Column(String(255), nullable=True)

    book = relationship("Book", back_populates="access_info")
