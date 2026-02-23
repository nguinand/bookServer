from typing import Optional

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.db_models.base import Base


class BookAccess(Base):
    __tablename__ = "book_access"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, autoincrement=True
    )
    book_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("books.book_id"), nullable=False
    )
    country: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    viewability: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    embeddable: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)
    public_domain: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)
    epub_available: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)
    epub_token_link: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    pdf_available: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)
    pdf_token_link: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    web_reader_link: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    book = relationship("Book", back_populates="access_info")
