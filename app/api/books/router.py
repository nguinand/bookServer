from fastapi import APIRouter
from .books_by_name import router as books_by_name

router = APIRouter(prefix="/books", tags=["books"])

router.include_router(books_by_name)
