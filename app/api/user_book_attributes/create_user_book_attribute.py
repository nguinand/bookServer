from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.crud.user_book_attributes_crud import create_user_book_attribute
from app.db.db_conn import db_manager
from app.db.db_models.user import User
from app.models.user_book_attributes import UserBookAttributesModel
from app.utils.api_token import get_current_user
from app.utils.authorization import ensure_current_user_matches_user_id
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/user_book_attributes", tags=["User Book Attributes"])


@router.post("/create_user_book_attribute/")
def create_book_attribute(
    user_book_attribute: UserBookAttributesModel,
    session: Session = Depends(db_manager.get_db),
    current_user: User = Depends(get_current_user),
) -> UserBookAttributesModel:
    ensure_current_user_matches_user_id(
        current_user,
        user_book_attribute.user_id,
        resource_name="create_user_book_attribute",
    )
    return create_user_book_attribute(user_book_attribute, session)
