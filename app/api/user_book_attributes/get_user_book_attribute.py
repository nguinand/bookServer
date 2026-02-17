from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from app.crud.user_book_attributes_crud import (
    convert_user_book_attribute,
    get_user_book_attribute_by_book_id,
    get_user_book_attribute_by_id,
    get_user_book_attribute_by_user_id,
)
from app.db.db_conn import db_manager
from app.models.user_book_attributes import UserBookAttributesModel
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
    attribute_id: int, session: Session = Depends(db_manager.get_db)
) -> UserBookAttributesModel:
    attribute_results = get_user_book_attribute_by_id(attribute_id, session)
    if attribute_results:
        return convert_user_book_attribute(attribute_results)
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Book attribute not found"
    )


@router.get(
    "/book_attribute_by_user_id/{user_id}",
    tags=["User Book Attributes"],
    response_model=List[UserBookAttributesModel],
    status_code=status.HTTP_200_OK,
)
async def user_book_attribute_by_user_id(
    user_id: int, session: Session = Depends(db_manager.get_db)
) -> List[UserBookAttributesModel]:
    attribute_result = get_user_book_attribute_by_user_id(user_id, session)
    attributes = []
    for attribute in attribute_result:
        attributes.append(convert_user_book_attribute(attribute))
    return attributes


@router.get(
    "/book_attribute_by_book_id/{book_id}",
    tags=["User Book Attributes"],
    response_model=List[UserBookAttributesModel],
    status_code=status.HTTP_200_OK,
)
async def user_book_attribute_by_book_id(
    book_id: int, session: Session = Depends(db_manager.get_db)
) -> List[UserBookAttributesModel]:
    attribute_result = get_user_book_attribute_by_book_id(book_id, session)
    attributes = []
    for attribute in attribute_result:
        attributes.append(convert_user_book_attribute(attribute))
    return attributes
