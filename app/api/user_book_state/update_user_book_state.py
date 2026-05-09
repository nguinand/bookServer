from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.user_book_state_crud import (
    convert_user_book_state,
    update_user_book_state,
)
from app.db.db_conn import db_manager
from app.models.user_book_state import UserBookStateModel

router = APIRouter()


@router.put(
    "/update_user_book_state/",
    response_model=UserBookStateModel,
    status_code=status.HTTP_200_OK,
)
async def user_book_state_update(
    user_book_state_model: UserBookStateModel,
    session: Session = Depends(db_manager.get_db),
) -> UserBookStateModel:
    try:
        user_book_state_result = update_user_book_state(
            user_book_state_replacement=user_book_state_model,
            session=session,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )

    if user_book_state_result:
        return convert_user_book_state(user_book_state_result)

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User book state not found.",
    )
