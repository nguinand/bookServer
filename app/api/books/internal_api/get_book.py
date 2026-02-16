from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette import status

from app.crud.book_crud import get_book_by_google_id, get_books_by_title
from app.crud.model_conversions import convert_book_to_model
from app.crud.shared_queries import get_book_by_book_id
from app.db.db_conn import db_manager
from app.models.book import BookModel
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/database", tags=["books-database"])


@router.get(
    "/books_by_title/",
    response_model=List[BookModel],
    status_code=status.HTTP_200_OK,
)
async def books_by_title(
    title: str, limit: int, offset: int, session: Session = Depends(db_manager.get_db)
) -> List[BookModel]:
    books_result = get_books_by_title(title, session, limit, offset)
    books = []
    for book in books_result:
        books.append(convert_book_to_model(book))
    return books


@router.get(
    "/books_by_google_id/{google_id}",
    response_model=BookModel,
    status_code=status.HTTP_200_OK,
)
async def books_by_google_id(
    google_id: str, session: Session = Depends(db_manager.get_db)
) -> BookModel:
    books_result = get_book_by_google_id(google_id=google_id, session=session)
    return convert_book_to_model(books_result)


@router.get(
    "/books_by_book_id/{book_id}",
    response_model=BookModel,
    status_code=status.HTTP_200_OK,
)
async def books_by_book_id(
    book_id: str, session: Session = Depends(db_manager.get_db)
) -> BookModel:
    books_result = get_book_by_book_id(book_id=book_id, session=session)
    return convert_book_to_model(books_result)
