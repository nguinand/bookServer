from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.user_book_attributes_crud import (
    convert_user_book_attribute,
    get_user_book_attribute_by_id,
    get_user_book_attribute_by_user_and_book_id,
    get_user_book_attribute_by_user_id,
)
from app.db.db_conn import db_manager
from app.db.db_models.user import User
from app.models.user_book_attributes import UserBookAttributesModel
from app.utils.api_token import get_current_user
from app.utils.authorization import ensure_current_user_matches_user_id
from app.utils.logger import get_logger

logger = get_logger(__name__)


router = APIRouter(prefix="/user_book_attributes", tags=["books-external"])


@router.get(
    "/book_attribute_by_id/{attribute_id}",
    tags=["User Book Attributes"],
    response_model=UserBookAttributesModel,
    status_code=status.HTTP_200_OK,
)
async def user_book_attribute_by_id(
    attribute_id: int,
    session: Session = Depends(db_manager.get_db),
    current_user: User = Depends(get_current_user),
) -> UserBookAttributesModel:
    attribute_results = get_user_book_attribute_by_id(attribute_id, session)
    if attribute_results:
        ensure_current_user_matches_user_id(
            current_user,
            attribute_results.user_id,
            resource_name="user_book_attribute_by_id",
            resource_id=attribute_id,
        )
        return convert_user_book_attribute(attribute_results)
    logger.error(
        "Requested user book attribute was not found. "
        f"current_user_id={current_user.id} attribute_id={attribute_id}",
    )
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Book attribute not found"
    )


@router.get(
    "/book_attribute_by_user_id/",
    tags=["User Book Attributes"],
    response_model=List[UserBookAttributesModel],
    status_code=status.HTTP_200_OK,
)
async def user_book_attribute_by_user_id(
    user_id: int,
    limit: int = 100,
    offset: int = 0,
    session: Session = Depends(db_manager.get_db),
    current_user: User = Depends(get_current_user),
) -> List[UserBookAttributesModel]:
    ensure_current_user_matches_user_id(
        current_user,
        user_id,
        resource_name="user_book_attribute_by_user_id",
    )
    attribute_result = get_user_book_attribute_by_user_id(
        user_id, session, limit, offset
    )
    return [convert_user_book_attribute(attribute) for attribute in attribute_result]


@router.get(
    "/book_attribute_by_book_id/",
    tags=["User Book Attributes"],
    response_model=List[UserBookAttributesModel],
    status_code=status.HTTP_200_OK,
)
async def user_book_attribute_by_book_id(
    book_id: int,
    session: Session = Depends(db_manager.get_db),
    current_user: User = Depends(get_current_user),
) -> List[UserBookAttributesModel]:
    attribute_result = get_user_book_attribute_by_user_and_book_id(
        current_user.id, book_id, session
    )
    return [convert_user_book_attribute(attribute) for attribute in attribute_result]
