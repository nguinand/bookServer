from typing import List
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from app.utils.get_env import get_env_val_or_raise
from app.utils.logger import get_logger
import httpx

from app.models.book import BookModel

logger = get_logger()


router = APIRouter()
GOOGLE_BOOKS_API_URL = get_env_val_or_raise("GOOGLE_BOOKS_API_URL")
api_key = get_env_val_or_raise("GOOGLE_BOOKS_API_KEY")


@router.get("/name/", response_model=List[BookModel])
async def get_books_by_name(
    query: str, max_results: int = 10, start_index: int = 0
) -> List[BookModel]:
    params = {
        "q": query,
        "startIndex": start_index,
        "maxResults": max_results,
        "key": api_key,
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(GOOGLE_BOOKS_API_URL, params=params)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            logger.error(e.response.text)
            return JSONResponse(
                status_code=e.response.status_code, content=e.response.json()
            )
        except httpx.RequestError as e:
            logger.error(f"Network error calling Google Books API, {str(e)}")
            return JSONResponse(
                status_code=502,
                content={
                    "error": "Upstream request to Google Books failed",
                    "detail": str(e),
                },
            )

        data = response.json()

        books: List[BookModel] = []
        for item in data.get("items", []):
            book_data = {
                "google_books_id": item["id"],
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