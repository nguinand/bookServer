from fastapi import APIRouter

from app.api.books.external_api.books_by_name import router as books_by_name
from app.api.books.external_api.books_by_isbn import router as books_by_isbn
from app.api.books.external_api.books_by_generic import router as books_by_generic
from app.api.books.internal_api.create_book import router as create_book

router = APIRouter(prefix="/books", tags=["books"])

router.include_router(books_by_name)
router.include_router(books_by_isbn)
router.include_router(books_by_generic)
router.include_router(create_book)
