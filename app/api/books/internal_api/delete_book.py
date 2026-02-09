from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from app.crud.book_crud import delete_book_by_book_id
from app.db.db_conn import DatabaseOperationError, db_manager
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/database", tags=["books-database"])


@router.delete("/delete_book/{book_id}", status_code=200)
async def delete_book(
    book_id: int, session: Session = Depends(db_manager.get_db)
) -> JSONResponse:
    try:
        deleted = delete_book_by_book_id(book_id=book_id, session=session)
    except DatabaseOperationError as e:
        raise HTTPException(
            status_code=409, detail=f"Unable to delete book by ID {book_id} - {e}"
        )
    content = {
        "book_id": book_id,
        "deleted": deleted,
    }

    return JSONResponse(
        status_code=200,
        content=content,
    )
