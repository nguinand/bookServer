from typing import Optional
from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.db.db_models.base import Base


class BookAccess(Base):
    __tablename__ = "book_access"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, autoincrement=True
    )
    book_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("books.id"), nullable=False
    )
    country: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    viewability: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    embeddable: Mapped[Optional[Boolean]] = mapped_column(Boolean, nullable=True)
    public_domain: Mapped[Optional[Boolean]] = mapped_column(Boolean, nullable=True)
    epub_available: Mapped[Optional[Boolean]] = mapped_column(Boolean, nullable=True)
    epub_token_link: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    pdf_available: Mapped[Optional[Boolean]] = mapped_column(Boolean, nullable=True)
    pdf_token_link: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    web_reader_link: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    book = relationship("Book", back_populates="access_info")
