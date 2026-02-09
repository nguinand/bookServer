from typing import List

import httpx
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from starlette import status

from app.api.books.external_api import BooksRequestError, api_key, book_api_request
from app.models.book import BookModel
from app.utils.logger import get_logger

logger = get_logger(__name__)


router = APIRouter(prefix="/books", tags=["books-external"])


@router.get("/name/", response_model=List[BookModel], status_code=status.HTTP_200_OK)
async def get_books_by_name(
    book_name: str, max_results: int = 10, start_index: int = 0
) -> List[BookModel]:
    params = {
        "q": book_name,
        "startIndex": start_index,
        "maxResults": max_results,
        "key": api_key,
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await book_api_request(client, params, logger)
        except BooksRequestError as e:
            return JSONResponse(status_code=e.status_code, content=e.error)

        data = response.json()

        books: List[BookModel] = []
        for item in data.get("items", []):
            book_data = {
                "id": item["id"],
                "volumeInfo": item.get("volumeInfo", {}),
                "saleInfo": item.get("saleInfo"),
                "accessInfo": item.get("accessInfo", {}),
            }

            try:
                books.append(BookModel(**book_data))
            except (ValidationError, TypeError) as e:
                logger.error(f"Validation error building BookModel: {str(e)}")
                return JSONResponse(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    content={"error": "Validation error", "detail": str(e)},
                )
        return books
