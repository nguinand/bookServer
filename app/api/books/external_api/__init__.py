import httpx
from app.utils.get_env import get_env_val_or_raise

GOOGLE_BOOKS_API_URL = get_env_val_or_raise("GOOGLE_BOOKS_API_URL")
api_key = get_env_val_or_raise("GOOGLE_BOOKS_API_KEY")


class BooksRequestError(Exception):
    def __init__(self, status_code: int, error: dict):
        self.status_code = status_code
        self.error = error
        super().__init__()


async def book_api_request(client, params, logger):
    try:
        response = await client.get(GOOGLE_BOOKS_API_URL, params=params)
        response.raise_for_status()
        return response
    except httpx.HTTPStatusError as e:
        logger.error(e.response.text)
        raise BooksRequestError(
            status_code=e.response.status_code, error=e.response.json()
        )
    except httpx.RequestError as e:
        logger.error(f"Network error calling Google Books API, {str(e)}")
        raise BooksRequestError(
            status_code=502,
            error={
                "error": "Upstream request to Google Books endpoint failed",
                "detail": str(e),
            },
        )
