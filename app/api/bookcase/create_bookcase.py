from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.crud.bookcase_crud import (
    convert_bookcase,
)
from app.crud.bookcase_crud import (
    create_bookcase as create_bookcase_entry,
)
from app.db.db_conn import db_manager
from app.db.db_models.user import User
from app.models.bookcase import BookcaseModel
from app.utils.api_token import get_current_user
from app.utils.authorization import ensure_current_user_matches_user_id
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/database", tags=["Bookcase"])


@router.post(
    "/create_bookcase/", response_model=BookcaseModel, status_code=status.HTTP_200_OK
)
async def create_bookcase(
    bookcase_model: BookcaseModel,
    session: Session = Depends(db_manager.get_db),
    current_user: User = Depends(get_current_user),
) -> BookcaseModel:
    ensure_current_user_matches_user_id(
        current_user,
        bookcase_model.user_id,
        resource_name="create_bookcase",
    )
    bookcase_data = create_bookcase_entry(
        bookcase_model=bookcase_model, session=session
    )
    return convert_bookcase(bookcase_data)
