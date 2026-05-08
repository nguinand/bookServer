from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.book_sale_info_crud import (
    convert_book_sale_info,
    get_book_sale_info_by_id,
)
from app.db.db_conn import db_manager
from app.models.book_sale_info import BookSaleInfoModel

router = APIRouter()


@router.get(
    "/get_book_sale_info_by_id/{book_sale_info_id}",
    response_model=BookSaleInfoModel,
    status_code=status.HTTP_200_OK,
)
async def book_sale_info_by_id(
    book_sale_info_id: int,
    session: Session = Depends(db_manager.get_db),
) -> BookSaleInfoModel:
    book_sale_info_result = get_book_sale_info_by_id(
        book_sale_info_id=book_sale_info_id,
        session=session,
    )
    if book_sale_info_result:
        return convert_book_sale_info(book_sale_info_result)

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Book sale info not found.",
    )
