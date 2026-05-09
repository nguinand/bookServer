from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.crud.user_book_state_crud import (
    convert_user_book_state,
    create_user_book_state,
)
from app.db.db_conn import db_manager
from app.models.user_book_state import UserBookStateModel

router = APIRouter()


@router.post(
    "/create_user_book_state/",
    response_model=UserBookStateModel,
    status_code=status.HTTP_200_OK,
)
async def user_book_state_create(
    user_book_state_model: UserBookStateModel,
    session: Session = Depends(db_manager.get_db),
) -> UserBookStateModel:
    user_book_state_data = create_user_book_state(
        user_book_state_model=user_book_state_model,
        session=session,
    )
    return convert_user_book_state(user_book_state_data)
