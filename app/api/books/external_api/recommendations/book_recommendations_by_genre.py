import httpx

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.api.books.external_api import BooksRequestError, api_key, book_api_request
from app.models.book import BookModel
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/books/recommendations", tags=["books-external"])


@router.get(
    "/by_genre/",
    response_model=list[BookModel],
    status_code=status.HTTP_200_OK,
)
async def get_book_recommendations_by_genre(
    genre_name: str,
    max_results: int = 10,
    start_index: int = 0,
) -> list[BookModel] | JSONResponse:
    """Recommend books from Google Books that match a caller-provided genre."""
    genre_query = genre_name.strip()
    if not genre_query:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="genre_name must not be blank.",
        )

    async with httpx.AsyncClient() as client:
        books: list[BookModel] = []
        seen_google_books_ids: set[str] = set()
        current_start_index = start_index

        while len(books) < max_results:
            params = {
                "q": f"subject:{genre_query}",
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
