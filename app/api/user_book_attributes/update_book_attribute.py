from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from app.crud.user_book_attributes_crud import (
    get_user_book_attribute_by_id,
    update_user_book_attribute_entry,
)
from app.db.db_conn import db_manager
from app.db.db_models.user import User
from app.models.user_book_attributes import UserBookAttributesModel
from app.utils.api_token import get_current_user
from app.utils.authorization import ensure_current_user_matches_user_id
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.post(
    "/update_book_attribute",
    response_model=UserBookAttributesModel,
    status_code=status.HTTP_200_OK,
)
async def update_book_attribute(
    book_replacement: UserBookAttributesModel,
    session: Session = Depends(db_manager.get_db),
    current_user: User = Depends(get_current_user),
) -> JSONResponse:
    ensure_current_user_matches_user_id(
        current_user,
        book_replacement.user_id,
        resource_name="update_user_book_attribute_request",
        resource_id=book_replacement.id,
    )
    if book_replacement.id is not None:
        existing_attribute = get_user_book_attribute_by_id(
            book_replacement.id,
            session,
        )
        if existing_attribute is not None:
            ensure_current_user_matches_user_id(
                current_user,
                existing_attribute.user_id,
                resource_name="update_user_book_attribute_record",
                resource_id=book_replacement.id,
            )
    try:
        updated_book_attribute = update_user_book_attribute_entry(
            book_replacement, session
        )
    except ValueError:
        logger.error(
            "User book attribute update failed validation. "
            f"current_user_id={current_user.id} attribute_id={book_replacement.id}",
        )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Invalid book attribute update request.",
        )
    if updated_book_attribute:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "detail": f"Updated book attribute for book id {book_replacement.id}"
            },
        )

    logger.error(
        "User book attribute update failed because the record was not found. "
        f"current_user_id={current_user.id} attribute_id={book_replacement.id}",
    )
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Book attribute was not found.",
    )
