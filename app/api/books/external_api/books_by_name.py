from typing import List
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.api.books.external_api import api_key, book_api_request, BooksRequestError
from app.utils.logger import get_logger
import httpx

from app.models.book import BookModel

logger = get_logger(__name__)


router = APIRouter()


@router.get("/name/", response_model=List[BookModel], status_code=200)
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
                    status_code=422,
                    content={"error": "Validation error", "detail": str(e)},
                )
        return books
