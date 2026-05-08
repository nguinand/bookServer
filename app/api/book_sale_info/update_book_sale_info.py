from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.book_sale_info_crud import (
    convert_book_sale_info,
    update_book_sale_info,
)
from app.db.db_conn import db_manager
from app.models.book_sale_info import BookSaleInfoModel

router = APIRouter()


@router.put(
    "/update_book_sale_info/",
    response_model=BookSaleInfoModel,
    status_code=status.HTTP_200_OK,
)
async def book_sale_info_update(
    book_sale_info_model: BookSaleInfoModel,
    session: Session = Depends(db_manager.get_db),
) -> BookSaleInfoModel:
    try:
        book_sale_info_result = update_book_sale_info(
            book_sale_info_replacement=book_sale_info_model,
            session=session,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )

    if book_sale_info_result:
        return convert_book_sale_info(book_sale_info_result)

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Book sale info not found.",
    )
