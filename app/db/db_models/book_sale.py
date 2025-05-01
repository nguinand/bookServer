from sqlalchemy import DECIMAL, Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.db.db_models.base import Base


class BookSale(Base):
    __tablename__ = "book_sales"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    country = Column(String(10), nullable=True)
    saleability = Column(String(50), nullable=True)
    is_ebook = Column(Boolean, nullable=True)
    price = Column(DECIMAL(10, 2), nullable=True)
    currency_code = Column(String(5), nullable=True)
    retail_price = Column(DECIMAL(10, 2), nullable=True)
    retail_currency_code = Column(String(5), nullable=True)

    book = relationship("Book", back_populates="sale_info")
