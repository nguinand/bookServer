from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi import status

from app.crud.bookcase_crud import (
    convert_bookcase,
    get_bookcase_by_id,
    get_bookcases_by_user_id,
)
from app.db.db_conn import db_manager
from app.db.db_models.user import User
from app.models.bookcase import BookcaseModel
from app.utils.api_token import get_current_user
from app.utils.authorization import ensure_current_user_matches_user_id
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/database", tags=["Bookcase"])


@router.get(
    "/bookcase_by_id/{bookcase_id}",
    response_model=BookcaseModel,
    status_code=status.HTTP_200_OK,
)
async def bookcase_by_id(
    bookcase_id: int,
    session: Session = Depends(db_manager.get_db),
    current_user: User = Depends(get_current_user),
) -> BookcaseModel:
    bookcase_data = get_bookcase_by_id(bookcase_id=bookcase_id, session=session)
    if bookcase_data:
        ensure_current_user_matches_user_id(
            current_user,
            bookcase_data.user_id,
            resource_name="bookcase_by_id",
            resource_id=bookcase_id,
        )
        return convert_bookcase(bookcase_data)
    logger.error(
        "Requested bookcase was not found. "
        f"current_user_id={current_user.id} bookcase_id={bookcase_id}",
    )
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Bookcase was not found"
    )


@router.get(
    "/bookcases_by_user_id/",
    response_model=List[BookcaseModel],
    status_code=status.HTTP_200_OK,
)
async def bookcases_by_user_id(
    user_id: int,
    limit: int = 100,
    offset: int = 0,
    session: Session = Depends(db_manager.get_db),
    current_user: User = Depends(get_current_user),
) -> List[BookcaseModel]:
    ensure_current_user_matches_user_id(
        current_user,
        user_id,
        resource_name="bookcases_by_user_id",
    )
    bookcase_rows = get_bookcases_by_user_id(
        user_id=user_id, session=session, limit=limit, offset=offset
    )
    return [convert_bookcase(bookcase_data) for bookcase_data in bookcase_rows]
