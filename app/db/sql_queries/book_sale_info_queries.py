from sqlalchemy.orm import Session

from app.db.db_models.book_sale_info import BookSaleInfo


def get_book_sale_info_by_id(id: int, session: Session) -> BookSaleInfo:
    return session.query(BookSaleInfo).filter_by(id=id).first()
