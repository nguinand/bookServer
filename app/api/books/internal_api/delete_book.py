from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import JSONResponse

from app.crud.book_crud import delete_book_by_book_id
from app.db.db_conn import db_manager
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/database", tags=["books-database"])


@router.delete("/delete_book/{book_id}", status_code=status.HTTP_200_OK)
async def delete_book(
    book_id: int, session: Session = Depends(db_manager.get_db)
) -> JSONResponse:
    deleted = delete_book_by_book_id(book_id=book_id, session=session)
    content = {
        "book_id": book_id,
        "deleted": deleted,
    }

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=content,
    )
