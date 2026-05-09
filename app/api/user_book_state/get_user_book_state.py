from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.user_book_state_crud import (
    convert_user_book_state,
    get_user_book_state_by_id,
    get_user_book_state_by_user_and_book,
    get_user_book_states_by_user_id,
)
from app.db.db_conn import db_manager
from app.models.user_book_state import (
    GetUserBookStateByUserAndBookRequest,
    GetUserBookStatesByUserIdRequest,
    UserBookStateModel,
)

router = APIRouter()


@router.get(
    "/get_user_book_state_by_id/{user_book_state_id}",
    response_model=UserBookStateModel,
    status_code=status.HTTP_200_OK,
)
async def user_book_state_by_id(
    user_book_state_id: int,
    session: Session = Depends(db_manager.get_db),
) -> UserBookStateModel:
    user_book_state_result = get_user_book_state_by_id(
        user_book_state_id=user_book_state_id,
        session=session,
    )
    if user_book_state_result:
        return convert_user_book_state(user_book_state_result)

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User book state not found.",
    )


@router.post(
    "/get_user_book_states_by_user_id/",
    response_model=list[UserBookStateModel],
    status_code=status.HTTP_200_OK,
)
async def user_book_states_by_user_id(
    user_book_states_request: GetUserBookStatesByUserIdRequest,
    session: Session = Depends(db_manager.get_db),
) -> list[UserBookStateModel]:
    user_book_state_results = get_user_book_states_by_user_id(
        user_id=user_book_states_request.user_id,
        limit=user_book_states_request.limit,
        offset=user_book_states_request.offset,
        session=session,
    )
    return [
        convert_user_book_state(user_book_state)
        for user_book_state in user_book_state_results
    ]


@router.post(
    "/get_user_book_state_by_user_and_book/",
    response_model=UserBookStateModel,
    status_code=status.HTTP_200_OK,
)
async def user_book_state_by_user_and_book(
    user_book_state_request: GetUserBookStateByUserAndBookRequest,
    session: Session = Depends(db_manager.get_db),
) -> UserBookStateModel:
    user_book_state_result = get_user_book_state_by_user_and_book(
        user_id=user_book_state_request.user_id,
        book_id=user_book_state_request.book_id,
        session=session,
    )
    if user_book_state_result:
        return convert_user_book_state(user_book_state_result)

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User book state not found.",
    )
