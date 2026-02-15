from sqlite3 import DatabaseError

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from app.crud.user_book_attributes_crud import create_user_book_attribute
from app.db.db_conn import db_manager
from app.models.user_book_attributes import UserBookAttributesModel
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/user_book_attributes", tags=["User Book Attributes"])


@router.post("/create_user_book_attribute/")
def create_book_attribute(
    user_book_attribute: UserBookAttributesModel,
    session: Session = Depends(db_manager.get_db),
) -> UserBookAttributesModel:
    try:
        return create_user_book_attribute(user_book_attribute, session)
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Unable to create the user book attribute for the book {user_book_attribute.book_id} - {e}",
        )
