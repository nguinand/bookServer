from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette import status

from app.crud.book_crud import store_book_entry
from app.crud.model_conversions import convert_book_to_model
from app.db.db_conn import db_manager
from app.models.book import BookModel
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/database", tags=["books-database"])


@router.post("/create_book/", response_model=BookModel, status_code=status.HTTP_200_OK)
async def create_book(
    book_model: BookModel, session: Session = Depends(db_manager.get_db)
) -> BookModel:
    book_data = store_book_entry(book_model=book_model, session=session)
    return convert_book_to_model(book_data)
