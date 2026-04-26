from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from app.crud.user_book_attributes_crud import (
    delete_user_book_attribute_by_id,
    get_user_book_attribute_by_id,
)
from app.db.db_conn import db_manager
from app.db.db_models.user import User
from app.utils.api_token import get_current_user
from app.utils.authorization import ensure_current_user_matches_user_id
from app.utils.logger import get_logger

logger = get_logger(__name__)


router = APIRouter(prefix="/user_book_attributes", tags=["User Book Attributes"])


@router.delete(
    "/delete_user_book_attribute/{attribute_id}", status_code=status.HTTP_200_OK
)
async def delete_user_book_attribute(
    attribute_id: int,
    session: Session = Depends(db_manager.get_db),
    current_user: User = Depends(get_current_user),
) -> JSONResponse:
    existing_attribute = get_user_book_attribute_by_id(attribute_id, session)
    if existing_attribute is not None:
        ensure_current_user_matches_user_id(
            current_user,
            existing_attribute.user_id,
            resource_name="delete_user_book_attribute",
            resource_id=attribute_id,
        )
    deleted = delete_user_book_attribute_by_id(attribute_id, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"user_attribute_id": attribute_id, "deleted": deleted},
    )
