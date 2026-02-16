from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from app.crud.book_crud import get_book_by_google_id, get_books_by_title
from app.crud.model_conversions import convert_book_to_model
from app.crud.shared_queries import get_book_by_book_id
from app.db.db_conn import DatabaseOperationError, db_manager
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
    title: str,
    limit: int = 100,
    offset: int = 0,
    session: Session = Depends(db_manager.get_db),
) -> List[BookModel]:
    try:
        books_result = get_books_by_title(title, session, limit, offset)
    except DatabaseOperationError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"unable to fetch book by title - {title}",
        )
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
    try:
        books_result = get_book_by_google_id(google_id=google_id, session=session)
    except DatabaseOperationError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"unable to fetch book by google ID - {google_id}",
        )
    if books_result:
        return convert_book_to_model(books_result)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")


@router.get(
    "/books_by_book_id/{book_id}",
    response_model=BookModel,
    status_code=status.HTTP_200_OK,
)
async def books_by_book_id(
    book_id: int, session: Session = Depends(db_manager.get_db)
) -> BookModel:
    try:
        books_result = get_book_by_book_id(book_id=book_id, session=session)
    except DatabaseOperationError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"unable to fetch book by book ID- {book_id}",
        )
    if books_result:
        return convert_book_to_model(books_result)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
