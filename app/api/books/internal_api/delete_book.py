from fastapi import APIRouter, Depends
from starlette.responses import JSONResponse
from sqlalchemy.orm import Session

from app.crud.book_crud import delete_book_by_book_id
from app.utils.logger import get_logger
from app.db.db_conn import db_manager

logger = get_logger(__name__)
router = APIRouter(prefix="/database", tags=["books-database"])


@router.delete("/delete_book/{book_id}", status_code=200)
async def delete_book(
    book_id: int, session: Session = Depends(db_manager.get_db)
) -> JSONResponse:
    deleted = delete_book_by_book_id(book_id=book_id, session=session)
    content = {
        "book_id": book_id,
        "deleted": deleted,
    }

    return JSONResponse(
        status_code=200,
        content=content,
    )
