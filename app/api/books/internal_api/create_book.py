from app.db.db_models import Book
from app.models.book import BookModel
from app.utils.logger import get_logger
from fastapi import APIRouter
from app.crud.book_crud import create_book

logger = get_logger(__name__)
router = APIRouter()

@router.post("/create_book/", response_model=Book ,tags=["create_book"], status_code=200)
async def create_book(book_model: BookModel) -> Book:
    book_data = create_book(book_model)
    return book_data