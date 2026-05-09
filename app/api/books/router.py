from fastapi import APIRouter, Depends

from app.api.books.external_api.books_by_generic import router as books_by_generic
from app.api.books.external_api.books_by_isbn import router as books_by_isbn
from app.api.books.external_api.books_by_name import router as books_by_name
from app.api.books.external_api.recommendations.book_recommendations_by_author import (
    router as book_recommendations_by_author,
)
from app.api.books.external_api.recommendations.book_recommendations_by_bookshelf import (
    router as book_recommendations_by_bookshelf,
)
from app.api.books.external_api.recommendations.book_recommendations_by_genre import (
    router as book_recommendations_by_genre,
)
from app.api.books.internal_api.create_book import router as create_book
from app.api.books.internal_api.delete_book import router as delete_book
from app.api.books.internal_api.get_book import router as get_books
from app.api.books.internal_api.update_book import router as update_book
from app.utils.api_token import get_current_user

router = APIRouter(dependencies=[Depends(get_current_user)])

router.include_router(books_by_name)
router.include_router(books_by_isbn)
router.include_router(books_by_generic)
router.include_router(book_recommendations_by_author)
router.include_router(book_recommendations_by_bookshelf)
router.include_router(book_recommendations_by_genre)
router.include_router(create_book)
router.include_router(get_books)
router.include_router(update_book)
router.include_router(delete_book)
