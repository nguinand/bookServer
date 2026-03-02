from fastapi import APIRouter, Depends, HTTPException
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
    except ValueError as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
        )

    if books_result:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={f"Updated book - {book_model.volume_info.title}"},
        )

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Book not found - {book_model.volume_info.title}",
    )
