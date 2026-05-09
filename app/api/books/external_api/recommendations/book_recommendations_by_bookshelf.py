from collections import Counter

import httpx
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.api.books.external_api import BooksRequestError, api_key, book_api_request
from app.crud.bookcase_crud import get_bookcases_with_books_by_user_id
from app.db.db_conn import db_manager
from app.db.db_models.bookcase import Bookcase
from app.db.db_models.user import User
from app.models.book import BookModel
from app.utils.api_token import get_current_user
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/books/recommendations", tags=["books-external"])
GENERIC_FALLBACK_QUERY = "bestsellers"


def get_top_bookshelf_genre(bookcases: list[Bookcase]) -> tuple[str | None, set[str]]:
    genre_counts: Counter[str] = Counter()
    owned_google_books_ids: set[str] = set()

    for bookcase in bookcases:
        for book in bookcase.books:
            if book.google_books_id:
                owned_google_books_ids.add(book.google_books_id)

            for genre in book.genres:
                genre_name = genre.name.strip()
                if genre_name:
                    genre_counts[genre_name] += 1

    if not genre_counts:
        return None, owned_google_books_ids

    highest_count = max(genre_counts.values())
    top_genre = sorted(
        genre for genre, count in genre_counts.items() if count == highest_count
    )[0]
    return top_genre, owned_google_books_ids


@router.get(
    "/by_bookshelf_genre/",
    response_model=list[BookModel],
    status_code=status.HTTP_200_OK,
)
async def get_book_recommendations_by_bookshelf_genre(
    max_results: int = 10,
    start_index: int = 0,
    session: Session = Depends(db_manager.get_db),
    current_user: User = Depends(get_current_user),
) -> list[BookModel] | JSONResponse:
    """Recommend books using the most common genre in the current user's bookcases."""
    bookcases = get_bookcases_with_books_by_user_id(
        user_id=current_user.id,
        session=session,
    )
    top_genre, owned_google_books_ids = get_top_bookshelf_genre(bookcases)
    query = f"subject:{top_genre}" if top_genre else GENERIC_FALLBACK_QUERY
    async with httpx.AsyncClient() as client:
        books: list[BookModel] = []
        seen_google_books_ids: set[str] = set()
        current_start_index = start_index

        while len(books) < max_results:
            params = {
                "q": query,
                "startIndex": current_start_index,
                "maxResults": max_results,
                "key": api_key,
            }

            try:
                response = await book_api_request(client, params, logger)
            except BooksRequestError as e:
                return JSONResponse(status_code=e.status_code, content=e.error)

            data = response.json()
            items = data.get("items", [])
            if not items:
                break

            for item in items:
                book_data = {
                    "id": item["id"],
                    "volumeInfo": item.get("volumeInfo", {}),
                    "saleInfo": item.get("saleInfo"),
                    "accessInfo": item.get("accessInfo", {}),
                }

                try:
                    book = BookModel(**book_data)
                    if book.google_books_id in seen_google_books_ids:
                        continue
                    if book.google_books_id in owned_google_books_ids:
                        continue
                    books.append(book)
                    seen_google_books_ids.add(book.google_books_id)
                except (ValidationError, TypeError) as e:
                    logger.error(f"Validation error building BookModel: {str(e)}")
                    return JSONResponse(
                        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                        content={"error": "Validation error", "detail": str(e)},
                    )

                if len(books) >= max_results:
                    break

            current_start_index += len(items)
        return books
