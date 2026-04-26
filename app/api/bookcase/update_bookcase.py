from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from fastapi import status

from app.crud.bookcase_crud import (
    get_bookcase_by_id,
    update_bookcase as update_bookcase_entry,
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
    "/update_bookcase/", response_model=BookcaseModel, status_code=status.HTTP_200_OK
)
async def update_bookcase(
    bookcase_replacement: BookcaseModel,
    session: Session = Depends(db_manager.get_db),
    current_user: User = Depends(get_current_user),
) -> JSONResponse:
    ensure_current_user_matches_user_id(
        current_user,
        bookcase_replacement.user_id,
        resource_name="update_bookcase_request",
        resource_id=bookcase_replacement.id,
    )
    if bookcase_replacement.id is not None:
        existing_bookcase = get_bookcase_by_id(bookcase_replacement.id, session=session)
        if existing_bookcase is not None:
            ensure_current_user_matches_user_id(
                current_user,
                existing_bookcase.user_id,
                resource_name="update_bookcase_record",
                resource_id=bookcase_replacement.id,
            )
    try:
        updated_bookcase = update_bookcase_entry(
            bookcase_replacement=bookcase_replacement, session=session
        )
    except ValueError:
        logger.error(
            "Bookcase update request failed validation. "
            f"current_user_id={current_user.id} bookcase_id={bookcase_replacement.id}",
        )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Invalid bookcase update request.",
        )

    if updated_bookcase:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"detail": f"Updated bookcase - {bookcase_replacement.name}"},
        )
    logger.error(
        "Bookcase update failed because the record was not found. "
        f"current_user_id={current_user.id} bookcase_id={bookcase_replacement.id}",
    )
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Bookcase was not found.",
    )
