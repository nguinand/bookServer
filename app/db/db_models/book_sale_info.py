from typing import Optional
from sqlalchemy import DECIMAL, Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.db.db_models.base import Base
from decimal import Decimal


class BookSaleInfo(Base):
    __tablename__ = "book_sale_info"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, autoincrement=True
    )
    book_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("books.id", ondelete="CASCADE"), nullable=False
    )
    country: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    saleability: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    is_ebook: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    buy_link: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    list_price: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(10, 2), nullable=True)
    list_price_currency_code: Mapped[Optional[str]] = mapped_column(
        String(5), nullable=True
    )
    retail_price: Mapped[Optional[Decimal]] = mapped_column(
        DECIMAL(10, 2), nullable=True
    )
    retail_price_currency_code: Mapped[Optional[str]] = mapped_column(
        String(5), nullable=True
    )

    book = relationship("Book", back_populates="book_sale_info")
