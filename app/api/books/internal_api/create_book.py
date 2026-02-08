from app.crud.model_conversions import convert_book_to_model
from app.models.book import BookModel
from app.utils.logger import get_logger
from fastapi import APIRouter, Depends
from app.crud.book_crud import store_book_entry
from app.db.db_conn import db_manager
from sqlalchemy.orm import Session

logger = get_logger(__name__)
router = APIRouter(prefix="/database", tags=["books-database"])


@router.post("/create_book/", response_model=BookModel, status_code=200)
async def create_book(
    book_model: BookModel, session: Session = Depends(db_manager.get_db)
) -> BookModel:
    book_data = store_book_entry(book_model=book_model, session=session)
    return convert_book_to_model(book_data)
