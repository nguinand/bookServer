from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.crud.book_sale_info_crud import delete_book_sale_info
from app.db.db_conn import db_manager

router = APIRouter()


@router.delete(
    "/delete_book_sale_info/{book_sale_info_id}",
    status_code=status.HTTP_200_OK,
)
async def book_sale_info_delete(
    book_sale_info_id: int,
    session: Session = Depends(db_manager.get_db),
) -> JSONResponse:
    deleted = delete_book_sale_info(
        book_sale_info_id=book_sale_info_id,
        session=session,
    )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"book_sale_info_id": book_sale_info_id, "deleted": deleted},
    )
