from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.crud.book_sale_info_crud import (
    convert_book_sale_info,
    create_book_sale_info,
)
from app.db.db_conn import db_manager
from app.models.book_sale_info import BookSaleInfoModel

router = APIRouter()


@router.post(
    "/create_book_sale_info/",
    response_model=BookSaleInfoModel,
    status_code=status.HTTP_200_OK,
)
async def book_sale_info_create(
    book_sale_info_model: BookSaleInfoModel,
    session: Session = Depends(db_manager.get_db),
) -> BookSaleInfoModel:
    book_sale_info_data = create_book_sale_info(
        book_sale_info_model=book_sale_info_model,
        session=session,
    )
    return convert_book_sale_info(book_sale_info_data)
