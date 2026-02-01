from fastapi import APIRouter
from typing import List

from app.crud.book_crud import get_books_by_title, get_book_by_google_id
from app.crud.model_conversions import convert_book_to_model
from app.crud.shared_queries import get_book_by_book_id
from app.db.db_conn import db_manager
from app.models.book import BookModel
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/books_by_title/", response_model=List[BookModel], status_code=200)
async def books_by_title(title: str) -> List[BookModel]:
    books_result = get_books_by_title(title=title, session=db_manager.session)
    books = []
    for book in books_result:
        books.append(convert_book_to_model(book))
    return books


@router.get("/books_by_google_id/", response_model=BookModel, status_code=200)
async def books_by_google_id(google_id: str) -> BookModel:
    books_result = get_book_by_google_id(
        google_id=google_id, session=db_manager.session
    )
    return convert_book_to_model(books_result)


@router.get("/books_by_book_id/", response_model=BookModel, status_code=200)
async def books_by_book_id(book_id: str) -> BookModel:
    books_result = get_book_by_book_id(book_id=book_id, session=db_manager.session)
    return convert_book_to_model(books_result)
