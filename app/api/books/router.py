from fastapi import APIRouter
from .books_by_name import router as books_by_name
from .books_by_isbn import router as books_by_isbn

router = APIRouter(prefix="/books", tags=["books"])

router.include_router(books_by_name)
router.include_router(books_by_isbn)
