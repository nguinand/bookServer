from fastapi import APIRouter

from app.api.books.external_api.books_by_name import router as books_by_name
from app.api.books.external_api.books_by_isbn import router as books_by_isbn
from app.api.books.external_api.books_by_generic import router as books_by_generic
from app.api.books.internal_api.create_book import router as create_book
from app.api.books.internal_api.get_book import router as get_books
from app.api.books.internal_api.update_book import router as update_book
from app.api.books.internal_api.delete_book import router as delete_book

router = APIRouter()

router.include_router(books_by_name)
router.include_router(books_by_isbn)
router.include_router(books_by_generic)
router.include_router(create_book)
router.include_router(get_books)
router.include_router(update_book)
router.include_router(delete_book)
