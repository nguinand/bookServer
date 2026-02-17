from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import JSONResponse

from app.crud.book_crud import update_book_by_model
from app.db.db_conn import db_manager
from app.models.book import BookModel
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/database", tags=["books-database"])


@router.post("/update_book/", response_model=BookModel, status_code=status.HTTP_200_OK)
async def update_book(
    book_model: BookModel, session: Session = Depends(db_manager.get_db)
) -> JSONResponse:
    try:
        books_result = update_book_by_model(
            book_replacement=book_model, session=session
        )
        if books_result:
            status_code = status.HTTP_200_OK
            content = {f"Updated book - {book_model.volume_info.title}"}
        else:
            status_code = status.HTTP_204_NO_CONTENT
            content = {f"Book not updated - {book_model.volume_info.title}"}
        return JSONResponse(status_code=status_code, content=content)

    except ValueError as e:
        logger.error(e)
        return JSONResponse(
            status_code=422,
            content={
                "book_id is required to update database entry for a book.": str(e)
            },
        )
