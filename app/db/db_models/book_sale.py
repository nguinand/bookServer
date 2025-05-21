from typing import Optional
from sqlalchemy import DECIMAL, Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.db.db_models.base import Base


class BookSale(Base):
    __tablename__ = "book_sales"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, autoincrement=True
    )
    book_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("books.id"), nullable=False
    )
    country: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    saleability: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    is_ebook: Mapped[Optional[Boolean]] = mapped_column(Boolean, nullable=True)
    price: Mapped[Optional[DECIMAL]] = mapped_column(DECIMAL(10, 2), nullable=True)
    currency_code: Mapped[Optional[str]] = mapped_column(String(5), nullable=True)
    retail_price: Mapped[Optional[DECIMAL]] = mapped_column(
        DECIMAL(10, 2), nullable=True
    )
    retail_currency_code: Mapped[Optional[str]] = mapped_column(
        String(5), nullable=True
    )

    book = relationship("Book", back_populates="sale_info")
