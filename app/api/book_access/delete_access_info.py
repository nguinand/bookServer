from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.crud.book_access_crud import delete_access_info
from app.db.db_conn import db_manager

router = APIRouter()


@router.delete("/delete_access_info/{book_access_id}", status_code=status.HTTP_200_OK)
async def access_info_delete(
    book_access_id: int,
    session: Session = Depends(db_manager.get_db),
) -> JSONResponse:
    deleted = delete_access_info(book_access_id=book_access_id, session=session)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"book_access_id": book_access_id, "deleted": deleted},
    )
