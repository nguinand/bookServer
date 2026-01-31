from app.models.book import BookModel
from app.utils.logger import get_logger
from fastapi import APIRouter
from app.crud.book_crud import store_book_entry
from app.db.db_conn import db_manager

logger = get_logger(__name__)
router = APIRouter()


@router.post(
    "/create_book/", response_model=BookModel, tags=["create_book"], status_code=200
)
async def create_book(book_model: BookModel) -> BookModel:
    book_data = store_book_entry(book_model=book_model, session=db_manager.session)
    return book_data
