from fastapi import APIRouter
from starlette.responses import JSONResponse

from app.crud.book_crud import update_book_by_model
from app.crud.model_conversions import convert_book_to_model
from app.db.db_conn import db_manager
from app.models.book import BookModel
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.post("/update_book/", response_model=BookModel, status_code=200)
async def update_book(book_model: BookModel) -> BookModel:
    try:
        books_result = update_book_by_model(
            book_replacement=book_model, session=db_manager.session
        )
        return convert_book_to_model(books_result)
    except ValueError as e:
        logger.error(e)
        return JSONResponse(
            status_code=422,
            content={
                "book_id is required to update database entry for a book.": str(e)
            },
        )
